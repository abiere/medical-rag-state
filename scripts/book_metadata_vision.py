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

def _isbn10_to_isbn13(isbn10: str) -> str:
    """Convert ISBN-10 to ISBN-13."""
    clean = re.sub(r"[^\dX]", "", isbn10.upper())
    if len(clean) != 10:
        return ""
    base  = "978" + clean[:9]
    total = sum(int(d) * (1 if i % 2 == 0 else 3)
                for i, d in enumerate(base))
    check = (10 - (total % 10)) % 10
    return base + str(check)


def _validate_isbn13(isbn: str) -> Optional[str]:
    """
    Validate ISBN-13 checksum. Returns clean 13-digit string or None.
    Also accepts ISBN-10 (converts to ISBN-13) and strips dashes/spaces
    for copy-paste friendliness.
    Attempts OCR last-digit correction if checksum fails.
    """
    if not isbn:
        return None
    clean = re.sub(r"[^\dX]", "", str(isbn).upper())

    # ISBN-10 → convert to ISBN-13
    if len(clean) == 10:
        converted = _isbn10_to_isbn13(clean)
        if converted:
            log.info("ISBN-10 %s converted to ISBN-13 %s", clean, converted)
            return converted

    if not re.match(r"^\d{13}$", clean):
        return None

    def _checksum(s):
        total = sum(int(c) * (1 if i % 2 == 0 else 3)
                    for i, c in enumerate(s[:12]))
        return (10 - (total % 10)) % 10

    if int(clean[12]) == _checksum(clean):
        return clean

    # Try OCR corrections on last digit
    for sub in "0123456789":
        candidate = clean[:12] + sub
        if int(candidate[12]) == _checksum(candidate):
            log.info("ISBN corrected: %s → %s", clean, candidate)
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
        epub_images = _render_epub_cover(book_path, max_images=pages)
        png_paths.extend(epub_images)

    log.info("Rendered %d pages for %s", len(png_paths), book_path.name)
    return png_paths


def _render_epub_cover(epub_path: Path,
                       max_images: int = 10) -> list[Path]:
    """
    Extract cover and first images directly from EPUB zip.
    Much more reliable than rendering HTML via fitz.
    """
    import zipfile
    render_subdir = RENDER_DIR / epub_path.stem[:40]
    render_subdir.mkdir(parents=True, exist_ok=True)
    results = []

    try:
        with zipfile.ZipFile(str(epub_path)) as z:
            names = z.namelist()

            # Strategy 1: find OPF manifest cover-image item
            opf_files = [n for n in names if n.endswith(".opf")]
            cover_name = None
            for opf in opf_files:
                try:
                    content = z.read(opf).decode("utf-8", errors="ignore")
                    m = re.search(
                        r'id=["\']cover[^"\']*["\'][^>]*href=["\']([^"\']+)["\']',
                        content, re.I)
                    if not m:
                        m = re.search(
                            r'href=["\']([^"\']+)["\'][^>]*id=["\']cover[^"\']*["\']',
                            content, re.I)
                    if m:
                        href = m.group(1)
                        opf_dir = opf.rsplit("/", 1)[0] if "/" in opf else ""
                        cover_name = (opf_dir + "/" + href).lstrip("/")
                        if cover_name not in names:
                            cover_name = href
                        break
                except Exception:
                    pass

            # Strategy 2: common cover filenames
            if not cover_name:
                for candidate in [
                    "cover.jpg", "cover.jpeg", "cover.png",
                    "OEBPS/cover.jpg", "OEBPS/cover.jpeg",
                    "OEBPS/cover.png", "OEBPS/images/cover.jpg",
                ]:
                    if candidate in names:
                        cover_name = candidate
                        break

            # Strategy 3: first image file in zip
            if not cover_name:
                img_exts = (".jpg", ".jpeg", ".png")
                for name in names:
                    if any(name.lower().endswith(e) for e in img_exts):
                        cover_name = name
                        break

            # Extract cover image
            if cover_name and cover_name in names:
                data = z.read(cover_name)
                ext  = Path(cover_name).suffix.lower()
                out  = render_subdir / f"cover{ext}"
                out.write_bytes(data)
                results.append(out)

            # Extract up to max_images-1 additional image assets
            img_exts = (".jpg", ".jpeg", ".png")
            count = 0
            for name in names:
                if name == cover_name:
                    continue
                if any(name.lower().endswith(e) for e in img_exts):
                    if count >= max_images - 1:
                        break
                    data = z.read(name)
                    ext  = Path(name).suffix.lower()
                    out  = render_subdir / f"page_{count+1:03d}{ext}"
                    out.write_bytes(data)
                    results.append(out)
                    count += 1

    except Exception as e:
        log.error("EPUB cover extraction failed %s: %s", epub_path.name, e)

    return results


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


