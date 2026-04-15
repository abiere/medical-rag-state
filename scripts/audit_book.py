#!/usr/bin/env python3
"""
audit_book.py — LLM quality audit for parsed book chunks.

Usage:
    python3 scripts/audit_book.py \
        --chunks /tmp/test_chunks.json \
        --output /tmp/test_audit.json

Outputs a structured audit report JSON.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)

BASE             = Path(__file__).parent.parent
QUALITY_DIR      = BASE / "data" / "book_quality"
TAGS_FILE        = BASE / "config" / "usability_tags.json"
IMAGE_APPROVALS  = BASE / "data" / "image_approvals.json"
AI_INSTRUCTIONS  = BASE / "config" / "ai_instructions"
OLLAMA_URL       = "http://localhost:11434"
OLLAMA_MODEL     = "llama3.1:8b"
AUDIT_SAMPLE     = 15
TAG_BATCH        = 5
MIN_QUALITY      = 3.5


def _load_ai_instruction(filename: str) -> str:
    """Load an AI instruction MD file, stripping frontmatter comments."""
    try:
        return (AI_INSTRUCTIONS / filename).read_text(encoding="utf-8")
    except Exception:
        return ""


# ── Ollama helper ─────────────────────────────────────────────────────────────

def _ollama(prompt: str, timeout: int = 120) -> dict | None:
    body = json.dumps({
        "model":  OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            raw = data.get("response", "").strip()
            # Strip markdown code fences if present
            raw = raw.lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("Ollama JSON parse error: %s", e)
        return None
    except Exception as e:
        logger.warning("Ollama request failed: %s", e)
        return None


# ── Phase 1: structural checks ────────────────────────────────────────────────

def structural_audit(chunks: list[dict]) -> dict:
    if not chunks:
        return {
            "total_chunks": 0, "avg_chunk_words": 0,
            "short_chunks": 0, "long_chunks": 0,
            "point_codes_found": 0, "figure_refs_found": 0,
            "images_extracted": 0, "translation_applied": False,
            "epub_strategy": None,
        }

    word_counts = [len(c.get("text", "").split()) for c in chunks]
    avg_words   = sum(word_counts) / len(word_counts) if word_counts else 0
    short       = sum(1 for w in word_counts if w < 50)
    long        = sum(1 for w in word_counts if w > 800)

    point_total = sum(len(c.get("point_codes", [])) for c in chunks)
    fig_total   = sum(len(c.get("figure_refs", [])) for c in chunks)
    img_total   = sum(len(c.get("image_links", [])) for c in chunks)
    translated  = any(c.get("text_original") for c in chunks)
    strategy    = chunks[0].get("epub_strategy") if chunks else None

    return {
        "total_chunks":      len(chunks),
        "avg_chunk_words":   round(avg_words, 1),
        "short_chunks":      short,
        "long_chunks":       long,
        "point_codes_found": point_total,
        "figure_refs_found": fig_total,
        "images_extracted":  img_total,
        "translation_applied": translated,
        "epub_strategy":     strategy,
    }


# ── Phase 2: LLM semantic audit ───────────────────────────────────────────────

def llm_audit(chunks: list[dict]) -> dict:
    sample_size = min(AUDIT_SAMPLE, len(chunks))
    if sample_size == 0:
        return {"sample_size": 0, "quality_score": None, "flagged_chunks": 0}

    sample = random.sample(chunks, sample_size)
    scores: list[dict] = []
    flagged = 0

    for i, chunk in enumerate(sample):
        text = chunk.get("text", "")[:800]
        has_translation = bool(chunk.get("text_original"))
        trans_note = "The chunk was translated from another language." if has_translation else "No translation."

        prompt = (
            "You are auditing chunks from a medical/acupuncture textbook for RAG quality.\n"
            f"{trans_note}\n"
            "Evaluate this chunk:\n\n"
            f'"""{text}"""\n\n'
            "Rate each dimension 1-5:\n"
            "1. coherence: Does it start and end at natural boundaries?\n"
            "2. completeness: Is the medical concept complete within this chunk?\n"
            "3. terminology: Are medical terms, point codes, anatomical terms preserved?\n"
            "4. translation: If translated, is the English natural and accurate? (rate 5 if not translated)\n"
            "Give one specific improvement suggestion if any score < 4, else 'none'.\n"
            'Respond in JSON only: {"coherence":N,"completeness":N,"terminology":N,"translation":N,"suggestion":"..."}'
        )
        result = _ollama(prompt, timeout=60)
        if result and all(k in result for k in ("coherence", "completeness", "terminology", "translation")):
            scores.append(result)
            if any(result.get(k, 5) < 3 for k in ("coherence", "completeness", "terminology", "translation")):
                flagged += 1
        else:
            logger.warning("LLM audit failed for chunk %d", i)

    if not scores:
        return {
            "sample_size":   sample_size,
            "quality_score": None,
            "flagged_chunks": flagged,
            "error":         "All LLM calls failed",
        }

    def _avg(key: str) -> float:
        vals = [s[key] for s in scores if isinstance(s.get(key), (int, float))]
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    avg_coh  = _avg("coherence")
    avg_comp = _avg("completeness")
    avg_term = _avg("terminology")
    avg_trans = _avg("translation")
    quality_score = round((avg_coh + avg_comp + avg_term + avg_trans) / 4, 2)

    suggestions = [s["suggestion"] for s in scores
                   if s.get("suggestion") and s["suggestion"] != "none"]

    return {
        "sample_size":      sample_size,
        "avg_coherence":    avg_coh,
        "avg_completeness": avg_comp,
        "avg_terminology":  avg_term,
        "avg_translation":  avg_trans,
        "quality_score":    quality_score,
        "flagged_chunks":   flagged,
        "suggestion":       suggestions[0] if suggestions else "none",
    }


# ── Auto-classification ───────────────────────────────────────────────────────

def auto_classify(chunks: list[dict]) -> dict:
    if not chunks:
        return {"error": "no chunks"}

    sample = chunks[:5]
    combined = "\n\n---\n\n".join(c.get("text", "")[:400] for c in sample)

    prompt = (
        "Based on these chunks from a medical book, classify:\n"
        "1. primary_use: list from [acupuncture_points, tcm_diagnosis, anatomy, "
        "physiology, nrt_treatment, qat_treatment, device_settings]\n"
        "2. image_quality: none/low/medium/high\n"
        "3. image_type: describe what the images likely contain\n"
        "4. recommended_collection: single best collection name from "
        "[anatomy_atlas, acupuncture_points, medical_literature, nrt_curriculum, "
        "qat_curriculum, device_documentation]\n"
        "5. confidence: 0.0-1.0\n"
        "Respond in JSON only.\n\n"
        f"Chunks:\n{combined}"
    )
    result = _ollama(prompt, timeout=90)
    if not result:
        return {"error": "classification failed"}

    return {
        "primary_use":            result.get("primary_use", []),
        "secondary_use":          result.get("secondary_use", []),
        "image_quality":          result.get("image_quality", "unknown"),
        "image_type":             result.get("image_type", ""),
        "recommended_collection": result.get("recommended_collection", ""),
        "confidence":             result.get("confidence", 0.0),
    }


# ── Usability tagging ─────────────────────────────────────────────────────────

def _load_usability_tags() -> dict:
    try:
        return json.loads(TAGS_FILE.read_text()).get("tags", {})
    except Exception:
        return {}


def tag_chunks_with_ollama(chunks: list[dict]) -> list[dict]:
    """
    Add usability_tags, protocol_relevance, and primary_use to each chunk.
    Processes in batches of TAG_BATCH. Modifies chunks in-place, returns them.
    Uses tagging_rules.md and nrt_qat_bridge.md as context.
    """
    usability_tags = _load_usability_tags()
    if not usability_tags:
        logger.warning("No usability tags found in config — skipping tagging")
        return chunks

    tag_names = list(usability_tags.keys())
    tag_descriptions = {k: v["description"] for k, v in usability_tags.items()}
    tag_summary = json.dumps(tag_descriptions, indent=2)

    # Load AI instruction context
    nrt_qat_bridge  = _load_ai_instruction("nrt_qat_bridge.md")
    tagging_rules   = _load_ai_instruction("tagging_rules.md")

    system_context = (
        "You are tagging medical textbook chunks for a QAT/NRT treatment protocol "
        "generation system.\n\n"
        "About the treatment method:\n"
        f"{nrt_qat_bridge[:2000]}\n\n"
        "Tagging rules:\n"
        f"{tagging_rules[:2000]}\n\n"
        "Tag each chunk according to these rules. Be precise about protocol_relevance."
    ) if nrt_qat_bridge or tagging_rules else (
        "You are tagging medical textbook chunks for a RAG system "
        "that generates acupuncture treatment protocols."
    )

    tagged = 0
    failed = 0

    for i in range(0, len(chunks), TAG_BATCH):
        batch = chunks[i: i + TAG_BATCH]
        for chunk in batch:
            text = chunk.get("text", "")[:800]
            prompt = (
                f"{system_context}\n\n"
                f"Available tags and their meanings:\n{tag_summary}\n\n"
                "Tag this chunk. Return JSON only:\n"
                '{"usability_tags":["tag1","tag2"],'
                '"protocol_relevance":0.0,'
                '"has_point_codes":false,'
                '"has_figure_refs":false,'
                '"primary_use":"one sentence"}\n\n'
                f"Chunk:\n{text}"
            )
            result = _ollama(prompt, timeout=60)
            if result:
                valid_tags = [t for t in result.get("usability_tags", []) if t in tag_names]
                chunk["usability_tags"]     = valid_tags
                chunk["protocol_relevance"] = float(result.get("protocol_relevance", 0.0))
                chunk["has_point_codes"]    = bool(result.get("has_point_codes", False))
                chunk["has_figure_refs"]    = bool(result.get("has_figure_refs", False))
                chunk["primary_use"]        = str(result.get("primary_use", ""))
                tagged += 1
            else:
                chunk.setdefault("usability_tags", [])
                chunk.setdefault("protocol_relevance", 0.0)
                failed += 1

    logger.info("Tagged %d/%d chunks (%d failed)", tagged, len(chunks), failed)
    return chunks


def build_usability_profile(chunks: list[dict]) -> dict:
    """
    Count tag frequencies and normalise to 0-5 scale.
    Returns {tag_name: score_0_to_5} plus raw counts.
    """
    counts: dict[str, int] = {}
    for chunk in chunks:
        for tag in chunk.get("usability_tags", []):
            counts[tag] = counts.get(tag, 0) + 1

    if not counts:
        return {"scores": {}, "counts": {}, "total_tagged": 0}

    max_count = max(counts.values()) or 1
    scores = {tag: round(count / max_count * 5, 1) for tag, count in counts.items()}
    return {
        "scores": scores,
        "counts": counts,
        "total_tagged": sum(1 for c in chunks if c.get("usability_tags")),
    }


# ── Image pre-screening ────────────────────────────────────────────────────────

def prescreeen_images(chunks: list[dict], book_name: str) -> None:
    """
    For each image extracted from this book, add an entry to image_approvals.json
    with an AI pre-screening suggestion (if not already present).
    """
    # Collect all image paths across chunks, with surrounding text
    image_context: dict[str, str] = {}
    for chunk in chunks:
        for img_path in chunk.get("image_links", []):
            if img_path not in image_context:
                image_context[img_path] = chunk.get("text", "")[:100]

    if not image_context:
        return

    # Load existing approvals
    try:
        approvals = json.loads(IMAGE_APPROVALS.read_text()) if IMAGE_APPROVALS.exists() else {}
    except Exception:
        approvals = {}
    if not isinstance(approvals, dict):
        approvals = {}
    approvals.setdefault("approved", [])
    approvals.setdefault("rejected", [])
    approvals.setdefault("pending", [])

    existing_paths = {
        e["path"] for lst in approvals.values() for e in lst if isinstance(e, dict)
    }

    new_entries: list[dict] = []
    for img_path, surrounding_text in image_context.items():
        if img_path in existing_paths:
            continue

        # AI pre-screening
        prompt = (
            "Based on this image path and surrounding text, is this image "
            "useful for acupuncture treatment protocols?\n"
            f"image_path: {img_path}\n"
            f"surrounding_text: {surrounding_text}\n"
            'Respond JSON: {"useful":true,"reason":"...","confidence":0.0}'
        )
        result = _ollama(prompt, timeout=30)
        ai_suggestion = None
        ai_confidence = None
        if result:
            ai_suggestion = bool(result.get("useful"))
            ai_confidence = float(result.get("confidence", 0.0))

        try:
            page = int(img_path.split("_")[1]) if "_" in img_path else 0
        except Exception:
            page = 0

        entry = {
            "path":             img_path,
            "book":             book_name,
            "page":             page,
            "surrounding_text": surrounding_text,
            "ai_suggestion":    ai_suggestion,
            "ai_confidence":    ai_confidence,
            "approved":         None,
            "approved_by":      None,
            "approved_at":      None,
        }
        new_entries.append(entry)

    if new_entries:
        approvals["pending"].extend(new_entries)
        IMAGE_APPROVALS.parent.mkdir(parents=True, exist_ok=True)
        IMAGE_APPROVALS.write_text(json.dumps(approvals, indent=2))
        logger.info("Added %d images to pending approval list", len(new_entries))


# ── Auto-remediation check ────────────────────────────────────────────────────

def check_remediation(structural: dict, llm: dict) -> dict:
    issues: list[str] = []
    suggestions: list[str] = []

    avg_words = structural.get("avg_chunk_words", 0)
    total     = structural.get("total_chunks", 1) or 1
    short_pct = structural.get("short_chunks", 0) / total * 100

    if avg_words < 100:
        issues.append("avg_chunk_words < 100")
        suggestions.append("retry with larger chunk target (600 words)")

    if short_pct > 20:
        issues.append(f"short_chunks > 20% ({short_pct:.0f}%)")
        suggestions.append("parsing strategy problem — check parser output")

    qs = llm.get("quality_score")
    if qs is not None and qs < MIN_QUALITY:
        issues.append(f"quality_score {qs} < {MIN_QUALITY}")
        suggestions.append("retry with different chunking parameters")

    at = llm.get("avg_translation")
    if at is not None and at < 3:
        issues.append(f"avg_translation {at} < 3")
        suggestions.append("retry translation with more context")

    return {
        "issues":      issues,
        "suggestions": suggestions,
        "remediation_needed": len(issues) > 0,
    }


# ── Main audit function ───────────────────────────────────────────────────────

def audit_book(
    chunks: list[dict],
    book_name: str = "",
    collection: str = "",
    run_llm: bool = True,
    run_tagging: bool = True,
    save: bool = True,
) -> dict:
    """
    Run full audit on a chunk list. Returns audit report dict.
    Saves to data/book_quality/{stem}_audit.json if save=True.
    """
    logger.info("Auditing %s (%d chunks)", book_name, len(chunks))

    s = structural_audit(chunks)
    logger.info("Structural: avg_words=%.0f short=%d long=%d points=%d figs=%d",
                s["avg_chunk_words"], s["short_chunks"], s["long_chunks"],
                s["point_codes_found"], s["figure_refs_found"])

    llm = {}
    classification = {}

    usability_profile: dict = {}

    if run_llm and chunks:
        logger.info("Running LLM audit on %d sample chunks...", min(AUDIT_SAMPLE, len(chunks)))
        llm = llm_audit(chunks)
        logger.info("LLM quality_score=%.2f flagged=%d",
                    llm.get("quality_score") or 0, llm.get("flagged_chunks", 0))

        logger.info("Running auto-classification...")
        classification = auto_classify(chunks)
        logger.info("Recommended collection: %s (confidence=%.2f)",
                    classification.get("recommended_collection", "?"),
                    classification.get("confidence", 0))

    if run_tagging and chunks:
        logger.info("Tagging %d chunks with usability tags...", len(chunks))
        tag_chunks_with_ollama(chunks)
        usability_profile = build_usability_profile(chunks)
        logger.info("Usability profile: %d tags applied", len(usability_profile.get("scores", {})))

    if book_name and chunks:
        prescreeen_images(chunks, book_name)

    remediation = check_remediation(s, llm)

    qs = llm.get("quality_score")
    status = "approved" if (qs is None or qs >= MIN_QUALITY) else "low_quality"
    if remediation["remediation_needed"] and qs is not None and qs < MIN_QUALITY:
        status = "needs_remediation"

    report: dict[str, Any] = {
        "book":             book_name,
        "collection":       collection,
        "audited_at":       datetime.now(timezone.utc).isoformat(),
        "total_chunks":     s["total_chunks"],
        "structural":       s,
        "llm_audit":        llm if llm else None,
        "auto_classification": classification if classification else None,
        "usability_profile": usability_profile if usability_profile else None,
        "remediation":      remediation,
        "remediation_applied": False,
        "status":           status,
    }

    if save and book_name:
        QUALITY_DIR.mkdir(parents=True, exist_ok=True)
        stem = Path(book_name).stem
        out_path = QUALITY_DIR / f"{stem}_audit.json"
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        logger.info("Audit saved → %s", out_path)

    return report


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Audit parsed book chunks for RAG quality")
    ap.add_argument("--chunks",     required=True, help="Path to chunks JSON file")
    ap.add_argument("--output",     default="/tmp/audit_output.json")
    ap.add_argument("--no-llm",     action="store_true", help="Skip LLM audit (structural only)")
    ap.add_argument("--book",       default="", help="Book filename (for report metadata)")
    ap.add_argument("--collection", default="", help="Target collection name")
    args = ap.parse_args()

    chunks = json.loads(Path(args.chunks).read_text())
    book_name = args.book or (chunks[0].get("source_file", "") if chunks else "")
    collection = args.collection or (chunks[0].get("collection_type", "") if chunks else "")

    report = audit_book(
        chunks,
        book_name=book_name,
        collection=collection,
        run_llm=not args.no_llm,
        save=False,
    )

    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\n→ Written to {args.output}")


if __name__ == "__main__":
    main()
