#!/usr/bin/env python3
"""
watchdog.py — Autonomous self-healing watchdog for book-ingest-queue.

Runs every 60 seconds, checks:
  - book-ingest-queue service state (not active → restart)
  - ingest progress (no change in BOOK_STALE_MIN → restart service)
  - transcription-queue service state (not active + videos waiting → restart)

Writes SYSTEM_DOCS/WATCHDOG_LOG.md after every event.
Called as a standalone systemd service (book-ingest-watchdog).
"""
from __future__ import annotations

import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────

BASE               = Path(__file__).parent.parent
WATCHDOG_LOG       = BASE / "SYSTEM_DOCS" / "WATCHDOG_LOG.md"
BOOK_CURRENT_FILE  = Path("/tmp/book_ingest_current.json")
TRANS_QUEUE_FILE   = Path("/tmp/transcription_queue.json")
CACHE_DIR          = BASE / "data" / "ingest_cache"

POLL_INTERVAL      = 60    # seconds between polls
BOOK_STALE_MIN     = 120   # minutes with same progress → stale
MAX_RESTART_EVENTS = 10    # keep last N events in log

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/var/log/watchdog.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _svc_active(name: str) -> bool:
    try:
        r = subprocess.run(
            ["systemctl", "is-active", name],
            capture_output=True, text=True, timeout=5,
        )
        return r.stdout.strip() == "active"
    except Exception:
        return False


def _svc_restart(name: str) -> bool:
    try:
        r = subprocess.run(
            ["systemctl", "restart", name],
            capture_output=True, text=True, timeout=30,
        )
        return r.returncode == 0
    except Exception:
        return False


def _read_book_current() -> dict:
    try:
        if BOOK_CURRENT_FILE.exists():
            return json.loads(BOOK_CURRENT_FILE.read_text())
    except Exception:
        pass
    return {}


def _trans_queue_len() -> int:
    try:
        if TRANS_QUEUE_FILE.exists():
            q = json.loads(TRANS_QUEUE_FILE.read_text())
            return len(q) if isinstance(q, list) else 0
    except Exception:
        pass
    return 0


def _elapsed_min(ts_str: str) -> float:
    """Minutes since ISO timestamp string, or 0.0 on error."""
    try:
        ts = datetime.fromisoformat(ts_str)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - ts).total_seconds() / 60
    except Exception:
        return 0.0


# ── Progress snapshot ─────────────────────────────────────────────────────────

class ProgressSnapshot:
    """Tracks the last seen progress value to detect stalls."""

    def __init__(self) -> None:
        self._last_key:  str   = ""
        self._last_time: float = time.monotonic()

    def check(self, current: dict) -> bool:
        """
        Update snapshot. Returns True if progress appears stale
        (same book + same phase + same page/chunk for BOOK_STALE_MIN minutes).
        """
        filename = current.get("filename", "")
        phase    = current.get("phase", "")
        page     = current.get("current_page", 0)
        chunk    = current.get("chunks_embedded", 0)
        key      = f"{filename}|{phase}|{page}|{chunk}"

        if key != self._last_key:
            self._last_key  = key
            self._last_time = time.monotonic()
            return False

        elapsed_min = (time.monotonic() - self._last_time) / 60
        return elapsed_min >= BOOK_STALE_MIN

    def reset(self) -> None:
        self._last_key  = ""
        self._last_time = time.monotonic()


# ── Log writer ────────────────────────────────────────────────────────────────