def _safe_json_parse(text: str) -> dict:
    """Try multiple strategies to parse Gemini JSON output."""
    # Strategy 1: direct parse
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    # Strategy 2: strip markdown fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        result = json.loads(cleaned)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    # Strategy 3: find first complete JSON object by brace matching
    start = cleaned.find("{")
    if start >= 0:
        depth = 0
        for i, ch in enumerate(cleaned[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        result = json.loads(cleaned[start:i + 1])
                        if isinstance(result, dict):
                            return result
                    except json.JSONDecodeError:
                        break
    # Strategy 4: extract isbn_13 at minimum via regex
    isbn_match = re.search(r'"isbn_13"\s*:\s*"(\d{13})"', text)
    if isbn_match:
        log.warning("JSON parse failed, extracting ISBN only via regex")
        return {"isbn_13": isbn_match.group(1)}
    log.error("All JSON parse strategies failed")
    return {}


def _extract_metadata_gemini(png_paths: list[Path]) -> dict:
    """
    Send rendered pages to Gemini Vision and extract metadata.
    Returns raw dict from Gemini or empty dict on failure.
    """
    if not png_paths:
        return {}
    try:
        from google import genai
        from google.genai import types
        import os

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")

        client = genai.Client(api_key=api_key)

        # Detect mime type per image (EPUB may provide JPEG)
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".png": "image/png",  ".webp": "image/webp"}
        contents = []
        for p in png_paths:
            img_data = p.read_bytes()
            mime     = mime_map.get(p.suffix.lower(), "image/png")
            contents.append(types.Part.from_bytes(data=img_data, mime_type=mime))
        contents.append(GEMINI_PROMPT)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                max_output_tokens=3000,
                response_mime_type="application/json",
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

        result = _safe_json_parse(text)
        log.info("Gemini extracted: title=%s isbn=%s",
                 (result.get("title") or "?")[:40],
                 result.get("isbn_13") or "?")
        return result

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
    _WAIT_TIMES = [5, 15, 30]
    for attempt, wait in enumerate(_WAIT_TIMES):
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
            if e.code in (429, 503) and attempt < len(_WAIT_TIMES) - 1:
                log.warning("Google Books %d, retry in %ds", e.code, wait)
                time.sleep(wait)
                continue
            log.warning("Google Books failed %d", e.code)
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


# ── Firecrawl helper ──────────────────────────────────────────────

def _get_firecrawl_key() -> str:
    """Return Firecrawl API key from settings.json, or '' if not set."""
    try:
        cfg_path = BASE / "config" / "settings.json"
        cfg = json.loads(cfg_path.read_text())
        return cfg.get("firecrawl_api", {}).get("api_key", "").strip()
    except Exception:
        return ""


def _firecrawl_scrape(url: str) -> str:
    """
    Scrape a URL via Firecrawl and return markdown content.
    Uses firecrawl-py v4.x: V1FirecrawlApp (FirecrawlApp is an empty alias).
    Returns empty string on failure.
    """
    key = _get_firecrawl_key()
    if not key:
        return ""
    try:
        from firecrawl import V1FirecrawlApp
        app = V1FirecrawlApp(api_key=key)
        result = app.scrape_url(url, formats=["markdown"])

        content = None
        if hasattr(result, "markdown") and result.markdown:
            content = result.markdown
        elif hasattr(result, "content") and result.content:
            content = result.content
        elif isinstance(result, dict):
            content = result.get("markdown") or result.get("content", "")

        if not content:
            log.warning("Firecrawl returned empty content for %s", url)
            return ""

        log.info("Firecrawl scraped %s: %d chars", url, len(content))
        return content

    except Exception as e:
        log.error("Firecrawl scrape failed for %s: %s", url, e)
        return ""


# ── ISBNsearch.org scraper (Firecrawl) ───────────────────────────

def _fetch_isbnsearch(isbn: str) -> dict:
    """
    Scrape ISBNsearch.org via Firecrawl (bypasses bot detection).
    Falls back to direct urllib request when no Firecrawl API key is set.
    """
    if not isbn:
        return {}
    url = f"https://isbnsearch.org/isbn/{isbn}"

    key = _get_firecrawl_key()
    if key:
        md = _firecrawl_scrape(url)
        if not md:
            return {}
        result: dict = {}
        for line in md.splitlines():
            line = line.strip()
            m = re.match(r"\*?\*?([^:*]+)\*?\*?\s*:\s*(.+)", line)
            if not m:
                continue
            label = m.group(1).strip().lower()
            value = m.group(2).strip()
            if label == "title" and not result.get("title"):
                result["title"] = value
            elif label in ("author", "authors") and not result.get("authors"):
                result["authors"] = [
                    a.split(",")[0].strip()
                    for a in value.split(";")
                    if a.strip()
                ]
            elif label == "publisher" and not result.get("publisher"):
                result["publisher"] = value
            elif label in ("published", "year") and not result.get("year"):
                ym = re.search(r"\b(\d{4})\b", value)
                if ym:
                    result["year"] = int(ym.group(1))
            elif label in ("isbn-13", "isbn13") and not result.get("isbn_13"):
                clean = re.sub(r"[^\d]", "", value)
                if len(clean) == 13:
                    result["isbn_13"] = clean
            elif label in ("isbn-10", "isbn10") and not result.get("isbn_10"):
                clean = re.sub(r"[^\d]", "", value)
                if len(clean) == 10:
                    result["isbn_10"] = clean
        if result:
            log.info("ISBNsearch (Firecrawl): found %s (%s)",
                     result.get("title", "?")[:40],
                     result.get("year", "?"))
        return result

    # Fallback: direct urllib
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="ignore")

        try:
            from bs4 import BeautifulSoup
        except ImportError:
            log.warning("BeautifulSoup not installed — ISBNsearch skipped")
            return {}

        if "Please Verify" in html or "captcha" in html.lower():
            log.warning("ISBNsearch.org returned CAPTCHA for %s", isbn)
            return {}

        soup   = BeautifulSoup(html, "html.parser")
        result = {}

        h1 = soup.find("h1")
        if h1:
            result["title"] = h1.get_text(strip=True)

        for strong in soup.find_all("strong"):
            label   = strong.get_text(strip=True).rstrip(":").lower()
            sibling = strong.next_sibling
            if not sibling:
                continue
            value = str(sibling).strip()
            if not value:
                continue
            if label == "author":
                result["authors"] = [
                    a.split(",")[0].strip()
                    for a in value.split(";")
                    if a.strip()
                ]
            elif label == "publisher":
                result["publisher"] = value
            elif label == "published":
                m = re.search(r"\b(\d{4})\b", value)
                if m:
                    result["year"] = int(m.group(1))
            elif label in ("isbn-13", "isbn13"):
                clean = re.sub(r"[^\d]", "", value)
                if len(clean) == 13:
                    result["isbn_13"] = clean
            elif label in ("isbn-10", "isbn10"):
                clean = re.sub(r"[^\d]", "", value)
                if len(clean) == 10:
                    result["isbn_10"] = clean

        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            result["cover_url"] = og_img["content"]

        if result:
            log.info("ISBNsearch (direct): found %s (%s)",
                     result.get("title", "?")[:40],
                     result.get("year", "?"))
        return result

    except Exception as e:
        log.warning("ISBNsearch failed isbn=%s: %s", isbn, e)
        return {}


