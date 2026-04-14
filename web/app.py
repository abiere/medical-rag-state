from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx, psutil, subprocess, json, os
from pathlib import Path
from datetime import datetime

app = FastAPI()
BASE = Path("/root/medical-rag")

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
