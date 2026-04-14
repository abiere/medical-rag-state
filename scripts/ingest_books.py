"""
Medical RAG – Book Ingestion Pipeline  (PDF + EPUB)

Extracts text and images from PDF and EPUB books, saves images to disk,
and indexes rich text + image-link metadata into Qdrant via LlamaIndex.

EPUB special handling
─────────────────────
Docling does not yet support EPUB natively, so EPUBs are handled with
ebooklib + BeautifulSoup4.  Historical anatomy books (e.g. "Cunningham's
Manual", Gray's Atlas) often follow this layout:

  • A "Plates" section  – <figure id="plate_i"><img src="…"/></figure>
  • A "Descriptions" section – <p><a href="plates.xhtml#plate_i">Plate I.</a>
                                  The brachial plexus, anterior view…</p>

A two-pass strategy resolves this:
  Pass 1 – walk every HTML item and build a map:
              anchor_id  →  [description text that links to this anchor]
  Pass 2 – process HTML spine items in reading order; when an <img> is
             found, look up its container id in the map and attach the
             matching descriptions as searchable context.

Usage
─────
    python scripts/ingest_books.py --books-dir ./books [--collection anatomy]
    python scripts/ingest_books.py --books-dir ./books --dry-run

Requirements
────────────
    pip install llama-index llama-index-vector-stores-qdrant \
                llama-index-embeddings-huggingface \
                docling qdrant-client \
                ebooklib beautifulsoup4 lxml
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

QDRANT_URL = "http://localhost:6333"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

# BAAI/bge-large-en-v1.5: 1024-dim, strong on medical/scientific text
EMBED_MODEL_NAME = "BAAI/bge-large-en-v1.5"
EMBED_DIM = 1024

# Chunking tuned for dense medical prose and figure captions
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

IMAGES_DIR = Path("/root/medical-rag/data/extracted_images")

# EPUB image MIME types we handle (SVG intentionally excluded — decorative)
_MIME_TO_EXT: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/tiff": ".tiff",
}


# ---------------------------------------------------------------------------
# Shared image-saving utility
# ---------------------------------------------------------------------------

def _save_image(data: bytes, book_stem: str, ext: str, images_dir: Path) -> Path:
    """
    Persist image bytes to *images_dir* using a deterministic filename:
        {book_stem}_{md5_of_content[:10]}{ext}
    Skips the write if the file already exists (idempotent re-runs).
    Returns the absolute path of the saved file.
    """
    images_dir.mkdir(parents=True, exist_ok=True)
    content_hash = hashlib.md5(data).hexdigest()[:10]
    out_path = images_dir / f"{book_stem}_{content_hash}{ext}"
    if not out_path.exists():
        out_path.write_bytes(data)
    return out_path.resolve()


# ---------------------------------------------------------------------------
# PDF extraction — Docling
# ---------------------------------------------------------------------------

def extract_pdf(pdf_path: Path, images_dir: Path) -> list[dict]:
    """
    Extract per-page sections from a PDF using Docling.

    Each section dict contains:
        page_number   – 1-based PDF page
        text          – all text on the page, with [Image: …] markers inline
        image_links   – list[str] of absolute paths to saved image files
        source_file / source_path / format / chunk_hash
    """
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling_core.types.doc import PictureItem
    except ImportError as exc:
        raise ImportError("pip install docling") from exc

    logger.info("Extracting PDF: %s", pdf_path.name)

    pipeline_opts = PdfPipelineOptions(
        generate_picture_images=True,   # capture embedded figures as PIL images
        images_scale=2.0,               # 2× resolution → better quality saves
    )
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts)}
    )
    result = converter.convert(str(pdf_path))
    doc = result.document

    # Accumulate per-page data
    pages: dict[int, dict] = {}

    for element, _level in doc.iterate_items():
        page_no = element.prov[0].page_no if element.prov else 0
        if page_no not in pages:
            pages[page_no] = {"text_parts": [], "image_links": []}

        if isinstance(element, PictureItem):
            # --- Save the image ---
            pil_img = element.image.pil_image if element.image else None
            if pil_img:
                buf = io.BytesIO()
                pil_img.save(buf, "PNG")
                img_path = _save_image(buf.getvalue(), pdf_path.stem, ".png", images_dir)
                pages[page_no]["image_links"].append(str(img_path))

            # --- Inline image marker with caption ---
            caption = element.caption_text(doc=doc)
            marker = f"[Image: {caption}]" if caption else "[Image]"
            pages[page_no]["text_parts"].append(marker)

        else:
            # TextItem, TableItem, SectionHeaderItem, …
            text = getattr(element, "text", None)
            if text and text.strip():
                pages[page_no]["text_parts"].append(text.strip())

    sections: list[dict] = []
    for page_no in sorted(pages):
        data = pages[page_no]
        full_text = "\n".join(data["text_parts"]).strip()
        if not full_text and not data["image_links"]:
            continue
        sections.append({
            "page_number": page_no,
            "section_number": page_no,
            "text": full_text,
            "image_links": data["image_links"],
            "source_file": pdf_path.name,
            "source_path": str(pdf_path),
            "format": "pdf",
            "chunk_hash": hashlib.md5(
                f"{pdf_path.name}:p{page_no}:{full_text[:64]}".encode()
            ).hexdigest(),
        })

    img_count = sum(len(s["image_links"]) for s in sections)
    logger.info("  Extracted %d pages, %d images", len(sections), img_count)
    return sections


# ---------------------------------------------------------------------------
# EPUB extraction — ebooklib + BeautifulSoup4
# ---------------------------------------------------------------------------

def _build_epub_cross_ref_map(book) -> dict[str, list[str]]:
    """
    Pass 1 – scan every HTML item in the EPUB and collect, for each anchor id,
    all surrounding text snippets that *link to* that anchor.

    This resolves the common historical-anatomy pattern where a "Descriptions"
    chapter contains <a href="plates.xhtml#plate_iii">Plate III.</a> followed
    by the actual descriptive text, while the image itself sits in a "Plates"
    chapter under <figure id="plate_iii">.

    Returns: { anchor_id: [context_text_1, context_text_2, …] }
    """
    import ebooklib
    from bs4 import BeautifulSoup

    ref_map: dict[str, list[str]] = {}

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "lxml")
        for a_tag in soup.find_all("a", href=True):
            href: str = a_tag["href"]
            if "#" not in href:
                continue
            anchor = href.split("#", 1)[-1].strip()
            if not anchor:
                continue

            # Prefer the full parent paragraph/list-item text; fall back to
            # the link text itself.
            parent = a_tag.find_parent(["p", "li", "div", "td", "dd"])
            context = (
                parent.get_text(separator=" ", strip=True)
                if parent
                else a_tag.get_text(strip=True)
            )
            if len(context) > 8:   # discard trivial "See fig." links
                ref_map.setdefault(anchor, []).append(context[:600])

    return ref_map


def _image_surrounding_text(img_tag, n_siblings: int = 2) -> str:
    """
    Collect the immediate visual context around an <img> element:
    1. The img's own alt attribute
    2. Any <figcaption> inside the enclosing <figure> / <div>
    3. Up to *n_siblings* sibling block elements on each side
    """
    texts: list[str] = []

    alt = img_tag.get("alt", "").strip()
    if alt:
        texts.append(alt)

    container = img_tag.find_parent(["figure", "div", "td"]) or img_tag.parent
    if container:
        figcap = container.find("figcaption")
        if figcap:
            cap_text = figcap.get_text(strip=True)
            if cap_text and cap_text not in texts:
                texts.append(cap_text)

    block = ["p", "h1", "h2", "h3", "h4", "h5", "div", "li"]
    pivot = container or img_tag
    before: list[str] = []
    nxt = pivot
    for _ in range(n_siblings):
        sib = nxt.find_previous_sibling(block) if nxt else None
        if sib:
            t = sib.get_text(separator=" ", strip=True)
            if t:
                before.insert(0, t)
        nxt = sib

    pivot = container or img_tag
    after: list[str] = []
    prv = pivot
    for _ in range(n_siblings):
        sib = prv.find_next_sibling(block) if prv else None
        if sib:
            t = sib.get_text(separator=" ", strip=True)
            if t:
                after.append(t)
        prv = sib

    all_parts = before + texts + after
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for p in all_parts:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return " | ".join(unique)


def _resolve_epub_img_src(src: str, item_name: str) -> str:
    """
    Convert an <img src="…"> relative path to the canonical EPUB item name
    (the key used in the image asset map).
    """
    item_dir = str(Path(item_name).parent)
    raw = "/".join([item_dir, src]) if item_dir != "." else src
    # Normalise path traversal (../../images/foo.jpg → images/foo.jpg)
    parts: list[str] = []
    for part in raw.replace("\\", "/").split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part and part != ".":
            parts.append(part)
    return "/".join(parts)


def extract_epub(epub_path: Path, images_dir: Path) -> list[dict]:
    """
    Extract per-section records from an EPUB.

    Each record mirrors the PDF format (same keys) so the downstream
    LlamaIndex / Qdrant pipeline is format-agnostic.

    'page_number' is the 1-based spine position (EPUBs have no real pages).
    """
    try:
        import ebooklib
        from ebooklib import epub as ebooklib_epub
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise ImportError("pip install ebooklib beautifulsoup4 lxml") from exc

    logger.info("Extracting EPUB: %s", epub_path.name)
    book = ebooklib_epub.read_epub(str(epub_path), options={"ignore_ncx": True})

    # ── Pass 1: index all image assets ──────────────────────────────────────
    image_asset_map: dict[str, tuple[bytes, str]] = {}  # epub_name → (data, ext)
    for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        ext = _MIME_TO_EXT.get(item.media_type or "", "")
        if ext:
            image_asset_map[item.get_name()] = (item.get_content(), ext)

    logger.info("  %d image assets in EPUB", len(image_asset_map))

    # ── Pass 2: build anchor → description cross-reference map ──────────────
    logger.info("  Building hyperlink cross-reference map …")
    cross_ref = _build_epub_cross_ref_map(book)
    logger.info("  %d anchors with cross-references found", len(cross_ref))

    # ── Pass 3: process HTML spine items in reading order ───────────────────
    spine_ids: set[str] = {item_id for item_id, _ in book.spine}
    spine_items = [
        book.get_item_with_id(item_id)
        for item_id in (i for i, _ in book.spine)
        if book.get_item_with_id(item_id) is not None
    ]

    sections: list[dict] = []

    for section_num, item in enumerate(spine_items, start=1):
        if item.get_id() not in spine_ids:
            continue

        soup = BeautifulSoup(item.get_content(), "lxml")
        text_parts: list[str] = []
        image_links: list[str] = []

        # Collect body text (skip content inside <figure> — handled below)
        for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "li"]):
            if tag.find_parent("figure"):
                continue
            t = tag.get_text(separator=" ", strip=True)
            if t:
                text_parts.append(t)

        # Process every <img> in this section
        for img_tag in soup.find_all("img"):
            src = img_tag.get("src", "").strip()
            if not src:
                continue

            epub_name = _resolve_epub_img_src(src, item.get_name())
            if epub_name not in image_asset_map:
                logger.debug("  Skipping unresolved img src: %s → %s", src, epub_name)
                continue

            img_data, ext = image_asset_map[epub_name]
            img_path = _save_image(img_data, epub_path.stem, ext, images_dir)
            image_links.append(str(img_path))

            # ── Immediate visual context (alt, figcaption, siblings) ─────
            surrounding = _image_surrounding_text(img_tag)

            # ── Cross-reference context (descriptions from elsewhere) ────
            # Find the nearest ancestor that carries an id attribute — that
            # is the anchor that description chapters link back to.
            container_id: str | None = None
            for ancestor in img_tag.parents:
                if ancestor.get("id"):
                    container_id = ancestor["id"]
                    break
            img_own_id = img_tag.get("id") or container_id

            cross_texts: list[str] = []
            if img_own_id and img_own_id in cross_ref:
                cross_texts = cross_ref[img_own_id][:3]   # cap at 3 snippets
                logger.debug(
                    "  Anchor '%s' matched %d description(s)",
                    img_own_id, len(cross_ref[img_own_id]),
                )

            # ── Compose inline image marker ──────────────────────────────
            context_parts = list(filter(None, [surrounding] + cross_texts))
            marker = (
                f"[Image: {' | '.join(context_parts)}]"
                if context_parts
                else "[Image]"
            )
            text_parts.append(marker)

        full_text = "\n".join(text_parts).strip()
        if not full_text and not image_links:
            continue

        sections.append({
            "page_number": section_num,    # spine position (no real page numbers)
            "section_number": section_num,
            "text": full_text,
            "image_links": image_links,
            "source_file": epub_path.name,
            "source_path": str(epub_path),
            "format": "epub",
            "chunk_hash": hashlib.md5(
                f"{epub_path.name}:s{section_num}:{full_text[:64]}".encode()
            ).hexdigest(),
        })

    img_count = sum(len(s["image_links"]) for s in sections)
    logger.info("  Extracted %d sections, %d images", len(sections), img_count)
    return sections


# ---------------------------------------------------------------------------
# Format dispatcher
# ---------------------------------------------------------------------------

def extract_book(book_path: Path, images_dir: Path) -> list[dict]:
    """Route a book file to the correct extractor based on suffix."""
    suffix = book_path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(book_path, images_dir)
    if suffix == ".epub":
        return extract_epub(book_path, images_dir)
    logger.warning("Unsupported format, skipping: %s", book_path.name)
    return []


# ---------------------------------------------------------------------------
# LlamaIndex document creation
# ---------------------------------------------------------------------------

def sections_to_llama_documents(sections: list[dict]):
    """
    Convert section dicts into LlamaIndex Document objects.

    Metadata stored in Qdrant payload (all fields filterable at query time):
        source_file    – filename of the source book
        source_path    – absolute path to the source file
        page_number    – page (PDF) or spine position (EPUB)
        section_number – same as page_number (unified field for querying)
        format         – "pdf" or "epub"
        subject        – empty; set via CLI --subject flag
        chapter        – empty; can be populated by a future TOC pass
        image_links    – list[str] of absolute paths to extracted images
        chunk_hash     – content fingerprint for idempotency checks

    image_links is excluded from the LLM metadata prompt (paths are not
    useful as reasoning text) but IS stored in the Qdrant payload so that
    retrieval clients can load the corresponding images.
    """
    try:
        from llama_index.core import Document
    except ImportError as exc:
        raise ImportError("pip install llama-index") from exc

    documents = []
    for sec in sections:
        doc = Document(
            text=sec["text"],
            metadata={
                "source_file":    sec["source_file"],
                "source_path":    sec["source_path"],
                "page_number":    sec["page_number"],
                "section_number": sec["section_number"],
                "format":         sec["format"],
                "subject":        "",
                "chapter":        "",
                "image_links":    sec["image_links"],   # list[str]
                "chunk_hash":     sec["chunk_hash"],
            },
            excluded_llm_metadata_keys=[
                "source_path", "chunk_hash", "image_links",
            ],
            excluded_embed_metadata_keys=[
                "source_path", "chunk_hash", "image_links",
            ],
        )
        documents.append(doc)
    return documents


# ---------------------------------------------------------------------------
# Qdrant + LlamaIndex index construction
# ---------------------------------------------------------------------------

def build_index(documents, collection_name: str):
    """
    Chunk documents and upsert embeddings into Qdrant.

    • The embedding model runs locally (no API key required).
    • Re-running is safe: existing chunks are overwritten by LlamaIndex's
      default upsert behaviour.
    • image_links is stored as a Qdrant array payload — natively filterable,
      e.g. filter to chunks that have at least one image.
    """
    try:
        from llama_index.core import Settings, VectorStoreIndex
        from llama_index.core.node_parser import SentenceSplitter
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        from llama_index.vector_stores.qdrant import QdrantVectorStore
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
    except ImportError as exc:
        raise ImportError(
            "pip install llama-index llama-index-vector-stores-qdrant "
            "llama-index-embeddings-huggingface qdrant-client"
        ) from exc

    logger.info("Loading embedding model: %s", EMBED_MODEL_NAME)
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
    Settings.embed_model = embed_model
    Settings.chunk_size = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP
    Settings.llm = None   # ingestion is embedding-only; no LLM calls

    client = QdrantClient(url=QDRANT_URL)
    existing = {c.name for c in client.get_collections().collections}

    if collection_name not in existing:
        logger.info("Creating Qdrant collection: %s (dim=%d)", collection_name, EMBED_DIM)
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
    else:
        logger.info("Upserting into existing collection: %s", collection_name)

    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)

    logger.info("Indexing %d documents …", len(documents))
    VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store,
        transformations=[
            SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        ],
        show_progress=True,
    )
    logger.info("Indexing complete — collection '%s' is ready.", collection_name)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest medical PDFs and EPUBs into Qdrant via Docling + LlamaIndex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--books-dir",
        type=Path,
        default=Path("./books"),
        help="Directory containing .pdf and/or .epub files (default: ./books)",
    )
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=IMAGES_DIR,
        help=f"Directory to save extracted images (default: {IMAGES_DIR})",
    )
    parser.add_argument(
        "--collection",
        default="medical_rag",
        help="Qdrant collection name (default: medical_rag)",
    )
    parser.add_argument(
        "--subject",
        default="",
        help="Subject tag stored in metadata, e.g. 'anatomy' or 'osteopathy'",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extract and print a summary without writing to Qdrant",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    books_dir: Path = args.books_dir.resolve()
    images_dir: Path = args.images_dir.resolve()

    if not books_dir.exists():
        logger.error("Books directory not found: %s", books_dir)
        return

    book_files = sorted(
        p for p in books_dir.iterdir()
        if p.suffix.lower() in {".pdf", ".epub"}
    )
    if not book_files:
        logger.warning("No .pdf or .epub files found in %s", books_dir)
        return

    logger.info(
        "Found %d book(s): %s",
        len(book_files),
        ", ".join(f.name for f in book_files),
    )

    all_sections: list[dict] = []
    for book_path in book_files:
        sections = extract_book(book_path, images_dir)
        # Apply subject tag if provided
        if args.subject:
            for s in sections:
                s["subject"] = args.subject
        all_sections.extend(sections)

    total_images = sum(len(s["image_links"]) for s in all_sections)
    logger.info(
        "Total: %d sections across %d book(s), %d images extracted",
        len(all_sections), len(book_files), total_images,
    )

    if args.dry_run:
        summary = []
        for s in all_sections[:15]:
            summary.append({
                "source_file":  s["source_file"],
                "format":       s["format"],
                "page_number":  s["page_number"],
                "image_links":  s["image_links"],
                "text_preview": s["text"][:140].replace("\n", " "),
            })
        print(json.dumps(summary, indent=2))
        logger.info("Dry run complete — Qdrant ingestion skipped.")
        return

    documents = sections_to_llama_documents(all_sections)
    build_index(documents, collection_name=args.collection)


if __name__ == "__main__":
    main()
