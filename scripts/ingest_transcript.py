#!/usr/bin/env python3
"""
Ingest a Whisper JSON transcript into Qdrant collection "video_transcripts".

Usage:
    python3 ingest_transcript.py --file data/transcripts/Foo.json --video-type qat

Idempotent: chunks are identified by SHA-256 hash and skipped if already present.
"""

import argparse
import hashlib
import json
import sys
import uuid
from pathlib import Path

QDRANT_URL      = "http://localhost:6333"
COLLECTION_NAME = "video_transcripts"
EMBED_MODEL     = "BAAI/bge-large-en-v1.5"
VECTOR_DIM      = 1024
TARGET_WORDS    = 300
OVERLAP_SEGS    = 2


# ── chunking ──────────────────────────────────────────────────────────────────

def chunk_segments(segments: list[dict]) -> list[list[dict]]:
    """Group segments into ~TARGET_WORDS-word chunks with OVERLAP_SEGS overlap."""
    chunks: list[list[dict]] = []
    i = 0
    while i < len(segments):
        chunk: list[dict] = []
        word_count = 0
        j = i
        while j < len(segments):
            words = len(segments[j]["text"].split())
            if word_count + words > TARGET_WORDS and chunk:
                break
            chunk.append(segments[j])
            word_count += words
            j += 1
        if not chunk:
            break
        chunks.append(chunk)
        i += max(1, len(chunk) - OVERLAP_SEGS)
    return chunks


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _point_id(chunk_hash: str) -> str:
    """Stable UUID derived from hash — ensures upsert idempotency by ID."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_hash))


# ── qdrant helpers ────────────────────────────────────────────────────────────

def _ensure_collection(client) -> None:
    from qdrant_client.models import Distance, VectorParams
    existing = {c.name for c in client.get_collections().collections}
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
        )
        print(f"Created collection '{COLLECTION_NAME}'")


def _existing_ids(client, point_ids: list[str]) -> set[str]:
    """Return the subset of point_ids that already exist in Qdrant."""
    if not point_ids:
        return set()
    results = client.retrieve(
        collection_name=COLLECTION_NAME,
        ids=point_ids,
        with_payload=False,
        with_vectors=False,
    )
    return {str(r.id) for r in results}


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Whisper transcript into Qdrant")
    parser.add_argument("--file",       required=True, help="Path to transcript JSON")
    parser.add_argument("--video-type", required=True, help="Video type (qat, nrt, pemf, rlt)")
    args = parser.parse_args()

    transcript_path = Path(args.file)
    if not transcript_path.exists():
        print(f"ERROR: transcript not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    data       = json.loads(transcript_path.read_text())
    segments   = data.get("segments", [])
    source_file = data.get("source_file", transcript_path.stem + ".mp4")

    if not segments:
        print(f"No segments in {transcript_path.name} — nothing to ingest.")
        return

    # ── build chunks ──────────────────────────────────────────────────────────
    chunks = chunk_segments(segments)
    total  = len(chunks)
    print(f"{transcript_path.name}: {len(segments)} segments → {total} chunks")

    # ── load models ───────────────────────────────────────────────────────────
    print("Loading embedding model …")
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer(EMBED_MODEL)

    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct

    client = QdrantClient(url=QDRANT_URL, timeout=30)
    _ensure_collection(client)

    # ── prepare payloads ──────────────────────────────────────────────────────
    records = []
    for idx, chunk in enumerate(chunks):
        text       = " ".join(s["text"].strip() for s in chunk)
        ch         = _hash(text)
        pid        = _point_id(ch)
        start_time = chunk[0]["start"]
        end_time   = chunk[-1]["end"]
        records.append({
            "pid":        pid,
            "hash":       ch,
            "text":       text,
            "chunk_index": idx,
            "start_time": start_time,
            "end_time":   end_time,
        })

    # ── idempotency check ─────────────────────────────────────────────────────
    all_ids  = [r["pid"] for r in records]
    seen_ids = _existing_ids(client, all_ids)

    to_insert = [r for r in records if r["pid"] not in seen_ids]
    skipped   = len(records) - len(to_insert)

    if not to_insert:
        print(f"Done: 0 chunks ingested, {skipped} skipped (already exists)")
        return

    # ── embed ─────────────────────────────────────────────────────────────────
    texts      = [r["text"] for r in to_insert]
    embeddings = embedder.encode(texts, show_progress_bar=False, normalize_embeddings=True)

    # ── upsert ────────────────────────────────────────────────────────────────
    points = []
    for r, vec in zip(to_insert, embeddings):
        points.append(PointStruct(
            id=r["pid"],
            vector=vec.tolist(),
            payload={
                "text":             r["text"],
                "video_type":       args.video_type,
                "source_file":      source_file,
                "collection_type":  "video_transcript",
                "chunk_index":      r["chunk_index"],
                "start_time":       r["start_time"],
                "end_time":         r["end_time"],
                "chunk_hash":       r["hash"],
            },
        ))

    BATCH = 64
    for start in range(0, len(points), BATCH):
        batch = points[start:start + BATCH]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        done_so_far = min(start + BATCH, len(points))
        print(f"  Ingested chunk {done_so_far}/{len(points)} for {source_file}")

    print(f"Done: {len(to_insert)} chunks ingested, {skipped} skipped (already exists)")


if __name__ == "__main__":
    main()
