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
│   ├── fetch_book_metadata.py    # OpenLibrary + Google Books metadata
│   ├── run_tests.py              # Test suite → SYSTEM_DOCS/TEST_REPORT.md
│   └── nightly_maintenance.py   # Snapshots, consistency, cleanup, git push
├── SYSTEM_DOCS/                  # Technical documentation
├── CLAUDE.md                     # Standing instructions
├── PROJECT_STATE.md              # This file
└── docker-compose.yml
```

**Disk usage (2026-04-14):** `/dev/sda1` — 301 GB total, 17 GB used (6%), 272 GB free.
**Disk usage (2026-04-15):** `/dev/sda1` — 301 GB total, ~24 GB used (QAT videos +7.5 GB), ~265 GB free.  
**videos/qat/:** 15 × MP4 bestanden — transcriptie bezig via `transcription-queue.service`.

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
| `transcription-queue` | `/etc/systemd/system/transcription-queue.service` | — | **Active (running) — processing QAT** |
| `medical-rag-state` | `/etc/systemd/system/medical-rag-state.service` | 8080 | **Disabled / stopped** |

### Systemd Timers

| Timer | Service | Schedule | Purpose |
|---|---|---|---|
| `medical-rag-tests.timer` | `medical-rag-tests.service` | Daily 00:00 UTC | Run test suite → TEST_REPORT.md |
| `medical-rag-maintenance.timer` | `medical-rag-maintenance.service` | Daily 00:30 UTC | Snapshots, consistency, cleanup, git push |

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
| `GET /videos` | Video overview by type; per-video metadata + transcription status | **Live** |
| `POST /videos/upload` | Upload video file to correct type directory | **Live** |
| `POST /videos/transcribe` | Enqueue video in `/tmp/transcription_queue.json` (queue service picks up) | **Live** |
| `GET /videos/status/{type}/{filename}` | Queue status: done/running/queued/waiting | **Live** |
| `GET /videos/transcript/{type}/{stem}` | Timestamped segment viewer | **Live** |
| `GET /library` | Book management — upload, metadata, ingestion | Planned |
| `GET /images` | Image browser with tissue/structure filter | Planned |
| `GET /protocols` | Protocol builder + Word document generation | Planned |
| `GET /search` | Multi-collection RAG search | Planned |

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
| `docling` | **Installed** | PDF extraction, figure detection |
| `easyocr` | **Installed** | OCR for scanned PDFs + figure labels |
| `openai-whisper` | **Installed** | Video transcription |
| `ffmpeg` | **Installed** (apt) | Audio extraction for Whisper |
| `llama-index` | **Installed** | Chunking, VectorStoreIndex |
| `llama-index-vector-stores-qdrant` | **Installed** | Qdrant backend |
| `llama-index-embeddings-huggingface` | **Installed** | Local embeddings |
| `sentence-transformers` | **Installed** | `BAAI/bge-large-en-v1.5` embeddings |
| `qdrant-client` | **Installed** | Qdrant REST/gRPC client |
| `pypdf` | **Installed** | PDF text density pre-scan |
| `pillow` | **Installed** | PIL image handling |
| `opencv-python-headless` | **Installed** | Headless OpenCV (no libGL.so.1) |

**All ingestion dependencies installed.** `BAAI/bge-large-en-v1.5` model cached and verified (1024-dim).

---

## 10. Pending Tasks

- [ ] **Add books** — Drop `.pdf`/`.epub` into `./books/`, run `fetch_book_metadata.py` then `ingest_books.py --content-type medical_literature`
- [~] **QAT-videos transcriberen** — 15 videos in sequentiële queue via `transcription-queue.service`; controleer `tail -20 /var/log/transcription_queue.log`
- [ ] **NRT-videos transcriberen** — Drop `.mp4` into `./videos/nrt/`, start via `/videos` pagina of `transcribe_videos.py --type nrt`
- [ ] **Add device docs** — Drop PEMF/RLT PDFs or `.md` settings files, run ingestion with `--content-type device_pemf` / `device_rlt`
- [ ] **Build `/library` page** — Book upload, metadata cards, ingestion trigger, processing status
- [ ] **Build `/search` page** — Multi-collection RAG search with citation display
- [ ] **Build `/images` page** — Image browser with tissue/structure filter
- [ ] **Build `/protocols` page** — Protocol builder + Word document generation
- [ ] **Build `query_rag.py`** — Multi-collection search across all three Qdrant collections in parallel
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
| Queue file `/tmp/transcription_queue.json` lost on reboot | Low | systemd `Restart=on-failure` restarts the service but the queue file lives in `/tmp` which is cleared on reboot. The startup scan repopulates from the filesystem automatically — any untranscribed video is re-queued. |

---

## 12. Session 2026-04-14 (evening) — Video Transcription System

### Wat gebouwd

| Feature | Status |
|---|---|
| Upload progress bar via XHR (% + MB/s) | ✅ |
| Auto-transcribe na upload (geen knop klik nodig) | ✅ |
| Status endpoint via logfile mtime detectie | ✅ |
| Elapsed timer "Bezig... 0:12" in UI per video | ✅ |
| RAM warning bij >3 parallelle transcripties | ✅ |
| Multi-file select op upload input | ✅ |
| Batch start 15 QAT-videos via curl loop | ✅ |

### Bug fix: `_run_transcription` args
- Removed `--type` (mutually exclusive with `--file` in argparse — caused silent failure)
- Added `--content-type training_qat` etc. via `_CONTENT_TYPE_MAP`
- Added log output to `/tmp/transcribe_{filename}.log` for debugging

### Commits
| Hash | Beschrijving |
|---|---|
| `8b9ee02` | feat: upload progress, auto-transcribe, progress polling |
| `3522abc` | fix: transcription args, auto-transcribe, spinner timer, multi-select, batch start QAT |
| `439cb6c` | fix: status detection via logfile, RAM warning |

### Transcriptie status 22:30 UTC
- **15 QAT-videos** gestart via batch curl loop
- Whisper `medium` model, CPU-only (FP32), ~40–90 min per video verwacht
- Logs beschikbaar in `/tmp/transcribe_*.log`
- Verwacht klaar: vroeg op 15-04-2026

### Volgende sessie — prioriteiten
1. Controleer hoeveel QAT-transcripties klaar zijn (`ls data/transcripts/*.json | wc -l`)
2. Bouw `/library` pagina — PDF/EPUB upload, metadata cards, ingestie trigger
3. Bouw `/search` pagina — multi-collectie RAG zoekopdracht met citaten
4. Start NRT-video transcripties als RAM beschikbaar is

---

## 13. Session 2026-04-15 — Sequentiële transcriptie queue

### Probleem opgelost
- 13+ parallelle Whisper processen → OOM-killed door Linux kernel
- Oplossing: sequentiële queue via systemd service (één video tegelijk)

### Gebouwd
- `scripts/transcription_queue.py` — queue manager; startup scan + loop; EXIT wanneer leeg
- `/etc/systemd/system/transcription-queue.service` — enabled, auto-start na `medical-rag-web`
- `web/app.py` — `_run_transcription` schrijft naar `/tmp/transcription_queue.json` (geen subprocess meer)
- `web/app.py` — `/videos/status` endpoint: 4-state check via `current.json` + `queue.json`
- UI badges: Klaar (groen) / Bezig… (blauw spinner) / In wachtrij (geel) / Wachten (grijs)
- `run_tests.py` — 4 nieuwe tests voor queue systeem

### Commits
| Hash | Beschrijving |
|---|---|
| `014d5a7` | feat: sequential transcription queue, systemd service, queued status |
| `ae5f7e3` | fix: strip whitespace in status filename comparison |

### Status transcripties 06:30 UTC
- `Anti-Inflammatory_Procedure.mp4` → **DONE** (eerste klaar)
- `Connection_to_the_Brain.mp4` → **RUNNING** (tweede in progress)
- 13 overige QAT-videos → **QUEUED**
- Verwacht klaar: morgenochtend vroeg

### Volgende sessie
```bash
! tail -20 /var/log/transcription_queue.log   # voortgang
! ls /root/medical-rag/data/transcripts/ | wc -l  # hoeveel klaar
```
Daarna: `/library` pagina bouwen.
