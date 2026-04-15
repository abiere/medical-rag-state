#!/usr/bin/env python3
"""
parse_pdf.py — PDF parser for the Medical RAG book ingestion pipeline.

Usage:
    python3 scripts/parse_pdf.py \
        --file books/acupuncture/deadman.pdf \
        --collection acupuncture_points \
        --category acupuncture \
        --output /tmp/chunks.json

Output: JSON list of chunk dicts ready for Qdrant upsert.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)

BASE       = Path(__file__).parent.parent
IMAGES_DIR = BASE / "data" / "extracted_images"

OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

# Acupuncture point codes: ST-36, SP-10, BL-40, GV-4, CV-6, KD-3 etc.
_POINT_RE = re.compile(
    r"\b(?:LU|LI|ST|SP|HT|SI|BL|KD|PC|SJ|GB|LR|GV|CV|TH|TW|TB|TE|TR|KI|UB|"
    r"VG|VC|RM|DU|RN)-\d+\b",
    re.IGNORECASE,
)
# Figure references: Fig. 4.155, Figure 3.2, Afb 2.1, Abb. 3.4
_FIG_RE = re.compile(
    r"\b(?:Fig(?:ure)?|Afb(?:eelding)?|Abb(?:ildung)?)[.\s]+(\d+[\.\d]*)",
    re.IGNORECASE,
)
# Chapter/section headers (heuristic patterns)
_CHAP_RE    = re.compile(r"^(?:Chapter|Hoofdstuk|Kapitel)\s+(\d+[\w.]*)\s*[:\-–]?\s*(.*)$", re.I)
_SECTION_RE = re.compile(r"^(\d+[\.\d]+)\s+(.{5,80})$")

TARGET_WORDS    = 450   # target chunk size
MIN_WORDS       = 50
MAX_WORDS       = 800
OVERLAP_SENTS   = 2     # carry last N sentences into next chunk

MIN_OCR_WORDS   = 10   # minimum words to accept an OCR result
NATIVE_THRESHOLD = 15  # pdfplumber words/page below this → OCR the page


# ── language detection + translation ─────────────────────────────────────────

def _detect_lang(text: str) -> str:
    try:
        from langdetect import detect
        return detect(text[:1000])
    except Exception:
        return "en"


def _translate_via_ollama(text: str) -> str | None:
    """Translate text to English using Ollama. Returns None on failure."""
    import urllib.request as _ur
    import urllib.error
    prompt = (
        "Translate the following medical/acupuncture text to English. "
        "Preserve all technical terms, point codes (ST-36 etc.), "
        "figure references, and Latin anatomical terms exactly as-is. "
        "Return only the translated text, nothing else.\n\n"
        f"{text[:3000]}"
    )
    body = json.dumps({"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}).encode()
    req = _ur.Request(f"{OLLAMA_URL}/api/generate", data=body,
                      headers={"Content-Type": "application/json"})
    try:
        with _ur.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data.get("response", "").strip() or None
    except Exception as e:
        logger.warning("Translation failed: %s", e)
        return None


# ── text chunking ─────────────────────────────────────────────────────────────

def _split_sentences(text: str) -> list[str]:
    """Rough sentence splitter that respects abbreviations."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\d])", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _chunk_text(paragraphs: list[str]) -> list[str]:
    """
    Merge paragraphs into chunks of ~TARGET_WORDS words.
    Never split mid-sentence; carry OVERLAP_SENTS sentences between chunks.
    """
    chunks: list[str] = []
    current_sents: list[str] = []
    current_words = 0

    for para in paragraphs:
        sents = _split_sentences(para)
        for sent in sents:
            wc = len(sent.split())
            if current_words + wc > MAX_WORDS and current_sents:
                chunks.append(" ".join(current_sents))
                # carry last OVERLAP_SENTS sentences as overlap
                current_sents = current_sents[-OVERLAP_SENTS:]
                current_words = sum(len(s.split()) for s in current_sents)
            current_sents.append(sent)
            current_words += wc
            if current_words >= TARGET_WORDS:
                chunks.append(" ".join(current_sents))
                current_sents = current_sents[-OVERLAP_SENTS:]
                current_words = sum(len(s.split()) for s in current_sents)

    if current_sents:
        leftover = " ".join(current_sents)
        if len(leftover.split()) >= MIN_WORDS:
            chunks.append(leftover)
        elif chunks:
            chunks[-1] = chunks[-1] + " " + leftover
        else:
            # Entire document is smaller than MIN_WORDS — keep it anyway
            chunks.append(leftover)

    return chunks


