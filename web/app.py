from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import httpx, psutil, subprocess, json, os, re, shutil, time
from pathlib import Path
from datetime import datetime

app = FastAPI()
BASE         = Path("/root/medical-rag")
VIDEOS_DIR   = BASE / "videos"
TRANS_DIR    = BASE / "data" / "transcripts"
QUEUE_FILE   = Path("/tmp/transcription_queue.json")
CURRENT_FILE = Path("/tmp/transcription_current.json")
MARKERS_FILE = Path("/var/log/markers.json")

BOOKS_DIR          = BASE / "books"
BOOK_QUEUE_FILE    = Path("/tmp/book_ingest_queue.json")
BOOK_CURRENT_FILE  = Path("/tmp/book_ingest_current.json")
QUALITY_DIR        = BASE / "data" / "book_quality"

SECTION_MAP = {
    "medical_literature": {
        "label":       "Medische Literatuur",
        "color":       "#2563eb",
        "collection":  "medical_library",
        "category":    "medical_literature",
        "description": "Upload PDF of EPUB — AI analyseert automatisch bruikbaarheid",
    },
    "nrt_qat": {
        "label":       "NRT & QAT Curriculum",
        "color":       "#7c3aed",
        "collection":  "nrt_qat_curriculum",
        "category":    "nrt_qat",
        "description": "Eigen behandelmethode documentatie",
    },
    "device": {
        "label":       "Apparatuur",
        "color":       "#059669",
        "collection":  "device_documentation",
        "category":    "device",
        "description": "PEMF en RLT apparatuur documentatie",
    },
}
USABILITY_TAGS_FILE  = BASE / "config" / "usability_tags.json"
IMAGE_APPROVALS_FILE = BASE / "data" / "image_approvals.json"
BOOK_EXTS = {".pdf", ".epub"}

_LOG_MAP = {
    "transcription_queue": ("file",    "/var/log/transcription_queue.log"),
    "system":              ("file",    "/var/log/syslog"),
    "web":                 ("journal", "medical-rag-web"),
    "tests":               ("file",    "/root/medical-rag/data/last_test_run.log"),
}

VIDEO_TYPES = {
    "nrt":  "NRT — Neural Reset Therapy",
    "qat":  "QAT — Quantum Alignment Technique",
    "pemf": "PEMF — Pulsed Electromagnetic Field",
    "rlt":  "RLT — Red Light Therapy",
}
VIDEO_TYPE_COLORS = {
    "nrt":  "#2563eb",
    "qat":  "#7c3aed",
    "pemf": "#059669",
    "rlt":  "#dc2626",
}
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".m4v"}

# ── helpers ─────────────────────────────────────────────────────────────────

def _dir_size_gb(p: Path) -> str:
    try:
        r = subprocess.run(["du", "-sb", str(p)], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            b = int(r.stdout.split()[0])
            if b < 1_000_000:
                return f"{b/1024:.0f} KB"
            elif b < 1_000_000_000:
                return f"{b/1_000_000:.1f} MB"
            else:
                return f"{b/1_000_000_000:.2f} GB"
    except Exception:
        pass
    return "?"

def _file_count(p: Path, glob: str = "*") -> int:
    try:
        return sum(1 for _ in p.glob(glob) if _.is_file())
    except Exception:
        return 0

def _docker_containers() -> list[dict]:
    try:
        r = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Image}}"],
            capture_output=True, text=True, timeout=5
        )
        containers = []
        for line in r.stdout.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                name, status, image = parts[0], parts[1], parts[2]
                healthy = "healthy" in status or "Up" in status
                containers.append({"name": name, "status": status, "image": image, "ok": healthy})
        return containers
    except Exception:
        return []

def _qdrant_info() -> dict:
    try:
        r = httpx.get("http://localhost:6333/collections", timeout=4)
        cols = r.json()["result"]["collections"]
        info = {"online": True, "collections": []}
        for c in cols:
            name = c["name"]
            try:
                cr = httpx.get(f"http://localhost:6333/collections/{name}", timeout=4)
                res = cr.json()["result"]
                pts = res.get("vectors_count") or res.get("points_count", 0)
                info["collections"].append({"name": name, "vectors": pts})
            except Exception:
                info["collections"].append({"name": name, "vectors": "?"})
        return info
    except Exception:
        return {"online": False, "collections": []}

def _ollama_info() -> dict:
    try:
        r = httpx.get("http://localhost:11434/api/tags", timeout=4)
        models = []
        for m in r.json().get("models", []):
            size_gb = round(m.get("size", 0) / 1e9, 2)
            models.append({"name": m["name"], "size": f"{size_gb} GB"})
        return {"online": True, "models": models}
    except Exception:
        return {"online": False, "models": []}

def _progress_bar(pct: float, color: str = "#3b82f6") -> str:
    pct = min(max(pct, 0), 100)
    warn = pct > 80
    c = "#ef4444" if pct > 90 else ("#f59e0b" if warn else color)
    return (
        f'<div style="background:#e5e7eb;border-radius:6px;height:10px;overflow:hidden;margin-top:4px">'
        f'<div style="width:{pct:.1f}%;background:{c};height:10px;border-radius:6px;transition:width 0.3s"></div>'
        f'</div>'
    )

def _badge(text: str, ok: bool) -> str:
    bg = "#dcfce7" if ok else "#fee2e2"
    fg = "#166534" if ok else "#991b1b"
    dot = "#22c55e" if ok else "#ef4444"
    return (
        f'<span style="background:{bg};color:{fg};border-radius:999px;'
        f'padding:2px 10px;font-size:13px;font-weight:600;white-space:nowrap">'
        f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
        f'background:{dot};margin-right:5px;vertical-align:middle"></span>{text}</span>'
    )

def _card(title: str, body: str, accent: str = "#3b82f6") -> str:
    return (
        f'<div style="background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.08);'
        f'padding:20px;border-top:3px solid {accent}">'
        f'<div style="font-size:13px;font-weight:700;color:#6b7280;text-transform:uppercase;'
        f'letter-spacing:.05em;margin-bottom:12px">{title}</div>'
        f'{body}'
        f'</div>'
    )

def _stat_row(label: str, value: str) -> str:
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'padding:5px 0;border-bottom:1px solid #f3f4f6">'
        f'<span style="color:#374151;font-size:14px">{label}</span>'
        f'<span style="font-weight:600;color:#111827;font-size:14px">{value}</span>'
        f'</div>'
    )

# ── shared page shell ────────────────────────────────────────────────────────

NAV_ITEMS = [
    ("/",          "Dashboard"),
    ("/library",   "Bibliotheek"),
    ("/images",    "Afbeeldingen"),
    ("/protocols", "Protocollen"),
    ("/search",    "Zoeken"),
    ("/videos",    "Video's"),
    ("/terminal",  "Terminal"),
]

def _nav_html(active: str) -> str:
    links = ""
    for href, label in NAV_ITEMS:
        is_active = href == active
        bg = "background:rgba(255,255,255,.18);" if is_active else ""
        links += (
            f'<a href="{href}" style="color:#e0e7ff;text-decoration:none;'
            f'padding:6px 14px;border-radius:6px;font-size:14px;font-weight:500;{bg}">'
            f'{label}</a>'
        )
    return links

