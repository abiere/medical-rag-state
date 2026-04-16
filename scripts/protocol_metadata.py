"""
Protocol metadata management.
Tracks which literature was used per protocol.
Earmarks protocols when new relevant literature is added.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone

log = logging.getLogger(__name__)

PROTOCOLS_DIR   = Path("/root/medical-rag/data/protocols")
CLASSIFICATIONS = Path("/root/medical-rag/config/book_classifications.json")


def save_protocol_metadata(
    protocol_id: str,
    klacht: str,
    literature_used: list,
    version: int = 1,
) -> dict:
    """
    Save metadata for a generated protocol.
    Called by generate_protocol.py after each protocol is created.

    literature_used: list of {
        book_key, chunk_ids, pages, kai_role, title
    }
    """
    PROTOCOLS_DIR.mkdir(parents=True, exist_ok=True)

    # Load current library state for snapshot
    classes = json.loads(CLASSIFICATIONS.read_text())
    ingested_books = [
        k for k, v in classes["classifications"].items()
        if v.get("ingested", False)
    ]

    metadata = {
        "protocol_id":     protocol_id,
        "klacht":          klacht,
        "version":         version,
        "generated_at":    datetime.now(timezone.utc).isoformat(),
        "literature_used": literature_used,
        "library_snapshot": ingested_books,
        "needs_review":    False,
        "review_reasons":  [],
        "reviewed_at":     None,
    }

    path = PROTOCOLS_DIR / f"{protocol_id}_metadata.json"
    path.write_text(json.dumps(metadata, indent=2))
    log.info("Saved metadata for protocol: %s", protocol_id)
    return metadata


def check_protocols_for_review(new_book_key: str) -> list:
    """
    Called after a new book is successfully ingested.
    Checks all existing protocols to see if any should be earmarked.
    Returns list of protocol_ids that need review.
    """
    if not PROTOCOLS_DIR.exists():
        return []

    try:
        classes = json.loads(CLASSIFICATIONS.read_text())
    except Exception as e:
        log.warning("check_protocols_for_review: could not load classifications: %s", e)
        return []

    new_book  = classes["classifications"].get(new_book_key, {})
    new_k     = new_book.get("k", 3)
    new_a     = new_book.get("a", 3)
    new_role  = new_book.get("role", "")
    new_title = new_book.get("full_title", new_book_key)

    flagged = []

    for meta_file in PROTOCOLS_DIR.glob("*_metadata.json"):
        try:
            metadata = json.loads(meta_file.read_text())
        except Exception:
            continue

        # Skip if already flagged for this book
        already_flagged = any(
            new_book_key in r for r in metadata.get("review_reasons", [])
        )
        if already_flagged:
            continue

        # Skip if this book was already in library when protocol was made
        if new_book_key in metadata.get("library_snapshot", []):
            continue

        # Check relevance: does new book share K/A/I role with used literature?
        should_flag = False
        reason      = None

        used_books = [
            classes["classifications"].get(lu.get("book_key", ""), {})
            for lu in metadata.get("literature_used", [])
        ]

        for used in used_books:
            used_k = used.get("k", 3)
            used_a = used.get("a", 3)

            # New book is primary (score 1) in same dimension as used source
            if new_k == 1 and used_k <= 2:
                should_flag = True
                reason = f"Nieuwe primaire anatomie/klinische bron: {new_title}"
                break
            if new_a == 1 and used_a <= 2:
                should_flag = True
                reason = f"Nieuwe primaire acupunctuurbron: {new_title}"
                break
            # Same role category
            if new_role and new_role == used.get("role"):
                should_flag = True
                reason = f"Nieuwe bron in zelfde categorie ({new_role}): {new_title}"
                break

        if should_flag and reason:
            metadata["needs_review"] = True
            metadata["review_reasons"].append(reason)
            try:
                meta_file.write_text(json.dumps(metadata, indent=2))
            except Exception as e:
                log.warning("Could not write metadata for %s: %s", meta_file.name, e)
                continue
            flagged.append(metadata["protocol_id"])
            log.info("Earmarked protocol '%s': %s", metadata["klacht"], reason)

    return flagged


def mark_as_reviewed(protocol_id: str) -> None:
    """Mark a protocol as reviewed after user acknowledges the flag."""
    path = PROTOCOLS_DIR / f"{protocol_id}_metadata.json"
    if not path.exists():
        return
    metadata = json.loads(path.read_text())
    metadata["needs_review"]   = False
    metadata["review_reasons"] = []
    metadata["reviewed_at"]    = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(metadata, indent=2))


def get_all_protocol_status() -> list:
    """Get status of all protocols for the /protocols page."""
    if not PROTOCOLS_DIR.exists():
        return []

    protocols = []
    for f in sorted(PROTOCOLS_DIR.glob("*_metadata.json")):
        try:
            metadata = json.loads(f.read_text())
        except Exception:
            continue
        protocols.append({
            "protocol_id":      metadata["protocol_id"],
            "klacht":           metadata["klacht"],
            "version":          metadata.get("version", 1),
            "generated_at":     metadata["generated_at"],
            "needs_review":     metadata.get("needs_review", False),
            "review_reasons":   metadata.get("review_reasons", []),
            "literature_count": len(metadata.get("literature_used", [])),
            "literature_titles": [
                lu.get("title", lu.get("book_key"))
                for lu in metadata.get("literature_used", [])
            ],
        })
    return protocols
