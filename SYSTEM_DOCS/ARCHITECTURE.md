# Architecture — Medical RAG System

## Overview

A fully local, private RAG (Retrieval-Augmented Generation) pipeline for medical and acupuncture literature. All inference and storage run on a single Hetzner server; access is restricted to the Tailscale network.

```
Browser (Tailscale) ──► FastAPI (planned, :8000)
                              │
              ┌───────────────┼────────────────┐
              │               │                │
         Docling          Qdrant          Ollama
       (ingestion)     (vector DB)    (llama3.1:8b)
              │               │
         books/ (PDFs)   BAAI/bge-large-en-v1.5
         data/extracted_images/
```

## Server

| Property | Value |
|---|---|
| Provider | Hetzner CX53 |
| vCPUs | 16 |
| RAM | 30 GiB (no swap) |
| Disk | 301 GB (`/dev/sda1`) |
| OS | Ubuntu, kernel 6.8.0-79-generic |
| Docker | 29.1.3 |
| docker-compose | v1.29.2 (use `docker-compose`, not `docker compose`) |
| Python | 3.12 system install — packages via `--break-system-packages` |

## Components

### Qdrant (vector database)
- Image: `qdrant/qdrant:latest`
- Ports: `6333` (REST), `6334` (gRPC)
- Memory limit: 8 GB
- CPU limit: 6 cores
- Volume: `./data/qdrant`
- Performance tuning: `MAX_SEARCH_THREADS=8`, `INDEXING_THRESHOLD_KB=20000`, `MEMMAP_THRESHOLD_KB=50000`, HNSW `M=16` / `ef_construct=100`
- Restart: `unless-stopped`

### Ollama (LLM inference)
- Image: `ollama/ollama:latest`
- Port: `11434`
- Memory limit: 16 GB
- CPU limit: 8 cores
- Volume: `./data/ollama`
- Loaded model: `llama3.1:8b` (4.92 GB, Q4_K_M quantization)
- Restart: `unless-stopped`

### Docling (document parsing)
- Runs in-process (Python library, not a container)
- Handles PDF via `PdfPipelineOptions` — extracts text layout, tables, and figures
- EPUB handled by `ebooklib` + `BeautifulSoup4` (Docling upstream issue #515)
- Images extracted as PNG at 2× scale, saved to `data/extracted_images/`

### Embedding model
- `BAAI/bge-large-en-v1.5` — 1024-dim, strong on medical/scientific text
- Runs via `llama-index-embeddings-huggingface`; cached in `~/.cache/huggingface` after first download
- Runs in-process on the host (no GPU required)

### Ingestion pipeline (`scripts/ingest_books.py`)
- Accepts `--collection`, `--subject`, `--books-dir` args
- Chunking: 512 tokens, 64-token overlap, `SentenceSplitter` (LlamaIndex)
- Payload per chunk: `page_number`, `section_number`, `text`, `image_links`, `source_file`, `source_path`, `format`, `chunk_hash`
- Idempotency: skips chunks whose `chunk_hash` already exists in the collection

### FastAPI web layer *(planned)*
- Python, served on port `8000`
- Endpoints: book upload, ingestion trigger, Q&A, protocol generation, blog generation
- Accessible only via Tailscale

### Output generation *(planned)*
- Word documents: `python-docx`
- Blog articles: plain text / Markdown → HTML
- Citations injected from Qdrant payload (`source_file` + `page_number`)

### State HTTP server (`serve_state.py`)
- Python `http.server`, port `8080`
- Serves `/root/medical-rag/` directory
- Runs as `medical-rag-state.service` (systemd, enabled at boot)

## Network / Access

- **Tailscale** restricts all access — no public ports planned except the state server (port 8080, informational only)
- Docker containers bind to `0.0.0.0` internally; firewall/Tailscale ACLs control external access

## RAM Budget

| Component | Limit | Typical idle |
|---|---|---|
| Qdrant | 8 GB | ~32 MiB |
| Ollama (model loaded) | 16 GB | ~12 MiB idle / ~5 GB under load |
| OS + Python | ~1.5 GB | ~1.5 GB |
| **Total** | **25.5 GB** | **~1.6 GB idle** |

~5 GB headroom before OOM risk. No swap configured — monitor with `docker stats` during heavy ingestion.

## Repository

- GitHub: https://github.com/abiere/medical-rag-state (private)
- Local: `/root/medical-rag/`
- Credential helper: `gh auth git-credential`
