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
        opts = PdfPipelineOptions(generate_picture_images=False)
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
        pages.append({"page_number": page_no, "paragraphs": paras, "chapter": ch, "section": sec})
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
            "page_number": page_num + 1,
            "paragraphs":  paras,
            "chapter":     ch,
            "section":     sec,
        })
    doc.close()
    return pages


# ── main build_chunks function ────────────────────────────────────────────────

def parse_pdf(
    pdf_path: Path,
    collection_type: str,
    source_category: str,
) -> list[dict[str, Any]]:
    """
    Parse a PDF and return a list of Qdrant-ready chunk dicts.
    """
    book_stem = pdf_path.stem

    logger.info("Parsing %s (collection=%s)", pdf_path.name, collection_type)

    # 1. Try Docling; fall back to PyMuPDF
    pages = _parse_docling(pdf_path)
    if pages is None:
        pages = _parse_pymupdf(pdf_path)

    if not pages:
        logger.error("No pages extracted from %s", pdf_path.name)
        return []

    # 2. Extract images with PyMuPDF (always)
    page_images = _extract_images_pymupdf(pdf_path, book_stem)

    # 3. Build chunks
    chunks: list[dict] = []
    chunk_idx = 0
    current_chapter = current_section = ""
    ingested_at = datetime.now(timezone.utc).isoformat()

    for page in pages:
        page_no   = page["page_number"]
        paragraphs = page["paragraphs"]
        # Update chapter/section context
        if page["chapter"]:
            current_chapter = page["chapter"]
        if page["section"]:
            current_section = page["section"]

        text_chunks = _chunk_text(paragraphs)
        img_links   = page_images.get(page_no, [])

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

            h = hashlib.sha256(f"{pdf_path.name}:{page_no}:{chunk_idx}:{text_en[:200]}".encode()).hexdigest()[:16]

            chunk = {
                "text":               text_en,
                "page_number":        page_no,
                "chapter":            current_chapter,
                "section":            current_section,
                "source_file":        pdf_path.name,
                "source_category":    source_category,
                "collection_type":    collection_type,
                "format":             "pdf",
                "point_codes":        point_codes,
                "figure_refs":        fig_refs,
                "image_links":        img_links,
                "chunk_index":        chunk_idx,
                "chunk_hash":         h,
                "ingested_at":        ingested_at,
                "language_detected":  lang,
            }
            if text_original:
                chunk["text_original"] = text_original

            chunks.append(chunk)
            chunk_idx += 1

    logger.info("Produced %d chunks from %s", len(chunks), pdf_path.name)
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
