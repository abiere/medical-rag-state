"""
Medical RAG — Video Transcription Pipeline

Transcribes training videos using OpenAI Whisper (local, no API key needed)
and ingests the resulting transcripts into Qdrant with full citation metadata.

Installation
────────────
    pip install openai-whisper --break-system-packages
    apt-get install -y ffmpeg          # for audio extraction

Folder layout
─────────────
    /root/medical-rag/videos/
        nrt/    ← NRT training videos  → content_type: training_nrt
        qat/    ← QAT training videos  → content_type: training_qat
        pemf/   ← PEMF instruction     → content_type: device_pemf
        rlt/    ← RLT instruction      → content_type: device_rlt

Output per video
────────────────
    data/transcripts/{video_stem}.json   — timestamped segments
    data/transcripts/{video_stem}.txt    — plain text (for manual review)

Usage
─────
    python scripts/transcribe_videos.py --type nrt
    python scripts/transcribe_videos.py --type qat --model small
    python scripts/transcribe_videos.py --file videos/nrt/NRT_Shoulder.mp4
    python scripts/transcribe_videos.py --type nrt --dry-run
    python scripts/transcribe_videos.py --type nrt --ingest
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR      = Path("/root/medical-rag")
VIDEOS_DIR    = BASE_DIR / "videos"
TRANSCRIPTS_DIR = BASE_DIR / "data" / "transcripts"
BOOKS_DIR     = BASE_DIR / "books"
VIDEO_DOCUMENT_LINKS_PATH = BASE_DIR / "data" / "video_document_links.json"
BOOKS_METADATA_PATH       = BASE_DIR / "data" / "books_metadata.json"

QDRANT_URL   = "http://localhost:6333"
EMBED_MODEL  = "BAAI/bge-large-en-v1.5"
EMBED_DIM    = 1024
CHUNK_SIZE   = 512
CHUNK_OVERLAP = 64

# Supported video containers
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".m4v", ".webm", ".avi"}

# Content type per video subfolder
FOLDER_CONTENT_TYPE: dict[str, str] = {
    "nrt":  "training_nrt",
    "qat":  "training_qat",
    "pemf": "device_pemf",
    "rlt":  "device_rlt",
}

# Qdrant collection per content type
CONTENT_TYPE_COLLECTION: dict[str, str] = {
    "training_nrt": "training_materials",
    "training_qat": "training_materials",
    "device_pemf":  "device_protocols",
    "device_rlt":   "device_protocols",
}

# Whisper model choices — tradeoff: speed vs accuracy
# tiny < base < small < medium < large
DEFAULT_WHISPER_MODEL = "medium"


# ---------------------------------------------------------------------------
# Audio extraction
# ---------------------------------------------------------------------------

def _extract_audio(video_path: Path, tmp_dir: Path) -> Path:
    """
    Extract audio from a video file using ffmpeg.
    Returns path to a temporary WAV file (16 kHz mono, as Whisper expects).
    Raises RuntimeError if ffmpeg is not installed or extraction fails.
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found. Install with: apt-get install -y ffmpeg"
        )

    audio_path = tmp_dir / f"{video_path.stem}.wav"
    cmd = [
        "ffmpeg", "-y",
        "-i",    str(video_path),
        "-vn",                  # no video
        "-acodec", "pcm_s16le", # PCM WAV
        "-ar",   "16000",       # 16 kHz — Whisper's native rate
        "-ac",   "1",           # mono
        str(audio_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed for {video_path.name}:\n{result.stderr[-500:]}"
        )
    return audio_path


# ---------------------------------------------------------------------------
# Transcript persistence
# ---------------------------------------------------------------------------

def _save_transcript(
    video_path: Path,
    segments: list[dict],
    transcripts_dir: Path,
) -> tuple[Path, Path]:
    """
    Save transcript as:
      - {stem}.json  — full segments with timestamps
      - {stem}.txt   — plain text for easy reading
    Returns (json_path, txt_path).
    """
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    stem = video_path.stem

    json_path = transcripts_dir / f"{stem}.json"
    txt_path  = transcripts_dir / f"{stem}.txt"

    payload = {
        "source_file":  video_path.name,
        "transcribed_at": datetime.datetime.utcnow().isoformat() + "Z",
        "segments":     segments,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    txt_path.write_text(
        "\n".join(s["text"].strip() for s in segments if s.get("text")),
        encoding="utf-8",
    )
    return json_path, txt_path


# ---------------------------------------------------------------------------
# Video–document link matching
# ---------------------------------------------------------------------------

def _find_related_documents(video_path: Path) -> dict:
    """
    Try to find related PDF/EPUB files in books/ by name similarity.
    Also loads existing entries from video_document_links.json.
    Returns a dict with 'related_muscles' and 'related_pdf_pages' keys.
    """
    # Load existing manual links
    if VIDEO_DOCUMENT_LINKS_PATH.exists():
        try:
            links = json.loads(VIDEO_DOCUMENT_LINKS_PATH.read_text())
            if video_path.name in links:
                return links[video_path.name]
        except Exception:
            pass

    # Auto-match: check if any book filename shares significant words with the video
    video_words = set(
        w.lower() for w in re.split(r"[\W_]+", video_path.stem) if len(w) > 3
    )
    matches: list[dict] = []
    if BOOKS_DIR.exists():
        for book in BOOKS_DIR.iterdir():
            if book.suffix.lower() not in {".pdf", ".epub"}:
                continue
            book_words = set(
                w.lower() for w in re.split(r"[\W_]+", book.stem) if len(w) > 3
            )
            overlap = video_words & book_words
            if len(overlap) >= 2:
                matches.append({"file": book.name, "page": None, "match_words": list(overlap)})

    return {
        "related_muscles":   [],
        "related_pdf_pages": matches,
    }


def _update_video_document_links(video_path: Path, link_data: dict) -> None:
    """Persist link data for a video to video_document_links.json."""
    links: dict = {}
    if VIDEO_DOCUMENT_LINKS_PATH.exists():
        try:
            links = json.loads(VIDEO_DOCUMENT_LINKS_PATH.read_text())
        except Exception:
            pass
    links[video_path.name] = link_data
    VIDEO_DOCUMENT_LINKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    VIDEO_DOCUMENT_LINKS_PATH.write_text(json.dumps(links, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Qdrant ingestion of transcript segments
# ---------------------------------------------------------------------------

def _ingest_transcript(
    video_path:   Path,
    segments:     list[dict],
    content_type: str,
    link_data:    dict,
) -> None:
    """
    Ingest transcript segments into Qdrant.

    Each segment becomes a Document with:
        content_type, source_file, timestamp (start seconds),
        format: "transcript", see_also (related PDF pages)
    """
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

    collection = CONTENT_TYPE_COLLECTION.get(content_type, "training_materials")
    see_also   = [p["file"] for p in link_data.get("related_pdf_pages", []) if p.get("file")]

    documents = []
    for seg in segments:
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        chunk_hash = hashlib.md5(
            f"{video_path.name}:{seg.get('start', 0):.1f}:{text[:64]}".encode()
        ).hexdigest()
        doc = Document(
            text=text,
            metadata={
                "source_file":    video_path.name,
                "source_path":    str(video_path),
                "format":         "transcript",
                "content_type":   content_type,
                "timestamp":      seg.get("start", 0.0),
                "timestamp_end":  seg.get("end", 0.0),
                "page_number":    0,
                "section_number": 0,
                "chunk_hash":     chunk_hash,
                "image_links":    [],
                "see_also":       see_also,
                "caption":        "",
                "figure_labels":  [],
                "image_type":     "",
                "image_description": "",
                "figure_number":  "",
                "citation":       {},
                "citation_apa":   "",
            },
            excluded_llm_metadata_keys=[
                "source_path", "chunk_hash", "image_links",
                "figure_labels", "image_type", "citation", "see_also",
            ],
            excluded_embed_metadata_keys=[
                "source_path", "chunk_hash", "image_links",
                "figure_labels", "image_type", "citation",
            ],
        )
        documents.append(doc)

    if not documents:
        logger.warning("No transcript segments to ingest for %s", video_path.name)
        return

    logger.info("Loading embedding model: %s", EMBED_MODEL)
    Settings.embed_model   = HuggingFaceEmbedding(model_name=EMBED_MODEL)
    Settings.chunk_size    = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP
    Settings.llm           = None

    client   = QdrantClient(url=QDRANT_URL)
    existing = {c.name for c in client.get_collections().collections}
    if collection not in existing:
        logger.info("Creating collection '%s'", collection)
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )

    vector_store = QdrantVectorStore(client=client, collection_name=collection)
    logger.info(
        "Ingesting %d transcript segments → '%s'", len(documents), collection
    )
    VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store,
        transformations=[
            SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        ],
        show_progress=True,
    )
    logger.info("Ingestion complete — '%s'", collection)


# ---------------------------------------------------------------------------
# Main transcription logic
# ---------------------------------------------------------------------------

def transcribe_video(
    video_path:    Path,
    content_type:  str,
    whisper_model: str = DEFAULT_WHISPER_MODEL,
    language:      str = "nl",
    task:          str = "translate",
    dry_run:       bool = False,
    do_ingest:     bool = False,
) -> dict:
    """
    Full pipeline for one video:
      1. Check transcript cache (skip if already transcribed)
      2. Extract audio with ffmpeg
      3. Transcribe with Whisper
      4. Save JSON + TXT transcripts
      5. Find related documents
      6. Update video_document_links.json
      7. Optionally ingest into Qdrant

    Returns the transcript payload dict.
    """
    json_path = TRANSCRIPTS_DIR / f"{video_path.stem}.json"
    txt_path  = TRANSCRIPTS_DIR / f"{video_path.stem}.txt"

    # ── Cache check ──────────────────────────────────────────────────────────
    if json_path.exists() and not dry_run:
        logger.info("  Transcript exists — skipping: %s", json_path.name)
        payload = json.loads(json_path.read_text())
        segments = payload.get("segments", [])
    else:
        logger.info("Transcribing: %s  [model=%s, lang=%s, task=%s]",
                    video_path.name, whisper_model, language, task)

        if dry_run:
            logger.info("  DRY RUN — skipping audio extraction and transcription")
            return {"source_file": video_path.name, "segments": [], "dry_run": True}

        # ── Audio extraction ─────────────────────────────────────────────────
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path  = Path(tmp)
            audio_path = _extract_audio(video_path, tmp_path)
            logger.info("  Audio extracted: %s (%.1f MB)",
                        audio_path.name, audio_path.stat().st_size / 1e6)

            # ── Whisper transcription ────────────────────────────────────────
            try:
                import whisper  # type: ignore
            except ImportError as exc:
                raise ImportError(
                    "pip install openai-whisper --break-system-packages"
                ) from exc

            logger.info("  Loading Whisper model '%s' …", whisper_model)
            model = whisper.load_model(whisper_model)

            logger.info("  Transcribing …")
            result = model.transcribe(
                str(audio_path),
                language=language,
                task=task,
                verbose=False,
            )
            segments = [
                {
                    "start": round(seg["start"], 2),
                    "end":   round(seg["end"],   2),
                    "text":  seg["text"].strip(),
                }
                for seg in result.get("segments", [])
            ]

        # ── Save transcripts ─────────────────────────────────────────────────
        json_path, txt_path = _save_transcript(video_path, segments, TRANSCRIPTS_DIR)
        logger.info(
            "  Saved: %s (%d segments)", json_path.name, len(segments)
        )

    # ── Document linking ─────────────────────────────────────────────────────
    link_data = _find_related_documents(video_path)
    _update_video_document_links(video_path, link_data)
    if link_data["related_pdf_pages"]:
        logger.info(
            "  Related documents: %s",
            ", ".join(p["file"] for p in link_data["related_pdf_pages"]),
        )

    # ── Qdrant ingestion ─────────────────────────────────────────────────────
    if do_ingest:
        _ingest_transcript(video_path, segments, content_type, link_data)

    return {
        "source_file":  video_path.name,
        "content_type": content_type,
        "segments":     len(segments),
        "json_path":    str(json_path),
        "txt_path":     str(txt_path),
        "related_docs": len(link_data.get("related_pdf_pages", [])),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe NRT/QAT/PEMF/RLT training videos and ingest into Qdrant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--type",
        choices=list(FOLDER_CONTENT_TYPE.keys()),
        help="Process all videos in videos/{type}/ (nrt | qat | pemf | rlt)",
    )
    source.add_argument(
        "--file",
        type=Path,
        help="Transcribe a single video file",
    )
    parser.add_argument(
        "--content-type",
        choices=list(CONTENT_TYPE_COLLECTION.keys()),
        help="Override content_type (default: derived from --type or folder)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_WHISPER_MODEL,
        choices=["tiny", "base", "small", "medium", "large"],
        help=f"Whisper model size (default: {DEFAULT_WHISPER_MODEL})",
    )
    parser.add_argument(
        "--language",
        default="nl",
        help="Transcription language hint for Whisper (default: nl)",
    )
    parser.add_argument(
        "--task",
        default="translate",
        choices=["transcribe", "translate"],
        help="Whisper task: 'translate' outputs English, 'transcribe' keeps source language (default: translate)",
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="After transcription, ingest segments into Qdrant",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan for videos and check cache without transcribing",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ── Collect video files ──────────────────────────────────────────────────
    if args.file:
        video_files   = [args.file.resolve()]
        content_type  = args.content_type or "training_nrt"
    else:
        folder       = VIDEOS_DIR / args.type
        if not folder.exists():
            logger.error(
                "Video directory not found: %s  "
                "(run: mkdir -p %s)", folder, folder
            )
            return
        video_files  = sorted(
            p for p in folder.iterdir()
            if p.suffix.lower() in VIDEO_EXTENSIONS
        )
        content_type = args.content_type or FOLDER_CONTENT_TYPE[args.type]

    if not video_files:
        logger.warning("No video files found.")
        return

    logger.info(
        "Found %d video(s)  [content_type=%s]",
        len(video_files), content_type,
    )

    results = []
    for vp in video_files:
        try:
            r = transcribe_video(
                video_path    = vp,
                content_type  = content_type,
                whisper_model = args.model,
                language      = args.language,
                task          = args.task,
                dry_run       = args.dry_run,
                do_ingest     = args.ingest and not args.dry_run,
            )
            results.append(r)
        except Exception as exc:
            logger.error("Failed: %s — %s", vp.name, exc)
            results.append({"source_file": vp.name, "error": str(exc)})

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
