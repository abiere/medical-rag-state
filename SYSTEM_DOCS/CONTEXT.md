# CONTEXT — Session Loader
> Read this file at the start of every session. Max 150 lines.
> Live status: https://raw.githubusercontent.com/abiere/medical-rag-state/main/SYSTEM_DOCS/LIVE_STATUS.md
> Backlog: https://raw.githubusercontent.com/abiere/medical-rag-state/main/SYSTEM_DOCS/BACKLOG.md

## What this system is

A **private, fully-local RAG system** for medical and acupuncture literature.
Built for **Axel Biere** (NRT-Amsterdam.nl), complementary therapist, Amsterdam.
Access via **Tailscale only**. All inference runs on a single Hetzner server.

> Full practice context — modalities, protocol structure, image requirements, writing rules:
> **→ read `SYSTEM_DOCS/PRACTICE_CONTEXT.md` before generating any content**

**Treatment modalities (always combined):** NRT · QAT · GTR · Tit Tar · PEMF · RLT

**Primary outputs:**
1. **Word documents** — treatment protocols: §1 Klachtbeeld · §2 Behandeling (anatomical + acupuncture images) · §3 Bijlagen/Rationale (page-cited)
2. **Blog articles** for nrt-amsterdam.nl — accessible Dutch prose, grounded in retrieved literature
3. **Ad hoc Q&A** — free-form questions against the book database with page citations

---

## Server

| Property | Value |
|---|---|
| Host | Hetzner CX53 — **100.66.194.55 (Tailscale only)** — public IP blocked by UFW |
| vCPUs / RAM / Disk | 16 / 32 GiB / 322 GB |
| OS | Ubuntu, kernel 6.8.0-79-generic |
| Docker | 29.1.3 — use `docker-compose` (v1), NOT `docker compose` |
| Python | 3.12 system — `pip install --break-system-packages` |
| Git identity | Axel Biere `<axelbiere@gmail.com>` |

---

## Running services

| Service | How | Port | State |
|---|---|---|---|
| Qdrant | Docker | 6333 REST, 6334 gRPC | Up, healthy |
| Ollama | Docker | 11434 | Up, healthy — llama3.1:8b loaded |
| FastAPI web interface | systemd `medical-rag-web.service` | 8000 | Active |
| Book ingest queue | systemd `book-ingest-queue.service` | — | **Active — Deadman processing (60+ min)** |
| Transcription queue | systemd `transcription-queue.service` | — | Active — 21 NRT videos queued |
| ttyd browser terminal | systemd `ttyd.service` | 7682 | Active (iframe bug open) |
| sync-status timer | systemd `sync-status.timer` | — | Active — every 5 min |

**Dashboard:** `http://100.66.194.55:8000` (Tailscale only)

---

## Qdrant collections

| Collection | Points | Source |
|---|---|---|
| `medical_library` | 2 (test data) + Deadman incoming | `books/medical_literature/` |
| `nrt_qat_curriculum` | 0 (empty) | `books/nrt/` + `books/qat/` |
| `device_documentation` | — (not created) | `books/device/` |
| `video_transcripts` | 6 | QAT videos (all 15 transcribed + ingested) |

---

## Book ingest — current state (2026-04-15)

**Processing now:** `pdfcoffee.com_a-manual-of-acupuncture-peter-deadmanpdf-4-pdf-free.pdf`
→ via Docling (native PDF path), ~60 min elapsed, → `medical_library`

**Queue (2 books waiting):**
1. `359609833-Travell-and-Simons-Myofascial-Pain-and-Dysfunction-Vol-1-2nd-Ed-D-Simons-Et-Al-Williams-and-Wilkins-1999-WW.pdf`
2. `969553977-Trail-Guide-to-the-Body-6th-Edition-Andrew-Biel.pdf`

All three → `medical_library` collection. Monitor: `tail -f /var/log/book_ingest_queue.log`

---

## Video transcription — current state (2026-04-15)

| Type | Total | Done | Queue |
|---|---|---|---|
| QAT | 15 | **15 ✅** | 0 |
| NRT | 21 | 0 | **21 pending** |

QAT: all 15 transcripts in `data/transcripts/`, ingested → `video_transcripts`.
NRT: 21 videos in `videos/nrt/`, processed sequentially by transcription-queue.
Monitor: `tail -f /var/log/transcription_queue.log`

---

## Key paths

