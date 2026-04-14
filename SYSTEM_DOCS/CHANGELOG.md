# Changelog

All notable changes to the medical-rag system are recorded here.
Format: `[YYYY-MM-DD] — description (git commit)`

---

## 2026-04-14

### Infrastructure provisioned
- Hetzner CX53 server set up (16 vCPU, 30 GiB RAM, 301 GB disk)
- Docker 29.1.3 and docker-compose v1.29.2 installed

### Docker stack deployed (`8b14570`)
- `docker-compose.yml` written with Qdrant and Ollama services
- Memory and CPU limits set per service (Qdrant: 8 GB / 6 CPU; Ollama: 16 GB / 8 CPU)
- Healthchecks implemented using bash TCP redirects (no curl/wget in images)
- Both containers confirmed Up and healthy

### Ollama model pulled
- `llama3.1:8b` (4.92 GB, Q4_K_M) pulled into `./data/ollama/`
- `llama3.1:70b` evaluated and rejected — exceeds available RAM when running alongside Qdrant

### Ingestion pipeline written (`8b14570`)
- `scripts/ingest_books.py` — supports PDF (Docling) and EPUB (ebooklib + BeautifulSoup4)
- Embedding: `BAAI/bge-large-en-v1.5` (1024-dim) via LlamaIndex HuggingFace integration
- Chunking: 512 tokens / 64 overlap / SentenceSplitter
- Images extracted as PNG at 2× scale into `data/extracted_images/`
- EPUB three-pass image extraction with cross-reference map for anatomy atlases
- Qdrant collection auto-created on first run with Cosine / 1024-dim config
- Idempotent via `chunk_hash` (MD5 fingerprint)

### Git repository initialised (`8b14570`)
- `git init`, branch renamed to `main`
- `.gitignore` excludes: `books/`, `*.pdf`, `*.epub`, `.env*`, `data/`
- First commit pushed to https://github.com/abiere/medical-rag-state (private)

### `PROJECT_STATE.md` created (`8b14570`)
- Documents server specs, folder structure, container state, pipeline design, pending tasks, known issues
- Convention: updated and committed after every significant task

### `CLAUDE.md` standing instruction added (`447d5e7`)
- Rule: after every significant task, commit and push `PROJECT_STATE.md`

### State HTTP server deployed (`6bb40df`)
- `serve_state.py` — Python `http.server` serving project directory on port 8080
- `/etc/systemd/system/medical-rag-state.service` — enabled at boot, `Restart=always`
- `PROJECT_STATE.md` accessible at http://178.104.77.146:8080/PROJECT_STATE.md

### System documentation initialised *(this commit)*
- `SYSTEM_DOCS/REQUIREMENTS.md` — functional requirements
- `SYSTEM_DOCS/ARCHITECTURE.md` — current stack and planned components
- `SYSTEM_DOCS/CHANGELOG.md` — this file
- `SYSTEM_DOCS/TEST_REPORT.md` — placeholder
- `SYSTEM_DOCS/CONTEXT.md` — compact session loader

### Ingestion pipeline — major update *(this commit)*

**scripts/ingest_books.py** rewritten:
- Scanned PDF auto-detection: density pre-scan via pypdf; EasyOCR enabled if < 50 chars/page
- Figure naming changed to `{slug}_p{page}_fig{n}.png` (was MD5 hash — now human-readable)
- New Qdrant payload fields: `caption`, `figure_labels`, `image_type`, `image_description`, `figure_number`
- Figure label extraction via EasyOCR (lazy-init singleton, CPU mode)
- Ollama vision description (LLaVA if loaded; "pending" otherwise)
- Figure number detection: regex for `Fig./Figure/Afb./Abb.` patterns
- Full citation object on every chunk: loaded from `books_metadata.json`, APA + Vancouver formats
- Processing logs per book → `data/processing_logs/{slug}.json`
- `data/image_memory.json` initialised on first run
- `extract_pdf` / `extract_epub` now return `(sections, stats)` tuple

**scripts/fetch_book_metadata.py** (new):
- EPUB OPF metadata extraction (dc:title, dc:creator, dc:identifier, dc:publisher, dc:date)
- PDF XMP + DocInfo extraction
- ISBN regex extraction from filename as fallback
- OpenLibrary API: full metadata by ISBN; title search as fallback
- Google Books API: description, categories, language, thumbnail
- Citation generation: APA 7th, Vancouver (ICMJE), Chicago 17th
- `data/books_metadata.json` creation and update
- CLI: `--books-dir`, `--file`, `--isbn`, `--refresh --slug`

**data/books_metadata.json** (new): empty template, populated by fetch_book_metadata.py

**SYSTEM_DOCS/TECHNICAL_DESIGN.md** (new): full technical reference documenting
ingestion flow, scanned-PDF detection, figure extraction, bibliographic metadata
pipeline, citation formats (APA/Vancouver/Chicago), Qdrant payload schema,
image memory, processing logs, pre/post checks.

### Content types, video transcription, device extraction *(this commit)*

**scripts/ingest_books.py** extended:
- `content_type` field on every Qdrant chunk (5 types: medical_literature, training_nrt/qat, device_pemf/rlt)
- `--content-type` CLI arg; collection auto-derived from content type
- PEMF/RLT structured extraction: setting, program, intensity_range, duration_minutes, indication, contraindication, body_region
- `see_also` cross-reference field on all chunks
- `_collection_for_content_type()` router; `CONTENT_TYPE_COLLECTION_MAP` constant
- `_ensure_video_document_links()` init function

