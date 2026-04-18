#!/usr/bin/env python3
"""
parse_epub.py — EPUB parser for the Medical RAG book ingestion pipeline.

Three strategies tried in order:
  1. ebooklib  — standard EPUB3/EPUB2
  2. raw ZIP   — non-standard / broken EPUB
  3. text fallback — last resort plain text extraction

Usage:
    python3 scripts/parse_epub.py \
        --file books/acupuncture/some_book.epub \
        --collection acupuncture_points \
        --category acupuncture \
        --output /tmp/chunks.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Reuse shared helpers from parse_pdf
sys.path.insert(0, str(Path(__file__).parent))
from parse_pdf import (
    _detect_lang, _translate_via_ollama,
    _chunk_text, _extract_points, _extract_fig_refs,
    _detect_chapter_section, _split_sentences,
    get_kai_scores,
    IMAGES_DIR, BASE, MIN_WORDS, TARGET_WORDS, MAX_WORDS,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"}


# ── image extraction (ZIP-based) ──────────────────────────────────────────────

def _extract_epub_images(epub_path: Path, book_stem: str) -> list[str]:
    """Extract images > 100×100 px from EPUB (which is a ZIP). Returns relative paths."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    try:
        from PIL import Image as PilImage
        import io as _io

        with zipfile.ZipFile(str(epub_path)) as zf:
            img_entries = [n for n in zf.namelist()
                           if Path(n).suffix.lower() in IMAGE_EXTS]
            for n_idx, entry in enumerate(img_entries):
                try:
                    data = zf.read(entry)
                    img = PilImage.open(_io.BytesIO(data))
                    w, h = img.size
                    if w < 100 or h < 100:
                        continue
                    fname = f"{book_stem}_{n_idx:04d}.png"
                    out_path = IMAGES_DIR / fname
                    img.save(str(out_path), "PNG")
                    saved.append(str(out_path.relative_to(BASE)))
                except Exception as e:
                    logger.debug("EPUB image %s: %s", entry, e)
    except Exception as e:
        logger.warning("EPUB image extraction failed: %s", e)
    return saved


# ── Strategy 1: ebooklib ──────────────────────────────────────────────────────

def _parse_ebooklib(epub_path: Path) -> list[dict] | None:
    """Returns [{page_number, paragraphs, chapter, section}] or None."""
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
    except ImportError:
        logger.info("ebooklib not available")
        return None

    try:
        book = epub.read_epub(str(epub_path), options={"ignore_ncx": True})
    except Exception as e:
        logger.warning("ebooklib read failed: %s", e)
        return None

    pages: list[dict] = []
    spine_idx = 0
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        try:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            # Remove nav/script/style
            for tag in soup(["script", "style", "nav"]):
                tag.decompose()

            paragraphs: list[str] = []
            for el in soup.find_all(["p", "h1", "h2", "h3", "h4", "li"]):
                txt = el.get_text(" ", strip=True)
                if txt:
                    paragraphs.append(txt)

            if not paragraphs:
                continue

            ch, sec = _detect_chapter_section(paragraphs)
            pages.append({
                "page_number": spine_idx + 1,
                "paragraphs":  paragraphs,
                "chapter":     ch,
                "section":     sec,
            })
            spine_idx += 1
        except Exception as e:
            logger.debug("ebooklib item %s: %s", item.get_name(), e)

    if not pages:
        return None

    logger.info("ebooklib: %d spine items", len(pages))
    return pages


# ── Strategy 2: raw ZIP ───────────────────────────────────────────────────────