# ── metadata extractors ───────────────────────────────────────────────────────

def _extract_points(text: str) -> list[str]:
    return sorted({m.group().upper() for m in _POINT_RE.finditer(text)})


def _extract_fig_refs(text: str) -> list[str]:
    return list({m for m in _FIG_RE.findall(text)})


def _detect_chapter_section(lines: list[str]) -> tuple[str, str]:
    chapter = section = ""
    for line in lines:
        line = line.strip()
        m = _CHAP_RE.match(line)
        if m:
            chapter = f"Chapter {m.group(1)}" + (f": {m.group(2).strip()}" if m.group(2).strip() else "")
            continue
        m = _SECTION_RE.match(line)
        if m:
            section = f"{m.group(1)} {m.group(2).strip()}"
    return chapter, section


# ── image extraction (PyMuPDF) ────────────────────────────────────────────────

def _extract_images_pymupdf(pdf_path: Path, book_stem: str) -> dict[int, list[str]]:
    """
    Extract images > 100×100 px from PDF using PyMuPDF at 300 DPI.
    Returns {page_number: [image_path, ...]} (1-based pages).
    """
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    page_images: dict[int, list[str]] = {}
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf_path))
        for page_num in range(len(doc)):
            page = doc[page_num]
            imgs = page.get_images(full=True)
            saved = []
            for n, img_info in enumerate(imgs):
                xref = img_info[0]
                try:
                    base_img = doc.extract_image(xref)
                    w, h = base_img.get("width", 0), base_img.get("height", 0)
                    if w < 100 or h < 100:
                        continue
                    ext = base_img.get("ext", "png")
                    img_bytes = base_img["image"]
                    fname = f"{book_stem}_{page_num+1:04d}_{n:02d}.png"
                    out_path = IMAGES_DIR / fname
                    # Convert to PNG via PIL
                    try:
                        from PIL import Image as PilImage
                        import io as _io
                        img = PilImage.open(_io.BytesIO(img_bytes))
                        img.save(str(out_path), "PNG")
                    except Exception:
                        out_path.write_bytes(img_bytes)
                    saved.append(str(out_path.relative_to(BASE)))
                except Exception as e:
                    logger.debug("Image extraction xref %s: %s", xref, e)
            if saved:
                page_images[page_num + 1] = saved
        doc.close()
    except Exception as e:
        logger.warning("PyMuPDF image extraction failed: %s", e)
    return page_images


# ── Docling parser ────────────────────────────────────────────────────────────

