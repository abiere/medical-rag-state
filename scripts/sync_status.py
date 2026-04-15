#!/usr/bin/env python3
"""
Generates SYSTEM_DOCS/LIVE_STATUS.md and pushes to GitHub.
Intended to run every 5 minutes via sync-status.timer.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import psutil

BASE      = Path("/root/medical-rag")
OUT_FILE  = BASE / "SYSTEM_DOCS" / "LIVE_STATUS.md"
TRANS_DIR = BASE / "data" / "transcripts"
VIDEOS_DIR = BASE / "videos"
QUEUE_FILE   = Path("/tmp/transcription_queue.json")
CURRENT_FILE = Path("/tmp/transcription_current.json")
MARKERS_FILE = Path("/var/log/markers.json")
QUEUE_LOG    = Path("/var/log/transcription_queue.log")
BOOKS_DIR        = BASE / "books"
BOOK_QUEUE_FILE  = Path("/tmp/book_ingest_queue.json")
BOOK_CURRENT_FILE = Path("/tmp/book_ingest_current.json")
QUALITY_DIR      = BASE / "data" / "book_quality"
BOOK_EXTS = {".pdf", ".epub"}
COLLECTION_MAP = {
    "medical": "medical_literature", "anatomy": "anatomy_atlas",
    "acupuncture": "acupuncture_points", "nrt": "nrt_curriculum",
    "qat": "qat_curriculum", "device": "device_documentation",
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _svc(name: str) -> str:
    try:
        r = subprocess.run(["systemctl", "is-active", name],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _docker_health(container: str) -> str:
    try:
        r = subprocess.run(
            ["docker", "inspect", "--format={{.State.Health.Status}}", container],
            capture_output=True, text=True, timeout=5,
        )
        s = r.stdout.strip()
        return s if s else "unknown"
    except Exception:
        return "unknown"


def _svc_icon(s: str) -> str:
    return "✅" if s == "active" else ("⚠️" if s in ("activating", "deactivating") else "❌")


def _health_icon(s: str) -> str:
    return "✅" if s == "healthy" else ("⚠️" if s == "starting" else "❌")


def _current_job() -> str:
    try:
        if CURRENT_FILE.exists():
            d = json.loads(CURRENT_FILE.read_text())
            f = d.get("file", "")
            ts = d.get("started", "")
            if f:
                return f"`{f}`" + (f" (since {ts[:19]})" if ts else "")
    except Exception:
        pass
    return "idle"


def _queue_count() -> int:
    try:
        if QUEUE_FILE.exists():
            q = json.loads(QUEUE_FILE.read_text())
            return len(q) if isinstance(q, list) else 0
    except Exception:
        pass
    return 0


def _done_count() -> int:
    try:
        return sum(1 for _ in TRANS_DIR.rglob("*.json")) if TRANS_DIR.exists() else 0
    except Exception:
        return 0


def _total_videos() -> int:
    exts = {".mp4", ".mov", ".mkv", ".m4v"}
    try:
        return sum(1 for f in VIDEOS_DIR.rglob("*") if f.suffix.lower() in exts)
    except Exception:
        return 0


def _uptime() -> str:
    try:
        r = subprocess.run(["uptime", "-p"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _markers_section() -> str:
    try:
        if MARKERS_FILE.exists():
            data = json.loads(MARKERS_FILE.read_text())
            if isinstance(data, list) and data:
                last5 = data[-5:]
                return "\n".join(
                    f"- `{m.get('timestamp', '?')}` **{m.get('event', '?')}** — {m.get('message', '')}"
                    for m in reversed(last5)
                )
    except Exception:
        pass
    return "_geen markers_"


def _book_stats() -> tuple[int, int, int, str]:
    """Returns (total, ingested, queued, current_book)."""
    total = ingested = queued = 0
    current = ""
    try:
        for sub in COLLECTION_MAP:
            d = BOOKS_DIR / sub
            if d.exists():
                total += sum(1 for f in d.iterdir() if f.suffix.lower() in BOOK_EXTS)
    except Exception:
        pass
    try:
        if BOOK_QUEUE_FILE.exists():
            q = json.loads(BOOK_QUEUE_FILE.read_text())
            queued = len(q) if isinstance(q, list) else 0
    except Exception:
        pass
    try:
        if BOOK_CURRENT_FILE.exists():
            current = json.loads(BOOK_CURRENT_FILE.read_text()).get("filename", "")
    except Exception:
        pass
    try:
        if QUALITY_DIR.exists():
            ingested = sum(
                1 for af in QUALITY_DIR.glob("*_audit.json")
                if json.loads(af.read_text()).get("status") == "approved"
            )
    except Exception:
        pass
    return total, ingested, queued, current


def _queue_log_tail() -> str:
    try:
        if QUEUE_LOG.exists():
            lines = QUEUE_LOG.read_text(errors="replace").splitlines()
            return "\n".join(lines[-10:]) if lines else "_leeg_"
    except Exception:
        pass
    return "_log niet gevonden_"


# ── build document ────────────────────────────────────────────────────────────

def build_md() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    web_s   = _svc("medical-rag-web")
    queue_s = _svc("transcription-queue")
    ttyd_s  = _svc("ttyd")
    qdr_s   = _docker_health("qdrant")
    oll_s   = _docker_health("ollama")

    mem = psutil.virtual_memory()
    dsk = psutil.disk_usage("/")
    cpu = psutil.cpu_percent(interval=0.5)

    ram_used  = round(mem.used  / 1e9, 2)
    ram_total = round(mem.total / 1e9, 2)
    dsk_used  = round(dsk.used  / 1e9, 1)
    dsk_total = round(dsk.total / 1e9, 1)

    book_total, book_ingested, book_queued, book_current = _book_stats()
    book_ingest_s = _svc("book-ingest-queue")

    return f"""# LIVE STATUS — auto-updated every 5 minutes
