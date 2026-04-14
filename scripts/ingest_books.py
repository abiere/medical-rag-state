"""
Medical RAG – Book Ingestion Pipeline  (PDF + EPUB)

Extracts text and figures from PDF/EPUB books, indexes into Qdrant via
LlamaIndex, and attaches rich bibliographic citations to every chunk.

New in this version
───────────────────
• Scanned-PDF detection — if avg text < OCR_CHARS_PER_PAGE_THRESHOLD
  chars/page the Docling pass is re-run with EasyOCR enabled.
• Figure naming: {slug}_p{page}_fig{n}.png  (deterministic, traceable)
• Per-figure payload: caption, figure_labels (OCR), image_type, image_description
• Figure-number detection: "Fig. 4.52", "Abb. 3.1", "Afb. 2.4", …
• Full citation object on every Qdrant chunk (APA + Vancouver), loaded from
  data/books_metadata.json (populated by scripts/fetch_book_metadata.py)
• Per-book processing logs → data/processing_logs/{slug}.json
• data/image_memory.json initialised on first run

Usage
─────
    python scripts/ingest_books.py --books-dir ./books [--collection anatomy]
    python scripts/ingest_books.py --books-dir ./books --dry-run

Requirements
────────────
    pip install docling docling-core easyocr \
                llama-index llama-index-vector-stores-qdrant \
                llama-index-embeddings-huggingface \
                qdrant-client ebooklib beautifulsoup4 lxml \
                pypdf pillow numpy
"""

from __future__ import annotations

import argparse
import base64
import datetime
import hashlib
import io
import json
import logging
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

QDRANT_URL       = "http://localhost:6333"
OLLAMA_BASE_URL  = "http://localhost:11434"
OLLAMA_MODEL     = "llama3.1:8b"

EMBED_MODEL_NAME = "BAAI/bge-large-en-v1.5"
EMBED_DIM        = 1024

CHUNK_SIZE    = 512
CHUNK_OVERLAP = 64

BASE_DIR            = Path("/root/medical-rag")
IMAGES_DIR          = BASE_DIR / "data" / "extracted_images"
LOGS_DIR            = BASE_DIR / "data" / "processing_logs"
IMAGE_MEMORY_PATH   = BASE_DIR / "data" / "image_memory.json"
BOOKS_METADATA_PATH        = BASE_DIR / "data" / "books_metadata.json"
VIDEO_DOCUMENT_LINKS_PATH  = BASE_DIR / "data" / "video_document_links.json"

# Maps content_type → Qdrant collection name
CONTENT_TYPE_COLLECTION_MAP: dict[str, str] = {
    "medical_literature": "medical_literature",
    "training_nrt":       "training_materials",
    "training_qat":       "training_materials",
    "device_pemf":        "device_protocols",
    "device_rlt":         "device_protocols",
}

# If a PDF averages fewer characters per page than this, enable OCR
OCR_CHARS_PER_PAGE_THRESHOLD = 50

# EPUB image MIME types (SVG intentionally excluded — decorative)
_MIME_TO_EXT: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png":  ".png",
    "image/gif":  ".gif",
    "image/webp": ".webp",
    "image/tiff": ".tiff",
}

# Detects figure numbers in caption / surrounding text
_FIGURE_NUMBER_RE = re.compile(
    r"\b(?:Fig(?:ure)?|Afb|Abb)\.?\s*"   # prefix
    r"(\d+[\.\-]\d+(?:[\.\-]\d+)?|\d+)",  # number (e.g. 4.52 or 12)
    re.IGNORECASE,
)

# Device settings extraction — PEMF / RLT documents
_DEV_SETTING_RE   = re.compile(r"\bsetting\s+(\d+)",                        re.IGNORECASE)
_DEV_PROGRAM_RE   = re.compile(r"\bprogram(?:ma)?\s+(\d+)",                 re.IGNORECASE)
_DEV_INTENSITY_RE = re.compile(r"\bintensit(?:y|eit)\s*([\d]+(?:[-–]\d+)?)", re.IGNORECASE)
_DEV_DURATION_RE  = re.compile(
    r"\b(?:duur|duration)[:\s]+(\d+)\s*min(?:uten?)?",                      re.IGNORECASE
)
_DEV_INDICATIE_RE = re.compile(r"\bindicati[eo][:\s]+([^.\n;]{3,80})",      re.IGNORECASE)
_DEV_CONTRA_RE    = re.compile(
    r"\bcontra[-\s]?indicati[eo][:\s]+([^.\n;]{3,80})",                     re.IGNORECASE
)
_BODY_REGION_KEYWORDS: list[str] = [
    "lumbal", "cervical", "thoracal", "knie", "schouder", "heup",
    "pols", "enkel", "rug", "nek", "elleboog", "bekken", "ribben",
    "sacral", "gluteal", "hamstring", "quadriceps",
]

# ---------------------------------------------------------------------------
# Lazy singletons  (initialised on first use, shared across all books)
# ---------------------------------------------------------------------------

_easyocr_reader: Any = None     # None = not yet initialised
_ollama_vision_model: Any = False  # False = unchecked; None = unavailable