```
/root/medical-rag/
├── books/
│   ├── medical_literature/   ← 3 PDFs: Deadman, Travell+Simons, Trail Guide
│   ├── nrt/                  ← NRT cursusmateriaal (empty — awaiting upload)
│   ├── qat/                  ← QAT cursusmateriaal (empty — awaiting upload)
│   └── device/               ← PEMF/RLT documentation (empty)
├── videos/
│   ├── nrt/                  ← 21 NRT videos (transcription pending)
│   └── qat/                  ← 15 QAT videos (all transcribed ✅)
├── data/
│   ├── transcripts/          ← 15 QAT transcripts (JSON + TXT), NRT incoming
│   ├── extracted_images/     ← figures from books (PNG)
│   ├── book_quality/         ← audit reports + calibration_cache.json
│   └── image_approvals.json  ← pending/approved/rejected images
├── web/
│   └── app.py                ← FastAPI, all routes, port 8000
├── scripts/
│   ├── parse_pdf.py          ← PDF parser: native (Docling) / scanned / mixed + OCR cascade
│   ├── parse_epub.py         ← EPUB parser (3 strategies)
│   ├── audit_book.py         ← structural + LLM quality audit
│   ├── book_ingest_queue.py  ← sequential book queue (systemd, pause-flag aware)
│   ├── transcription_queue.py← sequential video queue (systemd, pause-flag aware)
│   ├── ocr_preprocess.py     ← OpenCV deskew/denoise/CLAHE per page
│   ├── ocr_calibrate.py      ← per-book engine calibration via Ollama
│   ├── ocr_postcorrect.py    ← rule + Ollama OCR error correction
│   ├── ingest_transcript.py  ← transcript → Qdrant video_transcripts
│   ├── sync_status.py        ← LIVE_STATUS.md + git push every 5 min
│   └── run_tests.py          ← test suite → TEST_REPORT.md
└── SYSTEM_DOCS/
    ├── CONTEXT.md            ← this file
    ├── PRACTICE_CONTEXT.md   ← practitioner, modalities, protocol, image rules
    ├── BACKLOG.md            ← prioritised task list
    └── LIVE_STATUS.md        ← auto-generated every 5 min
```

---

## Stack

| Component | Role | Status |
|---|---|---|
| FastAPI + Uvicorn | Web layer — all routes | Running (port 8000) |
| Qdrant | Vector store | Running |
| Ollama / llama3.1:8b | Local LLM inference | Running |
| Docling | PDF parsing (native PDFs with text) | Installed |
| EasyOCR + Surya + Tesseract | Cascade OCR (scanned/mixed PDFs) | Installed |
| OpenCV 4.11.0 | Image preprocessing for OCR | Installed |
| BAAI/bge-large-en-v1.5 | Local embeddings, 1024-dim | Installed (cached) |
| Whisper (local) | Video transcription | Running via queue |
| pdfplumber + PyMuPDF | PDF type detection + fallback text extraction | Installed |
| python-docx | Word document output | **Not yet installed** |

---

## OCR cascade (parse_pdf.py)

PDF routing: `detect_pdf_type()` samples 5 pages → `native` / `mixed` / `scanned`

For non-native pages:
1. `ocr_preprocess.py` — deskew → denoise → CLAHE → Otsu binarization
2. `ocr_calibrate.py` — sample 5 pages, Ollama picks best engine, cached per book
3. Cascade: EasyOCR → Surya → Tesseract (first to return ≥10 words wins)
4. `ocr_postcorrect.py` — point code normalisation (ST36→ST-36) + Ollama correction for low-confidence chunks

---

## Web routes

| Route | Status |
|---|---|
| `/`, `/health`, `/status/snapshot`, `/status/markers` | ✅ Live |
| `/library`, `/library/overview`, `/library/audit/{f}`, `/library/retag/{f}` | ✅ Live |
| `/library/progress`, `/library/pause`, `/library/resume`, `/library/paused` | ✅ Live |
| `/videos`, `/videos/transcript/{type}/{stem}`, `/videos/status/{type}/{f}` | ✅ Live |
| `/videos/progress`, `/videos/pause`, `/videos/resume`, `/videos/paused` | ✅ Live |
| `/images`, `/images/approve`, `/images/approved`, `/images/file/{f}` | ✅ Live |
| `/search` (RAG query, SSE streaming, citations, image search) | ✅ Live |
| `/logs/{logname}`, `/terminal` | ✅ Live |
| `/protocols` | ❌ Not built |

Pause/resume: both queues check `/tmp/book_ingest_pause` and `/tmp/transcription_pause`
before starting the next job (does not interrupt the currently running job).

---

## Immediate next steps

1. **Deadman finishes** → verify chunk count; Travell+Simons + Trail Guide process automatically
2. **NRT videos** → 21 pending; transcription-queue processing sequentially
3. **Upload NRT + QAT curriculum books** → drop in `books/nrt/` and `books/qat/`
4. **Validate search quality** — test RAG once Deadman chunks are in medical_library
5. **Build `/protocols`** — Word (.docx) treatment protocol output
6. **Fix ttyd iframe bug** — browser terminal loads but iframe blocked

---

## Tests & git

```bash
python3 scripts/run_tests.py          # 33/33 passing (2026-04-15)
git add SYSTEM_DOCS/ && git commit -m "state: ..." && git push
```

---

## Correct terminology

NRT = Neural Reset Therapy · QAT = Quantum Alignment Technique · GTR = Golgi Tendon Reflex
PEMF = Pulsed Electromagnetic Field · RLT = Red Light Therapy · Bedrijfsnaam = NRT-Amsterdam.nl