def _parse_docling(pdf_path: Path) -> list[dict] | None:
    """
    Returns list of {page_number, paragraphs, chapter, section} dicts,
    or None if Docling fails / returns too little text.
    """
    try:
        from docling.document_converter import DocumentConverter
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.datamodel.base_models import InputFormat
        from docling.document_converter import PdfFormatOption
    except ImportError:
        logger.info("Docling not available — using PyMuPDF fallback")
        return None

    try:
        # do_ocr=False: disable Docling's internal OCR pipeline (RapidOCR etc.)
        # We handle scanned pages ourselves via cascade OCR in _parse_scanned/_parse_mixed.
        # Docling is only used here for native PDFs with extractable text.
        opts = PdfPipelineOptions(generate_picture_images=False, do_ocr=False)
        converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
        )
        result = converter.convert(str(pdf_path))
    except Exception as e:
        logger.warning("Docling conversion failed: %s", e)
        return None

    md_text = result.document.export_to_markdown()
    if len(md_text.split()) < 50:
        logger.info("Docling returned < 50 words — falling back to PyMuPDF")
        return None

    # Group by page via prov info
    page_data: dict[int, list[str]] = {}
    try:
        for item, _ in result.document.iterate_items():
            text = getattr(item, "text", None)
            if not text or not text.strip():
                continue
            page_no = 1
            if hasattr(item, "prov") and item.prov:
                page_no = getattr(item.prov[0], "page_no", 1)
            page_data.setdefault(page_no, []).append(text.strip())
    except Exception:
        # Fall back to full markdown split by page marker
        for i, line in enumerate(md_text.splitlines()):
            page_data.setdefault(1, []).append(line)

    pages = []
    for page_no in sorted(page_data):
        paras = [p for p in page_data[page_no] if p]
        ch, sec = _detect_chapter_section(paras)
        pages.append({
            "page_number": page_no, "paragraphs": paras,
            "chapter": ch, "section": sec,
            "ocr_engine": "native", "ocr_confidence": 1.0,
        })
    return pages


# ── PyMuPDF text parser ───────────────────────────────────────────────────────

def _parse_pymupdf(pdf_path: Path) -> list[dict]:
    """
    Returns list of {page_number, paragraphs, chapter, section} dicts.
    """
    try:
        import fitz
    except ImportError:
        logger.error("Neither Docling nor PyMuPDF available")
        return []

    pages = []
    doc = fitz.open(str(pdf_path))
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")  # list of (x0, y0, x1, y1, text, ...)
        paras = [b[4].strip() for b in sorted(blocks, key=lambda b: (b[1], b[0])) if b[4].strip()]
        ch, sec = _detect_chapter_section(paras)
        pages.append({
            "page_number":    page_num + 1,
            "paragraphs":     paras,
            "chapter":        ch,
            "section":        sec,
            "ocr_engine":     "native",
            "ocr_confidence": 1.0,
        })
    doc.close()
    return pages


# ═══════════════════════════════════════════════════════════════════════════════
# OCR CASCADE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

# ── OCR engine singletons (lazy-loaded) ───────────────────────────────────────

_easyocr_reader = None
_surya_det      = None
_surya_rec      = None
_engines: list[tuple[str, Any]] | None = None


def _lazy_easyocr():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        logger.info("Loading EasyOCR model (first use)...")
        _easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _easyocr_reader


def _lazy_surya():
    global _surya_det, _surya_rec
    if _surya_det is None:
        from surya.detection import DetectionPredictor
        from surya.recognition import RecognitionPredictor
        logger.info("Loading Surya models (first use)...")
        _surya_det = DetectionPredictor()
        _surya_rec = RecognitionPredictor()
    return _surya_det, _surya_rec


# ── per-engine OCR functions ───────────────────────────────────────────────────

def _ocr_easyocr(pil_image) -> tuple[str, float]:
    import numpy as np
    reader  = _lazy_easyocr()
    results = reader.readtext(np.array(pil_image))
    if not results:
        return "", 0.0
    text = " ".join(r[1] for r in results)
    conf = sum(r[2] for r in results) / len(results)
    return text, round(conf, 3)


def _ocr_surya(pil_image) -> tuple[str, float]:
    det, rec = _lazy_surya()
    det_preds = det([pil_image])
    bboxes    = [p.bboxes for p in det_preds]
    rec_preds = rec([pil_image], bboxes=bboxes)
    lines = rec_preds[0].text_lines if rec_preds else []
    if not lines:
        return "", 0.0
    text = "\n".join(line.text for line in lines if line.text)
    confs = [getattr(line, "confidence", 0.8) for line in lines]
    conf = sum(confs) / len(confs) if confs else 0.0
    return text, round(conf, 3)