def _get_ocr_reader():
    """Lazy-init shared EasyOCR reader (English, CPU only)."""
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr  # type: ignore
            logger.info("Initialising EasyOCR reader (first use) …")
            _easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        except ImportError:
            logger.warning("easyocr not installed — figure label extraction disabled")
            _easyocr_reader = False   # False = permanently disabled
    return _easyocr_reader if _easyocr_reader is not False else None


def _get_ollama_vision_model() -> str | None:
    """Return the name of a loaded Ollama vision model, or None if absent."""
    global _ollama_vision_model
    if _ollama_vision_model is False:
        try:
            with urllib.request.urlopen(
                f"{OLLAMA_BASE_URL}/api/tags", timeout=5
            ) as resp:
                tags = json.loads(resp.read())
            models = [m["name"] for m in tags.get("models", [])]
            _ollama_vision_model = next(
                (m for m in models if "llava" in m.lower()), None
            )
            if _ollama_vision_model:
                logger.info("Ollama vision model: %s", _ollama_vision_model)
            else:
                logger.info("No Ollama vision model — image_description will be 'pending'")
        except Exception as exc:
            logger.debug("Ollama model query failed: %s", exc)
            _ollama_vision_model = None
    return _ollama_vision_model  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _book_slug(book_path: Path) -> str:
    """Lowercase underscore-sanitised stem: 'Sobotta Vol1.epub' → 'sobotta_vol1'."""
    slug = re.sub(r"[^a-z0-9]+", "_", book_path.stem.lower()).strip("_")
    return slug


def _save_figure(data: bytes, out_name: str, images_dir: Path) -> Path:
    """
    Save *data* as *images_dir/out_name*. Idempotent — skips write if the
    file already exists. Returns the resolved absolute path.
    """
    images_dir.mkdir(parents=True, exist_ok=True)
    out_path = images_dir / out_name
    if not out_path.exists():
        out_path.write_bytes(data)
    return out_path.resolve()


def _ocr_figure_labels(pil_image) -> list[str]:
    """
    Extract text labels found inside a figure using EasyOCR.
    Returns [] if EasyOCR is unavailable or the figure contains no readable text.
    """
    reader = _get_ocr_reader()
    if reader is None:
        return []
    try:
        import numpy as np  # type: ignore
        img_array = np.array(pil_image.convert("RGB"))
        results = reader.readtext(img_array, detail=1)
        return [
            text.strip()
            for _, text, conf in results
            if conf > 0.5 and len(text.strip()) > 1
        ]
    except Exception as exc:
        logger.debug("EasyOCR label extraction failed: %s", exc)
        return []


def _classify_image_type(is_table: bool, figure_labels: list[str]) -> str:
    """Heuristic classification: table > diagram (many text labels) > figure."""
    if is_table:
        return "table"
    if len(figure_labels) > 3:
        return "diagram"
    return "figure"


def _describe_image_ollama(img_path: Path) -> str:
    """
    Generate a 1-sentence description via an Ollama vision model (LLaVA).
    Returns 'pending' immediately if no vision model is loaded.
    """
    vision_model = _get_ollama_vision_model()
    if not vision_model:
        return "pending"
    try:
        img_b64 = base64.b64encode(img_path.read_bytes()).decode()
        payload = json.dumps({
            "model":  vision_model,
            "prompt": "Describe this medical or anatomical image in one concise sentence.",
            "images": [img_b64],
            "stream": False,
        }).encode()
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read()).get("response", "").strip()
    except Exception as exc:
        logger.debug("Ollama vision failed for %s: %s", img_path.name, exc)
        return "pending"


def _detect_figure_number(caption: str, surrounding_text: str = "") -> str:
    """
    Detect official figure numbers like 'Fig. 4.52', 'Figure 12', 'Afb. 2.4'.
    Checks caption first, then surrounding text. Returns '' if not found.
    """
    for text in (caption, surrounding_text):
        m = _FIGURE_NUMBER_RE.search(text)
        if m:
            return m.group(0).strip()
    return ""


# ---------------------------------------------------------------------------
# Bibliographic citation helpers
# ---------------------------------------------------------------------------

def _load_books_metadata() -> dict:
    """Load data/books_metadata.json; return {} if missing or malformed."""
    if BOOKS_METADATA_PATH.exists():
        try:
            return json.loads(BOOKS_METADATA_PATH.read_text())
        except Exception as exc:
            logger.warning("Could not load books_metadata.json: %s", exc)
    return {}


def _format_apa_authors(authors: list[str]) -> str:
    """Format author list for APA 7th edition."""
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
    """Format author list for Vancouver style (max 6; et al. after)."""
    if not authors:
        return "Unknown Author"
    listed = authors[:6]
    parts = []
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


