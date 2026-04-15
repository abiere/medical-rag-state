#!/usr/bin/env python3
"""
book_ingest_queue.py — Sequential book ingestion queue for Medical RAG.

Architecture mirrors transcription_queue.py:
  Queue file:   /tmp/book_ingest_queue.json
  Current job:  /tmp/book_ingest_current.json
  Log:          /var/log/book_ingest_queue.log

Run as systemd service (book-ingest-queue.service).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ── paths & config ─────────────────────────────────────────────────────────────

BASE         = Path("/root/medical-rag")
QUEUE_FILE   = Path("/tmp/book_ingest_queue.json")
CURRENT_FILE = Path("/tmp/book_ingest_current.json")
BOOKS_DIR    = BASE / "books"
QUALITY_DIR  = BASE / "data" / "book_quality"
MARKERS_FILE = Path("/var/log/markers.json")

QDRANT_URL   = "http://localhost:6333"
OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"
PAUSE_FILE   = Path("/tmp/book_ingest_pause")

VECTOR_SIZE       = 1024
BOOK_EXTS         = {".pdf", ".epub"}
MIN_QUALITY_SCORE = 3.5

# Section → Qdrant collection mapping (mirrors web/app.py SECTION_MAP)
SECTION_COLLECTION_MAP = {
    "medical_literature": "medical_library",
    "nrt_qat":            "nrt_qat_curriculum",
    "device":             "device_documentation",
}

# ── logging ────────────────────────────────────────────────────────────────────

LOG_FILE = Path("/var/log/book_ingest_queue.log")
LOG_FILE.touch(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE)),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

SEP = "─" * 60


# ── queue helpers ──────────────────────────────────────────────────────────────

def _read_queue() -> list[dict]:
    try:
        if QUEUE_FILE.exists():
            data = json.loads(QUEUE_FILE.read_text())
            return data if isinstance(data, list) else []
    except Exception:
        pass
    return []


def _write_queue(q: list[dict]) -> None:
    QUEUE_FILE.write_text(json.dumps(q, indent=2))


def _set_current(item: dict | None) -> None:
    if item is None:
        CURRENT_FILE.unlink(missing_ok=True)
    else:
        CURRENT_FILE.write_text(json.dumps(item, indent=2))


# ── notify helper ──────────────────────────────────────────────────────────────

def _notify(event: str, message: str) -> None:
    try:
        markers: list[dict] = []
        if MARKERS_FILE.exists():
            markers = json.loads(MARKERS_FILE.read_text())
        markers.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event":     event,
            "message":   message,
        })
        MARKERS_FILE.write_text(json.dumps(markers[-50:], indent=2))
    except Exception as e:
        logger.debug("notify failed: %s", e)


# ── Qdrant helpers ─────────────────────────────────────────────────────────────

def _qdrant_request(method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        f"{QDRANT_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _ensure_collection(name: str) -> None:
    """Create Qdrant collection if it doesn't exist."""
    try:
        _qdrant_request("GET", f"/collections/{name}")
        logger.debug("Collection %s exists", name)
        return
    except Exception:
        pass

    logger.info("Creating Qdrant collection: %s", name)
    _qdrant_request("PUT", f"/collections/{name}", {
        "vectors": {
            "size":     VECTOR_SIZE,
            "distance": "Cosine",
        },
        "hnsw_config": {"m": 16, "ef_construct": 100},
        "optimizers_config": {
            "indexing_threshold": 20000,
            "memmap_threshold":   50000,
        },
    })


def _source_file_exists(collection: str, source_file: str) -> bool:
    """Check if any vector from this source_file already exists."""
    try:
        body = {
            "filter": {
                "must": [{"key": "source_file", "match": {"value": source_file}}]
            },
            "limit": 1,
            "with_payload": False,
            "with_vector": False,
        }
        r = _qdrant_request("POST", f"/collections/{collection}/points/scroll", body)
        return len(r.get("result", {}).get("points", [])) > 0
    except Exception:
        return False


def _embed(texts: list[str]) -> list[list[float]]:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    return model.encode(texts, show_progress_bar=False, batch_size=16).tolist()