def _parse_raw_zip(epub_path: Path) -> list[dict] | None:
    """Open EPUB as ZIP, find all HTML/XHTML, parse with BS4."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return None

    try:
        with zipfile.ZipFile(str(epub_path)) as zf:
            html_entries = sorted(
                [n for n in zf.namelist()
                 if Path(n).suffix.lower() in {".html", ".xhtml", ".htm"}]
            )
            if not html_entries:
                return None

            pages: list[dict] = []
            for idx, entry in enumerate(html_entries):
                try:
                    data = zf.read(entry).decode("utf-8", errors="replace")
                    soup = BeautifulSoup(data, "html.parser")
                    for tag in soup(["script", "style", "nav"]):
                        tag.decompose()
                    paragraphs = [
                        el.get_text(" ", strip=True)
                        for el in soup.find_all(["p", "h1", "h2", "h3", "h4", "li"])
                        if el.get_text(strip=True)
                    ]
                    if paragraphs:
                        ch, sec = _detect_chapter_section(paragraphs)
                        pages.append({
                            "page_number": idx + 1,
                            "paragraphs":  paragraphs,
                            "chapter":     ch,
                            "section":     sec,
                        })
                except Exception as e:
                    logger.debug("raw_zip %s: %s", entry, e)

        if not pages:
            return None
        logger.info("raw_zip: %d HTML files", len(pages))
        return pages
    except Exception as e:
        logger.warning("raw_zip failed: %s", e)
        return None


# ── Strategy 3: text fallback ─────────────────────────────────────────────────

def _parse_text_fallback(epub_path: Path) -> list[dict]:
    """Extract all text from ZIP without HTML parsing."""
    try:
        with zipfile.ZipFile(str(epub_path)) as zf:
            texts: list[str] = []
            for entry in sorted(zf.namelist()):
                if Path(entry).suffix.lower() in {".html", ".xhtml", ".htm", ".txt"}:
                    try:
                        raw = zf.read(entry).decode("utf-8", errors="replace")
                        # Strip HTML tags naively
                        clean = re.sub(r"<[^>]+>", " ", raw)
                        clean = re.sub(r"\s+", " ", clean).strip()
                        if len(clean) > 100:
                            texts.append(clean)
                    except Exception:
                        pass

        if not texts:
            return []

        # Chunk the combined text
        full_text = " ".join(texts)
        sents = _split_sentences(full_text)

        pages: list[dict] = []
        page_sents: list[str] = []
        page_words = 0
        page_idx = 1

        for sent in sents:
            wc = len(sent.split())
            page_sents.append(sent)
            page_words += wc
            if page_words >= TARGET_WORDS * 3:
                pages.append({
                    "page_number": page_idx,
                    "paragraphs":  [" ".join(page_sents)],
                    "chapter":     "",
                    "section":     "",
                })
                page_sents = []
                page_words = 0
                page_idx += 1

        if page_sents:
            pages.append({
                "page_number": page_idx,
                "paragraphs":  [" ".join(page_sents)],
                "chapter":     "",
                "section":     "",
            })

        logger.info("text_fallback: %d pseudo-pages", len(pages))
        return pages
    except Exception as e:
        logger.warning("text_fallback failed: %s", e)
        return []


# ── main parse function ───────────────────────────────────────────────────────

def parse_epub(
    epub_path: Path,
    collection_type: str,
    source_category: str,
) -> list[dict[str, Any]]:
    """Parse an EPUB and return Qdrant-ready chunk dicts."""
    book_stem = epub_path.stem
    logger.info("Parsing %s (collection=%s)", epub_path.name, collection_type)

    # Try strategies in order
    strategy = "unknown"
    pages = _parse_ebooklib(epub_path)
    if pages:
        strategy = "ebooklib"
    else:
        pages = _parse_raw_zip(epub_path)
        if pages:
            strategy = "raw_zip"
        else:
            pages = _parse_text_fallback(epub_path)
            strategy = "text_fallback"

    if not pages:
        logger.error("All EPUB strategies failed for %s", epub_path.name)
        return []

    # Extract images
    all_images = _extract_epub_images(epub_path, book_stem)

    chunks: list[dict] = []
    chunk_idx = 0
    current_chapter = current_section = ""
    ingested_at = datetime.now(timezone.utc).isoformat()
    kai = get_kai_scores(epub_path.name)

    for page in pages:
        page_no    = page["page_number"]
        paragraphs = page["paragraphs"]
        if page["chapter"]:
            current_chapter = page["chapter"]
        if page["section"]:
            current_section = page["section"]

        text_chunks = _chunk_text(paragraphs)

        for raw_text in text_chunks:
            if len(raw_text.split()) < MIN_WORDS:
                continue

            lang = _detect_lang(raw_text)
            text_original = None
            if lang not in ("en", "und"):
                translated = _translate_via_ollama(raw_text)
                if translated:
                    text_original = raw_text
                    text_en = translated
                else:
                    text_en = raw_text
            else:
                text_en = raw_text
                lang = "en"

            point_codes = _extract_points(text_en + (text_original or ""))
            fig_refs    = _extract_fig_refs(text_en + (text_original or ""))

            # Distribute images roughly evenly across spine positions
            img_links: list[str] = []
            if all_images and len(pages) > 0:
                imgs_per_page = max(1, len(all_images) // len(pages))
                start = (page_no - 1) * imgs_per_page
                img_links = all_images[start: start + imgs_per_page]

            h = hashlib.sha256(
                f"{epub_path.name}:{page_no}:{chunk_idx}:{text_en[:200]}".encode()
            ).hexdigest()[:16]

            chunk: dict[str, Any] = {
                "text":               text_en,
                "page_number":        page_no,
                "chapter":            current_chapter,
                "section":            current_section,
                "source_file":        epub_path.name,
                "source_category":    source_category,
                "collection_type":    collection_type,
                "format":             "epub",
                "epub_strategy":      strategy,
                "point_codes":        point_codes,
                "figure_refs":        fig_refs,
                "image_links":        img_links,
                "chunk_index":        chunk_idx,
                "chunk_hash":         h,
                "ingested_at":        ingested_at,
                "language_detected":  lang,
                "kai_k":              kai["kai_k"],
                "kai_a":              kai["kai_a"],
                "kai_i":              kai["kai_i"],
                "kai_role":           kai["kai_role"],
            }
            if text_original:
                chunk["text_original"] = text_original

            chunks.append(chunk)
            chunk_idx += 1

    logger.info("Produced %d chunks from %s (strategy=%s)", len(chunks), epub_path.name, strategy)
    return chunks


# ── metadata extractors ───────────────────────────────────────────────────────

def _extract_epub_dc_metadata(epub_path: Path) -> dict:
    """Extract Dublin Core metadata (ISBN, ASIN, title, creator, publisher, date) from EPUB."""
    try:
        import ebooklib
        from ebooklib import epub as epublib
        book = epublib.read_epub(str(epub_path), options={"ignore_ncx": True})
        meta: dict = {}
        for field in ["title", "creator", "publisher", "date", "identifier", "language"]:
            vals = book.get_metadata("DC", field)
            if not vals:
                continue
            if field == "identifier":
                for v, attrs in vals:
                    scheme = (attrs or {}).get("opf:scheme", "").lower()
                    v_str = str(v).strip()
                    if "isbn" in scheme or "isbn" in v_str.lower():
                        meta["isbn"] = v_str
                    elif "asin" in v_str.lower() or v_str.startswith("urn:asin:"):
                        meta["asin"] = v_str.replace("urn:asin:", "").strip()
                    else:
                        meta.setdefault("identifier", v_str)
            else:
                meta[field] = vals[0][0].strip() if vals else ""
        return meta
    except Exception:
        return {}


def _extract_pdf_metadata(pdf_path: Path) -> dict:
    """Extract metadata from PDF file via PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        raw = doc.metadata or {}
        doc.close()
        meta: dict = {}
        if raw.get("title"):
            meta["title"] = raw["title"]
        if raw.get("author"):
            meta["creator"] = raw["author"]
        if raw.get("producer"):
            meta["publisher"] = raw["producer"]
        raw_date = raw.get("creationDate", "") or raw.get("modDate", "")
        if raw_date:
            date_clean = re.sub(r"^D:", "", raw_date.strip())
            m = re.match(r"(\d{4})", date_clean)
            if m:
                year = m.group(1)
                if 1990 <= int(year) <= 2030:
                    meta["date"] = year
        return meta
    except Exception:
        return {}