def _build_citation_payload(
    book_meta: dict,
    page: int,
    figure_number: str = "",
    caption: str = "",
) -> dict:
    """
    Build a structured citation dict for a Qdrant chunk.
    Uses metadata from books_metadata.json if available; gracefully
    degrades to minimal citation when fields are missing.
    """
    authors   = book_meta.get("authors", [])
    year      = book_meta.get("publish_year", "")
    title     = book_meta.get("title", book_meta.get("filename", "Unknown"))
    edition   = book_meta.get("edition", "")
    publisher = book_meta.get("publisher", "")

    edition_str = f" ({edition} ed.)" if edition else ""

    apa = (
        f"{_format_apa_authors(authors)} ({year}). "
        f"{title}{edition_str}. {publisher}. p. {page}"
    ).strip(". ")

    van_edition = f" {edition} ed." if edition else ""
    page_ref = f" {figure_number}," if figure_number else ""
    vancouver = (
        f"{_format_vancouver_authors(authors)} "
        f"{title}.{van_edition} {publisher}; {year}.{page_ref} p. {page}."
    ).strip()

    return {
        "authors":        authors,
        "year":           year,
        "title":          title,
        "edition":        edition,
        "publisher":      publisher,
        "page":           page,
        "figure_number":  figure_number,
        "figure_caption": caption,
        "apa":            apa,
        "vancouver":      vancouver,
    }


# ---------------------------------------------------------------------------
# Content-type routing and device settings extraction
# ---------------------------------------------------------------------------

def _collection_for_content_type(content_type: str) -> str:
    """Return the Qdrant collection name for a given content_type."""
    return CONTENT_TYPE_COLLECTION_MAP.get(content_type, "medical_literature")


def _extract_device_settings(text: str, content_type: str) -> dict:
    """
    Parse structured PEMF / RLT settings from a text chunk.

    Detects: setting, program, intensity range, duration, indication,
    contraindication, and body region.  Returns a dict of those fields
    (values are None when not found so they remain filterable in Qdrant).
    """
    device = "PEMF" if content_type == "device_pemf" else "RLT"

    def _first(pattern: re.Pattern, txt: str):
        m = pattern.search(txt)
        return m.group(1).strip() if m else None

    setting      = _first(_DEV_SETTING_RE,   text)
    program      = _first(_DEV_PROGRAM_RE,   text)
    intensity    = _first(_DEV_INTENSITY_RE, text)
    duration_raw = _first(_DEV_DURATION_RE,  text)
    indication   = _first(_DEV_INDICATIE_RE, text)
    contraindic  = _first(_DEV_CONTRA_RE,    text)

    duration_min: int | None = None
    if duration_raw and duration_raw.isdigit():
        duration_min = int(duration_raw)

    body_region: str = ""
    text_lower = text.lower()
    for kw in _BODY_REGION_KEYWORDS:
        if kw in text_lower:
            body_region = kw
            break
    # Also check indication text
    if not body_region and indication:
        ind_lower = indication.lower()
        for kw in _BODY_REGION_KEYWORDS:
            if kw in ind_lower:
                body_region = kw
                break

    return {
        "device":              device,
        "setting":             setting,
        "program":             program,
        "intensity_range":     intensity,
        "duration_minutes":    duration_min,
        "indication":          indication,
        "contraindication":    contraindic,
        "body_region":         body_region,
    }


