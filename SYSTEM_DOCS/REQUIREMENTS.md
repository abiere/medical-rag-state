# Requirements — Medical RAG System

## Access & Security

- Web interface accessible **via Tailscale only** (not exposed to the public internet)
- No public authentication layer required — Tailscale network membership is the access control

## Book Ingestion

- Upload books in **PDF** and **EPUB** format through the web interface
- Process with **Docling**: extract text, images, and page numbers
- Images saved locally; inline `[Image: …]` markers embedded in text so image context is captured by the vector embedding
- Idempotent: re-uploading the same file must not create duplicate vectors (enforced via `chunk_hash`)
- Page numbers preserved and stored as Qdrant payload for citation purposes

## Vector Search

- Embeddings generated locally with `BAAI/bge-large-en-v1.5` (1024-dim)
- Vectors stored in **Qdrant**; collection per subject (e.g. `anatomy`, `acupuncture`)
- Retrieval returns top-K chunks with `source_file`, `page_number`, and `image_links` payload

## Output Types

### Treatment Protocols
- Generated as **Word documents** (`.docx`)
- Content: acupuncture points with rationale, supporting images, and sourced citations
- Each claim cites source book and page number

### Blog Articles
- Plain prose suitable for publication on **nrt-amsterdam.nl**
- Grounded in retrieved literature; references listed at end of article
- Tone: professional but accessible (patient-facing)

### Ad Hoc Q&A
- Free-form questions answered against the full literature database
- Answer includes inline citations: `[Author/Title, p. N]`
- Optional: filter search to a specific subject collection or source file

## Citation Requirements

- **All** generated content must cite sources with book title and page number
- Images in Word output must reference source page
- No hallucinated references — LLM must only cite chunks that were actually retrieved

## Non-Requirements (explicit exclusions)

- No cloud LLM APIs — all inference runs locally via Ollama
- No public-facing endpoints — Tailscale-only
- No user accounts or multi-tenancy for now
