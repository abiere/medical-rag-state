# CONTEXT — Session Loader

> Read this file at the start of every session. Max 150 lines.
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
| Qdrant | Docker | 6333 (REST), 6334 (gRPC) | Up, healthy |
| Ollama | Docker | 11434 | Up, healthy |
| FastAPI dashboard | systemd `medical-rag-web.service` | **8000** | **Active** |
| State HTTP server | systemd `medical-rag-state.service` | 8080 | **Disabled** |

**Ollama model loaded:** `llama3.1:8b` (4.92 GB, Q4_K_M)

**Dashboard:** `http://100.66.194.55:8000` (Tailscale only)

---

## Key paths

```
/root/medical-rag/
├── books/                  ← drop PDFs/EPUBs here (empty — no books ingested yet)
├── data/
│   ├── extracted_images/   ← saved figures from ingested books
│   ├── ollama/             ← model weights (Docker volume)
│   └── qdrant/             ← vector storage (Docker volume)
├── scripts/
│   └── ingest_books.py     ← main ingestion pipeline
├── serve_state.py          ← http.server on :8080
├── docker-compose.yml
├── CLAUDE.md               ← standing instructions
├── PROJECT_STATE.md        ← live server state (update & commit after each task)
└── SYSTEM_DOCS/
    ├── CONTEXT.md          ← this file
    ├── PRACTICE_CONTEXT.md ← practitioner, modalities, protocol structure, image rules, writing rules
    ├── REQUIREMENTS.md     ← FR + NFR
    ├── ARCHITECTURE.md     ← full stack description
    ├── TECHNICAL_DESIGN.md ← ingestion pipeline, metadata pipeline, Qdrant payload, citations
    ├── CHANGELOG.md        ← dated history of all changes
    └── TEST_REPORT.md      ← test results (no tests yet)
```

---

## Stack

| Component | Role | Status |
|---|---|---|
| Docling | PDF parsing — text, images, page numbers | Ready (not yet installed) |
| EasyOCR | OCR for scanned PDFs + figure labels | Ready (not yet installed) |
| ebooklib + BS4 | EPUB parsing (Docling doesn't support EPUB) | Installed |
| BAAI/bge-large-en-v1.5 | Local embeddings, 1024-dim | Ready (not yet installed) |
| Qdrant | Vector store | Running |
| Ollama / llama3.1:8b | Local LLM inference | Running |
| LLaVA (vision) | Figure descriptions | Not yet pulled |
| OpenAI Whisper (local) | Video transcription | Ready (not yet installed) |
| ffmpeg | Audio extraction for Whisper | Not yet installed |
| FastAPI | Web layer — upload, status, Q&A, generation | **Planned** |
| python-docx | Word document output | **Planned** |
| Tailscale | Access control | **Planned / pending setup** |

---

## Qdrant collections

| Collection | content_type(s) | What goes in |
|---|---|---|
| `medical_literature` | `medical_literature` | Anatomy/clinical EPUBs + PDFs |
| `training_materials` | `training_nrt`, `training_qat` | NRT/QAT PDFs, video transcripts, text |
| `device_protocols` | `device_pemf`, `device_rlt` | Device manuals, settings, videos |

## Ingestion pipeline

```bash
# Step 1: fetch bibliographic metadata (run once per new book)
python scripts/fetch_book_metadata.py --books-dir ./books

# Step 2a: medical books
python scripts/ingest_books.py --books-dir ./books --content-type medical_literature

# Step 2b: NRT/QAT plain text
python scripts/ingest_text.py --file books/QAT_Manual.txt \
  --content-type training_qat --title "QAT Manual"

# Step 2c: training videos
python scripts/transcribe_videos.py --type nrt --ingest
python scripts/transcribe_videos.py --type qat --ingest

# Step 2d: device PDFs
python scripts/ingest_books.py --books-dir ./books/pemf --content-type device_pemf
```

- Chunking: 512 tokens / 64 overlap / SentenceSplitter
- Qdrant collection auto-created on first run (Cosine / 1024-dim)
- Idempotent — `chunk_hash` prevents duplicate vectors
- Figures named: `{slug}_p{page}_fig{n}.png` — deterministic, traceable
- Payload: `content_type`, `page_number`, `image_links`, `caption`, `figure_labels`,
  `image_type`, `image_description`, `figure_number`, `citation`, `citation_apa`,
  `see_also`, `device`, `setting`, `intensity_range`, `duration_minutes`,
  `indication`, `contraindication`, `body_region`
- Scanned PDFs: auto-detected (< 50 chars/page) → EasyOCR
- PEMF/RLT: structured settings extracted automatically
- Video transcripts: Whisper `medium`, Dutch language hint (`nl`)
- **Pre/post-check RAM and disk** before large runs (NFR-4)

---

## Standing rules (from CLAUDE.md + NFR)

| Rule | When |
|---|---|
| `git add PROJECT_STATE.md && git commit -m "state: ..." && git push` | After every significant task |
| `git tag -a v<date>-<desc>` | Before every significant change |
| Docker volume snapshot of `data/qdrant/` | Before any ingestion that modifies an existing collection |
| Update `CHANGELOG.md` with a dated entry | End of every session |
| Automated tests pass + `TEST_REPORT.md` updated | Before every deploy |

---

## Immediate next steps

1. Install dependencies: `pip install docling easyocr openai-whisper llama-index qdrant-client pypdf pillow --break-system-packages` + `apt install ffmpeg`
2. Add `.pdf` / `.epub` books to `./books/` → run `fetch_book_metadata.py` → run `ingest_books.py`
3. Add NRT/QAT videos to `./videos/nrt/` and `./videos/qat/` → run `transcribe_videos.py --ingest`
4. Build `query_rag.py` — multi-collection search across all three collections
5. Build FastAPI web layer: upload, status, Q&A, protocol generation, metadata review card
6. Implement Word output for treatment protocols (§1/§2/§3 structure — see FR-3)
7. Set up Tailscale access control

---

## Test status

**Laatste run:** 14-04-2026 18:52 (0.9s)  
**Uitslag:** ✅ GESLAAGD — 15/15 geslaagd, 9 overgeslagen
---

## Git / state tracking

- Repo: https://github.com/abiere/medical-rag-state (private)
- After every significant task:
  ```bash
  git add PROJECT_STATE.md && git commit -m "state: [description]" && git push
  ```
- Live state always readable at: http://100.66.194.55 (Tailscale):8000
