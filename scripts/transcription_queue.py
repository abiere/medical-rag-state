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
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# ── config ────────────────────────────────────────────────────────────────────
BASE       = Path("/root/medical-rag")
VIDEOS_DIR = BASE / "videos"
TRANS_DIR  = BASE / "data" / "transcripts"
LOG_FILE   = Path("/var/log/transcription_queue.log")
QUEUE_FILE = Path("/tmp/transcription_queue.json")
CURRENT    = Path("/tmp/transcription_current.json")

NOTIFY      = BASE / "scripts" / "notify.sh"
INGEST      = BASE / "scripts" / "ingest_transcript.py"
PAUSE_FILE  = Path("/tmp/transcription_pause")
STATS_FILE  = BASE / "data" / "transcription_stats.json"
SETTINGS_FILE = BASE / "config" / "settings.json"
VIDEO_TYPES = ["nrt", "qat", "pemf", "rlt"]
VIDEO_EXTS  = {".mp4", ".mov", ".mkv", ".m4v"}
CONTENT_TYPE_MAP = {
    "nrt":  "training_nrt",
    "qat":  "training_qat",
    "pemf": "device_pemf",
    "rlt":  "device_rlt",
}


def _load_transcription_settings() -> dict:
    try:
        data = json.loads(SETTINGS_FILE.read_text())
        return data.get("transcription", {})
    except Exception:
        return {}

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


# ── notify helper ────────────────────────────────────────────────────────────

def _notify(event: str, message: str) -> None:
    try:
        subprocess.run([str(NOTIFY), event, message], timeout=10, check=False)
    except Exception as exc:
        log.warning(f"notify failed: {exc}")


# ── ingestion helper ─────────────────────────────────────────────────────────

