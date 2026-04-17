from fastapi import FastAPI, BackgroundTasks, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
import asyncio, httpx, psutil, subprocess, json, os, re, shutil, sys, threading, time
from pathlib import Path
from datetime import datetime, timezone

# ── rag_query module (lazy, imported at first use) ────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

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
CACHE_DIR          = BASE / "data" / "ingest_cache"
TRANS_STATS_FILE   = BASE / "data" / "transcription_stats.json"

SECTION_MAP = {
    "medical_literature": {
        "label":       "Medische Literatuur",
        "color":       "#1A6B72",
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
IMAGES_DIR           = BASE / "data" / "extracted_images"
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
    "nrt":  "#1A6B72",
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

def _progress_bar(pct: float, color: str = "#1A6B72") -> str:
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

def _card(title: str, body: str, accent: str = "#1A6B72") -> str:
    return (
        f'<div style="background:#fff;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.08);'
        f'border:1px solid #e2e8f0;padding:20px;border-top:3px solid {accent}">'
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
    ("/",                "Dashboard"),
    ("/library",         "Bibliotheek"),
    ("/library/ingest",  "Importeer"),
    ("/images",          "Afbeeldingen"),
    ("/protocols",       "Protocollen"),
    ("/search",          "Zoeken"),
    ("/videos",          "Video's"),
    ("/terminal",        "Terminal"),
    ("/settings",        "Instellingen"),
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
  th{{text-align:left;font-size:12px;font-weight:700;background:#1A6B72;color:#fff;text-transform:uppercase;letter-spacing:.05em;padding:8px 12px}}
  td{{padding:10px 12px;border-bottom:1px solid #e2e8f0;font-size:14px;vertical-align:middle}}
  tr:hover td{{background:#f8fafc}}
  .btn{{display:inline-block;padding:6px 14px;border-radius:7px;font-size:13px;font-weight:600;text-decoration:none;border:none;cursor:pointer;white-space:nowrap}}
  .btn-primary{{background:#1A6B72;color:#fff}}
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
<div style="background:linear-gradient(135deg,#1e3a5f 0%,#1A6B72 100%);padding:16px 24px">
  <div style="max-width:1100px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
    <div>
      <div style="color:#fff;font-size:20px;font-weight:700;letter-spacing:-.02em">⚕ Medical RAG</div>
      <div style="color:#e8f4f5;font-size:13px">NRT-Amsterdam.nl</div>
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

    # ── protocol review notifications ──
    try:
        from protocol_metadata import get_all_protocol_status as _proto_status
        _proto_list    = _proto_status()
        n_proto_review = sum(1 for p in _proto_list if p.get("needs_review"))
    except Exception:
        n_proto_review = 0

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
    nav_links = "".join(
        f'<a href="{href}" style="color:#e0e7ff;text-decoration:none;padding:6px 14px;'
        f'border-radius:6px;font-size:14px;font-weight:500;'
        f'{"background:rgba(255,255,255,.15)" if href=="/" else ""}">{label}</a>'
        for href, label in NAV_ITEMS
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
<div style="background:linear-gradient(135deg,#1e3a5f 0%,#1A6B72 100%);padding:16px 24px">
  <div style="max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
    <div>
      <div style="color:#fff;font-size:20px;font-weight:700;letter-spacing:-.02em">⚕ Medical RAG</div>
      <div style="color:#e8f4f5;font-size:13px">NRT-Amsterdam.nl</div>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap">{nav_links}</div>
  </div>
</div>

<!-- timestamp + refresh -->
<div style="max-width:1200px;margin:0 auto;padding:12px 24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
  <span style="color:#6b7280;font-size:13px">Bijgewerkt: {now}</span>
  <span id="countdown" style="color:#9ca3af;font-size:13px">Vernieuwt over 30s</span>
</div>

{"" if not n_proto_review else f'''<!-- protocol review banner -->
<div style="max-width:1200px;margin:0 auto;padding:0 24px 10px">
  <a href="/protocols?tab=protocollen" style="display:flex;align-items:center;gap:10px;
     background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:12px 18px;
     text-decoration:none;color:#c2410c">
    <span style="font-size:18px">&#x1F514;</span>
    <span style="font-size:14px;font-weight:600">{n_proto_review} protocol(len) mogelijk verouderd door nieuwe literatuur</span>
    <span style="font-size:13px;margin-left:auto">Bekijk &rarr;</span>
  </a>
</div>'''}

<!-- grid -->
<div class="grid" style="max-width:1200px;margin:0 auto">
  {_card("Systeembronnen", sys_body, "#8b5cf6")}
  {_card("Qdrant — Vector Store", q_body, "#1A6B72")}
  {_card("Ollama — LLM", o_body, "#10b981")}
  {_card("Docker containers", d_body, "#f59e0b")}
  {_card("RAG statistieken", rag_body, "#ec4899")}
  {_card("Opslagruimte", dir_body, "#14b8a6")}
</div>

<!-- quick search + actions -->
<div style="max-width:1200px;margin:0 auto;padding:0 20px 24px">
  <div style="background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.08);padding:20px;margin-bottom:16px">
    <div style="font-size:13px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px">Snel zoeken</div>
    <form onsubmit="event.preventDefault();window.location='/search?q='+encodeURIComponent(document.getElementById('dash-q').value)" style="display:flex;gap:8px">
      <input id="dash-q" type="text" placeholder="Zoeken in medische literatuur, video's..." style="flex:1;padding:9px 14px;border:1px solid #d1d5db;border-radius:8px;font-size:14px">
      <button type="submit" style="background:#1A6B72;color:#fff;border:none;border-radius:8px;padding:9px 18px;font-size:14px;font-weight:600;cursor:pointer">Zoeken</button>
    </form>
  </div>
  <div style="background:#fff;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.08);padding:20px">
    <div style="font-size:13px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;margin-bottom:14px">Snelle acties</div>
    <div style="display:flex;gap:10px;flex-wrap:wrap">
      <a href="/library" style="background:#1A6B72;color:#fff;text-decoration:none;padding:9px 18px;border-radius:8px;font-size:14px;font-weight:600">+ Boek uploaden</a>
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
.vspin{display:inline-block;width:11px;height:11px;border:2px solid #e8f4f5;
       border-top-color:#1A6B72;border-radius:50%;
       animation:_vspin .8s linear infinite;vertical-align:middle;margin-right:5px}
</style>
<script>
const _timers = {};
function _clearTimer(k) { if (_timers[k]) { clearInterval(_timers[k]); delete _timers[k]; } }

function escHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

function showFileList(vtype) {
  const inp = document.getElementById('file-' + vtype);
  const listDiv = document.getElementById('filelist-' + vtype);
  if (!listDiv) return;
  if (!inp.files.length) { listDiv.innerHTML = ''; return; }
  const files = Array.from(inp.files);
  let html = '<div style="font-size:13px;color:#4a5568;margin-bottom:6px;font-weight:500">'
    + files.length + (files.length === 1 ? ' bestand' : ' bestanden') + ' geselecteerd:</div>'
    + '<div style="display:flex;flex-direction:column;gap:4px">';
  files.forEach((f, i) => {
    const size = f.size >= 1e6 ? (f.size/1e6).toFixed(1)+'\u00a0MB' : (f.size/1e3).toFixed(0)+'\u00a0KB';
    html += '<div id="filelist-item-' + vtype + '-' + i + '" '
      + 'style="display:flex;align-items:center;gap:8px;padding:6px 10px;background:#f8fafc;'
      + 'border-radius:6px;border:1px solid #e2e8f0">'
      + '<span style="flex:1;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'
      + escHtml(f.name) + '</span>'
      + '<span style="font-size:12px;color:#6b7280;white-space:nowrap">' + size + '</span>'
      + '<span id="filelist-status-' + vtype + '-' + i + '" style="font-size:13px;white-space:nowrap;min-width:20px;text-align:right"></span>'
      + '</div>';
  });
  html += '</div>';
  listDiv.innerHTML = html;
}

function setRunning(vtype, safeId) {
  document.getElementById('status-' + vtype + '-' + safeId).innerHTML =
    '<span style="background:#e8f4f5;color:#1A6B72;border-radius:999px;padding:2px 9px;font-size:12px;font-weight:600">' +
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
    const statusEl = document.getElementById('filelist-status-' + vtype + '-' + i);
    if (statusEl) statusEl.innerHTML = '<span style="color:#1A6B72">&#9203;</span>';
    const d = await _uploadFile(vtype, files[i], i + 1, files.length);
    if (d) {
      uploaded.push(d.filename);
      if (statusEl) statusEl.innerHTML = '<span style="color:#16a34a;font-weight:700">&#10003;</span>';
    } else {
      if (statusEl) statusEl.innerHTML = '<span style="color:#dc2626;font-weight:700">&#10007;</span>';
      document.getElementById('msg-' + vtype).textContent = 'Upload mislukt: ' + files[i].name;
      document.getElementById('msg-' + vtype).style.display = 'block';
    }
    if (files.length > 1) {
      const mbEl = document.getElementById('mb-' + vtype);
      if (mbEl) mbEl.textContent = (i + 1) + ' / ' + files.length + ' bestanden ge\u00fcpload';
    }
  }
  if (!uploaded.length) { document.getElementById('progress-' + vtype).style.display = 'none'; return; }
  document.getElementById('pct-' + vtype).textContent = '\u2713';
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


_VIDEO_PROGRESS_SCRIPT = r"""<script>
async function _toggleVideoPause() {
  const btn = document.getElementById('video-pause-btn');
  if (!btn) return;
  const paused = btn.dataset.paused === 'true';
  const url = paused ? '/videos/resume' : '/videos/pause';
  try {
    await fetch(url, {method: 'POST'});
    btn.dataset.paused = paused ? 'false' : 'true';
    btn.textContent = paused ? '⏸ Pauzeer' : '▶ Hervat';
    btn.style.background = paused ? '#dc2626' : '#059669';
  } catch(e) {}
  _refreshVideoProgress();
}
async function _refreshVideoProgress() {
  try {
    const [pr, ps, ts] = await Promise.all([
      fetch('/videos/progress').then(r => r.json()),
      fetch('/videos/paused').then(r => r.json()),
      fetch('/api/transcription/stats').then(r => r.ok ? r.json() : null).catch(() => null),
    ]);
    const d = pr;
    const el = document.getElementById('video-progress');
    if (!el) return;
    if (!d.current && d.queue_count === 0 && !ps.paused) { el.innerHTML = ''; return; }
    const isPaused = ps.paused;

    // ── Helpers (same as book widget) ─────────────────────────────────────
    const fmt = n => (n == null || n === '' ? '?' : Number(n).toLocaleString('nl-NL'));
    const parseTs = s => s ? new Date(s) : null;
    const fmtTime = dt => dt
      ? dt.toLocaleTimeString('nl-NL', {hour:'2-digit', minute:'2-digit'})
      : '\u2014';
    const fmtDateTime = dt => dt
      ? dt.toLocaleDateString('nl-NL', {day:'2-digit', month:'2-digit'}).replace('/', '-') + ' ' + fmtTime(dt)
      : '\u2014';
    const elapsed = (start, end) => {
      if (!start) return '\u2014';
      const ms  = (end || new Date()) - start;
      const tot = Math.floor(ms / 60000);
      const h   = Math.floor(tot / 60);
      const m   = String(tot % 60).padStart(2, '0');
      return `${h}:${m}`;
    };

    // ── Outer card ────────────────────────────────────────────────────────
    let html = '<div style="background:#e8f4f5;border:1px solid #1A6B72;border-radius:10px;padding:16px 20px">';
    html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">';
    html += '<span style="font-weight:700;font-size:15px;color:#1A6B72">\uD83C\uDFAC Video transcriptie wachtrij</span>';
    html += '<div style="display:flex;gap:8px;align-items:center">';
    if (isPaused) html += '<span style="background:#fef3c7;color:#92400e;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:600">\u23F8 Gepauzeerd</span>';
    html += `<button id="video-pause-btn" onclick="_toggleVideoPause()" data-paused="${isPaused}" style="font-size:12px;padding:4px 12px;border-radius:6px;border:none;cursor:pointer;color:#fff;background:${isPaused ? '#059669' : '#dc2626'}">${isPaused ? '\u25B6 Hervat' : '\u23F8 Pauzeer'}</button>`;
    html += '<span style="font-size:12px;color:#6b7280">\u21BB 10s</span>';
    html += '</div></div>';

    if (d.current) {
      // Filename + category + size line
      const cur  = d.current;
      const vtype = cur.video_type || '';
      const sizeMb = ts && ts.current_file_size_mb ? `${ts.current_file_size_mb}\u00a0MB` : '';
      const catLabel = vtype ? vtype.toUpperCase() : '';
      const metaParts = [cur.file, catLabel, sizeMb].filter(Boolean);
      html += `<div style="font-size:13px;margin-bottom:10px;color:#374151">${metaParts.join(' \u00b7 ')}</div>`;

      // Summary bar
      const bookStart = parseTs(cur.started || (ts && ts.current_started_at));
      const sumParts  = [
        `Start ${fmtDateTime(bookStart)}`,
        `Eind \u2014`,
        `Verstreken ${elapsed(bookStart, null)}`,
      ];
      html += `<div style="background:#ddf2f3;border-radius:6px;padding:3px 10px;font-size:12px;font-family:monospace;color:#085041;margin-bottom:10px">${sumParts.join('  \u00b7  ')}</div>`;

      // ── Phase table ───────────────────────────────────────────────────
      const thBase = 'text-align:left;padding:5px 6px 7px;font-weight:500;font-size:12px;border-bottom:1.5px solid #1A6B72;white-space:nowrap;background:#ddf2f3;color:#085041';
      const thS  = `style="${thBase}"`;
      const thSF = `style="${thBase};padding-left:0"`;
      const tdS  = 'style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0"';
      const tdSF = 'style="padding:7px 0;vertical-align:top;border-bottom:1px solid #e2e8f0"';

      html += '<div style="overflow-x:auto;margin-bottom:8px">';
      html += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:13px">';
      html += '<colgroup><col style="width:32%"><col style="width:14%"><col style="width:18%"><col style="width:18%"><col style="width:18%"></colgroup>';
      html += `<thead><tr><th ${thSF}>Fase</th><th ${thS}>Status</th><th ${thS}>Start</th><th ${thS}>Eind</th><th ${thS}>Totaal</th></tr></thead>`;
      html += '<tbody>';

      // ── Row 1: Whisper transcriptie ──────────────────────────────────
      const whisperStart = parseTs(cur.started || (ts && ts.current_started_at));
      const mr = ts && ts.model_rate;
      const sizeMb2 = ts && ts.current_file_size_mb;
      let whisperDetail = '';
      let whisperBar = '';

      if (mr && sizeMb2) {
        const estSec     = mr.seconds_per_mb * sizeMb2;
        const elapsedSec = whisperStart ? (new Date() - whisperStart) / 1000 : 0;
        const pct        = Math.min(Math.round(elapsedSec / estSec * 100), 95);
        const etaSec     = Math.max(estSec - elapsedSec, 0);
        const etaMin     = Math.round(etaSec / 60);
        const nSamples   = mr.n_samples || 0;
        whisperDetail = etaMin > 1
          ? `ETA ~${etaMin} min \u00b7 schatting op basis van ${nSamples} video${nSamples === 1 ? '' : "'s"}`
          : `afronden\u2026 \u00b7 schatting op basis van ${nSamples} video${nSamples === 1 ? '' : "'s"}`;
        whisperBar = `<div style="margin-top:4px;background:#c7e8eb;border-radius:999px;height:4px"><div style="background:#1A6B72;border-radius:999px;height:4px;width:${pct}%;transition:width 0.8s"></div></div>`;
      } else {
        whisperDetail = 'geen schatting beschikbaar (eerste video)';
      }

      html += `<tr style="background:#f0faf8">`;
      html += `<td ${tdSF}><div style="display:flex;align-items:flex-start;gap:6px">`;
      html += `<span style="margin-top:2px;width:16px;height:16px;border-radius:50%;background:#1A6B72;color:#fff;font-size:9px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0">\u25B6</span>`;
      html += `<div><span style="font-size:13px;color:#1A6B72;font-weight:600">1. Whisper transcriptie</span>`;
      html += `<div style="font-size:12px;color:#6b7280;margin-top:1px">${whisperDetail}</div>`;
      html += whisperBar;
      html += `</div></div></td>`;
      html += `<td ${tdS}><span style="background:#e8f4f5;color:#1A6B72;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:600">Bezig</span></td>`;
      html += `<td ${tdS} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#4a5568">${fmtTime(whisperStart)}</td>`;
      html += `<td ${tdS} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#1A6B72">bezig</td>`;
      html += `<td ${tdS} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#4a5568;font-variant-numeric:tabular-nums">${elapsed(whisperStart, null)}</td>`;
      html += '</tr>';

      // ── Row 2: Qdrant ingest (pending for active video) ──────────────
      html += '<tr>';
      html += `<td ${tdSF}><div style="display:flex;align-items:center;gap:6px">`;
      html += `<span style="width:16px;height:16px;border-radius:50%;background:#d1d5db;color:#fff;font-size:9px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0">\u2022</span>`;
      html += `<span style="font-size:13px;color:#374151">2. Qdrant ingest</span>`;
      html += `</div></td>`;
      html += `<td ${tdS}><span style="background:#f3f4f6;color:#6b7280;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:600">Wacht</span></td>`;
      html += `<td ${tdS} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#4a5568">\u2014</td>`;
      html += `<td ${tdS} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#4a5568">\u2014</td>`;
      html += `<td ${tdS} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#4a5568">\u2014</td>`;
      html += '</tr>';

      html += '</tbody></table></div>';
    }

    // ── Queue stats row ────────────────────────────────────────────────────
    const nDone = d.done_count || 0;
    const nActive = d.current ? 1 : 0;
    const nWait = d.queue_count || 0;
    html += `<div style="font-size:12px;color:#374151;margin-bottom:8px">`;
    html += `<span style="background:#dcfce7;color:#16a34a;border-radius:999px;padding:1px 8px;font-size:11px;font-weight:600;margin-right:4px">Klaar ${nDone}</span>`;
    html += `<span style="background:#e8f4f5;color:#1A6B72;border-radius:999px;padding:1px 8px;font-size:11px;font-weight:600;margin-right:4px">Bezig ${nActive}</span>`;
    html += `<span style="background:#f3f4f6;color:#6b7280;border-radius:999px;padding:1px 8px;font-size:11px;font-weight:600;margin-right:4px">Wachtrij ${nWait}</span>`;
    html += `<span style="background:#f3f4f6;color:#374151;border-radius:999px;padding:1px 8px;font-size:11px;font-weight:600">Totaal ${nDone + nActive + nWait}</span>`;
    html += '</div>';

    // ── Queue grouped by category ──────────────────────────────────────────
    if (nWait > 0) {
      const items = d.queue_items || d.queue.map(f => ({filename: f, video_type: ''}));
      const byType = {};
      items.forEach(it => {
        const t = (it.video_type || 'overig').toUpperCase();
        (byType[t] = byType[t] || []).push(it.filename);
      });
      const MAX_SHOW = 3;
      Object.entries(byType).forEach(([cat, files]) => {
        const shown = files.slice(0, MAX_SHOW);
        const rest  = files.length - MAX_SHOW;
        html += `<div style="font-size:12px;color:#374151;margin-bottom:3px">`;
        html += `<span style="background:#e8f4f5;color:#1A6B72;border-radius:4px;padding:1px 6px;font-size:11px;font-weight:600;margin-right:6px">${cat}</span>`;
        html += shown.join(', ');
        if (rest > 0) html += ` <span style="color:#9ca3af">+${rest} meer</span>`;
        html += '</div>';
      });
    }

    // ── Tempo indicator ────────────────────────────────────────────────────
    const mr2 = ts && ts.model_rate;
    if (mr2 && mr2.n_samples > 0) {
      const rate = mr2.seconds_per_mb.toLocaleString('nl-NL', {minimumFractionDigits:1, maximumFractionDigits:1});
      html += `<div style="font-size:11px;color:#6b7280;margin-top:8px;text-align:right">Leersnelheid: ${rate}\u00a0sec/MB \u00b7 ${mr2.n_samples} meting${mr2.n_samples === 1 ? '' : 'en'}</div>`;
    }

    html += '</div>';
    el.innerHTML = html;
  } catch(e) {}
}
_refreshVideoProgress();
setInterval(_refreshVideoProgress, 10000);
</script>"""

_BOOK_PROGRESS_SCRIPT = r"""<script>
async function _toggleBookPause() {
  const btn = document.getElementById('book-pause-btn');
  if (!btn) return;
  const paused = btn.dataset.paused === 'true';
  const url = paused ? '/library/resume' : '/library/pause';
  try {
    await fetch(url, {method: 'POST'});
    btn.dataset.paused = paused ? 'false' : 'true';
    btn.textContent = paused ? '▶ Hervat' : '⏸ Pauzeer';
    btn.style.background = paused ? '#dc2626' : '#059669';
  } catch(e) {}
  _refreshBookProgress();
}
async function _refreshBookProgress() {
  try {
    const [pr, ps, active] = await Promise.all([
      fetch('/library/progress').then(r => r.json()),
      fetch('/library/paused').then(r => r.json()),
      fetch('/api/library/progress/active').then(r => r.ok ? r.json() : null).catch(() => null),
    ]);
    const d = pr;
    const el = document.getElementById('book-progress');
    if (!el) return;
    if (!d.current && d.queue_count === 0 && !ps.paused) { el.innerHTML = ''; return; }
    const isPaused = ps.paused;

    // ── Helpers ───────────────────────────────────────────────────────────
    const fmt = n => (n == null || n === '' ? '?' : Number(n).toLocaleString('nl-NL'));
    const parseTs = s => s ? new Date(s) : null;
    const fmtTime = d => d
      ? d.toLocaleTimeString('nl-NL', {hour:'2-digit', minute:'2-digit'})
      : '\u2014';
    const fmtDateTime = d => d
      ? d.toLocaleDateString('nl-NL', {day:'2-digit', month:'2-digit'})
          .replace('/', '-') + ' ' + fmtTime(d)
      : '\u2014';
    const elapsed = (start, end) => {
      if (!start) return '\u2014';
      const ms  = (end || new Date()) - start;
      const tot = Math.floor(ms / 60000);
      const h   = Math.floor(tot / 60);
      const m   = String(tot % 60).padStart(2, '0');
      return `${h}:${m}`;
    };

    // ── Outer card ────────────────────────────────────────────────────────
    let html = '<div style="background:#e8f4f5;border:1px solid #1A6B72;border-radius:10px;padding:16px 20px">';

    // Header row: title + pause button
    html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">';
    html += '<span style="font-weight:700;font-size:15px;color:#1A6B72">\uD83D\uDCDA Boek ingest voortgang</span>';
    html += '<div style="display:flex;gap:8px;align-items:center">';
    if (isPaused) html += '<span style="background:#fef3c7;color:#92400e;border-radius:999px;padding:2px 10px;font-size:12px;font-weight:600">\u23F8 Gepauzeerd</span>';
    html += `<button id="book-pause-btn" onclick="_toggleBookPause()" data-paused="${isPaused}" style="font-size:12px;padding:4px 12px;border-radius:6px;border:none;cursor:pointer;color:#fff;background:${isPaused ? '#059669' : '#dc2626'}">${isPaused ? '\u25B6 Hervat' : '\u23F8 Pauzeer'}</button>`;
    html += '<span style="font-size:12px;color:#6b7280">\u21BB 10s</span>';
    html += '</div></div>';

    if (d.current) {
      // Book filename line
      html += `<div style="font-size:14px;margin-bottom:10px"><strong>Bezig:</strong> ${d.current.filename}</div>`;

      if (active && active.phases) {
        // ── Phase table ───────────────────────────────────────────────────
        const phaseOrder  = ['parse','audit','embed','qdrant'];
        const phaseNames  = {parse:'Parsing', audit:'Audit & Tagging', embed:'Embedding', qdrant:'Qdrant upload'};
        const circleColor = {done:'#059669', running:'#1A6B72', failed:'#dc2626', pending:'#d1d5db'};
        const circleIcon  = {done:'\u2713', running:'\u25B6', failed:'\u2717', pending:'\u2022'};

        html += '<div style="overflow-x:auto;margin-bottom:8px">';
        html += '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:13px">';
        html += '<colgroup><col style="width:32%"><col style="width:14%"><col style="width:18%"><col style="width:18%"><col style="width:18%"></colgroup>';
        // Header
        const thBase = 'text-align:left;padding:5px 6px 7px;font-weight:500;font-size:12px;border-bottom:1.5px solid #1A6B72;white-space:nowrap;background:#ddf2f3;color:#085041';
        const thS  = `style="${thBase}"`;
        const thSF = `style="${thBase};padding-left:0"`;
        html += `<thead><tr><th ${thSF}>Fase</th><th ${thS}>Status</th><th ${thS}>Start</th><th ${thS}>Eind</th><th ${thS}>Totaal</th></tr></thead>`;
        html += '<tbody>';

        for (let pi = 0; pi < phaseOrder.length; pi++) {
          const ph      = phaseOrder[pi];
          const info    = active.phases[ph] || {};
          const st      = info.status || 'pending';
          const ccol    = circleColor[st] || '#d1d5db';
          const icon    = circleIcon[st]  || '\u2022';
          const isRunning = st === 'running';
          const isDone    = st === 'done';

          // ── Detail text (Fase cell) ─────────────────────────────────────
          let detail = '';
          if (ph === 'parse') {
            const engineBadge = info.ocr_engine === 'google_vision'
              ? ' \u00b7 <span style="color:#92400e;font-size:11px">Google Vision API</span>'
              : (info.ocr_engine && info.ocr_engine !== 'native'
                  ? ` \u00b7 <span style="color:#6b7280;font-size:11px">${info.ocr_engine}</span>`
                  : '');
            if (isRunning) {
              if (!info.pages_total) {
                detail = 'Voorbereiden\u2026 OCR model laden';
              } else if (info.pages_done > 0) {
                detail = `pagina ${fmt(info.pages_done)} / ${fmt(info.pages_total)}` + engineBadge;
              } else {
                detail = `opstarten\u2026 / ${fmt(info.pages_total)} pagina\u2019s`;
              }
            } else if (isDone) {
              detail = `${fmt(info.pages_total)} pagina\u2019s`;
              if (info.chunks_extracted) detail += ` \u00b7 ${fmt(info.chunks_extracted)} chunks`;
              detail += engineBadge;
            }
          } else if (ph === 'audit') {
            const processed = (info.chunks_tagged || 0) + (info.chunks_skipped || 0);
            if (isRunning && info.chunks_total) {
              detail = `chunk ${fmt(processed)} / ${fmt(info.chunks_total)}`;
            } else if (isDone && info.chunks_total) {
              detail = `${fmt(info.chunks_total)} chunks`;
              if (info.chunks_tagged)  detail += ` \u00b7 ${fmt(info.chunks_tagged)} getagd`;
              if (info.chunks_skipped) detail += ` \u00b7 ${fmt(info.chunks_skipped)} overgeslagen`;
            }
            if (info.ollama_available === false || info.consecutive_failures_hit) {
              detail += (detail ? ' \u2014 ' : '') + '<span style="color:#b45309;font-size:11px">Ollama timeout</span>';
            } else if ((isDone || isRunning) && info.ollama_available === true) {
              detail += (detail ? ' \u2014 ' : '') + '<span style="color:#059669;font-size:11px">Ollama \u2713</span>';
            }
          } else if (ph === 'embed') {
            const done_e  = info.chunks_done  || 0;
            const total_e = info.chunks_total;
            if (isRunning && total_e) {
              detail = `chunk ${fmt(done_e)} / ${fmt(total_e)}`;
              if (info.vectors_per_minute) detail += ` \u00b7 ${fmt(Math.round(info.vectors_per_minute))}/min`;
              if (info.eta_minutes != null && info.eta_minutes > 1) detail += ` \u00b7 ETA ${Math.round(info.eta_minutes)} min`;
            } else if (isDone) {
              const v = info.chunks_done || info.chunks_total;
              if (v) detail = `${fmt(v)} vectors`;
            }
          } else if (ph === 'qdrant') {
            const ins     = info.chunks_inserted || 0;
            const coll    = info.collection || active.collection || '';
            const total_q = (active.phases.embed || {}).chunks_total
                          || (active.phases.parse || {}).chunks_extracted;
            if (isRunning) {
              detail = total_q ? `${fmt(ins)} / ${fmt(total_q)} vectors` : `${fmt(ins)} vectors`;
            } else if (isDone) {
              detail = `${fmt(ins)} vectors`;
              if (coll) detail += ` \u2192 ${coll}`;
            }
          }

          // ── Progress bar (parse + embed only, while running) ────────────
          let bar = '';
          if (ph === 'parse' && isRunning && info.pages_total) {
            const pct = Math.min(Math.round((info.pages_done||0) / info.pages_total * 100), 100);
            bar = `<div style="margin-top:4px;background:#c7e8eb;border-radius:999px;height:4px"><div style="background:#1A6B72;border-radius:999px;height:4px;width:${pct}%;transition:width 0.5s"></div></div>`;
          } else if (ph === 'embed' && isRunning && info.chunks_total) {
            const pct = Math.min(Math.round((info.chunks_done||0) / info.chunks_total * 100), 100);
            bar = `<div style="margin-top:4px;background:#c7e8eb;border-radius:999px;height:4px"><div style="background:#1A6B72;border-radius:999px;height:4px;width:${pct}%;transition:width 0.8s"></div></div>`;
          }

          // ── Status pill ─────────────────────────────────────────────────
          const pillStyles = {
            done:    'background:#dcfce7;color:#16a34a',
            running: 'background:#e8f4f5;color:#1A6B72',
            failed:  'background:#fee2e2;color:#dc2626',
            pending: 'background:#f3f4f6;color:#6b7280',
          };
          const pillLabels = {done:'Klaar', running:'Bezig', failed:'Fout', pending:'Wacht'};
          const pStyle = pillStyles[st] || pillStyles.pending;
          const pLabel = pillLabels[st] || 'Wacht';
          const pill = `<span style="${pStyle};border-radius:999px;padding:2px 8px;font-size:11px;font-weight:600;white-space:nowrap">${pLabel}</span>`;

          // ── Time cells ──────────────────────────────────────────────────
          const phStart  = parseTs(info.started_at);
          const phEnd    = parseTs(info.completed_at);
          const startTxt = fmtTime(phStart);
          const eindTxt  = isDone ? fmtTime(phEnd) : (isRunning ? 'bezig' : '\u2014');
          const totalTxt = (isDone || isRunning) ? elapsed(phStart, phEnd) : '\u2014';

          // ── Row ─────────────────────────────────────────────────────────
          const tdS  = 'style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0"';
          const tdSF = 'style="padding:7px 0;vertical-align:top;border-bottom:1px solid #e2e8f0"';
          const rowBg = isRunning ? ' style="background:#f0faf8"' : '';
          html += `<tr${rowBg}>`;

          // Fase cell
          html += `<td ${tdSF}>`;
          html += '<div style="display:flex;align-items:flex-start;gap:6px">';
          html += `<span style="margin-top:2px;width:16px;height:16px;border-radius:50%;background:${ccol};color:#fff;font-size:9px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0">${icon}</span>`;
          html += '<div>';
          html += `<span style="font-size:13px;color:${isRunning?'#1A6B72':'#374151'};font-weight:${isRunning?600:400}">${pi+1}. ${phaseNames[ph]}</span>`;
          if (detail) html += `<div style="font-size:12px;color:#6b7280;margin-top:1px">${detail}</div>`;
          if (bar)    html += bar;
          html += '</div></div></td>';

          // Status, Start, Eind, Totaal cells
          html += `<td ${tdS}>${pill}</td>`;
          html += `<td ${tdS} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#4a5568">${startTxt}</td>`;
          html += `<td ${tdS} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:${isRunning?'#1A6B72':'#4a5568'}">${eindTxt}</td>`;
          html += `<td ${tdS} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#4a5568;font-variant-numeric:tabular-nums">${totalTxt}</td>`;
          html += '</tr>';
        }

        // ── 5th row: Image extraction ────────────────────────────────────
        const ie2    = active.image_extraction || {};
        const ieSt2  = ie2.status || 'pending';
        if (ieSt2 !== 'not_applicable') {
          const ieRunning2 = ieSt2 === 'running';
          const ieDone2    = ieSt2 === 'done';
          let   ieccol2    = ieDone2 ? '#059669' : (ieRunning2 ? '#1A6B72' : '#d1d5db');
          let   ieicon2    = ieDone2 ? '\u2713'  : (ieRunning2 ? '\u25B6'  : '\u2022');
          let   ieDetail2  = '';
          let   ieBar2     = '';
          if (ieRunning2) {
            const pp = ie2.pages_processed, pt = ie2.pages_total, ff = ie2.figures_found;
            if (pp != null && pt != null) {
              ieDetail2 = `pagina ${fmt(pp)} / ${fmt(pt)}`;
              if (ff) ieDetail2 += ` \u00b7 ${fmt(ff)} figuren`;
              const pct2 = Math.min(Math.round(pp / pt * 100), 100);
              ieBar2 = `<div style="margin-top:4px;background:#c7e8eb;border-radius:999px;height:4px">`
                + `<div style="background:#1A6B72;border-radius:999px;height:4px;width:${pct2}%;transition:width 0.8s"></div></div>`;
            }
          }
          const iePillStyles2 = {done:'background:#dcfce7;color:#16a34a',running:'background:#e8f4f5;color:#1A6B72',failed:'background:#fee2e2;color:#dc2626',pending:'background:#f3f4f6;color:#6b7280'};
          const iePillLabels2 = {done:'Klaar',running:'Bezig',failed:'Fout',pending:'Wacht'};
          // Fix: 0 figures → "Geen" instead of "Klaar"
          if (ieDone2) {
            const nf2 = ie2.figures_found;
            if (nf2 === 0 || nf2 == null) {
              iePillStyles2.done = 'background:#f3f4f6;color:#6b7280';
              iePillLabels2.done = 'Geen';
              ieccol2 = '#d1d5db';
              ieicon2 = '\u2014';
              ieDetail2 = 'Geen figuren gevonden in document';
            }
          }
          const iePill2   = `<span style="${iePillStyles2[ieSt2]||iePillStyles2.pending};border-radius:999px;padding:2px 8px;font-size:11px;font-weight:600;white-space:nowrap">${iePillLabels2[ieSt2]||'Wacht'}</span>`;
          const tdS2  = 'style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0"';
          const tdSF2 = 'style="padding:7px 0;vertical-align:top;border-bottom:1px solid #e2e8f0"';
          const rowBg2 = ieRunning2 ? ' style="background:#f0faf8"' : '';
          html += `<tr${rowBg2}>`;
          html += `<td ${tdSF2}>`;
          html += '<div style="display:flex;align-items:flex-start;gap:6px">';
          html += `<span style="margin-top:2px;width:16px;height:16px;border-radius:50%;background:${ieccol2};color:#fff;font-size:9px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0">${ieicon2}</span>`;
          html += '<div>';
          html += `<span style="font-size:13px;color:${ieRunning2?'#1A6B72':'#374151'};font-weight:${ieRunning2?600:400}">5. Afbeeldingen</span>`;
          if (ieDetail2) html += `<div style="font-size:12px;color:#6b7280;margin-top:1px">${ieDetail2}</div>`;
          if (ieBar2)    html += ieBar2;
          html += '</div></div></td>';
          html += `<td ${tdS2}>${iePill2}</td>`;
          html += `<td ${tdS2} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#4a5568">\u2014</td>`;
          html += `<td ${tdS2} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#4a5568">\u2014</td>`;
          html += `<td ${tdS2} style="padding:7px 6px;vertical-align:top;border-bottom:1px solid #e2e8f0;font-size:12px;color:#4a5568">\u2014</td>`;
          html += '</tr>';
        }

        html += '</tbody></table></div>';

        // ── Book-level summary bar ────────────────────────────────────────
        const bookStart = parseTs(active.started_at);
        const bookEnd   = parseTs(active.completed_at);
        const sumParts  = [
          `Start ${fmtDateTime(bookStart)}`,
          `Eind ${bookEnd ? fmtDateTime(bookEnd) : '\u2014'}`,
          `Verstreken ${elapsed(bookStart, bookEnd)}`,
        ];
        html += `<div style="background:#ddf2f3;border-radius:6px;padding:3px 10px;font-size:12px;font-family:monospace;color:#085041;margin-top:4px">${sumParts.join('  \u00b7  ')}</div>`;

      } else {
        // Fallback: pre-state-machine legacy progress object
        const prog = d.current.progress;
        if (prog && prog.phase) {
          const legacyCol = {parsing:'#7c3aed',auditing:'#b45309',embedding:'#065f46'}[prog.phase] || '#374151';
          html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">';
          html += `<span style="background:${legacyCol};color:#fff;border-radius:999px;padding:2px 10px;font-size:11px;font-weight:600">${prog.phase}</span>`;
          if (prog.total_pages > 0) html += `<span style="font-size:12px;color:#6b7280">Pagina ${prog.current_page}/${prog.total_pages}</span>`;
          html += '</div>';
        }
      }
    }

    if (d.queue_count > 0) {
      html += `<div style="font-size:13px;color:#374151;margin-top:10px"><strong>${d.queue_count}</strong> boek(en) in wachtrij:</div>`;
      html += '<ul style="margin:3px 0 0 20px;font-size:12px;color:#6b7280">';
      d.queue.forEach(f => { html += `<li>${f}</li>`; });
      html += '</ul>';
    }
    html += '</div>';
    el.innerHTML = html;
  } catch(e) {}
}
_refreshBookProgress();
setInterval(_refreshBookProgress, 10000);
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
            f'<input type="file" id="file-{vtype}" multiple accept=".mp4,.mov,.mkv,.m4v" onchange="showFileList(\'{vtype}\')" style="flex:1;min-width:200px">'
            f'<button onclick="doUpload(\'{vtype}\')" class="btn" style="background:{color};color:#fff">'
            f'Uploaden naar {vtype.upper()}</button>'
            f'</div>'
            f'<div id="filelist-{vtype}" style="margin-top:10px"></div>'
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

    body = (
        f'<div class="wrap">'
        f'<h1 style="font-size:22px;font-weight:700;margin-bottom:20px">Video\'s</h1>'
        f'<div id="video-progress" style="margin-bottom:16px"></div>'
        f'{sections_html}'
        f'</div>'
        + _VIDEO_SCRIPT
        + _VIDEO_PROGRESS_SCRIPT
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
  document.getElementById('ttyd-frame').src = 'http://' + host + ':7682/terminal/shell/';
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

# ── Status system — single source of truth ────────────────────────────────────

_STATUS_PILLS_PY: dict[str, dict] = {
    "in_wachtrij":    {"label": "In wachtrij",       "bg": "#f3f4f6", "color": "#374151"},
    "bezig":          {"label": "Bezig\u2026",        "bg": "#e8f4f5", "color": "#085041"},
    "audit_lopend":   {"label": "Audit lopend",       "bg": "#fde68a", "color": "#92400e"},
    "afb_lopend":     {"label": "Afb. lopend",        "bg": "#ddf2f3", "color": "#085041"},
    "afb_bezig":      {"label": "Afb. bezig\u2026",   "bg": "#ddf2f3", "color": "#085041"},
    "klaar":          {"label": "Klaar",              "bg": "#dcfce7", "color": "#166534"},
    "fout":           {"label": "Fout",               "bg": "#fee2e2", "color": "#991b1b"},
    "permanent_fout": {"label": "Permanent fout",     "bg": "#fee2e2", "color": "#7f1d1d"},
}


def _get_book_image_source(filename: str) -> str:
    """Return image_source for a book filename from book_classifications.json."""
    try:
        cls_data = json.loads(CLASSIFICATIONS_PATH.read_text()).get("classifications", {})
        fn_lower = filename.lower()
        for entry in cls_data.values():
            for pat in entry.get("filename_patterns", []):
                if pat.lower() in fn_lower:
                    return entry.get("image_source") or "none"
    except Exception:
        pass
    return "none"


def _get_image_progress(book_hash: str) -> dict | None:
    """Read live extraction progress from /tmp file."""
    p = Path(f"/tmp/image_extraction_{book_hash}.json")
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _compute_book_status(state: dict) -> str:
    """Single source of truth for book status. Returns one of 8 status strings."""
    if state.get("status") == "permanently_failed":
        return "permanent_fout"

    phases  = state.get("phases", {})
    parse   = phases.get("parse",  {})
    audit   = phases.get("audit",  {})
    qdrant  = phases.get("qdrant", {})

    if parse.get("status") == "failed":
        return "fout"

    for ph in phases.values():
        if isinstance(ph, dict) and ph.get("status") == "running":
            return "bezig"

    if qdrant.get("status") != "done":
        return "in_wachtrij"

    skipped = audit.get("chunks_skipped", 0) or 0
    if skipped > 0:
        return "audit_lopend"

    # Explicitly disabled by user → treat as klaar
    if not state.get("image_extraction_enabled", True):
        return "klaar"

    # Check images
    book_hash    = state.get("book_hash", "")
    filename     = state.get("filename", "")
    image_source = _get_book_image_source(filename)

    if image_source in ("none", None, ""):
        return "klaar"

    if _get_image_progress(book_hash) is not None:
        return "afb_bezig"

    meta_path = BASE / "data" / "extracted_images" / book_hash / "images_metadata.json"
    if meta_path.exists():
        try:
            data = json.loads(meta_path.read_text())
            if len(data.get("images", [])) > 0:
                return "klaar"
        except Exception:
            pass
        return "afb_lopend"

    return "afb_lopend"


def _find_state_for_file(filename: str) -> dict | None:
    """Find state.json for a book file by matching filename."""
    fn_lower = filename.lower()
    if CACHE_DIR.exists():
        for sf in CACHE_DIR.glob("*/state.json"):
            try:
                s = json.loads(sf.read_text())
                sfn = (s.get("filename") or "").lower()
                if sfn == fn_lower or fn_lower in sfn or sfn in fn_lower:
                    return s
            except Exception:
                pass
    return None


def _book_status(filename: str) -> dict:
    """Return status dict for one book file, using _compute_book_status if state.json found."""
    state = _find_state_for_file(filename)
    if state:
        s = _compute_book_status(state)
        pill = _STATUS_PILLS_PY.get(s, _STATUS_PILLS_PY["in_wachtrij"])
        return {"status": s, "label": pill["label"], "bg": pill["bg"], "color": pill["color"],
                "book_hash": state.get("book_hash", "")}

    # Fallback when no state.json: check queue/current files
    try:
        if BOOK_CURRENT_FILE.exists():
            cur = json.loads(BOOK_CURRENT_FILE.read_text())
            if cur.get("filename") == filename:
                p = _STATUS_PILLS_PY["bezig"]
                return {"status": "bezig", "label": p["label"], "bg": p["bg"], "color": p["color"],
                        "book_hash": cur.get("book_hash", "")}
    except Exception:
        pass
    try:
        if BOOK_QUEUE_FILE.exists():
            q = json.loads(BOOK_QUEUE_FILE.read_text())
            if any(item.get("filename") == filename for item in q):
                p = _STATUS_PILLS_PY["in_wachtrij"]
                return {"status": "in_wachtrij", "label": p["label"], "bg": p["bg"], "color": p["color"],
                        "book_hash": ""}
    except Exception:
        pass
    p = _STATUS_PILLS_PY["in_wachtrij"]
    return {"status": "in_wachtrij", "label": p["label"], "bg": p["bg"], "color": p["color"],
            "book_hash": ""}


def _enqueue_book(filename: str, filepath: str, collection: str, category: str, fmt: str,
                  image_extraction_enabled: bool = True) -> None:
    entry = {
        "filename":                 filename,
        "filepath":                 filepath,
        "collection":               collection,
        "source_category":          category,
        "format":                   fmt,
        "requested":                datetime.now().isoformat(),
        "image_extraction_enabled": image_extraction_enabled,
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


def _book_hash_for_file(filepath: Path) -> str:
    """Lookup book_hash from ingest_cache by matching filename."""
    cache = BASE / "data" / "ingest_cache"
    if not cache.exists():
        return ""
    for sf in cache.glob("*/state.json"):
        try:
            s = json.loads(sf.read_text())
            if Path(s.get("filepath", "")).name == filepath.name:
                return s.get("book_hash", sf.parent.name)
        except Exception:
            pass
    return ""


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

    cls = _load_classifications()
    rows = ""
    if books:
        for b in books:
            badge_bg  = b.get("bg", b["color"] + "22")
            badge_fg  = b["color"]
            safe_id   = re.sub(r"[^a-zA-Z0-9]", "_", b["name"])
            is_done   = b["status"] in ("klaar", "audit_lopend", "afb_lopend", "afb_bezig")
            reaudit_btn = (
                f'<button onclick="reauditBook(\'{b["name"]}\')" '
                f'class="btn btn-secondary" style="font-size:12px;margin-left:4px">Heraudit</button>'
                f'<span id="ra-{safe_id}" style="font-size:11px;color:#6b7280;margin-left:4px"></span>'
            ) if is_done else ""
            disp_title, disp_authors, disp_file = _book_display(b["name"], cls)
            has_meta = disp_title != b["name"]
            if has_meta:
                name_cell = (
                    f'<span style="font-size:14px;font-weight:500;color:#111">{disp_title}</span>'
                    + (f'<br><span style="font-size:11px;color:#6b7280">{disp_authors}</span>' if disp_authors else "")
                    + f'<br><span style="font-size:11px;color:#9ca3af;font-family:monospace">{disp_file}</span>'
                )
            else:
                name_cell = f'<span style="font-weight:600">{b["name"]}</span>'
            # Build status cell — add extraction progress for afb_bezig
            status_cell = (f'<span style="background:{badge_bg};color:{badge_fg};padding:3px 10px;'
                           f'border-radius:999px;font-size:12px;font-weight:600">{b["label"]}</span>')
            if b["status"] == "afb_bezig":
                bh_prog = b.get("book_hash", "")
                if bh_prog:
                    prog = _get_image_progress(bh_prog)
                    if prog:
                        pp = prog.get("pages_processed", "?")
                        pt = prog.get("pages_total", "?")
                        ff = prog.get("figures_found", 0)
                        status_cell += (f'<div style="font-size:10px;color:#085041;'
                                        f'opacity:0.7;margin-top:2px">'
                                        f'{pp}/{pt} pag. &middot; {ff} fig.</div>')
            rows += f"""
<tr>
  <td>{name_cell}</td>
  <td class="hide-sm">{b.get('size','')}</td>
  <td>{status_cell}</td>
  <td>{b.get('total_chunks','') or ''}</td>
  <td style="white-space:nowrap">
    <a href="/library/audit/{b['name']}" class="btn btn-secondary" style="font-size:12px"
       {'onclick="return false;this.style.opacity=.4" ' if b['status'] == 'in_wachtrij' else ''}>Rapport</a>
    <a href="/images?book={b['name']}" class="btn btn-secondary" style="font-size:12px;margin-left:4px">Afb.</a>
    {reaudit_btn}
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
      <th>Boek</th><th class="hide-sm">Grootte</th>
      <th>Status</th><th>Chunks</th><th></th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div style="padding:16px 20px;border-top:1px solid #f3f4f6">
    <p style="font-size:13px;color:#6b7280;margin-bottom:10px">{description}</p>
    <form id="form-{section_key}" style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
      <input type="file" name="file" accept=".pdf,.epub" multiple
             style="flex:1;min-width:200px" required>
      <div style="flex-basis:100%;display:flex;align-items:center;gap:8px;margin-top:4px">
        <input type="checkbox" id="enable-images-{section_key}" name="enable_images" checked
               style="width:14px;height:14px;cursor:pointer">
        <label for="enable-images-{section_key}"
               style="font-size:13px;color:#6b7280;cursor:pointer">
          Afbeeldingen extraheren na verwerking
        </label>
      </div>
      <button type="button" onclick="uploadBook('{section_key}')"
              class="btn btn-primary">Uploaden + ingesteren</button>
      <span id="upload-msg-{section_key}" style="font-size:13px;color:#059669"></span>
    </form>
  </div>
</div>"""


# ── Catalog helpers ───────────────────────────────────────────────────────────

CLASSIFICATIONS_PATH = BASE / "config" / "book_classifications.json"


def _load_classifications() -> dict:
    """Load book_classifications.json → classifications sub-dict."""
    try:
        return json.loads(CLASSIFICATIONS_PATH.read_text()).get("classifications", {})
    except Exception:
        return {}


def _book_display(filename: str, classifications: dict) -> tuple:
    """Return (title, authors, filename) for a given filename.
    Looks up by server_filename first, then filename_patterns.
    Falls back to (filename, '', filename) if no match found.
    """
    stem = filename.lower().replace(".pdf", "").replace(".epub", "")
    for meta in classifications.values():
        if not isinstance(meta, dict):
            continue
        if meta.get("server_filename") == filename:
            return meta.get("full_title", filename), meta.get("authors", ""), filename
        for pat in meta.get("filename_patterns", []):
            if pat.lower() in stem or stem in pat.lower().replace(".pdf","").replace(".epub",""):
                return meta.get("full_title", filename), meta.get("authors", ""), filename
    return filename, "", filename


_CAT_LABELS = {
    "medical_literature": "Medische Literatuur",
    "acupuncture":        "Acupunctuur",
    "nrt_kinesiology":    "NRT/Kinesiologie",
    "qat_curriculum":     "QAT Curriculum",
    "device":             "Apparatuur",
    "videos":             "Video's",
}
_CAT_ORDER = list(_CAT_LABELS.keys())

_CAT_COLLECTION = {
    "medical_literature": "medical_library",
    "acupuncture":        "medical_library",
    "nrt_kinesiology":    "nrt_qat_curriculum",
    "qat_curriculum":     "nrt_qat_curriculum",
    "device":             "device_documentation",
    "videos":             "video_transcripts",
}

_KAI_COLORS = {1: "#16a34a", 2: "#d97706", 3: "#9ca3af"}
_KAI_LABELS = {1: "Primair", 2: "Ondersteunend", 3: "Achtergrond"}


async def _qdrant_count_source(collection: str, source_file: str) -> int:
    """Count Qdrant points where source_file == source_file in the given collection."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.post(
                f"http://localhost:6333/collections/{collection}/points/count",
                json={"filter": {"must": [{"key": "source_file", "match": {"value": source_file}}]}},
            )
            if r.status_code == 200:
                return r.json().get("result", {}).get("count", 0)
    except Exception:
        pass
    return 0


# ── GET /library ───────────────────────────────────────────────────────────────

@app.get("/library", response_class=HTMLResponse)
async def library_page():
    body = """
<style>
.book-row { transition: background 0.12s; }
.book-row:hover { background: #f0faf8 !important; }
.book-row.active-row { background: #e8f4f5 !important;
  border-radius: 10px 10px 0 0 !important; box-shadow: 0 0 0 2px #1A6B72 !important; }
</style>
<div class="wrap">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px">
    <h1 style="font-size:22px;font-weight:700">Bibliotheek — Catalogus</h1>
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <a href="/library/ingest" class="btn btn-secondary">Upload / Ingest</a>
      <a href="/library/overview" class="btn btn-secondary">Literatuuroverzicht</a>
    </div>
  </div>

  <!-- K/A/I legenda -->
  <div style="background:#f8fafc;border-radius:8px;padding:12px 16px;
       display:grid;grid-template-columns:1fr 1fr 1fr;
       gap:16px 24px;margin-bottom:16px">

    <!-- Kolom 1: K/A/I categorie + prioriteit -->
    <div>
      <div style="font-size:11px;font-weight:500;color:#6b7280;margin-bottom:8px">K / A / I \u2014 categorie</div>
      <div style="display:flex;flex-direction:column;gap:4px;font-size:11px;color:#6b7280">
        <div><b style="color:#111827">K</b>&nbsp;Klinisch \u2014 weefsel, anatomie, pathologie</div>
        <div><b style="color:#111827">A</b>&nbsp;Acupunctuur \u2014 meridianen, punten, TCM</div>
        <div><b style="color:#111827">I</b>&nbsp;Afbeeldingen \u2014 illustraties voor protocollen</div>
      </div>
      <div style="font-size:11px;font-weight:500;color:#6b7280;margin-top:10px;margin-bottom:6px">K / A / I \u2014 prioriteit</div>
      <div style="display:flex;flex-direction:column;gap:4px">
        <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#6b7280">
          <span style="background:#dcfce7;color:#166534;border-radius:3px;padding:1px 6px;font-weight:500;font-size:10px;min-width:18px;text-align:center">1</span>
          Primaire bron
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#6b7280">
          <span style="background:#ffedd5;color:#9a3412;border-radius:3px;padding:1px 6px;font-weight:500;font-size:10px;min-width:18px;text-align:center">2</span>
          Ondersteunend
        </div>
        <div style="display:flex;align-items:center;gap:6px;font-size:11px;color:#6b7280">
          <span style="background:#f3f4f6;color:#374151;border-radius:3px;padding:1px 6px;font-weight:500;font-size:10px;min-width:18px;text-align:center">3</span>
          Achtergrond
        </div>
      </div>
    </div>

    <!-- Kolom 2: Gebruiksprofiel bolletjes 1-5 -->
    <div>
      <div style="font-size:11px;font-weight:500;color:#6b7280;margin-bottom:8px">Gebruiksprofiel \u2014 bolletjes</div>
      <div style="display:flex;flex-direction:column;gap:7px">
        <div style="display:flex;align-items:center;gap:8px">
          <span style="display:inline-flex;gap:2px;flex-shrink:0">
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
          </span>
          <span style="font-size:11px;color:#6b7280"><b style="color:#111827">5</b> Uitputtend \u2014 alles staat erin</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="display:inline-flex;gap:2px;flex-shrink:0">
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#c7e8eb;display:inline-block"></span>
          </span>
          <span style="font-size:11px;color:#6b7280"><b style="color:#111827">4</b> Sterk \u2014 brede dekking</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="display:inline-flex;gap:2px;flex-shrink:0">
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#c7e8eb;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#c7e8eb;display:inline-block"></span>
          </span>
          <span style="font-size:11px;color:#6b7280"><b style="color:#111827">3</b> Goed \u2014 nuttige aanvulling</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="display:inline-flex;gap:2px;flex-shrink:0">
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#c7e8eb;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#c7e8eb;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#c7e8eb;display:inline-block"></span>
          </span>
          <span style="font-size:11px;color:#6b7280"><b style="color:#111827">2</b> Beperkt \u2014 zijdelings relevant</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <span style="display:inline-flex;gap:2px;flex-shrink:0">
            <span style="width:8px;height:8px;border-radius:50%;background:#1A6B72;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#c7e8eb;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#c7e8eb;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#c7e8eb;display:inline-block"></span>
            <span style="width:8px;height:8px;border-radius:50%;background:#c7e8eb;display:inline-block"></span>
          </span>
          <span style="font-size:11px;color:#6b7280"><b style="color:#111827">1</b> Minimaal \u2014 nauwelijks dekking</span>
        </div>
      </div>
    </div>

    <!-- Kolom 3: Audit score -->
    <div>
      <div style="font-size:11px;font-weight:500;color:#6b7280;margin-bottom:8px">Audit score (1.0 \u2013 5.0)</div>
      <div style="display:flex;flex-direction:column;gap:5px;font-size:11px;color:#6b7280">
        <div style="display:flex;align-items:center;gap:6px">
          <span style="width:36px;font-weight:500;color:#166534;flex-shrink:0">4.5\u20135</span>
          Uitstekend \u2014 native PDF
        </div>
        <div style="display:flex;align-items:center;gap:6px">
          <span style="width:36px;font-weight:500;color:#1A6B72;flex-shrink:0">3.5\u20134</span>
          Goed \u2014 lichte OCR-ruis
        </div>
        <div style="display:flex;align-items:center;gap:6px">
          <span style="width:36px;font-weight:500;color:#92400e;flex-shrink:0">2.5\u20133</span>
          Normaal \u2014 gescande PDF
        </div>
        <div style="display:flex;align-items:center;gap:6px">
          <span style="width:36px;font-weight:500;color:#991b1b;flex-shrink:0">&lt; 2.5</span>
          Laag \u2014 OCR-problemen
        </div>
      </div>
      <div style="margin-top:10px;font-size:10px;color:#6b7280;line-height:1.5;
           border-top:0.5px solid #e2e8f0;padding-top:8px">
        Score gebaseerd op steekproef van ~15 chunks.
        Gebruiksprofiel afgeleid uit K/A/I-tags van alle chunks.
      </div>
    </div>

  </div><!-- /legenda grid -->

  <!-- Verwerkingsstatus flow -->
  <div style="background:#f8fafc;border-radius:8px;padding:12px 16px;margin-bottom:16px">
    <div style="font-size:11px;font-weight:500;color:#6b7280;margin-bottom:10px">Verwerkingsstatus</div>
    <div style="display:flex;align-items:center;gap:0;flex-wrap:wrap;row-gap:8px">
      <div style="display:flex;flex-direction:column;align-items:center;gap:3px;min-width:76px">
        <span style="background:#f3f4f6;color:#374151;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:500">In wachtrij</span>
        <span style="font-size:10px;color:#6b7280;text-align:center">Wacht op<br>verwerking</span>
      </div>
      <span style="font-size:14px;color:#d1d5db;margin:0 4px;padding-bottom:14px">&rsaquo;</span>
      <div style="display:flex;flex-direction:column;align-items:center;gap:3px;min-width:76px">
        <span style="background:#e8f4f5;color:#085041;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:500">Bezig&hellip;</span>
        <span style="font-size:10px;color:#6b7280;text-align:center">Parsing,<br>embedding</span>
      </div>
      <span style="font-size:14px;color:#d1d5db;margin:0 4px;padding-bottom:14px">&rsaquo;</span>
      <div style="display:flex;flex-direction:column;align-items:center;gap:3px;min-width:84px">
        <span style="background:#fde68a;color:#92400e;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:500">Audit lopend</span>
        <span style="font-size:10px;color:#6b7280;text-align:center">Tekst klaar,<br>tags wachten</span>
      </div>
      <span style="font-size:14px;color:#d1d5db;margin:0 4px;padding-bottom:14px">&rsaquo;</span>
      <div style="display:flex;flex-direction:column;align-items:center;gap:3px;min-width:84px">
        <span style="background:#ddf2f3;color:#085041;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:500">Afb. lopend</span>
        <span style="font-size:10px;color:#6b7280;text-align:center">Tekst + audit<br>klaar</span>
      </div>
      <span style="font-size:14px;color:#d1d5db;margin:0 4px;padding-bottom:14px">&rsaquo;</span>
      <div style="display:flex;flex-direction:column;align-items:center;gap:3px;min-width:76px">
        <span style="background:#ddf2f3;color:#085041;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:500">Afb. bezig</span>
        <span style="font-size:10px;color:#6b7280;text-align:center">Extractie<br>actief</span>
      </div>
      <span style="font-size:14px;color:#d1d5db;margin:0 4px;padding-bottom:14px">&rsaquo;</span>
      <div style="display:flex;flex-direction:column;align-items:center;gap:3px;min-width:76px">
        <span style="background:#dcfce7;color:#166534;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:500">Klaar</span>
        <span style="font-size:10px;color:#6b7280;text-align:center">Volledig<br>doorzoekbaar</span>
      </div>
      <div style="width:0.5px;height:32px;background:#e2e8f0;margin:0 12px;align-self:center"></div>
      <div style="display:flex;flex-direction:column;align-items:center;gap:3px;min-width:76px">
        <span style="background:#fee2e2;color:#991b1b;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:500">Fout</span>
        <span style="font-size:10px;color:#6b7280;text-align:center">Handmatige<br>interventie</span>
      </div>
    </div>
  </div>

  <!-- Search + sort bar -->
  <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;align-items:center">
    <input id="search-input" type="text" placeholder="Zoek op titel of auteur…"
      oninput="filterItems()"
      style="flex:1;min-width:200px;padding:8px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:14px">
    <label style="font-size:13px;color:#6b7280">Sorteer:
      <select id="sort-select" onchange="renderItems()"
        style="margin-left:4px;padding:6px 10px;border:1px solid #d1d5db;border-radius:6px;font-size:13px">
        <option value="title">Titel</option>
        <option value="chunks_desc">Chunks ↓</option>
        <option value="chunks_asc">Chunks ↑</option>
        <option value="k">K-waarde</option>
      </select>
    </label>
  </div>

  <!-- Category tabs -->
  <div id="cat-tabs" style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:16px"></div>

  <!-- Item list -->
  <div id="item-list" style="display:flex;flex-direction:column;gap:8px">
    <div style="color:#6b7280;font-size:14px;text-align:center;padding:40px">Laden…</div>
  </div>
</div>

<!-- Delete confirmation modal -->
<div id="del-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:1000;align-items:center;justify-content:center">
  <div style="background:#fff;border-radius:12px;padding:28px;max-width:440px;width:90%;box-shadow:0 8px 32px rgba(0,0,0,.18)">
    <h3 style="font-size:16px;font-weight:700;margin-bottom:12px;color:#111">Verwijder uit Qdrant</h3>
    <p id="del-msg" style="font-size:14px;color:#374151;margin-bottom:20px"></p>
    <div style="display:flex;gap:10px;justify-content:flex-end">
      <button onclick="closeDelModal()" class="btn btn-secondary">Annuleren</button>
      <button id="del-confirm-btn" onclick="confirmDelete()"
        style="background:#dc2626;color:#fff;border:none;padding:8px 18px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600">
        Verwijder
      </button>
    </div>
  </div>
</div>

<script>
let _allItems = [];
let _filtered = [];
let _activeTab = 'all';
let _pendingDelete = null;

const CAT_LABELS = {
  all:              'Alles',
  medical_literature: 'Medische Literatuur',
  acupuncture:      'Acupunctuur',
  nrt_kinesiology:  'NRT/Kinesiologie',
  qat_curriculum:   'QAT Curriculum',
  device:           'Apparatuur',
  videos:           "Video's",
};
const CAT_ORDER = ['all','medical_literature','acupuncture','nrt_kinesiology','qat_curriculum','device','videos'];
const KAI_COLORS = {1:'#16a34a', 2:'#ea580c', 3:'#6b7280'};
const STATUS_PILLS = {
  in_wachtrij:   {label:'In wachtrij',      bg:'#f3f4f6', color:'#374151'},
  bezig:         {label:'Bezig\u2026',      bg:'#e8f4f5', color:'#085041'},
  audit_lopend:  {label:'Audit lopend',     bg:'#fde68a', color:'#92400e'},
  afb_lopend:    {label:'Afb. lopend',      bg:'#ddf2f3', color:'#085041'},
  afb_bezig:     {label:'Afb. bezig\u2026', bg:'#ddf2f3', color:'#085041'},
  klaar:         {label:'Klaar',            bg:'#dcfce7', color:'#166534'},
  fout:          {label:'Fout',             bg:'#fee2e2', color:'#991b1b'},
  permanent_fout:{label:'Permanent fout',   bg:'#fee2e2', color:'#7f1d1d'},
};

async function loadItems() {
  try {
    const r = await fetch('/api/library/items');
    const d = await r.json();
    _allItems = d.items || [];
    filterItems();
    renderTabs();
    return _allItems;
  } catch(e) {
    document.getElementById('item-list').innerHTML =
      '<div style="color:#dc2626;font-size:14px;text-align:center;padding:40px">Fout bij laden: ' + e + '</div>';
    return [];
  }
}

function renderTabs() {
  const counts = {};
  counts['all'] = _allItems.length;
  for (const item of _allItems) {
    counts[item.library_category] = (counts[item.library_category] || 0) + 1;
  }
  const el = document.getElementById('cat-tabs');
  el.innerHTML = CAT_ORDER
    .filter(k => counts[k] > 0)
    .map(k => {
      const active = k === _activeTab;
      const cnt = counts[k] || 0;
      return `<button onclick="setTab('${k}')"
        style="padding:6px 14px;border-radius:20px;border:1px solid ${active?'#2563eb':'#d1d5db'};
               background:${active?'#2563eb':'#fff'};color:${active?'#fff':'#374151'};
               font-size:13px;cursor:pointer;font-weight:${active?'600':'400'}">
        ${CAT_LABELS[k] || k} <span style="opacity:.7">(${cnt})</span>
      </button>`;
    }).join('');
}

function setTab(tab) {
  _activeTab = tab;
  filterItems();
  renderTabs();
}

function filterItems() {
  const q = (document.getElementById('search-input').value || '').toLowerCase();
  _filtered = _allItems.filter(item => {
    if (_activeTab !== 'all' && item.library_category !== _activeTab) return false;
    if (q) {
      const hay = (item.title + ' ' + item.authors).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
  renderItems();
}

function renderItems() {
  const sort = document.getElementById('sort-select').value;
  const items = [..._filtered];
  items.sort((a, b) => {
    if (sort === 'title')       return a.title.localeCompare(b.title);
    if (sort === 'chunks_desc') return (b.chunk_count || 0) - (a.chunk_count || 0);
    if (sort === 'chunks_asc')  return (a.chunk_count || 0) - (b.chunk_count || 0);
    if (sort === 'k')           return (a.k || 9) - (b.k || 9);
    return 0;
  });

  if (!items.length) {
    document.getElementById('item-list').innerHTML =
      '<div style="color:#6b7280;font-size:14px;text-align:center;padding:40px">Geen items gevonden</div>';
    return;
  }

  document.getElementById('item-list').innerHTML = items.map(item => renderCard(item)).join('');
}

function kaiPill(letter, val) {
  if (!val) return '';
  const KAI_LABELS_MAP = {K:'Klinisch', A:'Acupunctuur', I:'Afbeeldingen'};
  const KAI_PRIO_MAP   = {1:'primaire bron', 2:'ondersteunend', 3:'achtergrond'};
  const KAI_BG_STYLE   = {
    1:'background:#dcfce7;color:#166534',
    2:'background:#ffedd5;color:#9a3412',
    3:'background:#f3f4f6;color:#374151'
  };
  const bgStyle = KAI_BG_STYLE[val] || 'background:#f3f4f6;color:#374151';
  const lbl  = KAI_LABELS_MAP[letter] || letter;
  const prio = KAI_PRIO_MAP[val] || val;
  return `<div style="display:flex;align-items:center;gap:6px">
    <span style="font-size:11px;color:#6b7280">${lbl}, ${prio}</span>
    <span style="font-size:11px;${bgStyle};border-radius:4px;padding:2px 8px;font-weight:500">${letter}${val}</span>
  </div>`;
}

function statusPill(status) {
  const s = STATUS_PILLS[status] || STATUS_PILLS['in_wachtrij'];
  return `<span style="background:${s.bg};color:${s.color};border-radius:999px;
    padding:3px 10px;font-size:12px;font-weight:500;white-space:nowrap">${s.label}</span>`;
}

function ocrBadge(engine) {
  if (!engine || engine === 'native') return '';
  if (engine === 'google_vision')
    return '<span style="font-size:10px;background:#fef3c7;color:#92400e;border-radius:4px;padding:1px 6px;margin-left:4px">Google Vision</span>';
  return `<span style="font-size:10px;background:#f3f4f6;color:#6b7280;border-radius:4px;padding:1px 6px;margin-left:4px">${engine}</span>`;
}

function renderCard(item) {
  const clickable = item.book_hash
    ? `class="book-row" onclick="toggleBookDetail(this,'${escJs(item.book_hash)}')" style="cursor:pointer;`
    : 'style="';

  const kaiBadges = [['K', item.k], ['A', item.a], ['I', item.i]]
    .filter(([, v]) => v)
    .map(([l, v]) => kaiPill(l, v))
    .join('');

  let statusHtml = statusPill(item.status);
  if (item.status === 'afb_bezig' && item.image_progress) {
    const pr = item.image_progress;
    const pp = pr.pages_processed ?? '?';
    const pt = pr.pages_total ?? '?';
    const ff = pr.figures_found ?? 0;
    statusHtml += `<div style="font-size:10px;color:#085041;opacity:0.7;margin-top:3px;text-align:right;white-space:nowrap">${pp}/${pt} pagina's &middot; ${ff} fig.</div>`;
  }

  return `<div ${clickable}background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.07);
                      padding:14px 18px;display:flex;align-items:center;gap:12px;flex-wrap:wrap">
    <div style="flex:1;min-width:200px">
      <div style="font-weight:600;font-size:15px;color:#111">${escHtml(item.title)}</div>
      <div style="font-size:12px;color:#6b7280;margin-top:2px">${escHtml(item.authors || '')}</div>
    </div>
    <div style="display:flex;flex-direction:column;gap:4px;align-items:flex-end">
      ${kaiBadges}
    </div>
    <div style="display:flex;gap:6px;align-items:flex-start;flex-wrap:wrap">
      <div style="display:flex;flex-direction:column;align-items:flex-end">${statusHtml}</div>
      ${ocrBadge(item.ocr_engine)}
    </div>
  </div>`;
}

async function toggleBookDetail(row, bookHash) {
  const existingDetail = document.getElementById('detail-' + bookHash);
  if (existingDetail) {
    existingDetail.remove();
    row.classList.remove('active-row');
    return;
  }
  row.classList.add('active-row');

  // Insert loading placeholder immediately
  const placeholder = document.createElement('div');
  placeholder.id = 'detail-' + bookHash;
  placeholder.style.cssText = 'background:#f8fffe;border-left:3px solid #1A6B72;'
    + 'border-radius:0 0 10px 10px;padding:10px 16px;margin-top:-4px;'
    + 'box-shadow:0 2px 4px rgba(0,0,0,.06)';
  placeholder.innerHTML = '<div style="font-size:12px;color:#6b7280;padding:6px 0">\u23F3 Laden\u2026</div>';
  row.insertAdjacentElement('afterend', placeholder);

  try {
    const resp = await fetch('/api/library/book/' + bookHash + '/detail');
    if (!resp.ok) {
      placeholder.innerHTML = '<div style="font-size:12px;color:#dc2626;padding:6px 0">Geen ingest data beschikbaar voor dit boek.</div>';
      return;
    }
    const d    = await resp.json();
    const item = (_allItems || []).find(it => it.book_hash === bookHash) || {};
    placeholder.innerHTML = buildPhaseTable(d, {
      itemId:     item.id         || '',
      itemTitle:  item.title      || '',
      itemColl:   item.collection || '',
      chunkCount: item.chunk_count || 0,
      bookHash:   bookHash,
    });
  } catch(e) {
    placeholder.innerHTML = '<div style="font-size:12px;color:#dc2626;padding:6px 0">Fout: ' + e + '</div>';
  }
}

function buildPhaseTable(d, meta) {
  meta = meta || {};
  const parseTs = s => s ? new Date(s) : null;
  const fmtTime = dt => dt
    ? dt.toLocaleTimeString('nl-NL', {hour:'2-digit', minute:'2-digit'})
    : '\u2014';
  const elapsed = (start, end) => {
    if (!start) return '\u2014';
    const ms  = (end || new Date()) - start;
    const tot = Math.floor(ms / 60000);
    return Math.floor(tot / 60) + ':' + String(tot % 60).padStart(2, '0');
  };
  const fmt = n => (n == null) ? '\u2014' : Number(n).toLocaleString('nl-NL');

  const phaseOrder = ['parse','audit','embed','qdrant'];
  const phaseNames = {
    parse:'Parsing', audit:'Audit & Tagging',
    embed:'Embedding', qdrant:'Qdrant upload'
  };
  const circleColor = {done:'#059669', running:'#1A6B72', failed:'#dc2626', pending:'#d1d5db'};
  const circleIcon  = {done:'\u2713', running:'\u25B6', failed:'\u2717', pending:'\u2022'};
  const pillStyles  = {
    done:'background:#dcfce7;color:#16a34a',
    running:'background:#e8f4f5;color:#1A6B72',
    failed:'background:#fee2e2;color:#dc2626',
    pending:'background:#f3f4f6;color:#6b7280'
  };
  const pillLabels  = {done:'Klaar', running:'Bezig', failed:'Fout', pending:'Wacht'};

  // ── Audit score + categories info block ─────────────────────────────────────
  const auditScore   = (d.audit_score != null) ? d.audit_score.toFixed(1) + ' / 5.0' : '\u2014';
  const chunkCountD  = d.chunk_count || 0;
  const catScores    = d.category_scores || {};
  const catDefs      = [
    ['Protocol',   catScores.protocol   || 0, 'Behandelinstructies, punten'],
    ['Diagnose',   catScores.diagnose   || 0, 'Symptomen, TCM-patronen'],
    ['Anatomie',   catScores.anatomie   || 0, 'Spieren, zenuwen, structuren'],
    ['Literatuur', catScores.literatuur || 0, 'Wetenschappelijke basis'],
  ];
  const dotRow = (label, n, desc) => {
    const dots = Array.from({length: 5}, (_, i) =>
      '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
      + 'background:' + (i < n ? '#1A6B72' : '#c7e8eb') + ';margin-right:2px"></span>'
    ).join('');
    return '<div style="display:flex;align-items:center;gap:4px;margin-bottom:2px">'
      + '<span style="font-size:11px;color:#085041;width:68px">' + label + '</span>' + dots
      + (desc ? '<span style="font-size:11px;color:#085041;opacity:0.65;margin-left:8px">' + desc + '</span>' : '')
      + '</div>';
  };
  let html = '<div style="background:#ddf2f3;border-radius:8px;padding:10px 12px;margin-bottom:12px;'
    + 'display:flex;justify-content:space-between;align-items:flex-start;gap:16px">'
    + '<div>'
      + '<div style="font-size:11px;color:#085041;font-weight:500;margin-bottom:4px">Audit score</div>'
      + '<div style="font-size:22px;font-weight:500;color:#085041">' + auditScore + '</div>'
    + '</div>'
    + '<div style="flex:1">'
      + '<div style="display:flex;justify-content:space-between;align-items:flex-start">'
        + '<div>'
          + '<div style="font-size:11px;color:#085041;font-weight:500;margin-bottom:4px">Categorie\u00ebn</div>'
          + catDefs.map(([l, n, d]) => dotRow(l, n, d)).join('')
        + '</div>'
        + '<div style="font-size:13px;font-weight:500;color:#085041;white-space:nowrap">'
          + (chunkCountD ? chunkCountD.toLocaleString('nl-NL') + ' chunks' : '\u2014')
        + '</div>'
      + '</div>'
    + '</div>'
  + '</div>';

  // Book-level summary bar — started_at may be null at top level; fall back to parse phase
  const bkStart = parseTs(d.started_at || (d.phases && d.phases.parse && d.phases.parse.started_at));
  const bkEnd   = parseTs(d.completed_at);
  html += `<div style="background:#ddf2f3;border-radius:6px;padding:3px 10px;`
    + `font-size:12px;font-family:monospace;color:#085041;margin-bottom:10px">`
    + `Start ${bkStart
        ? bkStart.toLocaleDateString('nl-NL',{day:'2-digit',month:'2-digit'}).replace('/','-')
          + ' ' + fmtTime(bkStart)
        : '\u2014'}`
    + ` &nbsp;\u00b7&nbsp; Eind ${fmtTime(bkEnd)}`
    + ` &nbsp;\u00b7&nbsp; Verstreken ${elapsed(bkStart, bkEnd)}`
    + `</div>`;

  const thS = 'text-align:left;padding:5px 6px 7px;font-weight:500;font-size:12px;'
    + 'border-bottom:1.5px solid #1A6B72;white-space:nowrap;background:#ddf2f3;color:#085041';

  html += `<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:13px">`
    + `<colgroup><col style="width:32%"><col style="width:14%">`
    + `<col style="width:18%"><col style="width:18%"><col style="width:18%"></colgroup>`
    + `<thead><tr>`
    + `<th style="${thS};padding-left:0">Fase</th>`
    + `<th style="${thS}">Status</th>`
    + `<th style="${thS}">Start</th>`
    + `<th style="${thS}">Eind</th>`
    + `<th style="${thS}">Totaal</th>`
    + `</tr></thead><tbody>`;

  for (let pi = 0; pi < phaseOrder.length; pi++) {
    const ph   = phaseOrder[pi];
    const info = (d.phases && d.phases[ph]) || {};
    const st   = info.status || 'pending';
    const isDone    = st === 'done';
    const isRunning = st === 'running';
    let ccol = circleColor[st] || '#d1d5db';
    let icon = circleIcon[st]  || '\u2022';

    let detail = '';
    if (ph === 'parse' && isDone) {
      detail = fmt(info.pages_total) + " pagina\u2019s";
      if (info.chunks_extracted) detail += ' \u00b7 ' + fmt(info.chunks_extracted) + ' chunks';
      if (info.ocr_engine && info.ocr_engine !== 'native' && info.ocr_engine !== 'pymupdf')
        detail += ' \u00b7 <span style="color:#6b7280">' + info.ocr_engine + '</span>';
    } else if (ph === 'audit' && isDone) {
      const cs = info.chunks_skipped || 0;
      const ct = info.chunks_tagged  || 0;
      const cx = info.chunks_total   || 0;
      if (cs > 0) {
        const claudeOn = !!d.claude_api_enabled;
        let infoBox;
        if (claudeOn) {
          infoBox = '<div style="background:#EEEDFE;border-radius:6px;padding:4px 8px;font-size:11px;'
            + 'color:#3C3489;margin-top:5px">Claude API actief \u2014 run \u2018Nu uitvoeren\u2019 voor directe verwerking</div>';
        } else {
          infoBox = '<div style="background:#fde68a;border-radius:6px;padding:4px 8px;font-size:11px;'
            + 'color:#78350f;margin-top:5px">Nachtrun verwerkt overgeslagen chunks binnen tijdvenster'
            + ' (02:00\u201307:00 Amsterdam) \u2014 proportioneel budget</div>';
        }
        detail = fmt(ct) + ' getagd \u00b7 ' + fmt(cs) + ' overgeslagen' + infoBox;
        ccol = claudeOn ? '#7c3aed' : '#d97706';
        icon = '\u263D';
      } else {
        detail = fmt(cx) + ' chunks';
        if (ct) detail += ' \u00b7 ' + fmt(ct) + ' getagd';
      }
    } else if (ph === 'embed' && isDone) {
      detail = fmt(info.chunks_done || info.chunks_total) + ' vectors';
    } else if (ph === 'qdrant' && isDone) {
      detail = fmt(info.chunks_inserted) + ' vectors';
      if (info.collection) detail += ' \u2192 ' + info.collection;
    } else if (st === 'failed' && info.error) {
      detail = '<span style="color:#dc2626">' + String(info.error).slice(0, 80) + '</span>';
    }

    const phStart = parseTs(info.started_at);
    const phEnd   = parseTs(info.completed_at);
    const auditNachtrun = ph === 'audit' && isDone && (info.chunks_skipped || 0) > 0;
    let pill, rowBg;
    if (auditNachtrun) {
      pill  = `<span style="background:#fef3c7;color:#92400e;border-radius:999px;`
        + `padding:2px 8px;font-size:11px;font-weight:600">Nachtrun</span>`;
      rowBg = 'background:#fffbeb;';
    } else {
      pill  = `<span style="${pillStyles[st]||pillStyles.pending};border-radius:999px;`
        + `padding:2px 8px;font-size:11px;font-weight:600">${pillLabels[st]||'Wacht'}</span>`;
      rowBg = isRunning ? 'background:#f0faf8;' : '';
    }

    html += `<tr style="${rowBg}border-bottom:0.5px solid #e2e8f0">`
      + `<td style="padding:7px 0;vertical-align:top">`
        + `<div style="display:flex;align-items:flex-start;gap:6px">`
          + `<span style="margin-top:2px;width:16px;height:16px;border-radius:50%;`
            + `background:${ccol};color:#fff;font-size:9px;font-weight:700;display:flex;`
            + `align-items:center;justify-content:center;flex-shrink:0">${icon}</span>`
          + `<div>`
            + `<span style="font-size:13px;color:${isRunning?'#1A6B72':'#374151'};`
              + `font-weight:${isRunning?600:400}">${pi+1}. ${phaseNames[ph]}</span>`
            + (detail ? `<div style="font-size:11px;color:#6b7280;margin-top:1px">${detail}</div>` : '')
          + `</div>`
        + `</div>`
      + `</td>`
      + `<td style="padding:7px 6px;vertical-align:top">${pill}</td>`
      + `<td style="padding:7px 6px;font-size:12px;color:#4a5568;vertical-align:top">${fmtTime(phStart)}</td>`
      + `<td style="padding:7px 6px;font-size:12px;color:${isRunning?'#1A6B72':'#4a5568'};vertical-align:top">`
        + `${isDone ? fmtTime(phEnd) : (isRunning ? 'bezig' : '\u2014')}</td>`
      + `<td style="padding:7px 6px;font-size:12px;color:#4a5568;vertical-align:top">`
        + `${(isDone||isRunning) ? elapsed(phStart, phEnd) : '\u2014'}</td>`
      + `</tr>`;
  }

  // ── 5th row: Image extraction (outside phase loop, background thread) ────────
  {
    const ie   = d.image_extraction || {};
    const ieSt = ie.status || 'pending';
    let ieccol   = '#d1d5db';
    let ieicon   = '\u2022';
    let ieDetail = '';
    let ieBar    = '';
    let iePillSt = 'background:#f3f4f6;color:#6b7280';
    let iePillLb = 'Wacht';
    if (ieSt === 'not_applicable') {
      iePillLb = 'N.v.t.';
      iePillSt = 'background:#f3f4f6;color:#6b7280';
      ieccol   = '#d1d5db';
      ieicon   = '\u2014';
      ieDetail = 'Geen afbeeldingen verwacht voor dit boektype';
    } else if (ieSt === 'running') {
      iePillSt = 'background:#ddf2f3;color:#085041';
      iePillLb = 'Bezig';
      ieccol   = '#1A6B72';
      ieicon   = '\u25B6';
      const pp = ie.pages_processed, pt = ie.pages_total, ff = ie.figures_found;
      if (pp != null && pt != null) {
        ieDetail = `pagina ${fmt(pp)} / ${fmt(pt)}`;
        if (ff) ieDetail += ` \u00b7 ${fmt(ff)} figuren`;
        const pct = Math.min(Math.round(pp / pt * 100), 100);
        ieBar = `<div style="margin-top:4px;background:#c7e8eb;border-radius:999px;height:4px">`
          + `<div style="background:#1A6B72;border-radius:999px;height:4px;width:${pct}%;transition:width 0.5s"></div></div>`;
      }
    } else if (ieSt === 'done') {
      const nf = ie.figures_found;
      if (nf != null && nf > 0) {
        iePillSt = 'background:#dcfce7;color:#166534';
        iePillLb = 'Klaar';
        ieccol   = '#059669';
        ieicon   = '\u2713';
        ieDetail = fmt(nf) + ' figuren ge\u00ebxtraheerd';
      } else {
        iePillLb = 'Geen';
        iePillSt = 'background:#f3f4f6;color:#6b7280';
        ieDetail = 'Geen figuren gevonden in document';
        ieccol   = '#d1d5db';
        ieicon   = '\u2014';
      }
    } else if (ieSt === 'disabled') {
      iePillLb = 'Uit';
      iePillSt = 'background:#f3f4f6;color:#6b7280';
      ieccol   = '#d1d5db';
      ieicon   = '\u2014';
      ieDetail = 'Afbeeldingen extractie uitgeschakeld';
    }
    const ieRunning = ieSt === 'running';
    const iePill  = `<span style="${iePillSt};border-radius:999px;padding:2px 8px;font-size:11px;font-weight:600">${iePillLb}</span>`;
    const ieRowBg = ieRunning ? 'background:#f0faf8;' : '';
    html += `<tr style="${ieRowBg}border-bottom:0.5px solid #e2e8f0">`
      + `<td style="padding:7px 0;vertical-align:top">`
        + `<div style="display:flex;align-items:flex-start;gap:6px">`
          + `<span style="margin-top:2px;width:16px;height:16px;border-radius:50%;`
            + `background:${ieccol};color:#fff;font-size:9px;font-weight:700;display:flex;`
            + `align-items:center;justify-content:center;flex-shrink:0">${ieicon}</span>`
          + `<div>`
            + `<span style="font-size:13px;color:${ieRunning?'#1A6B72':'#374151'};`
              + `font-weight:${ieRunning?600:400}">5. Afbeeldingen</span>`
            + (ieDetail ? `<div style="font-size:11px;color:#6b7280;margin-top:1px">${ieDetail}</div>` : '')
            + ieBar
          + `</div>`
        + `</div>`
      + `</td>`
      + `<td style="padding:7px 6px;vertical-align:top">${iePill}</td>`
      + `<td style="padding:7px 6px;font-size:12px;color:#4a5568;vertical-align:top">\u2014</td>`
      + `<td style="padding:7px 6px;font-size:12px;color:#4a5568;vertical-align:top">\u2014</td>`
      + `<td style="padding:7px 6px;font-size:12px;color:#4a5568;vertical-align:top">\u2014</td>`
      + `</tr>`;
  }

  html += '</tbody></table>';

  // ── Image extraction toggle row ───────────────────────────────────────────────
  {
    const imgHash    = meta.bookHash || '';
    const imgEnabled = d.image_extraction_enabled !== false;
    const toggleId   = 'img-toggle-' + imgHash;
    if (imgHash) {
      html += '<div style="padding:10px 0 6px;border-top:0.5px solid #e2e8f0;'
        + 'display:flex;align-items:center;justify-content:space-between">'
        + '<span style="font-size:12px;color:#6b7280">Afbeeldingen extraheren</span>'
        + '<label style="display:flex;align-items:center;gap:6px;cursor:pointer">'
          + '<input type="checkbox" id="' + escHtml(toggleId) + '"'
            + (imgEnabled ? ' checked' : '')
            + ' onchange="confirmImageToggle(\'' + escJs(imgHash) + '\',this.checked,this)"'
            + ' style="width:14px;height:14px;cursor:pointer">'
          + '<span id="' + escHtml(toggleId) + '-lbl" style="font-size:12px;color:#6b7280">'
            + (imgEnabled ? 'Aan' : 'Uit')
          + '</span>'
        + '</label>'
        + '</div>';
    }
  }

  // Delete button at drawer bottom — use data attributes to avoid quote escaping issues
  const delItemId = meta.itemId     || '';
  const delTitle  = meta.itemTitle  || '';
  const delColl   = meta.itemColl   || '';
  const delChunks = meta.chunkCount || 0;
  if (delItemId && delChunks > 0) {
    html += '<div style="display:flex;justify-content:flex-end;margin-top:14px;'
      + 'padding-top:10px;border-top:0.5px solid #e2e8f0">'
      + '<button onclick="event.stopPropagation();'
        + 'openDelModal(this.dataset.id,this.dataset.title,+this.dataset.chunks,this.dataset.coll)"'
      + ' data-id="' + escHtml(delItemId) + '"'
      + ' data-title="' + escHtml(delTitle) + '"'
      + ' data-chunks="' + String(delChunks) + '"'
      + ' data-coll="' + escHtml(delColl) + '"'
      + ' style="font-size:12px;padding:5px 14px;border-radius:6px;'
      + 'border:0.5px solid #dc2626;color:#dc2626;background:transparent;cursor:pointer">'
      + 'Verwijder uit Qdrant'
      + '</button></div>';
  }

  return html;
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escJs(s) {
  return String(s).replace(/\\\\/g,'\\\\\\\\').replace(/'/g,"\\\\'");
}

let _delItem = null;
function openDelModal(id, title, chunks, collection) {
  _delItem = {id, title, chunks, collection};
  document.getElementById('del-msg').textContent =
    `Verwijder ${chunks.toLocaleString()} chunks voor "${title}" uit Qdrant? Dit kan niet ongedaan worden gemaakt.`;
  const modal = document.getElementById('del-modal');
  modal.style.display = 'flex';
}
function closeDelModal() {
  document.getElementById('del-modal').style.display = 'none';
  _delItem = null;
}
async function confirmDelete() {
  if (!_delItem) return;
  const btn = document.getElementById('del-confirm-btn');
  btn.disabled = true;
  btn.textContent = 'Bezig…';
  try {
    const r = await fetch(`/api/library/items/${encodeURIComponent(_delItem.id)}?dry_run=false`, {method:'DELETE'});
    const d = await r.json();
    closeDelModal();
    if (d.deleted !== undefined) {
      await loadItems();
    } else {
      alert('Fout: ' + (d.error || JSON.stringify(d)));
    }
  } catch(e) {
    alert('Fout: ' + e);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Verwijder';
  }
}

async function confirmImageToggle(hash, enabled, checkbox) {
  const msg = enabled
    ? 'Afbeeldingen extractie wordt gestart voor dit boek. Doorgaan?'
    : 'Alle ge\u00ebxtraheerde afbeeldingen worden definitief verwijderd van de server. Doorgaan?';
  if (!confirm(msg)) {
    checkbox.checked = !enabled;
    return;
  }
  try {
    const r = await fetch('/api/library/book/' + hash + '/toggle-images', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({enabled})
    });
    const d = await r.json();
    if (d.ok) {
      const lbl = document.getElementById('img-toggle-' + hash + '-lbl');
      if (lbl) lbl.textContent = enabled ? 'Aan' : 'Uit';
      loadItems();
    } else {
      alert('Fout: ' + (d.error || 'onbekend'));
      checkbox.checked = !enabled;
    }
  } catch(e) {
    alert('Fout: ' + e);
    checkbox.checked = !enabled;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadItems().then(items => {
    const hasActive = items.some(i => i.status === 'afb_bezig');
    if (hasActive && !window._imgRefreshTimer) {
      window._imgRefreshTimer = setInterval(() => {
        loadItems().then(items => {
          const stillActive = items.some(i => i.status === 'afb_bezig');
          if (!stillActive) {
            clearInterval(window._imgRefreshTimer);
            window._imgRefreshTimer = null;
          }
        });
      }, 15000);
    }
  });
});
</script>"""
    return _page_shell("Bibliotheek", "/library", body)


# ── GET /api/library/items ─────────────────────────────────────────────────────

@app.get("/api/library/items")
async def api_library_items():
    """Return all catalog items with metadata + live Qdrant chunk counts."""
    try:
        cfg = json.loads(CLASSIFICATIONS_PATH.read_text())
    except Exception as e:
        return JSONResponse({"error": str(e), "items": []}, status_code=500)

    classifications: dict = cfg.get("classifications", {})

    # Determine currently processing / queued books
    processing_file = ""
    queued_files: set[str] = set()
    try:
        if BOOK_CURRENT_FILE.exists():
            cur = json.loads(BOOK_CURRENT_FILE.read_text())
            processing_file = cur.get("filename", "") or cur.get("file", "")
    except Exception:
        pass
    try:
        if BOOK_QUEUE_FILE.exists():
            q = json.loads(BOOK_QUEUE_FILE.read_text())
            for entry in q:
                fn = entry.get("filename", "") or entry.get("file", "")
                if fn:
                    queued_files.add(fn)
    except Exception:
        pass

    # Build map of filename.lower() → {book_hash, ocr_engine, state, _full_state} from state.json cache
    # MUST be built before count_coros so we can use the real filename as Qdrant source_key
    state_map: dict[str, dict] = {}
    try:
        for sf in CACHE_DIR.glob("*/state.json"):
            try:
                s  = json.loads(sf.read_text())
                fn = (s.get("filename") or "").lower()
                if fn:
                    phases = s.get("phases") or {}
                    state_map[fn] = {
                        "book_hash":       s.get("book_hash", ""),
                        "ocr_engine":      phases.get("parse", {}).get("ocr_engine") or "",
                        "completed_at":    s.get("completed_at") or "",
                        "chunks_inserted": phases.get("qdrant", {}).get("chunks_inserted") or 0,
                        "_full_state":     s,
                    }
            except Exception:
                pass
    except Exception:
        pass

    def _resolve_state_entry(patterns: list[str], book_id: str) -> tuple[str, dict]:
        """Return (actual_filename, state_map_entry) for the best pattern match."""
        for p in (patterns or [book_id]):
            pl = p.lower()
            for fn_key, sm in state_map.items():
                if pl in fn_key or fn_key in pl:
                    return fn_key, sm
        return "", {}

    # Build item list and collect async Qdrant queries
    items_meta: list[dict] = []
    count_coros = []

    for book_id, info in classifications.items():
        category = info.get("library_category", "")
        collection = _CAT_COLLECTION.get(category, "medical_library")
        patterns = info.get("filename_patterns", [])

        items_meta.append({
            "id":               book_id,
            "title":            info.get("full_title", book_id),
            "authors":          info.get("authors", ""),
            "k":                info.get("k"),
            "a":                info.get("a"),
            "i":                info.get("i"),
            "library_category": category,
            "collection":       collection,
            "patterns":         patterns,
            "format":           info.get("format", ""),
        })
        # Use actual filename from state.json as Qdrant source_key (exact match)
        # Fall back to first pattern if no state.json entry found
        actual_fn, _sm = _resolve_state_entry(patterns, book_id)
        source_key = actual_fn if actual_fn else (patterns[0] if patterns else book_id)
        count_coros.append(_qdrant_count_source(collection, source_key))

    # Run all Qdrant count queries in parallel
    counts = await asyncio.gather(*count_coros, return_exceptions=True)

    items_out = []
    for meta, count in zip(items_meta, counts):
        chunk_count = count if isinstance(count, int) else 0
        patterns    = meta.pop("patterns")

        actual_fn, sm = _resolve_state_entry(patterns, meta["id"])
        ocr_engine    = sm.get("ocr_engine", "")
        book_hash     = sm.get("book_hash", "")

        # Determine status via _compute_book_status (single source of truth)
        full_state = sm.get("_full_state", {})
        if full_state:
            status = _compute_book_status(full_state)
            if status == "klaar" and chunk_count == 0:
                chunk_count = sm.get("chunks_inserted", 0)
        else:
            # No state.json — fall back to queue/current file check
            def _matches_file(fname: str, _pats=patterns, _id=meta["id"]) -> bool:
                if not fname:
                    return False
                fl = fname.lower()
                return any(p.lower() in fl or fl in p.lower() for p in _pats) if _pats else (_id.lower() in fl)
            if _matches_file(processing_file):
                status = "bezig"
            elif any(_matches_file(qf) for qf in queued_files):
                status = "in_wachtrij"
            else:
                status = "in_wachtrij"

        image_progress = _get_image_progress(book_hash) if status == "afb_bezig" else None
        items_out.append({**meta, "chunk_count": chunk_count, "status": status,
                          "ocr_engine": ocr_engine, "book_hash": book_hash,
                          "image_progress": image_progress})

    return {"items": items_out}


# ── GET /api/library/book/{book_hash}/detail ───────────────────────────────────

@app.get("/api/library/book/{book_hash}/detail")
async def api_library_book_detail(book_hash: str):
    """Return state.json enriched with audit data — used by the library detail drawer."""
    safe = re.sub(r"[^a-f0-9]", "", book_hash)[:16]
    sf   = CACHE_DIR / safe / "state.json"
    state = _load_state(sf)
    if state is None:
        return JSONResponse({"error": "not found"}, status_code=404)

    # Enrich with audit score + category scores
    audit_score: float | None = None
    category_scores = {"protocol": 0, "diagnose": 0, "anatomie": 0, "literatuur": 0}
    chunk_count = (state.get("phases") or {}).get("qdrant", {}).get("chunks_inserted") or 0

    filename = state.get("filename", "")
    if filename:
        stem = Path(filename).stem
        audit_path = QUALITY_DIR / f"{stem}_audit.json"
        if audit_path.exists():
            try:
                a = json.loads(audit_path.read_text())
                qs_val = (a.get("llm_audit") or {}).get("quality_score")
                if qs_val is not None:
                    audit_score = float(qs_val)
                up = (a.get("usability_profile") or {}).get("scores", {})
                if up:
                    category_scores = {
                        "protocol":   round(max(
                            float(up.get("acupuncture_point_indication", 0)),
                            float(up.get("treatment_protocol", 0))
                        )),
                        "diagnose":   round(float(up.get("tcm_diagnosis", 0))),
                        "anatomie":   round(float(up.get("anatomy", 0))),
                        "literatuur": round(float(up.get("literature_reference", 0))),
                    }
            except Exception:
                pass

    claude_api_enabled = False
    try:
        settings = json.loads(SETTINGS_PATH.read_text())
        claude_api_enabled = bool(settings.get("claude_api", {}).get("enabled", False))
    except Exception:
        pass

    image_extraction = _build_image_extraction_info(safe, state, filename)
    computed_status  = _compute_book_status(state)

    return {**state, "audit_score": audit_score,
            "category_scores": category_scores, "chunk_count": chunk_count,
            "claude_api_enabled": claude_api_enabled,
            "image_extraction": image_extraction,
            "computed_status": computed_status,
            "image_extraction_enabled": state.get("image_extraction_enabled", True)}


# ── DELETE /api/library/items/{item_id} ────────────────────────────────────────

@app.delete("/api/library/items/{item_id}")
async def api_library_delete(item_id: str, dry_run: bool = True):
    """Delete all Qdrant points for a book by item_id. dry_run=true returns count only."""
    # Sanitise
    safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "", item_id)
    try:
        cfg = json.loads(CLASSIFICATIONS_PATH.read_text())
    except Exception as e:
        return JSONResponse({"error": f"Cannot read classifications: {e}"}, status_code=500)

    info = cfg.get("classifications", {}).get(safe_id)
    if not info:
        return JSONResponse({"error": f"Unknown item: {safe_id}"}, status_code=404)

    category   = info.get("library_category", "")
    collection = _CAT_COLLECTION.get(category, "medical_library")
    patterns   = info.get("filename_patterns", [])
    source_key = patterns[0] if patterns else safe_id

    # Count first (always)
    count = await _qdrant_count_source(collection, source_key)

    if dry_run:
        return {"item_id": safe_id, "collection": collection, "source_key": source_key, "count": count}

    if count == 0:
        return {"deleted": 0, "message": "Geen chunks gevonden"}

    # Delete points
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"http://localhost:6333/collections/{collection}/points/delete",
                json={"filter": {"must": [{"key": "source_file", "match": {"value": source_key}}]}},
            )
            if r.status_code == 200:
                return {"deleted": count, "collection": collection, "source_key": source_key}
            else:
                return JSONResponse(
                    {"error": f"Qdrant returned {r.status_code}: {r.text[:200]}"},
                    status_code=500,
                )
    except Exception as e:
        return JSONResponse({"error": str(e)[:300]}, status_code=500)


# ── GET /library/ingest ────────────────────────────────────────────────────────

@app.get("/library/ingest", response_class=HTMLResponse)
async def library_ingest_page():
    sections = "".join(_library_section_html(sec) for sec in SECTION_MAP)

    body = f"""
<div class="wrap">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:10px">
    <h1 style="font-size:22px;font-weight:700">Bibliotheek — Upload</h1>
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <a href="/library" class="btn btn-secondary">← Catalogus</a>
      <a href="/library/overview" class="btn btn-secondary">Literatuuroverzicht</a>
      <span style="font-size:13px;color:#6b7280">→ alle boeken in <code>medical_library</code></span>
    </div>
  </div>
  <div id="book-progress" style="margin-bottom:16px"></div>

  <!-- Claude Retroaudit widget -->
  <div id="retroaudit-widget" style="margin-bottom:20px;display:none">
    <div class="section">
      <div class="section-head" style="display:flex;align-items:center;justify-content:space-between">
        <span class="section-title">Claude Retroaudit</span>
        <button id="ra-start-btn" onclick="retroauditStart()"
          style="padding:7px 16px;background:#1A6B72;color:#fff;border:none;
                 border-radius:7px;font-size:13px;font-weight:600;cursor:pointer">
          Nu uitvoeren
        </button>
      </div>
      <div style="padding:16px 20px">
        <!-- summary bar -->
        <div id="ra-summary" style="display:flex;gap:24px;flex-wrap:wrap;font-size:13px;color:#374151;margin-bottom:12px">
          <span id="ra-status-label" style="font-weight:600;color:#6b7280">Gereed</span>
          <span id="ra-found"  style="display:none">Gevonden: <b id="ra-found-n">0</b></span>
          <span id="ra-done"   style="display:none">Getagd: <b id="ra-done-n">0</b></span>
          <span id="ra-errors" style="display:none">Fouten: <b id="ra-errors-n">0</b></span>
          <span id="ra-book"   style="display:none;color:#6b7280">Bezig:
            <span id="ra-book-title" style="font-weight:500;color:#374151"></span>
            <span id="ra-book-name"  style="font-size:11px;color:#9ca3af;font-family:monospace;margin-left:4px"></span>
          </span>
        </div>
        <!-- progress bar -->
        <div id="ra-progress-wrap" style="display:none;margin-bottom:12px">
          <div style="height:8px;background:#e5e7eb;border-radius:4px;overflow:hidden">
            <div id="ra-progress-bar"
              style="height:100%;background:#1A6B72;border-radius:4px;width:0%;transition:width .4s"></div>
          </div>
        </div>
        <!-- per-book table -->
        <div id="ra-books-wrap" style="display:none">
          <table style="width:100%;font-size:12px;border-collapse:collapse">
            <thead>
              <tr style="background:#ddf2f3;color:#085041">
                <th style="padding:6px 10px;text-align:left;background:#1A6B72;color:#fff;border-radius:4px 0 0 0">Boek</th>
                <th style="padding:6px 10px;text-align:right;background:#1A6B72;color:#fff">Getagd</th>
                <th style="padding:6px 10px;text-align:right;background:#1A6B72;color:#fff;border-radius:0 4px 0 0">Fouten</th>
              </tr>
            </thead>
            <tbody id="ra-books-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

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
    const _imgChk = document.getElementById('enable-images-' + category);
    fd.append('enable_images', _imgChk ? (_imgChk.checked ? 'true' : 'false') : 'true');
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

// ── Heraudit (retroactive chunk audit) ──────────────────────────────────────
const _raJobs    = {{}};
const _raPollers = {{}};

async function reauditBook(filename) {{
  const safeId = filename.replace(/[^a-zA-Z0-9]/g, '_');
  const el = document.getElementById('ra-' + safeId);
  if (el) {{ el.style.color = '#6b7280'; el.textContent = 'Bezig…'; }}
  try {{
    const r = await fetch('/library/reaudit/' + encodeURIComponent(filename), {{method: 'POST'}});
    const d = await r.json();
    if (d.job_id) {{
      _raJobs[filename]    = d.job_id;
      _raPollers[filename] = setInterval(() => pollReaudit(filename), 2000);
    }} else {{
      if (el) {{ el.style.color = '#dc2626'; el.textContent = 'Fout: ' + (d.error || 'onbekend'); }}
    }}
  }} catch(e) {{
    if (el) {{ el.style.color = '#dc2626'; el.textContent = 'Fout: ' + e; }}
  }}
}}

async function pollReaudit(filename) {{
  const safeId = filename.replace(/[^a-zA-Z0-9]/g, '_');
  const el     = document.getElementById('ra-' + safeId);
  const jobId  = _raJobs[filename];
  if (!jobId) return;
  try {{
    const r = await fetch('/library/reaudit/status/' + jobId);
    const d = await r.json();
    if (d.status === 'done') {{
      clearInterval(_raPollers[filename]);
      if (el) {{ el.style.color = '#059669'; el.textContent = '✓ ' + (d.result || ''); }}
    }} else if (d.status === 'error') {{
      clearInterval(_raPollers[filename]);
      if (el) {{ el.style.color = '#dc2626'; el.textContent = 'Fout: ' + (d.error || ''); }}
    }} else {{
      if (el) {{ el.style.color = '#6b7280'; el.textContent = d.progress || 'Bezig…'; }}
    }}
  }} catch(e) {{ /* ignore poll errors */ }}
}}

// ── Global Claude Retroaudit widget ──────────────────────────────────────────
let _raGlobalPoller = null;
let _raFinishedAt   = null;

async function retroauditStart() {{
  const btn = document.getElementById('ra-start-btn');
  btn.disabled = true;
  btn.textContent = 'Starten\u2026';
  try {{
    const r = await fetch('/api/retroaudit/start', {{method:'POST'}});
    const d = await r.json();
    if (!d.ok) {{
      alert('Kan niet starten: ' + (d.error || 'onbekend'));
      btn.disabled = false;
      btn.textContent = 'Nu uitvoeren';
      return;
    }}
  }} catch(e) {{
    alert('Netwerkfout: ' + e);
    btn.disabled = false;
    btn.textContent = 'Nu uitvoeren';
    return;
  }}
  startRetroauditPolling();
}}

function startRetroauditPolling() {{
  if (_raGlobalPoller) clearInterval(_raGlobalPoller);
  _raGlobalPoller = setInterval(pollRetroaudit, 5000);
  pollRetroaudit();
}}

async function pollRetroaudit() {{
  try {{
    const r = await fetch('/api/retroaudit/status');
    const d = await r.json();
    renderRetroauditState(d);
  }} catch(e) {{ /* ignore */ }}
}}

function renderRetroauditState(d) {{
  const widget = document.getElementById('retroaudit-widget');
  widget.style.display = 'block';

  const btn   = document.getElementById('ra-start-btn');
  const label = document.getElementById('ra-status-label');

  if (d.running) {{
    btn.disabled = true;
    btn.textContent = 'Bezig\u2026';
    label.textContent = 'Bezig\u2026';
    label.style.color = '#1A6B72';
  }} else if (d.error) {{
    btn.disabled = false;
    btn.textContent = 'Nu uitvoeren';
    label.textContent = '\u2717 Fout: ' + d.error;
    label.style.color = '#dc2626';
    if (_raGlobalPoller) {{ clearInterval(_raGlobalPoller); _raGlobalPoller = null; }}
  }} else if (d.finished_at) {{
    btn.disabled = false;
    btn.textContent = 'Nu uitvoeren';
    label.textContent = '\u2713 Klaar';
    label.style.color = '#059669';
    if (_raGlobalPoller) {{ clearInterval(_raGlobalPoller); _raGlobalPoller = null; }}
    // hide widget after 60s if no new run
    if (d.finished_at !== _raFinishedAt) {{
      _raFinishedAt = d.finished_at;
      setTimeout(() => {{
        if (!_retroauditRunning()) widget.style.display = 'none';
      }}, 60000);
    }}
  }} else {{
    label.textContent = 'Gereed';
    label.style.color = '#6b7280';
    btn.disabled = false;
    btn.textContent = 'Nu uitvoeren';
  }}

  // found / done / errors
  const total = d.total_found || 0;
  const done  = d.total_done  || 0;

  _setVis('ra-found',  total > 0);
  _setVis('ra-done',   total > 0);
  _setVis('ra-errors', (d.total_errors || 0) > 0);
  _setVis('ra-book',   d.running && d.current_book);

  document.getElementById('ra-found-n').textContent  = total;
  document.getElementById('ra-done-n').textContent   = done;
  document.getElementById('ra-errors-n').textContent = d.total_errors || 0;
  document.getElementById('ra-book-title').textContent = d.current_book_title || d.current_book || '';
  document.getElementById('ra-book-name').textContent  = (d.current_book_title && d.current_book_title !== d.current_book) ? d.current_book : '';

  // progress bar
  const pctWrap = document.getElementById('ra-progress-wrap');
  const bar     = document.getElementById('ra-progress-bar');
  if (total > 0) {{
    pctWrap.style.display = 'block';
    bar.style.width = Math.round(done / total * 100) + '%';
  }} else {{
    pctWrap.style.display = 'none';
  }}

  // per-book table
  const books = d.books_done || [];
  const tbody = document.getElementById('ra-books-tbody');
  const bwrap = document.getElementById('ra-books-wrap');
  if (books.length) {{
    bwrap.style.display = 'block';
    tbody.innerHTML = books.map(b =>
      '<tr style="border-bottom:1px solid #f3f4f6">'
      + '<td style="padding:5px 10px">'
      + '<span style="font-weight:500;color:#111">' + escHtml(b.book_title || b.book) + '</span>'
      + ((b.book_title && b.book_title !== b.book)
          ? '<br><span style="font-size:10px;color:#9ca3af;font-family:monospace">' + escHtml(b.book) + '</span>'
          : '')
      + '</td>'
      + '<td style="padding:5px 10px;text-align:right;color:#059669">' + b.scored + '</td>'
      + '<td style="padding:5px 10px;text-align:right;color:' + (b.errors ? '#dc2626' : '#6b7280') + '">' + b.errors + '</td>'
      + '</tr>'
    ).join('');
  }} else {{
    bwrap.style.display = 'none';
  }}
}}

function _retroauditRunning() {{
  return document.getElementById('ra-start-btn').textContent.startsWith('Bezig');
}}

function _setVis(id, show) {{
  document.getElementById(id).style.display = show ? '' : 'none';
}}

function escHtml(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

// On load: fetch status once to check if Claude is enabled and show widget
(async function() {{
  try {{
    const r = await fetch('/api/retroaudit/status');
    const d = await r.json();
    // Show widget if Claude is enabled (no error about disabled)
    const settR = await fetch('/api/settings');
    const sett  = await settR.json();
    const caEnabled = (sett.claude_api || {{}}).enabled;
    if (caEnabled) {{
      document.getElementById('retroaudit-widget').style.display = 'block';
    }}
    if (d.running) startRetroauditPolling();
    else if (d.total_found > 0 || d.finished_at) renderRetroauditState(d);
  }} catch(e) {{ /* ignore */ }}
}})();
</script>""" + _BOOK_PROGRESS_SCRIPT
    return _page_shell("Importeer", "/library/ingest", body)


# ── GET /library/status/{filename} ────────────────────────────────────────────

@app.get("/library/status/{filename}")
async def library_status(filename: str):
    return _book_status(filename)


# ── POST /library/upload ───────────────────────────────────────────────────────

@app.post("/library/upload")
async def library_upload(
    file:          UploadFile = File(...),
    collection:    str        = Form(...),   # section key (medical_literature/nrt_qat/device)
    enable_images: str        = Form("true"),
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

    image_extraction_enabled = enable_images.lower() == "true"
    _enqueue_book(fname, str(dest), qdrant_collection, source_category, ext.lstrip("."),
                  image_extraction_enabled=image_extraction_enabled)

    return {"status": "queued", "filename": fname, "collection": qdrant_collection,
            "section": section_key, "image_extraction_enabled": image_extraction_enabled}


# ── GET /library/audit/{filename} ─────────────────────────────────────────────

@app.get("/library/audit/{filename}")
async def library_audit(filename: str):
    stem = Path(filename).stem
    audit_path = QUALITY_DIR / f"{stem}_audit.json"
    if not audit_path.exists():
        return JSONResponse({"error": "No audit report found"}, status_code=404)
    return json.loads(audit_path.read_text())


# ── GET /api/settings ─────────────────────────────────────────────────────────

SETTINGS_PATH = BASE / "config" / "settings.json"

def _load_settings_cfg() -> dict:
    try:
        return json.loads(SETTINGS_PATH.read_text())
    except Exception:
        return {}

def _save_settings_cfg(data: dict) -> None:
    tmp = SETTINGS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tmp.replace(SETTINGS_PATH)

@app.get("/api/settings")
async def api_settings_get():
    cfg = _load_settings_cfg()
    # Mask API key — show only last 6 chars in UI
    api_key = (cfg.get("claude_api") or {}).get("api_key", "")
    masked  = ("●" * (len(api_key) - 6) + api_key[-6:]) if len(api_key) > 6 else ("●" * len(api_key))
    if cfg.get("claude_api"):
        cfg["claude_api"]["api_key_masked"] = masked
        cfg["claude_api"]["api_key_set"]    = bool(api_key or os.environ.get("ANTHROPIC_API_KEY"))
    # Vision credentials status
    cfg["vision_credentials_missing"] = not (BASE / "config" / "google_vision_key.json").exists()
    # Ensure google_vision section has defaults for UI even if not in settings.json
    gv_defaults = {
        "dpi": 300, "language_hints": ["en"], "min_words_per_page": 1,
        "max_workers": 8, "enable_confidence_scores": False,
        "confidence_threshold": 0.0, "advanced_ocr_options": [],
    }
    gv_defaults.update(cfg.get("google_vision") or {})
    cfg["google_vision"] = gv_defaults
    return cfg

@app.post("/api/settings")
async def api_settings_post(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    current = _load_settings_cfg()

    # Deep merge — only update known top-level sections
    for section in ("claude_api", "nightly", "google_vision"):
        if section in body and isinstance(body[section], dict):
            if section not in current:
                current[section] = {}
            for k, v in body[section].items():
                if k not in ("api_key_masked", "api_key_set"):  # never write derived fields
                    current[section][k] = v

    _save_settings_cfg(current)
    return {"ok": True}

@app.post("/api/settings/test-claude")
async def api_settings_test_claude():
    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE / "scripts"))
        from claude_audit import get_client, load_settings
        import time

        s   = load_settings()
        cfg = s.get("claude_api", {})

        # Resolve key — settings first, env fallback
        key = cfg.get("api_key", "").strip() or os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            return JSONResponse({"ok": False, "error": "Geen API key geconfigureerd"})

        import anthropic
        client = anthropic.Anthropic(api_key=key)
        model  = cfg.get("model", "claude-haiku-4-5-20251001")

        t0 = time.time()
        resp = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Reply with the single word: OK"}],
        )
        latency_ms = round((time.time() - t0) * 1000)
        return {
            "ok":         True,
            "model":      model,
            "latency_ms": latency_ms,
            "response":   resp.content[0].text.strip(),
        }
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)[:200]})


# ── GET /api/pipeline-diagrams ────────────────────────────────────────────────

PIPELINE_DIAGRAMS_PATH = BASE / "config" / "pipeline_diagrams.json"


def _load_pipeline_diagrams() -> dict:
    """Load pipeline_diagrams.json and overlay live settings values."""
    try:
        data = json.loads(PIPELINE_DIAGRAMS_PATH.read_text())
    except Exception:
        data = {}

    live = _load_settings_cfg()
    n  = live.get("nightly", {})
    ca = live.get("claude_api", {})

    data.setdefault("nightly", {})
    data.setdefault("audit", {})
    data["audit"].setdefault("primary", {})
    data["audit"].setdefault("fallback", {})
    data["audit"].setdefault("retroaudit", {})

    # Overlay live nightly settings
    data["nightly"]["start_time"]         = n.get("start_time",        data["nightly"].get("start_time", "00:00"))
    data["nightly"]["end_time"]           = n.get("end_time",          data["nightly"].get("end_time",   "07:00"))
    data["nightly"]["image_screen_limit"] = n.get("image_screen_limit",data["nightly"].get("image_screen_limit", 200))

    # Overlay live audit settings
    workers = ca.get("max_workers", data["audit"]["primary"].get("workers", 10))
    enabled = ca.get("enabled", False)
    data["audit"]["enabled"]                  = enabled
    data["audit"]["primary"]["model"]         = ca.get("model", data["audit"]["primary"].get("model", "claude-haiku-4-5-20251001"))
    data["audit"]["primary"]["workers"]       = workers
    data["audit"]["primary"]["enabled"]       = enabled
    data["audit"]["primary"]["subtitle"]      = f"{workers} workers parallel"

    # Keep retroaudit notes in sync with nightly window
    start = data["nightly"]["start_time"]
    end   = data["nightly"]["end_time"]
    data["audit"]["retroaudit"]["ollama_note"]   = f"{start}\u2013{end} Amsterdam"
    data["audit"]["retroaudit"]["ollama_window"] = f"{start}\u2013{end} Amsterdam"  # backward compat

    # Overlay live nightly stats (sec/chunk, sec/image)
    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE / "scripts"))
        from nightly_stats import get_stats_summary as _gss
        data["nightly_stats"] = _gss()
    except Exception:
        data["nightly_stats"] = {
            "sec_per_chunk":      6.0,
            "sec_per_image":      8.0,
            "retroaudit_samples": 0,
            "image_samples":      0,
        }

    return data


@app.get("/api/pipeline-diagrams")
async def api_pipeline_diagrams():
    return JSONResponse(_load_pipeline_diagrams())


@app.get("/api/pipeline-diagrams/refresh")
async def api_pipeline_diagrams_refresh():
    """Re-extract constants from parse_pdf.py and update pipeline_diagrams.json."""
    import importlib.util as _ilu
    min_ocr = 10
    native_threshold = 15
    try:
        spec = _ilu.spec_from_file_location("parse_pdf", BASE / "scripts" / "parse_pdf.py")
        mod  = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        min_ocr          = getattr(mod, "MIN_OCR_WORDS",    min_ocr)
        native_threshold = getattr(mod, "NATIVE_THRESHOLD", native_threshold)
    except Exception:
        pass

    try:
        data = json.loads(PIPELINE_DIAGRAMS_PATH.read_text())
    except Exception:
        data = {}

    data.setdefault("pdf_type_detection", {})
    data.setdefault("ocr_cascade", {})
    data["pdf_type_detection"]["threshold_words_native"] = 50
    data["pdf_type_detection"]["threshold_words_low"]    = native_threshold
    # backward compat aliases
    data["pdf_type_detection"]["threshold_words_per_page_native"] = 50
    data["pdf_type_detection"]["threshold_words_per_page_low"]    = native_threshold
    data["ocr_cascade"]["min_words_threshold"]                    = min_ocr
    data["updated_at"]  = datetime.now(timezone.utc).isoformat()
    data["updated_by"]  = "Claude Code — auto-refresh"

    PIPELINE_DIAGRAMS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return JSONResponse(_load_pipeline_diagrams())


# ── GET /settings ──────────────────────────────────────────────────────────────

@app.get("/settings", response_class=HTMLResponse)
async def settings_page():
    body = """
<div class="wrap">
  <h1 style="font-size:22px;font-weight:700;margin-bottom:20px;color:#111">Instellingen</h1>

  <!-- Tab bar -->
  <div style="display:flex;gap:0;border-bottom:1px solid #e5e7eb;margin-bottom:24px;max-width:880px">
    <button type="button" id="tab-params" onclick="switchSettingsTab('params')"
      style="padding:10px 22px;border:none;background:none;cursor:pointer;font-size:14px;
             font-weight:600;color:#1A6B72;border-bottom:2px solid #1A6B72;margin-bottom:-1px">
      Parameters
    </button>
    <button type="button" id="tab-schemas" onclick="switchSettingsTab('schemas')"
      style="padding:10px 22px;border:none;background:none;cursor:pointer;font-size:14px;
             font-weight:400;color:#6b7280;border-bottom:2px solid transparent;margin-bottom:-1px">
      Schema's
    </button>
  </div>

  <!-- TAB 1: Parameters -->
  <div id="pane-params">

    <!-- Claude API card -->
    <div class="section" style="max-width:680px;margin-bottom:24px">
      <div class="section-head">
        <span class="section-title">Claude API audit</span>
        <span id="claude-status-badge" style="font-size:12px;color:#6b7280"></span>
      </div>
      <div style="padding:20px 24px;display:flex;flex-direction:column;gap:18px">

        <!-- API key row -->
        <div>
          <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">API key</label>
          <div style="display:flex;gap:8px;align-items:center">
            <input id="api-key-input" type="password" placeholder="sk-ant-api03-\u2026"
              style="flex:1;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;
                     font-size:13px;font-family:monospace;color:#111">
            <button onclick="testClaude()"
              style="padding:9px 16px;background:#1A6B72;color:#fff;border:none;
                     border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;
                     white-space:nowrap">
              Testen
            </button>
          </div>
          <div id="test-result" style="margin-top:6px;font-size:12px;color:#6b7280"></div>
        </div>

        <!-- Enabled toggle -->
        <div style="display:flex;align-items:center;justify-content:space-between">
          <div>
            <div style="font-size:13px;font-weight:600;color:#374151">Ingeschakeld</div>
            <div style="font-size:12px;color:#6b7280;margin-top:2px">
              Vervangt Ollama voor chunk-tagging. Geen nachtlimiet bij retroaudit.
            </div>
          </div>
          <label style="position:relative;display:inline-block;width:44px;height:24px">
            <input id="enabled-toggle" type="checkbox" style="opacity:0;width:0;height:0"
              onchange="toggleChanged()">
            <span id="toggle-slider"
              style="position:absolute;cursor:pointer;inset:0;border-radius:12px;
                     background:#d1d5db;transition:.2s">
              <span id="toggle-thumb"
                style="position:absolute;width:18px;height:18px;border-radius:50%;
                       background:#fff;top:3px;left:3px;transition:.2s;
                       box-shadow:0 1px 3px rgba(0,0,0,.3)"></span>
            </span>
          </label>
        </div>

        <!-- Model + Workers -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
          <div>
            <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">Model</label>
            <select id="model-select"
              style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;
                     font-size:13px;color:#111;background:#fff">
              <option value="claude-haiku-4-5-20251001">claude-haiku-4-5 (snel)</option>
              <option value="claude-sonnet-4-6">claude-sonnet-4-6 (beter)</option>
            </select>
          </div>
          <div>
            <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">Parallelle workers</label>
            <input id="workers-input" type="number" min="1" max="50" value="10"
              style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;
                     font-size:13px;color:#111">
          </div>
        </div>

        <!-- Save button -->
        <div style="display:flex;justify-content:flex-end;padding-top:4px">
          <button onclick="saveSettings()"
            style="padding:10px 24px;background:#1A6B72;color:#fff;border:none;
                   border-radius:8px;font-size:14px;font-weight:600;cursor:pointer">
            Opslaan
          </button>
        </div>
      </div>
    </div>

    <!-- Nightly limits card -->
    <div class="section" style="max-width:680px">
      <div class="section-head">
        <span class="section-title">Nachtelijke onderhoud</span>
      </div>
      <div style="padding:20px 24px;display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <div>
          <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">
            Nachtrun start (Amsterdam)
          </label>
          <input id="nightly-start" type="time" value="02:00"
            style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:13px">
        </div>
        <div>
          <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">
            Nachtrun einde (Amsterdam)
          </label>
          <input id="nightly-end" type="time" value="05:00"
            style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:13px">
        </div>
        <div>
          <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">
            Afbeelding screening/nacht
          </label>
          <input id="image-limit" type="number" min="50" max="2000" value="200"
            style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:13px">
        </div>
        <div style="grid-column:1/-1;display:flex;justify-content:flex-end">
          <button onclick="saveNightly()"
            style="padding:10px 24px;background:#1A6B72;color:#fff;border:none;
                   border-radius:8px;font-size:14px;font-weight:600;cursor:pointer">
            Opslaan
          </button>
        </div>
      </div>
    </div>

    <!-- Google Vision card -->
    <div class="section" style="max-width:680px">
      <div class="section-head">
        <span class="section-title">Google Vision OCR</span>
      </div>
      <div id="vision-creds-banner" style="display:none;margin:16px 24px 0;padding:12px 16px;
           background:#fef3c7;border:1px solid #d97706;border-radius:8px;font-size:13px;color:#92400e">
        &#9888; <strong>Credentials ontbreken</strong> — <code>config/google_vision_key.json</code>
        niet aanwezig. Google Vision wordt overgeslagen; RapidOCR neemt over als fallback.
      </div>
      <div style="padding:20px 24px;display:grid;grid-template-columns:1fr 1fr;gap:16px">
        <div>
          <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">
            DPI (72\u2013600, stap 50)
          </label>
          <input id="vision-dpi" type="number" min="72" max="600" step="50" value="300"
            style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:13px">
        </div>
        <div>
          <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">
            Language hints (komma-gescheiden)
          </label>
          <input id="vision-language-hints" type="text" value="en"
            style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:13px">
        </div>
        <div>
          <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">
            Min. woorden per pagina
          </label>
          <input id="vision-min-words" type="number" min="0" max="50" value="1"
            style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:13px">
        </div>
        <div>
          <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">
            Parallelle verzoeken (1\u201316)
          </label>
          <input id="vision-max-workers" type="number" min="1" max="16" value="8"
            style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:13px">
        </div>
        <div style="display:flex;align-items:center;gap:10px">
          <label style="font-size:13px;font-weight:600;color:#374151">
            Confidence scores inschakelen
          </label>
          <input id="vision-confidence-toggle" type="checkbox"
            onchange="document.getElementById('vision-confidence-row').style.display=this.checked?'block':'none'"
            style="width:16px;height:16px;cursor:pointer">
        </div>
        <div>
          <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">
            Advanced OCR opties (komma-gescheiden)
          </label>
          <input id="vision-advanced-options" type="text" placeholder="bijv. TEXT_DETECTION"
            style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:13px">
        </div>
        <div id="vision-confidence-row" style="display:none">
          <label style="font-size:13px;font-weight:600;color:#374151;display:block;margin-bottom:6px">
            Confidence drempel (0.0\u20131.0)
          </label>
          <input id="vision-confidence-threshold" type="number" min="0" max="1" step="0.05" value="0.0"
            style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:13px">
        </div>
        <div style="grid-column:1/-1;display:flex;justify-content:flex-end">
          <button onclick="saveVision()"
            style="padding:10px 24px;background:#1A6B72;color:#fff;border:none;
                   border-radius:8px;font-size:14px;font-weight:600;cursor:pointer">
            Opslaan
          </button>
        </div>
      </div>
    </div>

  </div><!-- /pane-params -->

  <!-- TAB 2: Schema's -->
  <div id="pane-schemas" style="display:none;max-width:880px">
    <div id="diagrams-container">
      <div style="color:#6b7280;font-size:13px;padding:20px 0">Schema's laden\u2026</div>
    </div>
  </div>

</div><!-- /wrap -->

<script>
// ═══════════════════════════════════════════════════════════
// TAB SWITCHING
// ═══════════════════════════════════════════════════════════
function switchSettingsTab(tab) {
  ['params','schemas'].forEach(t => {
    document.getElementById('pane-' + t).style.display = t === tab ? 'block' : 'none';
    const btn = document.getElementById('tab-' + t);
    const active = t === tab;
    btn.style.fontWeight     = active ? '600' : '400';
    btn.style.color          = active ? '#1A6B72' : '#6b7280';
    btn.style.borderBottom   = active ? '2px solid #1A6B72' : '2px solid transparent';
  });
  if (tab === 'schemas' && !window._diagramsLoaded) loadDiagrams();
}

// ═══════════════════════════════════════════════════════════
// PARAMETERS TAB — existing settings functions
// ═══════════════════════════════════════════════════════════
let _settings = {};

async function loadSettings() {
  try {
    const r = await fetch('/api/settings');
    _settings = await r.json();
    const ca = _settings.claude_api || {};
    const n  = _settings.nightly    || {};

    if (ca.api_key_set) {
      document.getElementById('api-key-input').placeholder =
        ca.api_key_masked || '\u25cf\u25cf\u25cf\u25cf (opgeslagen)';
      updateStatus('\u2713 API key aanwezig', '#059669');
    } else {
      updateStatus('Geen API key', '#6b7280');
    }
    const tog = document.getElementById('enabled-toggle');
    tog.checked = ca.enabled || false;
    refreshToggleUI(tog.checked);

    const sel = document.getElementById('model-select');
    if (ca.model) { sel.value = ca.model; if (!sel.value) sel.value = 'claude-haiku-4-5-20251001'; }
    if (ca.max_workers) document.getElementById('workers-input').value = ca.max_workers;

    if (n.start_time) document.getElementById('nightly-start').value = n.start_time;
    if (n.end_time)   document.getElementById('nightly-end').value   = n.end_time;
    if (n.image_screen_limit) document.getElementById('image-limit').value = n.image_screen_limit;

    const gv = _settings.google_vision || {};
    if (gv.dpi !== undefined)  document.getElementById('vision-dpi').value = gv.dpi;
    if (gv.language_hints)     document.getElementById('vision-language-hints').value = gv.language_hints.join(',');
    if (gv.min_words_per_page !== undefined) document.getElementById('vision-min-words').value = gv.min_words_per_page;
    if (gv.max_workers !== undefined)        document.getElementById('vision-max-workers').value = gv.max_workers;
    const confToggle = document.getElementById('vision-confidence-toggle');
    confToggle.checked = !!gv.enable_confidence_scores;
    document.getElementById('vision-confidence-row').style.display = confToggle.checked ? 'block' : 'none';
    if (gv.confidence_threshold !== undefined) document.getElementById('vision-confidence-threshold').value = gv.confidence_threshold;
    if (gv.advanced_ocr_options) document.getElementById('vision-advanced-options').value = (gv.advanced_ocr_options || []).join(',');
    if (_settings.vision_credentials_missing) {
      document.getElementById('vision-creds-banner').style.display = 'block';
    }
  } catch(e) { console.error('loadSettings failed:', e); }
}

function updateStatus(msg, color) {
  const el = document.getElementById('claude-status-badge');
  el.textContent = msg; el.style.color = color;
}
function toggleChanged() { refreshToggleUI(document.getElementById('enabled-toggle').checked); }
function refreshToggleUI(on) {
  document.getElementById('toggle-slider').style.background = on ? '#1A6B72' : '#d1d5db';
  document.getElementById('toggle-thumb').style.left = on ? '23px' : '3px';
}

async function testClaude() {
  const btn = document.querySelector('button[onclick="testClaude()"]');
  const res = document.getElementById('test-result');
  btn.disabled = true; btn.textContent = 'Testen\u2026'; res.textContent = '';
  const keyVal = document.getElementById('api-key-input').value.trim();
  if (keyVal && keyVal !== '\u25cf\u25cf\u25cf\u25cf (opgeslagen)') {
    await fetch('/api/settings', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({claude_api: {api_key: keyVal}})});
  }
  try {
    const r = await fetch('/api/settings/test-claude', {method:'POST'});
    const d = await r.json();
    if (d.ok) {
      res.textContent = '\u2713 Verbonden \u00b7 ' + d.model + ' \u00b7 ' + d.latency_ms + 'ms';
      res.style.color = '#059669';
      updateStatus('\u2713 Verbonden \u00b7 ' + d.model, '#059669');
    } else {
      res.textContent = '\u2717 ' + (d.error || 'Onbekende fout');
      res.style.color = '#dc2626';
      updateStatus('Verbindingsfout', '#dc2626');
    }
  } catch(e) { res.textContent = 'Netwerkfout: ' + e; res.style.color = '#dc2626'; }
  btn.disabled = false; btn.textContent = 'Testen';
}

async function saveSettings() {
  const keyVal = document.getElementById('api-key-input').value.trim();
  const payload = { claude_api: {
    enabled:     document.getElementById('enabled-toggle').checked,
    model:       document.getElementById('model-select').value,
    max_workers: parseInt(document.getElementById('workers-input').value) || 10,
  }};
  if (keyVal && !keyVal.startsWith('\u25cf')) payload.claude_api.api_key = keyVal;
  const r = await fetch('/api/settings', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)});
  const d = await r.json();
  if (d.ok) { showToast('Opgeslagen'); await loadSettings(); }
  else showToast('Fout: ' + JSON.stringify(d), true);
}

async function saveNightly() {
  const payload = { nightly: {
    start_time:         document.getElementById('nightly-start').value || '02:00',
    end_time:           document.getElementById('nightly-end').value   || '05:00',
    image_screen_limit: parseInt(document.getElementById('image-limit').value) || 200,
  }};
  const r = await fetch('/api/settings', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)});
  const d = await r.json();
  showToast(d.ok ? 'Opgeslagen' : 'Fout');
}

async function saveVision() {
  const hintsRaw = document.getElementById('vision-language-hints').value.trim();
  const advRaw   = document.getElementById('vision-advanced-options').value.trim();
  const confEnabled = document.getElementById('vision-confidence-toggle').checked;
  const payload = { google_vision: {
    dpi:                    parseInt(document.getElementById('vision-dpi').value) || 300,
    language_hints:         hintsRaw ? hintsRaw.split(',').map(s => s.trim()).filter(Boolean) : ['en'],
    min_words_per_page:     parseInt(document.getElementById('vision-min-words').value) || 1,
    max_workers:            parseInt(document.getElementById('vision-max-workers').value) || 8,
    enable_confidence_scores: confEnabled,
    confidence_threshold:   parseFloat(document.getElementById('vision-confidence-threshold').value) || 0.0,
    advanced_ocr_options:   advRaw ? advRaw.split(',').map(s => s.trim()).filter(Boolean) : [],
  }};
  const r = await fetch('/api/settings', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)});
  const d = await r.json();
  showToast(d.ok ? 'Opgeslagen' : 'Fout');
}

function showToast(msg, isError) {
  const t = document.createElement('div');
  t.textContent = msg;
  t.style.cssText = 'position:fixed;bottom:24px;right:24px;padding:10px 18px;'
    + 'border-radius:8px;font-size:13px;font-weight:600;color:#fff;z-index:9999;'
    + 'background:' + (isError ? '#dc2626' : '#059669');
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2800);
}

// ═══════════════════════════════════════════════════════════
// DIAGRAM RENDERER — HYBRID (CSS/flexbox + SVG connectors)
// ═══════════════════════════════════════════════════════════
const COLORS = {
  teal:   {bg:'#e8f4f5', bd:'#1A6B72', tx:'#085041'},
  green:  {bg:'#dcfce7', bd:'#16a34a', tx:'#166534'},
  amber:  {bg:'#fef3c7', bd:'#d97706', tx:'#78350f'},
  purple: {bg:'#EEEDFE', bd:'#534AB7', tx:'#3C3489'},
  red:    {bg:'#fee2e2', bd:'#dc2626', tx:'#991b1b'},
  gray:   {bg:'#f3f4f6', bd:'#d1d5db', tx:'#6b7280'},
};

let _nuTimer = null;

async function loadDiagrams() {
  const cont = document.getElementById('diagrams-container');
  try {
    const r = await fetch('/api/pipeline-diagrams');
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const d = await r.json();
    try {
      renderPipelineDiagrams(d);
    } catch(re) {
      console.error('renderPipelineDiagrams error:', re);
      cont.innerHTML = '<div style="color:#92400e;background:#fef3c7;padding:12px 16px;'
        + 'border-radius:8px;font-size:13px">Diagram render fout: ' + re.message + '</div>';
    }
    window._diagramsLoaded = true;
  } catch(e) {
    console.error('loadDiagrams error:', e);
    if (cont) cont.innerHTML = '<div style="color:#92400e;background:#fef3c7;padding:12px 16px;'
      + 'border-radius:8px;font-size:13px">Diagrammen tijdelijk niet beschikbaar: ' + e.message + '</div>';
  }
}

function renderPipelineDiagrams(d) {
  const c = document.getElementById('diagrams-container');
  c.innerHTML = '';
  c.appendChild(dCard('A. 24-uurs tijdlijn', renderTimeline(d)));
  c.appendChild(dCard('B. Boekimport pipeline', renderImportFlow(d)));
  c.appendChild(dCard('C. OCR engine cascade', renderOcrCascade(d)));
  c.appendChild(dCard('D. Audit engine selectie', renderAuditSelection(d)));
  c.appendChild(dCard('E. Nachtrun fasen', renderNightlyPhases(d)));
}

function dCard(title, contentEl) {
  const wrap = document.createElement('div');
  wrap.className = 'section';
  wrap.style.marginBottom = '20px';
  const head = document.createElement('div');
  head.className = 'section-head';
  const t = document.createElement('span');
  t.className = 'section-title'; t.textContent = title;
  head.appendChild(t);
  wrap.appendChild(head);
  const body = document.createElement('div');
  body.style.padding = '20px 24px';
  body.appendChild(contentEl);
  wrap.appendChild(body);
  return wrap;
}

// ─── A. 24-uurs tijdlijn ───────────────────────────────────
function hmToMin(hm) {
  const [h, m] = (hm || '00:00').split(':').map(Number);
  return h * 60 + m;
}
function minToPct(min) { return (min / 1440 * 100).toFixed(3) + '%'; }

function renderTimeline(d) {
  const n = d.nightly || {};
  const startMin = hmToMin(n.start_time || '00:00');
  const endMin   = hmToMin(n.end_time   || '07:00');
  const startHm  = n.start_time || '00:00';
  const endHm    = n.end_time   || '07:00';
  const claudeOn = (d.audit || {}).enabled || false;

  const outer = document.createElement('div');
  outer.style.cssText = 'width:100%;overflow-x:auto';

  // Hour labels: 00:00 / 06:00 / 12:00 / 18:00 / 24:00
  const lblRow = document.createElement('div');
  lblRow.style.cssText = 'position:relative;height:18px;margin-bottom:6px;margin-left:130px';
  [0,6,12,18,24].forEach(h => {
    const s = document.createElement('span');
    s.textContent = (h === 0 || h === 24) ? h + ':00' : h + ':00';
    s.style.cssText = 'position:absolute;font-size:10px;color:#9ca3af;transform:translateX(-50%)';
    s.style.left = (h / 24 * 100) + '%';
    lblRow.appendChild(s);
  });
  outer.appendChild(lblRow);

  const processes = [
    { label: 'Boekverwerking', colorKey: 'teal',   pauseAmber: true },
    { label: "Video's",        colorKey: 'teal',   pauseAmber: true },
    { label: 'Nachtrun',       colorKey: 'amber',  fixed: [startMin, endMin] },
    { label: 'Claude API',     colorKey: claudeOn ? 'purple' : 'gray',
      fixed: claudeOn ? [0, 1440] : null, inactive: !claudeOn },
  ];

  const grid = document.createElement('div');
  grid.style.cssText = 'display:flex;flex-direction:column;gap:4px';

  processes.forEach(proc => {
    const row = document.createElement('div');
    row.style.cssText = 'display:flex;align-items:center;height:26px';

    const lbl = document.createElement('div');
    lbl.textContent = proc.label;
    lbl.style.cssText = 'width:130px;font-size:11px;color:#4a5568;flex-shrink:0;padding-right:8px;text-align:right';
    row.appendChild(lbl);

    const barWrap = document.createElement('div');
    barWrap.style.cssText = 'flex:1;position:relative;height:20px;background:#f3f4f6;border-radius:3px;overflow:hidden';

    const C = COLORS[proc.colorKey] || COLORS.gray;

    if (proc.inactive) {
      const bar = document.createElement('div');
      bar.style.cssText = 'position:absolute;inset:0;background:#f3f4f6;border:1px solid #d1d5db;'
        + 'border-radius:3px;display:flex;align-items:center;justify-content:center';
      bar.innerHTML = '<span style="font-size:9px;color:#9ca3af">uitgeschakeld</span>';
      barWrap.appendChild(bar);
    } else if (proc.fixed) {
      const bar = document.createElement('div');
      bar.style.cssText = 'position:absolute;top:0;bottom:0;background:' + C.bg
        + ';border:1px solid ' + C.bd + ';border-radius:3px;box-sizing:border-box';
      bar.style.left  = minToPct(proc.fixed[0]);
      bar.style.width = proc.fixed[1] === 1440 ? '100%' : minToPct(proc.fixed[1] - proc.fixed[0]);
      barWrap.appendChild(bar);
    } else {
      const bar = document.createElement('div');
      bar.style.cssText = 'position:absolute;inset:0;background:' + C.bg
        + ';border:1px solid ' + C.bd + ';border-radius:3px;box-sizing:border-box';
      barWrap.appendChild(bar);
      if (proc.pauseAmber) {
        const pause = document.createElement('div');
        pause.style.cssText = 'position:absolute;top:0;bottom:0;background:rgba(254,243,199,.75)';
        pause.style.left  = minToPct(startMin);
        pause.style.width = minToPct(endMin - startMin);
        barWrap.appendChild(pause);
      }
    }

    const nu = document.createElement('div');
    nu.className = 'nu-marker';
    nu.style.cssText = 'position:absolute;top:-2px;bottom:-2px;width:2px;background:#dc2626;z-index:5;border-radius:1px';
    barWrap.appendChild(nu);

    row.appendChild(barWrap);
    grid.appendChild(row);
  });

  outer.appendChild(grid);

  const leg = document.createElement('div');
  leg.style.cssText = 'display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;font-size:11px;color:#6b7280;align-items:center';
  leg.innerHTML = '<span style="display:inline-flex;align-items:center;gap:4px">'
    + '<span style="width:14px;height:10px;background:#e8f4f5;border:1px solid #1A6B72;border-radius:2px;display:inline-block"></span>Actief</span>'
    + '<span style="display:inline-flex;align-items:center;gap:4px">'
    + '<span style="width:14px;height:10px;background:#fef3c7;border:1px solid #d97706;border-radius:2px;display:inline-block"></span>'
    + 'Nachtrun (' + startHm + '\u2013' + endHm + ' Amsterdam)</span>'
    + '<span style="display:inline-flex;align-items:center;gap:4px">'
    + '<span style="width:2px;height:12px;background:#dc2626;display:inline-block;border-radius:1px"></span>Nu</span>';
  outer.appendChild(leg);

  updateNuLine();
  if (_nuTimer) clearInterval(_nuTimer);
  _nuTimer = setInterval(updateNuLine, 60000);

  return outer;
}

function updateNuLine() {
  const now = new Date();
  const nowMin = now.getHours() * 60 + now.getMinutes();
  const pct = minToPct(nowMin);
  document.querySelectorAll('.nu-marker').forEach(el => { el.style.left = pct; });
}

// ─── B. Boekimport pipeline ────────────────────────────────
function renderImportFlow(d) {
  const pt      = d.pdf_type_detection || {};
  const thrNat  = pt.threshold_words_native || pt.threshold_words_per_page_native || 50;
  const thrLow  = pt.threshold_words_low    || pt.threshold_words_per_page_low    || 15;
  const paths   = pt.paths || [];

  const wrap = document.createElement('div');
  wrap.style.cssText = 'overflow-x:auto';

  const flow = document.createElement('div');
  flow.style.cssText = 'display:flex;align-items:stretch;gap:0;flex-wrap:nowrap;min-width:660px';

  function stepBox(label, sub, colorKey) {
    const C = COLORS[colorKey] || COLORS.gray;
    const box = document.createElement('div');
    box.style.cssText = 'flex:1;min-width:76px;padding:10px 8px;text-align:center;'
      + 'border-radius:8px;border:1.5px solid ' + C.bd + ';background:' + C.bg + ';'
      + 'display:flex;flex-direction:column;justify-content:center';
    const nm = document.createElement('div');
    nm.textContent = label;
    nm.style.cssText = 'font-size:12px;font-weight:600;color:#111;margin-bottom:4px';
    box.appendChild(nm);
    if (sub) {
      const s = document.createElement('div');
      s.style.cssText = 'font-size:10px;color:#6b7280;white-space:pre-line;line-height:1.4';
      s.textContent = sub;
      box.appendChild(s);
    }
    return box;
  }

  function arrowEl() {
    const a = document.createElement('div');
    a.textContent = '\u2192';
    a.style.cssText = 'color:#9ca3af;font-size:16px;padding:0 3px;flex-shrink:0;display:flex;align-items:center';
    return a;
  }

  // Parse box: 3 stacked variants from JSON paths
  function parseBox() {
    const outer = document.createElement('div');
    outer.style.cssText = 'flex:1.5;min-width:116px;display:flex;flex-direction:column;'
      + 'gap:3px;justify-content:center;padding:4px 0';
    const hdr = document.createElement('div');
    hdr.textContent = 'Parse';
    hdr.style.cssText = 'font-size:11px;font-weight:700;color:#6b7280;text-align:center;margin-bottom:3px';
    outer.appendChild(hdr);
    const variants = paths.length > 0 ? paths : [
      { label:'Native',  condition:'\u2265'+thrNat+' w/p', engine:'PyMuPDF',        color:'teal'  },
      { label:'Mixed',   condition:'\u2265'+thrLow+' w/p', engine:'pdfplumber+OCR', color:'teal'  },
      { label:'Scanned', condition:'< '+thrLow+' w/p',     engine:'OCR cascade',    color:'amber' },
    ];
    variants.forEach(v => {
      const C2 = COLORS[v.color] || COLORS.gray;
      const row = document.createElement('div');
      row.style.cssText = 'padding:3px 7px;border-radius:5px;border:1px solid '
        + C2.bd + ';background:' + C2.bg;
      row.innerHTML = '<div style="font-size:10px;font-weight:600;color:' + C2.tx + '">'
        + v.label + ' <span style="font-weight:400;color:#6b7280">(' + v.condition + ')</span></div>'
        + '<div style="font-size:9px;color:#6b7280;margin-top:1px">' + v.engine + '</div>';
      outer.appendChild(row);
    });
    return outer;
  }

  flow.appendChild(stepBox('Upload', 'PDF/EPUB\\n/ingest', 'teal'));
  flow.appendChild(arrowEl());
  flow.appendChild(stepBox('Detectie', 'steekproef\\n5 pagina\\'s', 'gray'));
  flow.appendChild(arrowEl());
  flow.appendChild(parseBox());
  flow.appendChild(arrowEl());
  flow.appendChild(stepBox('Chunking', '~450 w\\nper chunk', 'teal'));
  flow.appendChild(arrowEl());
  flow.appendChild(stepBox('Audit', 'Claude/Ollama\\nK/A/I+tags', 'purple'));
  flow.appendChild(arrowEl());
  flow.appendChild(stepBox('Embedding', 'BGE-large\\n1024 dims', 'teal'));
  flow.appendChild(arrowEl());
  flow.appendChild(stepBox('Qdrant', 'medical_\\nlibrary', 'green'));

  wrap.appendChild(flow);
  return wrap;
}

// ─── C. OCR cascade (HYBRID: CSS list + SVG succes-lijn) ───
function renderOcrCascade(d) {
  const engines  = ((d.ocr_cascade || {}).engines || []).slice().sort((a,b) => a.order - b.order);
  const minWords = (d.ocr_cascade || {}).min_words_threshold || 10;

  const wrap = document.createElement('div');

  const note = document.createElement('div');
  note.style.cssText = 'font-size:12px;color:#6b7280;margin-bottom:14px';
  note.textContent = 'Elke engine wordt geprobeerd totdat \u2265' + minWords + ' woorden herkend zijn. '
    + 'Bij succes stopt de cascade.';
  wrap.appendChild(note);

  const container = document.createElement('div');
  container.style.cssText = 'display:flex;gap:0;align-items:stretch';

  // Left: CSS engine list
  const list = document.createElement('div');
  list.style.cssText = 'flex:1;display:flex;flex-direction:column;gap:0';

  const ROW_H = 52;

  engines.forEach((eng, i) => {
    const colorKey = eng.color || (eng.type === 'cloud' ? 'amber' : 'teal');
    const C = COLORS[colorKey] || COLORS.teal;
    const isFirst = i === 0;
    const isLast  = i === engines.length - 1;

    const row = document.createElement('div');
    row.style.cssText = 'display:flex;align-items:center;gap:12px;padding:10px 14px;'
      + 'height:' + ROW_H + 'px;box-sizing:border-box;'
      + 'background:' + C.bg + ';border:1px solid ' + C.bd + ';'
      + 'border-bottom:' + (isLast ? '1px' : '0px') + ' solid ' + C.bd + ';'
      + 'border-radius:' + (isFirst ? '8px 8px 0 0' : isLast ? '0 0 8px 8px' : '0');

    const num = document.createElement('div');
    num.textContent = eng.order;
    num.style.cssText = 'width:22px;height:22px;border-radius:50%;background:' + C.bd
      + ';color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;'
      + 'justify-content:center;flex-shrink:0';
    row.appendChild(num);

    const info = document.createElement('div');
    info.style.cssText = 'flex:1';
    info.innerHTML = '<div style="font-size:13px;font-weight:600;color:#111">' + eng.name + '</div>'
      + '<div style="font-size:11px;color:#6b7280;margin-top:2px">'
      + (eng.subtitle || eng.speed || '') + '</div>';
    row.appendChild(info);

    const badge = document.createElement('span');
    badge.textContent = eng.type === 'cloud' ? 'cloud' : 'local';
    badge.style.cssText = 'font-size:10px;font-weight:600;padding:2px 8px;border-radius:999px;'
      + 'background:' + C.bg + ';color:' + C.tx + ';border:1px solid ' + C.bd;
    row.appendChild(badge);

    list.appendChild(row);
  });

  container.appendChild(list);

  // Right: SVG dashed success line with arrows
  const svgW = 72;
  const totalH = engines.length * ROW_H;
  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width', svgW);
  svg.setAttribute('height', totalH);
  svg.style.cssText = 'flex-shrink:0;overflow:visible';

  // arrowhead marker
  const defs = document.createElementNS(NS, 'defs');
  const mk = document.createElementNS(NS, 'marker');
  mk.setAttribute('id', 'ag'); mk.setAttribute('markerWidth','6');
  mk.setAttribute('markerHeight','6'); mk.setAttribute('refX','5');
  mk.setAttribute('refY','3'); mk.setAttribute('orient','auto');
  const poly = document.createElementNS(NS, 'polygon');
  poly.setAttribute('points','0 0,6 3,0 6'); poly.setAttribute('fill','#16a34a');
  mk.appendChild(poly); defs.appendChild(mk); svg.appendChild(defs);

  // Vertical dashed green line
  const vl = document.createElementNS(NS, 'line');
  vl.setAttribute('x1',16); vl.setAttribute('y1', ROW_H/2);
  vl.setAttribute('x2',16); vl.setAttribute('y2', totalH - ROW_H/2);
  vl.setAttribute('stroke','#16a34a'); vl.setAttribute('stroke-width','1.5');
  vl.setAttribute('stroke-dasharray','4 3');
  svg.appendChild(vl);

  engines.forEach((eng, i) => {
    const cy = i * ROW_H + ROW_H / 2;
    // horizontal entry tick
    const hl = document.createElementNS(NS, 'line');
    hl.setAttribute('x1',0); hl.setAttribute('y1',cy);
    hl.setAttribute('x2',16); hl.setAttribute('y2',cy);
    hl.setAttribute('stroke','#16a34a'); hl.setAttribute('stroke-width','1.5');
    hl.setAttribute('stroke-dasharray','4 3');
    svg.appendChild(hl);
    // arrow exit
    const al = document.createElementNS(NS, 'line');
    al.setAttribute('x1',16); al.setAttribute('y1',cy);
    al.setAttribute('x2',44); al.setAttribute('y2',cy);
    al.setAttribute('stroke','#16a34a'); al.setAttribute('stroke-width','1.5');
    al.setAttribute('marker-end','url(#ag)');
    svg.appendChild(al);
    // label
    const lbl = document.createElementNS(NS, 'text');
    lbl.setAttribute('x',48); lbl.setAttribute('y', cy+4);
    lbl.setAttribute('font-size','9'); lbl.setAttribute('fill','#16a34a');
    lbl.setAttribute('font-weight','600');
    lbl.textContent = 'ok';
    svg.appendChild(lbl);
  });

  container.appendChild(svg);
  wrap.appendChild(container);

  const fnote = document.createElement('div');
  fnote.style.cssText = 'font-size:11px;color:#6b7280;margin-top:10px;padding:8px 12px;'
    + 'background:#f8fafc;border:1px solid #e5e7eb;border-radius:6px';
  fnote.textContent = 'Als alle ' + engines.length + ' engines < ' + minWords
    + ' woorden opleveren: chunk opgeslagen met lege tekst + fout-flag.';
  wrap.appendChild(fnote);

  return wrap;
}

// ─── D. Audit engine selectie (HYBRID: CSS + SVG Y-branch) ─
function renderAuditSelection(d) {
  const pri   = (d.audit || {}).primary    || {};
  const fall  = (d.audit || {}).fallback   || {};
  const retro = (d.audit || {}).retroaudit || {};
  const claudeOn = (d.audit || {}).enabled !== undefined
    ? (d.audit || {}).enabled : (pri.enabled || false);

  const wrap = document.createElement('div');

  // Decision box
  const dec = document.createElement('div');
  dec.style.cssText = 'text-align:center;padding:10px 20px;background:#f3f4f6;border-radius:8px;'
    + 'border:2px solid #e5e7eb;font-size:13px;font-weight:600;color:#374151;'
    + 'max-width:300px;margin:0 auto';
  dec.innerHTML = 'claude_api.enabled = <span style="font-family:monospace;color:'
    + (claudeOn ? '#16a34a' : '#dc2626') + '">' + (claudeOn ? 'true' : 'false') + '</span>';
  wrap.appendChild(dec);

  // SVG Y-branch connector
  const NS = 'http://www.w3.org/2000/svg';
  const SVG_W = 400; const SVG_H = 58;
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', '0 0 ' + SVG_W + ' ' + SVG_H);
  svg.setAttribute('width', '100%'); svg.setAttribute('height', SVG_H);
  svg.style.cssText = 'display:block;overflow:visible';

  const cx = SVG_W / 2;
  const lx = SVG_W * 0.2;
  const rx = SVG_W * 0.8;
  const mid = SVG_H * 0.55;

  function svgLine(x1,y1,x2,y2,color,w,dash) {
    const l = document.createElementNS(NS,'line');
    l.setAttribute('x1',x1); l.setAttribute('y1',y1);
    l.setAttribute('x2',x2); l.setAttribute('y2',y2);
    l.setAttribute('stroke',color); l.setAttribute('stroke-width',w||2);
    if(dash) l.setAttribute('stroke-dasharray','5 3');
    return l;
  }
  function svgTxt(x,y,txt,color,fw) {
    const t = document.createElementNS(NS,'text');
    t.setAttribute('x',x); t.setAttribute('y',y);
    t.setAttribute('text-anchor','middle'); t.setAttribute('font-size','11');
    t.setAttribute('fill',color||'#6b7280');
    if(fw) t.setAttribute('font-weight',fw);
    t.textContent = txt; return t;
  }

  // stem
  svg.appendChild(svgLine(cx,2, cx,mid, '#9ca3af',2));
  // left branch (ja = Claude)
  const lColor = claudeOn ? '#534AB7' : '#9ca3af';
  const rColor = claudeOn ? '#9ca3af' : '#1A6B72';
  svg.appendChild(svgLine(cx,mid, lx,SVG_H-2, lColor, claudeOn?2.5:1.5, !claudeOn));
  svg.appendChild(svgLine(cx,mid, rx,SVG_H-2, rColor, claudeOn?1.5:2.5, claudeOn));
  svg.appendChild(svgTxt(lx-28, mid+8, 'ja',  '#16a34a','700'));
  svg.appendChild(svgTxt(rx+28, mid+8, 'nee', '#dc2626','700'));
  wrap.appendChild(svg);

  // Two columns
  const cols = document.createElement('div');
  cols.style.cssText = 'display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px';

  const Cp = COLORS[pri.color  || 'purple'];
  const Cf = COLORS[fall.color || 'gray'];

  const left = document.createElement('div');
  left.style.cssText = 'padding:16px;border-radius:8px;border:2px solid '
    + (claudeOn ? Cp.bd : '#e5e7eb') + ';background:' + (claudeOn ? Cp.bg : '#fafafa');
  left.innerHTML = '<div style="font-size:12px;font-weight:700;color:' + (claudeOn ? Cp.tx : '#9ca3af') + ';margin-bottom:8px">'
    + (claudeOn ? '\u2713 ACTIEF' : 'INACTIEF') + ' \u2014 Claude API</div>'
    + '<div style="font-size:13px;font-weight:600;color:#111;margin-bottom:4px">' + (pri.name || 'Claude Haiku') + '</div>'
    + '<div style="font-size:11px;color:#6b7280;font-family:monospace;margin-bottom:5px">' + (pri.model || '') + '</div>'
    + '<div style="font-size:11px;color:#6b7280">' + (pri.subtitle || (pri.workers||10) + ' workers parallel') + '</div>'
    + '<div style="font-size:11px;color:#6b7280;margin-top:3px">K/A/I + tags + summary</div>';
  cols.appendChild(left);

  const right = document.createElement('div');
  right.style.cssText = 'padding:16px;border-radius:8px;border:2px solid '
    + (!claudeOn ? Cf.bd : '#e5e7eb') + ';background:' + (!claudeOn ? Cf.bg : '#fafafa');
  right.innerHTML = '<div style="font-size:12px;font-weight:700;color:' + (!claudeOn ? Cf.tx : '#9ca3af') + ';margin-bottom:8px">'
    + (!claudeOn ? '\u2713 ACTIEF' : 'FALLBACK') + ' \u2014 Ollama</div>'
    + '<div style="font-size:13px;font-weight:600;color:#111;margin-bottom:4px">' + (fall.name || 'Ollama llama3.1:8b') + '</div>'
    + '<div style="font-size:11px;color:#6b7280;margin-bottom:5px">' + (fall.subtitle || 'Sequentieel \u00b7 lokaal') + '</div>'
    + '<div style="font-size:11px;color:#6b7280">Stopt na ' + (fall.timeout_failures||3) + ' opeenvolgende timeouts</div>';
  cols.appendChild(right);
  wrap.appendChild(cols);

  // Retroaudit amber box
  const retBox = document.createElement('div');
  retBox.style.cssText = 'padding:12px 16px;background:#fef3c7;border:1px solid #d97706;border-radius:8px;font-size:12px';
  retBox.innerHTML = '<div style="font-weight:600;color:#78350f;margin-bottom:6px">Retroaudit — skipped chunks</div>'
    + '<div style="color:#6b7280;line-height:1.7">'
    + '<span style="color:#534AB7;font-weight:600">Claude:</span> ' + (retro.claude_note || retro.claude_limit || 'geen limiet') + '<br>'
    + '<span style="color:#1A6B72;font-weight:600">Ollama:</span> ' + (retro.ollama_note || retro.ollama_window || '') + '<br>'
    + '<span style="color:#6b7280">Trigger:</span> <code style="font-size:10px">' + (retro.trigger || '') + '</code>'
    + '</div>';
  wrap.appendChild(retBox);

  return wrap;
}

// ─── E. Nachtrun fasen ─────────────────────────────────────
function renderNightlyPhases(d) {
  const n = d.nightly || {};
  const phases = (n.phases || []).slice().sort((a,b) => a.order - b.order);
  const claudeOn = (d.audit || {}).enabled || ((d.audit||{}).primary||{}).enabled || false;
  const startHm  = n.start_time || '00:00';
  const endHm    = n.end_time   || '07:00';
  const limit    = n.image_screen_limit || 200;

  const wrap = document.createElement('div');

  const meta = document.createElement('div');
  meta.style.cssText = 'display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px;font-size:12px;color:#6b7280';
  meta.innerHTML = '<span>\u23F0 Tijdvenster: <strong>' + startHm + '\u2013' + endHm + ' Amsterdam</strong></span>'
    + '<span>Afbeeldingen: max <strong>' + limit + '/nacht</strong></span>'
    + '<span>Europe/Amsterdam</span>';
  wrap.appendChild(meta);

  // Outer wrapper: left padding for connector line + number badges
  const listWrap = document.createElement('div');
  listWrap.style.cssText = 'position:relative;padding-left:38px';

  // CSS vertical connector line
  const connector = document.createElement('div');
  connector.style.cssText = 'position:absolute;left:11px;top:18px;bottom:18px;width:2px;'
    + 'background:#e5e7eb;border-radius:1px';
  listWrap.appendChild(connector);

  const list = document.createElement('div');
  list.style.cssText = 'display:flex;flex-direction:column;gap:6px';

  phases.forEach(ph => {
    const colorKey = ph.color || (ph.order === 0 || ph.order === 8 ? 'green'
                    : ph.order === 4 ? (claudeOn ? 'purple' : 'teal') : 'gray');
    const C = COLORS[colorKey] || COLORS.gray;

    // Wrapper: relative so number badge can overlap connector
    const rowWrap = document.createElement('div');
    rowWrap.style.cssText = 'position:relative';

    // Number badge — absolutely positioned to sit on connector
    const numBadge = document.createElement('div');
    numBadge.textContent = ph.order;
    numBadge.style.cssText = 'position:absolute;left:-38px;top:50%;transform:translateY(-50%);'
      + 'width:24px;height:24px;border-radius:50%;background:' + C.bd
      + ';color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;'
      + 'justify-content:center;z-index:1';
    rowWrap.appendChild(numBadge);

    const row = document.createElement('div');
    row.style.cssText = 'display:flex;align-items:flex-start;gap:10px;padding:10px 14px;'
      + 'background:' + C.bg + ';border-radius:8px;border:1px solid ' + C.bd;

    const info = document.createElement('div');
    const name = document.createElement('div');
    name.textContent = ph.name;
    name.style.cssText = 'font-size:13px;font-weight:600;color:#111';
    info.appendChild(name);

    let desc = ph.description;
    if (ph.order === 4) desc += ' \u00b7 ' + startHm + '\u2013' + endHm;
    if (ph.order === 5) desc = 'Max ' + limit + '/nacht via Ollama';
    const sub = document.createElement('div');
    sub.textContent = desc;
    sub.style.cssText = 'font-size:11px;color:#6b7280;margin-top:2px';
    info.appendChild(sub);

    if (ph.engine) {
      const Ce = ph.engine === 'claude_or_ollama' ? COLORS.purple
               : ph.engine === 'ollama'           ? COLORS.teal
               : ph.engine === 'qdrant'           ? COLORS.teal
               : COLORS.gray;
      const eng = document.createElement('span');
      eng.textContent = ph.engine;
      eng.style.cssText = 'font-size:10px;font-weight:600;padding:1px 6px;border-radius:999px;'
        + 'margin-top:4px;display:inline-block;background:' + Ce.bg
        + ';color:' + Ce.tx + ';border:1px solid ' + Ce.bd;
      info.appendChild(eng);
    }

    row.appendChild(info);
    rowWrap.appendChild(row);
    list.appendChild(rowWrap);
  });

  listWrap.appendChild(list);
  wrap.appendChild(listWrap);

  // Timing stats footer
  const ns = d.nightly_stats || {};
  const statsRow = document.createElement('div');
  statsRow.style.cssText = 'margin-top:14px;padding:10px 14px;background:#f8fafc;'
    + 'border:1px solid #e5e7eb;border-radius:8px;font-size:11px;color:#6b7280;'
    + 'display:flex;gap:20px;flex-wrap:wrap;align-items:center';
  const nRA = ns.retroaudit_samples || 0;
  const nIM = ns.image_samples || 0;
  const spc = (ns.sec_per_chunk || 6.0).toFixed(1);
  const spi = (ns.sec_per_image || 8.0).toFixed(1);
  const raLabel = nRA > 0
    ? '<strong>' + spc + '</strong> sec/chunk'
    : '<strong>' + spc + '</strong> sec/chunk <em>(standaard)</em>';
  const imLabel = nIM > 0
    ? '<strong>' + spi + '</strong> sec/afbeelding'
    : '<strong>' + spi + '</strong> sec/afbeelding <em>(standaard)</em>';
  const nLabel = (nRA === 0 && nIM === 0)
    ? 'Nog geen metingen — standaardwaarden gebruikt'
    : 'Gebaseerd op ' + Math.max(nRA, nIM) + ' meting' + (Math.max(nRA, nIM) !== 1 ? 'en' : '');
  statsRow.innerHTML = '<span style="color:#374151;font-weight:600">Timing:</span>'
    + '<span>Retroaudit: ' + raLabel + '</span>'
    + '<span>Afbeelding: ' + imLabel + '</span>'
    + '<span style="margin-left:auto;font-style:italic">' + nLabel + '</span>';
  wrap.appendChild(statsRow);

  return wrap;
}

loadSettings();
</script>
"""
    return HTMLResponse(_page_shell("Instellingen", "/settings", body))


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
        chunks_n = imgs_total = 0
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
        # Count extracted images from images_metadata.json if available
        bh_meta = None
        try:
            bh = _book_hash_for_file(f)
            meta_path = IMAGES_DIR / bh / "images_metadata.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text())
                imgs_total = len(meta.get("images", []))
        except Exception:
            pass
        rows += f"""
<tr>
  <td><span style="font-weight:600">{f.name}</span><br>
      <span style="font-size:12px;color:#6b7280">{sec_label}</span></td>
  <td style="text-align:right">{chunks_n or '—'}</td>
  <td style="text-align:right">{imgs_total or '—'}</td>
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
                limit=5000, with_payload=True, with_vectors=False,
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


# ── POST /library/reaudit/{filename} ─────────────────────────────────────────

@app.post("/library/reaudit/{filename}")
async def library_reaudit(filename: str):
    """Start a background retroaudit job for skipped chunks of this book."""
    import uuid as _uuid
    import threading
    safe_name = re.sub(r"[^a-zA-Z0-9_\-.]", "_", filename)
    job_id = str(_uuid.uuid4())[:8]
    _REAUDIT_JOBS[job_id] = {"status": "queued", "progress": "Wachten op start…", "result": None, "error": None}
    t = threading.Thread(target=_run_reaudit_job, args=(job_id, safe_name), daemon=True)
    t.start()
    return {"job_id": job_id, "filename": safe_name}


# ── GET /library/reaudit/status/{job_id} ─────────────────────────────────────

@app.get("/library/reaudit/status/{job_id}")
async def library_reaudit_status(job_id: str):
    """Poll status of a reaudit job."""
    safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "", job_id)
    job = _REAUDIT_JOBS.get(safe_id)
    if not job:
        return JSONResponse({"status": "error", "error": "Job not found"}, status_code=404)
    return JSONResponse(job)


# ── GET /library/progress ─────────────────────────────────────────────────────

@app.get("/library/progress")
async def library_progress():
    result: dict = {"current": None, "queue": [], "queue_count": 0, "last_log": ""}
    try:
        if BOOK_CURRENT_FILE.exists():
            cur = json.loads(BOOK_CURRENT_FILE.read_text())
            started_str = cur.get("started", "")
            elapsed_min = 0
            if started_str:
                started = datetime.fromisoformat(started_str)
                if started.tzinfo is None:
                    started = started.replace(tzinfo=timezone.utc)
                elapsed_min = int((datetime.now(timezone.utc) - started).total_seconds() / 60)
            result["current"] = {
                "filename":        cur.get("filename", ""),
                "started":         started_str,
                "elapsed_minutes": elapsed_min,
                "collection":      cur.get("collection", ""),
                "progress":        cur.get("progress"),
            }
    except Exception:
        pass
    try:
        log = Path("/var/log/book_ingest_queue.log")
        if log.exists():
            lines = [l for l in log.read_text(errors="replace").splitlines() if l.strip()]
            if lines:
                result["last_log"] = lines[-1]
    except Exception:
        pass
    try:
        if BOOK_QUEUE_FILE.exists():
            q = json.loads(BOOK_QUEUE_FILE.read_text())
            if isinstance(q, list):
                result["queue"]       = [item.get("filename", "") for item in q]
                result["queue_count"] = len(q)
    except Exception:
        pass
    return result


# ── GET /api/library/progress/all  (state-machine) ───────────────────────────

def _load_state(state_file: Path) -> dict | None:
    try:
        return json.loads(state_file.read_text())
    except Exception:
        return None


def _save_state(state_file: Path, state: dict) -> None:
    """Write state dict atomically (tmp-then-rename)."""
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    try:
        tmp = state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False))
        tmp.replace(state_file)
    except Exception as exc:
        import logging as _logging
        _logging.getLogger(__name__).warning("Could not write state: %s", exc)


def _build_image_extraction_info(book_hash: str, state: dict, filename: str) -> dict:
    """Build image_extraction status dict for drawer and progress widget display."""
    image_source = _get_book_image_source(filename)

    if image_source in ("none", None, ""):
        return {"status": "not_applicable", "source": "none",
                "figures_found": 0, "pages_processed": None, "pages_total": None}

    if not state.get("image_extraction_enabled", True):
        return {"status": "disabled", "source": image_source,
                "figures_found": 0, "pages_processed": None, "pages_total": None}

    # ALWAYS check live progress FIRST — takes priority over stale metadata
    progress = _get_image_progress(book_hash)
    if progress is not None:
        return {
            "status":          "running",
            "figures_found":   progress.get("figures_found", 0),
            "pages_processed": progress.get("pages_processed", 0),
            "pages_total":     progress.get("pages_total"),
            "source":          progress.get("source", image_source),
        }

    # No live extraction — check completed metadata
    meta_path = BASE / "data" / "extracted_images" / book_hash / "images_metadata.json"
    if meta_path.exists():
        try:
            data = json.loads(meta_path.read_text())
            figures = data.get("images", [])
            return {"status": "done", "figures_found": len(figures),
                    "pages_processed": None, "pages_total": None,
                    "source": data.get("source", image_source)}
        except Exception:
            return {"status": "done", "figures_found": 0,
                    "pages_processed": None, "pages_total": None,
                    "source": image_source}

    return {"status": "pending", "figures_found": 0,
            "pages_processed": None, "pages_total": None, "source": image_source}


@app.get("/api/library/progress/all")
async def api_library_progress_all():
    """Return list of state.json dicts for every book in ingest_cache/."""
    states = []
    if CACHE_DIR.exists():
        for sf in sorted(CACHE_DIR.glob("*/state.json")):
            s = _load_state(sf)
            if s:
                s = dict(s)
                s["computed_status"] = _compute_book_status(s)
                states.append(s)
    return states


@app.get("/api/library/progress/active")
async def api_library_progress_active():
    """Return state.json for the currently-processing book, enriched with image_extraction."""
    state = None
    # First check the fast /tmp/book_ingest_current.json for the book_hash
    try:
        if BOOK_CURRENT_FILE.exists():
            cur = json.loads(BOOK_CURRENT_FILE.read_text())
            book_hash = cur.get("book_hash")
            if book_hash:
                sf = CACHE_DIR / book_hash / "state.json"
                state = _load_state(sf)
    except Exception:
        pass

    # Fallback: scan for first state that has status=processing
    if state is None and CACHE_DIR.exists():
        for sf in CACHE_DIR.glob("*/state.json"):
            s = _load_state(sf)
            if s and s.get("status") == "processing":
                state = s
                break

    if state is None:
        return None

    # Enrich with image_extraction status and computed_status
    bh = state.get("book_hash", "")
    fn = state.get("filename", "")
    state = dict(state)  # shallow copy — don't mutate cached state
    if bh and fn:
        state["image_extraction"] = _build_image_extraction_info(bh, state, fn)
    state["computed_status"] = _compute_book_status(state)
    return state


@app.get("/api/library/progress/{book_hash}")
async def api_library_progress_book(book_hash: str):
    """Return state.json for a specific book_hash."""
    sf = CACHE_DIR / book_hash / "state.json"
    state = _load_state(sf)
    if state is None:
        return JSONResponse({"error": "not found"}, status_code=404)
    return state


# ── POST /api/library/book/{book_hash}/re-extract-images ─────────────────────

@app.post("/api/library/book/{book_hash}/re-extract-images")
async def api_re_extract_images(book_hash: str):
    """Delete images_metadata.json and re-trigger image extraction for a completed book."""
    sf = CACHE_DIR / book_hash / "state.json"
    state = _load_state(sf)
    if state is None:
        return JSONResponse({"error": "book not found"}, status_code=404)

    filepath = state.get("filepath", "")
    if not filepath:
        return JSONResponse({"error": "no filepath in state"}, status_code=400)

    book_path = Path(filepath)
    if not book_path.exists():
        return JSONResponse({"error": f"file not found: {filepath}"}, status_code=404)

    # Delete existing metadata so extraction runs fresh
    meta_path = IMAGES_DIR / book_hash / "images_metadata.json"
    if meta_path.exists():
        meta_path.unlink()

    suffix = book_path.suffix.lower()

    import threading
    import sys
    sys.path.insert(0, str(BASE / "scripts"))
    from image_extractor import extract_figures_from_pdf, extract_images_from_epub, IMAGES_OUT as _IMAGES_OUT

    def _run():
        try:
            if suffix == ".pdf":
                extract_figures_from_pdf(book_path, book_hash, _IMAGES_OUT)
            elif suffix in (".epub",):
                extract_images_from_epub(book_path, book_hash, _IMAGES_OUT)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("re-extract failed for %s: %s", book_hash, exc)

    threading.Thread(target=_run, daemon=True).start()
    return {"status": "started", "book_hash": book_hash, "file": book_path.name}


# ── POST /api/library/book/{book_hash}/toggle-images ─────────────────────────

@app.post("/api/library/book/{book_hash}/toggle-images")
async def api_toggle_images(book_hash: str, body: dict):
    """Enable or disable image extraction for a book. Disabling deletes extracted images."""
    safe = re.sub(r"[^a-f0-9]", "", book_hash)[:16]
    sf   = CACHE_DIR / safe / "state.json"
    state = _load_state(sf)
    if state is None:
        return JSONResponse({"error": "not found"}, status_code=404)

    enabled = bool(body.get("enabled", True))
    state["image_extraction_enabled"] = enabled

    if not enabled:
        img_dir = IMAGES_DIR / safe
        if img_dir.exists():
            import shutil
            shutil.rmtree(img_dir)
        state["image_extraction_disabled_at"] = datetime.now(timezone.utc).isoformat()
        _save_state(sf, state)
        return {"ok": True, "action": "disabled_and_deleted"}

    # Re-enable
    state.pop("image_extraction_disabled_at", None)
    _save_state(sf, state)

    filepath = state.get("filepath", "")
    if filepath and Path(filepath).exists():
        import threading, sys as _sys
        _sys.path.insert(0, str(BASE / "scripts"))
        from image_extractor import (
            extract_figures_from_pdf, extract_images_from_epub, IMAGES_OUT as _IMAGES_OUT
        )
        suffix = Path(filepath).suffix.lower()

        def _run_toggle():
            try:
                if suffix == ".pdf":
                    extract_figures_from_pdf(Path(filepath), safe, _IMAGES_OUT)
                elif suffix in (".epub",):
                    extract_images_from_epub(Path(filepath), safe, _IMAGES_OUT)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning("toggle re-extract failed: %s", exc)

        threading.Thread(target=_run_toggle, daemon=True).start()
        return {"ok": True, "action": "enabled_and_started"}

    return {"ok": True, "action": "enabled_no_file"}


# ── GET /videos/progress ──────────────────────────────────────────────────────

@app.get("/videos/progress")
async def videos_progress():
    result: dict = {"current": None, "queue": [], "queue_items": [], "queue_count": 0, "last_log": "", "done_count": 0}
    # Count completed transcripts
    try:
        result["done_count"] = sum(1 for _ in TRANS_DIR.glob("*.json")) if TRANS_DIR.exists() else 0
    except Exception:
        pass
    try:
        if CURRENT_FILE.exists():
            cur = json.loads(CURRENT_FILE.read_text())
            started_str = cur.get("started", "")
            elapsed_min = 0
            if started_str:
                started = datetime.fromisoformat(started_str)
                if started.tzinfo is None:
                    started = started.replace(tzinfo=timezone.utc)
                elapsed_min = int((datetime.now(timezone.utc) - started).total_seconds() / 60)
            result["current"] = {
                "file":            cur.get("file", ""),
                "video_type":      cur.get("video_type", ""),
                "started":         started_str,
                "elapsed_minutes": elapsed_min,
            }
    except Exception:
        pass
    try:
        log = Path("/var/log/transcription_queue.log")
        if log.exists():
            lines = [l for l in log.read_text(errors="replace").splitlines() if l.strip()]
            if lines:
                result["last_log"] = lines[-1]
    except Exception:
        pass
    try:
        if QUEUE_FILE.exists():
            q = json.loads(QUEUE_FILE.read_text())
            if isinstance(q, list):
                result["queue"]       = [item.get("filename", item.get("file", "")) for item in q]
                result["queue_items"] = [{"filename": item.get("filename", item.get("file", "")), "video_type": item.get("video_type", "")} for item in q]
                result["queue_count"] = len(q)
    except Exception:
        pass
    return result


# ── GET /api/transcription/stats ─────────────────────────────────────────────

@app.get("/api/transcription/stats")
async def api_transcription_stats():
    """Return model_rate and current video file size for ETA estimation."""
    result: dict = {"model_rate": None, "current_file_size_mb": None, "current_started_at": None}
    try:
        if TRANS_STATS_FILE.exists():
            stats = json.loads(TRANS_STATS_FILE.read_text())
            result["model_rate"] = stats.get("model_rate")
    except Exception:
        pass
    try:
        if CURRENT_FILE.exists():
            cur = json.loads(CURRENT_FILE.read_text())
            vtype    = cur.get("video_type", "")
            filename = cur.get("file", "")
            result["current_started_at"] = cur.get("started")
            if vtype and filename:
                vpath = BASE / "videos" / vtype / filename
                if vpath.exists():
                    result["current_file_size_mb"] = round(vpath.stat().st_size / 1e6, 1)
    except Exception:
        pass
    return result


# ── Pause / resume endpoints ──────────────────────────────────────────────────

_BOOK_PAUSE_FILE  = Path("/tmp/book_ingest_pause")
_VIDEO_PAUSE_FILE = Path("/tmp/transcription_pause")


@app.post("/library/pause")
async def library_pause():
    _BOOK_PAUSE_FILE.touch()
    return {"paused": True}


@app.post("/library/resume")
async def library_resume():
    _BOOK_PAUSE_FILE.unlink(missing_ok=True)
    return {"paused": False}


@app.get("/library/paused")
async def library_paused():
    return {"paused": _BOOK_PAUSE_FILE.exists()}


# ── GET /library/classifications ──────────────────────────────────────────────

@app.get("/library/classifications")
async def library_classifications():
    """Return book_classifications.json with ingestion status per book."""
    cfg_path = Path("/root/medical-rag/config/book_classifications.json")
    try:
        return json.loads(cfg_path.read_text())
    except Exception as e:
        return {"error": str(e), "classifications": {}}


@app.post("/videos/pause")
async def videos_pause():
    _VIDEO_PAUSE_FILE.touch()
    return {"paused": True}


@app.post("/videos/resume")
async def videos_resume():
    _VIDEO_PAUSE_FILE.unlink(missing_ok=True)
    return {"paused": False}


@app.get("/videos/paused")
async def videos_paused():
    return {"paused": _VIDEO_PAUSE_FILE.exists()}


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGES — priority-based browser (no approval gating)
# ═══════════════════════════════════════════════════════════════════════════════

def _load_kai_cache() -> dict:
    """Load book_classifications.json, cached per request."""
    try:
        return json.loads((BASE / "config" / "book_classifications.json").read_text()).get("classifications", {})
    except Exception:
        return {}


def _priority_badge(priority: str, override: str | None = None) -> str:
    effective = override or priority
    cfg = {
        "high":   ("#dcfce7", "#16a34a", "Hoog"),
        "normal": ("#e8f4f5", "#1A6B72", "Normaal"),
        "low":    ("#f3f4f6", "#6b7280", "Laag"),
        "skip":   ("#fee2e2", "#991b1b", "Overslaan"),
    }.get(effective, ("#f3f4f6", "#6b7280", effective))
    marker = " ★" if override else ""
    return (f'<span style="background:{cfg[0]};color:{cfg[1]};padding:2px 8px;'
            f'border-radius:999px;font-size:11px;font-weight:600">{cfg[2]}{marker}</span>')


def _prio_dropdown_items(book_hash: str, cls_key: str, current: str) -> str:
    items = ""
    for p, lbl in [("high", "Hoog"), ("normal", "Normaal"), ("low", "Laag"), ("skip", "Overslaan")]:
        fw = "700" if current == p else "400"
        items += (f'<button onclick="setPriority(\'{book_hash}\',\'{cls_key}\',\'{p}\')" '
                  f'style="display:block;width:100%;text-align:left;padding:6px 10px;'
                  f'border:none;background:none;cursor:pointer;font-size:13px;'
                  f'border-radius:4px;font-weight:{fw}">{lbl}</button>')
    return items


def _eval_badge(evaluated: bool) -> str:
    if evaluated:
        return ('<span style="background:#dcfce7;color:#16a34a;padding:2px 8px;'
                'border-radius:999px;font-size:11px;font-weight:600">Beoordeeld</span>')
    return ('<span style="background:#fef3c7;color:#b45309;padding:2px 8px;'
            'border-radius:999px;font-size:11px;font-weight:600">Niet beoordeeld</span>')


# ── GET /images ────────────────────────────────────────────────────────────────

@app.get("/images", response_class=HTMLResponse)
async def images_page(filter: str = "all"):
    kai = _load_kai_cache()

    # Collect all books with images_metadata.json
    books_data: list[dict] = []
    for meta_file in sorted(IMAGES_DIR.glob("*/images_metadata.json")):
        try:
            meta = json.loads(meta_file.read_text())
        except Exception:
            continue
        book_hash = meta.get("book_hash", meta_file.parent.name)
        filename  = meta.get("filename", "")
        images    = meta.get("images", [])
        if not images:
            continue

        # Find matching classification entry
        cls_entry: dict = {}
        for entry in kai.values():
            for pat in entry.get("filename_patterns", []):
                if pat.lower() in filename.lower():
                    cls_entry = entry
                    break
            if cls_entry:
                break

        priority          = cls_entry.get("image_priority", "normal")
        priority_override = cls_entry.get("image_priority_override") or None
        effective         = priority_override or priority
        evaluated         = bool(cls_entry.get("image_evaluated", False))

        books_data.append({
            "book_hash":   book_hash,
            "filename":    filename,
            "images":      images,
            "priority":    priority,
            "override":    priority_override,
            "effective":   effective,
            "evaluated":   evaluated,
            "cls_key":     next((k for k, v in kai.items()
                                 if v is cls_entry), ""),
        })

    # Apply filter
    filter_map = {
        "high":   lambda b: b["effective"] == "high",
        "normal": lambda b: b["effective"] == "normal",
        "low":    lambda b: b["effective"] == "low",
        "skip":   lambda b: b["effective"] == "skip",
        "unreviewed": lambda b: not b["evaluated"],
    }
    if filter != "all" and filter in filter_map:
        books_data = [b for b in books_data if filter_map[filter](b)]

    # Sort: unreviewed first, then by priority level, then by filename
    prio_order = {"high": 0, "normal": 1, "low": 2, "skip": 3}
    books_data.sort(key=lambda b: (b["evaluated"], prio_order.get(b["effective"], 9), b["filename"]))

    sections = ""
    for bd in books_data:
        cards = ""
        for img in bd["images"][:20]:  # cap at 20 per book for performance
            fname   = img.get("file", "")
            img_src = f"/images/file/{bd['book_hash']}/{fname}" if fname else ""
            caption = img.get("caption", "") or img.get("alt_text", "")
            cards += f"""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px;
            width:180px;flex-shrink:0">
  <div style="height:110px;background:#f8fafc;border-radius:6px;overflow:hidden;
              display:flex;align-items:center;justify-content:center;margin-bottom:6px">
    <img src="{img_src}" style="max-width:100%;max-height:100%;object-fit:contain"
         onerror="this.style.display='none';this.nextSibling.style.display='flex'"
         loading="lazy">
    <div style="display:none;color:#9ca3af;font-size:11px;text-align:center;padding:8px">
      Niet gevonden
    </div>
  </div>
  <div style="font-size:11px;color:#6b7280;overflow:hidden;text-overflow:ellipsis;
              white-space:nowrap;margin-bottom:4px" title="{fname}">{fname}</div>
  {f'<div style="font-size:11px;color:#4a5568;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical">{caption[:80]}</div>' if caption else ''}
</div>"""

        more = len(bd["images"]) - 20
        if more > 0:
            cards += f'<div style="display:flex;align-items:center;justify-content:center;width:180px;color:#6b7280;font-size:13px">+{more} meer</div>'

        n = len(bd["images"])
        sections += f"""
<div class="section" style="margin-bottom:20px">
  <div class="section-head" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
      <span class="section-title" style="font-size:15px">{bd['filename']}</span>
      {_priority_badge(bd['priority'], bd['override'])}
      {_eval_badge(bd['evaluated'])}
    </div>
    <div style="display:flex;align-items:center;gap:8px">
      <span style="font-size:13px;color:#6b7280">{n} afbeelding(en)</span>
      <div style="position:relative">
        <button onclick="togglePrioMenu('{bd['book_hash']}')"
                class="btn btn-secondary" style="font-size:12px;padding:4px 10px">
          Prioriteit ▾
        </button>
        <div id="prio-{bd['book_hash']}"
             style="display:none;position:absolute;right:0;top:110%;background:#fff;
                    border:1px solid #e2e8f0;border-radius:8px;padding:4px;
                    min-width:140px;z-index:100;box-shadow:0 4px 12px rgba(0,0,0,.1)">
          {_prio_dropdown_items(bd['book_hash'], bd['cls_key'], bd['override'] or bd['priority'])}
        </div>
      </div>
    </div>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:10px;padding:14px 20px">{cards}</div>
</div>"""

    filter_links = ""
    for fkey, flabel in [("all","Alle"),("high","Hoog"),("normal","Normaal"),
                         ("low","Laag"),("skip","Overslaan"),("unreviewed","Niet beoordeeld")]:
        active = "background:#1A6B72;color:#fff;" if filter == fkey else ""
        filter_links += (f'<a href="/images?filter={fkey}" class="btn btn-secondary" '
                         f'style="font-size:13px;{active}">{flabel}</a>')

    total = sum(len(b["images"]) for b in books_data)
    body = f"""
<div class="wrap">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:10px">
    <h1 style="font-size:22px;font-weight:700">Afbeeldingen</h1>
    <span style="font-size:13px;color:#6b7280">{len(books_data)} boek(en) · {total} afbeeldingen</span>
  </div>
  <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap">{filter_links}</div>
  {sections if sections else
   '<div style="color:#9ca3af;padding:24px">Geen afbeeldingen gevonden. Nachtrun verwerkt nieuwe boeken automatisch.</div>'}
</div>
<script>
function togglePrioMenu(bh) {{
  const el = document.getElementById('prio-' + bh);
  el.style.display = el.style.display === 'none' ? 'block' : 'none';
}}
document.addEventListener('click', function(e) {{
  if (!e.target.closest('[id^=prio-]') && !e.target.textContent.includes('▾'))
    document.querySelectorAll('[id^=prio-]').forEach(el => el.style.display = 'none');
}});
function setPriority(bookHash, clsKey, priority) {{
  fetch('/api/images/priority', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{book_hash: bookHash, cls_key: clsKey, priority_override: priority}})
  }})
  .then(r => r.json())
  .then(d => {{ if (d.status === 'ok') location.reload(); else alert(JSON.stringify(d)); }})
  .catch(e => alert('Fout: ' + e));
}}
</script>"""
    return _page_shell("Afbeeldingen", "/images", body)


# ── GET /api/images/library ────────────────────────────────────────────────────

@app.get("/api/images/library")
async def api_images_library():
    kai = _load_kai_cache()
    books: list[dict] = []
    for meta_file in sorted(IMAGES_DIR.glob("*/images_metadata.json")):
        try:
            meta = json.loads(meta_file.read_text())
        except Exception:
            continue
        book_hash = meta.get("book_hash", meta_file.parent.name)
        filename  = meta.get("filename", "")
        images    = meta.get("images", [])

        cls_entry: dict = {}
        cls_key = ""
        for k, entry in kai.items():
            for pat in entry.get("filename_patterns", []):
                if pat.lower() in filename.lower():
                    cls_entry = entry
                    cls_key = k
                    break
            if cls_entry:
                break

        books.append({
            "book_hash":        book_hash,
            "filename":         filename,
            "image_count":      len(images),
            "image_source":     meta.get("image_source", ""),
            "priority":         cls_entry.get("image_priority", "normal"),
            "priority_override":cls_entry.get("image_priority_override"),
            "image_evaluated":  bool(cls_entry.get("image_evaluated", False)),
            "cls_key":          cls_key,
        })
    return books


# ── POST /api/images/priority ──────────────────────────────────────────────────

@app.post("/api/images/priority")
async def api_images_priority(request_data: dict):
    cls_key          = request_data.get("cls_key", "")
    priority_override = request_data.get("priority_override")

    cfg_path = BASE / "config" / "book_classifications.json"
    try:
        cfg = json.loads(cfg_path.read_text())
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)

    classifications = cfg.get("classifications", {})

    # Find by cls_key or by book_hash match
    if cls_key and cls_key in classifications:
        classifications[cls_key]["image_priority_override"] = priority_override
        classifications[cls_key]["image_evaluated"] = True
    else:
        return JSONResponse({"error": f"cls_key '{cls_key}' not found"}, status_code=404)

    cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    return {"status": "ok", "cls_key": cls_key, "priority_override": priority_override}

# ═══════════════════════════════════════════════════════════════════════════════
# SEARCH — /search  /search/query  /search/images  /search/suggest
# ═══════════════════════════════════════════════════════════════════════════════

_QUICK_QUERIES = [
    ("ST-36 Zusanli",              "ST-36 Zusanli indicaties"),
    ("Blood stasis onderbeen",     "Blood stasis onderbeen behandeling"),
    ("A. femoralis anatomie",      "A. femoralis anatomie"),
    ("Etalagebenen protocol",      "Etalagebenen claudicatio intermittens behandeling"),
    ("GTR Golgi Tendon Reflex",    "Golgi Tendon Reflex NRT mechanisme"),
    ("QAT balancering",            "QAT meridiaan balancering techniek"),
]

_COLL_OPTIONS = [
    ("medical_library",     "Medische Literatuur",   "#1A6B72"),
    ("nrt_qat_curriculum",  "NRT & QAT Curriculum",  "#7c3aed"),
    ("video_transcripts",   "Video Transcripts",      "#059669"),
]

_TAG_COLORS = {
    "acupuncture_point":     "#059669",
    "acupuncture_point_location": "#059669",
    "acupuncture_point_indication": "#059669",
    "treatment_protocol":    "#1A6B72",
    "tissue_cause":          "#dc2626",
    "tissue_consequence":    "#d97706",
    "anatomy_visualization": "#7c3aed",
    "tcm_diagnosis":         "#0891b2",
    "clinical_perspective":  "#6b7280",
    "nrt_relevant":          "#b45309",
    "device_settings":       "#9d174d",
}

def _tag_badge(tag: str) -> str:
    color = _TAG_COLORS.get(tag, "#6b7280")
    short = tag.replace("_", " ")
    return (
        f'<span style="background:{color}22;color:{color};padding:2px 7px;'
        f'border-radius:999px;font-size:11px;font-weight:600;white-space:nowrap">{short}</span>'
    )

def _score_bar(score: float) -> str:
    pct   = min(int(score * 100), 100)
    color = "#059669" if score > 0.75 else ("#d97706" if score > 0.55 else "#ef4444")
    return (
        f'<div style="display:inline-flex;align-items:center;gap:5px">'
        f'<div style="width:60px;height:6px;background:#e5e7eb;border-radius:3px;overflow:hidden">'
        f'<div style="width:{pct}%;height:6px;background:{color};border-radius:3px"></div>'
        f'</div>'
        f'<span style="font-size:11px;color:{color};font-weight:600">{score:.2f}</span>'
        f'</div>'
    )


@app.get("/search", response_class=HTMLResponse)
async def search_page(q: str = ""):
    quick_btns = "".join(
        f'<button onclick="doSearch({json.dumps(qv)})" class="btn btn-secondary" '
        f'style="font-size:12px;padding:5px 12px">{ql}</button>'
        for ql, qv in _QUICK_QUERIES
    )
    col_checks = "".join(
        f'<label style="display:flex;align-items:center;gap:5px;font-size:13px;cursor:pointer">'
        f'<input type="checkbox" class="col-check" value="{cv}" checked '
        f'style="accent-color:{cc};width:15px;height:15px"> '
        f'<span style="color:{cc};font-weight:600">{cl}</span></label>'
        for cv, cl, cc in _COLL_OPTIONS
    )

    body = f"""