def _ocr_tesseract(pil_image) -> tuple[str, float]:
    import pytesseract
    text = pytesseract.image_to_string(pil_image, lang="eng", config="--oem 3 --psm 6")
    return text.strip(), 0.7   # tesseract doesn't give per-image confidence easily


# ── engine registry ───────────────────────────────────────────────────────────

def _build_engines() -> list[tuple[str, Any]]:
    """
    Test which OCR engines are importable (without loading models).
    Returns ordered list of (name, ocr_fn) pairs.
    """
    result = []

    try:
        import easyocr  # noqa: F401 — just check import
        result.append(("easyocr", _ocr_easyocr))
        logger.info("OCR available: EasyOCR")
    except ImportError:
        logger.warning("EasyOCR not available")

    try:
        from surya.detection import DetectionPredictor     # noqa: F401
        from surya.recognition import RecognitionPredictor # noqa: F401
        result.append(("surya", _ocr_surya))
        logger.info("OCR available: Surya")
    except ImportError:
        logger.warning("Surya not available")

    try:
        import pytesseract  # noqa: F401
        pytesseract.get_tesseract_version()
        result.append(("tesseract", _ocr_tesseract))
        logger.info("OCR available: Tesseract")
    except Exception:
        logger.warning("Tesseract not available")

    if not result:
        logger.error("No OCR engines available — scanned PDFs will not be readable")
    return result


def _get_engines() -> list[tuple[str, Any]]:
    global _engines
    if _engines is None:
        _engines = _build_engines()
    return _engines


# ── cascade OCR function ──────────────────────────────────────────────────────

def ocr_page_with_fallback(pil_image, page_num: int) -> dict:
    """
    Try OCR engines in order until one returns >= MIN_OCR_WORDS words.

    Returns:
        {text, word_count, engine_used, engines_tried, confidence, readable}
    """
    engines_tried: list[str] = []

    for name, ocr_fn in _get_engines():
        engines_tried.append(name)
        try:
            text, conf = ocr_fn(pil_image)
            wc = len(text.split())
            if wc >= MIN_OCR_WORDS:
                logger.debug("Page %d: %s → %d words (conf=%.2f)", page_num, name, wc, conf)
                return {
                    "text":          text,
                    "word_count":    wc,
                    "engine_used":   name,
                    "engines_tried": engines_tried,
                    "confidence":    conf,
                    "readable":      True,
                }
            logger.warning(
                "Page %d: %s returned %d words (< %d) — trying next",
                page_num, name, wc, MIN_OCR_WORDS,
            )
        except Exception as e:
            logger.warning("Page %d: %s failed: %s — trying next", page_num, name, e)

    logger.warning("Page %d: all OCR engines failed — saved as image only", page_num)
    return {
        "text":          "",
        "word_count":    0,
        "engine_used":   "none",
        "engines_tried": engines_tried,
        "confidence":    0.0,
        "readable":      False,
    }


# ── smart PDF type detection ──────────────────────────────────────────────────

def detect_pdf_type(filepath: Path) -> str:
    """
    Sample up to 5 pages with pdfplumber to count native text words.

    Returns "native" | "scanned" | "mixed"
        native  → avg_words >= 50 across sampled pages
        mixed   → avg_words >= 15 (some pages have text, some don't)
        scanned → avg_words <  15 (virtually no extractable text)
    """
    try:
        import pdfplumber
    except ImportError:
        logger.warning("pdfplumber not available — assuming scanned")
        return "scanned"

    try:
        with pdfplumber.open(str(filepath)) as pdf:
            n_pages = len(pdf.pages)
            # Sample pages: 1, 10, 50, 100, 200 (0-indexed)
            candidates = [0, 9, 49, 99, 199]
            indices    = [i for i in candidates if i < n_pages]
            if not indices:
                indices = list(range(min(5, n_pages)))

            word_counts = []
            for i in indices:
                try:
                    text = pdf.pages[i].extract_text() or ""
                    word_counts.append(len(text.split()))
                except Exception:
                    word_counts.append(0)

            avg = sum(word_counts) / len(word_counts) if word_counts else 0
            logger.info(
                "PDF type detection: avg=%.1f words/page over %d sampled pages → %s",
                avg, len(indices),
                "native" if avg >= 50 else ("mixed" if avg >= 15 else "scanned"),
            )
            if avg >= 50:
                return "native"
            if avg >= 15:
                return "mixed"
            return "scanned"
    except Exception as e:
        logger.warning("PDF type detection failed: %s — assuming scanned", e)
        return "scanned"