**scripts/transcribe_videos.py** (new):
- Whisper `medium` model, Dutch language hint; idempotent transcript cache
- ffmpeg audio extraction (16 kHz mono WAV)
- Saves `data/transcripts/{stem}.json` + `.txt` per video
- Auto-links videos to related PDFs by name matching
- `data/video_document_links.json` updated per run
- Optional `--ingest` flag to push segments into Qdrant
- Content types: training_nrt, training_qat, device_pemf, device_rlt
- CLI: `--type`, `--file`, `--model`, `--language`, `--ingest`, `--dry-run`

**scripts/ingest_text.py** (new):
- Ingests `.txt` / `.md` files into Qdrant without PDF/EPUB pipeline
- Paragraph-aware chunking with sentence-level fallback
- Full citation metadata (APA + Vancouver)
- Updates `books_metadata.json` with `media_type: "text"`, `internal_only: true`
- CLI: `--file`, `--content-type`, `--title`, `--author`, `--year`, `--publisher`

**New directories:** `videos/nrt/`, `videos/qat/`, `videos/pemf/`, `videos/rlt/`,
`data/transcripts/`, `data/device_settings/` — each with README.md

**New data files:** `data/video_document_links.json` (empty template, tracked in git)

**SYSTEM_DOCS/TECHNICAL_DESIGN.md** extended:
- Section 10: Content Types (table + ingestion commands per type)
- Section 11: Video Transcription Pipeline (Whisper model tradeoffs, flow diagram, idempotency)
- Section 12: Multi-Collection Search Strategy (query flow, Qdrant filter examples)

**SYSTEM_DOCS/REQUIREMENTS.md** extended:
- FR-7: Video transcription
- FR-8: PEMF/RLT structured settings extraction
- FR-9: Plain text/Markdown import
- NFR-6: Unified multi-collection search

**PROJECT_STATE.md** and **CONTEXT.md** updated with new folder structure, Qdrant collections, stack table, and ingestion commands.

### Tailscale + UFW security (`fad9f7c`)
- Tailscale installed and active — server accessible at `100.66.194.55` (Tailscale only)
- UFW firewall active — all public ingress blocked; allow SSH + `tailscale0` only
- Old `medical-rag-state.service` (port 8080) stopped and disabled
- Public IP `178.104.77.146` no longer reachable from outside

### FastAPI dashboard live (`e6826a0` + `fad9f7c`)
- `web/app.py` — FastAPI + Uvicorn on port 8000, systemd `medical-rag-web.service`
- Dashboard: CPU/RAM/disk progress bars, Qdrant + Ollama health cards, RAG stats, dir sizes
- 30 s auto-refresh, Dutch interface, no external CSS/JS dependencies (inline HTML only)
- Jinja2 version conflict resolved — all pages use inline HTML string generation
- Company name corrected to `NRT-Amsterdam.nl` throughout

### Comprehensive test suite (`dc8ad99`)
- `scripts/run_tests.py` — 4 classes, 24 tests; 24/24 passing
- Classes: InfrastructureTests, PipelineTests, QualityTests, IntegrationTests
- Results written to `SYSTEM_DOCS/TEST_REPORT.md` and `## Test status` in `CONTEXT.md`
- Auto git add + commit + push after every run
- Deploy gate added to `CLAUDE.md` — no deploy if any test FAIL or ERROR

### Nightly maintenance pipeline
- `scripts/nightly_maintenance.py` — 6 phases: pre_check, qdrant, consistency, software, cleanup, backup
- Writes `SYSTEM_DOCS/MAINTENANCE_REPORT.md` and updates `## Maintenance status` in `CONTEXT.md`
- systemd timer `medical-rag-maintenance.timer` at 00:30 UTC (`Persistent=true`, `RandomizedDelaySec=120`)
- systemd timer `medical-rag-tests.timer` at 00:00 UTC (daily test run)
- Qdrant snapshots: max 7 per collection; metadata backups: max 30 daily copies
- Weekly git tag on Sundays; git push after every maintenance run

### Video transcription pipeline + /videos page
- `ffmpeg` installed (apt) — `ffmpeg version 6.1.1-3ubuntu5`
- `openai-whisper` installed — Whisper `medium` model, Dutch language hint
- `scripts/transcribe_videos.py` — idempotent transcription; saves `data/transcripts/{stem}.json` + `.txt`
- `GET /videos` — four-section overview (NRT / QAT / PEMF / RLT) with per-video metadata
- `POST /videos/upload` — file upload with filename sanitisation
- `POST /videos/transcribe` — background task via FastAPI `BackgroundTasks`
- `GET /videos/transcript/{type}/{stem}` — timestamped segment viewer
- Treatment method names corrected: Neural Reset Therapy, Quantum Alignment Technique, Pulsed Electromagnetic Field, Red Light Therapy

### All ingestion dependencies installed
- `docling`, `easyocr`, `qdrant-client`, `sentence-transformers`, `llama-index` + integrations
- `pypdf`, `pillow`, `numpy`, `opencv-python-headless` (headless — no libGL.so.1 required)
- `BAAI/bge-large-en-v1.5` embedding model cached and verified (1024-dim)
- Debian `jsonschema` conflict resolved with `--ignore-installed`
- OpenCV headless substituted for `opencv-python` to fix `libGL.so.1` ImportError

### Git identity
- `Axel Biere <axelbiere@gmail.com>` set as git user for all commits

---

## Pending

See `REQUIREMENTS.md` and `PROJECT_STATE.md § 7 Pending Tasks`.
