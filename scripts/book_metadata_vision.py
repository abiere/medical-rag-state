"""
Pipeline A: Book metadata extraction via Gemini Vision
+ Google Books API + OpenLibrary API.

Renders first 5 pages as PNG → Gemini Vision extracts
bibliographic data → ISBN used to fetch official data
from Google Books and OpenLibrary → merge with field-level
priority rules → save to state.json + book_classifications.json.

No re-ingestion needed. Enriches existing data only.

Usage:
    python3 book_metadata_vision.py           # backfill all
    python3 book_metadata_vision.py --book filename.pdf
"""

import json
import logging
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

BASE          = Path("/root/medical-rag")
CACHE_DIR     = BASE / "data/ingest_cache"
BOOKS_DIR     = BASE / "books"
CFG_PATH      = BASE / "config/book_classifications.json"
RENDER_DIR    = BASE / "data/metadata_renders"
RENDER_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE / "scripts"))
from ai_client import AIClient

_ai = AIClient()


# ── ISBN validation ───────────────────────────────────────────────

def _validate_isbn13(isbn: str) -> Optional[str]:
    """
    Validate ISBN-13 checksum. Returns clean 13-digit string or None.
    Attempts common OCR corrections (0↔8, 1↔7) if checksum fails.
    """
    if not isbn:
        return None
    clean = re.sub(r"[\s\-]", "", str(isbn))
    if not re.match(r"^\d{13}$", clean):
        return None

    def _checksum(s):
        total = sum(int(c) * (1 if i % 2 == 0 else 3)
                    for i, c in enumerate(s[:12]))
        return (10 - (total % 10)) % 10

    if int(clean[12]) == _checksum(clean):
        return clean

    # Try common OCR substitutions on last digit only
    for sub in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        candidate = clean[:12] + sub
        if int(candidate[12]) == _checksum(candidate):
            log.info("ISBN corrected via checksum: %s → %s", clean, candidate)
            return candidate

    return None


# ── Page rendering ────────────────────────────────────────────────

def _render_title_pages(book_path: Path,
                        pages: int = 10) -> list[Path]:
    """
    Render first N pages of a PDF/EPUB as PNG files (300 DPI).
    Returns list of paths to rendered PNG files.
    """
    import fitz  # PyMuPDF

    render_subdir = RENDER_DIR / book_path.stem[:40]
    render_subdir.mkdir(parents=True, exist_ok=True)

    png_paths = []
    ext = book_path.suffix.lower()

    if ext in (".pdf",):
        try:
            doc = fitz.open(str(book_path))
            for i in range(min(pages, len(doc))):
                page = doc[i]
                mat  = fitz.Matrix(300 / 72, 300 / 72)
                pix  = page.get_pixmap(matrix=mat)
                out  = render_subdir / f"page_{i+1:03d}.png"
                pix.save(str(out))
                png_paths.append(out)
            doc.close()
        except Exception as e:
            log.error("PDF render failed %s: %s", book_path.name, e)

    elif ext in (".epub",):
        try:
            from ebooklib import epub
            from bs4 import BeautifulSoup

            book = epub.read_epub(str(book_path),
                                  options={"ignore_ncx": True})
            count = 0
            for item in book.get_items():
                if item.get_type() != 9:  # ITEM_DOCUMENT
                    continue
                soup = BeautifulSoup(item.content, "html.parser")
                text = soup.get_text()
                if len(text.strip()) < 20:
                    continue

                # Render HTML page as PNG via fitz
                html_bytes = item.content
                doc = fitz.open(stream=html_bytes,
                                filetype="html")
                if len(doc) == 0:
                    doc.close()
                    continue
                page = doc[0]
                mat  = fitz.Matrix(300 / 72, 300 / 72)
                pix  = page.get_pixmap(matrix=mat)
                out  = render_subdir / f"page_{count+1:03d}.png"
                pix.save(str(out))
                png_paths.append(out)
                doc.close()
                count += 1
                if count >= pages:
                    break
        except Exception as e:
            log.error("EPUB render failed %s: %s", book_path.name, e)

    log.info("Rendered %d pages for %s", len(png_paths), book_path.name)
    return png_paths


