"""
Medical RAG — Plain Text / Markdown Ingestion

Imports manually typed or clean text files (.txt, .md) directly into Qdrant
without requiring a PDF or EPUB.  Useful for:
  - QAT training manuals typed up by Axel
  - NRT protocol notes
  - Device setting summaries
  - Any structured text that doesn't come from a book

Usage
─────
    python scripts/ingest_text.py \\
        --file /root/medical-rag/books/QAT_Manual_Clean.txt \\
        --content-type training_qat \\
        --title "QAT Training Manual" \\
        --author "QAT Institute" \\
        --year 2024

    python scripts/ingest_text.py \\
        --file books/PEMF_Settings.md \\
        --content-type device_pemf \\
        --title "PEMF Protocol Guide" \\
        --dry-run

Requirements
────────────
    pip install llama-index llama-index-vector-stores-qdrant \\
                llama-index-embeddings-huggingface qdrant-client
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR            = Path("/root/medical-rag")
BOOKS_METADATA_PATH = BASE_DIR / "data" / "books_metadata.json"
LOGS_DIR            = BASE_DIR / "data" / "processing_logs"

QDRANT_URL    = "http://localhost:6333"
EMBED_MODEL   = "BAAI/bge-large-en-v1.5"
EMBED_DIM     = 1024
CHUNK_SIZE    = 512
CHUNK_OVERLAP = 64

CONTENT_TYPE_COLLECTION: dict[str, str] = {
    "medical_literature": "medical_literature",
    "training_nrt":       "training_materials",
    "training_qat":       "training_materials",
    "device_pemf":        "device_protocols",
    "device_rlt":         "device_protocols",
}

# Accepted file extensions
TEXT_EXTENSIONS = {".txt", ".md", ".rst"}


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def _book_slug(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "_", path.stem.lower()).strip("_")


def _format_apa_authors(authors: list[str]) -> str:
    if not authors:
        return "Unknown Author"
    parts = []
    for name in authors:
        words = name.split()
        if len(words) >= 2:
            initials = "".join(f"{w[0]}." for w in words[:-1])
            parts.append(f"{words[-1]}, {initials}")
        else:
            parts.append(name)
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]}, & {parts[1]}"
    return ", ".join(parts[:-1]) + f", & {parts[-1]}"


def _build_citation(
    authors: list[str], year: int | None, title: str, publisher: str, page: int
) -> dict:
    apa_auth = _format_apa_authors(authors)
    year_str = str(year) if year else "n.d."
    apa = f"{apa_auth} ({year_str}). {title}. {publisher}. p. {page}".strip(". ")
    vancouver = (
        f"{', '.join(authors) or 'Unknown'}. "
        f"{title}. {publisher}; {year_str}. p. {page}."
    )
    return {
        "authors":   authors,
        "year":      year,
        "title":     title,
        "publisher": publisher,
        "page":      page,
        "apa":       apa,
        "vancouver": vancouver,
    }


# ---------------------------------------------------------------------------
# Text splitting
# ---------------------------------------------------------------------------

def _split_text(
    text: str,
    chunk_size: int  = CHUNK_SIZE,
    overlap:    int  = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into roughly chunk_size-character chunks with overlap.
    Tries to break on sentence/paragraph boundaries.
    Falls back to character splits for very long sentences.
    """
    # Split on double newlines (paragraphs) first
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > chunk_size and current:
            chunks.append("\n\n".join(current))
            # Overlap: keep the last paragraph as the start of the next chunk
            current     = [current[-1]] if overlap > 0 else []
            current_len = len(current[0]) if current else 0
        current.append(para)
        current_len += para_len

    if current:
        chunks.append("\n\n".join(current))

    # Further split any chunk that is still too long
    final: list[str] = []
    for chunk in chunks:
        if len(chunk) <= chunk_size * 2:
            final.append(chunk)
        else:
            # Hard split on sentences
            sentences = re.split(r"(?<=[.!?])\s+", chunk)
            buf: list[str] = []
            buf_len = 0
            for sent in sentences:
                if buf_len + len(sent) > chunk_size and buf:
                    final.append(" ".join(buf))
                    buf = buf[-1:] if overlap > 0 else []
                    buf_len = len(buf[0]) if buf else 0
                buf.append(sent)
                buf_len += len(sent)
            if buf:
                final.append(" ".join(buf))

    return [c for c in final if c.strip()]


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