# ── ISBN extraction + API lookup ─────────────────────────────────────────────

def _get_first_pages_text(book_path: Path, pages: int = 10) -> str:
    """Extract plain text from first N pages — PDF or EPUB."""
    ext = book_path.suffix.lower()
    try:
        if ext == ".pdf":
            import fitz
            doc  = fitz.open(str(book_path))
            text = ""
            for i in range(min(pages, len(doc))):
                text += doc[i].get_text()
            doc.close()
            return text
        elif ext == ".epub":
            from ebooklib import epub as _epub
            from bs4 import BeautifulSoup
            book  = _epub.read_epub(str(book_path), options={"ignore_ncx": True})
            text  = ""
            count = 0
            for item in book.get_items():
                if item.get_type() == 9:  # ITEM_DOCUMENT
                    soup   = BeautifulSoup(item.content, "html.parser")
                    text  += soup.get_text() + "\n"
                    count += 1
                    if count >= pages:
                        break
            return text
    except Exception as e:
        logging.getLogger(__name__).warning(
            "First pages extraction failed %s: %s", book_path.name, e
        )
    return ""


def _extract_isbn_from_text(text: str) -> str:
    """
    Extract ISBN-13 from text.
    Handles labelled forms (ISBN-13, International ISBN-13, etc.)
    and bare 978/979 prefixed numbers.
    Returns 13-digit string or empty string.
    """
    patterns = [
        r"(?:ISBN[-\s]?13|International\s+ISBN[-\s]?13?|"
        r"North\s+American\s+ISBN[-\s]?13?)\s*:?\s*"
        r"((?:978|979)[\d\s\-]{10,17})",
        r"ISBN\s*[-:]?\s*((?:978|979)[\d\s\-]{10,17})",
        r"\b((?:978|979)[\d\-]{10,15})\b",
    ]
    for pat in patterns:
        for m in re.findall(pat, text):
            clean = re.sub(r"[\s\-]", "", m)
            if len(clean) == 13 and clean.isdigit():
                return clean
    return ""


