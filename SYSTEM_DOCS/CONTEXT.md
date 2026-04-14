# CONTEXT — Session Loader

> Read this file at the start of every session.
> Full detail lives in PROJECT_STATE.md and SYSTEM_DOCS/*.

---

## What this system is

A **private, fully-local RAG system** for medical and acupuncture literature.
Built for **Axel Biere** (NRT-Amsterdam.nl), complementary therapist, Amsterdam.
Access via **Tailscale only**. All inference runs on a single Hetzner server.

> Full practice context — modalities, protocol structure, image requirements, writing rules:
> **→ read `SYSTEM_DOCS/PRACTICE_CONTEXT.md` before generating any content**

**Treatment modalities (always combined):** NRT · QAT · GTR · Tit Tar · PEMF · RLT

**Primary outputs:**
1. **Word documents** — treatment protocols: §1 Klachtbeeld · §2 Behandeling (with anatomical + acupuncture images) · §3 Bijlagen/Rationale (page-cited)
2. **Blog articles** for nrt-amsterdam.nl — accessible prose, grounded in retrieved literature, Dutch writing rules apply
3. **Ad hoc Q&A** — free-form questions answered against the book database, with citations

All outputs cite exact page numbers and source documents. No hallucinated references.

---

## Server

| Property | Value |
|---|---|
| Host | Hetzner CX53 — **100.66.194.55 (Tailscale only)** — public IP blocked by UFW |
| vCPUs / RAM / Disk | 16 / 30 GiB / 301 GB |
| OS | Ubuntu, kernel 6.8.0-79-generic |
| Docker | 29.1.3 — use `docker-compose` (v1), NOT `docker compose` |
| Python | 3.12 system — `pip install --break-system-packages` |
| Git identity | Axel Biere `<axelbiere@gmail.com>` |
| UFW | **Active** — deny all except tailscale0 and loopback |

---

## Running services

| Service | How | Port | State |
|---|---|---|---|
| Qdrant | Docker (`docker-compose`) | 6333 REST, 6334 gRPC | Up, healthy |
| Ollama | Docker (`docker-compose`) | 11434 | Up, healthy |
| FastAPI dashboard | systemd `medical-rag-web.service` | **8000** | **Active** |

**Ollama model loaded:** `llama3.1:8b` (4.92 GB, Q4_K_M)  
**Dashboard:** `http://100.66.194.55:8000` (Tailscale only)

## Systemd timers

| Timer | Service | Schedule | Purpose |
|---|---|---|---|
| `medical-rag-tests.timer` | `medical-rag-tests.service` | Daily 00:00 UTC | Run test suite → TEST_REPORT.md |
| `medical-rag-maintenance.timer` | `medical-rag-maintenance.service` | Daily 00:30 UTC | Snapshots, consistency, cleanup, git push |

---

## Key paths

```
/root/medical-rag/
├── books/                        ← drop PDFs/EPUBs here (empty — no books ingested yet)
├── videos/{nrt,qat,pemf,rlt}/   ← drop .mp4 files here
├── data/
│   ├── books_metadata.json       ← bibliographic metadata + citations
│   ├── video_document_links.json ← video ↔ PDF cross-references
│   ├── image_memory.json         ← Axel's preferred images per tissue
│   ├── extracted_images/         ← saved figures: {slug}_p{page}_fig{n}.png
│   ├── transcripts/              ← Whisper JSON + TXT
│   ├── device_settings/          ← PEMF/RLT settings files
│   └── processing_logs/          ← per-book ingestion stats
├── web/
│   └── app.py                    ← FastAPI dashboard (port 8000)
├── scripts/
│   ├── ingest_books.py           ← PDF + EPUB ingestion (all content types)
│   ├── ingest_text.py            ← plain text / Markdown ingestion
│   ├── transcribe_videos.py      ← Whisper transcription + ingest
│   ├── fetch_book_metadata.py    ← OpenLibrary + Google Books metadata
│   ├── run_tests.py              ← test suite → SYSTEM_DOCS/TEST_REPORT.md
│   └── nightly_maintenance.py   ← snapshots, consistency, cleanup, git push
├── backups/
│   ├── qdrant/                   ← Qdrant snapshots (kept 7 per collection)
│   └── metadata/                 ← daily JSON backups (kept 30)
├── docker-compose.yml
├── CLAUDE.md                     ← standing instructions (read before every task)
├── PROJECT_STATE.md              ← live server state (update & commit after each task)
└── SYSTEM_DOCS/
    ├── CONTEXT.md                ← this file
    ├── PRACTICE_CONTEXT.md       ← practitioner, modalities, protocol, image rules
    ├── REQUIREMENTS.md           ← FR + NFR
    ├── ARCHITECTURE.md           ← full stack description
    ├── TECHNICAL_DESIGN.md       ← ingestion, metadata, Qdrant payload, citations
    ├── CHANGELOG.md              ← dated history
    ├── TEST_REPORT.md            ← auto-updated by run_tests.py
    └── MAINTENANCE_REPORT.md     ← auto-updated by nightly_maintenance.py
```

---

## Stack

| Component | Role | Status |
|---|---|---|
| FastAPI + Uvicorn | Web layer — dashboard, upload, Q&A, generation | **Running** (port 8000) |
| Tailscale | Access control — VPN-only access | **Active** (100.66.194.55) |
| Qdrant | Vector store | Running |
| Ollama / llama3.1:8b | Local LLM inference | Running |
| ebooklib + BS4 | EPUB parsing (Docling doesn't support EPUB) | Installed |
| Docling | PDF parsing — text, images, page numbers | Not yet installed |
| EasyOCR | OCR for scanned PDFs + figure labels | Not yet installed |
| BAAI/bge-large-en-v1.5 | Local embeddings, 1024-dim | Not yet installed |
| OpenAI Whisper (local) | Video transcription | Not yet installed |
| ffmpeg | Audio extraction for Whisper | Not yet installed |
| LLaVA (vision) | Figure descriptions from images | Not yet pulled |
| python-docx | Word document output | Not yet installed |

---

## Qdrant collections

| Collection | content_type(s) | What goes in |
|---|---|---|
| `medical_literature` | `medical_literature` | Anatomy/clinical EPUBs + PDFs |
| `training_materials` | `training_nrt`, `training_qat` | NRT/QAT PDFs, video transcripts, text |
| `device_protocols` | `device_pemf`, `device_rlt` | Device manuals, settings, videos |

## Ingestion pipeline

```bash
# Step 1 — fetch metadata (once per new book)
python scripts/fetch_book_metadata.py --books-dir ./books

# Step 2a — medical books
python scripts/ingest_books.py --books-dir ./books --content-type medical_literature

# Step 2b — NRT/QAT plain text
python scripts/ingest_text.py --file books/QAT_Manual.txt \
  --content-type training_qat --title "QAT Manual"

# Step 2c — training videos
python scripts/transcribe_videos.py --type nrt --ingest
python scripts/transcribe_videos.py --type qat --ingest

# Step 2d — device PDFs
python scripts/ingest_books.py --books-dir ./books/pemf --content-type device_pemf
```

- Chunking: 512 tokens / 64 overlap / SentenceSplitter
- Qdrant collection auto-created on first run (Cosine / 1024-dim)
- Idempotent — `chunk_hash` prevents duplicate vectors
- Figures: `{slug}_p{page}_fig{n}.png` — deterministic, traceable
- Scanned PDFs: auto-detected (< 50 chars/page) → EasyOCR
- **Pre/post-check RAM and disk** before large runs

---

## Standing rules (from CLAUDE.md)

| Rule | When |
|---|---|
| `git add PROJECT_STATE.md && git commit -m "state: ..." && git push` | After every significant task |
| `python3 scripts/run_tests.py` — all tests pass before deploy | Before every deploy |
| `git tag -a v<date>-<desc>` | Before every significant change |
| Docker volume snapshot of `data/qdrant/` | Before any ingestion that modifies an existing collection |
| Update `CHANGELOG.md` with a dated entry | End of every session |

---

## Immediate next steps

1. **Install ingestion deps:** `pip install docling easyocr openai-whisper llama-index qdrant-client pypdf pillow --break-system-packages` + `apt install ffmpeg`
2. **Add books:** Drop `.pdf`/`.epub` into `./books/` → `fetch_book_metadata.py` → `ingest_books.py`
3. **Add videos:** Drop `.mp4` into `./videos/nrt/` and `./videos/qat/` → `transcribe_videos.py --ingest`
4. **Build `query_rag.py`** — multi-collection search across all three collections
5. **Build remaining web pages:** `/library`, `/images`, `/protocols`, `/search`, `/videos`
6. **Word output:** `.docx` treatment protocols (§1 Klachtbeeld / §2 Behandeling / §3 Bijlagen)

---

## Maintenance status

**Laatste run:** 14-04-2026 19:05 (15.6s)  
**Uitslag:** ⚠️ WARNING — 1 waarschuwing(en), 4 OK  

---

## Test status

**Laatste run:** 14-04-2026 19:16 (35.4s)  
**Uitslag:** ❌ MISLUKT — 22/24 geslaagd, 2 mislukt, 0 overgeslagen  
**Mislukt:** `test_pdf_text_extraction`, `test_figure_detection`

---

## Git / state tracking

- Repo: https://github.com/abiere/medical-rag-state (private)
- After every significant task:
  ```bash
  git add PROJECT_STATE.md && git commit -m "state: [description]" && git push
  ```
- Dashboard + live state: `http://100.66.194.55:8000` (Tailscale only)