def _ensure_video_document_links(path: Path) -> None:
    """Create data/video_document_links.json as an empty object if absent."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n")
        logger.info("Initialised video_document_links: %s", path)


# ---------------------------------------------------------------------------
# PDF extraction — Docling (with EasyOCR fallback for scanned PDFs)
# ---------------------------------------------------------------------------

def _estimate_pdf_text_density(pdf_path: Path) -> float:
    """
    Return average characters per page.  Uses pypdf (fast); if unavailable
    returns 9999 (assumes digital PDF — no OCR needed).
    """
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            logger.debug("pypdf not installed; assuming digital PDF: %s", pdf_path.name)
            return 9999.0
    try:
        reader = PdfReader(str(pdf_path))
        total = sum(len(page.extract_text() or "") for page in reader.pages)
        return total / max(1, len(reader.pages))
    except Exception as exc:
        logger.warning("PDF density pre-scan failed (%s): %s", pdf_path.name, exc)
        return 9999.0


def extract_pdf(pdf_path: Path, images_dir: Path) -> tuple[list[dict], dict]:
    """
    Extract per-page sections from a PDF via Docling.

    Auto-enables EasyOCR when text density < OCR_CHARS_PER_PAGE_THRESHOLD.
    Per-figure data (caption, labels, type, description, figure_number) is
    aggregated to page level and stored in the section dict.

    Returns (sections, stats).
    """
    try:
        from docling.datamodel.base_models import InputFormat  # type: ignore
        from docling.datamodel.pipeline_options import PdfPipelineOptions  # type: ignore
        from docling.document_converter import (  # type: ignore
            DocumentConverter, PdfFormatOption,
        )
        from docling_core.types.doc import PictureItem, TableItem  # type: ignore
    except ImportError as exc:
        raise ImportError("pip install docling docling-core") from exc

    logger.info("Extracting PDF: %s", pdf_path.name)
    slug = _book_slug(pdf_path)

    # ── Scanned-PDF detection ────────────────────────────────────────────────
    avg_chars = _estimate_pdf_text_density(pdf_path)
    use_ocr   = avg_chars < OCR_CHARS_PER_PAGE_THRESHOLD
    if use_ocr:
        logger.info(
            "  %.1f avg chars/page < threshold %d — enabling EasyOCR",
            avg_chars, OCR_CHARS_PER_PAGE_THRESHOLD,
        )
    else:
        logger.info("  %.1f avg chars/page — digital PDF, OCR skipped", avg_chars)

    # ── Pipeline options ─────────────────────────────────────────────────────
    opts_kwargs: dict = {
        "generate_picture_images": True,
        "images_scale":            2.0,
        "do_ocr":                  use_ocr,
    }
    if use_ocr:
        try:
            from docling.datamodel.pipeline_options import EasyOcrOptions  # type: ignore
            opts_kwargs["ocr_options"] = EasyOcrOptions()
        except ImportError:
            logger.warning(
                "EasyOcrOptions not available in this Docling version — "
                "OCR will use the Docling default engine"
            )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=PdfPipelineOptions(**opts_kwargs)
            )
        }
    )
    result = converter.convert(str(pdf_path))
    doc    = result.document

    # ── Per-page accumulators ────────────────────────────────────────────────
    pages: dict[int, dict]         = {}
    page_fig_counters: dict[int, int] = {}

    stats: dict = {
        "book":                    pdf_path.name,
        "slug":                    slug,
        "format":                  "pdf",
        "ocr_applied":             use_ocr,
        "avg_chars_per_page":      round(avg_chars, 1),
        "total_pages":             0,
        "pages_with_ocr":          0,
        "figures_extracted":       0,
        "figures_with_captions":   0,
        "figures_without_captions":0,
        "figures_with_labels":     0,
        "figures_without_labels":  0,
        "errors":                  [],
        "processed_at":            datetime.datetime.utcnow().isoformat() + "Z",
    }

    def _init_page(page_no: int) -> None:
        if page_no not in pages:
            pages[page_no] = {
                "text_parts":        [],
                "image_links":       [],
                "captions":          [],
                "figure_labels_all": [],
                "figure_numbers":    [],
                "image_type":        None,
                "image_description": None,
            }
            page_fig_counters[page_no] = 0

    for element, _level in doc.iterate_items():
        page_no = element.prov[0].page_no if element.prov else 0
        _init_page(page_no)

        is_picture = isinstance(element, PictureItem)
        is_table   = isinstance(element, TableItem)

        if is_picture or is_table:
            pil_img = getattr(getattr(element, "image", None), "pil_image", None)
            if pil_img is None:
                continue

            page_fig_counters[page_no] += 1
            fig_n    = page_fig_counters[page_no]
            out_name = f"{slug}_p{page_no}_fig{fig_n}.png"

            buf = io.BytesIO()
            pil_img.save(buf, "PNG")
            try:
                img_path = _save_figure(buf.getvalue(), out_name, images_dir)
            except Exception as exc:
                err = f"p{page_no} fig{fig_n}: save failed — {exc}"
                stats["errors"].append(err)
                logger.warning("  %s", err)
                continue

            pages[page_no]["image_links"].append(str(img_path))
            stats["figures_extracted"] += 1

            # Caption
            caption = ""
            if is_picture:
                caption = element.caption_text(doc=doc) or ""
            pages[page_no]["captions"].append(caption)
            if caption:
                stats["figures_with_captions"] += 1
            else:
                stats["figures_without_captions"] += 1

            # Figure number from caption
            fig_num = _detect_figure_number(caption)
            if fig_num:
                pages[page_no]["figure_numbers"].append(fig_num)

            # Labels via OCR
            labels = _ocr_figure_labels(pil_img)
            pages[page_no]["figure_labels_all"].extend(labels)
            if labels:
                stats["figures_with_labels"] += 1
            else:
                stats["figures_without_labels"] += 1

            # Image type and vision description (first figure per page wins)
            if pages[page_no]["image_type"] is None:
                pages[page_no]["image_type"] = _classify_image_type(is_table, labels)
            if pages[page_no]["image_description"] is None:
                pages[page_no]["image_description"] = _describe_image_ollama(img_path)

            # Inline text marker
            marker = f"[Image: {caption}]" if caption else "[Image]"
            pages[page_no]["text_parts"].append(marker)

            if is_table:
                table_text = getattr(element, "text", None)
                if table_text and table_text.strip():
                    pages[page_no]["text_parts"].append(table_text.strip())

        else:
            text = getattr(element, "text", None)
            if text and text.strip():
                pages[page_no]["text_parts"].append(text.strip())

    # ── Build section dicts ──────────────────────────────────────────────────
    sections: list[dict] = []
    for page_no in sorted(pages):
        data      = pages[page_no]
        full_text = "\n".join(data["text_parts"]).strip()
        if not full_text and not data["image_links"]:
            continue

        combined_caption   = " | ".join(c for c in data["captions"] if c)
        combined_fig_num   = data["figure_numbers"][0] if data["figure_numbers"] else ""
        deduped_labels     = list(dict.fromkeys(data["figure_labels_all"]))

        sections.append({
            "page_number":       page_no,
            "section_number":    page_no,
            "text":              full_text,
            "image_links":       data["image_links"],
            "source_file":       pdf_path.name,
            "source_path":       str(pdf_path),
            "format":            "pdf",
            "chunk_hash":        hashlib.md5(
                f"{pdf_path.name}:p{page_no}:{full_text[:64]}".encode()
            ).hexdigest(),
            # ── Figure metadata ──
            "caption":           combined_caption,
            "figure_labels":     deduped_labels,
            "image_type":        data["image_type"] or "",
            "image_description": data["image_description"] or "",
            "figure_number":     combined_fig_num,
            # ── Citation (filled in main() from books_metadata.json) ──
            "citation":          {},
        })

    stats["total_pages"]    = len(pages)
    stats["pages_with_ocr"] = len(pages) if use_ocr else 0

    logger.info(
        "  Extracted %d pages, %d figures (OCR: %s)",
        len(sections),
        stats["figures_extracted"],
        use_ocr,
    )
    return sections, stats


# ---------------------------------------------------------------------------
# EPUB extraction — ebooklib + BeautifulSoup4
# ---------------------------------------------------------------------------

def _build_epub_cross_ref_map(book) -> dict[str, list[str]]:
    """
    Pass 1 — map anchor ids to the description text that links to them.

    Resolves the anatomy-atlas pattern where a "Plates" chapter holds images
    (<figure id="plate_i">) and a "Descriptions" chapter holds the captions
    (<a href="plates.xhtml#plate_i">Plate I. The brachial plexus…</a>).
    """
    import ebooklib  # type: ignore
    from bs4 import BeautifulSoup  # type: ignore

    ref_map: dict[str, list[str]] = {}
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "lxml")
        for a_tag in soup.find_all("a", href=True):
            href: str = a_tag["href"]
            if "#" not in href:
                continue
            anchor = href.split("#", 1)[-1].strip()
            if not anchor:
                continue
            parent = a_tag.find_parent(["p", "li", "div", "td", "dd"])
            context = (
                parent.get_text(separator=" ", strip=True)
                if parent
                else a_tag.get_text(strip=True)
            )
            if len(context) > 8:
                ref_map.setdefault(anchor, []).append(context[:600])
    return ref_map


def _image_surrounding_text(img_tag, n_siblings: int = 2) -> str:
    """
    Collect immediate visual context: alt text, figcaption, sibling blocks.
    Returns a '|'-separated string for the [Image: …] inline marker.
    """
    texts: list[str] = []

    alt = img_tag.get("alt", "").strip()
    if alt:
        texts.append(alt)

    container = img_tag.find_parent(["figure", "div", "td"]) or img_tag.parent
    if container:
        figcap = container.find("figcaption")
        if figcap:
            cap_text = figcap.get_text(strip=True)
            if cap_text and cap_text not in texts:
                texts.append(cap_text)

    block_tags = ["p", "h1", "h2", "h3", "h4", "h5", "div", "li"]
    pivot  = container or img_tag
    before: list[str] = []
    nxt    = pivot
    for _ in range(n_siblings):
        sib = nxt.find_previous_sibling(block_tags) if nxt else None
        if sib:
            t = sib.get_text(separator=" ", strip=True)
            if t:
                before.insert(0, t)
        nxt = sib

    pivot = container or img_tag
    after: list[str] = []
    prv   = pivot
    for _ in range(n_siblings):
        sib = prv.find_next_sibling(block_tags) if prv else None
        if sib:
            t = sib.get_text(separator=" ", strip=True)
            if t:
                after.append(t)
        prv = sib

    all_parts = before + texts + after
    seen:   set[str]  = set()
    unique: list[str] = []
    for p in all_parts:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return " | ".join(unique)


def _resolve_epub_img_src(src: str, item_name: str) -> str:
    """Resolve an <img src="…"> relative path to a canonical EPUB item name."""
    item_dir = str(Path(item_name).parent)
    raw      = "/".join([item_dir, src]) if item_dir != "." else src
    parts: list[str] = []
    for part in raw.replace("\\", "/").split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part and part != ".":
            parts.append(part)
    return "/".join(parts)


def extract_epub(epub_path: Path, images_dir: Path) -> tuple[list[dict], dict]:
    """
    Extract per-section records from an EPUB (ebooklib + BeautifulSoup4).

    Each section corresponds to one spine item. 'page_number' is the
    1-based spine position (EPUBs have no real page numbers).

    Returns (sections, stats).
    """
    try:
        import ebooklib  # type: ignore
        from ebooklib import epub as ebooklib_epub  # type: ignore
        from bs4 import BeautifulSoup  # type: ignore
    except ImportError as exc:
        raise ImportError("pip install ebooklib beautifulsoup4 lxml") from exc

    logger.info("Extracting EPUB: %s", epub_path.name)
    slug = _book_slug(epub_path)

    book = ebooklib_epub.read_epub(str(epub_path), options={"ignore_ncx": True})

    # ── Pass 1: image asset index ────────────────────────────────────────────
    image_asset_map: dict[str, tuple[bytes, str]] = {}
    for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        ext = _MIME_TO_EXT.get(item.media_type or "", "")
        if ext:
            image_asset_map[item.get_name()] = (item.get_content(), ext)
    logger.info("  %d image assets in EPUB", len(image_asset_map))

    # ── Pass 2: cross-reference map ──────────────────────────────────────────
    logger.info("  Building cross-reference map …")
    cross_ref = _build_epub_cross_ref_map(book)
    logger.info("  %d anchors with cross-references", len(cross_ref))

    # ── Pass 3: spine items ──────────────────────────────────────────────────
    spine_ids   = {item_id for item_id, _ in book.spine}
    spine_items = [
        book.get_item_with_id(item_id)
        for item_id in (i for i, _ in book.spine)
        if book.get_item_with_id(item_id) is not None
    ]

    stats: dict = {
        "book":                    epub_path.name,
        "slug":                    slug,
        "format":                  "epub",
        "ocr_applied":             False,
        "avg_chars_per_page":      None,
        "total_pages":             0,
        "pages_with_ocr":          0,
        "figures_extracted":       0,
        "figures_with_captions":   0,
        "figures_without_captions":0,
        "figures_with_labels":     0,
        "figures_without_labels":  0,
        "errors":                  [],
        "processed_at":            datetime.datetime.utcnow().isoformat() + "Z",
    }

    sections: list[dict] = []

    for section_num, item in enumerate(spine_items, start=1):
        if item.get_id() not in spine_ids:
            continue

        soup = BeautifulSoup(item.get_content(), "lxml")

        text_parts:        list[str]  = []
        image_links:       list[str]  = []
        captions:          list[str]  = []
        figure_labels_all: list[str]  = []
        figure_numbers:    list[str]  = []
        section_image_type: str | None = None
        section_img_desc:  str | None  = None
        fig_counter        = 0

        # Body text (skip text inside <figure> — handled with the image)
        for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "li"]):
            if tag.find_parent("figure"):
                continue
            t = tag.get_text(separator=" ", strip=True)
            if t:
                text_parts.append(t)

        # Images
        for img_tag in soup.find_all("img"):
            src = img_tag.get("src", "").strip()
            if not src:
                continue
            epub_name = _resolve_epub_img_src(src, item.get_name())
            if epub_name not in image_asset_map:
                logger.debug("  Unresolved img src: %s → %s", src, epub_name)
                continue

            img_data, ext = image_asset_map[epub_name]
            fig_counter += 1
            out_name = f"{slug}_p{section_num}_fig{fig_counter}{ext}"
            try:
                img_path = _save_figure(img_data, out_name, images_dir)
            except Exception as exc:
                stats["errors"].append(
                    f"s{section_num} fig{fig_counter}: {exc}"
                )
                continue

            image_links.append(str(img_path))
            stats["figures_extracted"] += 1

            # Extract figcaption for the payload caption field
            container = img_tag.find_parent(["figure", "div", "td"]) or img_tag.parent
            figcap_tag = container.find("figcaption") if container else None
            caption    = figcap_tag.get_text(strip=True) if figcap_tag else ""
            captions.append(caption)
            if caption:
                stats["figures_with_captions"] += 1
            else:
                stats["figures_without_captions"] += 1

            # Figure number
            fig_num = _detect_figure_number(caption)
            if fig_num:
                figure_numbers.append(fig_num)

            # Figure labels via OCR (open image bytes as PIL)
            labels: list[str] = []
            try:
                from PIL import Image  # type: ignore
                pil_img = Image.open(io.BytesIO(img_data))
                labels  = _ocr_figure_labels(pil_img)
            except ImportError:
                pass
            except Exception as exc:
                logger.debug("  PIL/EasyOCR failed for %s: %s", out_name, exc)

            figure_labels_all.extend(labels)
            if labels:
                stats["figures_with_labels"] += 1
            else:
                stats["figures_without_labels"] += 1

            if section_image_type is None:
                section_image_type = _classify_image_type(False, labels)
            if section_img_desc is None:
                section_img_desc = _describe_image_ollama(img_path)

            # Cross-reference context
            container_id: str | None = None
            for ancestor in img_tag.parents:
                if ancestor.get("id"):
                    container_id = ancestor["id"]
                    break
            img_own_id   = img_tag.get("id") or container_id
            cross_texts  = cross_ref.get(img_own_id, [])[:3] if img_own_id else []

            # Inline image marker
            surrounding   = _image_surrounding_text(img_tag)
            context_parts = list(filter(None, [surrounding] + cross_texts))
            marker = (
                f"[Image: {' | '.join(context_parts)}]"
                if context_parts
                else "[Image]"
            )
            text_parts.append(marker)

        full_text = "\n".join(text_parts).strip()
        if not full_text and not image_links:
            continue

        combined_caption = " | ".join(c for c in captions if c)
        combined_fig_num = figure_numbers[0] if figure_numbers else ""

        sections.append({
            "page_number":       section_num,
            "section_number":    section_num,
            "text":              full_text,
            "image_links":       image_links,
            "source_file":       epub_path.name,
            "source_path":       str(epub_path),
            "format":            "epub",
            "chunk_hash":        hashlib.md5(
                f"{epub_path.name}:s{section_num}:{full_text[:64]}".encode()
            ).hexdigest(),
            # ── Figure metadata ──
            "caption":           combined_caption,
            "figure_labels":     list(dict.fromkeys(figure_labels_all)),
            "image_type":        section_image_type or "",
            "image_description": section_img_desc   or "",
            "figure_number":     combined_fig_num,
            # ── Citation (filled in main()) ──
            "citation":          {},
        })

    stats["total_pages"] = len(sections)
    logger.info(
        "  Extracted %d sections, %d figures",
        len(sections),
        stats["figures_extracted"],
    )
    return sections, stats


# ---------------------------------------------------------------------------
# Format dispatcher
# ---------------------------------------------------------------------------

def extract_book(book_path: Path, images_dir: Path) -> tuple[list[dict], dict]:
    """Route a book file to the correct extractor. Returns (sections, stats)."""
    suffix = book_path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(book_path, images_dir)
    if suffix == ".epub":
        return extract_epub(book_path, images_dir)
    logger.warning("Unsupported format, skipping: %s", book_path.name)
    return [], {
        "book": book_path.name,
        "slug": _book_slug(book_path),
        "format": suffix,
        "errors": ["Unsupported format"],
        "processed_at": datetime.datetime.utcnow().isoformat() + "Z",
    }


# ---------------------------------------------------------------------------
# Processing log
# ---------------------------------------------------------------------------

def _write_processing_log(stats: dict, logs_dir: Path) -> None:
    """Write per-book processing stats to data/processing_logs/{slug}.json."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{stats['slug']}.json"
    log_path.write_text(json.dumps(stats, indent=2))
    logger.info("  Processing log → %s", log_path)


