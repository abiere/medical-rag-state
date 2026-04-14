# Requirements — Medical RAG System

---

## Functional Requirements

### FR-1 — Web Interface
- Accessible **via Tailscale only**; not exposed to the public internet
- No separate authentication layer — Tailscale network membership is the access control

### FR-2 — Book Management
- Upload books in **PDF** and **EPUB** format through the web interface
- View **processing status** per book (queued / processing / ready / failed)
- View a **usability rating** per book — a quality signal derived from ingestion (e.g. chunk count, image extraction rate, text density)
- Process with **Docling** (PDF) or ebooklib + BeautifulSoup4 (EPUB): extract text, images, and page numbers
- Images saved locally; inline `[Image: …]` markers embedded in text so image context is captured by the embedding
- Idempotent: re-uploading the same file must not create duplicate vectors (enforced via `chunk_hash`)
- Page numbers preserved and stored as Qdrant payload for citation purposes

### FR-3 — Treatment Protocol Generation
- Output: **Word document** (`.docx`)
- **Section 1 — Condition overview**
  - Condition description
  - Anatomical cause
  - Possible symptoms
- **Section 2 — Acupuncture treatment**
  - Acupuncture points with rationale
  - Point images (extracted from source books where available)
- **Appendix — Full rationale**
  - Every clinical choice cited with exact source document and page number
  - No claim may appear without a retrieved supporting chunk

### FR-4 — Blog Article Generation
- Output: plain prose suitable for publication on **nrt-amsterdam.nl**
- Grounded exclusively in retrieved literature — no unsupported claims
- Tone: professional but accessible (patient-facing)
- References section at end: `[Title, p. N]` for every source used

### FR-5 — Ad Hoc Q&A
- Free-form questions answered against the full literature database
- Answer includes inline citations: `[Title, p. N]`
- Optional: filter search to a specific subject collection or source file

### FR-6 — Citation Integrity
- **All** generated content must cite exact page numbers and source documents
- Images in Word output must reference their source page
- LLM must only cite chunks that were actually retrieved — no hallucinated references
- Citations format: `[Book Title, p. N]`

---

## Non-Functional Requirements

### NFR-1 — Security ✅
- All interfaces reachable via **Tailscale only**
- No public internet exposure for any application endpoint
- Secrets (API keys, tokens) stored in `.env` files, never committed to git
- **Status:** Tailscale active (`100.66.194.55`); UFW blocks all public ingress; port 8080 disabled

### NFR-2 — Rollback & Safety ✅
- Create a **git tag** before every significant change: `git tag -a v<date>-<description>`
- Create **Docker volume snapshots** of `data/qdrant/` and `data/ollama/` before any ingestion run that modifies an existing collection
- Document rollback procedure in `SYSTEM_DOCS/` before executing irreversible operations
- **Status:** Nightly maintenance handles automated Qdrant snapshots (max 7) and weekly git tags

### NFR-3 — Testing ✅
- Automated tests must pass before every deploy
- Test results written to `SYSTEM_DOCS/TEST_REPORT.md` after each test run
- Test areas: ingestion idempotency, embedding dimension, Qdrant round-trip, Ollama inference, citation integrity, FastAPI endpoints
- **Status:** 24/24 tests passing; `medical-rag-tests.timer` runs daily at 00:00 UTC; deploy gate in `CLAUDE.md`

### NFR-4 — Batch Processing
- **Pre-check** available RAM and disk before large ingestion operations
- **Log every step** of ingestion (book name, chunk count, image count, duration, errors)
- **Post-check** Qdrant point count and sampled payload after ingestion to confirm correctness
- Abort gracefully if pre-check thresholds are not met (e.g. < 4 GB free RAM)

### NFR-5 — Documentation
- `SYSTEM_DOCS/` must be up to date at the end of every session
- `PROJECT_STATE.md` committed and pushed after every significant task
- `CHANGELOG.md` updated with a dated entry for every session's work
- `CONTEXT.md` reflects current stack status and next steps at all times

### NFR-6 — Unified multi-collection search
- A single treatment protocol query MUST search all three Qdrant collections
  (`medical_literature`, `training_materials`, `device_protocols`) simultaneously
- Results are merged by cosine similarity score before ranking
- Each result carries its `content_type` so the protocol generator can route
  it to the correct section (§1 Klachtbeeld / §2 Behandeling / §3 Bijlagen)

---

## Functional Requirements — Extended

### FR-7 — Video transcription (NRT / QAT extra muscle resets) ✅
- Accept MP4/MOV/MKV/M4V video files in `videos/{nrt,qat,pemf,rlt}/`
- Transcribe locally with OpenAI Whisper (model: `medium`; language hint: `nl`)
- Save timestamped segments to `data/transcripts/{stem}.json` and `.txt`
- Ingest transcript segments into Qdrant (`training_materials` or `device_protocols`)
- Cross-reference transcript chunks with related PDF sections via `see_also` field
- Idempotent: skip transcription if transcript file already exists
- **Status:** `scripts/transcribe_videos.py` complete; `GET /videos` + upload/transcribe routes live; ffmpeg + Whisper installed

### FR-8 — PEMF / RLT structured settings extraction
- For every chunk with `content_type: device_pemf` or `device_rlt`, automatically
  extract structured fields from the text:
  `setting`, `program`, `intensity_range`, `duration_minutes`,
  `indication`, `contraindication`, `body_region`
- Store as Qdrant payload for direct use in §2 (Behandeling) of treatment protocols
- Protocol generator auto-formats: "PEMF: Setting 3, Intensity 4-6, 20 min op lumbale regio"

### FR-9 — Plain text / Markdown import (QAT and others)
- Accept `.txt` and `.md` files via `scripts/ingest_text.py`
- CLI arguments: `--content-type`, `--title`, `--author`, `--year`, `--publisher`
- Same chunking, embedding, and citation pipeline as PDF/EPUB
- Updates `books_metadata.json` with `media_type: "text"` and `internal_only: true`

---

## Explicit Exclusions

- No cloud LLM APIs — all inference runs locally via Ollama
- No public-facing endpoints
- No user accounts or multi-tenancy (single-user system)
