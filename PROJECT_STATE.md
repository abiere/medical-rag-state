# Medical RAG — Project State

> **Update this file at the end of every major step.**
> Captures server specs, architecture decisions, live container state, and pending work so any session can resume without re-reading the full conversation history.

---

## 1. Server

| Property | Value |
|---|---|
| Provider | Hetzner CX53 |
| vCPUs | 16 |
| RAM | 30 GiB usable (no swap) |
| Disk | 301 GB (`/dev/sda1`), ~17 GB used |
| OS Kernel | Linux 6.8.0-79-generic |
| Docker | 29.1.3 |
| docker-compose | 1.29.2 (v1 — use `docker-compose`, not `docker compose`) |
| Python | 3.12 (`/usr/bin/python3`) — no venv, packages installed with `--break-system-packages` |
| Git identity | Axel Biere `<axelbiere@gmail.com>` |

---

## 2. Security

| Property | Value |
|---|---|
| Tailscale IP | `100.66.194.55` |
| Public IP | `178.104.77.146` (blocked by UFW — do not use) |
| UFW | **Active** — deny all incoming by default |
| UFW rules | Allow SSH + all traffic on `tailscale0`; reject everything else |
| Port 8080 | **Disabled** — old `medical-rag-state.service` stopped and disabled |
| Port 8000 | FastAPI dashboard — reachable only via Tailscale |
| Port 6333/6334 | Qdrant — reachable only via Tailscale |
| Port 11434 | Ollama — reachable only via Tailscale |

All access to the server must go through Tailscale (`100.66.194.55`).

---

## 3. Folder Structure

```
/root/medical-rag/
├── books/                        # Drop PDFs/EPUBs here  ← EMPTY
├── videos/
│   ├── nrt/                      # NRT training videos  ← EMPTY
│   ├── qat/                      # QAT training videos  ← EMPTY
│   ├── pemf/                     # PEMF instruction videos  ← EMPTY
│   └── rlt/                      # RLT instruction videos  ← EMPTY
├── data/
│   ├── books_metadata.json       # Bibliographic metadata + citations (tracked in git)
│   ├── video_document_links.json # Video ↔ PDF cross-references (tracked in git)
│   ├── image_memory.json         # Axel's image selections per tissue (tracked in git)
│   ├── extracted_images/         # Saved figures — {slug}_p{page}_fig{n}.png
│   ├── transcripts/              # Whisper JSON + TXT transcripts
│   ├── device_settings/          # Curated PEMF/RLT settings files
│   ├── processing_logs/          # Per-book ingestion stats
│   ├── ollama/                   # Ollama model weights (Docker volume)
│   └── qdrant/                   # Qdrant vector storage (Docker volume)
├── web/
│   └── app.py                    # FastAPI dashboard + routes (:8000)
├── scripts/
│   ├── ingest_books.py           # PDF + EPUB ingestion (all content types)
│   ├── ingest_text.py            # Plain text / Markdown ingestion
│   ├── transcribe_videos.py      # Whisper video transcription + ingest
│   └── fetch_book_metadata.py    # OpenLibrary + Google Books metadata
├── SYSTEM_DOCS/                  # Technical documentation
├── CLAUDE.md                     # Standing instructions
├── PROJECT_STATE.md              # This file
└── docker-compose.yml
```

**Disk usage (2026-04-14):** `/dev/sda1` — 301 GB total, 17 GB used (6%), 272 GB free.
**books/ and videos/:** All empty — no content ingested yet.

---

## 4. Infrastructure

### docker-compose.yml — key settings

| Service | Image | Ports | mem_limit | CPUs | Restart |
|---|---|---|---|---|---|
| `qdrant` | `qdrant/qdrant:latest` | 6333 (REST), 6334 (gRPC) | 8 GB | 6 | unless-stopped |
| `ollama` | `ollama/ollama:latest` | 11434 | 16 GB | 8 | unless-stopped |

**RAM budget:** Qdrant 8 GB + Ollama 16 GB + OS ~1.2 GB + FastAPI ~0.1 GB = ~25 GB of 30 GB. ~5 GB headroom.

**Qdrant performance tuning applied:**
- `MAX_SEARCH_THREADS: 8`
- `INDEXING_THRESHOLD_KB: 20000`
- `MEMMAP_THRESHOLD_KB: 50000`
- `HNSW M: 16`, `ef_construct: 100`

**Healthcheck approach:** Both images lack `curl` and `wget`. Healthchecks use bash TCP redirects:
```bash
exec 3<>/dev/tcp/localhost/PORT && echo -e 'GET /path HTTP/1.0\r\n\r\n' >&3 && grep -q 'expected_string' <&3
```

### Live Container State *(last checked: 2026-04-14 ~18:30 UTC)*