def _extract_isbn(book_path: Path) -> str:
    """Extract ISBN-13 from first 10 pages of a book file."""
    text = _get_first_pages_text(book_path, pages=10)
    return _extract_isbn_from_text(text)


def _lookup_isbn(isbn: str) -> dict:
    """
    Fetch bibliographic metadata by ISBN-13.
    Tries Google Books first, then OpenLibrary.
    Returns dict with: isbn, title, authors, publisher, date, source.
    Returns empty dict on failure.
    """
    import urllib.request as _urlreq
    if not isbn:
        return {}
    log = logging.getLogger(__name__)

    # Google Books
    try:
        url = (
            f"https://www.googleapis.com/books/v1/volumes"
            f"?q=isbn:{isbn}&maxResults=1"
        )
        req = _urlreq.Request(url, headers={"User-Agent": "NRT-Amsterdam-RAG/1.0"})
        with _urlreq.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        items = data.get("items", [])
        if items:
            info  = items[0].get("volumeInfo", {})
            m     = re.search(r"\b(\d{4})\b", info.get("publishedDate", ""))
            year  = m.group(1) if m else ""
            title = info.get("title", "")
            sub   = info.get("subtitle", "")
            return {
                "isbn":      isbn,
                "title":     title + (": " + sub if sub else ""),
                "authors":   ", ".join(info.get("authors", [])),
                "publisher": info.get("publisher", ""),
                "date":      year,
                "source":    "google_books",
            }
    except Exception as e:
        log.warning("Google Books lookup failed isbn=%s: %s", isbn, e)

    # OpenLibrary fallback
    try:
        url = (
            f"https://openlibrary.org/api/books"
            f"?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        )
        req = _urlreq.Request(url, headers={"User-Agent": "NRT-Amsterdam-RAG/1.0"})
        with _urlreq.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        key = f"ISBN:{isbn}"
        if key in data:
            book    = data[key]
            m       = re.search(r"\b(\d{4})\b", book.get("publish_date", ""))
            year    = m.group(1) if m else ""
            authors = ", ".join(a.get("name", "") for a in book.get("authors", []))
            pub     = (book.get("publishers") or [{}])[0].get("name", "")
            return {
                "isbn":      isbn,
                "title":     book.get("title", ""),
                "authors":   authors,
                "publisher": pub,
                "date":      year,
                "source":    "openlibrary",
            }
    except Exception as e:
        log.warning("OpenLibrary lookup failed isbn=%s: %s", isbn, e)

    return {}


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Parse an EPUB into Qdrant-ready chunks")
    ap.add_argument("--file",       required=True)
    ap.add_argument("--collection", required=True)
    ap.add_argument("--category",   required=True)
    ap.add_argument("--output",     default="/tmp/parse_epub_output.json")
    args = ap.parse_args()

    chunks = parse_epub(Path(args.file), args.collection, args.category)
    Path(args.output).write_text(json.dumps(chunks, indent=2, ensure_ascii=False))
    print(f"Wrote {len(chunks)} chunks → {args.output}")


if __name__ == "__main__":
    main()
