#!/usr/bin/env python3
"""
ocr_calibrate.py — Per-book OCR engine calibration.

Samples N pages from a PDF, runs all available OCR engines, asks Ollama
to pick the winner, and caches the result so the same book reuses it.

Entry point:
    calibrate_book(pdf_path, engines) -> str | None
        Returns the name of the best engine, or None if calibration failed.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CACHE_FILE = Path("/root/medical-rag/data/book_quality/calibration_cache.json")
SAMPLE_N   = 5       # max pages to sample
MIN_WORDS  = 10      # minimum words to consider a sample usable

OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"


def calibrate_book(
    pdf_path: Path,
    engines: list[tuple[str, Any]],
) -> str | None:
    """
    Return the name of the best OCR engine for this PDF, or None.

    - Skips if only one engine is available (nothing to compare).
    - Returns cache hit immediately if this book was calibrated before.
    - Samples pages at 10/30/50/70/90% positions.
    - Asks Ollama to pick the best-quality output.
    - Caches result in CACHE_FILE.
    """
    if len(engines) <= 1:
        return engines[0][0] if engines else None

    stem   = pdf_path.stem
    cached = _load_cache()
    if stem in cached:
        winner = cached[stem]
        logger.info("Calibration cache hit for %s → %s", stem, winner)
        return winner

    try:
        import fitz
        from PIL import Image as _PIL
        import numpy as np
    except ImportError as e:
        logger.warning("calibrate_book: missing dependency (%s) — skipping", e)
        return None

    try:
        doc = fitz.open(str(pdf_path))
        n   = len(doc)

        positions = [max(0, int(n * pct / 100)) for pct in (10, 30, 50, 70, 90)]
        positions = list(dict.fromkeys(positions))[:SAMPLE_N]

        samples: dict[str, list[str]] = {name: [] for name, _ in engines}

        for idx in positions:
            pil_image = _render_page(doc, idx)
            for name, fn in engines:
                try:
                    text, _ = fn(pil_image)
                    if len(text.split()) >= MIN_WORDS:
                        samples[name].append(text)
                except Exception:
                    pass

        doc.close()

        summaries = {
            name: " ".join(texts[:3])[:600]
            for name, texts in samples.items()
            if texts
        }

        if not summaries:
            logger.warning("calibrate_book: no usable samples from %s", stem)
            return None

        winner = _ollama_pick_winner(summaries)
        engine_names = {n for n, _ in engines}

        if winner and winner in engine_names:
            cached[stem] = winner
            _save_cache(cached)
            logger.info("Calibration winner for %s → %s", stem, winner)
            return winner

        logger.warning("calibrate_book: Ollama returned '%s' (invalid)", winner)
        return None

    except Exception as e:
        logger.warning("calibrate_book failed for %s: %s", pdf_path.name, e)
        return None


def _render_page(fitz_doc, page_num: int, dpi: int = 150):
    """Quick low-res render for calibration (150 DPI is sufficient for comparison)."""
    import fitz as _fitz
    from PIL import Image as _PIL
    import numpy as np

    page = fitz_doc[page_num]
    mat  = _fitz.Matrix(dpi / 72, dpi / 72)
    pix  = page.get_pixmap(matrix=mat, colorspace=_fitz.csRGB)
    arr  = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
    return _PIL.fromarray(arr)


def _ollama_pick_winner(summaries: dict[str, str]) -> str | None:
    """
    Ask Ollama to compare OCR outputs and return the name of the best engine.
    Falls back to the first key in summaries on any error.
    """
    import urllib.request

    engine_block = "\n\n".join(
        f"=== {name} ===\n{text}"
        for name, text in summaries.items()
    )
    prompt = (
        "You are evaluating OCR output quality for a medical/acupuncture textbook. "
        "The text samples below were extracted from the same pages by different OCR engines. "
        "Choose the engine whose output is most readable, has the fewest garbled characters, "
        "and best preserves technical terms such as acupuncture point codes (e.g. ST-36, SP-10). "
        f"Engine names to choose from: {list(summaries.keys())}. "
        "Respond with ONLY the engine name, nothing else.\n\n"
        f"{engine_block}"
    )

    body = json.dumps({
        "model":   OLLAMA_MODEL,
        "prompt":  prompt,
        "stream":  False,
        "options": {"temperature": 0, "num_predict": 20},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data   = json.loads(resp.read())
            answer = data.get("response", "").strip().lower()
            for name in summaries:
                if name.lower() in answer:
                    return name
            return None
    except Exception as e:
        logger.warning("Ollama calibration request failed: %s — using first engine", e)
        return list(summaries.keys())[0]


def _load_cache() -> dict:
    try:
        if CACHE_FILE.exists():
            d = json.loads(CACHE_FILE.read_text())
            if isinstance(d, dict):
                return d
    except Exception:
        pass
    return {}


def _save_cache(data: dict) -> None:
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        logger.warning("calibration cache save failed: %s", e)
