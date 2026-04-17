#!/usr/bin/env python3
"""
image_extractor.py — Figure extraction from PDFs and EPUBs.

PDFs: Google Vision document_text_detection → PICTURE block bboxes →
      PyMuPDF high-res crop → saves isolated figures with caption metadata.
EPUBs: extract embedded images directly (no Vision API needed).
"""

from __future__ import annotations

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

BASE         = Path(__file__).parent.parent
IMAGES_OUT   = BASE / "data" / "extracted_images"
CREDS_FILE   = BASE / "config" / "google_vision_key.json"
_PROGRESS_DIR = Path("/tmp")

if CREDS_FILE.exists() and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CREDS_FILE)


def _write_extraction_progress(book_hash: str, pages_processed: int,
                                pages_total: int, figures_found: int) -> None:
    try:
        pf = _PROGRESS_DIR / f"image_extraction_{book_hash}.json"
        pf.write_text(json.dumps({
            "book_hash":       book_hash,
            "pages_processed": pages_processed,
            "pages_total":     pages_total,
            "figures_found":   figures_found,
            "updated_at":      datetime.now(timezone.utc).isoformat(),
        }))
    except Exception:
        pass


def _clear_extraction_progress(book_hash: str) -> None:
    try:
        pf = _PROGRESS_DIR / f"image_extraction_{book_hash}.json"
        if pf.exists():
            pf.unlink()
    except Exception:
        pass


def _lazy_vision_client():
    from google.cloud import vision as gv
    return gv.ImageAnnotatorClient()


def _render_page(page: fitz.Page, dpi: int):
    """Render a PyMuPDF page to a PIL Image at the given DPI."""
    import io
    from PIL import Image
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    return Image.open(io.BytesIO(pix.tobytes("png")))


def _vision_picture_blocks(pil_image) -> list[dict]:
    """
    Send page image to Vision document_text_detection.
    Return list of {bbox: [x1,y1,x2,y2], caption: str} for PICTURE blocks.
    PICTURE block_type == 3 in the Vision proto.
    """
    import io
    from google.cloud import vision as gv

    client = _lazy_vision_client()
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    image = gv.Image(content=buf.getvalue())
    response = client.document_text_detection(image=image)
    if response.error.message:
        raise RuntimeError(f"Vision API: {response.error.message}")

    picture_results: list[dict] = []
    text_blocks: list[dict] = []

    for vpage in response.full_text_annotation.pages:
        for block in vpage.blocks:
            verts = block.bounding_box.vertices
            xs = [v.x for v in verts]
            ys = [v.y for v in verts]
            bbox = [min(xs), min(ys), max(xs), max(ys)]

            if block.block_type == 3:  # PICTURE
                picture_results.append({"bbox": bbox, "caption": ""})
            elif block.block_type == 1:  # TEXT
                words = []
                for para in block.paragraphs:
                    for word in para.words:
                        words.append("".join(s.text for s in word.symbols))
                text_blocks.append({"bbox": bbox, "text": " ".join(words).strip()})

    # Match captions: text block within 50px below a picture block, horizontally overlapping
    for fig in picture_results:
        fx1, fy1, fx2, fy2 = fig["bbox"]
        best = ""
        for tb in text_blocks:
            tx1, ty1, tx2, ty2 = tb["bbox"]
            if ty1 >= fy2 and ty1 <= fy2 + 50 and tx1 <= fx2 and tx2 >= fx1:
                t = tb["text"]
                if len(t) > len(best):
                    best = t
        fig["caption"] = best

    return picture_results