def _page_shell(title: str, active: str, body: str) -> str:
    nav = _nav_html(active)
    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Medical RAG — {title}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f1f5f9;color:#111827;min-height:100vh}}
  .wrap{{max-width:1100px;margin:0 auto;padding:24px 20px}}
  table{{width:100%;border-collapse:collapse}}
  th{{text-align:left;font-size:12px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;padding:8px 12px;border-bottom:2px solid #e5e7eb}}
  td{{padding:10px 12px;border-bottom:1px solid #f3f4f6;font-size:14px;vertical-align:middle}}
  tr:hover td{{background:#f9fafb}}
  .btn{{display:inline-block;padding:6px 14px;border-radius:7px;font-size:13px;font-weight:600;text-decoration:none;border:none;cursor:pointer;white-space:nowrap}}
  .btn-primary{{background:#2563eb;color:#fff}}
  .btn-secondary{{background:#f3f4f6;color:#374151}}
  .btn-purple{{background:#7c3aed;color:#fff}}
  .btn-green{{background:#059669;color:#fff}}
  .section{{background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:24px;overflow:hidden}}
  .section-head{{padding:16px 20px;border-bottom:1px solid #f3f4f6;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}}
  .section-title{{font-size:15px;font-weight:700;color:#111827}}
  .empty{{padding:24px 20px;color:#9ca3af;font-size:14px}}
  input[type=file]{{font-size:14px}}
  select,input[type=text]{{padding:7px 10px;border:1px solid #d1d5db;border-radius:7px;font-size:14px;background:#fff}}
  @media(max-width:600px){{.hide-sm{{display:none}}}}
</style>
</head>
<body>
<div style="background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);padding:16px 24px">
  <div style="max-width:1100px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
    <div>
      <div style="color:#fff;font-size:20px;font-weight:700;letter-spacing:-.02em">⚕ Medical RAG</div>
      <div style="color:#93c5fd;font-size:13px">NRT-Amsterdam.nl</div>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap">{nav}</div>
  </div>
</div>
{body}
</body></html>"""

# ── video helpers ─────────────────────────────────────────────────────────────

def _video_duration(path: Path) -> str:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            secs = float(r.stdout.strip())
            m, s = divmod(int(secs), 60)
            h, m = divmod(m, 60)
            return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
    except Exception:
        pass
    return "—"

def _fmt_bytes(b: int) -> str:
    if b >= 1_000_000_000: return f"{b/1e9:.2f} GB"
    if b >= 1_000_000:     return f"{b/1e6:.1f} MB"
    return f"{b/1024:.0f} KB"

def _ts(secs: float) -> str:
    m, s = divmod(int(secs), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def _list_videos(vtype: str) -> list[dict]:
    d = VIDEOS_DIR / vtype
    if not d.exists():
        return []
    out = []
    for f in sorted(d.iterdir()):
        if f.suffix.lower() in VIDEO_EXTS:
            transcript = TRANS_DIR / f"{f.stem}.json"
            out.append({
                "path":       f,
                "name":       f.name,
                "size":       _fmt_bytes(f.stat().st_size),
                "duration":   _video_duration(f),
                "transcribed": transcript.exists(),
            })
    return out

_CONTENT_TYPE_MAP = {
    "nrt":  "training_nrt",
    "qat":  "training_qat",
    "pemf": "device_pemf",
    "rlt":  "device_rlt",
}

def _run_transcription(video_path: str, video_type: str) -> None:
    """Enqueue a video for transcription (picked up by transcription-queue service)."""
    filename = Path(video_path).name
    entry = {
        "video_type": video_type,
        "filename":   filename,
        "requested":  datetime.now().isoformat(),
    }
    try:
        if QUEUE_FILE.exists():
            with open(QUEUE_FILE) as f:
                queue = json.load(f)
            if not isinstance(queue, list):
                queue = []
        else:
            queue = []
    except Exception:
        queue = []

    # Add only if not already queued
    existing = {(i.get("video_type"), i.get("filename")) for i in queue}
    if (video_type, filename) not in existing:
        queue.append(entry)
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2)

# ── routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # ── system ──
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    dsk = psutil.disk_usage("/")
    mem_used_gb  = mem.used  / 1e9
    mem_total_gb = mem.total / 1e9
    dsk_used_gb  = dsk.used  / 1e9
    dsk_total_gb = dsk.total / 1e9
    mem_pct = mem.percent
    dsk_pct = dsk.percent

    # ── services ──
    qdrant  = _qdrant_info()
    ollama  = _ollama_info()
    dockers = _docker_containers()

    # ── rag stats ──
    books_dir  = BASE / "books"
    imgs_dir   = BASE / "data" / "extracted_images"
    logs_dir   = BASE / "data" / "processing_logs"
    trans_dir  = BASE / "data" / "transcripts"
    proto_dir  = BASE / "data" / "protocols" if (BASE / "data" / "protocols").exists() else None

    n_books_total    = _file_count(books_dir, "*.pdf") + _file_count(books_dir, "*.epub")
    n_books_ingested = _file_count(logs_dir, "*.json")
    n_books_pending  = max(0, n_books_total - n_books_ingested)
    n_figures        = _file_count(imgs_dir, "*.png")
    n_transcripts    = _file_count(trans_dir, "*.txt")
    n_protocols      = _file_count(proto_dir, "*.docx") if proto_dir else 0

    # total chunks across all qdrant collections
    total_chunks = sum(
        c["vectors"] for c in qdrant["collections"] if isinstance(c["vectors"], int)
    )

    # ── directory sizes ──
    sz_books  = _dir_size_gb(books_dir)
    sz_qdrant = _dir_size_gb(BASE / "data" / "qdrant")
    sz_ollama = _dir_size_gb(BASE / "data" / "ollama")

    # ── build HTML ──────────────────────────────────────────────────────────

    # nav
    nav_items = [
        ("/",          "Dashboard"),
        ("/library",   "Bibliotheek"),
        ("/images",    "Afbeeldingen"),
        ("/protocols", "Protocollen"),
        ("/search",    "Zoeken"),
        ("/videos",    "Video's"),
    ]
    nav_links = "".join(
        f'<a href="{href}" style="color:#e0e7ff;text-decoration:none;padding:6px 14px;'
        f'border-radius:6px;font-size:14px;font-weight:500;'
        f'{"background:rgba(255,255,255,.15)" if href=="/" else ""}">{label}</a>'
        for href, label in nav_items
    )

    # system card
    sys_body = (
        _stat_row("CPU gebruik", f"{cpu:.1f}%")
        + _progress_bar(cpu, "#8b5cf6")
        + "<div style='height:10px'></div>"
        + _stat_row("RAM geheugen", f"{mem_used_gb:.1f} GB / {mem_total_gb:.1f} GB ({mem_pct:.0f}%)")
        + _progress_bar(mem_pct)
        + "<div style='height:10px'></div>"
        + _stat_row("Schijfruimte", f"{dsk_used_gb:.1f} GB / {dsk_total_gb:.1f} GB ({dsk_pct:.0f}%)")
        + _progress_bar(dsk_pct, "#10b981")
    )

    # qdrant card
    if qdrant["online"]:
        q_body = _badge("Online", True) + "<div style='height:10px'></div>"
        if qdrant["collections"]:
            for col in qdrant["collections"]:
                vcount = f'{col["vectors"]:,}' if isinstance(col["vectors"], int) else col["vectors"]
                q_body += _stat_row(col["name"], f"{vcount} vectoren")
        else:
            q_body += '<div style="color:#6b7280;font-size:14px">Geen collecties aangemaakt</div>'
    else:
        q_body = _badge("Offline", False)

    # ollama card
    if ollama["online"]:
        o_body = _badge("Online", True) + "<div style='height:10px'></div>"
        if ollama["models"]:
            for m in ollama["models"]:
                o_body += _stat_row(m["name"], m["size"])
        else:
            o_body += '<div style="color:#6b7280;font-size:14px">Geen modellen geladen</div>'
    else:
        o_body = _badge("Offline", False)

    # docker card
    if dockers:
        d_body = "".join(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:5px 0;border-bottom:1px solid #f3f4f6">'
            f'<span style="color:#374151;font-size:14px;font-weight:500">{c["name"]}</span>'
            f'{_badge("Actief" if c["ok"] else "Gestopt", c["ok"])}'
            f'</div>'
            for c in dockers
        )
    else:
        d_body = '<div style="color:#6b7280;font-size:14px">Geen containers gevonden</div>'

    # rag stats card
    rag_body = (
        _stat_row("Boeken (totaal)", str(n_books_total) if n_books_total else "0 — nog leeg")
        + _stat_row("Ingested", str(n_books_ingested))
        + _stat_row("In wachtrij", str(n_books_pending))
        + _stat_row("Vectorchunks", f"{total_chunks:,}" if total_chunks else "0")
        + _stat_row("Figuren", str(n_figures))
        + _stat_row("Video transcripten", str(n_transcripts))
        + _stat_row("Protocollen (.docx)", str(n_protocols))
    )

    # dir sizes card
    dir_body = (
        _stat_row("books/", sz_books)
        + _stat_row("data/qdrant/", sz_qdrant)
        + _stat_row("data/ollama/", sz_ollama)
    )

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Medical RAG — Dashboard</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f1f5f9;color:#111827;min-height:100vh}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;padding:20px}}
  @media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<!-- header -->
<div style="background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);padding:16px 24px">
  <div style="max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
    <div>
      <div style="color:#fff;font-size:20px;font-weight:700;letter-spacing:-.02em">⚕ Medical RAG</div>
      <div style="color:#93c5fd;font-size:13px">NRT-Amsterdam.nl</div>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap">{nav_links}</div>
  </div>
</div>

<!-- timestamp + refresh -->
<div style="max-width:1200px;margin:0 auto;padding:12px 24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
  <span style="color:#6b7280;font-size:13px">Bijgewerkt: {now}</span>
  <span id="countdown" style="color:#9ca3af;font-size:13px">Vernieuwt over 30s</span>
</div>

<!-- grid -->
<div class="grid" style="max-width:1200px;margin:0 auto">
  {_card("Systeembronnen", sys_body, "#8b5cf6")}
  {_card("Qdrant — Vector Store", q_body, "#3b82f6")}
  {_card("Ollama — LLM", o_body, "#10b981")}
  {_card("Docker containers", d_body, "#f59e0b")}
  {_card("RAG statistieken", rag_body, "#ec4899")}
  {_card("Opslagruimte", dir_body, "#14b8a6")}
</div>

<!-- quick actions -->
<div style="max-width:1200px;margin:0 auto;padding:0 20px 24px">
  <div style="background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.08);padding:20px">
    <div style="font-size:13px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;margin-bottom:14px">Snelle acties</div>
    <div style="display:flex;gap:10px;flex-wrap:wrap">
      <a href="/library" style="background:#2563eb;color:#fff;text-decoration:none;padding:9px 18px;border-radius:8px;font-size:14px;font-weight:600">+ Boek uploaden</a>
      <a href="/videos" style="background:#7c3aed;color:#fff;text-decoration:none;padding:9px 18px;border-radius:8px;font-size:14px;font-weight:600">+ Video toevoegen</a>
      <a href="/protocols" style="background:#059669;color:#fff;text-decoration:none;padding:9px 18px;border-radius:8px;font-size:14px;font-weight:600">Nieuw protocol</a>
      <a href="/search" style="background:#0891b2;color:#fff;text-decoration:none;padding:9px 18px;border-radius:8px;font-size:14px;font-weight:600">Zoeken in RAG</a>
    </div>
  </div>
</div>

<script>
let secs = 30;
const el = document.getElementById("countdown");
setInterval(() => {{
  secs--;
  if (secs <= 0) location.reload();
  el.textContent = `Vernieuwt over ${{secs}}s`;
}}, 1000);
</script>
</body>
</html>"""

    return html


# ── GET /videos/status ────────────────────────────────────────────────────────

@app.get("/videos/status/{video_type}/{filename}")
async def videos_status(video_type: str, filename: str):
    if video_type not in VIDEO_TYPES:
        return {"status": "error"}
    safe = Path(filename).name          # strip any path traversal
    stem = Path(safe).stem

    # 1. Transcript exists → done
    if (TRANS_DIR / f"{stem}.json").exists():
        return {"status": "done"}

    # 2. Currently being processed by queue manager → running
    if CURRENT_FILE.exists():
        try:
            with open(CURRENT_FILE) as f:
                current = json.load(f)
            if current.get("file", "").strip() == safe.strip():
                return {"status": "running"}
        except Exception:
            pass

    # 3. Waiting in queue → queued
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE) as f:
                queue = json.load(f)
            for item in queue:
                if item.get("filename", "").strip() == safe.strip() and item.get("video_type") == video_type:
                    return {"status": "queued"}
        except Exception:
            pass

    # 4. Not queued, not running, no transcript
    return {"status": "waiting"}


# ── GET /videos ───────────────────────────────────────────────────────────────

_VIDEO_SCRIPT = r"""
<style>
@keyframes _vspin{to{transform:rotate(360deg)}}
.vspin{display:inline-block;width:11px;height:11px;border:2px solid #93c5fd;
       border-top-color:#1d4ed8;border-radius:50%;
       animation:_vspin .8s linear infinite;vertical-align:middle;margin-right:5px}
</style>
<script>
const _timers = {};
function _clearTimer(k) { if (_timers[k]) { clearInterval(_timers[k]); delete _timers[k]; } }

function setRunning(vtype, safeId) {
  document.getElementById('status-' + vtype + '-' + safeId).innerHTML =
    '<span style="background:#dbeafe;color:#1e40af;border-radius:999px;padding:2px 9px;font-size:12px;font-weight:600">' +
    '<span class="vspin"></span>Bezig</span>';
  const actEl = document.getElementById('actions-' + vtype + '-' + safeId);
  const key = vtype + '-' + safeId;
  let secs = 0;
  actEl.innerHTML = '<span id="timer-' + key + '" style="color:#6b7280;font-size:13px;font-style:italic">Bezig... 0:00</span>';
  _timers[key] = setInterval(() => {
    secs++;
    const el = document.getElementById('timer-' + key);
    if (el) el.textContent = 'Bezig... ' + Math.floor(secs/60) + ':' + String(secs%60).padStart(2,'0');
  }, 1000);
}

function setDone(vtype, safeId, filename) {
  _clearTimer(vtype + '-' + safeId);
  const stem = filename.replace(/\.[^.]+$/, '');
  document.getElementById('status-' + vtype + '-' + safeId).innerHTML =
    '<span style="background:#dcfce7;color:#166534;border-radius:999px;padding:2px 9px;font-size:12px;font-weight:600">&#10003; Klaar</span>';
  document.getElementById('actions-' + vtype + '-' + safeId).innerHTML =
    '<a href="/videos/transcript/' + vtype + '/' + stem + '" class="btn btn-secondary">Transcript bekijken</a>';
}

function setQueued(vtype, safeId) {
  _clearTimer(vtype + '-' + safeId);
  document.getElementById('status-' + vtype + '-' + safeId).innerHTML =
    '<span style="background:#fef3c7;color:#92400e;border-radius:999px;padding:2px 9px;font-size:12px;font-weight:600">In wachtrij</span>';
  const actEl = document.getElementById('actions-' + vtype + '-' + safeId);
  if (actEl) actEl.innerHTML = '<span style="color:#6b7280;font-size:13px;font-style:italic">Wacht op verwerking...</span>';
}

function startPoll(vtype, filename, safeId) {
  let _state = null;
  const iv = setInterval(() => {
    fetch('/videos/status/' + vtype + '/' + encodeURIComponent(filename))
      .then(r => r.json())
      .then(d => {
        if (d.status === 'done') {
          clearInterval(iv);
          setDone(vtype, safeId, filename);
        } else if (d.status === 'running' && _state !== 'running') {
          _state = 'running';
          setRunning(vtype, safeId);
        } else if (d.status === 'queued' && _state !== 'queued') {
          _state = 'queued';
          setQueued(vtype, safeId);
        } else if (d.status === 'error') {
          clearInterval(iv); _clearTimer(vtype + '-' + safeId);
          document.getElementById('actions-' + vtype + '-' + safeId).innerHTML =
            '<span style="color:#ef4444;font-size:13px">Fout bij transcriptie</span>';
        }
      })
      .catch(() => clearInterval(iv));
  }, 5000);
}

function manualTranscribe(vtype, filename, safeId) {
  const fd = new FormData();
  fd.append('video_type', vtype);
  fd.append('filename', filename);
  fetch('/videos/transcribe', {method:'POST', body:fd})
    .then(r => r.json())
    .then(d => {
      if (d.status === 'started') {
        if (document.getElementById('status-' + vtype + '-' + safeId)) {
          setQueued(vtype, safeId);
          startPoll(vtype, filename, safeId);
        } else {
          location.reload();
        }
      }
    });
}

function _uploadFile(vtype, file, idx, total) {
  return new Promise(resolve => {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('video_type', vtype);
    const lbl = document.getElementById('upload-label-' + vtype);
    if (lbl) lbl.textContent = total > 1 ? 'Bestand ' + idx + '/' + total + ' uploaden...' : 'Bezig met uploaden...';
    document.getElementById('pct-' + vtype).textContent = '0%';
    document.getElementById('bar-' + vtype).style.width = '0%';
    document.getElementById('mb-' + vtype).textContent = '';
    const xhr = new XMLHttpRequest();
    xhr.upload.addEventListener('progress', e => {
      if (e.lengthComputable) {
        const pct = Math.round(e.loaded / e.total * 100);
        document.getElementById('pct-' + vtype).textContent = pct + '%';
        document.getElementById('bar-' + vtype).style.width = pct + '%';
        document.getElementById('mb-' + vtype).textContent =
          (e.loaded/1e6).toFixed(1) + ' MB / ' + (e.total/1e6).toFixed(1) + ' MB';
      }
    });
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) resolve(JSON.parse(xhr.responseText));
      else resolve(null);
    });
    xhr.addEventListener('error', () => resolve(null));
    xhr.open('POST', '/videos/upload');
    xhr.send(fd);
  });
}

async function doUpload(vtype) {
  const inp = document.getElementById('file-' + vtype);
  if (!inp.files.length) { alert('Selecteer eerst een videobestand'); return; }
  const files = Array.from(inp.files);
  document.getElementById('progress-' + vtype).style.display = 'block';
  const uploaded = [];
  for (let i = 0; i < files.length; i++) {
    const d = await _uploadFile(vtype, files[i], i + 1, files.length);
    if (d) uploaded.push(d.filename);
    else {
      document.getElementById('msg-' + vtype).textContent = 'Upload mislukt: ' + files[i].name;
      document.getElementById('msg-' + vtype).style.display = 'block';
    }
  }
  if (!uploaded.length) { document.getElementById('progress-' + vtype).style.display = 'none'; return; }
  document.getElementById('pct-' + vtype).textContent = '&#10003;';
  document.getElementById('mb-' + vtype).textContent =
    uploaded.length + (uploaded.length === 1 ? ' bestand' : ' bestanden') + ' ge\u00fcpload. Transcriptie wordt gestart...';
  for (const filename of uploaded) {
    const fd = new FormData();
    fd.append('video_type', vtype);
    fd.append('filename', filename);
    await fetch('/videos/transcribe', {method:'POST', body:fd});
  }
  setTimeout(() => location.reload(), 300);
}

window.addEventListener('load', () => {
  document.querySelectorAll('tr[data-transcribed="false"]').forEach(row => {
    const vtype    = row.dataset.vtype;
    const filename = row.dataset.filename;
    const safeId   = row.dataset.safeId;
    fetch('/videos/status/' + vtype + '/' + encodeURIComponent(filename))
      .then(r => r.json())
      .then(d => {
        if (d.status === 'running') { setRunning(vtype, safeId); startPoll(vtype, filename, safeId); }
        else if (d.status === 'queued') { setQueued(vtype, safeId); startPoll(vtype, filename, safeId); }
        else if (d.status === 'done') { setDone(vtype, safeId, filename); }
      });
  });
});
</script>"""


@app.get("/videos", response_class=HTMLResponse)
async def videos_page():
    sections_html = ""

    for vtype, vname in VIDEO_TYPES.items():
        color    = VIDEO_TYPE_COLORS[vtype]
        videos   = _list_videos(vtype)
        n_done   = sum(1 for v in videos if v["transcribed"])
        n_total  = len(videos)
        counter  = f'<span style="font-size:13px;color:#6b7280;font-weight:400">{n_done}/{n_total} getranscribeerd</span>'

        if videos:
            rows = ""
            for v in videos:
                safe_id  = re.sub(r"[^\w]", "_", v["name"])
                esc_name = v["name"].replace("'", "\\'")
                if v["transcribed"]:
                    badge   = (
                        '<span style="background:#dcfce7;color:#166534;border-radius:999px;'
                        'padding:2px 9px;font-size:12px;font-weight:600">✓ Klaar</span>'
                    )
                    actions = (
                        f'<a href="/videos/transcript/{vtype}/{v["path"].stem}" '
                        f'class="btn btn-secondary">Bekijk</a>'
                    )
                else:
                    badge = (
                        '<span style="background:#f3f4f6;color:#6b7280;border-radius:999px;'
                        'padding:2px 9px;font-size:12px;font-weight:600">Wachten</span>'
                    )
                    actions = (
                        f"<button onclick=\"manualTranscribe('{vtype}','{esc_name}','{safe_id}')\" "
                        f'class="btn btn-primary">Transcribeer</button>'
                    )
                rows += (
                    f'<tr data-vtype="{vtype}" data-filename="{v["name"]}" '
                    f'data-safe-id="{safe_id}" data-transcribed="{str(v["transcribed"]).lower()}">'
                    f'<td style="font-weight:500">{v["name"]}</td>'
                    f'<td class="hide-sm">{v["size"]}</td>'
                    f'<td class="hide-sm">{v["duration"]}</td>'
                    f'<td id="status-{vtype}-{safe_id}">{badge}</td>'
                    f'<td id="actions-{vtype}-{safe_id}" style="white-space:nowrap">{actions}</td>'
                    f'</tr>'
                )
            table = (
                '<table><thead><tr>'
                '<th>Bestandsnaam</th>'
                '<th class="hide-sm">Grootte</th>'
                '<th class="hide-sm">Duur</th>'
                '<th>Status</th>'
                '<th>Acties</th>'
                f'</tr></thead><tbody>{rows}</tbody></table>'
            )
        else:
            table = f'<div class="empty">Geen video\'s in {vname} — upload hieronder.</div>'

        upload = (
            f'<div style="padding:16px 20px;background:#f9fafb;border-top:1px solid #f3f4f6">'
            f'<div id="progress-{vtype}" style="display:none;margin-bottom:12px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">'
            f'<span id="upload-label-{vtype}" style="font-size:13px;color:#374151;font-weight:500">Bezig met uploaden...</span>'
            f'<span id="pct-{vtype}" style="font-size:13px;font-weight:700;color:{color}">0%</span>'
            f'</div>'
            f'<div style="background:#e5e7eb;border-radius:6px;height:8px;overflow:hidden">'
            f'<div id="bar-{vtype}" style="width:0%;background:{color};height:8px;border-radius:6px;transition:width .15s"></div>'
            f'</div>'
            f'<div id="mb-{vtype}" style="font-size:12px;color:#9ca3af;margin-top:4px"></div>'
            f'</div>'
            f'<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">'
            f'<input type="file" id="file-{vtype}" multiple accept=".mp4,.mov,.mkv,.m4v" style="flex:1;min-width:200px">'
            f'<button onclick="doUpload(\'{vtype}\')" class="btn" style="background:{color};color:#fff">'
            f'Uploaden naar {vtype.upper()}</button>'
            f'</div>'
            f'<div id="msg-{vtype}" style="margin-top:8px;font-size:13px;color:#dc2626;display:none"></div>'
            f'</div>'
        )

        sections_html += (
            f'<div class="section">'
            f'<div class="section-head" style="border-left:4px solid {color}">'
            f'<span class="section-title">{vname}</span>{counter}'
            f'</div>'
            f'{table}'
            f'{upload}'
            f'</div>'
        )

    # Show queue status banner if queue manager is active
    warn_html = ""
    try:
        n_queued   = 0
        is_running = CURRENT_FILE.exists()
        if QUEUE_FILE.exists():
            with open(QUEUE_FILE) as _qf:
                _q = json.load(_qf)
            n_queued = len(_q) if isinstance(_q, list) else 0
        if is_running or n_queued:
            _cur_name = ""
            if is_running:
                try:
                    with open(CURRENT_FILE) as _cf:
                        _cur = json.load(_cf)
                    _cur_name = _cur.get("file", "")
                except Exception:
                    pass
            _msg = (
                f'<b>Transcriptie actief</b>: {_cur_name}'
                if _cur_name else "<b>Transcriptie actief</b>"
            )
            if n_queued:
                _msg += f' — {n_queued} video{"\'s" if n_queued != 1 else ""} in wachtrij'
            warn_html = (
                f'<div style="background:#dbeafe;border:1px solid #93c5fd;border-radius:8px;'
                f'padding:12px 16px;margin-bottom:16px;font-size:14px;color:#1e40af">'
                f'⏳ {_msg}</div>'
            )
    except Exception:
        pass

    body = (
        f'<div class="wrap">'
        f'<h1 style="font-size:22px;font-weight:700;margin-bottom:20px">Video\'s</h1>'
        f'{warn_html}'
        f'{sections_html}'
        f'</div>'
        + _VIDEO_SCRIPT
    )
    return _page_shell("Video's", "/videos", body)


# ── POST /videos/upload ───────────────────────────────────────────────────────

@app.post("/videos/upload")
async def videos_upload(
    file: UploadFile = File(...),
    video_type: str  = Form(...),
):
    if video_type not in VIDEO_TYPES:
        return JSONResponse({"status": "error", "message": "Ongeldig videotype"}, status_code=400)

    dest_dir = VIDEOS_DIR / video_type
    dest_dir.mkdir(parents=True, exist_ok=True)

    # sanitise filename
    safe_name = re.sub(r"[^\w.\-]", "_", Path(file.filename).name)
    dest = dest_dir / safe_name

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"status": "ok", "filename": safe_name, "video_type": video_type}


# ── POST /videos/transcribe ───────────────────────────────────────────────────

@app.post("/videos/transcribe")
async def videos_transcribe(
    background_tasks: BackgroundTasks,
    video_type: str = Form(...),
    filename:   str = Form(...),
):
    if video_type not in VIDEO_TYPES:
        return {"status": "error", "message": "Ongeldig videotype"}

    video_path = VIDEOS_DIR / video_type / filename
    if not video_path.exists():
        return {"status": "error", "message": f"Bestand niet gevonden: {filename}"}

    background_tasks.add_task(_run_transcription, str(video_path), video_type)
    return {"status": "started", "filename": filename, "video_type": video_type}


# ── GET /videos/transcript/{video_type}/{stem} ────────────────────────────────

@app.get("/videos/transcript/{video_type}/{stem}", response_class=HTMLResponse)
async def videos_transcript(video_type: str, stem: str):
    if video_type not in VIDEO_TYPES:
        return HTMLResponse("Ongeldig videotype", status_code=404)

    transcript_path = TRANS_DIR / f"{stem}.json"
    if not transcript_path.exists():
        body = (
            f'<div class="wrap">'
            f'<a href="/videos" class="btn btn-secondary" '
            f'style="margin-bottom:16px;display:inline-block">← Terug</a>'
            f'<p style="color:#6b7280">Transcript niet gevonden voor <b>{stem}</b>.</p>'
            f'</div>'
        )
        return _page_shell("Transcript", "/videos", body)

    with open(transcript_path) as f:
        data = json.load(f)

    segments  = data.get("segments", [])
    full_text = data.get("text", "")
    language  = data.get("language", "?")
    n_words   = len(full_text.split())
    duration  = _ts(segments[-1]["end"]) if segments else "?"
    vname     = VIDEO_TYPES[video_type]
    color     = VIDEO_TYPE_COLORS[video_type]

    seg_rows = ""
    for seg in segments:
        ts   = _ts(seg["start"])
        text = seg["text"].strip()
        seg_rows += (
            f'<div style="display:flex;gap:16px;padding:8px 0;'
            f'border-bottom:1px solid #f3f4f6">'
            f'<span style="font-variant-numeric:tabular-nums;color:#9ca3af;'
            f'font-size:13px;white-space:nowrap;padding-top:1px;min-width:52px">{ts}</span>'
            f'<span style="font-size:15px;line-height:1.5;color:#111827">{text}</span>'
            f'</div>'
        )

    body = f"""
<div class="wrap">
  <a href="/videos" class="btn btn-secondary" style="margin-bottom:20px;display:inline-block">← Terug naar Video's</a>
  <div style="background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.08);overflow:hidden">
    <div style="padding:20px 24px;border-left:4px solid {color};border-bottom:1px solid #f3f4f6">
      <div style="font-size:18px;font-weight:700;margin-bottom:4px">{stem}</div>
      <div style="color:#6b7280;font-size:14px">{vname}</div>
    </div>
    <div style="padding:14px 24px;background:#f9fafb;border-bottom:1px solid #f3f4f6;
                display:flex;gap:24px;flex-wrap:wrap">
      <span style="font-size:13px;color:#374151"><b>Duur:</b> {duration}</span>
      <span style="font-size:13px;color:#374151"><b>Woorden:</b> {n_words:,}</span>
      <span style="font-size:13px;color:#374151"><b>Taal:</b> {language}</span>
      <span style="font-size:13px;color:#374151"><b>Segmenten:</b> {len(segments)}</span>
    </div>
    <div style="padding:20px 24px;max-height:70vh;overflow-y:auto">
      {seg_rows if seg_rows else '<p style="color:#9ca3af">Geen segmenten gevonden.</p>'}
    </div>
  </div>
</div>"""

    return _page_shell(f"Transcript — {stem}", "/videos", body)


# ── GET /logs/{logname} ───────────────────────────────────────────────────────

@app.get("/logs/{logname}")
async def get_log(logname: str):
    if logname not in _LOG_MAP:
        return JSONResponse({"error": f"Unknown log: {logname}. Valid: {list(_LOG_MAP)}"}, status_code=404)

    kind, target = _LOG_MAP[logname]
    lines: list[str] = []

    try:
        if kind == "journal":
            r = subprocess.run(
                ["journalctl", "-u", target, "-n", "200", "--no-pager", "--output=short"],
                capture_output=True, text=True, timeout=10,
            )
            lines = r.stdout.splitlines()
        else:
            p = Path(target)
            if p.exists():
                lines = p.read_text(errors="replace").splitlines()
            else:
                lines = [f"[{target} bestaat nog niet]"]
    except Exception as exc:
        lines = [f"[Fout bij lezen log: {exc}]"]

    lines = lines[-200:]
    last_updated = None
    try:
        p = Path(target) if kind == "file" else None
        if p and p.exists():
            last_updated = datetime.fromtimestamp(p.stat().st_mtime).isoformat()
        else:
            last_updated = datetime.now().isoformat()
    except Exception:
        last_updated = datetime.now().isoformat()

    return {
        "log":          logname,
        "lines":        lines,
        "total_lines":  len(lines),
        "last_updated": last_updated,
    }


# ── GET /status/snapshot ──────────────────────────────────────────────────────

@app.get("/status/snapshot")
async def status_snapshot():
    # Services
    def _svc_active(name: str) -> str:
        try:
            r = subprocess.run(["systemctl", "is-active", name],
                               capture_output=True, text=True, timeout=5)
            return r.stdout.strip()
        except Exception:
            return "unknown"

    qdrant_info    = _qdrant_info()
    qdrant_status  = "healthy" if qdrant_info.get("online") else "unreachable"
    ollama_status  = "healthy" if _ollama_info().get("online") else "unreachable"

    # Transcription state
    current_file = ""
    try:
        if CURRENT_FILE.exists():
            current_file = json.loads(CURRENT_FILE.read_text()).get("file", "")
    except Exception:
        pass

    queued_count = 0
    try:
        if QUEUE_FILE.exists():
            q = json.loads(QUEUE_FILE.read_text())
            queued_count = len(q) if isinstance(q, list) else 0
    except Exception:
        pass

    done_count = sum(1 for _ in TRANS_DIR.glob("*.json")) if TRANS_DIR.exists() else 0
    total_qat  = sum(1 for f in (VIDEOS_DIR / "qat").iterdir()
                     if f.suffix.lower() in {".mp4", ".mov", ".mkv", ".m4v"}
                     ) if (VIDEOS_DIR / "qat").exists() else 0

    # System
    mem = psutil.virtual_memory()
    dsk = psutil.disk_usage("/")
    cpu = psutil.cpu_percent(interval=0.3)

    # Last test run — parse TEST_REPORT.md
    passed = failed = 0
    test_ts = None
    try:
        report = BASE / "SYSTEM_DOCS" / "TEST_REPORT.md"
        if report.exists():
            txt = report.read_text()
            import re as _re
            m = _re.search(r"(\d+)/(\d+)\s+geslaagd", txt)
            if m:
                passed = int(m.group(1))
            m2 = _re.search(r"(\d+)\s+mislukt", txt)
            if m2:
                failed = int(m2.group(1))
            m3 = _re.search(r"\*\*Gegenereerd:\*\*\s+(.+)", txt)
            if m3:
                test_ts = m3.group(1).strip()
    except Exception:
        pass

    # Books stats
    total_books = ingested_books = queued_books = 0
    quality_scores: list[float] = []
    try:
        for subdir in SECTION_MAP:
            d = BOOKS_DIR / subdir
            if d.exists():
                total_books += sum(1 for f in d.iterdir() if f.suffix.lower() in BOOK_EXTS)
        if BOOK_QUEUE_FILE.exists():
            bq = json.loads(BOOK_QUEUE_FILE.read_text())
            queued_books = len(bq) if isinstance(bq, list) else 0
        if QUALITY_DIR.exists():
            for af in QUALITY_DIR.glob("*_audit.json"):
                try:
                    a = json.loads(af.read_text())
                    if a.get("status") == "approved":
                        ingested_books += 1
                    qs = a.get("llm_audit", {}) or {}
                    s = qs.get("quality_score")
                    if s is not None:
                        quality_scores.append(float(s))
                except Exception:
                    pass
    except Exception:
        pass

    return {
        "timestamp": datetime.now().isoformat(),
        "services": {
            "web":                 _svc_active("medical-rag-web"),
            "transcription_queue": _svc_active("transcription-queue"),
            "book_ingest_queue":   _svc_active("book-ingest-queue"),
            "qdrant":              qdrant_status,
            "ollama":              ollama_status,
        },
        "books": {
            "total":            total_books,
            "ingested":         ingested_books,
            "queued":           queued_books,
            "avg_quality_score": round(sum(quality_scores)/len(quality_scores), 2)
                                  if quality_scores else None,
        },
        "qdrant_collections": {
            col["name"]: col.get("vectors", 0)
            for col in qdrant_info.get("collections", [])
            if col["name"] in ("medical_library", "video_transcripts")
        },
        "transcription": {
            "current": current_file,
            "queued":  queued_count,
            "done":    done_count,
            "total":   total_qat,
        },
        "system": {
            "ram_used_gb":  round(mem.used / 1e9, 2),
            "ram_total_gb": round(mem.total / 1e9, 2),
            "cpu_percent":  round(cpu, 1),
            "disk_used_gb": round(dsk.used / 1e9, 1),
        },
        "last_test_run": {
            "passed":    passed,
            "failed":    failed,
            "timestamp": test_ts,
        },
    }


# ── GET /status/markers ───────────────────────────────────────────────────────

@app.get("/status/markers")
async def status_markers():
    try:
        if MARKERS_FILE.exists():
            return json.loads(MARKERS_FILE.read_text())
    except Exception:
        pass
    return []


# ── GET /terminal ─────────────────────────────────────────────────────────────

@app.get("/terminal", response_class=HTMLResponse)
async def terminal_page():
    body = r"""
<div class="wrap">
  <h1 style="font-size:22px;font-weight:700;margin-bottom:20px">Terminal &amp; Logs</h1>

  <!-- ttyd iframe -->
  <div class="section" style="margin-bottom:24px">
    <div class="section-head">
      <span class="section-title">Shell</span>
      <span style="font-size:13px;color:#6b7280">Live terminal — volledig root-toegang</span>
    </div>
    <div style="padding:0">
      <iframe id="ttyd-frame" src="" style="width:100%;height:600px;border:none;border-radius:0 0 12px 12px;display:block"></iframe>
    </div>
  </div>

  <!-- Log viewer -->
  <div class="section" style="margin-bottom:24px">
    <div class="section-head">
      <span class="section-title">Logbestanden</span>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button onclick="fetchLog('transcription_queue')" class="btn btn-purple">Transcriptie</button>
        <button onclick="fetchLog('system')"              class="btn btn-secondary">Systeem</button>
        <button onclick="fetchLog('web')"                 class="btn btn-primary">Web</button>
        <button onclick="fetchLog('tests')"               class="btn btn-green">Tests</button>
      </div>
    </div>
    <div id="log-meta" style="padding:10px 20px;font-size:13px;color:#6b7280;display:none"></div>
    <pre id="log-output" style="margin:0;padding:16px 20px;background:#0f172a;color:#e2e8f0;
         font-size:12px;line-height:1.6;overflow-x:auto;max-height:500px;overflow-y:auto;
         border-radius:0 0 12px 12px;white-space:pre-wrap;word-break:break-word;display:none"></pre>
  </div>

  <!-- Status snapshot -->
  <div class="section">
    <div class="section-head">
      <span class="section-title">Status Snapshot</span>
      <div style="display:flex;gap:8px">
        <button onclick="fetchSnapshot()" class="btn btn-primary">Snapshot ophalen</button>
        <button onclick="fetchMarkers()"  class="btn btn-secondary">Markers</button>
      </div>
    </div>
    <pre id="snapshot-output" style="margin:0;padding:16px 20px;background:#0f172a;color:#e2e8f0;
         font-size:12px;line-height:1.6;overflow-x:auto;border-radius:0 0 12px 12px;
         white-space:pre-wrap;word-break:break-word;display:none"></pre>
  </div>
</div>

<script>
// Point iframe at ttyd using the same hostname the browser used
(function() {
  const host = window.location.hostname;
  document.getElementById('ttyd-frame').src = 'http://' + host + ':7682/terminal/shell';
})();

function fetchLog(name) {
  const out  = document.getElementById('log-output');
  const meta = document.getElementById('log-meta');
  out.style.display = 'none';
  meta.style.display = 'none';
  out.textContent = 'Laden...';
  fetch('/logs/' + name)
    .then(r => r.json())
    .then(d => {
      if (d.error) { out.textContent = d.error; out.style.display = 'block'; return; }
      const last50 = d.lines.slice(-50);
      out.textContent = last50.join('\n');
      meta.textContent = d.log + ' — ' + d.total_lines + ' regels  •  bijgewerkt: ' + (d.last_updated || '?');
      out.style.display = 'block';
      meta.style.display = 'block';
      out.scrollTop = out.scrollHeight;
    })
    .catch(e => { out.textContent = 'Fout: ' + e; out.style.display = 'block'; });
}

function fetchSnapshot() {
  const out = document.getElementById('snapshot-output');
  out.textContent = 'Laden...';
  out.style.display = 'block';
  fetch('/status/snapshot')
    .then(r => r.json())
    .then(d => { out.textContent = JSON.stringify(d, null, 2); })
    .catch(e => { out.textContent = 'Fout: ' + e; });
}

function fetchMarkers() {
  const out = document.getElementById('snapshot-output');
  out.textContent = 'Laden...';
  out.style.display = 'block';
  fetch('/status/markers')
    .then(r => r.json())
    .then(d => { out.textContent = JSON.stringify(d, null, 2); })
    .catch(e => { out.textContent = 'Fout: ' + e; });
}
</script>"""

    return _page_shell("Terminal", "/terminal", body)


# ═══════════════════════════════════════════════════════════════════════════════
# LIBRARY — helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _book_status(filename: str) -> dict:
    """Return status dict for one book file."""
    stem = Path(filename).stem
    # Running?
    try:
        if BOOK_CURRENT_FILE.exists():
            cur = json.loads(BOOK_CURRENT_FILE.read_text())
            if cur.get("filename") == filename:
                return {"status": "running", "label": "Ingesteren…", "color": "#2563eb"}
    except Exception:
        pass
    # Queued?
    try:
        if BOOK_QUEUE_FILE.exists():
            q = json.loads(BOOK_QUEUE_FILE.read_text())
            if any(item.get("filename") == filename for item in q):
                return {"status": "queued", "label": "In wachtrij", "color": "#d97706"}
    except Exception:
        pass
    # Done?
    audit_path = QUALITY_DIR / f"{stem}_audit.json"
    if audit_path.exists():
        try:
            a = json.loads(audit_path.read_text())
            qs = (a.get("llm_audit") or {}).get("quality_score")
            if a.get("status") == "approved":
                score_str = f" (score {qs:.1f})" if qs else ""
                return {"status": "done", "label": f"Klaar{score_str}", "color": "#059669",
                        "quality_score": qs, "total_chunks": a.get("total_chunks", 0)}
            else:
                return {"status": "low_quality", "label": f"Lage kwaliteit ({qs:.1f})",
                        "color": "#dc2626", "quality_score": qs}
        except Exception:
            pass
    return {"status": "waiting", "label": "Wachten", "color": "#6b7280"}


def _enqueue_book(filename: str, filepath: str, collection: str, category: str, fmt: str) -> None:
    entry = {
        "filename":        filename,
        "filepath":        filepath,
        "collection":      collection,
        "source_category": category,
        "format":          fmt,
        "requested":       datetime.now().isoformat(),
    }
    try:
        q = json.loads(BOOK_QUEUE_FILE.read_text()) if BOOK_QUEUE_FILE.exists() else []
        if not isinstance(q, list):
            q = []
    except Exception:
        q = []
    existing = {i.get("filename") for i in q}
    if filename not in existing:
        q.append(entry)
        BOOK_QUEUE_FILE.write_text(json.dumps(q, indent=2))


def _usability_dots(scores: dict, tags: list[str]) -> str:
    """Render ●●●●○ dot indicators for key usability dimensions."""
    icons = []
    key_map = [
        ("acupuncture_point_indication", "Protocol"),
        ("tcm_diagnosis", "Diagnose"),
        ("anatomy", "Anatomie"),
        ("treatment_protocol", "Protocol"),
        ("literature_reference", "Literatuur"),
    ]
    shown = set()
    for key, label in key_map:
        if key in shown:
            continue
        score = scores.get(key, 0)
        filled = round(score)
        dots = "●" * filled + "○" * (5 - filled)
        color = "#059669" if filled >= 4 else ("#d97706" if filled >= 2 else "#9ca3af")
        icons.append(
            f'<span style="font-size:11px;color:{color};white-space:nowrap">'
            f'{label} {dots}</span>'
        )
        shown.add(key)
    return '<span style="display:flex;gap:8px;flex-wrap:wrap">' + "".join(icons) + "</span>"


def _library_section_html(section_key: str) -> str:
    sec   = SECTION_MAP[section_key]
    label = sec["label"]
    color = sec["color"]
    collection = sec["collection"]
    description = sec["description"]
    books_dir = BOOKS_DIR / section_key

    books = []
    if books_dir.exists():
        for f in sorted(books_dir.iterdir()):
            if f.suffix.lower() in BOOK_EXTS:
                st = _book_status(f.name)
                usability_scores: dict = {}
                audit_path = QUALITY_DIR / f"{f.stem}_audit.json"
                if audit_path.exists():
                    try:
                        a = json.loads(audit_path.read_text())
                        up = a.get("usability_profile") or {}
                        usability_scores = up.get("scores", {})
                    except Exception:
                        pass
                books.append({"name": f.name, "size": _fmt_bytes(f.stat().st_size),
                               "usability_scores": usability_scores, **st})

    rows = ""
    if books:
        for b in books:
            badge_bg = b["color"] + "22"
            dots_html = _usability_dots(b["usability_scores"], []) if b["status"] == "done" else ""
            rows += f"""
<tr>
  <td>
    <span style="font-weight:600">{b['name']}</span>
    {f'<div style="margin-top:4px">{dots_html}</div>' if dots_html else ''}
  </td>
  <td class="hide-sm">{b.get('size','')}</td>
  <td><span style="background:{badge_bg};color:{b['color']};padding:3px 10px;
      border-radius:999px;font-size:12px;font-weight:600">{b['label']}</span></td>
  <td>{b.get('total_chunks','') or ''}</td>
  <td style="white-space:nowrap">
    <a href="/library/audit/{b['name']}" class="btn btn-secondary" style="font-size:12px"
       {'onclick="return false;this.style.opacity=.4" ' if b['status'] == 'waiting' else ''}>Rapport</a>
    <a href="/images?book={b['name']}" class="btn btn-secondary" style="font-size:12px;margin-left:4px">Afb.</a>
  </td>
</tr>"""
    else:
        rows = '<tr><td colspan="5" style="color:#9ca3af;font-size:14px">Geen bestanden</td></tr>'

    return f"""
<div class="section" style="border-top:3px solid {color}">
  <div class="section-head">
    <span class="section-title">{label}</span>
    <span style="font-size:12px;color:#6b7280;font-family:monospace">→ {collection}</span>
  </div>
  <table>
    <thead><tr>
      <th>Bestand</th><th class="hide-sm">Grootte</th>
      <th>Status</th><th>Chunks</th><th></th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div style="padding:16px 20px;border-top:1px solid #f3f4f6">
    <p style="font-size:13px;color:#6b7280;margin-bottom:10px">{description}</p>
    <form id="form-{section_key}" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
      <input type="file" name="file" accept=".pdf,.epub" multiple
             style="flex:1;min-width:200px" required>
      <button type="button" onclick="uploadBook('{section_key}')"
              class="btn btn-primary">Uploaden + ingesteren</button>
      <span id="upload-msg-{section_key}" style="font-size:13px;color:#059669"></span>
    </form>
  </div>
</div>"""


# ── GET /library ───────────────────────────────────────────────────────────────

@app.get("/library", response_class=HTMLResponse)
async def library_page():
    sections = "".join(_library_section_html(sec) for sec in SECTION_MAP)

    # Queue stats
    queued_count = 0
    current_book = ""
    try:
        if BOOK_QUEUE_FILE.exists():
            q = json.loads(BOOK_QUEUE_FILE.read_text())
            queued_count = len(q) if isinstance(q, list) else 0
    except Exception:
        pass
    try:
        if BOOK_CURRENT_FILE.exists():
            current_book = json.loads(BOOK_CURRENT_FILE.read_text()).get("filename", "")
    except Exception:
        pass

    status_bar = ""
    if current_book:
        status_bar = f'<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:12px 16px;margin-bottom:20px;font-size:14px">🔄 <strong>Bezig:</strong> {current_book} — {queued_count} in wachtrij</div>'
    elif queued_count:
        status_bar = f'<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:12px 16px;margin-bottom:20px;font-size:14px">⏳ {queued_count} boek(en) in wachtrij — start <code>book-ingest-queue.service</code></div>'

    body = f"""
<div class="wrap">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px">
    <h1 style="font-size:22px;font-weight:700">Bibliotheek</h1>
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <a href="/library/overview" class="btn btn-secondary">Literatuuroverzicht</a>
      <span style="font-size:13px;color:#6b7280">→ alle boeken in <code>medical_library</code></span>
    </div>
  </div>
  {status_bar}
  {sections}
</div>
<script>
async function uploadBook(category) {{
  const form      = document.getElementById('form-' + category);
  const msg       = document.getElementById('upload-msg-' + category);
  const fileInput = form.querySelector('input[type=file]');
  if (!fileInput.files.length) {{ msg.textContent = 'Selecteer een bestand.'; return; }}
  const files = Array.from(fileInput.files);
  const queued = [];
  const failed = [];
  msg.style.color = '#6b7280';
  for (let i = 0; i < files.length; i++) {{
    msg.textContent = `Uploaden ${{i + 1}}/${{files.length}}: ${{files[i].name}}…`;
    const fd = new FormData();
    fd.append('file',       files[i]);
    fd.append('collection', category);
    try {{
      const r = await fetch('/library/upload', {{ method: 'POST', body: fd }});
      const d = await r.json();
      if (d.status === 'queued') queued.push(d.filename);
      else failed.push(files[i].name + ': ' + (d.error || 'fout'));
    }} catch(e) {{
      failed.push(files[i].name + ': ' + e);
    }}
  }}
  if (failed.length) {{
    msg.style.color = '#dc2626';
    msg.textContent = 'Fouten: ' + failed.join(', ');
  }} else {{
    msg.style.color = '#059669';
    msg.textContent = `✓ ${{queued.length}} bestand(en) in wachtrij`;
    setTimeout(() => location.reload(), 1500);
  }}
}}
</script>"""
    return _page_shell("Bibliotheek", "/library", body)


# ── GET /library/status/{filename} ────────────────────────────────────────────

@app.get("/library/status/{filename}")
async def library_status(filename: str):
    return _book_status(filename)


# ── POST /library/upload ───────────────────────────────────────────────────────

@app.post("/library/upload")
async def library_upload(
    file:       UploadFile = File(...),
    collection: str        = Form(...),   # section key (medical_literature/nrt_qat/device)
):
    section_key = collection
    if section_key not in SECTION_MAP:
        return JSONResponse({"error": f"Unknown section: {section_key}"}, status_code=400)

    sec  = SECTION_MAP[section_key]
    qdrant_collection = sec["collection"]
    source_category   = sec["category"]

    fname = file.filename or "upload"
    ext   = Path(fname).suffix.lower()
    if ext not in BOOK_EXTS:
        return JSONResponse({"error": "Only .pdf and .epub allowed"}, status_code=400)

    dest_dir = BOOKS_DIR / section_key
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / fname

    content = await file.read()
    dest.write_bytes(content)

    _enqueue_book(fname, str(dest), qdrant_collection, source_category, ext.lstrip("."))

    return {"status": "queued", "filename": fname, "collection": qdrant_collection, "section": section_key}


# ── GET /library/audit/{filename} ─────────────────────────────────────────────

@app.get("/library/audit/{filename}")
async def library_audit(filename: str):
    stem = Path(filename).stem
    audit_path = QUALITY_DIR / f"{stem}_audit.json"
    if not audit_path.exists():
        return JSONResponse({"error": "No audit report found"}, status_code=404)
    return json.loads(audit_path.read_text())


# ── GET /library/overview ──────────────────────────────────────────────────────

@app.get("/library/overview", response_class=HTMLResponse)
async def library_overview():
    # Load usability tag definitions
    tag_defs: dict = {}
    try:
        if USABILITY_TAGS_FILE.exists():
            tag_defs = json.loads(USABILITY_TAGS_FILE.read_text()).get("tags", {})
    except Exception:
        pass

    # Build table rows from audit reports
    rows = ""
    all_books = []
    for sec_key, sec in SECTION_MAP.items():
        d = BOOKS_DIR / sec_key
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if f.suffix.lower() not in BOOK_EXTS:
                continue
            all_books.append((sec_key, f))

    for sec_key, f in all_books:
        sec_label = SECTION_MAP[sec_key]["label"]
        audit_path = QUALITY_DIR / f"{f.stem}_audit.json"
        chunks_n = imgs_approved = imgs_pending = imgs_total = 0
        qs = score_html = dots_html = ""
        if audit_path.exists():
            try:
                a = json.loads(audit_path.read_text())
                chunks_n = a.get("total_chunks", 0)
                qs_val = (a.get("llm_audit") or {}).get("quality_score")
                qs = f"{qs_val:.1f}" if qs_val else "—"
                up = (a.get("usability_profile") or {}).get("scores", {})
                dots_html = _usability_dots(up, []) if up else ""
            except Exception:
                pass
        try:
            if IMAGE_APPROVALS_FILE.exists():
                appr = json.loads(IMAGE_APPROVALS_FILE.read_text())
                for e in appr.get("approved", []):
                    if isinstance(e, dict) and e.get("book") == f.name:
                        imgs_approved += 1
                for e in appr.get("pending", []):
                    if isinstance(e, dict) and e.get("book") == f.name:
                        imgs_pending += 1
                imgs_total = imgs_approved + imgs_pending
        except Exception:
            pass
        rows += f"""
<tr>
  <td><span style="font-weight:600">{f.name}</span><br>
      <span style="font-size:12px;color:#6b7280">{sec_label}</span></td>
  <td style="text-align:right">{chunks_n or '—'}</td>
  <td style="text-align:right">{imgs_approved}/{imgs_total}</td>
  <td>{dots_html}</td>
  <td style="text-align:center">{qs}</td>
  <td style="white-space:nowrap">
    <a href="/library/audit/{f.name}" class="btn btn-secondary" style="font-size:12px">Rapport</a>
    <button onclick="retag('{f.name}')" class="btn btn-secondary" style="font-size:12px;margin-left:4px">Heranalyseer</button>
  </td>
</tr>"""

    # Tag definitions editor
    tag_rows = ""
    for tag_name, tag_info in tag_defs.items():
        tag_rows += f"""
<tr>
  <td><code style="font-size:13px">{tag_name}</code></td>
  <td><span style="font-size:13px">{tag_info.get('description','')}</span></td>
  <td><span style="font-size:12px;color:#6b7280">{tag_info.get('protocol_use','')}</span></td>
</tr>"""

    body = f"""
<div class="wrap">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px">
    <h1 style="font-size:22px;font-weight:700">Literatuuroverzicht</h1>
    <a href="/library" class="btn btn-secondary">← Bibliotheek</a>
  </div>

  <div class="section" style="margin-bottom:24px">
    <div class="section-head"><span class="section-title">Ingested boeken</span></div>
    <table>
      <thead><tr>
        <th>Bestand</th><th style="text-align:right">Chunks</th>
        <th style="text-align:right">Afb. (goedgekeurd/totaal)</th>
        <th>Bruikbaarheid</th>
        <th style="text-align:center">Score</th><th></th>
      </tr></thead>
      <tbody>{''.join([rows]) if rows else '<tr><td colspan="6" style="color:#9ca3af">Geen boeken</td></tr>'}</tbody>
    </table>
  </div>

  <div class="section">
    <div class="section-head">
      <span class="section-title">Bruikbaarheidsdefinities</span>
      <span style="font-size:12px;color:#6b7280">{USABILITY_TAGS_FILE}</span>
    </div>
    <table>
      <thead><tr><th>Tag</th><th>Beschrijving</th><th>Gebruik in protocol</th></tr></thead>
      <tbody>{tag_rows or '<tr><td colspan="3" style="color:#9ca3af">Geen tags</td></tr>'}</tbody>
    </table>
  </div>
</div>
<script>
function retag(filename) {{
  if (!confirm('Heranalyseer AI-tags voor ' + filename + '?')) return;
  fetch('/library/retag/' + encodeURIComponent(filename), {{method:'POST'}})
    .then(r => r.json())
    .then(d => alert(d.status || JSON.stringify(d)))
    .catch(e => alert('Fout: ' + e));
}}
</script>"""
    return _page_shell("Literatuuroverzicht", "/library", body)


# ── POST /library/retag/{filename} ────────────────────────────────────────────

@app.post("/library/retag/{filename}")
async def library_retag(filename: str, background_tasks: BackgroundTasks):
    """Re-runs AI usability tagging for all chunks of this book."""
    stem = Path(filename).stem
    audit_path = QUALITY_DIR / f"{stem}_audit.json"
    if not audit_path.exists():
        return JSONResponse({"error": "No audit report found — ingest first"}, status_code=404)

    def _do_retag():
        import sys as _sys
        _sys.path.insert(0, str(BASE / "scripts"))
        try:
            from audit_book import tag_chunks_with_ollama, build_usability_profile
            from qdrant_client import QdrantClient
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            client = QdrantClient(host="localhost", port=6333, timeout=60)
            # Scroll all chunks from this book
            results, _ = client.scroll(
                collection_name="medical_library",
                scroll_filter=Filter(must=[
                    FieldCondition(key="source_file", match=MatchValue(value=filename))
                ]),
                limit=5000, with_payload=True, with_vector=False,
            )
            chunks = [p.payload for p in results if p.payload]
            if not chunks:
                return
            tag_chunks_with_ollama(chunks)
            profile = build_usability_profile(chunks)
            # Update audit report
            a = json.loads(audit_path.read_text())
            a["usability_profile"] = profile
            a["retagged_at"] = datetime.now().isoformat()
            audit_path.write_text(json.dumps(a, indent=2))
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("Retag failed: %s", e)

    background_tasks.add_task(_do_retag)
    return {"status": "started", "filename": filename}


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGES — approval system
# ═══════════════════════════════════════════════════════════════════════════════

def _load_approvals() -> dict:
    try:
        if IMAGE_APPROVALS_FILE.exists():
            d = json.loads(IMAGE_APPROVALS_FILE.read_text())
            if isinstance(d, dict):
                return d
    except Exception:
        pass
    return {"approved": [], "rejected": [], "pending": []}


def _save_approvals(data: dict) -> None:
    IMAGE_APPROVALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    IMAGE_APPROVALS_FILE.write_text(json.dumps(data, indent=2))


# ── GET /images ────────────────────────────────────────────────────────────────

@app.get("/images", response_class=HTMLResponse)
async def images_page(book: str = "", filter: str = "all"):
    approvals = _load_approvals()
    all_entries: list[dict] = []
    for status_key in ("pending", "approved", "rejected"):
        for e in approvals.get(status_key, []):
            if isinstance(e, dict):
                all_entries.append({**e, "_status": status_key})

    # Filter
    if filter != "all":
        all_entries = [e for e in all_entries if e["_status"] == filter]
    if book:
        all_entries = [e for e in all_entries if e.get("book") == book]

    # Group by book
    by_book: dict[str, list[dict]] = {}
    for e in all_entries:
        by_book.setdefault(e.get("book", "unknown"), []).append(e)

    def _status_badge(s: str) -> str:
        cfg = {
            "pending":  ("#fef3c7", "#b45309", "Wachten"),
            "approved": ("#dcfce7", "#166534", "Goedgekeurd"),
            "rejected": ("#fee2e2", "#991b1b", "Afgewezen"),
        }.get(s, ("#f3f4f6", "#374151", s))
        return (f'<span style="background:{cfg[0]};color:{cfg[1]};padding:2px 8px;'
                f'border-radius:999px;font-size:11px;font-weight:600">{cfg[2]}</span>')

    def _confidence_bar(c) -> str:
        if c is None:
            return ""
        pct = int(float(c) * 100)
        color = "#059669" if pct >= 70 else ("#d97706" if pct >= 40 else "#dc2626")
        return (f'<div style="display:flex;align-items:center;gap:6px;font-size:11px">'
                f'<div style="background:#e5e7eb;border-radius:4px;height:6px;width:60px;overflow:hidden">'
                f'<div style="background:{color};height:6px;width:{pct}%"></div></div>'
                f'{pct}%</div>')

    sections = ""
    for bname, entries in sorted(by_book.items()):
        cards = ""
        for e in entries:
            path = e.get("path", "")
            img_src = f"/{path}" if path else ""
            ai_sug = e.get("ai_suggestion")
            ai_label = ("✓ Nuttig" if ai_sug else "✗ Niet nuttig") if ai_sug is not None else "—"
            ai_color = "#059669" if ai_sug else ("#dc2626" if ai_sug is False else "#6b7280")
            s = e.get("_status", "pending")
            cards += f"""
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:12px;
            width:200px;flex-shrink:0">
  <div style="height:120px;background:#f9fafb;border-radius:4px;overflow:hidden;
              display:flex;align-items:center;justify-content:center;margin-bottom:8px">
    <img src="{img_src}" style="max-width:100%;max-height:100%;object-fit:contain"
         onerror="this.style.display='none';this.nextSibling.style.display='block'">
    <span style="display:none;color:#9ca3af;font-size:12px">Afbeelding niet gevonden</span>
  </div>
  <div style="font-size:11px;color:#6b7280;overflow:hidden;text-overflow:ellipsis;
              white-space:nowrap;margin-bottom:4px" title="{path}">{Path(path).name}</div>
  <div style="margin-bottom:4px">{_status_badge(s)}</div>
  <div style="font-size:11px;color:{ai_color};margin-bottom:4px">AI: {ai_label}</div>
  {_confidence_bar(e.get('ai_confidence'))}
  <div style="font-size:11px;color:#6b7280;margin-top:4px;overflow:hidden;
              display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical">
    {e.get('surrounding_text','')[:80]}</div>
  <div style="display:flex;gap:4px;margin-top:8px">
    <button onclick="approve('{path}',true)" class="btn btn-green"
            style="font-size:11px;padding:3px 8px;flex:1"
            {'disabled style="opacity:.4"' if s=='approved' else ''}>✓</button>
    <button onclick="approve('{path}',false)" class="btn btn-secondary"
            style="font-size:11px;padding:3px 8px;flex:1;background:#fee2e2;color:#991b1b"
            {'disabled style="opacity:.4"' if s=='rejected' else ''}>✗</button>
  </div>
</div>"""

        n = len(entries)
        sections += f"""
<div class="section" style="margin-bottom:20px">
  <div class="section-head">
    <span class="section-title">{bname}</span>
    <span style="font-size:13px;color:#6b7280">{n} afbeelding(en)</span>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:12px;padding:16px 20px">{cards}</div>
</div>"""

    total_pending  = len([e for e in all_entries if e["_status"] == "pending"])
    total_approved = len([e for e in all_entries if e["_status"] == "approved"])
    total_rejected = len([e for e in all_entries if e["_status"] == "rejected"])

    filter_links = ""
    for fkey, flabel in [("all","Alle"),("pending","Wachten"),("approved","Goedgekeurd"),("rejected","Afgewezen")]:
        active = "background:#2563eb;color:#fff;" if filter == fkey else ""
        filter_links += f'<a href="/images?filter={fkey}" class="btn btn-secondary" style="font-size:13px;{active}">{flabel}</a>'

    body = f"""
<div class="wrap">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:10px">
    <h1 style="font-size:22px;font-weight:700">Afbeeldingen</h1>
    <div style="font-size:13px;color:#6b7280">
      Wachten: {total_pending} &nbsp;|&nbsp; Goedgekeurd: {total_approved} &nbsp;|&nbsp; Afgewezen: {total_rejected}
    </div>
  </div>
  <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap">{filter_links}</div>
  {sections if sections else '<div style="color:#9ca3af;padding:24px">Geen afbeeldingen gevonden.</div>'}
</div>
<script>
function approve(path, approved) {{
  fetch('/images/approve', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{path: path, approved: approved}})
  }})
  .then(r => r.json())
  .then(d => {{ if (d.status === 'ok') location.reload(); else alert(JSON.stringify(d)); }})
  .catch(e => alert('Fout: ' + e));
}}
</script>"""
    return _page_shell("Afbeeldingen", "/images", body)


# ── POST /images/approve ───────────────────────────────────────────────────────

@app.post("/images/approve")
async def images_approve(request_data: dict):
    path     = request_data.get("path", "")
    approved = request_data.get("approved")
    if not path:
        return JSONResponse({"error": "path required"}, status_code=400)

    data = _load_approvals()
    target_status = "approved" if approved else "rejected"

    # Find and move the entry
    moved = False
    for src_key in ("pending", "approved", "rejected"):
        for i, e in enumerate(data.get(src_key, [])):
            if isinstance(e, dict) and e.get("path") == path:
                entry = data[src_key].pop(i)
                entry["approved"]    = approved
                entry["approved_at"] = datetime.now().isoformat()
                data[target_status].append(entry)
                moved = True
                break
        if moved:
            break

    if not moved:
        return JSONResponse({"error": "Image not found"}, status_code=404)

    _save_approvals(data)
    return {"status": "ok", "path": path, "approved": approved}


# ── GET /images/approve ────────────────────────────────────────────────────────

@app.get("/images/approved")
async def images_approved_list():
    data = _load_approvals()
    return [e.get("path") for e in data.get("approved", []) if isinstance(e, dict)]
