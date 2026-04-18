#!/usr/bin/env python3
"""
image_extractor.py — Figure extraction from PDFs and EPUBs.

PDFs: Google Vision document_text_detection → bounding-box analysis →
      find text-sparse zones (likely figures) → crop at 300 DPI.
      Works for both raster and vector figures because it does NOT rely
      on PICTURE block type detection — instead finds areas without text.
EPUBs: extract embedded images directly (no Vision API needed).
"""

from __future__ import annotations

import json
import logging
import os
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

BASE          = Path(__file__).parent.parent
IMAGES_OUT    = BASE / "data" / "extracted_images"
CREDS_FILE    = BASE / "config" / "google_vision_key.json"
_PROGRESS_DIR = Path("/tmp")

# Google Cloud Vision — not migrated to AIClient (bounding-box API, not generative)
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


def _get_vision_response(pil_image):
    """Send page image to Vision document_text_detection. Return raw response."""
    import io
    from google.cloud import vision as gv

    client = _lazy_vision_client()
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    image = gv.Image(content=buf.getvalue())
    response = client.document_text_detection(image=image)
    if response.error.message:
        raise RuntimeError(f"Vision API: {response.error.message}")
    return response


def _find_figure_regions(
    page_img,            # PIL Image at 300 DPI
    vision_response,     # Vision API full response
    min_area_ratio=0.05  # minimum 5% of page area
) -> list[dict]:
    """
    Find text-sparse regions = likely figure zones.

    Uses Vision text block bounding boxes to identify areas where no text
    appears. These empty zones are candidate figure regions. Works for both
    raster images and vector graphics, since it only looks at where text
    is NOT present — block_type is irrelevant.
    """
    W, H = page_img.size
    page_area = W * H

    # Extract all text block bounding boxes from Vision response
    text_rects = []
    if vision_response.full_text_annotation:
        for page in vision_response.full_text_annotation.pages:
            for block in page.blocks:
                verts = block.bounding_box.vertices
                xs = [v.x for v in verts]
                ys = [v.y for v in verts]
                if xs and ys:
                    text_rects.append(
                        (min(xs), min(ys), max(xs), max(ys)))

    if not text_rects:
        return []  # No text at all = no figure context

    # Cell-based grid: 60×60 cells over the page
    CELLS = 60
    cell_w = max(1, W // CELLS)
    cell_h = max(1, H // CELLS)
    cols   = W // cell_w + 1
    rows   = H // cell_h + 1

    # Mark cells covered by text blocks (with small inward margin)
    grid = [[False] * cols for _ in range(rows)]
    for (x1, y1, x2, y2) in text_rects:
        margin_x = int((x2 - x1) * 0.1)
        margin_y = int((y2 - y1) * 0.1)
        c1 = max(0, (x1 - margin_x) // cell_w)
        r1 = max(0, (y1 - margin_y) // cell_h)
        c2 = min(cols - 1, (x2 + margin_x) // cell_w)
        r2 = min(rows - 1, (y2 + margin_y) // cell_h)
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                grid[r][c] = True

    # BFS to find contiguous empty (text-free) regions
    visited = [[False] * cols for _ in range(rows)]
    figure_regions = []

    for start_r in range(rows):
        for start_c in range(cols):
            if grid[start_r][start_c] or visited[start_r][start_c]:
                continue
            # BFS from this empty cell
            region_cells = []
            queue: deque = deque()
            queue.append((start_r, start_c))
            visited[start_r][start_c] = True
            while queue:
                cr, cc = queue.popleft()
                region_cells.append((cr, cc))
                for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    nr, nc = cr + dr, cc + dc
                    if (0 <= nr < rows and 0 <= nc < cols
                            and not grid[nr][nc]
                            and not visited[nr][nc]):
                        visited[nr][nc] = True
                        queue.append((nr, nc))

            if not region_cells:
                continue

            # Bounding box of region in pixels
            min_r = min(c[0] for c in region_cells)
            max_r = max(c[0] for c in region_cells)
            min_c = min(c[1] for c in region_cells)
            max_c = max(c[1] for c in region_cells)
            px1 = min_c * cell_w
            py1 = min_r * cell_h
            px2 = min((max_c + 1) * cell_w, W)
            py2 = min((max_r + 1) * cell_h, H)
            area = (px2 - px1) * (py2 - py1)

            if area < page_area * min_area_ratio:
                continue  # Too small

            # Skip narrow strips (headers/footers/margins with minimal text)
            region_h = py2 - py1
            region_w = px2 - px1
            if region_h < H * 0.08 or region_w < W * 0.15:
                continue

            # Density check: actual empty cells vs bounding-box cells.
            # A real figure block is a solid empty zone (density ≥ 0.55).
            # The margin/frame artefact (BFS finds all margins forming a
            # frame around text) has very low density (~0.05–0.20) because
            # its bounding box covers the full page while the actual cells
            # are only the thin perimeter.
            bbox_cell_count = (max_r - min_r + 1) * (max_c - min_c + 1)
            density = len(region_cells) / max(1, bbox_cell_count)
            if density < 0.55:
                continue

            figure_regions.append({
                "x1":         px1,
                "y1":         py1,
                "x2":         px2,
                "y2":         py2,
                "area_ratio": round(area / page_area, 3),
            })

    # Sort by area descending — largest figure first
    figure_regions.sort(key=lambda r: r["area_ratio"], reverse=True)

    # Max 2 figures per page to avoid over-segmentation
    return figure_regions[:2]


def _extract_alt_text(
    vision_response,
    figure_y1: int,
    figure_y2: int,
) -> str:
    """
    Find text blocks immediately above (title/section) and below (caption)
    the figure zone. Returns combined ALT text string.
    """
    above: list[tuple[int, str]] = []
    below: list[tuple[int, str]] = []

    if not vision_response.full_text_annotation:
        return ""

    for page in vision_response.full_text_annotation.pages:
        for block in page.blocks:
            block_text = " ".join(
                " ".join(
                    "".join(s.text for s in word.symbols)
                    for word in para.words
                )
                for para in block.paragraphs
            ).strip()
            if not block_text or len(block_text) < 3:
                continue

            verts    = block.bounding_box.vertices
            ys       = [v.y for v in verts]
            block_y1 = min(ys)
            block_y2 = max(ys)

            if block_y2 < figure_y1:
                above.append((figure_y1 - block_y2, block_text))
            elif block_y1 > figure_y2:
                below.append((block_y1 - figure_y2, block_text))

    parts = []
    if above:
        above.sort(key=lambda x: x[0])
        for _, text in above[:2]:
            if len(text) < 120:
                parts.append(text)
                break
    if below:
        below.sort(key=lambda x: x[0])
        for _, text in below[:1]:
            if len(text) < 200:
                parts.append(text)
                break

    return " — ".join(parts) if parts else ""


def extract_figures_from_pdf(
    pdf_path:   Path,
    book_hash:  str,
    output_dir: Path = IMAGES_OUT,
    max_workers: int = 8,
    progress_fn: Callable[[int, int], None] | None = None,
    max_pages:   int | None = None,
) -> list[dict]:
    """
    For each page: render at 300 DPI → Vision document_text_detection →
    find text-sparse zones via bounding-box analysis → crop and save PNG.
    Returns metadata list; saves images_metadata.json in output_dir/{book_hash}/.

    max_pages: limit page count (for testing only).
    """
    out = output_dir / book_hash
    out.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)
    doc.close()

    pages_to_process = list(range(min(total_pages, max_pages) if max_pages else total_pages))
    results: list[dict] = []
    done_count = 0

    def process_page(page_num: int) -> list[dict]:
        page_results: list[dict] = []
        doc_local = fitz.open(str(pdf_path))
        try:
            page = doc_local[page_num]

            # --- Tier 1 / 2 pre-filter (no Vision API call needed) ---
            pymupdf_chars = len(page.get_text().strip())

            # Render at 300 DPI — used for variance check, Vision, and cropping
            page_img = _render_page(page, dpi=300)

            if pymupdf_chars <= 50:
                # Near-zero text: could be a rasterised diagram OR a blank page.
                # Distinguish by pixel variance of a downscaled greyscale render.
                from PIL import Image as _PIL, ImageStat as _Stat
                thumb = page_img.convert("L").resize((200, 260), _PIL.LANCZOS)
                var = _Stat.Stat(thumb).var[0]
                if var < 500:
                    return page_results  # Blank / white page — skip
                # Has visual content → full-page rasterised diagram
                W, H = page_img.size
                fname = f"fig_{page_num + 1:04d}_00.png"
                page_img.save(str(out / fname))
                page_results.append({
                    "filename":    fname,
                    "page":        page_num + 1,
                    "bbox":        {"x1": 0, "y1": 0, "x2": W, "y2": H},
                    "area_ratio":  1.0,
                    "alt_text":    page.get_text().strip(),
                    "source":      "raster_page",
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                })
                return page_results

            if pymupdf_chars > 2000:
                # Dense text page — Vision would find no figure zones; skip API call.
                return page_results

            # --- Tier 3: moderate text (50–2000 chars) — Vision bbox detection ---
            response = _get_vision_response(page_img)
            regions  = _find_figure_regions(page_img, response)

            for idx, region in enumerate(regions):
                x1, y1, x2, y2 = region["x1"], region["y1"], region["x2"], region["y2"]
                cropped  = page_img.crop((x1, y1, x2, y2))
                fname    = f"fig_{page_num + 1:04d}_{idx:02d}.png"
                cropped.save(str(out / fname))

                alt_text = _extract_alt_text(response, y1, y2)

                page_results.append({
                    "filename":    fname,
                    "page":        page_num + 1,
                    "bbox":        {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                    "area_ratio":  region["area_ratio"],
                    "alt_text":    alt_text,
                    "source":      "vision_bbox",
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                })
        except Exception as exc:
            logger.warning("Page %d failed: %s", page_num + 1, exc)
        finally:
            doc_local.close()
        return page_results

    _write_extraction_progress(book_hash, 0, len(pages_to_process), 0)
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_page, p): p for p in pages_to_process}
            for future in as_completed(futures):
                try:
                    page_results = future.result()
                    results.extend(page_results)
                except Exception as exc:
                    logger.error("Page future failed: %s", exc)
                done_count += 1
                _write_extraction_progress(book_hash, done_count, len(pages_to_process), len(results))
                if progress_fn:
                    progress_fn(done_count, len(pages_to_process))
    finally:
        _clear_extraction_progress(book_hash)

    results.sort(key=lambda x: (x["page"], x["filename"]))

    meta = {
        "book_hash":    book_hash,
        "filename":     pdf_path.name,
        "image_source": "vision_bbox",
        "images":       results,
    }
    (out / "images_metadata.json").write_text(json.dumps(meta, indent=2))
    logger.info("Extracted %d figures from %s (pages tested: %d)",
                len(results), pdf_path.name, len(pages_to_process))
    return results


def _extract_img_caption(img_tag) -> str:
    """Extract caption text for a BS4 img element from surrounding HTML context."""
    parent = img_tag.parent

    # 1. figcaption anywhere inside parent (handles <figure> and div wrappers)
    if parent:
        fig_cap = parent.find("figcaption")
        if fig_cap:
            text = fig_cap.get_text(strip=True)
            if text:
                return text[:200]

    # 2. Next sibling <p> starting with "Figure" / "Fig." / "Fig "
    next_sib = img_tag.find_next_sibling()
    if next_sib is None and parent:
        next_sib = parent.find_next_sibling()
    if next_sib and hasattr(next_sib, "get_text"):
        text = next_sib.get_text(strip=True)
        if text and (
            text.lower().startswith("figure")
            or text.lower().startswith("fig.")
            or text.lower().startswith("fig ")
        ):
            return text[:200]

    # 3. Alt attribute fallback — skip trivial values (≤ 3 chars)
    alt = img_tag.get("alt", "").strip()
    if alt and len(alt) > 3:
        return alt[:200]

    return ""


def extract_images_from_epub(
    epub_path:  Path,
    book_hash:  str,
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

    # Build caption map using context-aware extraction
    caption_map: dict[str, str] = {}
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        try:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            for img_tag in soup.find_all("img"):
                src = img_tag.get("src", "")
                if not src:
                    continue
                basename = Path(src.split("?")[0]).name
                if basename and basename not in caption_map:
                    cap = _extract_img_caption(img_tag)
                    if cap:
                        caption_map[basename] = cap
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
            ext   = ext_map.get(item.media_type, "png")
            fname = f"epub_{idx:04d}.{ext}"
            (out / fname).write_bytes(content)

            img_name = Path(item.get_name()).name
            caption  = caption_map.get(img_name, "")

            results.append({
                "filename":     fname,
                "page":         None,
                "caption":      caption,
                "alt_text":     caption,
                "area_ratio":   None,
                "bbox":         None,
                "source":       "epub",
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