# ── Library of Congress API ───────────────────────────────────────

def _fetch_loc(isbn: str) -> dict:
    """Fetch from Library of Congress catalog API."""
    if not isbn:
        return {}
    url = f"https://www.loc.gov/search/?q={isbn}&fo=json&at=results"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "NRT-Amsterdam-RAG/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        results = data.get("results", [])
        if not results:
            return {}
        item   = results[0]
        result = {}
        if item.get("title"):
            result["title"] = item["title"].rstrip("/ ").strip()
        contributors = item.get("contributor", [])
        if contributors:
            result["authors"] = [
                c.split(",")[0].strip() for c in contributors[:5]
            ]
        m = re.search(r"\b(\d{4})\b", str(item.get("date", "")))
        if m:
            result["year"] = int(m.group(1))
        subjects = item.get("subject", [])
        if subjects:
            result["subjects"] = subjects[:5]
        if result:
            log.info("LOC: found %s (%s)",
                     result.get("title", "?")[:40],
                     result.get("year", "?"))
        return result
    except Exception as e:
        log.warning("LOC failed isbn=%s: %s", isbn, e)
        return {}


# ── Amazon ASIN scraper (Firecrawl) ──────────────────────────────

def _fetch_amazon_asin(asin: str) -> dict:
    """
    Scrape Amazon product page via Firecrawl (bypasses bot detection).
    Falls back to empty dict without Firecrawl key — Hetzner IPs are blocked.
    ASIN format: B01XXXXXXX or 10-digit alphanumeric.
    """
    if not asin:
        return {}
    asin = re.sub(r"[^A-Z0-9]", "", asin.upper().strip())
    if len(asin) != 10:
        return {}

    key = _get_firecrawl_key()
    if not key:
        log.warning("No Firecrawl API key — Amazon ASIN lookup skipped (Hetzner IPs blocked)")
        return {}

    url = f"https://www.amazon.com/dp/{asin}"
    md = _firecrawl_scrape(url)
    if not md:
        return {}

    result: dict = {}
    lines = md.splitlines()

    # Title: usually first H1 or line starting with #
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            result["title"] = line[2:].strip()
            break

    # Parse Key: Value lines for ISBN, publisher, year, authors
    for line in lines:
        line = line.strip()
        m = re.match(r"\*?\*?([^:*\n]+)\*?\*?\s*:\s*(.+)", line)
        if not m:
            continue
        label = m.group(1).strip().lower()
        value = m.group(2).strip()

        if "isbn-13" in label and not result.get("isbn_13"):
            clean = re.sub(r"[^0-9]", "", value)
            if len(clean) == 13:
                result["isbn_13"] = clean
        elif "isbn-10" in label and not result.get("isbn_10"):
            clean = re.sub(r"[^0-9X]", "", value.upper())
            if len(clean) == 10:
                result["isbn_10"] = clean
        elif label in ("publisher",) and not result.get("publisher"):
            result["publisher"] = value.split(";")[0].strip()[:80]
        elif label in ("publication date", "date", "year") and not result.get("year"):
            ym = re.search(r"\b(19|20)\d{2}\b", value)
            if ym:
                result["year"] = int(ym.group(0))
        elif label in ("author", "authors", "by") and not result.get("authors"):
            result["authors"] = [
                a.split(",")[0].strip()
                for a in re.split(r"[,;]", value)
                if a.strip()
            ]

    # Year fallback: scan for 4-digit year in detail lines
    if not result.get("year"):
        for line in lines:
            ym = re.search(r"\b(19|20)\d{2}\b", line)
            if ym:
                result["year"] = int(ym.group(0))
                break

    if result:
        log.info("Amazon ASIN %s (Firecrawl): title=%s isbn=%s",
                 asin,
                 result.get("title", "?")[:40],
                 result.get("isbn_13", "none"))
    return result