# ── Gemini Vision extraction ──────────────────────────────────────

GEMINI_PROMPT = """You are extracting bibliographic metadata from
title page images of a medical or health sciences textbook.

Analyze the provided images (cover, title page, copyright page —
typically the first 5 pages). These pages contain the book title,
authors, edition, publication year, ISBN, and publisher.

Return ONLY a JSON object — no explanation, no markdown, no
code fences. Just the raw JSON.

{
  "title": "Complete title as printed, excluding subtitle",
  "subtitle": "Subtitle if present, otherwise null",
  "authors": ["Surname A", "Surname B"],
  "edition_number": 7,
  "edition_label": "Seventh Edition",
  "year": 2021,
  "isbn_13": "9780443100284",
  "publisher": "Publisher name",
  "confidence": {
    "title": "high",
    "authors": "high",
    "edition": "high",
    "year": "medium",
    "isbn": "low"
  }
}

Rules:
- authors: surnames only, max 5 names.
  If more than 5 authors: first 4 surnames + "et al." as last entry.
- isbn_13: exactly 13 digits, no dashes or spaces.
  Look carefully at the copyright page for ISBN-13.
- year: use the copyright year (highest year after the © symbol),
  not the print run year.
- edition_number: integer only (7, not "7th").
- confidence per field: "high" (clearly visible and certain),
  "medium" (visible but some uncertainty),
  "low" (inferred or partially visible),
  "none" (not found — use null for that field).
- If a field is genuinely not visible in any of the images: null.
- Do not invent data. Only report what is visible."""


def _extract_metadata_gemini(png_paths: list[Path]) -> dict:
    """
    Send rendered pages to Gemini Vision and extract metadata.
    Returns raw dict from Gemini or empty dict on failure.
    """
    if not png_paths:
        return {}
    try:
        # Send all pages in one call — Gemini supports multi-image
        from google import genai
        from google.genai import types
        import os

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")

        client = genai.Client(api_key=api_key)

        contents = []
        for p in png_paths:
            img_data = p.read_bytes()
            contents.append(
                types.Part.from_bytes(data=img_data,
                                       mime_type="image/png")
            )
        contents.append(GEMINI_PROMPT)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                max_output_tokens=2000
            ),
        )
        if response.text is not None:
            text = response.text.strip()
        else:
            text = ""
            for cand in (response.candidates or []):
                for part in (cand.content.parts if cand.content else []):
                    if part.text:
                        text = part.text.strip()
                        break
        if not text:
            log.warning("Gemini returned empty response")
            return {}
        # Strip markdown fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        result = json.loads(text)
        if not isinstance(result, dict):
            log.warning("Gemini returned non-dict JSON: %s", type(result))
            return {}
        log.info("Gemini extracted: title=%s isbn=%s",
                 (result.get("title") or "?")[:40],
                 result.get("isbn_13") or "?")
        return result

    except json.JSONDecodeError as e:
        log.error("Gemini JSON parse failed: %s", e)
        return {}
    except Exception as e:
        log.error("Gemini vision failed: %s", e)
        return {}


# ── Google Books API ──────────────────────────────────────────────

