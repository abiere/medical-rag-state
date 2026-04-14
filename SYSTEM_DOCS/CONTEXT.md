# CONTEXT — Session Loader

> Read this file at the start of every session. Max 150 lines.
> Full detail lives in PROJECT_STATE.md and SYSTEM_DOCS/*.

---

## What this system is

A **private, fully-local RAG system** for medical and acupuncture literature.
Access via **Tailscale only**. All inference runs on a single Hetzner server.

**Primary outputs:**
1. **Word documents** — treatment protocols (condition overview, acupuncture points + images, cited appendix)
2. **Blog articles** for nrt-amsterdam.nl — grounded in retrieved literature
3. **Ad hoc Q&A** — free-form questions answered against the book database, with citations

All outputs cite exact page numbers and source documents. No hallucinated references.

---

## Server

| Property | Value |
|---|---|
| Host | Hetzner CX53 — 178.104.77.146 |
| vCPUs / RAM / Disk | 16 / 30 GiB / 301 GB |
| OS | Ubuntu, kernel 6.8.0-79-generic |
| Docker | 29.1.3 — use `docker-compose` (v1), NOT `docker compose` |
| Python | 3.12 system — `pip install --break-system-packages` |

---

## Running services

| Service | How | Port | State |
|---|---|---|---|
| Qdrant | Docker | 6333 (REST), 6334 (gRPC) | Up, healthy |
| Ollama | Docker | 11434 | Up, healthy |
| State HTTP server | systemd `medical-rag-state.service` | 8080 | Active |

**Ollama model loaded:** `llama3.1:8b` (4.92 GB, Q4_K_M)

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
    ├── REQUIREMENTS.md     ← FR + NFR (updated 2026-04-14)
    ├── ARCHITECTURE.md     ← full stack description
    ├── CHANGELOG.md        ← dated history of all changes
    └── TEST_REPORT.md      ← test results (no tests yet)
```

---

## Stack

| Component | Role | Status |
|---|---|---|
| Docling | PDF parsing — text, images, page numbers | Ready |
| ebooklib + BS4 | EPUB parsing (Docling doesn't support EPUB) | Ready |
| BAAI/bge-large-en-v1.5 | Local embeddings, 1024-dim | Ready |
| Qdrant | Vector store | Running |
| Ollama / llama3.1:8b | Local LLM inference | Running |
| FastAPI | Web layer — upload, status, Q&A, generation | **Planned** |
| python-docx | Word document output | **Planned** |
| Tailscale | Access control | **Planned / pending setup** |

---

## Ingestion pipeline

```bash
python scripts/ingest_books.py \
  --collection <name> \
  --subject <subject> \
  --books-dir ./books
```

- Chunking: 512 tokens / 64 overlap / SentenceSplitter
- Qdrant collection auto-created on first run (Cosine / 1024-dim)
- Idempotent — `chunk_hash` prevents duplicate vectors
- Payload fields: `page_number`, `section_number`, `text`, `image_links`, `source_file`, `format`, `chunk_hash`
- **Pre/post-check RAM and disk** before running on large collections (NFR-4)

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

1. Add `.pdf` / `.epub` books to `./books/` and run ingestion (with pre-check)
2. Build `query_rag.py` — embed question → Qdrant retrieval → Ollama → cited answer
3. Build FastAPI web layer: book upload, processing status, usability rating, Q&A, generation
4. Implement Word output for treatment protocols (3-section structure — see FR-3)
5. Set up Tailscale access control

---

## Git / state tracking

- Repo: https://github.com/abiere/medical-rag-state (private)
- After every significant task:
  ```bash
  git add PROJECT_STATE.md && git commit -m "state: [description]" && git push
  ```
- Live state always readable at: http://178.104.77.146:8080/PROJECT_STATE.md