<div class="wrap" style="max-width:1200px">

<!-- Tab bar -->
<div style="display:flex;gap:2px;margin-bottom:20px;border-bottom:2px solid #e5e7eb">
  <button id="tab-search-btn" onclick="switchTab('search')"
    style="padding:10px 20px;font-size:14px;font-weight:600;border:none;cursor:pointer;
           border-bottom:3px solid #1A6B72;margin-bottom:-2px;color:#1A6B72;background:#fff">
    Zoeken
  </button>
  <button id="tab-images-btn" onclick="switchTab('images')"
    style="padding:10px 20px;font-size:14px;font-weight:600;border:none;cursor:pointer;
           border-bottom:3px solid transparent;margin-bottom:-2px;color:#6b7280;background:#fff">
    Afbeeldingen zoeken
  </button>
</div>

<!-- TAB 1: Zoeken -->
<div id="tab-search">

  <!-- Search bar -->
  <div style="display:flex;gap:8px;margin-bottom:12px">
    <input id="search-input" type="text" value="{q.replace('"', '&quot;')}"
      placeholder="Zoek in medische literatuur, video transcripts..."
      style="flex:1;padding:12px 16px;font-size:16px;border:2px solid #e5e7eb;border-radius:10px"
      onkeydown="if(event.key==='Enter') doSearch()">
    <button onclick="doSearch()" class="btn btn-primary" style="padding:12px 24px;font-size:15px">
      Zoeken
    </button>
  </div>

  <!-- Collection checkboxes -->
  <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:12px;align-items:center">
    {col_checks}
  </div>

  <!-- Quick search buttons -->
  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:24px">
    {quick_btns}
  </div>

  <!-- Results: two-column layout -->
  <div style="display:grid;grid-template-columns:60% 40%;gap:20px">

    <!-- LEFT: Answer + Sources -->
    <div>
      <!-- Answer box -->
      <div id="answer-box" style="display:none;background:#e8f4f5;border:2px solid #1A6B72;
           border-radius:10px;padding:16px;margin-bottom:16px">
        <div style="font-size:11px;font-weight:700;color:#1A6B72;text-transform:uppercase;
             letter-spacing:.08em;margin-bottom:8px">Antwoord</div>
        <div id="answer-text" style="font-size:14px;line-height:1.7;color:#1e293b;
             white-space:pre-wrap"></div>
        <div id="answer-meta" style="margin-top:10px;font-size:12px;color:#64748b"></div>
      </div>

      <!-- Sources -->
      <div id="sources-list"></div>
    </div>

    <!-- RIGHT: Images panel -->
    <div>
      <div id="images-panel" style="display:none">
        <div style="font-size:13px;font-weight:700;color:#374151;margin-bottom:10px">
          Gevonden afbeeldingen (<span id="img-count">0</span>)
        </div>
        <div id="images-grid" style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px"></div>
      </div>
    </div>

  </div>