def _fetch_google_books(isbn: str) -> dict:
    """
    Fetch bibliographic data from Google Books API.
    Returns dict with available fields or empty dict.
    """
    if not isbn:
        return {}
    url = (f"https://www.googleapis.com/books/v1/volumes"
           f"?q=isbn:{isbn}&maxResults=1")
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "NRT-Amsterdam-RAG/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())

            items = data.get("items", [])
            if not items:
                log.info("Google Books: no results for ISBN %s", isbn)
                return {}

            info = items[0].get("volumeInfo", {})
            result = {}

            if info.get("title"):
                result["title"] = info["title"]
            if info.get("subtitle"):
                result["subtitle"] = info["subtitle"]
            if info.get("authors"):
                result["authors"] = info["authors"]
            if info.get("publisher"):
                result["publisher"] = info["publisher"]
            if info.get("pageCount"):
                result["pages"] = info["pageCount"]
            if info.get("language"):
                result["language"] = info["language"]
            if info.get("description"):
                result["description"] = info["description"][:500]
            if info.get("categories"):
                result["subjects"] = info["categories"]

            pub_date = info.get("publishedDate", "")
            m = re.search(r"\b(\d{4})\b", pub_date)
            if m:
                result["year"] = int(m.group(1))

            img = info.get("imageLinks", {})
            if img.get("thumbnail"):
                result["cover_url"] = img["thumbnail"]

            log.info("Google Books: found %s (%s)",
                     result.get("title", "?")[:40],
                     result.get("year", "?"))
            return result

        except urllib.error.HTTPError as e:
            if e.code == 503 and attempt < 2:
                log.warning("Google Books 503, retry %d", attempt + 1)
                time.sleep(5)
                continue
            log.error("Google Books HTTP error %d: %s", e.code, e)
            return {}
        except Exception as e:
            log.error("Google Books failed: %s", e)
            return {}

    return {}


# ── OpenLibrary API ───────────────────────────────────────────────

def _fetch_openlibrary(isbn: str) -> dict:
    """
    Fetch bibliographic data from OpenLibrary API.
    Returns dict with available fields or empty dict.
    """
    if not isbn:
        return {}
    url = (f"https://openlibrary.org/api/books"
           f"?bibkeys=ISBN:{isbn}&format=json&jscmd=data")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "NRT-Amsterdam-RAG/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())

        key = f"ISBN:{isbn}"
        if key not in data:
            log.info("OpenLibrary: no results for ISBN %s", isbn)
            return {}

        book   = data[key]
        result = {}

        if book.get("title"):
            result["title"] = book["title"]
        if book.get("subtitle"):
            result["subtitle"] = book["subtitle"]

        authors = [a.get("name", "") for a in book.get("authors", [])]
        if authors:
            result["authors"] = [a.split(",")[0].strip()
                                  for a in authors if a]

        pubs = book.get("publishers", [])
        if pubs:
            result["publisher"] = pubs[0].get("name", "")

        if book.get("number_of_pages"):
            result["pages"] = book["number_of_pages"]

        subjects = [s.get("name", "")
                    for s in book.get("subjects", [])[:10]]
        if subjects:
            result["subjects"] = subjects

        pub_date = book.get("publish_date", "")
        m = re.search(r"\b(\d{4})\b", pub_date)
        if m:
            result["year"] = int(m.group(1))

        cover = book.get("cover", {})
        if cover.get("medium"):
            result["cover_url"] = cover["medium"]

        log.info("OpenLibrary: found %s (%s)",
                 result.get("title", "?")[:40],
                 result.get("year", "?"))
        return result

    except Exception as e:
        log.error("OpenLibrary failed: %s", e)
        return {}


# ── Merge with field-level priority ──────────────────────────────

FIELD_PRIORITY = {
    # field: [source1, source2, source3]
    # source1 wins if non-empty, else source2, else source3
    "title":          ["google",      "gemini",      "openlibrary"],
    "subtitle":       ["google",      "gemini",      "openlibrary"],
    "authors":        ["google",      "openlibrary", "gemini"],
    "edition_number": ["gemini",      "google",      "openlibrary"],
    "edition_label":  ["gemini",      "google",      None],
    "year":           ["google",      "openlibrary", "gemini"],
    "isbn_13":        ["gemini",      "google",      "openlibrary"],
    "publisher":      ["google",      "gemini",      "openlibrary"],
    "pages":          ["openlibrary", "google",      None],
    "description":    ["google",      "openlibrary", None],
    "cover_url":      ["google",      "openlibrary", None],
    "language":       ["google",      "openlibrary", None],
    "subjects":       ["google",      "openlibrary", None],
}