# ── Merge with field-level priority ──────────────────────────────

def _is_bad_title(title: str) -> bool:
    """Return True if title looks like a bad extraction (cover branding, etc.)."""
    if not title:
        return True
    t = title.strip()
    # All caps and short = likely cover branding, not real title
    if t.isupper() and len(t) < 30:
        return True
    # Only one word and short = likely brand/surname only
    if len(t.split()) == 1 and len(t) < 15:
        return True
    # Looks like a phone number
    if re.search(r"\d{3}[\.\-]\d{3}", t):
        return True
    # Copyright text
    if t.lower().startswith("copyright"):
        return True
    return False


FIELD_PRIORITY = {
    "title":          ["google", "isbnsearch", "gemini", "loc", "openlibrary"],
    "subtitle":       ["google", "isbnsearch", "gemini", "openlibrary"],
    "authors":        ["google", "openlibrary", "isbnsearch", "loc", "gemini"],
    "edition_number": ["gemini", "google", "isbnsearch", "openlibrary"],
    "edition_label":  ["gemini", "isbnsearch", "google"],
    "year":           ["isbnsearch", "google", "openlibrary", "loc", "gemini"],
    "isbn_13":        ["gemini", "isbnsearch", "google", "openlibrary"],
    "publisher":      ["isbnsearch", "google", "gemini", "openlibrary"],
    "pages":          ["openlibrary", "google"],
    "description":    ["google", "openlibrary"],
    "cover_url":      ["isbnsearch", "google", "openlibrary"],
    "language":       ["google", "openlibrary"],
    "subjects":       ["google", "openlibrary", "loc"],
}


