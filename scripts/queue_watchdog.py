#!/usr/bin/env python3
"""
queue_watchdog.py — Detects hung book-ingest and transcription queues.

Runs every 10 minutes via queue-watchdog.timer.

Logic:
  1. If service is 'active' but the current-job file has not been modified
     in > STALE_MINUTES, the process is assumed hung → restart.
  2. For transcription-queue: skip if /tmp/transcription_pause exists.
  3. For book-ingest-queue: skip if /tmp/book_ingest_pause exists.
  4. On restart: write a marker to /var/log/markers.json.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE                 = Path("/root/medical-rag")
BOOK_STALE_MINUTES   = 120   # Docling can legitimately run 30–90 min per book
TRANS_STALE_MINUTES  = 30    # Whisper jobs are much shorter
MARKERS_FILE         = Path("/var/log/markers.json")

BOOK_CURRENT  = Path("/tmp/book_ingest_current.json")
BOOK_PAUSE    = Path("/tmp/book_ingest_pause")
TRANS_CURRENT = Path("/tmp/transcription_current.json")
TRANS_PAUSE   = Path("/tmp/transcription_pause")


# ── helpers ───────────────────────────────────────────────────────────────────

def _is_active(service: str) -> bool:
    try:
        r = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True, text=True, timeout=5,
        )
        return r.stdout.strip() == "active"
    except Exception:
        return False


def _mtime_age_minutes(path: Path) -> float | None:
    """Return minutes since path was last modified, or None if it doesn't exist."""
    try:
        age_secs = time.time() - path.stat().st_mtime
        return age_secs / 60
    except Exception:
        return None


def _restart(service: str) -> bool:
    try:
        r = subprocess.run(
            ["systemctl", "restart", service],
            capture_output=True, text=True, timeout=30,
        )
        return r.returncode == 0
    except Exception:
        return False


def _write_marker(event: str, message: str) -> None:
    try:
        data: list[dict] = []
        if MARKERS_FILE.exists():
            try:
                data = json.loads(MARKERS_FILE.read_text())
            except Exception:
                data = []
        data.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event":     event,
            "message":   message,
        })
        # Keep last 50 markers
        MARKERS_FILE.write_text(json.dumps(data[-50:], indent=2))
    except Exception as e:
        print(f"[watchdog] write_marker failed: {e}", file=sys.stderr)


# ── per-service check ─────────────────────────────────────────────────────────

def check_service(
    service: str,
    current_file: Path,
    stale_minutes: float,
    pause_file: Path | None = None,
) -> str:
    """
    Returns one of: "ok", "skipped", "restarted", "restart_failed".
    """
    if pause_file and pause_file.exists():
        print(f"[watchdog] {service}: paused — skipping")
        return "skipped"

    if not _is_active(service):
        print(f"[watchdog] {service}: not active — skipping")
        return "skipped"

    age = _mtime_age_minutes(current_file)
    if age is None:
        # Service running but no current-job file → between jobs, not hung
        print(f"[watchdog] {service}: active, no current job — ok")
        return "ok"

    if age > stale_minutes:
        print(
            f"[watchdog] {service}: current job stale ({age:.0f} min > {stale_minutes:.0f} min) — restarting"
        )
        ok = _restart(service)
        msg = (
            f"{service} hung ({age:.0f} min stale) — "
            f"{'restarted successfully' if ok else 'restart FAILED'}"
        )
        _write_marker("watchdog_restart", msg)
        print(f"[watchdog] {msg}")
        return "restarted" if ok else "restart_failed"

    print(f"[watchdog] {service}: ok ({age:.0f} min elapsed since last update)")
    return "ok"


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"[watchdog] {datetime.now(timezone.utc).isoformat()} — queue watchdog running")

    book_result  = check_service("book-ingest-queue",  BOOK_CURRENT,  BOOK_STALE_MINUTES,  BOOK_PAUSE)
    trans_result = check_service("transcription-queue", TRANS_CURRENT, TRANS_STALE_MINUTES, TRANS_PAUSE)

    print(f"[watchdog] results — book: {book_result}, transcription: {trans_result}")

    if "restart_failed" in (book_result, trans_result):
        sys.exit(1)


if __name__ == "__main__":
    main()