def _write_watchdog_log(events: list[dict]) -> None:
    """Overwrite WATCHDOG_LOG.md with the current event list (most recent first)."""
    WATCHDOG_LOG.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# WATCHDOG_LOG — Book Ingest Watchdog",
        f"> Auto-updated by watchdog.py — last written: **{_now_utc()}**",
        "",
        "| Timestamp | Event | Detail |",
        "|---|---|---|",
    ]
    for ev in reversed(events[-MAX_RESTART_EVENTS:]):
        ts     = ev.get("ts", "?")
        event  = ev.get("event", "?")
        detail = ev.get("detail", "")
        lines.append(f"| {ts} | {event} | {detail} |")

    lines += [
        "",
        "## Current state",
        "",
    ]

    # Append live progress from BOOK_CURRENT_FILE
    cur = _read_book_current()
    if cur.get("filename"):
        lines.append(f"- **Book:** `{cur['filename']}`")
        lines.append(f"- **Phase:** {cur.get('phase', '?')}")
        if cur.get("current_page"):
            lines.append(f"- **Page:** {cur['current_page']}")
        if cur.get("chunks_embedded"):
            lines.append(f"- **Chunks embedded:** {cur['chunks_embedded']}")
        if cur.get("started"):
            mins = _elapsed_min(cur["started"])
            lines.append(f"- **Running for:** {mins:.0f} min")
    else:
        lines.append("- Ingest queue: idle")

    WATCHDOG_LOG.write_text("\n".join(lines) + "\n")


# ── Push to git ───────────────────────────────────────────────────────────────

def _push_log() -> None:
    """Stage WATCHDOG_LOG.md and push if changed."""
    try:
        subprocess.run(
            ["git", "add", "SYSTEM_DOCS/WATCHDOG_LOG.md"],
            cwd=BASE, capture_output=True, timeout=10,
        )
        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=BASE,
        )
        if diff.returncode != 0:  # there are staged changes
            subprocess.run(
                ["git", "commit", "-m", f"watchdog: log update {_now_utc()[:16]}"],
                cwd=BASE, capture_output=True, timeout=30,
            )
            subprocess.run(
                ["git", "push"],
                cwd=BASE, capture_output=True, timeout=30,
            )
    except Exception as exc:
        logger.warning("watchdog: git push failed: %s", exc)


# ── Main loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info("watchdog: starting — poll_interval=%ds stale_threshold=%dmin",
                POLL_INTERVAL, BOOK_STALE_MIN)

    events:   list[dict] = []
    snapshot: ProgressSnapshot = ProgressSnapshot()
    last_push: float = 0.0

    def _log_event(event: str, detail: str = "") -> None:
        ts = _now_utc()
        logger.info("watchdog event: %s — %s", event, detail)
        events.append({"ts": ts, "event": event, "detail": detail})
        _write_watchdog_log(events)

    while True:
        # ── Check book-ingest-queue ──────────────────────────────────────────
        book_svc_active = _svc_active("book-ingest-queue")

        if not book_svc_active:
            _log_event("RESTART_BOOK_INGEST", "service not active — restarting")
            ok = _svc_restart("book-ingest-queue")
            snapshot.reset()
            _log_event(
                "RESTART_OK" if ok else "RESTART_FAILED",
                "book-ingest-queue",
            )
        else:
            # Check for stalled progress
            cur = _read_book_current()
            if cur.get("filename"):
                stale = snapshot.check(cur)
                if stale:
                    detail = (
                        f"{cur['filename']} phase={cur.get('phase','?')} "
                        f"no progress for ≥{BOOK_STALE_MIN}min"
                    )
                    _log_event("STALE_DETECTED", detail)
                    ok = _svc_restart("book-ingest-queue")
                    snapshot.reset()
                    _log_event(
                        "RESTART_OK" if ok else "RESTART_FAILED",
                        "book-ingest-queue (stale)",
                    )
            else:
                # Queue idle — reset stale tracker
                snapshot.reset()

        # ── Check transcription-queue ────────────────────────────────────────
        trans_active = _svc_active("transcription-queue")
        trans_waiting = _trans_queue_len()

        if not trans_active and trans_waiting > 0:
            _log_event(
                "RESTART_TRANSCRIPTION",
                f"service not active but {trans_waiting} videos waiting — restarting",
            )
            ok = _svc_restart("transcription-queue")
            _log_event(
                "RESTART_OK" if ok else "RESTART_FAILED",
                "transcription-queue",
            )

        # Push log to git every 10 minutes
        now = time.monotonic()
        if now - last_push >= 600:
            _push_log()
            last_push = now

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