def _upsert_chunks(collection: str, chunks: list[dict]) -> int:
    """Embed and upsert chunks into Qdrant. Returns count of upserted vectors."""
    if not chunks:
        return 0

    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct

    client = QdrantClient(host="localhost", port=6333, timeout=60)
    _ensure_collection(collection)

    # Deduplicate by chunk_hash
    seen_hashes: set[str] = set()
    unique_chunks = []
    for c in chunks:
        h = c.get("chunk_hash", "")
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique_chunks.append(c)

    texts = [c["text"] for c in unique_chunks]
    logger.info("Embedding %d unique chunks...", len(unique_chunks))
    vectors = _embed(texts)

    # Build points
    points = []
    for i, (chunk, vec) in enumerate(zip(unique_chunks, vectors)):
        # Build a deterministic integer ID from hash
        pid = int(hashlib.sha256(chunk["chunk_hash"].encode()).hexdigest()[:15], 16)
        payload = {k: v for k, v in chunk.items() if k != "text"}
        payload["text"] = chunk["text"]
        points.append(PointStruct(id=pid, vector=vec, payload=payload))

    # Upsert in batches of 100
    BATCH = 100
    for i in range(0, len(points), BATCH):
        client.upsert(collection_name=collection, points=points[i:i+BATCH])

    logger.info("Upserted %d vectors → %s", len(points), collection)
    return len(points)


# ── startup scan ───────────────────────────────────────────────────────────────

def startup_scan() -> int:
    """Scan books/ subdirs and enqueue any un-ingested files. Returns count added."""
    added = 0
    queue = _read_queue()
    queued_paths = {item["filepath"] for item in queue}

    for subdir, collection in SECTION_COLLECTION_MAP.items():
        d = BOOKS_DIR / subdir
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.suffix.lower() not in BOOK_EXTS:
                continue
            if str(f) in queued_paths:
                continue
            audit_path = QUALITY_DIR / f"{f.stem}_audit.json"
            if audit_path.exists():
                try:
                    audit = json.loads(audit_path.read_text())
                    if audit.get("status") == "approved":
                        logger.debug("Skip (already ingested): %s", f.name)
                        continue
                except Exception:
                    pass
            queue.append({
                "filename":        f.name,
                "filepath":        str(f),
                "collection":      collection,
                "source_category": subdir,
                "format":          f.suffix.lstrip(".").lower(),
                "requested":       datetime.now(timezone.utc).isoformat(),
            })
            added += 1
            logger.info("Startup scan: enqueued %s → %s", f.name, collection)

    if added:
        _write_queue(queue)
    return added


# ── process one book ───────────────────────────────────────────────────────────

