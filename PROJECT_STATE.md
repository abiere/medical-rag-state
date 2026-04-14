# Medical RAG — Project State

> **Update this file at the end of every major step.**
> Captures server specs, architecture decisions, live container state, and pending work so any session can resume without re-reading the full conversation history.

---

## 1. Server

| Property | Value |
|---|---|
| Provider | Hetzner CX53 |
| vCPUs | 16 |
| RAM | 30 GiB usable (no swap) |
| Disk | 301 GB (`/dev/sda1`), ~17 GB used |
| OS Kernel | Linux 6.8.0-79-generic |
| Docker | 29.1.3 |
| docker-compose | 1.29.2 (v1 — use `docker-compose`, not `docker compose`) |
| Python | 3.12 (`/usr/bin/python3`) — no venv, packages installed with `--break-system-packages` |

---

## 2. Folder Structure

```
/root/medical-rag/
├── books/                        # Drop PDFs/EPUBs here  ← EMPTY
├── videos/
│   ├── nrt/                      # NRT training videos  ← EMPTY
│   ├── qat/                      # QAT training videos  ← EMPTY
│   ├── pemf/                     # PEMF instruction videos  ← EMPTY
│   └── rlt/                      # RLT instruction videos  ← EMPTY
├── data/
│   ├── books_metadata.json       # Bibliographic metadata + citations (tracked in git)
│   ├── video_document_links.json # Video ↔ PDF cross-references (tracked in git)
│   ├── image_memory.json         # Axel's image selections per tissue (tracked in git)
│   ├── extracted_images/         # Saved figures — {slug}_p{page}_fig{n}.png
│   ├── transcripts/              # Whisper JSON + TXT transcripts
│   ├── device_settings/          # Curated PEMF/RLT settings files
│   ├── processing_logs/          # Per-book ingestion stats
│   ├── ollama/                   # Ollama model weights (Docker volume)
│   └── qdrant/                   # Qdrant vector storage (Docker volume)
├── scripts/
│   ├── ingest_books.py           # PDF + EPUB ingestion (all content types)
│   ├── ingest_text.py            # Plain text / Markdown ingestion
│   ├── transcribe_videos.py      # Whisper video transcription + ingest
│   └── fetch_book_metadata.py    # OpenLibrary + Google Books metadata
├── SYSTEM_DOCS/                  # Technical documentation
├── CLAUDE.md                     # Standing instructions
├── PROJECT_STATE.md              # This file
├── serve_state.py                # HTTP state server (:8080)
└── docker-compose.yml
```

**Disk usage (2026-04-14):** `/dev/sda1` — 301 GB total, 17 GB used (6%), 272 GB free.
**books/ and videos/:** All empty — no content ingested yet.

---

## 3. Infrastructure

### docker-compose.yml — key settings

| Service | Image | Ports | mem_limit | CPUs | Restart |
|---|---|---|---|---|---|
| `qdrant` | `qdrant/qdrant:latest` | 6333 (REST), 6334 (gRPC) | 8 GB | 6 | unless-stopped |
| `ollama` | `ollama/ollama:latest` | 11434 | 16 GB | 8 | unless-stopped |

**RAM budget:** Qdrant 8 GB + Ollama 16 GB + OS ~1.2 GB = ~25 GB of 30 GB. ~5 GB headroom.

**Qdrant performance tuning applied:**
- `MAX_SEARCH_THREADS: 8`
- `INDEXING_THRESHOLD_KB: 20000`
- `MEMMAP_THRESHOLD_KB: 50000`
- `HNSW M: 16`, `ef_construct: 100`

**Healthcheck approach:** Both images lack `curl` and `wget`. Healthchecks use bash TCP redirects:
```bash
exec 3<>/dev/tcp/localhost/PORT && echo -e 'GET /path HTTP/1.0\r\n\r\n' >&3 && grep -q 'expected_string' <&3
```

### Live Container State *(last checked: 2026-04-14 ~15:10 UTC)*

| Container | Image | Ports | Status | RAM used | CPU |
|---|---|---|---|---|---|
| `qdrant` | `qdrant/qdrant:latest` | 6333 (REST), 6334 (gRPC) | Up 4 h, **healthy** | 32 MiB / 8 GiB | 0.28% |
| `ollama` | `ollama/ollama:latest` | 11434 | Up 4 h, **healthy** | 12 MiB / 16 GiB | 0.00% |