def _merge_metadata(gemini: dict,
                    google: dict,
                    openlibrary: dict) -> dict:
    """
    Merge metadata from three sources using field-level priority.
    Adds source attribution and needs_review list.
    """
    sources = {
        "gemini":      gemini,
        "google":      google,
        "openlibrary": openlibrary,
    }
    merged       = {}
    needs_review = []

    for field, priority in FIELD_PRIORITY.items():
        value  = None
        source = None
        for src in priority:
            if src is None:
                continue
            v = sources[src].get(field)
            if v is not None and v != "" and v != []:
                value  = v
                source = src
                break
        merged[field]          = value
        merged[f"{field}_src"] = source
        if value is None:
            needs_review.append(field)

    # Confidence from Gemini
    merged["confidence"]       = gemini.get("confidence", {})
    merged["needs_review"]     = needs_review
    merged["metadata_sources"] = {
        "gemini":      bool(gemini),
        "google":      bool(google),
        "openlibrary": bool(openlibrary),
    }

    return merged


# ── Save to state.json + book_classifications.json ────────────────

def _save_metadata(state_path: Path,
                   state: dict,
                   merged: dict) -> None:
    """Update state.json with merged metadata."""
    bm = state.get("book_metadata", {})

    # Map merged fields to book_metadata fields
    field_map = {
        "title":          "title",
        "subtitle":       "subtitle",
        "authors":        "creator",
        "edition_number": "edition_number",
        "edition_label":  "edition_label",
        "year":           "date",
        "isbn_13":        "isbn",
        "publisher":      "publisher",
        "pages":          "pages",
        "description":    "description",
        "cover_url":      "cover_url",
        "language":       "language",
        "subjects":       "subjects",
    }
    for src_field, dst_field in field_map.items():
        val = merged.get(src_field)
        if val is not None:
            # Store year/date as string for consistency with other pipeline paths
            if src_field == "year":
                val = str(val)
            bm[dst_field] = val

    bm["metadata_method"]  = "vision_api_merge"
    bm["metadata_sources"] = merged.get("metadata_sources", {})
    bm["needs_review"]     = merged.get("needs_review", [])
    bm["confidence"]       = merged.get("confidence", {})

    state["book_metadata"] = bm
    tmp = state_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    tmp.replace(state_path)
    log.info("Saved metadata to %s", state_path)


def _update_classifications(filename: str,
                             merged: dict) -> None:
    """
    Update full_title and authors in book_classifications.json
    for entries matching this filename.
    """
    try:
        cfg = json.loads(CFG_PATH.read_text())
        cls = cfg.get("classifications", {})
        updated = False

        # Build full_title: title + subtitle
        title     = merged.get("title") or ""
        subtitle  = merged.get("subtitle") or ""
        full_title = title
        if subtitle:
            full_title = f"{title}: {subtitle}"

        # Authors: last names only
        authors = merged.get("authors") or []
        if isinstance(authors, list):
            authors_str = ", ".join(authors[:5])
        else:
            authors_str = str(authors)

        fn_lower = filename.lower()
        for key, entry in cls.items():
            pats = entry.get("filename_patterns", [])
            if any(p.lower() in fn_lower for p in pats):
                if full_title and not entry.get("full_title"):
                    entry["full_title"] = full_title
                    updated = True
                if authors_str and not entry.get("authors"):
                    entry["authors"] = authors_str
                    updated = True
                break

        if updated:
            cfg["classifications"] = cls
            tmp = CFG_PATH.with_suffix(".tmp")
            tmp.write_text(json.dumps(cfg, indent=2,
                                      ensure_ascii=False))
            tmp.replace(CFG_PATH)
            log.info("Updated classifications for %s", filename)

    except Exception as e:
        log.error("Classifications update failed: %s", e)


# ── Main enrichment function ──────────────────────────────────────