def extract_figures_from_pdf(
    pdf_path: Path,
    book_hash: str,
    output_dir: Path = IMAGES_OUT,
    max_workers: int = 8,
    progress_fn: Callable[[int, int], None] | None = None,
) -> list[dict]:
    """
    For each page: render at 150 DPI → Vision document_text_detection →
    find PICTURE blocks → crop at 300 DPI → save PNG.
    Returns metadata list; saves images_metadata.json in output_dir/{book_hash}/.
    """
    out = output_dir / book_hash
    out.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    doc.close()

    results: list[dict] = []
    done_count = 0
    lock_results: list = []

    def process_page(page_num: int) -> list[dict]:
        page_results: list[dict] = []
        doc_local = fitz.open(str(pdf_path))
        try:
            page = doc_local[page_num]
            low_res = _render_page(page, dpi=150)
            picture_blocks = _vision_picture_blocks(low_res)

            if not picture_blocks:
                return []

            hi_res = _render_page(page, dpi=300)
            iw, ih = hi_res.size
            scale = 300 / 150

            for idx, fig in enumerate(picture_blocks):
                bx1, by1, bx2, by2 = fig["bbox"]
                cx1 = max(0, int(bx1 * scale) - 10)
                cy1 = max(0, int(by1 * scale) - 10)
                cx2 = min(iw, int(bx2 * scale) + 10)
                cy2 = min(ih, int(by2 * scale) + 10)

                if cx2 - cx1 < 20 or cy2 - cy1 < 20:
                    continue

                cropped = hi_res.crop((cx1, cy1, cx2, cy2))
                fname = f"fig_{page_num + 1:04d}_{idx:02d}.png"
                cropped.save(str(out / fname))

                page_results.append({
                    "id":           f"fig_{page_num + 1:04d}_{idx:02d}",
                    "file":         fname,
                    "page":         page_num + 1,
                    "caption":      fig.get("caption", ""),
                    "confidence":   0.9,
                    "image_source": "pdf_cropped",
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                })
        except Exception as exc:
            logger.warning("Page %d failed: %s", page_num + 1, exc)
        finally:
            doc_local.close()
        return page_results

    _write_extraction_progress(book_hash, 0, total_pages, 0)
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_page, p): p for p in range(total_pages)}
            for future in as_completed(futures):
                try:
                    page_results = future.result()
                    results.extend(page_results)
                except Exception as exc:
                    logger.error("Page future failed: %s", exc)
                done_count += 1
                _write_extraction_progress(book_hash, done_count, total_pages, len(results))
                if progress_fn:
                    progress_fn(done_count, total_pages)
    finally:
        _clear_extraction_progress(book_hash)

    results.sort(key=lambda x: (x["page"], x["id"]))

    meta = {
        "book_hash":    book_hash,
        "filename":     pdf_path.name,
        "image_source": "pdf_cropped",
        "images":       results,
    }
    (out / "images_metadata.json").write_text(json.dumps(meta, indent=2))
    logger.info("Extracted %d figures from %s", len(results), pdf_path.name)
    return results


def extract_images_from_epub(
    epub_path: Path,
    book_hash: str,
    output_dir: Path = IMAGES_OUT,
) -> list[dict]:
    """
    Extract embedded images directly from EPUB.
    No Vision API — images are already isolated.
    Returns metadata list; saves images_metadata.json in output_dir/{book_hash}/.
    """
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup

    out = output_dir / book_hash
    out.mkdir(parents=True, exist_ok=True)

    book = epub.read_epub(str(epub_path))

    # Build caption map: image filename → caption or alt text
    caption_map: dict[str, str] = {}
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        try:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            for fig in soup.find_all("figure"):
                img = fig.find("img")
                cap = fig.find("figcaption")
                if img and cap:
                    src = img.get("src", "")
                    caption_map[Path(src).name] = cap.get_text(strip=True)
            for img_tag in soup.find_all("img"):
                alt = img_tag.get("alt", "")
                src = img_tag.get("src", "")
                if alt and src and Path(src).name not in caption_map:
                    caption_map[Path(src).name] = alt
        except Exception:
            pass

    IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}
    all_image_items = [
        item for item in book.get_items()
        if item.media_type in IMAGE_TYPES
        and item.get_content() and len(item.get_content()) >= 1000
    ]
    total_items = len(all_image_items)
    _write_extraction_progress(book_hash, 0, total_items, 0)

    results: list[dict] = []
    idx = 0
    try:
        for item in all_image_items:
            content = item.get_content()
            ext_map = {"image/jpeg": "jpg", "image/jpg": "jpg",
                       "image/png": "png", "image/webp": "webp", "image/gif": "gif"}
            ext = ext_map.get(item.media_type, "png")
            fname = f"epub_{idx:04d}.{ext}"
            (out / fname).write_bytes(content)

            img_name = Path(item.get_name()).name
            caption = caption_map.get(img_name, "")

            results.append({
                "id":           f"epub_{idx:04d}",
                "file":         fname,
                "page":         None,
                "caption":      caption,
                "alt_text":     caption,
                "confidence":   1.0,
                "image_source": "epub",
                "extracted_at": datetime.now(timezone.utc).isoformat(),
            })
            idx += 1
            _write_extraction_progress(book_hash, idx, total_items, len(results))
    finally:
        _clear_extraction_progress(book_hash)

    meta = {
        "book_hash":    book_hash,
        "filename":     epub_path.name,
        "image_source": "epub",
        "images":       results,
    }
    (out / "images_metadata.json").write_text(json.dumps(meta, indent=2))
    logger.info("Extracted %d images from EPUB %s", len(results), epub_path.name)
    return results
