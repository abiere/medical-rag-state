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

### NFR-1 — Security
- All interfaces reachable via **Tailscale only**
- No public internet exposure for any application endpoint
- Secrets (API keys, tokens) stored in `.env` files, never committed to git

### NFR-2 — Rollback & Safety
- Create a **git tag** before every significant change: `git tag -a v<date>-<description>`
- Create **Docker volume snapshots** of `data/qdrant/` and `data/ollama/` before any ingestion run that modifies an existing collection
- Document rollback procedure in `SYSTEM_DOCS/` before executing irreversible operations

### NFR-3 — Testing
- Automated tests must pass before every deploy
- Test results written to `SYSTEM_DOCS/TEST_REPORT.md` after each test run
- Test areas: ingestion idempotency, embedding dimension, Qdrant round-trip, Ollama inference, citation integrity, FastAPI endpoints

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

---

## Explicit Exclusions

- No cloud LLM APIs — all inference runs locally via Ollama
- No public-facing endpoints
- No user accounts or multi-tenancy (single-user system)
