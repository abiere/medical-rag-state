# Technical Design — Medical RAG System

> Implementation-level reference. For requirements see REQUIREMENTS.md;
> for stack overview see ARCHITECTURE.md.

---

## 1. Ingestion Pipeline

### Entry point
```
python scripts/ingest_books.py --books-dir ./books --collection anatomy --subject anatomy
```

### Flow

```
books/*.{pdf,epub}
      │
      ▼
extract_book()
  ├─ PDF → extract_pdf()          ← Docling + optional EasyOCR
  └─ EPUB → extract_epub()        ← ebooklib + BeautifulSoup4
      │
      ▼  list[section dict]
      │
      ├─ _write_processing_log()  → data/processing_logs/{slug}.json
      │
      ├─ _build_citation_payload()← data/books_metadata.json
      │
      ▼
sections_to_llama_documents()     ← LlamaIndex Document objects
      │
      ▼
build_index()
  ├─ SentenceSplitter (512 tok / 64 overlap)
  ├─ HuggingFaceEmbedding (BAAI/bge-large-en-v1.5, 1024-dim)
  └─ QdrantVectorStore → upsert
```

### Scanned PDF detection
1. `_estimate_pdf_text_density(path)` — uses pypdf to extract raw text; returns average chars/page.
2. If avg < `OCR_CHARS_PER_PAGE_THRESHOLD` (default 50), Docling is re-run with `do_ocr=True` and `EasyOcrOptions()`.
3. `stats["ocr_applied"]` and `stats["pages_with_ocr"]` are written to the processing log.
4. Detection is document-level (Docling's OCR flag is per-document). True per-page OCR would require a custom Docling subclass.

### Figure extraction

For every `PictureItem` (Docling) or `<img>` (EPUB):

| Step | Detail |
|---|---|
| **Save** | `data/extracted_images/{slug}_p{page}_fig{n}.png` — deterministic, idempotent |
| **Caption** | Docling: `element.caption_text(doc)`. EPUB: `<figcaption>` text |
| **Labels** | EasyOCR on the figure PIL image (confidence > 0.5, length > 1 char) |
| **Type** | `table` if TableItem; `diagram` if labels > 3; else `figure` |
| **Description** | Ollama vision (LLaVA) if loaded; else `"pending"` |
| **Figure number** | Regex on caption + surrounding text: `Fig. 4.52`, `Abb. 3`, `Afb. 2.4` |

Multiple figures per page/section are aggregated: captions joined with ` | `, labels deduplicated, type/description from the first figure.

### Figure filename convention
```
{book_slug}_p{page_number}_fig{n}.png

Examples:
  sobotta_vol1_p147_fig1.png
  magee_7e_p445_fig2.png
  sobotta_vol1_p203_fig1.png   ← EPUB spine position used as "page"
```
- Deterministic per extraction order (same book/page/figure → same name)
- Idempotent: `_save_figure()` skips write if file already exists
- Human-readable: book + page in filename makes manual lookup easy

---

## 2. Bibliographic Metadata Pipeline

### Entry point
```
python scripts/fetch_book_metadata.py --books-dir ./books
python scripts/fetch_book_metadata.py --file books/Sobotta-Vol1.epub
python scripts/fetch_book_metadata.py --isbn 9780723436898
python scripts/fetch_book_metadata.py --refresh --slug sobotta_vol1
```

### Source priority

```
1. File-level   EPUB OPF (dc:title, dc:creator, dc:identifier, dc:publisher, dc:date)
                PDF XMP + DocInfo (/Title, /Author, /Subject, /Creator, /CreationDate)
2. Filename     ISBN regex fallback (e.g. 9780723436898_Sobotta.epub)
3. OpenLibrary  https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data
                Fallback: https://openlibrary.org/search.json?q={title}
4. Google Books https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}
```

OpenLibrary provides: full title, subtitle, authors, publisher, publish_date, page count, subjects, ISBN-10/13, LC classification.
Google Books fills: description, categories, language, cover thumbnail.

### books_metadata.json structure

Located at `data/books_metadata.json`. Keyed by book slug.

```json
{
  "sobotta_vol1": {
    "slug":                "sobotta_vol1",
    "filename":            "Sobotta-Vol1.epub",
    "title":               "Sobotta Atlas of Human Anatomy, Vol. 1",
    "subtitle":            "General Anatomy and Musculoskeletal System",
    "authors":             ["Friedrich Paulsen", "Jens Waschke"],
    "editors":             [],
    "publisher":           "Elsevier",
    "publisher_city":      "",
    "publish_year":        2011,
    "edition":             "15th",
    "isbn_10":             "0723436894",
    "isbn_13":             "9780723436898",
    "language":            "en",
    "total_pages":         896,
    "subjects":            ["Human anatomy", "Atlas"],
    "description":         "…",
    "lc_class":            "QM23.2",
    "metadata_source":     "openlibrary",
    "metadata_retrieved":  "2026-04-14T15:00:00Z",
    "ingested":            false,
    "ingestion_date":      null,
    "total_chunks":        0,
    "total_figures":       0,
    "citation_apa":        "Paulsen, F., & Waschke, J. (2011). Sobotta Atlas of Human Anatomy, Vol. 1 (15th ed.). Elsevier.",
    "citation_vancouver":  "Paulsen F, Waschke J. Sobotta Atlas of Human Anatomy, Vol. 1. 15th ed. Elsevier; 2011.",
    "citation_chicago":    "Paulsen, Friedrich, and Jens Waschke. Sobotta Atlas of Human Anatomy, Vol. 1. 15th ed. Elsevier, 2011."
  }
}
```

After ingestion `ingest_books.py` writes back: `ingested: true`, `ingestion_date`, `total_chunks`, `total_figures`.

### Web interface review card (planned)

After each import, the FastAPI web layer shows a metadata card where Axel can:
- Confirm or correct: title, authors, year, edition
- Add a missing ISBN to trigger re-fetch
- Click "Re-fetch" → calls `/api/books/{slug}/refresh-metadata`
  which runs `process_book(..., force_refresh=True)` and updates the JSON

---

## 3. Citation Formats

Three formats are generated and stored per book in `books_metadata.json`,
and per chunk in the Qdrant payload.

### APA 7th Edition
```
Paulsen, F., & Waschke, J. (2011). Sobotta Atlas of Human Anatomy, Vol. 1
(15th ed.). Elsevier. p. 147
```
Rules: Last, I. format; `&` before final author; year in parentheses; edition in parentheses.

### Vancouver (ICMJE / medical standard)
```
Paulsen F, Waschke J. Sobotta Atlas of Human Anatomy, Vol. 1. 15th ed.
Elsevier; 2011. Fig. 4.52, p. 147.
```
Rules: no punctuation in initials; ≤ 6 authors then "et al."; semicolon before year.

### Chicago 17th
```
Paulsen, Friedrich, and Jens Waschke. Sobotta Atlas of Human Anatomy, Vol. 1.
15th ed. Elsevier, 2011.
```
Rules: first author Last, First; "and" before final author; > 3 authors → et al.

---

## 4. Qdrant Payload Structure

Every point in Qdrant carries this payload (all fields filterable):

```json
{
  "source_file":       "Sobotta-Vol1.epub",
  "page_number":       147,
  "section_number":    147,
  "format":            "epub",
  "subject":           "anatomy",
  "chapter":           "",
  "image_links":       ["/root/medical-rag/data/extracted_images/sobotta_vol1_p147_fig1.png"],
  "chunk_hash":        "a3f9b21c04…",

  "caption":           "Regio cervicalis posterior, lateral view",
  "figure_labels":     ["M. trapezius", "C7", "Lig. nuchae"],
  "image_type":        "diagram",
  "image_description": "Posterior cervical region showing trapezius muscle and C7 vertebra.",
  "figure_number":     "Fig. 4.52",

  "citation": {
    "authors":        ["Friedrich Paulsen", "Jens Waschke"],
    "year":           2011,
    "title":          "Sobotta Atlas of Human Anatomy, Vol. 1",
    "edition":        "15th",
    "publisher":      "Elsevier",
    "page":           147,
    "figure_number":  "Fig. 4.52",
    "figure_caption": "Regio cervicalis posterior, lateral view",
    "apa":            "Paulsen, F., & Waschke, J. (2011). Sobotta Atlas … p. 147",
    "vancouver":      "Paulsen F, Waschke J. Sobotta Atlas … Fig. 4.52, p. 147."
  },

  "citation_apa":      "Paulsen, F., & Waschke, J. (2011). … p. 147"
}
```

Fields excluded from LLM prompt (structural, not useful as reasoning text):
`source_path`, `chunk_hash`, `image_links`, `figure_labels`, `image_type`, `citation` (nested)

Fields excluded from embedding (same + citation dicts):
`source_path`, `chunk_hash`, `image_links`, `figure_labels`, `image_type`, `citation`

Fields included in LLM context (semantic value):
`source_file`, `page_number`, `format`, `subject`, `caption`, `image_description`,
`figure_number`, `citation_apa` (flat string for citation generation)

---

## 5. Image Memory System

`data/image_memory.json` stores Axel's previously selected images per
tissue/structure. Updated by the web interface after protocol generation.

```json
{
  "M. trapezius":        ["sobotta_vol1_p147_fig1.png"],
  "lumbale wervelkolom": ["sobotta_vol2_p203_fig2.png"],
  "facetgewricht L4-L5": ["magee_7e_p445_fig1.png"]
}
```

On protocol generation: when a tissue is included in §2 (Behandeling), the
UI pre-selects the images in its memory entry. Axel confirms or replaces them.
On confirm, the memory entry is updated.

---

## 6. Processing Logs

Written per book to `data/processing_logs/{slug}.json` after every ingestion run.

```json
{
  "book":                     "Sobotta-Vol1.epub",
  "slug":                     "sobotta_vol1",
  "format":                   "epub",
  "ocr_applied":              false,
  "avg_chars_per_page":       null,
  "total_pages":              312,
  "pages_with_ocr":           0,
  "figures_extracted":        476,
  "figures_with_captions":    420,
  "figures_without_captions": 56,
  "figures_with_labels":      312,
  "figures_without_labels":   164,
  "errors":                   [],
  "processed_at":             "2026-04-14T15:30:00Z"
}
```

---

## 7. Pre/Post Checks (NFR-4)

Before large ingestion runs the caller should verify resources:

```bash
# Recommended pre-checks
free -h                          # >= 4 GB free RAM
df -h /                          # >= 20 GB free disk (image extraction)
docker ps                        # Qdrant + Ollama Up, healthy
curl -s http://localhost:6333/   # Qdrant REST responds
curl -s http://localhost:11434/api/tags | python3 -m json.tool
```

Post-check after ingestion:
```bash
curl -s http://localhost:6333/collections/{collection}/points/count
# Inspect a sample point to verify citation and figure fields
```

---

## 8. Acupuncture Point Images

476 PNG files with naming convention: `[MERIDIAN][NN].png`

Examples: `GB-20.png`, `BL-58.png`, `LI-4.png`, `ST-36.png`

These are NOT ingested through the standard pipeline. They are referenced
directly by the protocol generator when acupuncture points are selected.
Stored separately from anatomy images (different directory, TBD).

---

## 9. Key File Locations

| Path | Purpose |
|---|---|
| `scripts/ingest_books.py` | PDF/EPUB ingestion (all content types) |
| `scripts/ingest_text.py` | Plain text / Markdown ingestion |
| `scripts/transcribe_videos.py` | Video → Whisper transcript → Qdrant |
| `scripts/fetch_book_metadata.py` | Bibliographic metadata fetcher |
| `data/books_metadata.json` | Per-book metadata + citation strings |
| `data/image_memory.json` | Axel's image selections per tissue |
| `data/video_document_links.json` | Video ↔ PDF cross-references |
| `data/extracted_images/` | Extracted figures |
| `data/transcripts/` | Whisper JSON + TXT transcripts |
| `data/device_settings/` | Curated PEMF / RLT settings files |
| `data/processing_logs/{slug}.json` | Per-book ingestion stats |
| `videos/nrt/` | NRT training videos |
| `videos/qat/` | QAT training videos |
| `videos/pemf/` | PEMF instruction videos |
| `videos/rlt/` | RLT instruction videos |
| `docker-compose.yml` | Qdrant + Ollama services |
| `SYSTEM_DOCS/CONTEXT.md` | Session loader (read first) |

---

## 10. Content Types

Every Qdrant chunk carries a `content_type` field. This determines which
collection it lives in and how the protocol generator uses it.

| content_type | Qdrant collection | Source | Used in protocol |
|---|---|---|---|
| `medical_literature` | `medical_literature` | Anatomy/clinical EPUBs/PDFs | §1 Klachtbeeld, §3 Bijlagen |
| `training_nrt` | `training_materials` | NRT PDFs + video transcripts | §2 NRT muscle resets |
| `training_qat` | `training_materials` | QAT text/PDFs + video transcripts | §2 QAT tissue sequence |
| `device_pemf` | `device_protocols` | PEMF manuals/videos/settings | §2 PEMF settings |
| `device_rlt` | `device_protocols` | RLT manuals/videos/settings | §2 RLT settings |

### Ingestion command per content type

```bash
# Medical literature (anatomy, clinical)
python scripts/ingest_books.py --books-dir ./books --content-type medical_literature

# NRT training PDFs
python scripts/ingest_books.py --books-dir ./books/nrt --content-type training_nrt

# QAT plain text manual
python scripts/ingest_text.py --file books/QAT_Manual.txt \
  --content-type training_qat --title "QAT Manual"

# PEMF device manual (PDF)
python scripts/ingest_books.py --books-dir ./books/pemf --content-type device_pemf

# NRT video transcripts
python scripts/transcribe_videos.py --type nrt --ingest
```

---

## 11. Video Transcription Pipeline

### Dependencies
```bash
pip install openai-whisper --break-system-packages
apt-get install -y ffmpeg
```

### Flow per video
```
videos/{type}/{file}.mp4
        │
        ▼
ffmpeg → 16 kHz mono WAV (temporary)
        │
        ▼
whisper.load_model("medium")
whisper.transcribe(audio, language="nl")
        │
        ├─ data/transcripts/{stem}.json  — {"segments": [{"start","end","text"}]}
        ├─ data/transcripts/{stem}.txt   — plain text
        │
        ├─ _find_related_documents()     — name-match against books/
        ├─ video_document_links.json     — updated
        │
        └─ (optional) _ingest_transcript() → Qdrant training_materials
```

### Whisper model tradeoffs

| Model | VRAM | Speed | Accuracy | Recommended for |
|---|---|---|---|---|
| `tiny` | ~1 GB | 32× RT | low | Quick test |
| `small` | ~2 GB | 8× RT | medium | Short clips |
| `medium` | ~5 GB | 2× RT | high | **Default — NRT/QAT** |
| `large` | ~10 GB | 1× RT | highest | Critical accuracy |

RT = real-time. On 16 vCPU CPU-only: `medium` ≈ 3–4× real-time.
RAM budget: `medium` model needs ~3 GB; safe alongside Qdrant (32 MiB) + Ollama idle.

### Video–document linking

`data/video_document_links.json` maps video filenames to related content:
```json
{
  "NRT_Shoulder_Advanced.mp4": {
    "related_muscles":   ["M. infraspinatus", "M. supraspinatus"],
    "related_pdf_pages": [
      {"file": "NRT_Training_Manual.pdf", "page": 47}
    ]
  }
}
```

Auto-populated by name matching; manually refined via web interface.
The `see_also` field on transcript chunks links to related PDF files.

### Idempotency
Transcription is skipped if `data/transcripts/{stem}.json` already exists.
Delete the file to force re-transcription.

---

## 12. Multi-Collection Search Strategy

The treatment protocol generator queries all three collections and merges results.

### Query flow (planned FastAPI endpoint)
```
POST /api/generate/protocol  { "condition": "lumbale pijn" }
        │
        ├─ embed(condition) → query_vector
        │
        ├─ Qdrant search: medical_literature  (top 10, cosine)
        ├─ Qdrant search: training_materials  (top 5, cosine)
        └─ Qdrant search: device_protocols    (top 5, cosine)
                │
                ▼  merge + re-rank by score
                │
        ├─ content_type=medical_literature → §1 + §3 (anatomy, rationale)
        ├─ content_type=training_nrt/qat   → §2 (muscle resets, tissue sequence)
        └─ content_type=device_pemf/rlt    → §2 (device settings, auto-formatted)
                │
                ▼
        Ollama llama3.1:8b  →  structured Word document
```

### Collection filter examples (Qdrant Python client)
```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Only PEMF results for a body region
result = client.search(
    collection_name="device_protocols",
    query_vector=embed(question),
    query_filter=Filter(must=[
        FieldCondition(key="content_type",  match=MatchValue(value="device_pemf")),
        FieldCondition(key="body_region",   match=MatchValue(value="lumbal")),
    ]),
    limit=5,
)

# Only chunks with images
result = client.search(
    collection_name="medical_literature",
    query_vector=embed(question),
    query_filter=Filter(must_not=[
        FieldCondition(key="image_links", match=MatchValue(value=[])),
    ]),
    limit=10,
)
```