</div><!-- end tab-search -->


<!-- TAB 2: Afbeeldingen -->
<div id="tab-images" style="display:none">
  <div style="display:flex;gap:8px;margin-bottom:12px">
    <input id="img-search-input" type="text"
      placeholder="Zoek op punt (ST-36), figuur (4.155) of anatomie..."
      style="flex:1;padding:12px 16px;font-size:15px;border:2px solid #e5e7eb;border-radius:10px"
      onkeydown="if(event.key==='Enter') doImgSearch()">
    <button onclick="doImgSearch()" class="btn btn-primary" style="padding:12px 20px">Zoeken</button>
  </div>
  <div style="display:flex;gap:10px;margin-bottom:16px;align-items:center">
    <select id="img-filter" onchange="doImgSearch()" style="padding:7px 10px;border:1px solid #d1d5db;border-radius:7px;font-size:13px">
      <option value="false">Alle afbeeldingen</option>
      <option value="true" selected>Alleen goedgekeurd</option>
    </select>
  </div>
  <div id="img-search-results" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px"></div>
</div>

</div><!-- wrap -->

<!-- Lightbox -->
<div id="lightbox" onclick="this.style.display='none'"
  style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:9999;
         align-items:center;justify-content:center;cursor:zoom-out">
  <img id="lightbox-img" style="max-width:90vw;max-height:90vh;border-radius:8px;box-shadow:0 4px 40px rgba(0,0,0,.6)">
