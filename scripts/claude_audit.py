"""
Claude API audit module — replaces Ollama for K/A/I chunk tagging.
Uses claude-haiku for speed and cost efficiency.
Parallel via ThreadPoolExecutor — network I/O bound.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

SETTINGS_PATH = Path("/root/medical-rag/config/settings.json")

AUDIT_PROMPT = """Classify this medical/acupuncture text chunk.

Respond ONLY with valid JSON, no explanation:
{{
  "k": 1,
  "a": 1,
  "i": 1,
  "tags": ["tag1", "tag2"],
  "summary": "one sentence Dutch summary max 20 words"
}}

Where:
  k = Clinical/tissue relevance: 1=primary, 2=supporting, 3=background
  a = Acupuncture relevance:     1=primary, 2=supporting, 3=background
  i = Image/illustration relevance: 1=primary, 2=supporting, 3=background
  tags = max 3 Dutch clinical tags
  summary = one sentence Dutch summary, max 20 words

Text chunk:
{text}"""


def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_PATH.read_text())
    except Exception:
        return {}


def is_enabled() -> bool:
    """Return True if Claude API is enabled and a key is available."""
    s = load_settings()
    cfg = s.get("claude_api", {})
    if not cfg.get("enabled", False):
        return False
    # api_key in settings takes priority; fall back to env var
    key = cfg.get("api_key", "").strip() or os.environ.get("ANTHROPIC_API_KEY", "").strip()
    return bool(key)


def get_client():
    """Return an Anthropic client using settings or env var key."""
    s = load_settings()
    cfg = s.get("claude_api", {})
    key = cfg.get("api_key", "").strip() or os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        raise ValueError("No Anthropic API key configured in settings.json or ANTHROPIC_API_KEY env var")
    import anthropic
    return anthropic.Anthropic(api_key=key)


def audit_chunk(client, model: str, max_tokens: int, chunk: dict) -> dict:
    """Audit a single chunk. Returns updated chunk with kai tags."""
    text = chunk.get("text", "")[:2000]  # cap at 2000 chars

    # Immediate fallback for empty or too-short text — no API call needed
    if not text or len(text.strip()) < 10:
        chunk["kai_k"]        = 3
        chunk["kai_a"]        = 3
        chunk["kai_i"]        = 3
        chunk["tags"]         = []
        chunk["summary"]      = "Lege of te korte chunk"
        chunk["audit_status"] = "tagged_claude_default"
        chunk["audit_engine"] = "claude_api"
        return chunk

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": AUDIT_PROMPT.format(text=text),
            }],
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        result = json.loads(raw)
        chunk["kai_k"]         = max(1, min(3, int(result.get("k", 3))))
        chunk["kai_a"]         = max(1, min(3, int(result.get("a", 3))))
        chunk["kai_i"]         = max(1, min(3, int(result.get("i", 3))))
        chunk["tags"]          = result.get("tags", [])[:3]
        chunk["summary"]       = str(result.get("summary", ""))[:200]
        chunk["audit_status"]  = "tagged_claude"
        chunk["audit_engine"]  = "claude_api"
    except Exception as e:
        retry_count = chunk.get("_retry_count", 0) + 1
        chunk["_retry_count"] = retry_count
        logger.warning("Claude audit failed for chunk %s (attempt %d): %s",
                       chunk.get("chunk_id", "?"), retry_count, e)
        if retry_count >= 3:
            chunk["kai_k"]        = 3
            chunk["kai_a"]        = 3
            chunk["kai_i"]        = 3
            chunk["tags"]         = []
            chunk["summary"]      = "Automatisch getagd na herhaald falen"
            chunk["audit_status"] = "tagged_claude_default"
            chunk["audit_engine"] = "claude_api"
            logger.warning("Chunk %s assigned default tags after %d failures: %s",
                           chunk.get("chunk_id", "?"), retry_count, repr(text[:100]))
        else:
            chunk["audit_status"] = "skipped_claude_error"
            chunk["audit_engine"] = "claude_api"
    return chunk


def audit_chunks_parallel(chunks: list, progress_fn=None) -> list:
    """
    Audit all chunks in parallel using Claude API.
    Returns updated chunks list (same order as input).
    """
    if not chunks:
        return chunks

    s = load_settings()
    cfg = s.get("claude_api", {})
    model      = cfg.get("model",       "claude-haiku-4-5-20251001")
    max_workers = cfg.get("max_workers", 10)
    max_tokens  = cfg.get("max_tokens",  300)

    client  = get_client()
    results = [None] * len(chunks)
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(audit_chunk, client, model, max_tokens, chunk): i
            for i, chunk in enumerate(chunks)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                logger.error("Future error for chunk index %d: %s", idx, e)
                results[idx] = chunks[idx]
                results[idx]["audit_status"] = "skipped_claude_error"
            completed += 1
            if progress_fn:
                progress_fn(completed, len(chunks))

    return results


def _update_state_after_retroaudit(phase2_path: Path,
                                    tagged: int, errors: int) -> None:
    """
    Update state.json after retroaudit using phase2 file as ground truth.
    Atomic write — same pattern as book_ingest_queue._write_state.
    """
    state_path = phase2_path.parent / "state.json"
    if not state_path.exists():
        logger.warning("state.json not found at %s — skipping update", state_path)
        return
    try:
        state = json.loads(state_path.read_text())

        # Ground truth: recount directly from the updated phase2 file
        chunks = json.loads(phase2_path.read_text())
        total         = len(chunks)
        now_tagged    = sum(1 for c in chunks
                            if str(c.get("audit_status", "")).startswith("tagged"))
        still_skipped = sum(1 for c in chunks
                            if str(c.get("audit_status", "")).startswith("skipped"))

        audit = state.setdefault("phases", {}).setdefault("audit", {})
        audit["chunks_tagged"]  = now_tagged
        audit["chunks_skipped"] = still_skipped
        audit["chunks_total"]   = total

        if still_skipped == 0:
            audit["status"] = "done"
            audit["retroaudit_completed_at"] = datetime.now(timezone.utc).isoformat()
            logger.info("Audit phase fully complete after retroaudit: %s", phase2_path.name)
        else:
            logger.info("Retroaudit partial for %s: %d tagged, %d still skipped",
                        phase2_path.name, now_tagged, still_skipped)

        state["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Atomic write
        tmp = state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2))
        os.replace(tmp, state_path)

        logger.info("state.json updated: %d tagged, %d skipped, %d total — %s",
                    now_tagged, still_skipped, total, state_path.parent.name)
    except Exception as e:
        logger.error("Failed to update state.json after retroaudit: %s", e)


def retroaudit_skipped(phase2_path: Path, progress_fn=None) -> tuple[int, int]:
    """
    Re-audit all chunks that haven't been successfully tagged yet.
    Includes chunks with status starting with 'skipped' and chunks with no status.
    Updates phase2_path in-place (atomic write) and syncs state.json.
    Returns (tagged_count, error_count).
    """
    if not phase2_path.exists():
        return 0, 0

    chunks = json.loads(phase2_path.read_text())

    # Collect (original_index, chunk) for everything not yet tagged
    skipped_map = [
        (i, c) for i, c in enumerate(chunks)
        if not (c.get("audit_status") or "").startswith("tagged")
    ]

    if not skipped_map:
        return 0, 0

    skipped_list = [x[1] for x in skipped_map]
    logger.info("Claude retroaudit: %d chunks needing audit in %s",
                len(skipped_list), phase2_path.name)
    updated = audit_chunks_parallel(skipped_list, progress_fn=progress_fn)

    # Merge back: prefer chunk_id match, fallback to positional index for no-id chunks
    id_to_result: dict = {}
    for j, (orig_idx, _) in enumerate(skipped_map):
        upd = updated[j]
        cid = upd.get("chunk_id")
        if cid:
            id_to_result[cid] = upd
        else:
            chunks[orig_idx] = upd  # direct index update — no chunk_id available

    for i, chunk in enumerate(chunks):
        cid = chunk.get("chunk_id")
        if cid and cid in id_to_result:
            chunks[i] = id_to_result[cid]

    # Atomic write of phase2 file
    tmp = phase2_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(chunks, ensure_ascii=False, indent=2))
    tmp.replace(phase2_path)

    tagged = sum(1 for c in updated
                 if str(c.get("audit_status", "")).startswith("tagged"))
    errors = len(updated) - tagged

    # Sync state.json with ground-truth counts from updated phase2 file
    _update_state_after_retroaudit(phase2_path, tagged, errors)

    return tagged, errors