# ---------------------------------------------------------------------------
# Image memory
# ---------------------------------------------------------------------------

def _ensure_image_memory(memory_path: Path) -> None:
    """Create data/image_memory.json with an empty object if it doesn't exist."""
    if not memory_path.exists():
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        memory_path.write_text("{}\n")
        logger.info("Initialised image memory: %s", memory_path)


# ---------------------------------------------------------------------------
# LlamaIndex document creation
# ---------------------------------------------------------------------------

def sections_to_llama_documents(sections: list[dict]):
    """
    Convert section dicts into LlamaIndex Document objects.

    Metadata stored in Qdrant payload:
        source_file, source_path, page_number, section_number, format,
        content_type, subject, chapter, image_links, chunk_hash,
        caption, figure_labels, image_type, image_description,
        figure_number, citation (nested dict),
        see_also (cross-references to related video/pdf chunks),
        device, setting, program, intensity_range, duration_minutes,
        indication, contraindication, body_region  (device docs only)

    Excluded from LLM prompt: source_path, chunk_hash, image_links,
        figure_labels, image_type, citation, see_also, device,
        setting, program, intensity_range  (structural / redundant)

    Excluded from embedding: same as above + citation
    """
    try:
        from llama_index.core import Document  # type: ignore
    except ImportError as exc:
        raise ImportError("pip install llama-index") from exc

    _llm_exclude = [
        "source_path", "chunk_hash", "image_links",
        "figure_labels", "image_type", "citation", "see_also",
        "device", "setting", "program", "intensity_range",
    ]
    _embed_exclude = _llm_exclude  # same set

    documents = []
    for sec in sections:
        doc = Document(
            text=sec["text"],
            metadata={
                "source_file":       sec["source_file"],
                "source_path":       sec["source_path"],
                "page_number":       sec["page_number"],
                "section_number":    sec["section_number"],
                "format":            sec["format"],
                "content_type":      sec.get("content_type", "medical_literature"),
                "subject":           sec.get("subject", ""),
                "chapter":           "",
                "image_links":       sec["image_links"],
                "chunk_hash":        sec["chunk_hash"],
                # Figure metadata
                "caption":           sec.get("caption", ""),
                "figure_labels":     sec.get("figure_labels", []),
                "image_type":        sec.get("image_type", ""),
                "image_description": sec.get("image_description", ""),
                "figure_number":     sec.get("figure_number", ""),
                # Citation
                "citation":          sec.get("citation", {}),
                "citation_apa":      sec.get("citation", {}).get("apa", ""),
                # Cross-references (video ↔ document linking)
                "see_also":          sec.get("see_also", []),
                # Device settings (populated for device_pemf / device_rlt)
                "device":            sec.get("device", ""),
                "setting":           sec.get("setting"),
                "program":           sec.get("program"),
                "intensity_range":   sec.get("intensity_range"),
                "duration_minutes":  sec.get("duration_minutes"),
                "indication":        sec.get("indication"),
                "contraindication":  sec.get("contraindication"),
                "body_region":       sec.get("body_region", ""),
            },
            excluded_llm_metadata_keys=_llm_exclude,
            excluded_embed_metadata_keys=_embed_exclude,
        )
        documents.append(doc)
    return documents