def ingest_text_file(
    file_path:    Path,
    content_type: str,
    title:        str,
    authors:      list[str],
    year:         int | None,
    publisher:    str,
    subject:      str,
    collection:   str | None,
    dry_run:      bool,
) -> dict:
    """
    Read a text/markdown file, split into chunks, and upsert into Qdrant.
    Returns a stats dict.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    slug     = _book_slug(file_path)
    chunks   = _split_text(raw_text)
    target_collection = collection or CONTENT_TYPE_COLLECTION.get(
        content_type, "medical_literature"
    )

    logger.info(
        "Text file: %s  →  %d chunks  [content_type=%s, collection=%s]",
        file_path.name, len(chunks), content_type, target_collection,
    )

    stats = {
        "book":           file_path.name,
        "slug":           slug,
        "format":         file_path.suffix.lstrip("."),
        "content_type":   content_type,
        "collection":     target_collection,
        "total_pages":    len(chunks),
        "ocr_applied":    False,
        "avg_chars_per_page": round(len(raw_text) / max(1, len(chunks))),
        "figures_extracted":        0,
        "figures_with_captions":    0,
        "figures_without_captions": 0,
        "figures_with_labels":      0,
        "figures_without_labels":   0,
        "errors": [],
        "processed_at": datetime.datetime.utcnow().isoformat() + "Z",
    }

    if dry_run:
        logger.info("DRY RUN — preview of first 3 chunks:")
        for i, c in enumerate(chunks[:3]):
            logger.info("  Chunk %d (%d chars): %s …", i + 1, len(c), c[:100])
        return stats

    # ── Build LlamaIndex documents ───────────────────────────────────────────
    try:
        from llama_index.core import Document, Settings, VectorStoreIndex  # type: ignore
        from llama_index.core.node_parser import SentenceSplitter           # type: ignore
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding  # type: ignore
        from llama_index.vector_stores.qdrant import QdrantVectorStore      # type: ignore
        from qdrant_client import QdrantClient                              # type: ignore
        from qdrant_client.models import Distance, VectorParams             # type: ignore
    except ImportError as exc:
        raise ImportError(
            "pip install llama-index llama-index-vector-stores-qdrant "
            "llama-index-embeddings-huggingface qdrant-client"
        ) from exc

    documents = []
    for i, chunk_text in enumerate(chunks, start=1):
        chunk_hash = hashlib.md5(
            f"{file_path.name}:c{i}:{chunk_text[:64]}".encode()
        ).hexdigest()
        citation = _build_citation(authors, year, title, publisher, i)
        doc = Document(
            text=chunk_text,
            metadata={
                "source_file":       file_path.name,
                "source_path":       str(file_path),
                "page_number":       i,
                "section_number":    i,
                "format":            file_path.suffix.lstrip("."),
                "content_type":      content_type,
                "subject":           subject,
                "chapter":           "",
                "image_links":       [],
                "chunk_hash":        chunk_hash,
                "caption":           "",
                "figure_labels":     [],
                "image_type":        "",
                "image_description": "",
                "figure_number":     "",
                "citation":          citation,
                "citation_apa":      citation["apa"],
                "see_also":          [],
                # Device fields (empty for non-device content)
                "device":            "",
                "setting":           None,
                "program":           None,
                "intensity_range":   None,
                "duration_minutes":  None,
                "indication":        None,
                "contraindication":  None,
                "body_region":       "",
            },
            excluded_llm_metadata_keys=[
                "source_path", "chunk_hash", "image_links",
                "figure_labels", "image_type", "citation", "see_also",
                "device", "setting", "program", "intensity_range",
            ],
            excluded_embed_metadata_keys=[
                "source_path", "chunk_hash", "image_links",
                "figure_labels", "image_type", "citation",
            ],
        )
        documents.append(doc)

    # ── Index ────────────────────────────────────────────────────────────────
    logger.info("Loading embedding model: %s", EMBED_MODEL)
    Settings.embed_model   = HuggingFaceEmbedding(model_name=EMBED_MODEL)
    Settings.chunk_size    = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP
    Settings.llm           = None

    client   = QdrantClient(url=QDRANT_URL)
    existing = {c.name for c in client.get_collections().collections}
    if target_collection not in existing:
        logger.info("Creating collection '%s'", target_collection)
        client.create_collection(
            collection_name=target_collection,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )

    vector_store = QdrantVectorStore(client=client, collection_name=target_collection)
    logger.info("Indexing %d documents …", len(documents))
    VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store,
        transformations=[
            SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        ],
        show_progress=True,
    )
    logger.info("Done — '%s' collection updated.", target_collection)

    # ── Write processing log ─────────────────────────────────────────────────
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"{slug}.json"
    log_path.write_text(json.dumps(stats, indent=2))

    # ── Update books_metadata.json ───────────────────────────────────────────
    if BOOKS_METADATA_PATH.exists():
        try:
            meta = json.loads(BOOKS_METADATA_PATH.read_text())
            if slug not in meta:
                meta[slug] = {}
            meta[slug].update({
                "slug":             slug,
                "filename":         file_path.name,
                "title":            title,
                "authors":          authors,
                "publisher":        publisher,
                "publish_year":     year,
                "content_type":     content_type,
                "media_type":       "text",
                "is_primary_source": False,
                "internal_only":    True,
                "ingested":         True,
                "ingestion_date":   datetime.datetime.utcnow().isoformat() + "Z",
                "total_chunks":     len(documents),
                "total_figures":    0,
            })
            BOOKS_METADATA_PATH.write_text(json.dumps(meta, indent=2))
        except Exception as exc:
            logger.warning("Could not update books_metadata.json: %s", exc)

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest plain text / Markdown files into Qdrant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--file", type=Path, required=True,
                        help="Path to .txt or .md file")
    parser.add_argument("--content-type", required=True,
                        choices=list(CONTENT_TYPE_COLLECTION.keys()),
                        help="Content type tag")
    parser.add_argument("--title",     default="",   help="Document title")
    parser.add_argument("--author",    default="",
                        help="Author name(s), comma-separated")
    parser.add_argument("--year",      type=int, default=None, help="Publication year")
    parser.add_argument("--publisher", default="",   help="Publisher name")
    parser.add_argument("--subject",   default="",   help="Subject tag")
    parser.add_argument("--collection", default=None,
                        help="Override Qdrant collection (default: derived from content-type)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse and preview chunks without writing to Qdrant")
    return parser.parse_args()


def main() -> None:
    args    = parse_args()
    authors = [a.strip() for a in args.author.split(",") if a.strip()]

    stats = ingest_text_file(
        file_path    = args.file.resolve(),
        content_type = args.content_type,
        title        = args.title or args.file.stem,
        authors      = authors,
        year         = args.year,
        publisher    = args.publisher,
        subject      = args.subject,
        collection   = args.collection,
        dry_run      = args.dry_run,
    )
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