</div>

<style>
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0}} }}
#answer-text .cursor {{ display:inline-block;width:2px;height:1.1em;background:#1A6B72;
  vertical-align:middle;animation:blink .8s step-end infinite;margin-left:1px }}
.source-card {{ background:#fff;border-radius:12px;border:1px solid #e2e8f0;padding:12px;
  margin-bottom:8px;box-shadow:0 1px 3px rgba(0,0,0,.08) }}
.source-card:hover {{ border-color:#1A6B72 }}
.img-thumb {{ background:#f8fafc;border-radius:8px;border:1px solid #e2e8f0;overflow:hidden;cursor:zoom-in }}
.img-thumb:hover {{ border-color:#1A6B72 }}
.img-thumb img {{ width:100%;aspect-ratio:1;object-fit:cover;background:#e2e8f0 }}
.tab-active {{ border-bottom-color:#1A6B72!important;color:#1A6B72!important }}
.tab-inactive {{ border-bottom-color:transparent!important;color:#6b7280!important }}
</style>

<script>
function switchTab(name) {{
  document.getElementById('tab-search').style.display = name==='search' ? '' : 'none';
  document.getElementById('tab-images').style.display = name==='images' ? '' : 'none';
  document.getElementById('tab-search-btn').className = name==='search' ? 'tab-active' : 'tab-inactive';
  document.getElementById('tab-images-btn').className = name==='images' ? 'tab-active' : 'tab-inactive';
  // reset button styles inline since they're inline
  const sb = document.getElementById('tab-search-btn');
  const ib = document.getElementById('tab-images-btn');
  if (name==='search') {{
    sb.style.borderBottomColor='#1A6B72'; sb.style.color='#1A6B72';
    ib.style.borderBottomColor='transparent'; ib.style.color='#6b7280';
  }} else {{
    ib.style.borderBottomColor='#1A6B72'; ib.style.color='#1A6B72';
    sb.style.borderBottomColor='transparent'; sb.style.color='#6b7280';
  }}
}}

async function doSearch(prefillQuery) {{
  const q = prefillQuery || document.getElementById('search-input').value.trim();
  if (!q) return;
  document.getElementById('search-input').value = q;
  history.replaceState({{}}, '', '/search?q=' + encodeURIComponent(q));

  const cols = Array.from(document.querySelectorAll('.col-check:checked')).map(c => c.value);
  if (!cols.length) {{ alert('Selecteer ten minste één collectie'); return; }}

  const answerBox  = document.getElementById('answer-box');
  const answerText = document.getElementById('answer-text');
  const answerMeta = document.getElementById('answer-meta');
  const sourcesList = document.getElementById('sources-list');
  const imagesGrid  = document.getElementById('images-grid');
  const imgPanel    = document.getElementById('images-panel');
  const imgCount    = document.getElementById('img-count');

  answerBox.style.display  = 'block';
  answerText.innerHTML = '<span class="cursor"></span>';
  answerMeta.textContent   = '';
  sourcesList.innerHTML    = '<div style="color:#9ca3af;padding:12px;font-size:14px">Zoeken…</div>';
  imagesGrid.innerHTML     = '';
  imgPanel.style.display   = 'none';

  let fullText = '';
  const cursor = answerText.querySelector('.cursor');

  try {{
    const resp = await fetch('/search/query', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{query: q, collections: cols}})
    }});
    const reader = resp.body.getReader();
    const dec    = new TextDecoder();
    let buf = '';

    while (true) {{
      const {{done, value}} = await reader.read();
      if (done) break;
      buf += dec.decode(value, {{stream: true}});
      const parts = buf.split('\\n\\n');
      buf = parts.pop();
      for (const part of parts) {{
        if (!part.startsWith('data: ')) continue;
        try {{
          const d = JSON.parse(part.slice(6));
          if (d.type === 'token') {{
            fullText += d.text;
            answerText.textContent = fullText;
            answerText.appendChild(cursor);
          }} else if (d.type === 'done') {{
            cursor.remove();
            answerMeta.textContent = 'Gebaseerd op ' + d.sources.length + ' bronnen — zoektijd: ' + d.query_time_ms + 'ms';
            renderSources(d.sources, sourcesList);
            renderImages(d.images, imagesGrid, imgPanel, imgCount);
          }} else if (d.type === 'error') {{
            answerText.textContent = 'Fout: ' + d.message;
            cursor.remove();
          }}
        }} catch(e) {{}}
      }}
    }}
  }} catch(e) {{
    answerText.textContent = 'Fout: ' + e.message;
    cursor.remove();
  }}
}}

function renderSources(sources, container) {{
  if (!sources.length) {{
    container.innerHTML = '<div style="color:#9ca3af;padding:12px;font-size:14px">Geen bronnen gevonden</div>';
    return;
  }}
  let html = '<div style="font-size:12px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">Bronnen (' + sources.length + ')</div>';
  sources.forEach((s, i) => {{
    const isBook  = s.type === 'book';
    const icon    = isBook ? '📖' : '🎥';
    const title   = isBook
      ? (s.source_file || '').replace(/\\.pdf$/i,'').replace(/\\.epub$/i,'').slice(0,40) + ' p.' + (s.page_number||'?')
      : (s.source_file||'').replace(/\\.mp4$/i,'').replace(/_/g,' ').slice(0,35) + ' ' + (s.timestamp_display||'');
    const badges  = (s.usability_tags||[]).map(t => '<span style="background:#e8f4f5;color:#1A6B72;padding:2px 7px;border-radius:999px;font-size:10px;font-weight:600">' + t.replace(/_/g,' ') + '</span>').join(' ');
    const ptBadges = (s.point_codes||[]).map(p => '<span style="background:#05996922;color:#059669;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:700">' + p + '</span>').join(' ');
    const figBadge = (s.figure_refs||[]).map(f => '<span style="background:#7c3aed22;color:#7c3aed;padding:2px 6px;border-radius:4px;font-size:11px">Fig '+f+'</span>').join(' ');
    const score   = s.score || 0;
    const pct     = Math.min(Math.round(score*100),100);
    const scolor  = score>0.75 ? '#059669' : (score>0.55 ? '#d97706' : '#ef4444');
    const videoTag = !isBook ? '<span style="background:#7c3aed22;color:#7c3aed;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:600">' + (s.video_type||'').toUpperCase() + '</span>' : '';
    const truncText = (s.text||'').slice(0,200);
    html += `
<div class="source-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:6px">
    <span style="font-weight:600;font-size:13px">${{icon}} ${{title}}</span>
    <div style="display:inline-flex;align-items:center;gap:5px;flex-shrink:0">
      <div style="width:50px;height:5px;background:#e5e7eb;border-radius:3px;overflow:hidden">
        <div style="width:${{pct}}%;height:5px;background:${{scolor}};border-radius:3px"></div>
      </div>
      <span style="font-size:11px;color:${{scolor}};font-weight:600">${{score.toFixed(2)}}</span>
    </div>
  </div>
  <div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:6px">${{videoTag}}${{ptBadges}}${{figBadge}}${{badges}}</div>
  <details>
    <summary style="font-size:12px;color:#6b7280;cursor:pointer">${{truncText}}…</summary>
    <div style="font-size:13px;line-height:1.6;color:#374151;margin-top:6px;padding-top:6px;border-top:1px solid #f3f4f6">${{s.text||''}}</div>
  </details>
  ${{!isBook ? '<div style="font-size:11px;color:#9ca3af;margin-top:4px;font-style:italic">Gesproken kennis van de instructeur</div>' : ''}}
</div>`;
  }});
  container.innerHTML = html;
}}

function renderImages(images, grid, panel, count) {{
  if (!images.length) {{ panel.style.display='none'; return; }}
  panel.style.display = '';
  count.textContent = images.length;
  let html = '';
  images.forEach(img => {{
    const approved = img.approved ? '✅ Goedgekeurd' : '⏳ In behandeling';
    const aColor   = img.approved ? '#059669' : '#d97706';
    const approveBtn = !img.approved
      ? `<button onclick="approveImg('${{img.path}}',true)" style="background:#059669;color:#fff;border:none;border-radius:4px;padding:3px 8px;font-size:11px;cursor:pointer;margin-top:4px">Goedkeuren</button>`
      : '';
    const aiHint = img.ai_suggestion ? `<div style="font-size:10px;color:#6b7280;margin-top:2px">${{img.ai_suggestion}}</div>` : '';
    html += `
<div class="img-thumb" onclick="openLightbox('${{img.url}}')">
  <img src="${{img.url}}" alt="Afbeelding" loading="lazy" onerror="this.src=''">
  <div style="padding:6px">
    <div style="font-size:11px;font-weight:600;color:#374151;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${{(img.source_file||'').slice(0,25)}}</div>
    <div style="font-size:10px;color:#9ca3af">p.${{img.page||'?'}}</div>
    <div style="font-size:10px;color:${{aColor}};font-weight:600">${{approved}}</div>
    ${{aiHint}}${{approveBtn}}
  </div>
</div>`;
  }});
  grid.innerHTML = html;
}}

function openLightbox(url) {{
  event.stopPropagation();
  const lb = document.getElementById('lightbox');
  document.getElementById('lightbox-img').src = url;
  lb.style.display = 'flex';
}}
document.getElementById('lightbox').onclick = function(e) {{
  if (e.target === this) this.style.display = 'none';
}};

async function approveImg(path, approved) {{
  event.stopPropagation();
  await fetch('/images/approve', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{path, approved}})
  }});
  event.target.textContent = '✓ Opgeslagen';
  event.target.disabled = true;
}}

async function doImgSearch() {{
  const q  = document.getElementById('img-search-input').value.trim();
  const ao = document.getElementById('img-filter').value;
  if (!q) return;
  const res  = document.getElementById('img-search-results');
  res.innerHTML = '<div style="color:#9ca3af;font-size:14px">Zoeken...</div>';
  try {{
    const r = await fetch('/search/images?q=' + encodeURIComponent(q) + '&approved_only=' + ao);
    const d = await r.json();
    if (!d.images.length) {{ res.innerHTML = '<div style="color:#9ca3af;font-size:14px">Geen afbeeldingen gevonden</div>'; return; }}
    let html = '';
    d.images.forEach(img => {{
      const approved = img.approved ? '✅' : '⏳';
      html += `<div class="img-thumb" onclick="openLightbox('${{img.url}}')">
        <img src="${{img.url}}" alt="" loading="lazy" onerror="this.src=''">
        <div style="padding:6px">
          <div style="font-size:11px;font-weight:600">${{(img.source_file||'?').slice(0,20)}}</div>
          <div style="font-size:10px;color:#9ca3af">p.${{img.page||'?'}} ${{approved}}</div>
        </div>
      </div>`;
    }});
    res.innerHTML = html;
  }} catch(e) {{ res.innerHTML = 'Fout: ' + e.message; }}
}}

// Auto-run if query param present
{f"document.addEventListener('DOMContentLoaded', () => doSearch({json.dumps(q)}));" if q else ""}
</script>"""

    return _page_shell("Zoeken", "/search", body)


# ── POST /search/query (streaming SSE) ────────────────────────────────────────

@app.post("/search/query")
async def search_query(request: Request):
    body = await request.json()
    query       = (body.get("query") or "").strip()
    collections = body.get("collections") or ["medical_library", "nrt_qat_curriculum", "video_transcripts"]
    if not query:
        return JSONResponse({"error": "query required"}, status_code=400)

    async def generate():
        t0 = time.time()
        try:
            import rag_query as rq
            loop     = asyncio.get_running_loop()
            prepared = await loop.run_in_executor(
                None, lambda: rq.rag_search_only(query, collections)
            )
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','message':str(e)})}\n\n"
            return

        answer_text = ""
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream(
                    "POST",
                    "http://localhost:11434/api/generate",
                    json={
                        "model":  "llama3.1:8b",
                        "prompt": prepared["prompt"],
                        "system": prepared["system_context"],
                        "stream": True,
                    },
                ) as resp:
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            d     = json.loads(line)
                            token = d.get("response", "")
                            if token:
                                answer_text += token
                                yield f"data: {json.dumps({'type':'token','text':token})}\n\n"
                            if d.get("done"):
                                break
                        except Exception:
                            pass
        except Exception as e:
            err_msg = f"[Ollama fout: {e}]"
            answer_text = err_msg
            yield f"data: {json.dumps({'type':'token','text':err_msg})}\n\n"

        elapsed_ms = int((time.time() - t0) * 1000)
        done_payload = {
            "type":                "done",
            "answer":              answer_text,
            "sources":             prepared["sources"],
            "images":              prepared["images"],
            "query_time_ms":       elapsed_ms,
            "collections_searched": prepared["collections_searched"],
        }
        yield f"data: {json.dumps(done_payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


# ── GET /search/images ────────────────────────────────────────────────────────

@app.get("/search/images")
async def search_images(q: str = "", approved_only: bool = True, book: str = ""):
    if not q:
        return {"query": q, "images": [], "total": 0}
    try:
        import rag_query as rq
        loop    = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None,
            lambda: rq.image_search(q, approved_only=approved_only,
                                    book_filter=book or None),
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return {"query": q, "images": results, "total": len(results)}


# ── GET /search/suggest ────────────────────────────────────────────────────────

_SUGGEST_POOL = [
    "ST-36 Zusanli", "SP-6 Sanyinjiao", "BL-40 Weizhong", "SP-10 Xuehai",
    "LR-3 Taichong", "GB-39 Xuanzhong", "KD-3 Taixi", "GV-4 Mingmen",
    "ST-32 Futu", "BL-17 Geshu", "BL-23 Shenshu", "GB-37 Guangming",
    "blood stasis", "qi stagnation", "cold bi obstruction", "kidney yang deficiency",
    "dampness heat", "liver qi stagnation",
    "Golgi Tendon Reflex", "muscle spindle", "reciprocal innervation",
    "A. femoralis", "M. gastrocnemius", "M. tibialis anterior",
    "atherosclerosis", "claudicatio intermittens", "etalagebenen",
    "QAT blue pads", "QAT green pads", "PEMF settings", "RLT settings",
]

@app.get("/search/suggest")
async def search_suggest(q: str = ""):
    if not q or len(q) < 2:
        return []
    ql = q.lower()
    return [s for s in _SUGGEST_POOL if ql in s.lower()][:8]


# ═══════════════════════════════════════════════════════════════════════════════
# PROTOCOLS — NRT standaard behandelprotocol
# ═══════════════════════════════════════════════════════════════════════════════

_PROTOCOL_FILE = BASE / "config" / "ai_instructions" / "nrt_standaard_protocol_v3.md"


def _render_md_to_html(md: str) -> str:
    """Minimal Markdown → HTML: headers, bold, tables, code, hr, lists."""
    import html as _html
    lines = md.split("\n")
    out = []
    in_table = False
    in_code = False
    in_list = False
    skip_next_separator = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def close_table():
        nonlocal in_table, skip_next_separator
        if in_table:
            out.append("</tbody></table>")
            in_table = False
        skip_next_separator = False

    for raw in lines:
        line = raw.rstrip()

        # fenced code block
        if line.startswith("```"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                close_list()
                close_table()
                out.append('<pre style="background:#f8f9fa;border:1px solid #e5e7eb;border-radius:6px;padding:12px;overflow-x:auto;font-size:13px"><code>')
                in_code = True
            continue
        if in_code:
            out.append(_html.escape(line))
            continue

        # table row
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            # separator row (---|---|---)
            if all(re.match(r"^[-:]+$", c) for c in cells if c):
                if not in_table:
                    # this is header separator — close thead, open tbody
                    # find the last appended header row and wrap in thead
                    if out and "<tr>" in out[-1]:
                        out[-1] = "<thead>" + out[-1] + "</thead><tbody>"
                    in_table = True
                skip_next_separator = True
                continue
            row_html = "".join(f"<td>{_inline_md(_html.escape(c))}</td>" for c in cells)
            if not in_table:
                close_list()
                out.append(
                    '<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:14px">'
                    f'<tr style="background:#f3f4f6">{row_html}</tr>'
                )
            else:
                out.append(f'<tr>{row_html}</tr>')
            continue

        # non-table line — close table if open
        close_table()

        # horizontal rule
        if re.match(r"^---+$", line):
            close_list()
            out.append('<hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0">')
            continue

        # headings
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            close_list()
            level = len(m.group(1))
            text  = _inline_md(_html.escape(m.group(2)))
            sizes = {1:"22px",2:"19px",3:"16px",4:"15px",5:"14px",6:"14px"}
            weights = {1:"800",2:"700",3:"700",4:"600",5:"600",6:"600"}
            mt = "28px" if level <= 2 else "20px"
            out.append(
                f'<h{level} style="font-size:{sizes[level]};font-weight:{weights[level]};'
                f'margin-top:{mt};margin-bottom:8px;color:#111827">{text}</h{level}>'
            )
            continue

        # blockquote
        if line.startswith("> "):
            close_list()
            text = _inline_md(_html.escape(line[2:]))
            out.append(
                f'<blockquote style="border-left:3px solid #1A6B72;margin:10px 0;'
                f'padding:8px 14px;background:#e8f4f5;color:#155a60;font-size:14px">{text}</blockquote>'
            )
            continue

        # list item
        if re.match(r"^[-*]\s+", line):
            if not in_list:
                out.append('<ul style="margin:8px 0 8px 24px;font-size:14px">')
                in_list = True
            text = _inline_md(_html.escape(line.lstrip("-* ").lstrip()))
            out.append(f"<li style='margin:3px 0'>{text}</li>")
            continue

        close_list()

        # blank line
        if not line.strip():
            out.append("")
            continue

        # paragraph
        out.append(f'<p style="font-size:14px;line-height:1.7;margin:6px 0">{_inline_md(_html.escape(line))}</p>')

    close_list()
    close_table()
    return "\n".join(out)


def _inline_md(text: str) -> str:
    """Process inline markdown: **bold**, `code`, _italic_."""
    text = re.sub(r"\*\*(.+?)\*\*", r'<strong>\1</strong>', text)
    text = re.sub(r"`(.+?)`", r'<code style="background:#f3f4f6;padding:1px 5px;border-radius:4px;font-size:92%">\1</code>', text)
    text = re.sub(r"_(.+?)_", r'<em>\1</em>', text)
    return text


def _protocol_card_html(p: dict) -> str:
    """Render a single protocol status card for Tab 2."""
    import html as _html
    pid           = _html.escape(p["protocol_id"])
    klacht        = _html.escape(p["klacht"])
    version       = p.get("version", 1)
    needs_review  = p.get("needs_review", False)
    reasons       = p.get("review_reasons", [])
    lit_count     = p.get("literature_count", 0)
    lit_titles    = p.get("literature_titles", [])
    generated_at  = p.get("generated_at", "")

    # Format date
    try:
        from datetime import datetime as _dt
        dt = _dt.fromisoformat(generated_at.replace("Z", "+00:00"))
        date_str = dt.strftime("%d-%m-%Y %H:%M")
    except Exception:
        date_str = generated_at[:10] if generated_at else "—"

    # Lit summary: first 2 titles + "en N meer"
    if lit_titles:
        shown = lit_titles[:2]
        extra = len(lit_titles) - 2
        lit_str = ", ".join(shown)
        if extra > 0:
            lit_str += f" en {extra} meer"
    else:
        lit_str = "—"

    # Status badge
    if needs_review:
        badge = ('<span style="background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;'
                 'padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600">'
                 '&#x1F514; Update beschikbaar</span>')
    else:
        badge = ('<span style="background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;'
                 'padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600">'
                 '&#x1F7E2; Actueel</span>')

    # Reasons list
    reasons_html = ""
    if needs_review and reasons:
        items = "".join(f"<li style='margin:3px 0'>{_html.escape(r)}</li>" for r in reasons)
        reasons_html = (
            f'<div style="margin-top:10px;background:#fff7ed;border-left:3px solid #f97316;'
            f'padding:10px 14px;border-radius:0 6px 6px 0">'
            f'<div style="font-size:12px;font-weight:700;color:#9a3412;margin-bottom:4px">Reden voor review:</div>'
            f'<ul style="font-size:13px;color:#c2410c;margin:0 0 0 16px">{items}</ul>'
            f'<button onclick="markReviewed(\'{pid}\')" style="margin-top:10px;background:#f97316;'
            f'color:#fff;border:none;border-radius:6px;padding:6px 14px;font-size:12px;'
            f'font-weight:600;cursor:pointer">Markeer als bekeken</button>'
            f'</div>'
        )

    return f"""
<div id="card-{pid}" style="background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.08);
     padding:18px 20px;margin-bottom:14px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
    <div>
      <div style="font-size:16px;font-weight:700;color:#111827">{klacht}</div>
      <div style="font-size:12px;color:#6b7280;margin-top:2px">v{version} &nbsp;·&nbsp; {date_str}</div>
    </div>
    {badge}
  </div>
  <div style="margin-top:10px;font-size:13px;color:#374151">
    <strong>Literatuur ({lit_count}):</strong> {_html.escape(lit_str)}
  </div>
  {reasons_html}
</div>"""


@app.get("/protocols", response_class=HTMLResponse)
async def protocols_page(tab: str = "standaard"):
    import html as _html

    # --- Tab 1: Standaard Protocol ---
    try:
        raw_md = _PROTOCOL_FILE.read_text(encoding="utf-8")
    except Exception as e:
        raw_md = f"# Fout\n\nKon protocol niet laden: {e}"
    rendered    = _render_md_to_html(raw_md)
    raw_escaped = _html.escape(raw_md)

    # --- Tab 2: Behandelprotocollen ---
    try:
        from protocol_metadata import get_all_protocol_status
        all_protocols = get_all_protocol_status()
    except Exception:
        all_protocols = []

    n_review = sum(1 for p in all_protocols if p.get("needs_review"))

    if all_protocols:
        cards_html = "".join(_protocol_card_html(p) for p in all_protocols)
    else:
        cards_html = ('<div style="background:#fff;border-radius:10px;padding:32px 20px;'
                      'text-align:center;color:#9ca3af;font-size:14px">'
                      'Nog geen protocollen gegenereerd. '
                      'Gebruik <code>generate_protocol.py</code> om protocollen aan te maken.'
                      '</div>')

    review_badge = (f' <span style="background:#f97316;color:#fff;border-radius:10px;'
                    f'padding:1px 7px;font-size:11px;font-weight:700">{n_review}</span>'
                    if n_review else "")

    tab1_active = tab != "protocollen"
    tab1_style  = "border-bottom:3px solid #1A6B72;color:#1A6B72"   if tab1_active else "border-bottom:3px solid transparent;color:#6b7280"
    tab2_style  = "border-bottom:3px solid #1A6B72;color:#1A6B72"   if not tab1_active else "border-bottom:3px solid transparent;color:#6b7280"

    body = f"""
<div class="wrap" style="max-width:960px">

  <!-- Page header -->
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:10px">
    <h1 style="font-size:22px;font-weight:700">Behandelprotocollen</h1>
    <div style="font-size:13px;color:#6b7280">NRT-Amsterdam.nl</div>
  </div>

  <!-- Tab bar -->
  <div style="display:flex;gap:2px;margin-bottom:24px;border-bottom:2px solid #e5e7eb" id="tab-bar">
    <button onclick="switchTab('standaard')"
      id="tab-standaard-btn"
      style="padding:10px 20px;font-size:14px;font-weight:600;border:none;cursor:pointer;
             margin-bottom:-2px;background:#fff;{tab1_style}">
      Standaard Protocol
    </button>
    <button onclick="switchTab('protocollen')"
      id="tab-protocollen-btn"
      style="padding:10px 20px;font-size:14px;font-weight:600;border:none;cursor:pointer;
             margin-bottom:-2px;background:#fff;{tab2_style}">
      Behandelprotocollen{review_badge}
    </button>
  </div>

  <!-- TAB 1: Standaard Protocol -->
  <div id="tab-standaard" style="display:{'block' if tab1_active else 'none'}">
    <div style="display:flex;justify-content:flex-end;gap:8px;margin-bottom:14px">
      <a href="/protocols/raw" target="_blank" class="btn btn-secondary">↓ Raw MD</a>
      <button id="edit-btn" onclick="toggleEdit()" class="btn btn-primary">&#x270F; Bewerken</button>
    </div>
    <!-- Read view -->
    <div id="read-view" class="section" style="padding:24px 28px">
      {rendered}
    </div>
    <!-- Edit view (hidden by default) -->
    <div id="edit-view" style="display:none">
      <textarea id="md-editor"
        style="width:100%;height:65vh;font-family:monospace;font-size:13px;
               padding:16px;border:2px solid #1A6B72;border-radius:10px;
               resize:vertical;background:#1e293b;color:#e2e8f0;line-height:1.6"
      >{raw_escaped}</textarea>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;flex-wrap:wrap;gap:8px">
        <span id="save-msg" style="font-size:13px;color:#6b7280"></span>
        <div style="display:flex;gap:8px">
          <button onclick="cancelEdit()" class="btn btn-secondary">Annuleren</button>
          <button onclick="saveProtocol()" class="btn btn-green">&#x1F4BE; Opslaan &amp; committen</button>
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 2: Behandelprotocollen -->
  <div id="tab-protocollen" style="display:{'none' if tab1_active else 'block'}">

    <!-- Generator panel -->
    <div class="section" style="padding:20px 24px;margin-bottom:20px">
      <div style="font-size:15px;font-weight:700;margin-bottom:14px">Nieuw Protocol Genereren</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end">
        <div style="flex:1;min-width:220px">
          <label style="font-size:12px;font-weight:600;color:#6b7280;display:block;margin-bottom:4px">KLACHT</label>
          <input id="gen-klacht" type="text" placeholder="bijv. Etalagebenen, Hoofdpijn, Artrose…"
            style="width:100%;padding:9px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:14px"
            onkeydown="if(event.key==='Enter') startGenerate()">
        </div>
        <button id="gen-btn" onclick="startGenerate()" class="btn btn-primary"
          style="padding:9px 20px;font-size:14px;white-space:nowrap">
          &#x25B6; Genereer Protocol
        </button>
      </div>
      <!-- Progress -->
      <div id="gen-progress" style="display:none;margin-top:14px">
        <div style="background:#e5e7eb;border-radius:6px;height:22px;overflow:hidden;margin-bottom:8px">
          <div id="gen-bar-inner" style="height:100%;background:#1A6B72;border-radius:6px;
               width:0%;text-align:center;font-size:11px;color:#fff;font-weight:700;
               line-height:22px;transition:width .4s ease">0%</div>
        </div>
        <div id="gen-msg" style="font-size:13px;color:#6b7280"></div>
      </div>
      <a id="gen-download" href="#" download style="display:none;margin-top:10px"
         class="btn btn-green">&#x2193; Download .docx</a>
    </div>

    <!-- Existing protocols list -->
    {cards_html}
  </div>

</div>

<script>
function switchTab(name) {{
  ['standaard', 'protocollen'].forEach(t => {{
    const active = (t === name);
    document.getElementById('tab-' + t).style.display = active ? 'block' : 'none';
    const btn = document.getElementById('tab-' + t + '-btn');
    btn.style.borderBottom = active ? '3px solid #1A6B72' : '3px solid transparent';
    btn.style.color = active ? '#1A6B72' : '#6b7280';
  }});
}}

function toggleEdit() {{
  document.getElementById('read-view').style.display = 'none';
  document.getElementById('edit-view').style.display = 'block';
  document.getElementById('edit-btn').style.display  = 'none';
}}

function cancelEdit() {{
  document.getElementById('read-view').style.display = 'block';
  document.getElementById('edit-view').style.display = 'none';
  document.getElementById('edit-btn').style.display  = 'inline-block';
  document.getElementById('save-msg').textContent = '';
}}

async function saveProtocol() {{
  const content = document.getElementById('md-editor').value;
  const msg     = document.getElementById('save-msg');
  msg.style.color = '#6b7280';
  msg.textContent = 'Opslaan…';
  try {{
    const r = await fetch('/protocols/save', {{
      method:  'POST',
      headers: {{'Content-Type': 'application/json'}},
      body:    JSON.stringify({{content}})
    }});
    const d = await r.json();
    if (d.ok) {{
      msg.style.color = '#059669';
      msg.textContent = '&#x2713; Opgeslagen + gecommit (' + (d.commit || '') + ')';
      setTimeout(() => location.reload(), 1500);
    }} else {{
      msg.style.color = '#dc2626';
      msg.textContent = 'Fout: ' + (d.error || 'onbekend');
    }}
  }} catch(e) {{
    msg.style.color = '#dc2626';
    msg.textContent = 'Netwerk fout: ' + e;
  }}
}}

async function markReviewed(protocolId) {{
  try {{
    const r = await fetch('/protocols/' + protocolId + '/reviewed', {{method: 'POST'}});
    const d = await r.json();
    if (d.status === 'ok') location.reload();
  }} catch(e) {{ alert('Fout: ' + e); }}
}}

// ── Protocol generator ──────────────────────────────────────────────────────
let _genJobId   = null;
let _genPoller  = null;

async function startGenerate() {{
  const klacht = document.getElementById('gen-klacht').value.trim();
  if (!klacht) {{ showGenMsg('Vul een klacht in', '#dc2626'); return; }}

  showGenMsg('Bezig met opstarten…', '#6b7280');
  setGenBusy(true);

  try {{
    const r = await fetch('/protocols/generate', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{klacht}})
    }});
    const d = await r.json();
    if (d.job_id) {{
      _genJobId = d.job_id;
      _genPoller = setInterval(pollGenStatus, 2000);
    }} else {{
      showGenMsg('Fout: ' + (d.error || 'onbekend'), '#dc2626');
      setGenBusy(false);
    }}
  }} catch(e) {{
    showGenMsg('Netwerk fout: ' + e, '#dc2626');
    setGenBusy(false);
  }}
}}

