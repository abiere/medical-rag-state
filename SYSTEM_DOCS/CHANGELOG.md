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

---

## Pending

See `REQUIREMENTS.md` and `PROJECT_STATE.md § 7 Pending Tasks`.