def _merge_metadata(gemini: dict,
                    google: dict,
                    openlibrary: dict,
                    isbnsearch: dict = None,
                    loc: dict = None) -> dict:
    """
    Merge metadata from up to five sources using field-level priority.
    Adds source attribution and needs_review list.
    """
    sources = {
        "gemini":      gemini      or {},
        "google":      google      or {},
        "openlibrary": openlibrary or {},
        "isbnsearch":  isbnsearch  or {},
        "loc":         loc         or {},
    }
    merged       = {}
    needs_review = []

    for field, priority in FIELD_PRIORITY.items():
        value  = None
        source = None
        for src in priority:
            v = sources[src].get(field)
            if v is None or v == "" or v == []:
                continue
            # For title: skip values that look like bad extractions
            if field == "title" and isinstance(v, str) and _is_bad_title(v):
                log.debug("Skipping bad title from %s: %r", src, v[:40])
                continue
            value  = v
            source = src
            break
        merged[field]          = value
        merged[f"{field}_src"] = source
        if value is None:
            needs_review.append(field)

    merged["confidence"]       = gemini.get("confidence", {}) if gemini else {}
    merged["needs_review"]     = needs_review
    merged["metadata_sources"] = {
        "gemini":      bool(gemini),
        "google":      bool(google),
        "openlibrary": bool(openlibrary),
        "isbnsearch":  bool(isbnsearch),
        "loc":         bool(loc),
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
            if src_field == "year":
                val = str(val)
            elif src_field == "authors":
                if isinstance(val, list):
                    val = ", ".join(str(a) for a in val)
                else:
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

    # Step 4–7: API lookups (all sources)
    google      = _fetch_google_books(isbn) if isbn else {}
    openlibrary = _fetch_openlibrary(isbn)  if isbn else {}
    isbnsearch  = _fetch_isbnsearch(isbn)   if isbn else {}
    loc         = _fetch_loc(isbn)          if isbn else {}
    time.sleep(1)  # respectful rate-limiting after 4 external calls

    if not isbn:
        log.warning("No valid ISBN found for %s — "
                    "using Gemini Vision data only", filename)

    # Step 8: merge
    merged = _merge_metadata(gemini, google, openlibrary, isbnsearch, loc)
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


# ── Full backfill: ALL medical books ─────────────────────────────

def backfill_all_metadata() -> None:
    """Run full enrichment for ALL medical_library books."""
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
        targets.append((sp, s))

    log.info("Full backfill: %d medical books", len(targets))
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
        time.sleep(3)

    log.info("Full backfill done: %d ok, %d failed", ok, failed)


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
    elif "--all" in sys.argv:
        backfill_all_metadata()
    else:
        backfill_missing_metadata()