| Container | Image | Ports | Status | RAM used | CPU |
|---|---|---|---|---|---|
| `qdrant` | `qdrant/qdrant:latest` | 6333 (REST), 6334 (gRPC) | Up, **healthy** | 32 MiB / 8 GiB | 0.23% |
| `ollama` | `ollama/ollama:latest` | 11434 | Up, **healthy** | 12 MiB / 16 GiB | 0.00% |

### Ollama Models

| Model | Size | Purpose |
|---|---|---|
| `llama3.1:8b` | 4.92 GB | Medical text analysis and RAG responses |

`llama3.1:70b` was evaluated and rejected — requires ~40 GB+ quantized, exceeds available RAM when running alongside Qdrant and the OS.

### Qdrant Collections

No collections yet. The collections are created automatically on the first run of `ingest_books.py`.

| Collection | content_type(s) | Status |
|---|---|---|
| `medical_literature` | `medical_literature` | Not yet created (no books ingested) |
| `training_materials` | `training_nrt`, `training_qat` | Not yet created |
| `device_protocols` | `device_pemf`, `device_rlt` | Not yet created |

Collection config (applied at creation time):
- Vector size: **1024** (matches `BAAI/bge-large-en-v1.5`)
- Distance: **Cosine**
- Payload field `image_links` is a native JSON array — filterable without a separate index

---

## 5. Systemd Services

| Service | Unit file | Port | Status |
|---|---|---|---|
| `medical-rag-web` | `/etc/systemd/system/medical-rag-web.service` | 8000 | **Active (running)** |
| `medical-rag-state` | `/etc/systemd/system/medical-rag-state.service` | 8080 | **Disabled / stopped** |

**`medical-rag-web.service`** (FastAPI):
```ini
[Service]
WorkingDirectory=/root/medical-rag/web
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --no-access-log
Restart=always
User=root
```
Dashboard accessible at: `http://100.66.194.55:8000` (Tailscale only)

---

## 6. Web Interface (`web/app.py`)

**Framework:** FastAPI + Uvicorn (inline HTML — no Jinja2 templates)

**Note on Jinja2:** System jinja2 (`/usr/lib/python3/dist-packages/jinja2`) conflicts with starlette's LRU cache using dict keys. Fixed by generating HTML as inline strings — no `TemplateResponse` used.

| Route | Description | Status |
|---|---|---|
| `GET /` | Dashboard — system stats, service health, RAG stats, dir sizes | **Live** |
| `GET /health` | JSON health check | **Live** |
| `GET /library` | Book management — upload, metadata, ingestion | Planned |
| `GET /images` | Image browser with tissue/structure filter | Planned |
| `GET /protocols` | Protocol builder + Word document generation | Planned |
| `GET /search` | Multi-collection RAG search | Planned |
| `GET /videos` | Video upload + Whisper transcription trigger | Planned |

Dashboard features:
- System stats: CPU%, RAM, disk with progress bars
- Service health: Qdrant (collections + vector counts), Ollama (models + sizes)
- Docker container status
- RAG stats: books total/ingested/pending, chunks, figures, transcripts, protocols
- Directory sizes: books/, data/qdrant/, data/ollama/
- Quick action buttons for all major workflows
- Auto-refresh every 30 seconds
- Mobile-friendly, Dutch interface, no external CSS/JS dependencies

---

## 7. Ingestion Pipeline (`scripts/ingest_books.py`)