# ── page renderer (for OCR input) ────────────────────────────────────────────

def _render_page(fitz_doc, page_num: int, dpi: int = 300):
    """Render a fitz page to PIL Image."""
    import fitz
    from PIL import Image as PilImage
    import numpy as np

    page = fitz_doc[page_num]
    mat  = fitz.Matrix(dpi / 72, dpi / 72)
    pix  = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    arr  = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
    return PilImage.fromarray(arr)


def _save_page_render(pil_image, book_stem: str, page_num: int) -> str:
    """Save a page render for unreadable pages. Returns relative path string."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    fname    = f"{book_stem}_p{page_num:04d}_scan.png"
    out_path = IMAGES_DIR / fname
    pil_image.save(str(out_path), "PNG")
    return str(out_path.relative_to(BASE))


# ── scanned PDF parser ────────────────────────────────────────────────────────

def _parse_scanned(pdf_path: Path, book_stem: str) -> tuple[list[dict], dict]:
    """
    Parse fully scanned PDF using cascade OCR on every page.
    Returns (pages, ocr_stats).
    """
    import fitz

    ocr_stats: dict = {
        "total_pages":     0,
        "readable_pages":  0,
        "unreadable_pages": 0,
        "engine_usage":    {},
        "avg_confidence":  0.0,
    }

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        logger.error("Cannot open PDF with fitz: %s", e)
        return [], ocr_stats

    n_pages = len(doc)
    ocr_stats["total_pages"] = n_pages
    logger.info("Scanned PDF — cascade OCR on %d pages", n_pages)

    pages: list[dict] = []
    confidences: list[float] = []

    for page_num in range(n_pages):
        try:
            pil_image = _render_page(doc, page_num)
            result    = ocr_page_with_fallback(pil_image, page_num + 1)

            engine = result["engine_used"]
            ocr_stats["engine_usage"][engine] = \
                ocr_stats["engine_usage"].get(engine, 0) + 1

            if result["readable"]:
                ocr_stats["readable_pages"] += 1
                confidences.append(result["confidence"])
                paras      = [p.strip() for p in result["text"].split("\n") if p.strip()]
                ch, sec    = _detect_chapter_section(paras)
                pages.append({
                    "page_number":    page_num + 1,
                    "paragraphs":     paras,
                    "chapter":        ch,
                    "section":        sec,
                    "ocr_engine":     engine,
                    "ocr_confidence": result["confidence"],
                })
            else:
                ocr_stats["unreadable_pages"] += 1
                img_path = _save_page_render(pil_image, book_stem, page_num + 1)
                logger.debug("Page %d unreadable — saved render: %s", page_num + 1, img_path)
                pages.append({
                    "page_number":    page_num + 1,
                    "paragraphs":     [],
                    "chapter":        "",
                    "section":        "",
                    "ocr_engine":     "none",
                    "ocr_confidence": 0.0,
                    "_image_only":    True,
                    "_page_image":    img_path,
                })
        except Exception as e:
            logger.warning("Page %d failed: %s", page_num + 1, e)
            ocr_stats["unreadable_pages"] += 1

    doc.close()
    if confidences:
        ocr_stats["avg_confidence"] = round(sum(confidences) / len(confidences), 3)
    return pages, ocr_stats


# ── mixed PDF parser ──────────────────────────────────────────────────────────

def _parse_mixed(pdf_path: Path, book_stem: str) -> tuple[list[dict], dict]:
    """
    Mixed PDF: pdfplumber extracts text per page; pages with < NATIVE_THRESHOLD
    words are re-processed with cascade OCR.
    Returns (pages, ocr_stats).
    """
    import fitz

    ocr_stats: dict = {
        "total_pages":     0,
        "readable_pages":  0,
        "unreadable_pages": 0,
        "native_pages":    0,
        "ocr_pages":       0,
        "engine_usage":    {},
        "avg_confidence":  0.0,
    }

    try:
        import pdfplumber
        plumber = pdfplumber.open(str(pdf_path))
    except Exception as e:
        logger.warning("pdfplumber unavailable (%s) — full cascade OCR", e)
        return _parse_scanned(pdf_path, book_stem)

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        logger.error("Cannot open PDF with fitz: %s", e)
        plumber.close()
        return [], ocr_stats

    n_pages = len(doc)
    ocr_stats["total_pages"] = n_pages
    logger.info("Mixed PDF — %d pages, pdfplumber + OCR fallback", n_pages)

    pages: list[dict] = []
    confidences: list[float] = []

    for page_num in range(n_pages):
        try:
            # Try pdfplumber first
            native_text  = plumber.pages[page_num].extract_text() or ""
            native_words = len(native_text.split())

            if native_words >= NATIVE_THRESHOLD:
                ocr_stats["native_pages"] += 1
                ocr_stats["readable_pages"] += 1
                paras   = [p.strip() for p in native_text.split("\n") if p.strip()]
                ch, sec = _detect_chapter_section(paras)
                pages.append({
                    "page_number":    page_num + 1,
                    "paragraphs":     paras,
                    "chapter":        ch,
                    "section":        sec,
                    "ocr_engine":     "native",
                    "ocr_confidence": 1.0,
                })
            else:
                # Render and cascade OCR
                ocr_stats["ocr_pages"] += 1
                pil_image = _render_page(doc, page_num)
                result    = ocr_page_with_fallback(pil_image, page_num + 1)

                engine = result["engine_used"]
                ocr_stats["engine_usage"][engine] = \
                    ocr_stats["engine_usage"].get(engine, 0) + 1

                if result["readable"]:
                    ocr_stats["readable_pages"] += 1
                    confidences.append(result["confidence"])
                    paras   = [p.strip() for p in result["text"].split("\n") if p.strip()]
                    ch, sec = _detect_chapter_section(paras)
                    pages.append({
                        "page_number":    page_num + 1,
                        "paragraphs":     paras,
                        "chapter":        ch,
                        "section":        sec,
                        "ocr_engine":     engine,
                        "ocr_confidence": result["confidence"],
                    })
                else:
                    ocr_stats["unreadable_pages"] += 1
                    img_path = _save_page_render(pil_image, book_stem, page_num + 1)
                    pages.append({
                        "page_number":    page_num + 1,
                        "paragraphs":     [],
                        "chapter":        "",
                        "section":        "",
                        "ocr_engine":     "none",
                        "ocr_confidence": 0.0,
                        "_image_only":    True,
                        "_page_image":    img_path,
                    })
        except Exception as e:
            logger.warning("Page %d failed: %s", page_num + 1, e)
            ocr_stats["unreadable_pages"] += 1

    plumber.close()
    doc.close()
    if confidences:
        ocr_stats["avg_confidence"] = round(sum(confidences) / len(confidences), 3)
    return pages, ocr_stats


# ── main parse_pdf function ───────────────────────────────────────────────────

def parse_pdf(
    pdf_path: Path,
    collection_type: str,
    source_category: str,
) -> list[dict[str, Any]]:
    """
    Parse a PDF and return a list of Qdrant-ready chunk dicts.

    Routing:
        native  → Docling (or PyMuPDF fallback) — fast, no OCR
        scanned → cascade OCR on every page
        mixed   → pdfplumber per page; cascade OCR when native text is sparse
    """
    book_stem = pdf_path.stem
    logger.info("Parsing %s (collection=%s)", pdf_path.name, collection_type)

    # 1. Detect PDF type
    pdf_type = detect_pdf_type(pdf_path)
    logger.info("PDF type: %s", pdf_type)

    ocr_stats: dict | None = None

    if pdf_type == "native":
        pages = _parse_docling(pdf_path)
        if pages is None:
            pages = _parse_pymupdf(pdf_path)
    elif pdf_type == "scanned":
        pages, ocr_stats = _parse_scanned(pdf_path, book_stem)
    else:
        pages, ocr_stats = _parse_mixed(pdf_path, book_stem)

    if not pages:
        logger.error("No pages extracted from %s", pdf_path.name)
        return []

    # 2. Extract embedded images with PyMuPDF (always, even for scanned)
    page_images = _extract_images_pymupdf(pdf_path, book_stem)

    # 3. Build chunks
    chunks: list[dict] = []
    chunk_idx = 0
    current_chapter = current_section = ""
    ingested_at = datetime.now(timezone.utc).isoformat()
    first_chunk = True  # flag to attach ocr_stats to first chunk

    for page in pages:
        page_no    = page["page_number"]
        paragraphs = page["paragraphs"]

        # Unreadable pages: no text chunks, but image is already saved.
        # Link the rendered image so it shows up in /images approval.
        if page.get("_image_only"):
            render_path = page.get("_page_image", "")
            if render_path:
                existing = page_images.get(page_no, [])
                if render_path not in existing:
                    page_images[page_no] = existing + [render_path]
            continue

        # Update running chapter/section context
        if page["chapter"]:
            current_chapter = page["chapter"]
        if page["section"]:
            current_section = page["section"]

        text_chunks = _chunk_text(paragraphs)
        img_links   = page_images.get(page_no, [])
        ocr_engine  = page.get("ocr_engine", "native")
        ocr_conf    = page.get("ocr_confidence", 1.0)

        for raw_text in text_chunks:
            if len(raw_text.split()) < 5:   # drop truly empty fragments only
                continue

            # Language detection + translation
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

            h = hashlib.sha256(
                f"{pdf_path.name}:{page_no}:{chunk_idx}:{text_en[:200]}".encode()
            ).hexdigest()[:16]

            chunk: dict[str, Any] = {
                "text":               text_en,
                "page_number":        page_no,
                "chapter":            current_chapter,
                "section":            current_section,
                "source_file":        pdf_path.name,
                "source_category":    source_category,
                "collection_type":    collection_type,
                "format":             "pdf",
                "pdf_type":           pdf_type,
                "point_codes":        point_codes,
                "figure_refs":        fig_refs,
                "image_links":        img_links,
                "chunk_index":        chunk_idx,
                "chunk_hash":         h,
                "ingested_at":        ingested_at,
                "language_detected":  lang,
                "ocr_engine":         ocr_engine,
                "ocr_confidence":     ocr_conf,
            }
            if text_original:
                chunk["text_original"] = text_original

            # Attach ocr_stats to first chunk so audit_book.py can extract it
            if first_chunk and ocr_stats is not None:
                chunk["_ocr_stats"] = ocr_stats
                first_chunk = False

            chunks.append(chunk)
            chunk_idx += 1

    logger.info(
        "Produced %d chunks from %s (type=%s)", len(chunks), pdf_path.name, pdf_type
    )
    return chunks


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Parse a PDF into Qdrant-ready chunks")
    ap.add_argument("--file",       required=True)
    ap.add_argument("--collection", required=True)
    ap.add_argument("--category",   required=True)
    ap.add_argument("--output",     default="/tmp/parse_pdf_output.json")
    args = ap.parse_args()

    chunks = parse_pdf(Path(args.file), args.collection, args.category)
    Path(args.output).write_text(json.dumps(chunks, indent=2, ensure_ascii=False))
    print(f"Wrote {len(chunks)} chunks → {args.output}")


if __name__ == "__main__":
    main()
