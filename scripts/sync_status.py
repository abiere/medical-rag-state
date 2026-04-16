#!/usr/bin/env python3
"""
Generates SYSTEM_DOCS/LIVE_STATUS.md and pushes to GitHub.
Intended to run every 5 minutes via sync-status.timer.
"""

import json
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import psutil

BASE      = Path("/root/medical-rag")
OUT_FILE  = BASE / "SYSTEM_DOCS" / "LIVE_STATUS.md"
TRANS_DIR = BASE / "data" / "transcripts"
VIDEOS_DIR = BASE / "videos"
QUEUE_FILE   = Path("/tmp/transcription_queue.json")
CURRENT_FILE = Path("/tmp/transcription_current.json")
MARKERS_FILE  = Path("/var/log/markers.json")
QUEUE_LOG     = Path("/var/log/transcription_queue.log")
ERROR_LOG     = Path("/var/log/sync_status_errors.log")
CONSISTENCY_LOG = Path("/var/log/nightly_consistency.log")
BOOKS_DIR          = BASE / "books"
BOOK_QUEUE_FILE    = Path("/tmp/book_ingest_queue.json")
BOOK_CURRENT_FILE  = Path("/tmp/book_ingest_current.json")
QUALITY_DIR        = BASE / "data" / "book_quality"
IMAGE_APPROVALS    = BASE / "data" / "image_approvals.json"
BOOK_EXTS          = {".pdf", ".epub"}
SECTION_DIRS       = ["medical_literature", "nrt_qat", "device"]
AI_INSTRUCTIONS_SRC = BASE / "config" / "ai_instructions"
AI_INSTRUCTIONS_DST = BASE / "AI_INSTRUCTIONS"


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


def _elapsed_min(started_str: str) -> int:
    """Return elapsed minutes since started_str (ISO format), or 0 on error."""
    try:
        started = datetime.fromisoformat(started_str)
        if started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        return int((datetime.now(timezone.utc) - started).total_seconds() / 60)
    except Exception:
        return 0


def _qdrant_vector_count(collection: str) -> str:
    """Return vector count for a Qdrant collection as string, or '?' on error."""
    try:
        req = urllib.request.Request(f"http://localhost:6333/collections/{collection}")
        with urllib.request.urlopen(req, timeout=4) as resp:
            d = json.loads(resp.read())
            res = d.get("result", {})
            n = res.get("vectors_count") or res.get("points_count", 0)
            return str(n)
    except Exception:
        return "?"


def _current_job() -> str:
    try:
        if CURRENT_FILE.exists():
            d = json.loads(CURRENT_FILE.read_text())
            f = d.get("file", "")
            ts = d.get("started", "")
            if f:
                mins = _elapsed_min(ts) if ts else 0
                suffix = f" ({mins} min)" if mins else ""
                return f"`{f}`{suffix}"
    except Exception:
        pass
    return "idle"


def _book_current_display() -> str:
    try:
        if BOOK_CURRENT_FILE.exists():
            d = json.loads(BOOK_CURRENT_FILE.read_text())
            f = d.get("filename", "")
            ts = d.get("started", "")
            if f:
                mins = _elapsed_min(ts) if ts else 0
                suffix = f" ({mins} min)" if mins else ""
                return f"`{f}`{suffix}"
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


def _image_stats() -> tuple[int, int]:
    """Returns (pending, approved) image counts."""
    try:
        if IMAGE_APPROVALS.exists():
            data = json.loads(IMAGE_APPROVALS.read_text())
            return len(data.get("pending", [])), len(data.get("approved", []))
    except Exception:
        pass
    return 0, 0


def _book_stats() -> tuple[int, int, int, str]:
    """Returns (total, ingested, queued, current_book)."""
    total = ingested = queued = 0
    current = ""
    try:
        for sub in SECTION_DIRS:
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


def _consistency_summary() -> str:
    """Return last nightly consistency check summary, or a placeholder."""
    try:
        if CONSISTENCY_LOG.exists():
            lines = [l for l in CONSISTENCY_LOG.read_text(errors="replace").splitlines() if l.strip()]
            return "\n".join(lines[-8:]) if lines else "_nog niet uitgevoerd_"
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

    book_total, book_ingested, book_queued, _unused = _book_stats()
    book_current_disp = _book_current_display()
    imgs_pending, imgs_approved = _image_stats()
    book_ingest_s = _svc("book-ingest-queue")
    ml_vectors = _qdrant_vector_count("medical_library")
    vt_vectors  = _qdrant_vector_count("video_transcripts")

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

## Book Ingest
| Metric | Value |
|---|---|
| Current job | {book_current_disp} |
| Queued | {book_queued} |
| Total books | {book_total} |
| Ingested | {book_ingested} |
| Vectors in medical_library | {ml_vectors} |
| Images pending approval | {imgs_pending} |
| Images approved | {imgs_approved} |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | {_current_job()} |
| Queued | {_queue_count()} |
| Done | {_done_count()} / {_total_videos()} |
| Vectors in video_transcripts | {vt_vectors} |

## System
| Metric | Value |
|---|---|
| RAM used | {ram_used} GB / {ram_total} GB ({mem.percent:.0f}%) |
| CPU | {cpu:.1f}% |
| Disk used | {dsk_used} GB / {dsk_total} GB ({dsk.percent:.0f}%) |
| Uptime | {_uptime()} |

## Recent markers
{_markers_section()}

## Nightly Consistency
```
{_consistency_summary()}
```

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

    # Copy AI instructions to AI_INSTRUCTIONS/ for Lead Architect visibility
    if AI_INSTRUCTIONS_SRC.exists():
        AI_INSTRUCTIONS_DST.mkdir(exist_ok=True)
        for f in AI_INSTRUCTIONS_SRC.glob("*.md"):
            shutil.copy2(f, AI_INSTRUCTIONS_DST / f.name)

    files_to_add = ["SYSTEM_DOCS/LIVE_STATUS.md"]
    backlog = BASE / "SYSTEM_DOCS" / "BACKLOG.md"
    if backlog.exists():
        files_to_add.append("SYSTEM_DOCS/BACKLOG.md")
    watchdog_log = BASE / "SYSTEM_DOCS" / "WATCHDOG_LOG.md"
    if watchdog_log.exists():
        files_to_add.append("SYSTEM_DOCS/WATCHDOG_LOG.md")
    if AI_INSTRUCTIONS_DST.exists():
        files_to_add.append("AI_INSTRUCTIONS/")

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

    # Retry push up to 3 times with 10-second delay
    push_ok = False
    last_push_err = ""
    for attempt in range(1, 4):
        push = subprocess.run(
            ["git", "push"],
            cwd=BASE, capture_output=True, text=True,
        )
        if push.returncode == 0:
            push_ok = True
            break
        last_push_err = push.stderr.strip()
        print(f"git push failed (attempt {attempt}/3): {last_push_err}", file=sys.stderr)
        if attempt < 3:
            time.sleep(10)

    if push_ok:
        print(f"Pushed at {ts_short}")
    else:
        err_line = f"{datetime.now(timezone.utc).isoformat()} — push failed after 3 attempts: {last_push_err}\n"
        try:
            with open(ERROR_LOG, "a") as ef:
                ef.write(err_line)
        except Exception:
            pass
        print(f"All push attempts failed — LIVE_STATUS.md written locally, error logged to {ERROR_LOG}", file=sys.stderr)
        # Do NOT sys.exit(1) — local write succeeded; no need to crash the timer


if __name__ == "__main__":
    main()
