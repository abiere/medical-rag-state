"""
Nightly stats: tracks sec/chunk (retroaudit) and sec/image
(image screening) to enable smart time-window allocation.
Weighted average: recent samples count more (weight = 1/age_days+1).
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

STATS_PATH = Path("/root/medical-rag/data/nightly_stats.json")
logger = logging.getLogger(__name__)

_DEFAULTS: dict = {
    "retroaudit":      {"avg_sec_per_chunk": 6.0,  "n_samples": 0, "samples": []},
    "image_screening": {"avg_sec_per_image": 8.0,  "n_samples": 0, "samples": []},
}


def load_stats() -> dict:
    try:
        return json.loads(STATS_PATH.read_text())
    except Exception:
        return {k: dict(v) for k, v in _DEFAULTS.items()}


def save_stats(stats: dict) -> None:
    tmp = STATS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(stats, indent=2, ensure_ascii=False))
    os.replace(tmp, STATS_PATH)


def record_retroaudit(chunks_processed: int, elapsed_seconds: float) -> None:
    """Call after a retroaudit phase completes."""
    if chunks_processed <= 0 or elapsed_seconds <= 0:
        return
    stats = load_stats()
    sec_per_chunk = elapsed_seconds / chunks_processed
    sample = {
        "date":          datetime.now(timezone.utc).date().isoformat(),
        "chunks":        chunks_processed,
        "seconds":       round(elapsed_seconds, 1),
        "sec_per_chunk": round(sec_per_chunk, 3),
    }
    ra = stats.setdefault("retroaudit", dict(_DEFAULTS["retroaudit"]))
    ra.setdefault("samples", []).append(sample)
    ra["samples"] = ra["samples"][-30:]          # keep last 30
    ra["avg_sec_per_chunk"] = _weighted_avg(
        [s["sec_per_chunk"] for s in ra["samples"]],
        [s["date"]          for s in ra["samples"]],
    )
    ra["n_samples"] = len(ra["samples"])
    save_stats(stats)
    logger.info("Retroaudit stats: %.2f sec/chunk (n=%d)",
                ra["avg_sec_per_chunk"], ra["n_samples"])


def record_image_screening(images_processed: int, elapsed_seconds: float) -> None:
    """Call after an image screening phase completes."""
    if images_processed <= 0 or elapsed_seconds <= 0:
        return
    stats = load_stats()
    sec_per_image = elapsed_seconds / images_processed
    sample = {
        "date":          datetime.now(timezone.utc).date().isoformat(),
        "images":        images_processed,
        "seconds":       round(elapsed_seconds, 1),
        "sec_per_image": round(sec_per_image, 3),
    }
    im = stats.setdefault("image_screening", dict(_DEFAULTS["image_screening"]))
    im.setdefault("samples", []).append(sample)
    im["samples"] = im["samples"][-30:]
    im["avg_sec_per_image"] = _weighted_avg(
        [s["sec_per_image"] for s in im["samples"]],
        [s["date"]          for s in im["samples"]],
    )
    im["n_samples"] = len(im["samples"])
    save_stats(stats)
    logger.info("Image screening stats: %.2f sec/image (n=%d)",
                im["avg_sec_per_image"], im["n_samples"])


def allocate_window(
    window_seconds: float,
    n_chunks_skipped: int,
    n_images_pending: int,
    claude_api_enabled: bool,
) -> dict:
    """
    Calculate time budget for retroaudit and image screening.

    Rules:
    - Claude API enabled → retroaudit is on-demand (not nightly)
      → 100% of window to image screening
    - Nothing to do for a phase → 0 allocated, other gets 100%
    - Both need time → proportional to estimated need
    - Each phase gets at least 10% of window if it has any work
      (prevents starvation from bad estimates)
    - 15 min reserved for other nightly phases

    Returns dict with retroaudit_seconds, image_seconds, and note.
    """
    stats = load_stats()
    available = max(0.0, window_seconds - 900)   # 15 min for other phases

    # Claude API on → retroaudit handled on-demand via UI widget
    if claude_api_enabled:
        return {
            "retroaudit_seconds": 0,
            "image_seconds":      round(available),
            "note": "Claude API actief: retroaudit op aanvraag, 100% naar images",
        }

    sec_per_chunk = stats["retroaudit"]["avg_sec_per_chunk"]
    sec_per_image = stats["image_screening"]["avg_sec_per_image"]

    est_retro = n_chunks_skipped * sec_per_chunk
    est_image = n_images_pending * sec_per_image

    if n_chunks_skipped == 0 and n_images_pending == 0:
        return {"retroaudit_seconds": 0, "image_seconds": 0,
                "note": "Niets te verwerken"}

    if n_chunks_skipped == 0:
        return {"retroaudit_seconds": 0, "image_seconds": round(available),
                "note": "Geen skipped chunks: 100% naar images"}

    if n_images_pending == 0:
        return {"retroaudit_seconds": round(available), "image_seconds": 0,
                "note": "Geen afbeeldingen: 100% naar retroaudit"}

    # Proportional split, minimum 10% per phase (starvation protection)
    total_est  = est_retro + est_image
    retro_frac = max(0.10, min(0.90, est_retro / total_est))
    image_frac = 1.0 - retro_frac

    # Cap at 120% of estimated need to avoid huge over-allocation
    retro_alloc = min(retro_frac * available, est_retro * 1.2)
    image_alloc = min(image_frac * available, est_image * 1.2)

    # Redistribute any surplus proportionally
    surplus = available - (retro_alloc + image_alloc)
    if surplus > 0:
        retro_alloc += surplus * retro_frac
        image_alloc += surplus * image_frac

    return {
        "retroaudit_seconds": round(retro_alloc),
        "image_seconds":      round(image_alloc),
        "est_retro_need":     round(est_retro),
        "est_image_need":     round(est_image),
        "note": f"Split: {retro_frac:.0%} retro / {image_frac:.0%} images",
    }


def get_stats_summary() -> dict:
    """For API response and pipeline_diagrams overlay."""
    stats = load_stats()
    return {
        "sec_per_chunk":       stats["retroaudit"]["avg_sec_per_chunk"],
        "sec_per_image":       stats["image_screening"]["avg_sec_per_image"],
        "retroaudit_samples":  stats["retroaudit"]["n_samples"],
        "image_samples":       stats["image_screening"]["n_samples"],
    }


def _weighted_avg(values: list[float], dates: list[str]) -> float:
    """Recent samples count more. Weight = 1 / (days_ago + 1)."""
    if not values:
        return 6.0
    today = datetime.now(timezone.utc).date().isoformat()
    weights: list[float] = []
    for d in dates:
        try:
            days = (
                datetime.fromisoformat(today) - datetime.fromisoformat(d)
            ).days
            weights.append(1.0 / (days + 1))
        except Exception:
            weights.append(1.0)
    total_w = sum(weights)
    if total_w == 0:
        return round(sum(values) / len(values), 3)
    return round(sum(v * w for v, w in zip(values, weights)) / total_w, 3)
