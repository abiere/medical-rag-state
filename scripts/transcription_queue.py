#!/usr/bin/env python3
"""
Sequential transcription queue manager.

Processes one video at a time — never parallel.
On startup, scans all video dirs for untranscribed files and merges
them into the persistent queue at /tmp/transcription_queue.json.
The web API also appends to that file when the user clicks Transcribe.

Progress → /var/log/transcription_queue.log
Current job → /tmp/transcription_current.json  (removed when done)
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ── config ────────────────────────────────────────────────────────────────────
BASE       = Path("/root/medical-rag")
VIDEOS_DIR = BASE / "videos"
TRANS_DIR  = BASE / "data" / "transcripts"
LOG_FILE   = Path("/var/log/transcription_queue.log")
QUEUE_FILE = Path("/tmp/transcription_queue.json")
CURRENT    = Path("/tmp/transcription_current.json")

VIDEO_TYPES = ["nrt", "qat", "pemf", "rlt"]
VIDEO_EXTS  = {".mp4", ".mov", ".mkv", ".m4v"}
CONTENT_TYPE_MAP = {
    "nrt":  "training_nrt",
    "qat":  "training_qat",
    "pemf": "device_pemf",
    "rlt":  "device_rlt",
}

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE)),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ── queue helpers ─────────────────────────────────────────────────────────────

def _read_queue() -> list[dict]:
    try:
        if QUEUE_FILE.exists():
            with open(QUEUE_FILE) as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


def _write_queue(items: list[dict]) -> None:
    with open(QUEUE_FILE, "w") as f:
        json.dump(items, f, indent=2)


def _scan_untranscribed() -> list[dict]:
    """Return all video files that have no transcript JSON yet."""
    found = []
    for vtype in VIDEO_TYPES:
        vdir = VIDEOS_DIR / vtype
        if not vdir.exists():
            continue
        for f in sorted(vdir.iterdir()):
            if f.suffix.lower() in VIDEO_EXTS:
                if not (TRANS_DIR / f"{f.stem}.json").exists():
                    found.append({
                        "video_type": vtype,
                        "filename": f.name,
                        "requested": datetime.now().isoformat(),
                    })
    return found


def _merge_into_queue(new_items: list[dict]) -> int:
    """Add items to the queue if not already present. Returns count added."""
    current  = _read_queue()
    existing = {(i.get("video_type"), i.get("filename")) for i in current}
    added    = 0
    for item in new_items:
        key = (item["video_type"], item["filename"])
        if key not in existing:
            current.append(item)
            existing.add(key)
            added += 1
    if added:
        _write_queue(current)
    return added


# ── transcription ─────────────────────────────────────────────────────────────

def _transcribe_one(item: dict) -> bool:
    """Run transcription for one queue item. Returns True on success."""
    vtype      = item.get("video_type", "")
    filename   = item.get("filename", "")
    video_path = VIDEOS_DIR / vtype / filename

    if not video_path.exists():
        log.warning(f"Video not found, skipping: {vtype}/{filename}")
        return False

    stem = Path(filename).stem
    if (TRANS_DIR / f"{stem}.json").exists():
        log.info(f"Already transcribed, skipping: {filename}")
        return True

    content_type = CONTENT_TYPE_MAP.get(vtype, "training_nrt")

    # Mark current job
    CURRENT.write_text(json.dumps({
        "file": filename,
        "video_type": vtype,
        "started": datetime.now().isoformat(),
    }))

    log.info(f"START  {vtype}/{filename}")
    t0 = time.time()

    result = subprocess.run(
        [
            "python3", str(BASE / "scripts" / "transcribe_videos.py"),
            "--file", str(video_path),
            "--content-type", content_type,
        ],
        cwd=BASE,
        capture_output=True,
        text=True,
    )

    elapsed = time.time() - t0

    if result.returncode == 0:
        log.info(f"DONE   {vtype}/{filename}  ({elapsed:.0f}s)")
    else:
        log.error(
            f"FAIL   {vtype}/{filename}  ({elapsed:.0f}s)\n"
            + result.stderr[-800:]
        )

    # Write per-file log for compatibility with legacy log checks
    Path(f"/tmp/transcribe_{filename}.log").write_text(
        f"=== stdout ===\n{result.stdout}\n=== stderr ===\n{result.stderr}\n"
    )

    return result.returncode == 0


# ── main loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    log.info("─" * 60)
    log.info("Transcription queue manager started")

    # Populate queue from filesystem scan
    found = _scan_untranscribed()
    if found:
        added = _merge_into_queue(found)
        log.info(
            f"Startup scan: {len(found)} untranscribed video(s) found, "
            f"{added} new entry/entries added to queue"
        )
    else:
        log.info("Startup scan: no untranscribed videos found on filesystem")

    processed = 0

    while True:
        queue = _read_queue()
        if not queue:
            log.info(f"Queue empty — {processed} video(s) processed. Exiting.")
            break

        item     = queue[0]
        vtype    = item.get("video_type", "?")
        filename = item.get("filename", "?")

        # Skip if transcript appeared since enqueue (e.g. manual run)
        if (TRANS_DIR / f"{Path(filename).stem}.json").exists():
            log.info(f"Already done, removing from queue: {vtype}/{filename}")
            _write_queue(queue[1:])
            continue

        try:
            _transcribe_one(item)
        except Exception:
            log.exception(f"Unexpected error processing {vtype}/{filename}")
        finally:
            # Remove this item from queue (re-read to catch concurrent appends)
            refreshed = _read_queue()
            _write_queue([
                q for q in refreshed
                if not (
                    q.get("video_type") == vtype
                    and q.get("filename") == filename
                )
            ])
            CURRENT.unlink(missing_ok=True)

        processed += 1

    log.info("Transcription queue manager done")


if __name__ == "__main__":
    main()
