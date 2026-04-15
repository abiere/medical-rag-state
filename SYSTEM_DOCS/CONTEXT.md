# CONTEXT — Session Loader

> Read this file at the start of every session.
> Full detail lives in PROJECT_STATE.md and SYSTEM_DOCS/*.
> Live status: https://raw.githubusercontent.com/abiere/medical-rag-state/main/SYSTEM_DOCS/LIVE_STATUS.md  
> Backlog: https://raw.githubusercontent.com/abiere/medical-rag-state/main/SYSTEM_DOCS/BACKLOG.md

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
| FastAPI web interface | systemd `medical-rag-web.service` | **8000** | **Active** |
| Transcription queue | systemd `transcription-queue.service` | — | **Active, processing QAT videos** |
| ttyd browser terminal | systemd `ttyd.service` | **7682** | **Active** |

**Ollama model loaded:** `llama3.1:8b` (4.92 GB, Q4_K_M)  
**Dashboard:** `http://100.66.194.55:8000` (Tailscale only)  
**Browser terminal:** `http://100.66.194.55:7682` (Tailscale only)

## Systemd timers

| Timer | Service | Schedule | Purpose |
|---|---|---|---|
| `medical-rag-tests.timer` | `medical-rag-tests.service` | Daily 00:00 UTC | Run test suite → TEST_REPORT.md |
| `medical-rag-maintenance.timer` | `medical-rag-maintenance.service` | Daily 00:30 UTC | Snapshots, consistency, cleanup, git push |
| `sync-status.timer` | `sync-status.service` | Every 5 min | Write LIVE_STATUS.md → git push |

---

## Key paths

```
/root/medical-rag/
├── books/                        ← drop PDFs/EPUBs here (empty — no books ingested yet)
├── videos/
│   ├── nrt/                      ← NRT videos (0 files)
│   ├── qat/                      ← QAT videos (15 files, transcription in progress)
│   ├── pemf/                     ← PEMF videos (0 files)
│   └── rlt/                      ← RLT videos (0 files)
├── data/
│   ├── books_metadata.json       ← bibliographic metadata + citations
│   ├── video_document_links.json ← video ↔ PDF cross-references
│   ├── image_memory.json         ← Axel's preferred images per tissue
│   ├── extracted_images/         ← saved figures: {slug}_p{page}_fig{n}.png
│   ├── transcripts/              ← Whisper JSON + TXT (in progress, qat/)
│   ├── device_settings/          ← curated PEMF/RLT settings files
│   ├── processing_logs/          ← per-book ingestion stats
│   ├── ollama/                   ← model weights (Docker volume)
│   └── qdrant/                   ← vector storage (Docker volume)
├── web/
│   └── app.py                    ← FastAPI app (all routes, port 8000)
├── scripts/
│   ├── ingest_books.py           ← PDF + EPUB ingestion (all content types)
│   ├── ingest_text.py            ← plain text / Markdown ingestion
│   ├── transcribe_videos.py      ← Whisper transcription + ingest (called by queue)
│   ├── transcription_queue.py    ← sequential queue manager (systemd)
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
| Docling | PDF parsing — text, images, page numbers | **Installed** |
| EasyOCR | OCR for scanned PDFs + figure labels | **Installed** |
| BAAI/bge-large-en-v1.5 | Local embeddings, 1024-dim | **Installed** (cached) |
| OpenAI Whisper (local) | Video transcription | **Running** (via queue) |
| ffmpeg | Audio extraction for Whisper | **Installed** |
| LLaVA (vision) | Figure descriptions from images | Not yet pulled |
| python-docx | Word document output | Not yet installed |

---

## Transcription system

- **Queue manager:** `transcription-queue.service` (systemd, enabled, auto-start, auto-resume)
- **Sequential:** ONE Whisper process at a time — no OOM risk
- **Whisper flag:** `--task translate` — all transcripts produced in English
- **Queue file:** `/tmp/transcription_queue.json` — written by `POST /videos/transcribe`
- **Current job:** `/tmp/transcription_current.json` — present while running, removed on completion
- **Log:** `/var/log/transcription_queue.log`
- **Auto-ingest:** on completion, `ingest_transcript.py` is called → vectors pushed to Qdrant `video_transcripts` collection
- **Status endpoint:** `GET /videos/status/{video_type}/{filename}`
  → `done` / `running` / `queued` / `waiting`
- **UI badges:** Klaar (groen) / Bezig… (blauw spinner) / In wachtrij (geel) / Wachten (grijs)

**Transcription progress (2026-04-15 ~08:05):**
- Done: 3 (Anti-Inflammatory_Procedure, Connection_to_the_Brain, Emotional_Transformation_Technique)
- Running: Green_Square_Applications.mp4
- Queued: 11 remaining QAT videos
- Total: 15 QAT videos

Check progress:
```bash
tail -20 /var/log/transcription_queue.log
ls /root/medical-rag/data/transcripts/ | wc -l
cat /tmp/transcription_current.json
```

---

## AI Instructions (Lead Architect quality control)

Files at `config/ai_instructions/` — synced to `AI_INSTRUCTIONS/` on every 5-min push.

| File | Purpose |
|---|---|
| `AI_INSTRUCTIONS/nrt_qat_bridge.md` | How NRT/QAT uses medical literature |
| `AI_INSTRUCTIONS/protocol_structure.md` | What a good protocol looks like |
| `AI_INSTRUCTIONS/tagging_rules.md` | How chunks are tagged (editable, affects next ingest) |
| `AI_INSTRUCTIONS/learning_log.md` | What the AI has learned |
| `AI_INSTRUCTIONS/feedback_history.md` | Approved/rejected content |

Raw URLs (GitHub):
- `AI_INSTRUCTIONS/tagging_rules.md`
- `AI_INSTRUCTIONS/nrt_qat_bridge.md`

---

## Qdrant collections

| Collection | Source | What goes in | Status |
|---|---|---|---|
| `medical_library` | `medical_literature` subdir | All external medical books (Deadman, Sobotta, Guyton, etc.) | **Created** |
| `nrt_qat_curriculum` | `nrt_qat` subdir | NRT + QAT curriculum, treatment guides | **Created** |
| `device_documentation` | `device` subdir | PEMF mat manual, RLT FlexBeam docs | Not yet created |
| `video_transcripts` | auto-ingest | QAT video transcripts | **Created, growing** |

## Ingestion pipeline

```bash
# Step 1 — fetch metadata (once per new book)
python scripts/fetch_book_metadata.py --books-dir ./books

# Step 2a — medical books
python scripts/ingest_books.py --books-dir ./books --content-type medical_literature

# Step 2b — NRT/QAT plain text
python scripts/ingest_text.py --file books/QAT_Manual.txt \
  --content-type training_qat --title "QAT Manual"

# Step 2c — training videos (queue handles this automatically now)
# Videos → /videos/{type}/ → click Transcribeer in UI → queue picks up

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

## Web interface — live pages

| Route | Status | Description |
|---|---|---|
| `/` | ✅ Live | Dashboard — CPU/RAM/disk/services/stats |
| `/health` | ✅ Live | JSON health check |
| `/videos` | ✅ Live | Upload, transcription queue, status polling |
| `/videos/status/{type}/{file}` | ✅ Live | done/running/queued/waiting |
| `/videos/transcript/{type}/{stem}` | ✅ Live | Timestamped segment viewer |
| `/logs/{logname}` | ✅ Live | Tail log file (transcription_queue, web, maintenance) |
| `/status/snapshot` | ✅ Live | JSON snapshot — services, transcription, system stats |
| `/status/markers` | ✅ Live | Read/write status markers (notify.sh integration) |
| `/library` | ✅ Live | 3-section book upload (Medische Literatuur / NRT+QAT / Apparatuur) |
| `/library/overview` | ✅ Live | Literature overview — usability scores per book |
| `/library/audit/{filename}` | ✅ Live | JSON audit report per book |
| `/library/retag/{filename}` | ✅ Live | Re-tag chunks via Ollama without re-parsing |
| `/images` | ✅ Live | Image approval gallery (pending/approve/reject) |
| `/search` | ❌ Not built | RAG query interface |
| `/protocols` | ❌ Not built | Protocol builder |

---

## Standing rules (from CLAUDE.md)

| Rule | When |
|---|---|
| `git add PROJECT_STATE.md SYSTEM_DOCS/CONTEXT.md && git commit -m "state: ..." && git push` | After every significant task |
| `python3 scripts/run_tests.py` — all tests pass before deploy | Before every deploy |
| `git tag -a v<date>-<desc>` | Before every significant change |
| Docker volume snapshot of `data/qdrant/` | Before any ingestion that modifies an existing collection |
| Update `CHANGELOG.md` with a dated entry | End of every session |

---

## Immediate next steps

1. **Check QAT transcription progress** — read LIVE_STATUS.md or `tail -20 /var/log/transcription_queue.log`
   - Green_Square_Applications.mp4 running since 07:59; expect ~11 more videos after this
2. **Build `/library` page** — PDF/EPUB upload, metadata cards, ingestion trigger, processing status
3. **Build `/search` page** — multi-collection RAG search with citation display
4. **Add books:** Drop `.pdf`/`.epub` into `./books/` → `fetch_book_metadata.py` → `ingest_books.py`
5. **Build remaining web pages:** `/images`, `/protocols`
6. **Word output:** `.docx` treatment protocols (§1 Klachtbeeld / §2 Behandeling / §3 Bijlagen)
7. **Generate first treatment protocol** — once books + transcripts ingested, query RAG and produce Word output

---

## Maintenance status

**Laatste run:** 15-04-2026 00:30 (35.3s)  
**Uitslag:** ⚠️ WARNING — 1 waarschuwing(en), 4 OK

---

## Test status

**Laatste run:** 15-04-2026 08:08 (36.1s)  
**Uitslag:** ✅ GESLAAGD — 33/33 geslaagd, 0 overgeslagen

---

## Correct terminology — always use

| Term | Correct |
|---|---|
| Bedrijfsnaam | NRT-Amsterdam.nl |
| NRT | Neural Reset Therapy |
| QAT | Quantum Alignment Technique |
| GTR | Golgi Tendon Reflex |
| PEMF | Pulsed Electromagnetic Field |
| RLT | Red Light Therapy |

---

## Git / state tracking

- Repo: https://github.com/abiere/medical-rag-state (private)
- After every significant task:
  ```bash
  git add PROJECT_STATE.md SYSTEM_DOCS/CONTEXT.md && git commit -m "state: [description]" && git push
  ```
- Dashboard + live state: `http://100.66.194.55:8000` (Tailscale only)