async function pollGenStatus() {{
  if (!_genJobId) return;
  try {{
    const r = await fetch('/protocols/generate/status/' + _genJobId);
    const d = await r.json();
    const pct = d.progress || 0;
    document.getElementById('gen-bar-inner').style.width = pct + '%';
    document.getElementById('gen-bar-inner').textContent = pct + '%';
    showGenMsg(d.current_section || '…', '#6b7280');

    if (d.status === 'complete') {{
      clearInterval(_genPoller);
      setGenBusy(false);
      const dl = document.getElementById('gen-download');
      dl.href = d.download_url;
      dl.style.display = 'inline-block';
      showGenMsg('&#x2713; Protocol aangemaakt!', '#059669');
      setTimeout(() => location.reload(), 3000);
    }} else if (d.status === 'error') {{
      clearInterval(_genPoller);
      setGenBusy(false);
      showGenMsg('Fout: ' + (d.error || 'onbekend'), '#dc2626');
    }}
  }} catch(e) {{ /* ignore poll errors */ }}
}}

function setGenBusy(busy) {{
  document.getElementById('gen-btn').disabled = busy;
  document.getElementById('gen-progress').style.display = busy ? 'block' : 'none';
}}

function showGenMsg(msg, color) {{
  const el = document.getElementById('gen-msg');
  el.innerHTML = msg;
  el.style.color = color || '#6b7280';
}}
</script>
"""
    return _page_shell("Protocollen", "/protocols", body)


@app.post("/protocols/save")
async def protocols_save(request: Request):
    try:
        body = await request.json()
        content = body.get("content", "")
        if not content.strip():
            return JSONResponse({"ok": False, "error": "Lege inhoud — niet opgeslagen"})
        if len(content) > 500_000:
            return JSONResponse({"ok": False, "error": "Bestand te groot (max 500KB)"})

        _PROTOCOL_FILE.write_text(content, encoding="utf-8")

        # git commit
        result = subprocess.run(
            ["git", "add", str(_PROTOCOL_FILE)],
            cwd=str(BASE), capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return JSONResponse({"ok": False, "error": f"git add mislukt: {result.stderr.strip()}"})

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        commit = subprocess.run(
            ["git", "commit", "-m", f"protocol: NRT standaard protocol bijgewerkt {now_str}"],
            cwd=str(BASE), capture_output=True, text=True, timeout=15
        )
        if commit.returncode not in (0, 1):
            return JSONResponse({"ok": False, "error": f"git commit mislukt: {commit.stderr.strip()}"})

        short_hash = ""
        try:
            h = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(BASE), capture_output=True, text=True, timeout=5
            )
            short_hash = h.stdout.strip()
        except Exception:
            pass

        return JSONResponse({"ok": True, "commit": short_hash})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})


@app.get("/protocols/raw")
async def protocols_raw():
    try:
        content = _PROTOCOL_FILE.read_text(encoding="utf-8")
        return HTMLResponse(
            content=f"<pre style='font-family:monospace;font-size:13px;white-space:pre-wrap;padding:20px'>{content}</pre>",
            media_type="text/html"
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/protocols/status")
async def protocols_status():
    """Return status of all generated protocols including review flags."""
    try:
        from protocol_metadata import get_all_protocol_status
        return get_all_protocol_status()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/protocols/{protocol_id}/reviewed")
async def protocol_mark_reviewed(protocol_id: str):
    """Mark a protocol as reviewed after the user acknowledges the earmark."""
    safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "", protocol_id)
    if not safe_id:
        return JSONResponse({"status": "error", "error": "Invalid protocol id"}, status_code=400)
    try:
        from protocol_metadata import mark_as_reviewed
        mark_as_reviewed(safe_id)
        return JSONResponse({"status": "ok"})
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=500)


# ─── PROTOCOL GENERATOR — job tracking ───────────────────────────────────────

_PROTO_JOBS: dict[str, dict] = {}   # job_id → {status, section, progress, output_path, error}

# ─── RETROAUDIT — job tracking ────────────────────────────────────────────────

_REAUDIT_JOBS: dict[str, dict] = {}  # job_id → {status, progress, result, error}


def _run_reaudit_job(job_id: str, filename: str) -> None:
    """Background thread: find skipped chunks for this book and re-tag them in Qdrant."""
    try:
        _REAUDIT_JOBS[job_id]["status"] = "running"
        _REAUDIT_JOBS[job_id]["progress"] = "Skipped chunks ophalen…"

        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        from audit_book import tag_chunks_with_ollama

        client = QdrantClient(host="localhost", port=6333, timeout=60)

        results, _ = client.scroll(
            collection_name="medical_library",
            scroll_filter=Filter(must=[
                FieldCondition(key="source_file",  match=MatchValue(value=filename)),
                FieldCondition(key="audit_status", match=MatchValue(value="skipped_ollama_timeout")),
            ]),
            limit=2000, with_payload=True, with_vectors=False,
        )

        points = [(p.id, p.payload) for p in results if p.payload]
        if not points:
            _REAUDIT_JOBS[job_id].update({"status": "done", "result": "Geen overgeslagen chunks"})
            return

        _REAUDIT_JOBS[job_id]["progress"] = f"{len(points)} chunks taggen…"

        # Clear audit_status so success is detectable after tagging
        for _, chunk in points:
            chunk.pop("audit_status", None)

        chunks_only = [pair[1] for pair in points]
        tag_chunks_with_ollama(chunks_only)

        scored = still_pending = 0
        for point_id, chunk in points:
            if chunk.get("audit_status") == "skipped_ollama_timeout":
                still_pending += 1
                continue
            client.set_payload(
                collection_name="medical_library",
                payload={
                    "usability_tags":     chunk.get("usability_tags", []),
                    "protocol_relevance": chunk.get("protocol_relevance", 0.0),
                    "has_point_codes":    chunk.get("has_point_codes", False),
                    "has_figure_refs":    chunk.get("has_figure_refs", False),
                    "primary_use":        chunk.get("primary_use", ""),
                    "audit_status":       "tagged",
                },
                points=[point_id],
            )
            scored += 1

        _REAUDIT_JOBS[job_id].update({
            "status": "done",
            "result": f"{scored} gescoord, {still_pending} nog uitstaand",
        })
    except Exception as exc:
        _REAUDIT_JOBS[job_id].update({"status": "error", "error": str(exc)[:300]})


# ─── GLOBAL RETROAUDIT (Claude API, all books) ────────────────────────────────

_retroaudit_state: dict = {
    "running": False, "started_at": None, "finished_at": None,
    "total_found": 0, "total_done": 0, "total_errors": 0,
    "current_book": "", "current_book_title": "", "books_done": [], "error": None,
}
_retroaudit_lock = threading.Lock()


def _run_retroaudit() -> None:
    """Background thread: tag ALL skipped chunks across medical_library via Claude API."""
    global _retroaudit_state
    with _retroaudit_lock:
        _retroaudit_state.update({
            "running": True,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "finished_at": None,
            "total_found": 0,
            "total_done": 0,
            "total_errors": 0,
            "current_book": "",
            "current_book_title": "",
            "books_done": [],
            "error": None,
        })
    try:
        sys.path.insert(0, str(BASE / "scripts"))
        from claude_audit import is_enabled as _ca_enabled, audit_chunks_parallel
        if not _ca_enabled():
            _retroaudit_state.update({"running": False, "error": "Claude API niet ingeschakeld"})
            return

        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchAny
        client = QdrantClient(host="localhost", port=6333, timeout=60)
        COLLECTION = "medical_library"
        _cls = _load_classifications()

        results, _ = client.scroll(
            collection_name=COLLECTION,
            scroll_filter=Filter(should=[
                FieldCondition(key="audit_status", match=MatchAny(any=["skipped_ollama_timeout", "skipped_claude_error"])),
            ]),
            limit=10_000, with_payload=True, with_vectors=False,
        )
        points = [(p.id, p.payload) for p in results if p.payload]
        _retroaudit_state["total_found"] = len(points)

        if not points:
            _retroaudit_state.update({"running": False, "finished_at": datetime.now(timezone.utc).isoformat()})
            return

        # Group by source_file for progress reporting
        by_book: dict[str, list] = {}
        for pid, payload in points:
            src = payload.get("source_file", "onbekend")
            by_book.setdefault(src, []).append((pid, payload))

        done = 0
        errors = 0
        books_done: list[dict] = []

        for book_name, book_points in by_book.items():
            _bdisp = _book_display(book_name, _cls)
            _retroaudit_state["current_book"]       = book_name
            _retroaudit_state["current_book_title"] = _bdisp[0]
            chunks_only = [bp[1] for bp in book_points]
            for c in chunks_only:
                c.pop("audit_status", None)

            tagged_list = audit_chunks_parallel(chunks_only)

            book_scored = 0
            book_errors = 0
            for (pid, _), chunk in zip(book_points, tagged_list):
                if (chunk.get("audit_status") or "").startswith("skipped"):
                    book_errors += 1
                    errors += 1
                    continue
                client.set_payload(
                    collection_name=COLLECTION,
                    payload={
                        "kai_k":        chunk.get("kai_k", 3),
                        "kai_a":        chunk.get("kai_a", 3),
                        "kai_i":        chunk.get("kai_i", 3),
                        "tags":         chunk.get("tags", []),
                        "summary":      chunk.get("summary", ""),
                        "audit_status": "tagged_claude",
                        "audit_engine": "claude_api",
                    },
                    points=[pid],
                )
                book_scored += 1
                done += 1

            books_done.append({
                "book":         book_name,
                "book_title":   _bdisp[0],
                "book_authors": _bdisp[1],
                "scored":       book_scored,
                "errors":       book_errors,
            })
            _retroaudit_state["total_done"]   = done
            _retroaudit_state["total_errors"] = errors
            _retroaudit_state["books_done"]   = books_done

        _retroaudit_state.update({
            "running":            False,
            "current_book":       "",
            "current_book_title": "",
            "finished_at":        datetime.now(timezone.utc).isoformat(),
        })
    except Exception as exc:
        _retroaudit_state.update({"running": False, "error": str(exc)[:400]})


@app.post("/api/retroaudit/start")
async def api_retroaudit_start():
    """Start global Claude retroaudit for all skipped chunks."""
    import sys as _sys
    _sys.path.insert(0, str(BASE / "scripts"))
    try:
        from claude_audit import is_enabled as _ca_enabled
        if not _ca_enabled():
            return JSONResponse({"ok": False, "error": "Claude API niet ingeschakeld"}, status_code=400)
    except ImportError:
        return JSONResponse({"ok": False, "error": "claude_audit module niet gevonden"}, status_code=500)

    if _retroaudit_state.get("running"):
        return JSONResponse({"ok": False, "error": "Al bezig"}, status_code=409)

    t = threading.Thread(target=_run_retroaudit, daemon=True)
    t.start()
    return {"ok": True}


@app.get("/api/retroaudit/status")
async def api_retroaudit_status():
    """Current state of the global retroaudit job."""
    return JSONResponse(_retroaudit_state)


def _run_generate_job(job_id: str, klacht: str) -> None:
    """Run generate_protocol in a thread; update _PROTO_JOBS as it progresses."""
    import importlib.util, uuid

    def progress_fn(section: str, pct: int) -> None:
        _PROTO_JOBS[job_id].update({"current_section": section, "progress": pct})

    try:
        _PROTO_JOBS[job_id]["status"] = "running"
        sys.path.insert(0, str(BASE / "scripts"))
        import generate_protocol as gp
        importlib.reload(gp)               # always fresh on each call
        output_path = gp.generate_protocol(klacht, progress_fn=progress_fn)
        _PROTO_JOBS[job_id].update({
            "status":         "complete",
            "progress":       100,
            "current_section": "Klaar!",
            "output_path":    output_path,
            "download_url":   "/protocols/download/" + Path(output_path).name,
        })
    except Exception as e:
        _PROTO_JOBS[job_id].update({
            "status":  "error",
            "error":   str(e)[:300],
        })


@app.post("/protocols/generate")
async def protocols_generate(request: Request):
    """Start a protocol generation job in a background thread."""
    import threading, uuid
    body   = await request.json()
    klacht = (body.get("klacht") or "").strip()
    if not klacht:
        return JSONResponse({"error": "klacht is required"}, status_code=400)
    if len(klacht) > 200:
        return JSONResponse({"error": "klacht too long"}, status_code=400)

    job_id = str(uuid.uuid4())[:8]
    _PROTO_JOBS[job_id] = {
        "status":          "queued",
        "current_section": "Wachten op start…",
        "progress":        0,
        "klacht":          klacht,
        "output_path":     None,
        "download_url":    None,
        "error":           None,
    }

    t = threading.Thread(target=_run_generate_job, args=(job_id, klacht), daemon=True)
    t.start()
    return JSONResponse({"status": "started", "job_id": job_id})


@app.get("/protocols/generate/status/{job_id}")
async def protocols_generate_status(job_id: str):
    """Poll status of a protocol generation job."""
    safe_id = re.sub(r"[^a-zA-Z0-9_\-]", "", job_id)
    job = _PROTO_JOBS.get(safe_id)
    if not job:
        return JSONResponse({"status": "error", "error": "Job not found"}, status_code=404)
    return JSONResponse(job)


@app.get("/protocols/download/{filename}")
async def protocols_download(filename: str):
    """Serve a generated .docx file."""
    safe = Path(filename).name                 # strip path traversal
    if not safe.endswith(".docx"):
        return JSONResponse({"error": "Only .docx files"}, status_code=400)
    path = BASE / "data/protocols" / safe
    if not path.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(
        str(path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=safe,
    )


# ── GET /images/file/{path:path} ──────────────────────────────────────────────
# Serves both flat files (old) and subdir/{book_hash}/{fname} (new extraction)

@app.get("/images/file/{file_path:path}")
async def serve_image(file_path: str):
    # Resolve against IMAGES_DIR, prevent traversal outside it
    try:
        candidate = (IMAGES_DIR / file_path).resolve()
        candidate.relative_to(IMAGES_DIR.resolve())  # raises if outside
    except (ValueError, Exception):
        return JSONResponse({"error": "Forbidden"}, status_code=403)
    if not candidate.exists():
        return JSONResponse({"error": "Not found"}, status_code=404)
    suffix = candidate.suffix.lstrip(".").lower()
    media  = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
               "gif": "image/gif", "webp": "image/webp"}.get(suffix, "image/png")
    return FileResponse(str(candidate), media_type=media)