> Last update: **{ts} UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | {_svc_icon(web_s)} {web_s} |
| transcription-queue | {_svc_icon(queue_s)} {queue_s} |
| book-ingest-queue | {_svc_icon(book_ingest_s)} {book_ingest_s} |
| ttyd | {_svc_icon(ttyd_s)} {ttyd_s} |
| qdrant | {_health_icon(qdr_s)} {qdr_s} |
| ollama | {_health_icon(oll_s)} {oll_s} |

## Books
| Metric | Value |
|---|---|
| Total books | {book_total} |
| Ingested | {book_ingested} |
| Queued | {book_queued} |
| Current job | {('`' + book_current + '`') if book_current else 'idle'} |

## Transcription
| Metric | Value |
|---|---|
| Current job | {_current_job()} |
| Queued | {_queue_count()} |
| Done | {_done_count()} |
| Total videos | {_total_videos()} |

## System
| Metric | Value |
|---|---|
| RAM used | {ram_used} GB / {ram_total} GB ({mem.percent:.0f}%) |
| CPU | {cpu:.1f}% |
| Disk used | {dsk_used} GB / {dsk_total} GB ({dsk.percent:.0f}%) |
| Uptime | {_uptime()} |

## Recent markers
{_markers_section()}

## Queue log (last 10 lines)
```
{_queue_log_tail()}
```
"""


# ── write & push ──────────────────────────────────────────────────────────────

def main() -> None:
    content = build_md()
    OUT_FILE.write_text(content)
    print(f"Written: {OUT_FILE}")

    files_to_add = ["SYSTEM_DOCS/LIVE_STATUS.md"]
    backlog = BASE / "SYSTEM_DOCS" / "BACKLOG.md"
    if backlog.exists():
        files_to_add.append("SYSTEM_DOCS/BACKLOG.md")

    result = subprocess.run(
        ["git", "add"] + files_to_add,
        cwd=BASE, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"git add failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Check if there is actually a change to commit
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=BASE,
    )
    if diff.returncode == 0:
        print("No change — nothing to commit.")
        return

    ts_short = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    commit = subprocess.run(
        ["git", "commit", "-m", f"status: live update {ts_short}"],
        cwd=BASE, capture_output=True, text=True,
    )
    if commit.returncode != 0:
        print(f"git commit failed: {commit.stderr}", file=sys.stderr)
        sys.exit(1)

    push = subprocess.run(
        ["git", "push"],
        cwd=BASE, capture_output=True, text=True,
    )
    if push.returncode != 0:
        print(f"git push failed: {push.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"Pushed at {ts_short}")


if __name__ == "__main__":
    main()
