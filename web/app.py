from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import httpx, psutil, subprocess, json, os, re, shutil
from pathlib import Path
from datetime import datetime

app = FastAPI()
BASE         = Path("/root/medical-rag")
VIDEOS_DIR   = BASE / "videos"
TRANS_DIR    = BASE / "data" / "transcripts"

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
                pts = cr.json()["result"]["vectors_count"]
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
      <div style="color:#93c5fd;font-size:13px">NRT-Amsterdam &bull; Axel Biere</div>
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

def _run_transcription(video_path: str, video_type: str) -> None:
    """Background task: runs transcribe_videos.py for one file."""
    subprocess.run(
        ["python3", str(BASE / "scripts" / "transcribe_videos.py"),
         "--file", video_path,
         "--type", video_type],
        cwd=BASE,
        capture_output=True,
    )

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
      <div style="color:#93c5fd;font-size:13px">NRT-Amsterdam &bull; Axel Biere</div>
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


# ── GET /videos ───────────────────────────────────────────────────────────────

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
                badge = (
                    '<span style="background:#dcfce7;color:#166534;border-radius:999px;'
                    'padding:2px 9px;font-size:12px;font-weight:600">✓ Klaar</span>'
                    if v["transcribed"] else
                    '<span style="background:#fef3c7;color:#92400e;border-radius:999px;'
                    'padding:2px 9px;font-size:12px;font-weight:600">Wachten</span>'
                )
                view_btn = (
                    f'<a href="/videos/transcript/{vtype}/{v["path"].stem}" '
                    f'class="btn btn-secondary" style="margin-right:6px">Bekijk</a>'
                    if v["transcribed"] else ""
                )
                transcribe_btn = (
                    f'<form method="post" action="/videos/transcribe" style="display:inline">'
                    f'<input type="hidden" name="video_type" value="{vtype}">'
                    f'<input type="hidden" name="filename" value="{v["name"]}">'
                    f'<button type="submit" class="btn btn-primary">Transcribeer</button>'
                    f'</form>'
                    if not v["transcribed"] else ""
                )
                rows += (
                    f"<tr>"
                    f'<td style="font-weight:500">{v["name"]}</td>'
                    f'<td class="hide-sm">{v["size"]}</td>'
                    f'<td class="hide-sm">{v["duration"]}</td>'
                    f'<td>{badge}</td>'
                    f'<td style="white-space:nowrap">{view_btn}{transcribe_btn}</td>'
                    f"</tr>"
                )
            table = (
                f'<table><thead><tr>'
                f'<th>Bestandsnaam</th>'
                f'<th class="hide-sm">Grootte</th>'
                f'<th class="hide-sm">Duur</th>'
                f'<th>Status</th>'
                f'<th>Acties</th>'
                f'</tr></thead><tbody>{rows}</tbody></table>'
            )
        else:
            table = f'<div class="empty">Geen video\'s in {vname} — upload hieronder.</div>'

        # upload form
        upload = (
            f'<div style="padding:16px 20px;background:#f9fafb;border-top:1px solid #f3f4f6">'
            f'<form method="post" action="/videos/upload" enctype="multipart/form-data" '
            f'style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">'
            f'<input type="hidden" name="video_type" value="{vtype}">'
            f'<input type="file" name="file" accept=".mp4,.mov,.mkv,.m4v" required '
            f'style="flex:1;min-width:200px">'
            f'<button type="submit" class="btn" '
            f'style="background:{color};color:#fff">Uploaden naar {vtype.upper()}</button>'
            f'</form>'
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
        f'{sections_html}'
        f'</div>'
    )
    return _page_shell("Video's", "/videos", body)


# ── POST /videos/upload ───────────────────────────────────────────────────────

@app.post("/videos/upload")
async def videos_upload(
    file: UploadFile = File(...),
    video_type: str  = Form(...),
):
    if video_type not in VIDEO_TYPES:
        return HTMLResponse("Ongeldig videotype", status_code=400)

    dest_dir = VIDEOS_DIR / video_type
    dest_dir.mkdir(parents=True, exist_ok=True)

    # sanitise filename
    safe_name = re.sub(r"[^\w.\-]", "_", Path(file.filename).name)
    dest = dest_dir / safe_name

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return RedirectResponse("/videos", status_code=303)


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
    return RedirectResponse("/videos", status_code=303)


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
