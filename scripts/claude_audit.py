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
        logger.warning("Claude audit failed for chunk %s: %s",
                       chunk.get("chunk_id", "?"), e)
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


def retroaudit_skipped(phase2_path: Path, progress_fn=None) -> tuple[int, int]:
    """
    Re-audit all chunks with audit_status starting with 'skipped' using Claude API.
    Updates phase2_path in-place (atomic write).
    Returns (tagged_count, error_count).
    """
    if not phase2_path.exists():
        return 0, 0

    chunks = json.loads(phase2_path.read_text())
    skipped = [c for c in chunks
               if (c.get("audit_status") or "").startswith("skipped")]

    if not skipped:
        return 0, 0

    logger.info("Claude retroaudit: %d skipped chunks in %s", len(skipped), phase2_path.name)
    updated = audit_chunks_parallel(skipped, progress_fn=progress_fn)

    # Merge back by chunk_id
    id_to_updated = {c.get("chunk_id"): c for c in updated if c.get("chunk_id")}
    for i, chunk in enumerate(chunks):
        cid = chunk.get("chunk_id")
        if cid and cid in id_to_updated:
            chunks[i] = id_to_updated[cid]

    # Atomic write
    tmp = phase2_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(chunks, ensure_ascii=False, indent=2))
    tmp.replace(phase2_path)

    tagged = sum(1 for c in updated if c.get("audit_status") == "tagged_claude")
    errors = len(updated) - tagged
    return tagged, errors