def process_book(item: dict) -> bool:
    """
    Full pipeline for one book: parse → audit → ingest.
    Returns True on success.
    """
    filename   = item["filename"]
    filepath   = Path(item["filepath"])
    collection = item.get("collection") or SECTION_COLLECTION_MAP.get(
        item.get("source_category", ""), "medical_library"
    )
    category   = item["source_category"]
    fmt        = item.get("format", filepath.suffix.lstrip(".").lower())

    logger.info(SEP)
    logger.info("START  %s → %s", filename, collection)
    t0 = time.monotonic()

    if not filepath.exists():
        logger.error("File not found: %s", filepath)
        return False

    # 1. Parse
    try:
        sys.path.insert(0, str(BASE / "scripts"))
        if fmt == "pdf":
            from parse_pdf import parse_pdf
            chunks = parse_pdf(filepath, collection, category)
        elif fmt == "epub":
            from parse_epub import parse_epub
            chunks = parse_epub(filepath, collection, category)
        else:
            logger.error("Unsupported format: %s", fmt)
            return False
    except Exception as e:
        logger.error("Parse failed for %s: %s", filename, e)
        return False

    if not chunks:
        logger.error("No chunks produced from %s", filename)
        return False

    # 2. Structural audit (fast, always)
    from audit_book import structural_audit, llm_audit, auto_classify, check_remediation, audit_book
    s = structural_audit(chunks)
    logger.info("Structural: avg_words=%.0f short=%d long=%d",
                s["avg_chunk_words"], s["short_chunks"], s["long_chunks"])

    # 3. LLM audit
    llm = llm_audit(chunks)
    quality_score = llm.get("quality_score")
    logger.info("LLM quality_score=%s flagged=%d",
                quality_score, llm.get("flagged_chunks", 0))

    # 4. Remediation attempt (once)
    remediation_applied = False
    if quality_score is not None and quality_score < MIN_QUALITY_SCORE:
        logger.warning("Quality score %.2f < %.1f — retrying with 600-word target",
                       quality_score, MIN_QUALITY_SCORE)
        try:
            mod_name = "parse_pdf" if fmt == "pdf" else "parse_epub"
            mod = sys.modules.get(mod_name)
            if mod:
                orig = mod.TARGET_WORDS
                mod.TARGET_WORDS = 600
                chunks2 = (mod.parse_pdf if fmt == "pdf" else mod.parse_epub)(
                    filepath, collection, category
                )
                mod.TARGET_WORDS = orig
                llm2 = llm_audit(chunks2)
                if (llm2.get("quality_score") or 0) > (quality_score or 0):
                    chunks = chunks2
                    llm = llm2
                    quality_score = llm.get("quality_score")
                    remediation_applied = True
                    logger.info("Remediation improved score to %.2f", quality_score or 0)
        except Exception as e:
            logger.warning("Remediation failed: %s", e)

    # 5. Auto-classify
    classification = auto_classify(chunks)

    # 6. AI usability tagging
    from audit_book import tag_chunks_with_ollama, build_usability_profile, prescreeen_images
    logger.info("Tagging %d chunks with usability tags...", len(chunks))
    tag_chunks_with_ollama(chunks)
    usability_profile = build_usability_profile(chunks)
    prescreeen_images(chunks, filename)

    # 7. Build and save audit report
    from audit_book import check_remediation
    remediation_check = check_remediation(s, llm)
    qs = quality_score or 0
    status = "approved" if qs >= MIN_QUALITY_SCORE else "low_quality"
    report = {
        "book":               filename,
        "collection":         collection,
        "audited_at":         datetime.now(timezone.utc).isoformat(),
        "total_chunks":       len(chunks),
        "structural":         s,
        "llm_audit":          llm,
        "auto_classification": classification,
        "usability_profile":  usability_profile,
        "remediation":        remediation_check,
        "remediation_applied": remediation_applied,
        "status":             status,
    }
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    (QUALITY_DIR / f"{filepath.stem}_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )

    # 8. Ingest to Qdrant (even if low quality — but log warning)
    if qs < MIN_QUALITY_SCORE:
        logger.warning("Ingesting anyway with low quality score %.2f", qs)

    try:
        n_upserted = _upsert_chunks(collection, chunks)
    except Exception as e:
        logger.error("Qdrant upsert failed: %s", e)
        return False

    elapsed = time.monotonic() - t0
    logger.info("DONE   %s  (%ds)  %d chunks  score=%.2f",
                filename, int(elapsed), n_upserted, qs)
    _notify("book_ingested",
            f"{filename} → {collection}: {n_upserted} chunks, score {qs:.2f}")
    return True


# ── main loop ──────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info(SEP)
    logger.info("Book ingest queue manager started")

    added = startup_scan()
    if added:
        logger.info("Startup scan: %d file(s) added to queue", added)

    while True:
        # Pause support: check flag before starting next book
        if PAUSE_FILE.exists():
            logger.info("Queue paused (pause flag set) — waiting 30s")
            time.sleep(30)
            continue

        queue = _read_queue()
        if not queue:
            logger.info("Queue empty — exiting")
            _set_current(None)
            break

        item = queue[0]
        remaining = queue[1:]
        _write_queue(remaining)

        item["started"] = datetime.now(timezone.utc).isoformat()
        _set_current(item)

        try:
            process_book(item)
        except Exception as e:
            logger.error("Unhandled error processing %s: %s", item.get("filename"), e)
        finally:
            _set_current(None)

    logger.info(SEP)


if __name__ == "__main__":
    main()
