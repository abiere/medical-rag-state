#!/usr/bin/env python3
"""
book_ingest_queue.py — Sequential book ingestion queue with state-machine checkpointing.

Architecture:
  Queue file:    /tmp/book_ingest_queue.json
  Current job:   /tmp/book_ingest_current.json
  Cache dir:     /root/medical-rag/data/ingest_cache/{book_hash}/
  Log:           /var/log/book_ingest_queue.log

State machine per book:
  parse → audit → embed → qdrant → done
  image_screen is a background-only phase, never blocks the pipeline.

On restart: reads state.json, resumes from first non-done phase.
Run as systemd service (book-ingest-queue.service).
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import threading
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ── paths & config ─────────────────────────────────────────────────────────────

BASE          = Path("/root/medical-rag")
QUEUE_FILE    = Path("/tmp/book_ingest_queue.json")
CURRENT_FILE  = Path("/tmp/book_ingest_current.json")
BOOKS_DIR     = BASE / "books"
QUALITY_DIR   = BASE / "data" / "book_quality"
CACHE_DIR     = BASE / "data" / "ingest_cache"
MARKERS_FILE  = Path("/var/log/markers.json")

QDRANT_URL    = "http://localhost:6333"
PAUSE_FILE    = Path("/tmp/book_ingest_pause")

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

# ── state machine helpers ──────────────────────────────────────────────────────

def _book_hash(filepath: Path) -> str:
    """Deterministic 16-char hash from filepath (fast, no file read needed)."""
    return hashlib.sha256(str(filepath).encode()).hexdigest()[:16]


def _cache_dir(book_hash: str) -> Path:
    d = CACHE_DIR / book_hash
    d.mkdir(parents=True, exist_ok=True)
    return d


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _blank_state(filename: str, filepath: Path, collection: str, category: str) -> dict:
    """Build a fresh state.json structure for a book."""
    return {
        "filename":         filename,
        "book_hash":        _book_hash(filepath),
        "filepath":         str(filepath),
        "collection":       collection,
        "library_category": category,
        "started_at":       _now_iso(),
        "updated_at":       _now_iso(),
        "completed_at":     None,
        "phases": {
            "parse": {
                "status":          "pending",
                "started_at":      None,
                "completed_at":    None,
                "pages_total":     None,
                "pages_done":      0,
                "chunks_extracted": None,
                "images_extracted": None,
                "parse_method":    None,
                "output_file":     "phase1_chunks.json",
                "error":           None,
                "warnings":        [],
            },
            "audit": {
                "status":                   "pending",
                "started_at":               None,
                "completed_at":             None,
                "chunks_total":             None,
                "chunks_tagged":            0,
                "chunks_skipped":           0,
                "ollama_available":         None,
                "consecutive_failures_hit": False,
                "output_file":              "phase2_audited.json",
            },
            "embed": {
                "status":              "pending",
                "started_at":          None,
                "completed_at":        None,
                "chunks_total":        None,
                "chunks_done":         0,
                "vectors_per_minute":  None,
                "eta_minutes":         None,
                "last_progress_at":    None,
                "output_file":         "phase3_vectors.npy",
            },
            "qdrant": {
                "status":          "pending",
                "started_at":      None,
                "completed_at":    None,
                "chunks_inserted": 0,
                "collection":      collection,
            },
        },
        "image_extraction_enabled": True,
    }


def _read_state(book_hash: str) -> dict | None:
    p = _cache_dir(book_hash) / "state.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _write_state(state: dict) -> None:
    state["updated_at"] = _now_iso()
    bh = state["book_hash"]
    p  = _cache_dir(bh) / "state.json"
    try:
        p.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    except Exception as e:
        logger.warning("Could not write state.json: %s", e)
    # Also update CURRENT_FILE for backward-compat with existing UI
    _sync_current_file(state)


def _sync_current_file(state: dict) -> None:
    """Mirror key fields into /tmp/book_ingest_current.json for existing API."""
    try:
        # Find active phase
        active_phase = None
        active_data  = {}
        for phase_name, phase_data in state.get("phases", {}).items():
            if phase_data.get("status") == "running":
                active_phase = phase_name
                active_data  = phase_data
                break

        current = {
            "filename":  state.get("filename", ""),
            "filepath":  state.get("filepath", ""),
            "started":   state.get("started_at", ""),
            "book_hash": state.get("book_hash", ""),
        }

        if active_phase == "parse":
            pages_done  = active_data.get("pages_done", 0)
            pages_total = active_data.get("pages_total") or 0
            pct = int(pages_done / pages_total * 100) if pages_total else 0
            current["progress"] = {
                "phase":         "parsing",
                "current_page":  pages_done,
                "total_pages":   pages_total,
                "percent":       pct,
                "chunks_so_far": 0,
            }
        elif active_phase == "audit":
            tagged  = active_data.get("chunks_tagged", 0) + active_data.get("chunks_skipped", 0)
            total   = active_data.get("chunks_total") or 0
            pct     = int(tagged / total * 100) if total else 0
            current["progress"] = {
                "phase":         "auditing",
                "current_page":  tagged,
                "total_pages":   total,
                "percent":       pct,
                "chunks_so_far": tagged,
            }
        elif active_phase == "embed":
            done  = active_data.get("chunks_done", 0)
            total = active_data.get("chunks_total") or 0
            pct   = int(done / total * 100) if total else 0
            current["progress"] = {
                "phase":         "embedding",
                "current_page":  done,
                "total_pages":   total,
                "percent":       pct,
                "chunks_so_far": done,
            }
        elif active_phase == "qdrant":
            current["progress"] = {
                "phase": "qdrant", "current_page": 0, "total_pages": 0,
                "percent": 95, "chunks_so_far": 0,
            }

        CURRENT_FILE.write_text(json.dumps(current, indent=2))
    except Exception:
        pass


def _set_phase_running(state: dict, phase: str) -> None:
    state["phases"][phase]["status"]     = "running"
    state["phases"][phase]["started_at"] = _now_iso()
    _write_state(state)


def _set_phase_done(state: dict, phase: str, **extra) -> None:
    state["phases"][phase]["status"]       = "done"
    state["phases"][phase]["completed_at"] = _now_iso()
    for k, v in extra.items():
        state["phases"][phase][k] = v
    _write_state(state)


def _set_phase_failed(state: dict, phase: str, error: str) -> None:
    state["phases"][phase]["status"] = "failed"
    state["phases"][phase]["error"]  = error
    _write_state(state)


def _find_resume_phase(state: dict) -> str | None:
    """Return name of first phase that is not done/queued_background, or None if all done."""
    for phase in ("parse", "audit", "embed", "qdrant"):
        s = state["phases"][phase]["status"]
        if s not in ("done",):
            return phase
    return None


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
            "timestamp": _now_iso(),
            "event":     event,
            "message":   message,
        })
        MARKERS_FILE.write_text(json.dumps(markers[-50:], indent=2))
    except Exception as e:
        logger.debug("notify failed: %s", e)


# ── Qdrant helpers ─────────────────────────────────────────────────────────────

def _qdrant_request(method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(
        f"{QDRANT_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _ensure_collection(name: str) -> None:
    try:
        _qdrant_request("GET", f"/collections/{name}")
        return
    except Exception:
        pass
    logger.info("Creating Qdrant collection: %s", name)
    _qdrant_request("PUT", f"/collections/{name}", {
        "vectors": {"size": VECTOR_SIZE, "distance": "Cosine"},
        "hnsw_config": {"m": 16, "ef_construct": 100},
        "optimizers_config": {
            "indexing_threshold": 20000,
            "memmap_threshold":   50000,
        },
    })


# ── classification linker ──────────────────────────────────────────────────────

_CLASSIFICATIONS_FILE = BASE / "config" / "book_classifications.json"


def _link_classification(filename: str, filepath: str) -> str | None:
    try:
        config = json.loads(_CLASSIFICATIONS_FILE.read_text())
    except Exception as e:
        logger.warning("Could not read book_classifications.json: %s", e)
        return None

    fname_lower  = filename.lower()
    matched_key: str | None = None
    for key, val in config.get("classifications", {}).items():
        patterns = val.get("filename_patterns", [])
        if any(p.lower() in fname_lower for p in patterns):
            matched_key = key
            break

    ts = _now_iso()
    if matched_key:
        config["classifications"][matched_key]["server_path"]     = filepath
        config["classifications"][matched_key]["server_filename"] = filename
        config["classifications"][matched_key]["ingested"]        = True
        config["classifications"][matched_key]["ingested_at"]     = ts
        logger.info("Classification linked: %s → %s", filename, matched_key)
    else:
        auto_key = f"unclassified_{Path(filename).stem[:30]}"
        logger.warning("No classification for '%s' — adding as %s", filename, auto_key)
        config["classifications"][auto_key] = {
            "k": 2, "a": 2, "i": 2,
            "role": "unclassified",
            "server_path":     filepath,
            "server_filename": filename,
            "ingested":        True,
            "ingested_at":     ts,
            "filename_patterns": [filename],
            "notes": "Auto-added — needs manual K/A/I classification",
        }
        matched_key = auto_key

    try:
        _CLASSIFICATIONS_FILE.write_text(json.dumps(config, indent=2))
    except Exception as e:
        logger.warning("Could not write book_classifications.json: %s", e)

    return matched_key


def _check_protocols_for_review(book_key: str) -> None:
    try:
        from protocol_metadata import check_protocols_for_review
        flagged = check_protocols_for_review(book_key)
        if flagged:
            logger.info("Earmarked %d protocol(s) for review: %s", len(flagged), flagged)
    except Exception as e:
        logger.warning("Protocol earmark check failed (non-fatal): %s", e)


# ── Phase 1: Parse ─────────────────────────────────────────────────────────────

def _phase_parse(state: dict, filepath: Path, fmt: str, collection: str, category: str) -> bool:
    """Parse PDF/EPUB → chunks. Saves phase1_chunks.json. Returns True on success."""
    bh        = state["book_hash"]
    cache     = _cache_dir(bh)
    out_file  = cache / "phase1_chunks.json"
    phase     = state["phases"]["parse"]

    # Increment retry counter before starting (for failed-parse tracking in startup_scan)
    state["parse_retry_count"] = state.get("parse_retry_count", 0) + 1
    _write_state(state)

    _set_phase_running(state, "parse")
    logger.info("Phase 1 — Parsing %s (format=%s)", filepath.name, fmt)

    def _progress_fn(phase_name: str, current: int, total: int, chunks_so_far: int) -> None:
        """Called by parse_pdf every 10 pages."""
        if current % 10 == 0 or current == total:
            state["phases"]["parse"]["pages_done"]  = current
            state["phases"]["parse"]["pages_total"] = total
            _write_state(state)

    try:
        sys.path.insert(0, str(BASE / "scripts"))
        if fmt == "pdf":
            from parse_pdf import parse_pdf
            chunks = parse_pdf(filepath, collection, category, progress_fn=_progress_fn)
        elif fmt == "epub":
            from parse_epub import parse_epub
            chunks = parse_epub(filepath, collection, category)
        else:
            _set_phase_failed(state, "parse", f"Unsupported format: {fmt}")
            return False
    except Exception as e:
        _set_phase_failed(state, "parse", str(e))
        logger.error("Parse failed: %s", e)
        return False

    if not chunks:
        _set_phase_failed(state, "parse", "No chunks produced")
        return False

    # Count images across all chunks
    images_total = sum(len(c.get("image_links", [])) for c in chunks)

    # Derive dominant OCR engine from chunk metadata
    from collections import Counter
    engine_counts    = Counter(c.get("ocr_engine", "native") for c in chunks)
    dominant_engine  = engine_counts.most_common(1)[0][0] if engine_counts else "native"

    # Save output
    out_file.write_text(json.dumps(chunks, ensure_ascii=False))

    _set_phase_done(state, "parse",
                    chunks_extracted=len(chunks),
                    images_extracted=images_total,
                    ocr_engine=dominant_engine,
                    pages_total=state["phases"]["parse"].get("pages_total") or len(chunks),
                    pages_done=state["phases"]["parse"].get("pages_total") or len(chunks))

    state["parse_retry_count"] = 0  # reset on success
    _write_state(state)
    logger.info("Parse done: %d chunks, %d images", len(chunks), images_total)
    return True


# ── Phase 2: Audit ─────────────────────────────────────────────────────────────

def _phase_audit(state: dict) -> bool:
    """Audit + LLM-tag chunks. NO image screening. Saves phase2_audited.json."""
    bh       = state["book_hash"]
    cache    = _cache_dir(bh)
    in_file  = cache / "phase1_chunks.json"
    out_file = cache / "phase2_audited.json"

    if not in_file.exists():
        _set_phase_failed(state, "audit", "phase1_chunks.json not found")
        return False

    chunks = json.loads(in_file.read_text())
    _set_phase_running(state, "audit")
    state["phases"]["audit"]["chunks_total"] = len(chunks)
    _write_state(state)

    logger.info("Phase 2 — Auditing %d chunks (LLM + tagging)", len(chunks))

    from audit_book import structural_audit, llm_audit, auto_classify, tag_chunks_with_ollama, build_usability_profile, check_remediation

    # Structural audit (fast, no Ollama)
    s = structural_audit(chunks)
    logger.info("Structural: avg_words=%.0f short=%d long=%d",
                s["avg_chunk_words"], s["short_chunks"], s["long_chunks"])

    # LLM audit (sample, Ollama — bail on failure)
    llm = llm_audit(chunks)
    quality_score = llm.get("quality_score")
    logger.info("LLM quality_score=%s flagged=%d",
                quality_score, llm.get("flagged_chunks", 0))

    # Auto-classify
    classification = auto_classify(chunks)

    # AI usability tagging — Claude API primary, Ollama fallback
    try:
        from claude_audit import is_enabled as _claude_enabled, audit_chunks_parallel as _claude_tag
    except ImportError:
        _claude_enabled = lambda: False  # noqa: E731

    if _claude_enabled():
        logger.info("Phase 2 — Using Claude API for tagging (%d chunks)", len(chunks))
        chunks = _claude_tag(chunks)
    else:
        tag_chunks_with_ollama(chunks)
    usability_profile = build_usability_profile(chunks)

    # Update audit progress in state
    tagged  = sum(1 for c in chunks
                  if c.get("usability_tags") or c.get("audit_status") == "tagged_claude")
    skipped = sum(1 for c in chunks
                  if (c.get("audit_status") or "").startswith("skipped"))
    state["phases"]["audit"]["chunks_tagged"]  = tagged
    state["phases"]["audit"]["chunks_skipped"] = skipped
    state["phases"]["audit"]["ollama_available"] = (tagged > 0)
    state["phases"]["audit"]["consecutive_failures_hit"] = (skipped > 0)

    # Remediation attempt for low quality
    qs = quality_score or 0
    if quality_score is not None and quality_score < MIN_QUALITY_SCORE:
        logger.warning("Quality score %.2f < %.1f — trying remediation", quality_score, MIN_QUALITY_SCORE)
        try:
            filepath = Path(state["filepath"])
            fmt      = filepath.suffix.lstrip(".").lower()
            mod_name = "parse_pdf" if fmt == "pdf" else "parse_epub"
            mod      = sys.modules.get(mod_name)
            if mod:
                orig = mod.TARGET_WORDS
                mod.TARGET_WORDS = 600
                chunks2 = (mod.parse_pdf if fmt == "pdf" else mod.parse_epub)(
                    filepath, state["collection"], state["library_category"]
                )
                mod.TARGET_WORDS = orig
                llm2 = llm_audit(chunks2)
                if (llm2.get("quality_score") or 0) > qs:
                    chunks = chunks2
                    llm    = llm2
                    qs     = llm.get("quality_score") or 0
                    tag_chunks_with_ollama(chunks)
                    usability_profile = build_usability_profile(chunks)
                    logger.info("Remediation improved score to %.2f", qs)
        except Exception as e:
            logger.warning("Remediation failed: %s", e)

    # Save audit report
    status  = "approved" if qs >= MIN_QUALITY_SCORE else "low_quality"
    report  = {
        "book":                filename_from_state(state),
        "collection":          state["collection"],
        "audited_at":          _now_iso(),
        "total_chunks":        len(chunks),
        "structural":          s,
        "llm_audit":           llm,
        "auto_classification": classification,
        "usability_profile":   usability_profile,
        "remediation":         check_remediation(s, llm),
        "status":              status,
    }
    QUALITY_DIR.mkdir(parents=True, exist_ok=True)
    stem = Path(filename_from_state(state)).stem
    (QUALITY_DIR / f"{stem}_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )

    # Save audited chunks
    out_file.write_text(json.dumps(chunks, ensure_ascii=False))
    _set_phase_done(state, "audit",
                    chunks_total=len(chunks),
                    chunks_tagged=tagged,
                    chunks_skipped=skipped)
    logger.info("Audit done: %d tagged, %d skipped, quality=%.2f", tagged, skipped, qs)
    return True


def filename_from_state(state: dict) -> str:
    return state.get("filename", Path(state.get("filepath", "unknown")).name)


# ── Phase 3: Embed ─────────────────────────────────────────────────────────────

def _phase_embed(state: dict) -> bool:
    """Embed chunks with BAAI/bge-large. Saves phase3_vectors.npy. Returns True."""
    bh       = state["book_hash"]
    cache    = _cache_dir(bh)
    in_file  = cache / "phase2_audited.json"
    out_file = cache / "phase3_vectors.npy"

    if not in_file.exists():
        _set_phase_failed(state, "embed", "phase2_audited.json not found")
        return False

    chunks = json.loads(in_file.read_text())
    _set_phase_running(state, "embed")
    state["phases"]["embed"]["chunks_total"] = len(chunks)
    _write_state(state)

    logger.info("Phase 3 — Embedding %d chunks with BAAI/bge-large-en-v1.5", len(chunks))

    # Load model
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-large-en-v1.5")

    # Embed in batches of 16, updating state every 50 chunks
    import numpy as np

    texts      = [c["text"] for c in chunks]
    all_vecs   = []
    batch_size = 16
    t_start    = time.monotonic()

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        vecs  = model.encode(batch, show_progress_bar=False).tolist()
        all_vecs.extend(vecs)

        done = len(all_vecs)
        # Update state every 50 chunks
        if done % 50 < batch_size or done == len(texts):
            elapsed = time.monotonic() - t_start
            vpm     = round(done / (elapsed / 60), 1) if elapsed > 0 else None
            eta     = round((len(texts) - done) / (done / elapsed), 1) / 60 if elapsed > 0 and done > 0 else None
            state["phases"]["embed"]["chunks_done"]       = done
            state["phases"]["embed"]["vectors_per_minute"] = vpm
            state["phases"]["embed"]["eta_minutes"]        = eta
            state["phases"]["embed"]["last_progress_at"]   = _now_iso()
            _write_state(state)

    # Save vectors
    np.save(str(out_file), np.array(all_vecs, dtype=np.float32))

    elapsed = time.monotonic() - t_start
    logger.info("Embed done: %d vectors in %.0fs", len(all_vecs), elapsed)
    _set_phase_done(state, "embed",
                    chunks_total=len(chunks),
                    chunks_done=len(all_vecs))
    return True


# ── Phase 4: Qdrant ────────────────────────────────────────────────────────────

def _phase_qdrant(state: dict) -> bool:
    """Load vectors + chunks, upsert to Qdrant. Writes phase4_done.marker."""
    bh          = state["book_hash"]
    cache       = _cache_dir(bh)
    chunks_file = cache / "phase2_audited.json"
    vecs_file   = cache / "phase3_vectors.npy"
    done_marker = cache / "phase4_done.marker"

    if not chunks_file.exists():
        _set_phase_failed(state, "qdrant", "phase2_audited.json not found")
        return False
    if not vecs_file.exists():
        _set_phase_failed(state, "qdrant", "phase3_vectors.npy not found")
        return False

    chunks     = json.loads(chunks_file.read_text())
    collection = state["collection"]

    _set_phase_running(state, "qdrant")
    logger.info("Phase 4 — Upserting %d chunks → %s", len(chunks), collection)

    import numpy as np
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct

    vectors = np.load(str(vecs_file)).tolist()

    if len(vectors) != len(chunks):
        _set_phase_failed(state, "qdrant",
                          f"Vector count {len(vectors)} != chunk count {len(chunks)}")
        return False

    client = QdrantClient(host="localhost", port=6333, timeout=60)
    _ensure_collection(collection)

    # Deduplicate by chunk_hash
    seen_hashes: set[str] = set()
    points = []
    for chunk, vec in zip(chunks, vectors):
        h = chunk.get("chunk_hash", "")
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        pid     = int(hashlib.sha256(h.encode()).hexdigest()[:15], 16)
        payload = {k: v for k, v in chunk.items()}
        points.append(PointStruct(id=pid, vector=vec, payload=payload))

    # Upsert in batches of 100
    BATCH = 100
    n_upserted = 0
    for i in range(0, len(points), BATCH):
        client.upsert(collection_name=collection, points=points[i : i + BATCH])
        n_upserted += len(points[i : i + BATCH])
        state["phases"]["qdrant"]["chunks_inserted"] = n_upserted
        _write_state(state)

    # Write done marker
    done_marker.write_text(json.dumps({
        "completed_at":  _now_iso(),
        "chunks_inserted": n_upserted,
        "collection":    collection,
    }))

    logger.info("Qdrant done: %d vectors upserted to %s", n_upserted, collection)
    _set_phase_done(state, "qdrant", chunks_inserted=n_upserted)

    # Start image extraction in background thread (non-blocking)
    book_filepath = state.get("filepath", "")
    if book_filepath:
        book_path = Path(book_filepath)
        suffix = book_path.suffix.lower()
        import threading
        from image_extractor import extract_figures_from_pdf, extract_images_from_epub
        from image_extractor import IMAGES_OUT as _IMAGES_OUT

        def _run_extraction():
            try:
                if suffix == ".pdf":
                    extract_figures_from_pdf(book_path, bh, _IMAGES_OUT)
                elif suffix in (".epub",):
                    extract_images_from_epub(book_path, bh, _IMAGES_OUT)
                logger.info("Image extraction complete for %s", book_path.name)
            except Exception as exc:
                logger.warning("Image extraction failed (non-fatal): %s", exc)

        threading.Thread(target=_run_extraction, daemon=True).start()

    return True


# ── startup scan ───────────────────────────────────────────────────────────────

def startup_scan() -> int:
    """Scan books/ subdirs, enqueue any un-ingested files. Returns count added."""
    added   = 0
    queue   = _read_queue()
    queued_paths = {item["filepath"] for item in queue}

    for subdir, collection in SECTION_COLLECTION_MAP.items():
        d = BOOKS_DIR / subdir
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if f.suffix.lower() not in BOOK_EXTS:
                continue
            if str(f) in queued_paths:
                continue

            # Check state machine — skip fully completed books
            bh    = _book_hash(f)
            state = _read_state(bh)
            if state and state.get("completed_at"):
                logger.debug("Skip (completed): %s", f.name)
                continue

            if state:
                # Skip permanently failed books (exhausted retries)
                if state.get("status") == "permanently_failed":
                    logger.warning("Skip (permanently failed — manual intervention required): %s", f.name)
                    continue

                # Track parse failures — permanently fail after MAX_RETRIES
                parse_phase = state.get("phases", {}).get("parse", {})
                if parse_phase.get("status") == "failed":
                    retry_count = state.get("parse_retry_count", 0)
                    MAX_RETRIES = 3
                    if retry_count >= MAX_RETRIES:
                        state["status"] = "permanently_failed"
                        state["permanently_failed_at"] = datetime.now(timezone.utc).isoformat()
                        state["permanently_failed_reason"] = (
                            f"Parse failed {retry_count} times — manual intervention required"
                        )
                        _write_state(state)
                        logger.error(
                            "PERMANENTLY FAILED after %d retries: %s — not re-queuing",
                            retry_count, f.name,
                        )
                        continue

            # Also check legacy audit file (backward compat)
            audit_path = QUALITY_DIR / f"{f.stem}_audit.json"
            if audit_path.exists() and state is None:
                try:
                    audit = json.loads(audit_path.read_text())
                    if audit.get("status") == "approved":
                        logger.debug("Skip (legacy audit approved): %s", f.name)
                        continue
                except Exception:
                    pass

            queue.append({
                "filename":        f.name,
                "filepath":        str(f),
                "collection":      collection,
                "source_category": subdir,
                "format":          f.suffix.lstrip(".").lower(),
                "requested":       _now_iso(),
            })
            added += 1
            logger.info("Startup scan: enqueued %s → %s", f.name, collection)

    if added:
        _write_queue(queue)
    return added


# ── process one book ───────────────────────────────────────────────────────────

def process_book(item: dict) -> bool:
    """
    Full pipeline for one book, with state-machine checkpointing.
    Resumes from first incomplete phase.
    Returns True on success.
    """
    filename   = item["filename"]
    filepath   = Path(item["filepath"])
    collection = item.get("collection") or SECTION_COLLECTION_MAP.get(
        item.get("source_category", ""), "medical_library"
    )
    category   = item.get("source_category", "medical_literature")
    fmt        = item.get("format", filepath.suffix.lstrip(".").lower())

    logger.info(SEP)
    logger.info("START  %s → %s", filename, collection)
    t0 = time.monotonic()

    # Load or create state
    bh    = _book_hash(filepath)
    state = _read_state(bh)
    if state is None:
        state = _blank_state(filename, filepath, collection, category)
        state["image_extraction_enabled"] = item.get("image_extraction_enabled", True)
        _write_state(state)
        logger.info("Created new state for %s (hash=%s)", filename, bh)
    else:
        resume_phase = _find_resume_phase(state)
        if resume_phase:
            logger.info("Resuming from phase '%s' (cache found)", resume_phase)
        else:
            logger.info("All phases already done for %s — skipping", filename)
            state["completed_at"] = _now_iso()
            _write_state(state)
            return True

    # Heartbeat: touch CURRENT_FILE every 5 min
    _hb_stop = threading.Event()
    def _heartbeat() -> None:
        while not _hb_stop.wait(timeout=300):
            try:
                CURRENT_FILE.touch()
            except Exception:
                pass
    _hb_thread = threading.Thread(target=_heartbeat, daemon=True)
    _hb_thread.start()

    try:
        resume_phase = _find_resume_phase(state)
        if not resume_phase:
            logger.info("All phases done — nothing to do")
            state["completed_at"] = _now_iso()
            _write_state(state)
            return True

        # ── Phase 1: Parse ─────────────────────────────────────────────────
        if resume_phase == "parse":
            if not _phase_parse(state, filepath, fmt, collection, category):
                return False
            resume_phase = "audit"

        # ── Phase 2: Audit ─────────────────────────────────────────────────
        if resume_phase == "audit":
            if not _phase_audit(state):
                return False
            resume_phase = "embed"

        # ── Phase 3: Embed ─────────────────────────────────────────────────
        if resume_phase == "embed":
            if not _phase_embed(state):
                return False
            resume_phase = "qdrant"

        # ── Phase 4: Qdrant ────────────────────────────────────────────────
        if resume_phase == "qdrant":
            if not _phase_qdrant(state):
                return False

        # All phases done
        elapsed = time.monotonic() - t0
        state["completed_at"] = _now_iso()
        _write_state(state)
        logger.info("DONE   %s  (%.0fs)  phases: parse+audit+embed+qdrant",
                    filename, elapsed)

        # Link classification + check protocols
        book_key = _link_classification(filename, str(filepath))
        n_inserted = state["phases"]["qdrant"].get("chunks_inserted", 0)
        _notify("book_ingested",
                f"{filename} → {collection}: {n_inserted} chunks")
        if book_key:
            _check_protocols_for_review(book_key)

        # Reset OllamaManager failure counter between books
        try:
            from ollama_manager import ollama
            ollama.reset()
        except Exception:
            pass

        return True

    except Exception as e:
        logger.error("Unhandled error in process_book(%s): %s", filename, e)
        return False
    finally:
        _hb_stop.set()
        _set_current(None)


# ── main loop ──────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info(SEP)
    logger.info("Book ingest queue manager started")

    added = startup_scan()
    if added:
        logger.info("Startup scan: %d file(s) added to queue", added)

    while True:
        if PAUSE_FILE.exists():
            logger.info("Queue paused (pause flag set) — waiting 30s")
            time.sleep(30)
            continue

        queue = _read_queue()
        if not queue:
            logger.info("Queue empty — exiting")
            _set_current(None)
            break

        item      = queue[0]
        remaining = queue[1:]
        _write_queue(remaining)

        item["started"] = _now_iso()
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