### Ollama Models

| Model | Size | Purpose |
|---|---|---|
| `llama3.1:8b` | 4.92 GB | Medical text analysis and RAG responses |

`llama3.1:70b` was evaluated and rejected — requires ~40 GB+ quantized, exceeds available RAM when running alongside Qdrant and the OS.

### Qdrant Collections

No collections yet. The `medical_rag` collection is created automatically on the first run of `ingest_books.py`.

Collection config (applied at creation time):
- Vector size: **1024** (matches `BAAI/bge-large-en-v1.5`)
- Distance: **Cosine**
- Payload field `image_links` is a native JSON array — filterable without a separate index

---

## 4. Ingestion Pipeline (`scripts/ingest_books.py`)

### Supported formats
| Extension | Backend |
|---|---|
| `.pdf` | Docling (`PdfPipelineOptions`) |
| `.epub` | ebooklib + BeautifulSoup4 (Docling does not support EPUB — upstream issue #515) |

### Embedding model
`BAAI/bge-large-en-v1.5` — 1024-dim, strong on medical/scientific text, runs fully locally, cached in `~/.cache/huggingface` after first download.

### Chunking
- `CHUNK_SIZE = 512` tokens
- `CHUNK_OVERLAP = 64` tokens
- Splitter: `SentenceSplitter` (LlamaIndex) — respects sentence boundaries

### Section / page output format
Both extractors return the same `list[dict]` shape:

```python
{
    "page_number":    int,        # PDF: 1-based page; EPUB: spine position
    "section_number": int,        # same value, unified query field
    "text":           str,        # body text + inline [Image: …] markers
    "image_links":    list[str],  # absolute paths to saved image files
    "source_file":    str,        # filename only
    "source_path":    str,        # absolute path
    "format":         str,        # "pdf" or "epub"
    "chunk_hash":     str,        # MD5 fingerprint for idempotency
}
```

### Qdrant payload / metadata
All fields above are stored as Qdrant payload. Fields excluded from LLM context and embedding text (paths are not semantically useful): `source_path`, `chunk_hash`, `image_links`.

---

## 5. Image Extraction Logic

### PDF — Docling `PictureItem`

```python
pipeline_opts = PdfPipelineOptions(generate_picture_images=True, images_scale=2.0)
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts)}
)
result = converter.convert(path)

for element, _ in result.document.iterate_items():
    if isinstance(element, PictureItem):
        page_no   = element.prov[0].page_no        # 1-based
        pil_image = element.image.pil_image         # PIL.Image
        caption   = element.caption_text(doc=doc)  # str | ""
```

Images are saved as PNG regardless of source format. Filename: `{book_stem}_{md5_of_bytes[:10]}.png`.

### EPUB — ebooklib + BeautifulSoup4 (three-pass)

**Pass 1 — image asset index**
Iterates `book.get_items_of_type(ITEM_IMAGE)`. Builds `epub_item_name → (bytes, ext)`. SVG files are skipped (decorative in medical books). Supported MIME types: `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/tiff`.

**Pass 2 — hyperlink cross-reference map** *(the "Historical Anatomy" logic)*
Iterates every HTML item and, for each `<a href="…#anchor">`, records the full parent paragraph text under `anchor_id` as a key:

```python
# Example: descriptions chapter
# <p><a href="plates.xhtml#plate_i">Plate I.</a> The brachial plexus, C5-T1…</p>
# → cross_ref["plate_i"] = ["Plate I. The brachial plexus, C5-T1…"]
```

This resolves the pattern in older anatomy atlases where images live in a "Plates" chapter and their verbose descriptions live in a separate "Descriptions / Legends" chapter, linked by HTML anchors.

**Pass 3 — spine-order extraction**
Processes HTML items in reading order (via `book.spine`). For each `<img>`:

1. Resolve `src` relative path → canonical EPUB item name (`_resolve_epub_img_src`)
2. Look up bytes in asset map, save to disk
3. Collect immediate context via `_image_surrounding_text`:
   - `alt` attribute
   - `<figcaption>` inside the nearest `<figure>` or `<div>`
   - Up to 2 sibling block elements before and after the image container
4. Climb the DOM to find the nearest ancestor with an `id` attribute
5. Look that `id` up in the cross-reference map; attach up to 3 matching descriptions
6. Combine into an inline text marker:
   ```
   [Image: alt | figcaption | sibling text | Plate I. The brachial plexus…]
   ```

This marker is embedded into the text stream so the semantic embedding captures the figure's meaning even in chunks that don't include surrounding body text.

### Image filename convention
```
{slug}_p{page}_fig{n}.png
# e.g. sobotta_vol1_p147_fig1.png
```

- **Deterministic**: book + page + figure index → same name on re-run
- **Idempotent**: skips write if file already exists
- **Traceable**: human-readable source identification

---

## 6. Qdrant Collections

| Collection | content_type(s) | Status |
|---|---|---|
| `medical_literature` | `medical_literature` | Not yet created (no books ingested) |
| `training_materials` | `training_nrt`, `training_qat` | Not yet created |
| `device_protocols` | `device_pemf`, `device_rlt` | Not yet created |

Collections are auto-created on first ingestion run.

---

## 7. Installed Python Dependencies

| Package | Status | Purpose |
|---|---|---|
| `docling` | **Not installed** | PDF extraction, figure detection |
| `easyocr` | **Not installed** | OCR for scanned PDFs + figure labels |
| `openai-whisper` | **Not installed** | Video transcription |
| `llama-index` | **Not installed** | Chunking, VectorStoreIndex |
| `llama-index-vector-stores-qdrant` | **Not installed** | Qdrant backend |
| `llama-index-embeddings-huggingface` | **Not installed** | Local embeddings |
| `qdrant-client` | **Not installed** | Qdrant REST/gRPC client |
| `pypdf` | **Not installed** | PDF text density pre-scan |
| `pillow` | **Not installed** | PIL image handling |
| `ebooklib` | Installed | EPUB parsing |
| `beautifulsoup4` | Installed | HTML parsing for EPUB |
| `lxml` | System dep | XML/HTML parser |

**Install all at once:**
```bash
pip install docling docling-core easyocr openai-whisper \
    llama-index llama-index-vector-stores-qdrant \
    llama-index-embeddings-huggingface \
    qdrant-client pypdf pillow numpy \
    --break-system-packages
apt-get install -y ffmpeg
```

---

## 8. Pending Tasks

- [ ] **Install Python dependencies** — `pip install docling easyocr openai-whisper llama-index qdrant-client pypdf pillow --break-system-packages` + `apt install ffmpeg`
- [ ] **Add books** — Drop `.pdf`/`.epub` into `./books/`, run `fetch_book_metadata.py` then `ingest_books.py --content-type medical_literature`
- [ ] **Add training videos** — Drop `.mp4` into `./videos/nrt/` and `./videos/qat/`, run `transcribe_videos.py --type nrt --ingest`
- [ ] **Add device docs** — Drop PEMF/RLT PDFs or `.md` settings files, run ingestion with `--content-type device_pemf` / `device_rlt`
- [ ] **Multi-collection query** — Build `query_rag.py` that queries `medical_literature` + `training_materials` + `device_protocols` in parallel and merges results
- [ ] **FastAPI web layer** — Upload UI, metadata review cards, Q&A endpoint, protocol generation, blog generation
- [ ] **Word output** — Generate `.docx` treatment protocols (§1 Klachtbeeld / §2 Behandeling / §3 Bijlagen)
- [ ] **Tailscale** — Configure access control

## 8. Known Issues

| Issue | Severity | Notes |
|---|---|---|
| EPUB has no real page numbers | Low | `page_number` stores spine position (1-based reading order). Acceptable for retrieval; note in any UI. |
| Docling EPUB support | Low | Tracked upstream as issue #515. Current workaround (ebooklib) is full-featured for the anatomy use case. |
| No swap configured | Medium | If both Qdrant and Ollama are under peak load simultaneously and exceed their memory limits, the kernel OOM killer may intervene. Monitor with `docker stats` during heavy ingestion. |
| `docker-compose` v1 bug with new images | Resolved | v1.29.2 throws `KeyError: 'ContainerConfig'` on recreate. Workaround: always `docker-compose down` before `docker-compose up -d`. |