def _ingest_transcript(filename: str, vtype: str) -> bool:
    """Run ingest_transcript.py for the completed transcript. Returns True on success."""
    stem = Path(filename).stem
    json_path = TRANS_DIR / f"{stem}.json"
    if not json_path.exists():
        log.warning(f"Transcript not found for ingestion: {json_path}")
        return False
    log.info(f"INGEST {vtype}/{filename}")
    result = subprocess.run(
        ["python3", str(INGEST), "--file", str(json_path), "--video-type", vtype],
        cwd=BASE,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        for line in result.stdout.strip().splitlines():
            log.info(f"  [ingest] {line}")
    if result.returncode != 0:
        log.error(f"  [ingest] FAIL\n{result.stderr[-500:]}")
        return False
    return True


# ── transcription stats ───────────────────────────────────────────────────────

def _update_stats(filename: str, video_path: Path, duration_seconds: float) -> None:
    """
    Record seconds_per_mb for a completed transcription and update model_rate
    (weighted average, recency-weighted: weight = 1 / (days_since + 1)).
    Writes atomically via tempfile rename.
    """
    try:
        file_size_mb = os.path.getsize(video_path) / 1e6
    except OSError:
        return  # video file gone — skip silently

    if file_size_mb < 0.1 or duration_seconds < 1:
        return

    seconds_per_mb = duration_seconds / file_size_mb
    completed_at   = datetime.now(timezone.utc).isoformat()

    # Load existing
    try:
        stats: dict = json.loads(STATS_FILE.read_text()) if STATS_FILE.exists() else {}
    except Exception:
        stats = {}
    stats.setdefault("completed", [])
    stats.setdefault("model_rate", {"seconds_per_mb": seconds_per_mb, "n_samples": 0, "updated_at": ""})

    # Append new record
    stats["completed"].append({
        "filename":        filename,
        "file_size_mb":    round(file_size_mb, 2),
        "duration_seconds": round(duration_seconds, 1),
        "seconds_per_mb":  round(seconds_per_mb, 2),
        "completed_at":    completed_at,
    })

    # Recompute weighted average (recency weight = 1 / (days_since + 1))
    now = datetime.now(timezone.utc)
    total_w = 0.0
    total_wr = 0.0
    for entry in stats["completed"]:
        try:
            ts = datetime.fromisoformat(entry["completed_at"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            days = max((now - ts).total_seconds() / 86400, 0)
        except Exception:
            days = 0
        w = 1.0 / (days + 1)
        total_w  += w
        total_wr += w * entry["seconds_per_mb"]

    if total_w > 0:
        stats["model_rate"] = {
            "seconds_per_mb": round(total_wr / total_w, 2),
            "n_samples":      len(stats["completed"]),
            "updated_at":     completed_at,
        }

    # Atomic write
    try:
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp_fd, tmp_path = tempfile.mkstemp(dir=STATS_FILE.parent, suffix=".tmp")
        with os.fdopen(tmp_fd, "w") as f:
            json.dump(stats, f, indent=2)
        os.replace(tmp_path, STATS_FILE)
        log.info(f"Stats updated: {filename} — {seconds_per_mb:.1f}s/MB  rate={stats['model_rate']['seconds_per_mb']:.1f}s/MB ({stats['model_rate']['n_samples']} samples)")
    except Exception as exc:
        log.warning(f"Stats write failed: {exc}")


# ── video splitting ────────────────────────────────────────────────────────────

def _split_video_if_needed(
    video_path: Path,
    max_mb: int = 400,
    segment_minutes: int = 20,
) -> list[Path]:
    """
    Split video into segments if larger than max_mb.
    Returns list of segment paths (or [video_path] if no split needed).
    Uses ffmpeg stream copy (no re-encoding — fast).
    """
    size_mb = video_path.stat().st_size / 1024 / 1024
    if size_mb <= max_mb:
        return [video_path]

    segment_dir = video_path.parent / f"{video_path.stem}_segments"
    existing = sorted(segment_dir.glob(f"{video_path.stem}_part*.mp4"))
    if existing:
        log.info("Using existing segments for %s: %d parts", video_path.name, len(existing))
        return existing

    segment_dir.mkdir(exist_ok=True)
    log.info("Splitting %s (%.0f MB) into %d-min segments", video_path.name, size_mb, segment_minutes)
    segment_pattern = str(segment_dir / f"{video_path.stem}_part%03d.mp4")
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-c", "copy", "-map", "0",
        "-segment_time", str(segment_minutes * 60),
        "-f", "segment", "-reset_timestamps", "1",
        "-y", segment_pattern,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log.error("ffmpeg split failed for %s: %s", video_path.name, result.stderr[-500:])
        return [video_path]
    segments = sorted(segment_dir.glob(f"{video_path.stem}_part*.mp4"))
    log.info("Split %s into %d segments", video_path.name, len(segments))
    return segments


def _transcribe_segment(seg_path: Path, content_type: str) -> str:
    """Run transcribe_videos.py on a single file/segment. Returns stdout text."""
    result = subprocess.run(
        [
            "python3", str(BASE / "scripts" / "transcribe_videos.py"),
            "--file", str(seg_path),
            "--content-type", content_type,
            "--stdout-only",
        ],
        cwd=BASE,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("Segment transcription failed %s: %s", seg_path.name, result.stderr[-400:])
    return result.stdout


# ── transcription ─────────────────────────────────────────────────────────────

def _transcribe_one(item: dict) -> bool:
    """Run transcription for one queue item. Returns True on success."""
    vtype      = item.get("video_type", "")
    filename   = item.get("filename", "")
    video_path = VIDEOS_DIR / vtype / filename

    if not video_path.exists():
        log.warning(f"Video not found, skipping: {vtype}/{filename}")
        return False

    # Skip/size-limit checks from config/settings.json
    ts = _load_transcription_settings()
    skip_files = ts.get("skip_files", [])
    max_mb = ts.get("max_file_size_mb", 9999)
    file_mb = os.path.getsize(video_path) / 1024 / 1024

    if filename in skip_files:
        log.warning(f"Skipping {vtype}/{filename} (in skip_files list)")
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

    log.info(f"START  {vtype}/{filename}  ({file_mb:.0f} MB)")
    t0 = time.time()

    segments = _split_video_if_needed(video_path, max_mb=400, segment_minutes=20)
    if len(segments) > 1:
        log.info("Transcribing %d segments for %s", len(segments), filename)
        results = []
        for seg in segments:
            result = subprocess.run(
                [
                    "python3", str(BASE / "scripts" / "transcribe_videos.py"),
                    "--file", str(seg),
                    "--content-type", content_type,
                ],
                cwd=BASE,
                capture_output=True,
                text=True,
            )
            results.append(result)
            if result.returncode != 0:
                log.error("Segment FAIL %s: %s", seg.name, result.stderr[-400:])

        elapsed = time.time() - t0
        success = all(r.returncode == 0 for r in results)
        if success:
            log.info(f"DONE   {vtype}/{filename}  ({elapsed:.0f}s, {len(segments)} segments)")
            _update_stats(filename, video_path, elapsed)
        else:
            log.error(f"FAIL   {vtype}/{filename}  ({elapsed:.0f}s) — one or more segments failed")
        Path(f"/tmp/transcribe_{filename}.log").write_text(
            "\n\n".join(f"=== {s.name} ===\n{r.stdout}\n{r.stderr}" for s, r in zip(segments, results))
        )
        return success

    # Single file (no split needed)
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
        _update_stats(filename, video_path, elapsed)
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
    initial_total = len(_read_queue())

    while True:
        # Pause support: check flag before starting next video
        if PAUSE_FILE.exists():
            log.info("Queue paused (pause flag set) — waiting 30s")
            time.sleep(30)
            continue

        queue = _read_queue()
        if not queue:
            log.info(f"Queue empty — {processed} video(s) processed. Exiting.")
            if processed > 0:
                _notify("queue_empty", f"All {processed} videos transcribed")
            break

        item     = queue[0]
        vtype    = item.get("video_type", "?")
        filename = item.get("filename", "?")

        # Skip if transcript appeared since enqueue (e.g. manual run)
        if (TRANS_DIR / f"{Path(filename).stem}.json").exists():
            log.info(f"Already done, removing from queue: {vtype}/{filename}")
            _write_queue(queue[1:])
            continue

        ok = False
        try:
            ok = _transcribe_one(item)
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

        if ok:
            ingested = _ingest_transcript(filename, vtype)
            _notify(
                "transcript_ingested" if ingested else "ingest_failed",
                f"{filename} ingested into Qdrant" if ingested else f"{filename} ingest FAILED",
            )

        total_done = sum(1 for _ in TRANS_DIR.glob("*.json")) if TRANS_DIR.exists() else processed
        _notify(
            "transcription_done" if ok else "transcription_failed",
            f"{filename} {'complete' if ok else 'FAILED'} ({total_done}/{initial_total})",
        )

    log.info("Transcription queue manager done")


if __name__ == "__main__":
    main()