### Supported formats
| Extension | Backend |
|---|---|
| `.pdf` | Docling (`PdfPipelineOptions`) |
| `.epub` | ebooklib + BeautifulSoup4 (Docling does not support EPUB — upstream issue #515) |

### Embedding model
`BAAI/bge-large-en-v1.5` — 1024-dim, strong on medical/scientific text, runs fully locally, cached in `~/.cache/huggingface` after first download.

### Chunking
- `CHUNK_SIZE = 512` tokens
- `CHUNK_OVERLAP = 64` tokens
- Splitter: `SentenceSplitter` (LlamaIndex) — respects sentence boundaries

### Section / page output format
Both extractors return the same `list[dict]` shape:

```python
{
    "page_number":    int,        # PDF: 1-based page; EPUB: spine position
    "section_number": int,        # same value, unified query field
    "text":           str,        # body text + inline [Image: …] markers
    "image_links":    list[str],  # absolute paths to saved image files
    "source_file":    str,        # filename only
    "source_path":    str,        # absolute path
    "format":         str,        # "pdf" or "epub"
    "chunk_hash":     str,        # MD5 fingerprint for idempotency
}
```

### Qdrant payload / metadata
All fields above are stored as Qdrant payload. Fields excluded from LLM context and embedding text (paths are not semantically useful): `source_path`, `chunk_hash`, `image_links`.

---

## 8. Image Extraction Logic

### PDF — Docling `PictureItem`

```python
pipeline_opts = PdfPipelineOptions(generate_picture_images=True, images_scale=2.0)
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts)}
)
result = converter.convert(path)

for element, _ in result.document.iterate_items():
    if isinstance(element, PictureItem):
        page_no   = element.prov[0].page_no        # 1-based
        pil_image = element.image.pil_image         # PIL.Image
        caption   = element.caption_text(doc=doc)  # str | ""
```

Images are saved as PNG regardless of source format. Filename: `{slug}_p{page}_fig{n}.png`.

### EPUB — ebooklib + BeautifulSoup4 (three-pass)

Three-pass extraction with cross-reference map for anatomy atlases where images live in a "Plates" chapter and descriptions live in a separate "Descriptions / Legends" chapter, linked by HTML anchors.

### Image filename convention
```
{slug}_p{page}_fig{n}.png
# e.g. sobotta_vol1_p147_fig1.png
```

---

## 9. Installed Python Dependencies

| Package | Status | Purpose |
|---|---|---|
| `fastapi` | **Installed** | Web framework |
| `uvicorn` | **Installed** | ASGI server |
| `httpx` | **Installed** | Async HTTP client (service health checks) |
| `psutil` | **Installed** | System metrics (CPU, RAM, disk) |
| `python-multipart` | **Installed** | File upload support |
| `aiofiles` | **Installed** | Async file I/O |
| `jinja2` | Installed (system) | **Not used** — version conflict with starlette LRU cache |
| `ebooklib` | **Installed** | EPUB parsing |
| `beautifulsoup4` | **Installed** | HTML parsing for EPUB |
| `lxml` | **Installed** (system dep) | XML/HTML parser |
| `docling` | Not installed | PDF extraction, figure detection |
| `easyocr` | Not installed | OCR for scanned PDFs + figure labels |
| `openai-whisper` | Not installed | Video transcription |
| `llama-index` | Not installed | Chunking, VectorStoreIndex |
| `llama-index-vector-stores-qdrant` | Not installed | Qdrant backend |
| `llama-index-embeddings-huggingface` | Not installed | Local embeddings |
| `qdrant-client` | Not installed | Qdrant REST/gRPC client |
| `pypdf` | Not installed | PDF text density pre-scan |
| `pillow` | Not installed | PIL image handling |

**Install remaining dependencies:**
```bash
pip install docling docling-core easyocr openai-whisper \
    llama-index llama-index-vector-stores-qdrant \
    llama-index-embeddings-huggingface \
    qdrant-client pypdf pillow numpy \
    --break-system-packages
apt-get install -y ffmpeg
```

---

## 10. Pending Tasks

- [ ] **Install ingestion dependencies** — `pip install docling easyocr openai-whisper llama-index qdrant-client pypdf pillow --break-system-packages` + `apt install ffmpeg`
- [ ] **Add books** — Drop `.pdf`/`.epub` into `./books/`, run `fetch_book_metadata.py` then `ingest_books.py --content-type medical_literature`
- [ ] **Add training videos** — Drop `.mp4` into `./videos/nrt/` and `./videos/qat/`, run `transcribe_videos.py --type nrt --ingest`
- [ ] **Add device docs** — Drop PEMF/RLT PDFs or `.md` settings files, run ingestion with `--content-type device_pemf` / `device_rlt`
- [ ] **Build remaining web pages** — `/library`, `/images`, `/protocols`, `/search`, `/videos`
- [ ] **Multi-collection query** — Build `query_rag.py` that queries all three collections in parallel and merges results
- [ ] **Word output** — Generate `.docx` treatment protocols (§1 Klachtbeeld / §2 Behandeling / §3 Bijlagen)
- [ ] **Tailscale ACL** — Restrict which Tailscale devices can access the server

---

## 11. Known Issues

| Issue | Severity | Notes |
|---|---|---|
| EPUB has no real page numbers | Low | `page_number` stores spine position (1-based reading order). Acceptable for retrieval; note in any UI. |
| Docling EPUB support | Low | Tracked upstream as issue #515. Current workaround (ebooklib) is full-featured for the anatomy use case. |
| No swap configured | Medium | If both Qdrant and Ollama are under peak load simultaneously and exceed their memory limits, the kernel OOM killer may intervene. Monitor with `docker stats` during heavy ingestion. |
| Jinja2 version conflict | Low | System jinja2 conflicts with pip-installed starlette's LRU cache (`unhashable type: 'dict'`). Resolved by generating all HTML as inline strings — no templates used. |
| `docker-compose` v1 bug with new images | Resolved | v1.29.2 throws `KeyError: 'ContainerConfig'` on recreate. Workaround: always `docker-compose down` before `docker-compose up -d`. |