def enrich_book(state_path: Path, state: dict) -> bool:
    """
    Run full metadata enrichment for one book.
    Returns True if enrichment succeeded.
    """
    filename   = state.get("filename", "")
    collection = state.get("collection", "")

    if collection != "medical_library":
        return False

    # Find book file on disk
    book_path = None
    stored_fp = state.get("filepath", "")
    if stored_fp and Path(stored_fp).exists():
        book_path = Path(stored_fp)
    else:
        for fp in BOOKS_DIR.rglob(filename):
            book_path = fp
            break

    if not book_path:
        log.warning("File not found on disk: %s", filename)
        return False

    log.info("=== Enriching: %s ===", filename)

    # Step 1: render first 10 pages
    png_paths = _render_title_pages(book_path, pages=10)
    if not png_paths:
        log.error("No pages rendered for %s", filename)
        return False

    # Step 2: Gemini Vision
    gemini = _extract_metadata_gemini(png_paths)

    # Step 3: validate and fetch ISBN
    isbn = _validate_isbn13(gemini.get("isbn_13", ""))
    if not isbn:
        # Try existing metadata
        isbn = _validate_isbn13(
            state.get("book_metadata", {}).get("isbn", "")
        )

    # Step 4+5: API lookups (always run both)
    google      = _fetch_google_books(isbn) if isbn else {}
    openlibrary = _fetch_openlibrary(isbn)  if isbn else {}

    if not isbn:
        log.warning("No valid ISBN found for %s — "
                    "using Gemini Vision data only", filename)

    # Step 6: merge
    merged = _merge_metadata(gemini, google, openlibrary)
    merged["isbn_13"] = isbn  # Use validated ISBN

    # Step 7: save
    _save_metadata(state_path, state, merged)
    _update_classifications(filename, merged)

    # Cleanup renders
    import shutil
    shutil.rmtree(str(png_paths[0].parent), ignore_errors=True)

    log.info("Done: title=%s year=%s isbn=%s needs_review=%s",
             (merged.get("title") or "?")[:40],
             merged.get("year") or "?",
             isbn or "none",
             merged.get("needs_review", []))
    return True


# ── Backfill: all incomplete medical books ────────────────────────

def backfill_missing_metadata() -> None:
    """
    Run enrichment for all medical_library books that have
    incomplete metadata (missing isbn, title, or year).
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s"
    )
    targets = []
    for d in sorted(CACHE_DIR.iterdir()):
        sp = d / "state.json"
        if not sp.exists():
            continue
        try:
            s = json.loads(sp.read_text())
        except Exception:
            continue
        if s.get("collection") != "medical_library":
            continue
        bm = s.get("book_metadata", {})
        # Process if missing isbn, title, or already has needs_review flag
        if (not bm.get("isbn")
                or not bm.get("title")
                or bm.get("needs_review")):
            targets.append((sp, s))

    log.info("Backfill: %d books to process", len(targets))

    ok = failed = 0
    for sp, s in targets:
        try:
            success = enrich_book(sp, s)
            if success:
                ok += 1
            else:
                failed += 1
        except Exception as e:
            log.error("Failed %s: %s", s.get("filename", ""), e)
            failed += 1
        # Rate limit: avoid hammering APIs
        time.sleep(2)

    log.info("Backfill complete: %d ok, %d failed", ok, failed)


# ── Single book mode ──────────────────────────────────────────────

def enrich_single(filename: str) -> None:
    """Run enrichment for a single book by filename."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s"
    )
    for d in CACHE_DIR.iterdir():
        sp = d / "state.json"
        if not sp.exists():
            continue
        try:
            s = json.loads(sp.read_text())
        except Exception:
            continue
        if filename.lower() in s.get("filename", "").lower():
            enrich_book(sp, s)
            return
    log.error("Book not found in cache: %s", filename)


if __name__ == "__main__":
    if "--book" in sys.argv:
        idx = sys.argv.index("--book")
        enrich_single(sys.argv[idx + 1])
    else:
        backfill_missing_metadata()