# ---------------------------------------------------------------------------
# Qdrant + LlamaIndex index construction
# ---------------------------------------------------------------------------

def build_index(documents, collection_name: str) -> None:
    """Chunk documents and upsert embeddings into Qdrant."""
    try:
        from llama_index.core import Settings, VectorStoreIndex  # type: ignore
        from llama_index.core.node_parser import SentenceSplitter  # type: ignore
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding  # type: ignore
        from llama_index.vector_stores.qdrant import QdrantVectorStore  # type: ignore
        from qdrant_client import QdrantClient  # type: ignore
        from qdrant_client.models import Distance, VectorParams  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "pip install llama-index llama-index-vector-stores-qdrant "
            "llama-index-embeddings-huggingface qdrant-client"
        ) from exc

    logger.info("Loading embedding model: %s", EMBED_MODEL_NAME)
    Settings.embed_model  = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
    Settings.chunk_size   = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP
    Settings.llm          = None

    client   = QdrantClient(url=QDRANT_URL)
    existing = {c.name for c in client.get_collections().collections}

    if collection_name not in existing:
        logger.info("Creating collection '%s' (dim=%d)", collection_name, EMBED_DIM)
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
    else:
        logger.info("Upserting into existing collection '%s'", collection_name)

    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
    logger.info("Indexing %d documents …", len(documents))
    VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store,
        transformations=[
            SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        ],
        show_progress=True,
    )
    logger.info("Indexing complete — collection '%s' ready.", collection_name)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest medical PDFs/EPUBs into Qdrant via Docling + LlamaIndex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--books-dir",    type=Path, default=Path("./books"))
    parser.add_argument("--images-dir",   type=Path, default=IMAGES_DIR)
    parser.add_argument(
        "--content-type",
        default="medical_literature",
        choices=list(CONTENT_TYPE_COLLECTION_MAP.keys()),
        help=(
            "Content type tag stored on every chunk. "
            "Also determines the target Qdrant collection unless "
            "--collection is given explicitly. "
            f"Choices: {', '.join(CONTENT_TYPE_COLLECTION_MAP)}"
        ),
    )
    parser.add_argument(
        "--collection",
        default=None,
        help=(
            "Qdrant collection name. "
            "Defaults to the collection mapped from --content-type."
        ),
    )
    parser.add_argument("--subject",  default="")
    parser.add_argument("--dry-run",  action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    books_dir:    Path = args.books_dir.resolve()
    images_dir:   Path = args.images_dir.resolve()
    content_type: str  = args.content_type
    collection:   str  = args.collection or _collection_for_content_type(content_type)

    logger.info("Content type : %s", content_type)
    logger.info("Collection   : %s", collection)

    if not books_dir.exists():
        logger.error("Books directory not found: %s", books_dir)
        return

    book_files = sorted(
        p for p in books_dir.iterdir()
        if p.suffix.lower() in {".pdf", ".epub"}
    )
    if not book_files:
        logger.warning("No .pdf or .epub files found in %s", books_dir)
        return

    logger.info(
        "Found %d book(s): %s",
        len(book_files),
        ", ".join(f.name for f in book_files),
    )

    # ── One-time initialisation ──────────────────────────────────────────────
    _ensure_image_memory(IMAGE_MEMORY_PATH)
    _ensure_video_document_links(VIDEO_DOCUMENT_LINKS_PATH)
    books_meta = _load_books_metadata()
    if books_meta:
        logger.info("Loaded bibliographic metadata for %d book(s)", len(books_meta))
    else:
        logger.info(
            "No books_metadata.json found — citations will be minimal. "
            "Run scripts/fetch_book_metadata.py to populate."
        )

    is_device_content = content_type in ("device_pemf", "device_rlt")

    # ── Extract books ────────────────────────────────────────────────────────
    all_sections: list[dict] = []

    for book_path in book_files:
        slug = _book_slug(book_path)
        sections, stats = extract_book(book_path, images_dir)

        for sec in sections:
            # Content type on every chunk
            sec["content_type"] = content_type
            sec["see_also"]     = []

            if args.subject:
                sec["subject"] = args.subject

            # Device settings extraction for PEMF / RLT documents
            if is_device_content:
                device_fields = _extract_device_settings(sec["text"], content_type)
                sec.update(device_fields)

            # Citation from books_metadata.json
            book_meta = books_meta.get(slug, {})
            fig_num   = sec.get("figure_number", "")
            caption   = sec.get("caption", "")
            sec["citation"] = _build_citation_payload(
                book_meta, sec["page_number"], fig_num, caption
            )

        _write_processing_log(stats, LOGS_DIR)
        all_sections.extend(sections)

        # Mark as ingested in metadata
        if slug in books_meta:
            books_meta[slug]["ingested"]       = True
            books_meta[slug]["ingestion_date"] = (
                datetime.datetime.utcnow().isoformat() + "Z"
            )
            books_meta[slug]["total_chunks"]   = len(sections)
            books_meta[slug]["total_figures"]  = stats.get("figures_extracted", 0)

    # Persist updated metadata
    if books_meta and BOOKS_METADATA_PATH.exists():
        BOOKS_METADATA_PATH.write_text(json.dumps(books_meta, indent=2))
        logger.info("Updated books_metadata.json with ingestion stats")

    total_figures = sum(len(s["image_links"]) for s in all_sections)
    logger.info(
        "Total: %d sections, %d book(s), %d figures  [content_type=%s → %s]",
        len(all_sections), len(book_files), total_figures, content_type, collection,
    )

    if args.dry_run:
        preview = []
        for s in all_sections[:15]:
            preview.append({
                "source_file":    s["source_file"],
                "format":         s["format"],
                "content_type":   s["content_type"],
                "page_number":    s["page_number"],
                "image_links":    s["image_links"],
                "caption":        s.get("caption", ""),
                "figure_number":  s.get("figure_number", ""),
                "body_region":    s.get("body_region", ""),
                "citation_apa":   s.get("citation", {}).get("apa", ""),
                "text_preview":   s["text"][:140].replace("\n", " "),
            })
        print(json.dumps(preview, indent=2))
        logger.info("Dry run complete — Qdrant ingestion skipped.")
        return

    documents = sections_to_llama_documents(all_sections)
    build_index(documents, collection_name=collection)


if __name__ == "__main__":
    main()
