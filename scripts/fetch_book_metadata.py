"""
Medical RAG — Bibliographic Metadata Fetcher

Retrieves and stores structured bibliographic metadata for every book in the
library. Metadata is written to data/books_metadata.json, which the ingestion
pipeline reads to attach citation objects to every Qdrant chunk.

Sources (in priority order):
  1. File itself   — EPUB OPF dc:* tags / PDF XMP + DocInfo
  2. Filename      — ISBN regex fallback (e.g. '9780723436898_Sobotta.epub')
  3. OpenLibrary   — https://openlibrary.org/api/books  (free, no key)
  4. Google Books  — https://www.googleapis.com/books/v1/volumes  (free tier)

Usage
─────
    python scripts/fetch_book_metadata.py --books-dir ./books
    python scripts/fetch_book_metadata.py --file books/Sobotta-Vol1.epub
    python scripts/fetch_book_metadata.py --isbn 9780723436898
    python scripts/fetch_book_metadata.py --refresh --slug sobotta_vol1

Requirements
────────────
    pip install ebooklib beautifulsoup4 lxml pypdf pillow
    (all network calls use stdlib urllib — no extra packages needed)
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR            = Path("/root/medical-rag")
BOOKS_METADATA_PATH = BASE_DIR / "data" / "books_metadata.json"

# ISBN pattern (10 or 13 digits, optionally hyphenated)
_ISBN_RE = re.compile(r"(?:97[89][-\s]?)?(?:\d[-\s]?){9}[\dXx]")

# Minimum delay between API calls (politeness)
_API_DELAY_SECONDS = 0.5


# ---------------------------------------------------------------------------
# Slug helper
# ---------------------------------------------------------------------------

def _book_slug(book_path: Path) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", book_path.stem.lower()).strip("_")
    return slug


# ---------------------------------------------------------------------------
# ISBN utilities
# ---------------------------------------------------------------------------

def _clean_isbn(raw: str) -> str:
    """Strip hyphens and spaces from an ISBN string."""
    return re.sub(r"[-\s]", "", raw.strip())


def _extract_isbn_from_filename(path: Path) -> str:
    """Try to find a 10- or 13-digit ISBN in the filename."""
    m = _ISBN_RE.search(path.stem)
    if m:
        return _clean_isbn(m.group(0))
    return ""


# ---------------------------------------------------------------------------
# File-level metadata extraction
# ---------------------------------------------------------------------------

def _extract_epub_metadata(epub_path: Path) -> dict:
    """
    Read OPF dc:* metadata from an EPUB file.
    Returns a dict with keys: title, authors, isbn, publisher, publish_year,
    language, description.
    """
    try:
        from ebooklib import epub as ebooklib_epub  # type: ignore
    except ImportError as exc:
        logger.warning("ebooklib not installed — EPUB metadata extraction skipped: %s", exc)
        return {}

    try:
        book = ebooklib_epub.read_epub(str(epub_path), options={"ignore_ncx": True})
    except Exception as exc:
        logger.warning("Could not read EPUB %s: %s", epub_path.name, exc)
        return {}

    def _dc(field: str) -> list[str]:
        items = book.get_metadata("DC", field) or []
        return [str(v[0]) if isinstance(v, tuple) else str(v) for v in items if v]

    title       = _dc("title")[0]   if _dc("title")   else ""
    authors     = _dc("creator")
    publisher   = _dc("publisher")[0] if _dc("publisher") else ""
    language    = _dc("language")[0]  if _dc("language")  else ""
    description = _dc("description")[0] if _dc("description") else ""

    # Date: various formats — try to extract a 4-digit year
    publish_year: int | None = None
    for date_str in _dc("date"):
        m = re.search(r"\b(1[89]\d\d|20\d\d)\b", date_str)
        if m:
            publish_year = int(m.group(1))
            break

    # ISBN from dc:identifier
    isbn = ""
    for ident in _dc("identifier"):
        cleaned = _clean_isbn(ident)
        if re.fullmatch(r"\d{10}", cleaned) or re.fullmatch(r"\d{13}", cleaned):
            isbn = cleaned
            break

    return {
        "title":        title,
        "authors":      authors,
        "isbn":         isbn,
        "publisher":    publisher,
        "publish_year": publish_year,
        "language":     language,
        "description":  description,
        "source":       "epub_opf",
    }


def _extract_pdf_metadata(pdf_path: Path) -> dict:
    """
    Read XMP / DocInfo metadata from a PDF.
    Returns the same shape as _extract_epub_metadata.
    """
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore[no-redef]
        except ImportError:
            logger.warning("pypdf not installed — PDF metadata extraction skipped")
            return {}

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        logger.warning("Could not read PDF %s: %s", pdf_path.name, exc)
        return {}

    info        = reader.metadata or {}
    title       = info.get("/Title",   "") or ""
    author_raw  = info.get("/Author",  "") or ""
    subject     = info.get("/Subject", "") or ""
    creator     = info.get("/Creator", "") or ""

    authors: list[str] = []
    if author_raw:
        # Split on common separators
        authors = [a.strip() for a in re.split(r"[;,&]|\\band\\b", author_raw) if a.strip()]

    publish_year: int | None = None
    creation_date = info.get("/CreationDate", "") or ""
    m = re.search(r"(1[89]\d\d|20\d\d)", creation_date)
    if m:
        publish_year = int(m.group(1))

    # Try XMP for richer data
    isbn = ""
    try:
        xmp = reader.xmp_metadata
        if xmp:
            xmp_str = str(xmp)
            mi = _ISBN_RE.search(xmp_str)
            if mi:
                isbn = _clean_isbn(mi.group(0))
    except Exception:
        pass

    return {
        "title":        title.strip(),
        "authors":      authors,
        "isbn":         isbn,
        "publisher":    "",
        "publish_year": publish_year,
        "language":     "",
        "description":  subject.strip() or creator.strip(),
        "source":       "pdf_docinfo",
    }


# ---------------------------------------------------------------------------
# OpenLibrary API
# ---------------------------------------------------------------------------

def _query_openlibrary_by_isbn(isbn: str) -> dict:
    """
    Query https://openlibrary.org/api/books for a given ISBN.
    Returns a merged dict of all useful fields, or {} on failure.
    """
    if not isbn:
        return {}

    url = (
        f"https://openlibrary.org/api/books"
        f"?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    )
    logger.info("  OpenLibrary: querying ISBN %s …", isbn)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "medical-rag/1.0 (research; axel@nrt-amsterdam.nl)"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw: dict = json.loads(resp.read())
    except (urllib.error.URLError, Exception) as exc:
        logger.warning("  OpenLibrary request failed: %s", exc)
        return {}

    key   = f"ISBN:{isbn}"
    entry = raw.get(key, {})
    if not entry:
        logger.info("  OpenLibrary: no record found for ISBN %s", isbn)
        return {}

    # Authors
    authors = [a.get("name", "") for a in entry.get("authors", [])]

    # Publishers
    publishers = [p.get("name", "") for p in entry.get("publishers", [])]

    # Publish year
    publish_year: int | None = None
    pub_date_raw = entry.get("publish_date", "")
    m = re.search(r"(1[89]\d\d|20\d\d)", pub_date_raw)
    if m:
        publish_year = int(m.group(1))

    # Identifiers
    identifiers = entry.get("identifiers", {})
    isbn_10 = (identifiers.get("isbn_10",  [""])[0] or "").strip()
    isbn_13 = (identifiers.get("isbn_13",  [""])[0] or "").strip()

    # Subjects
    subjects = [s.get("name", "") for s in entry.get("subjects", [])]

    # Pagination
    total_pages = entry.get("number_of_pages") or None

    # LC classification
    lc_class = ", ".join(
        c.get("key", "") for c in entry.get("classifications", {}).get("lc_classifications", [])
    )

    # Subtitle from full_title if present
    full_title  = entry.get("full_title", "") or entry.get("title", "")
    title       = entry.get("title", "")
    subtitle    = entry.get("subtitle", "")
    if not subtitle and ":" in full_title:
        parts    = full_title.split(":", 1)
        title    = title or parts[0].strip()
        subtitle = parts[1].strip()

    return {
        "title":        title,
        "subtitle":     subtitle,
        "authors":      authors,
        "publisher":    publishers[0] if publishers else "",
        "publish_year": publish_year,
        "isbn_10":      isbn_10,
        "isbn_13":      isbn_13,
        "total_pages":  total_pages,
        "subjects":     subjects,
        "lc_class":     lc_class,
        "metadata_source": "openlibrary",
    }


def _search_openlibrary_by_title(title: str) -> dict:
    """
    Fallback: search OpenLibrary by title when ISBN is not available.
    Returns metadata for the best match, or {}.
    """
    if not title:
        return {}

    query = urllib.parse.urlencode({"q": title, "limit": 1, "fields": "isbn,title,author_name,publisher,first_publish_year,number_of_pages_median"})
    url   = f"https://openlibrary.org/search.json?{query}"
    logger.info("  OpenLibrary: title search for '%s' …", title[:60])
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "medical-rag/1.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = json.loads(resp.read())
    except Exception as exc:
        logger.warning("  OpenLibrary title search failed: %s", exc)
        return {}

    docs = raw.get("docs", [])
    if not docs:
        return {}

    doc = docs[0]
    isbns = doc.get("isbn", [])
    isbn_13 = next((i for i in isbns if len(i) == 13), "")
    isbn_10 = next((i for i in isbns if len(i) == 10), "")

    return {
        "title":        doc.get("title", ""),
        "subtitle":     "",
        "authors":      doc.get("author_name", []),
        "publisher":    (doc.get("publisher") or [""])[0],
        "publish_year": doc.get("first_publish_year"),
        "isbn_10":      isbn_10,
        "isbn_13":      isbn_13,
        "total_pages":  doc.get("number_of_pages_median"),
        "subjects":     [],
        "lc_class":     "",
        "metadata_source": "openlibrary_search",
    }


# ---------------------------------------------------------------------------
# Google Books API
# ---------------------------------------------------------------------------

def _query_google_books(isbn: str) -> dict:
    """
    Query the Google Books API (no key needed for basic lookups).
    Returns description, categories, page count, language; or {} on failure.
    """
    if not isbn:
        return {}

    url = (
        f"https://www.googleapis.com/books/v1/volumes"
        f"?q=isbn:{isbn}&maxResults=1"
    )
    logger.info("  Google Books: querying ISBN %s …", isbn)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "medical-rag/1.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = json.loads(resp.read())
    except Exception as exc:
        logger.warning("  Google Books request failed: %s", exc)
        return {}

    items = raw.get("items", [])
    if not items:
        logger.info("  Google Books: no result for ISBN %s", isbn)
        return {}

    vi = items[0].get("volumeInfo", {})
    return {
        "description": vi.get("description", ""),
        "categories":  vi.get("categories", []),
        "total_pages": vi.get("pageCount"),
        "language":    vi.get("language", ""),
        "thumbnail":   vi.get("imageLinks", {}).get("thumbnail", ""),
        "metadata_source_g": "google_books",
    }


# ---------------------------------------------------------------------------
# Citation generation
# ---------------------------------------------------------------------------

def _format_apa_authors(authors: list[str]) -> str:
    if not authors:
        return "Unknown Author"
    parts = []
    for name in authors:
        if "," in name:
            last, first = name.split(",", 1)
            initials = "".join(f"{w[0]}." for w in first.split() if w)
            parts.append(f"{last.strip()}, {initials}")
        else:
            words = name.split()
            if len(words) >= 2:
                initials = "".join(f"{w[0]}." for w in words[:-1])
                parts.append(f"{words[-1]}, {initials}")
            else:
                parts.append(name)
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]}, & {parts[1]}"
    return ", ".join(parts[:-1]) + f", & {parts[-1]}"


def _format_vancouver_authors(authors: list[str]) -> str:
    if not authors:
        return "Unknown Author"
    listed = authors[:6]
    parts  = []
    for name in listed:
        if "," in name:
            last, first = name.split(",", 1)
            initials = "".join(w[0] for w in first.split() if w)
            parts.append(f"{last.strip()} {initials}")
        else:
            words = name.split()
            if len(words) >= 2:
                initials = "".join(w[0] for w in words[:-1])
                parts.append(f"{words[-1]} {initials}")
            else:
                parts.append(name)
    suffix = " et al." if len(authors) > 6 else "."
    return ", ".join(parts) + suffix


def _format_chicago_authors(authors: list[str]) -> str:
    if not authors:
        return "Unknown Author"
    if len(authors) == 1:
        return authors[0]
    if len(authors) <= 3:
        first = authors[0]
        rest  = ", ".join(authors[1:-1])
        last  = authors[-1]
        if rest:
            return f"{first}, {rest}, and {last}"
        return f"{first} and {last}"
    return f"{authors[0]} et al."


def _generate_apa(meta: dict) -> str:
    authors   = meta.get("authors", [])
    year      = meta.get("publish_year", "n.d.")
    title     = meta.get("title", "Unknown Title")
    subtitle  = meta.get("subtitle", "")
    edition   = meta.get("edition", "")
    publisher = meta.get("publisher", "")

    full_title  = f"{title}: {subtitle}" if subtitle else title
    edition_str = f" ({edition} ed.)" if edition else ""
    parts = [
        f"{_format_apa_authors(authors)}",
        f"({year}).",
        f"{full_title}{edition_str}.",
    ]
    if publisher:
        parts.append(f"{publisher}.")
    return " ".join(parts).strip()


def _generate_vancouver(meta: dict) -> str:
    authors   = meta.get("authors", [])
    year      = meta.get("publish_year", "")
    title     = meta.get("title", "Unknown Title")
    subtitle  = meta.get("subtitle", "")
    edition   = meta.get("edition", "")
    publisher = meta.get("publisher", "")
    city      = meta.get("publisher_city", "")

    full_title  = f"{title}: {subtitle}" if subtitle else title
    edition_str = f" {edition} ed." if edition else ""
    place       = f"{city}: " if city else ""
    parts = [
        f"{_format_vancouver_authors(authors)}",
        f"{full_title}.{edition_str}",
        f"{place}{publisher};",
        f"{year}.",
    ]
    return " ".join(p for p in parts if p.strip()).strip()


def _generate_chicago(meta: dict) -> str:
    authors   = meta.get("authors", [])
    year      = meta.get("publish_year", "")
    title     = meta.get("title", "Unknown Title")
    subtitle  = meta.get("subtitle", "")
    edition   = meta.get("edition", "")
    publisher = meta.get("publisher", "")
    city      = meta.get("publisher_city", "")

    full_title  = f"{title}: {subtitle}" if subtitle else title
    edition_str = f" {edition} ed." if edition else ""
    place       = f"{city}: " if city else ""
    year_str    = f", {year}" if year else ""
    parts = [
        f"{_format_chicago_authors(authors)}.",
        f"{full_title}.{edition_str}",
        f"{place}{publisher}{year_str}.",
    ]
    return " ".join(p for p in parts if p.strip()).strip()


# ---------------------------------------------------------------------------
# Build and merge a book record
# ---------------------------------------------------------------------------

def _merge(primary: dict, *fallbacks: dict, field: str) -> object:
    """Return the first non-empty value for *field* across dicts."""
    for d in (primary, *fallbacks):
        val = d.get(field)
        if val or val == 0:
            return val
    return None


def _build_book_record(
    book_path: Path,
    file_meta: dict,
    ol_meta:   dict,
    gb_meta:   dict,
) -> dict:
    """
    Merge metadata from all sources into a single canonical book record.
    OpenLibrary takes priority over file metadata; Google Books fills gaps.
    """
    slug     = _book_slug(book_path)
    title    = (
        ol_meta.get("title")
        or file_meta.get("title")
        or book_path.stem
    )
    subtitle = ol_meta.get("subtitle") or ""
    authors  = (
        ol_meta.get("authors")
        or file_meta.get("authors")
        or []
    )
    publisher = (
        ol_meta.get("publisher")
        or file_meta.get("publisher")
        or ""
    )
    publish_year = (
        ol_meta.get("publish_year")
        or file_meta.get("publish_year")
    )
    isbn_10 = ol_meta.get("isbn_10") or file_meta.get("isbn", "")
    isbn_13 = ol_meta.get("isbn_13") or (
        file_meta.get("isbn", "") if len(file_meta.get("isbn","")) == 13 else ""
    )
    language    = file_meta.get("language") or gb_meta.get("language") or ""
    total_pages = ol_meta.get("total_pages") or gb_meta.get("total_pages")
    subjects    = ol_meta.get("subjects") or gb_meta.get("categories") or []
    description = (
        file_meta.get("description")
        or gb_meta.get("description")
        or ""
    )
    metadata_source = ol_meta.get("metadata_source") or file_meta.get("source") or "filename"

    meta: dict = {
        "slug":                slug,
        "filename":            book_path.name,
        "title":               title,
        "subtitle":            subtitle,
        "authors":             authors,
        "editors":             [],
        "publisher":           publisher,
        "publisher_city":      "",
        "publish_year":        publish_year,
        "edition":             "",
        "isbn_10":             isbn_10,
        "isbn_13":             isbn_13,
        "language":            language,
        "total_pages":         total_pages,
        "subjects":            subjects,
        "description":         description[:500] if description else "",
        "lc_class":            ol_meta.get("lc_class", ""),
        "metadata_source":     metadata_source,
        "metadata_retrieved":  datetime.datetime.utcnow().isoformat() + "Z",
        "ingested":            False,
        "ingestion_date":      None,
        "total_chunks":        0,
        "total_figures":       0,
        # Citations generated below
        "citation_apa":        "",
        "citation_vancouver":  "",
        "citation_chicago":    "",
    }

    meta["citation_apa"]       = _generate_apa(meta)
    meta["citation_vancouver"] = _generate_vancouver(meta)
    meta["citation_chicago"]   = _generate_chicago(meta)

    return meta


# ---------------------------------------------------------------------------
# books_metadata.json persistence
# ---------------------------------------------------------------------------

def load_books_metadata(path: Path = BOOKS_METADATA_PATH) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as exc:
            logger.warning("Could not load %s: %s", path, exc)
    return {}


def save_books_metadata(metadata: dict, path: Path = BOOKS_METADATA_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2))
    logger.info("Saved metadata for %d book(s) → %s", len(metadata), path)


# ---------------------------------------------------------------------------
# Process a single book
# ---------------------------------------------------------------------------

def process_book(book_path: Path, existing_meta: dict, force_refresh: bool = False) -> dict:
    """
    Fetch and merge metadata for one book.  Returns the record dict.
    Skips API calls if a non-empty record already exists and force_refresh is False.
    """
    slug = _book_slug(book_path)

    if not force_refresh and slug in existing_meta and existing_meta[slug].get("title"):
        logger.info("  %s — already in metadata, skipping (use --refresh to re-fetch)", book_path.name)
        return existing_meta[slug]

    logger.info("Processing: %s", book_path.name)

    # 1. Extract from file
    suffix = book_path.suffix.lower()
    if suffix == ".epub":
        file_meta = _extract_epub_metadata(book_path)
    elif suffix == ".pdf":
        file_meta = _extract_pdf_metadata(book_path)
    else:
        file_meta = {}

    # 2. Determine ISBN (file > filename)
    isbn = file_meta.get("isbn", "") or _extract_isbn_from_filename(book_path)
    logger.info("  ISBN: %s", isbn or "not found")

    # 3. OpenLibrary
    time.sleep(_API_DELAY_SECONDS)
    ol_meta = _query_openlibrary_by_isbn(isbn) if isbn else {}

    # 3b. OpenLibrary title fallback
    if not ol_meta and file_meta.get("title"):
        time.sleep(_API_DELAY_SECONDS)
        ol_meta = _search_openlibrary_by_title(file_meta["title"])

    # 4. Google Books
    effective_isbn = isbn or ol_meta.get("isbn_13") or ol_meta.get("isbn_10") or ""
    time.sleep(_API_DELAY_SECONDS)
    gb_meta = _query_google_books(effective_isbn) if effective_isbn else {}

    # 5. Build and return record
    record = _build_book_record(book_path, file_meta, ol_meta, gb_meta)
    logger.info(
        "  → %s (%s) — %s",
        record["title"] or book_path.stem,
        record["publish_year"] or "?",
        record["metadata_source"],
    )
    return record


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch bibliographic metadata for medical RAG books",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--books-dir",
        type=Path,
        default=Path("/root/medical-rag/books"),
        help="Directory containing .pdf / .epub files (default: ./books)",
    )
    group.add_argument(
        "--file",
        type=Path,
        help="Process a single book file",
    )
    group.add_argument(
        "--isbn",
        help="Fetch metadata for a specific ISBN and print the result",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-fetch from APIs even if the record already exists",
    )
    parser.add_argument(
        "--slug",
        help="With --refresh: limit refresh to a single book slug",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BOOKS_METADATA_PATH,
        help=f"Output JSON file (default: {BOOKS_METADATA_PATH})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ── ISBN-only mode ───────────────────────────────────────────────────────
    if args.isbn:
        isbn    = _clean_isbn(args.isbn)
        ol_meta = _query_openlibrary_by_isbn(isbn)
        gb_meta = _query_google_books(isbn)
        result  = {"openlibrary": ol_meta, "google_books": gb_meta}
        print(json.dumps(result, indent=2))
        return

    # ── Collect book files ───────────────────────────────────────────────────
    if args.file:
        book_files = [args.file.resolve()]
    else:
        books_dir = args.books_dir.resolve()
        if not books_dir.exists():
            logger.error("Books directory not found: %s", books_dir)
            return
        book_files = sorted(
            p for p in books_dir.iterdir()
            if p.suffix.lower() in {".pdf", ".epub"}
        )

    if not book_files:
        logger.warning("No books found.")
        return

    logger.info("Found %d book(s)", len(book_files))

    existing_meta = load_books_metadata(args.output)
    updated       = dict(existing_meta)

    for book_path in book_files:
        slug           = _book_slug(book_path)
        force_refresh  = args.refresh and (not args.slug or args.slug == slug)
        record         = process_book(book_path, existing_meta, force_refresh=force_refresh)
        updated[slug]  = record

    save_books_metadata(updated, args.output)

    # Print summary table
    print(f"\n{'Slug':<30} {'Title':<50} {'Year':<6} {'Source'}")
    print("-" * 100)
    for slug, rec in sorted(updated.items()):
        print(
            f"{slug:<30} "
            f"{(rec.get('title') or '')[:49]:<50} "
            f"{str(rec.get('publish_year') or ''):<6} "
            f"{rec.get('metadata_source', '')}"
        )


if __name__ == "__main__":
    main()
