#!/usr/bin/env python3
"""
rag_query.py — RAG query engine for Medical RAG.

Usage as CLI:
  python3 scripts/rag_query.py \
    --query "what is the Golgi Tendon Reflex and how does it relate to NRT" \
    --collections nrt_video_transcripts \
    --output /tmp/test_query.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────

BASE            = Path(__file__).parent.parent
AI_INSTRUCTIONS = BASE / "config" / "ai_instructions"
IMAGE_APPROVALS = BASE / "data" / "image_approvals.json"

QDRANT_URL   = "http://localhost:6333"
OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

sys.path.insert(0, str(BASE / "scripts"))
from ai_client import AIClient
_ai = AIClient()

ALL_COLLECTIONS = ["medical_library", "nrt_curriculum", "qat_curriculum", "rlt_flexbeam", "pemf_qrs", "nrt_video_transcripts", "qat_video_transcripts"]

POINT_CODE_RE = re.compile(
    r"\b(LU|LI|ST|SP|HT|SI|BL|KD|PC|SJ|GB|LR|GV|CV|TH|TW|TB|TE|TR|KI|UB|VG|VC|RM|DU|RN)-\d+\b",
    re.IGNORECASE,
)
FIGURE_RE = re.compile(r"\b(?:fig(?:ure)?\.?\s*)(\d+(?:\.\d+)*)\b", re.IGNORECASE)


# ── helpers ────────────────────────────────────────────────────────────────────

def _ts_display(start: float, end: float) -> str:
    def fmt(s: float) -> str:
        m, sec = divmod(int(s), 60)
        h, m = divmod(m, 60)
        return f"{h}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"
    return f"{fmt(start)} - {fmt(end)}"


def _load_ai_instruction(filename: str) -> str:
    try:
        return (AI_INSTRUCTIONS / filename).read_text(encoding="utf-8")
    except Exception:
        return ""


def _load_approvals() -> dict:
    try:
        if IMAGE_APPROVALS.exists():
            return json.loads(IMAGE_APPROVALS.read_text())
    except Exception:
        pass
    return {"approved": [], "rejected": [], "pending": []}


def _extract_point_codes(text: str) -> list[str]:
    return sorted({m.group().upper() for m in POINT_CODE_RE.finditer(text)})


# ── embedding ──────────────────────────────────────────────────────────────────

def embed_query(text: str) -> list[float]:
    """Embed a query using BAAI/bge-large-en-v1.5. Lazy import to avoid slow startup."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    return model.encode([text], show_progress_bar=False).tolist()[0]


# ── Qdrant helpers ─────────────────────────────────────────────────────────────

def _qdrant_request(method: str, path: str, body: dict | None = None, timeout: int = 30) -> dict:
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        f"{QDRANT_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _collection_exists(name: str) -> bool:
    try:
        r = _qdrant_request("GET", f"/collections/{name}", timeout=5)
        return r.get("status") == "ok"
    except Exception:
        return False


def _qdrant_search(collection: str, vector: list[float], limit: int = 15) -> list[dict]:
    try:
        r = _qdrant_request("POST", f"/collections/{collection}/points/search", {
            "vector":       vector,
            "limit":        limit,
            "with_payload": True,
            "with_vector":  False,
        })
        return r.get("result", [])
    except Exception:
        return []


def _qdrant_scroll(collection: str, filt: dict, limit: int = 50) -> list[dict]:
    try:
        r = _qdrant_request("POST", f"/collections/{collection}/points/scroll", {
            "filter":       filt,
            "limit":        limit,
            "with_payload": True,
            "with_vector":  False,
        })
        return r.get("result", {}).get("points", [])
    except Exception:
        return []


# ── result formatting ──────────────────────────────────────────────────────────

def _format_source(hit: dict, collection: str) -> dict:
    p     = hit.get("payload", {})
    score = hit.get("score", 0.0)

    if p.get("collection_type") == "video_transcript":
        start = float(p.get("start_time", 0.0))
        end   = float(p.get("end_time", 0.0))
        return {
            "type":              "video",
            "text":              p.get("text", ""),
            "source_file":       p.get("source_file", ""),
            "video_type":        p.get("video_type", ""),
            "start_time":        start,
            "end_time":          end,
            "timestamp_display": _ts_display(start, end),
            "score":             round(score, 4),
            "collection":        collection,
        }
    else:
        return {
            "type":               "book",
            "text":               p.get("text", ""),
            "source_file":        p.get("source_file", ""),
            "page_number":        p.get("page_number"),
            "chapter":            p.get("chapter", ""),
            "score":              round(score, 4),
            "point_codes":        p.get("point_codes", []),
            "figure_refs":        p.get("figure_refs", []),
            "image_links":        p.get("image_links", []),
            "collection":         collection,
            "source_category":    p.get("source_category", ""),
            "usability_tags":     p.get("usability_tags", []),
            "protocol_relevance": float(p.get("protocol_relevance", 0.0)),
        }


def _collect_images(sources: list[dict]) -> list[dict]:
    approvals     = _load_approvals()
    approved_set  = {e["path"] for e in approvals.get("approved", []) if isinstance(e, dict)}
    pending_set   = {e["path"] for e in approvals.get("pending",  []) if isinstance(e, dict)}
    approval_meta: dict[str, dict] = {}
    for entries in approvals.values():
        for e in entries:
            if isinstance(e, dict) and e.get("path"):
                approval_meta[e["path"]] = e

    seen: set[str] = set()
    images: list[dict] = []

    for src in sources:
        for img_path in src.get("image_links", []):
            if img_path in seen:
                continue
            seen.add(img_path)
            meta = approval_meta.get(img_path, {})
            images.append({
                "path":             img_path,
                "url":              f"/images/file/{Path(img_path).name}",
                "source_file":      src.get("source_file", ""),
                "page":             src.get("page_number"),
                "approved":         img_path in approved_set,
                "pending":          img_path in pending_set,
                "ai_suggestion":    meta.get("ai_suggestion"),
                "ai_confidence":    meta.get("ai_confidence"),
                "surrounding_text": meta.get("surrounding_text", ""),
            })

    return images


def _build_prompt(query: str, sources: list[dict]) -> str:
    chunks_text = ""
    for i, src in enumerate(sources, 1):
        if src["type"] == "book":
            book = Path(src["source_file"]).stem
            page = src.get("page_number", "?")
            pts  = ", ".join(src.get("point_codes", []))
            figs = ", ".join(src.get("figure_refs", []))
            ref  = f"({book} p.{page})"
            if pts:
                ref += f" [Punten: {pts}]"
            if figs:
                ref += f" [Figuur: {figs}]"
        else:
            vid = Path(src["source_file"]).stem
            ts  = src.get("timestamp_display", "")
            ref = f"({vid} {ts})"

        chunks_text += f"\n[{i}] {ref}\n{src['text'][:600]}\n"

    return (
        "Je bent een medisch assistent voor NRT-Amsterdam.nl die een QAT/NRT behandelaar "
        "helpt behandelprotocollen te genereren.\n\n"
        "Beantwoord de volgende vraag uitsluitend op basis van de onderstaande bronnen. "
        "Citeer altijd bronnen: voor boeken gebruik (Boeknaam p.PAGINA), voor video's gebruik "
        "(Videonaam MM:SS-MM:SS).\n"
        "Als de vraag over acupunctuurpunten gaat, vermeld altijd de puntcodes (ST-36).\n"
        "Als de vraag over anatomie gaat, verwijs naar figuurnummers indien beschikbaar.\n"
        "Houd antwoorden praktisch — de behandelaar moet weten WAT te behandelen en WAAR "
        "pads of naalden te plaatsen.\n"
        "Antwoord in het Nederlands. Wees beknopt en praktisch.\n\n"
        f"Vraag: {query}\n\n"
        f"Bronnen:\n{chunks_text}\n\n"
        "Antwoord:"
    )


# ── Ollama ─────────────────────────────────────────────────────────────────────

def _ollama_generate(prompt: str, system: str = "", timeout: int = 180) -> str:
    try:
        return _ai.generate("rag_answering", prompt, system=system or None)
    except Exception as e:
        return f"[Antwoord genereren mislukt: {e}]"


# ── core query functions ───────────────────────────────────────────────────────

def rag_search_only(
    query: str,
    collections: list[str] | None = None,
    filters: dict | None = None,
) -> dict:
    """
    Embed query, search Qdrant, return prepared dict.
    Does NOT call Ollama — fast path for the streaming endpoint.
    Returns: {sources, images, prompt, system_context, collections_searched}
    """
    if collections is None:
        collections = ALL_COLLECTIONS

    vector              = embed_query(query)
    point_codes_in_q    = _extract_point_codes(query)
    all_hits: list[dict] = []
    searched: list[str]  = []

    for coll in collections:
        if not _collection_exists(coll):
            continue
        hits = _qdrant_search(coll, vector, limit=15)
        for h in hits:
            h["_collection"] = coll
        all_hits.extend(hits)
        searched.append(coll)

    # Sort by score, take top 10
    all_hits.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    top_hits = all_hits[:10]

    # Boost chunks with matching point codes
    if point_codes_in_q:
        for hit in top_hits:
            chunk_pts = [c.upper() for c in hit.get("payload", {}).get("point_codes", [])]
            if any(p in chunk_pts for p in point_codes_in_q):
                hit["score"] = hit.get("score", 0.0) + 0.1
        top_hits.sort(key=lambda x: x.get("score", 0.0), reverse=True)

    sources = [_format_source(h, h.get("_collection", "")) for h in top_hits]
    images  = _collect_images(sources)

    nrt_qat_bridge = _load_ai_instruction("nrt_qat_bridge.md")
    tagging_rules  = _load_ai_instruction("tagging_rules.md")
    system_context = (
        f"{nrt_qat_bridge[:1500]}\n\n{tagging_rules[:1500]}"
        if (nrt_qat_bridge or tagging_rules) else ""
    )

    return {
        "sources":              sources,
        "images":               images,
        "prompt":               _build_prompt(query, sources),
        "system_context":       system_context,
        "collections_searched": searched,
    }


def rag_query(
    query: str,
    collections: list[str] | None = None,
    filters: dict | None = None,
) -> dict:
    """Full RAG pipeline including Ollama answer generation."""
    t0       = time.monotonic()
    prepared = rag_search_only(query, collections, filters)
    answer   = _ollama_generate(prepared["prompt"], prepared["system_context"])

    return {
        "answer":               answer,
        "sources":              prepared["sources"],
        "images":               prepared["images"],
        "query_time_ms":        int((time.monotonic() - t0) * 1000),
        "collections_searched": prepared["collections_searched"],
    }


# ── image search ───────────────────────────────────────────────────────────────

def image_search(
    query: str,
    approved_only: bool = True,
    book_filter: str | None = None,
) -> list[dict]:
    """Search for images matching query via point codes, figure refs, or semantics."""
    approvals    = _load_approvals()
    approved_set = {e["path"] for e in approvals.get("approved", []) if isinstance(e, dict)}
    approval_meta: dict[str, dict] = {}
    for entries in approvals.values():
        for e in entries:
            if isinstance(e, dict) and e.get("path"):
                approval_meta[e["path"]] = e

    image_links: list[str] = []
    pt_codes   = _extract_point_codes(query)
    fig_matches = FIGURE_RE.findall(query)

    if pt_codes:
        for coll in ["medical_library", "nrt_curriculum", "qat_curriculum"]:
            if not _collection_exists(coll):
                continue
            pts = _qdrant_scroll(coll, {
                "must": [{"key": "point_codes", "match": {"any": pt_codes}}]
            })
            for pt in pts:
                for img in pt.get("payload", {}).get("image_links", []):
                    if img not in image_links:
                        image_links.append(img)

    elif fig_matches:
        for coll in ["medical_library"]:
            if not _collection_exists(coll):
                continue
            pts = _qdrant_scroll(coll, {
                "must": [{"key": "figure_refs", "match": {"any": fig_matches}}]
            })
            for pt in pts:
                for img in pt.get("payload", {}).get("image_links", []):
                    if img not in image_links:
                        image_links.append(img)

    else:
        vector = embed_query(query)
        for coll in ["medical_library", "nrt_curriculum", "qat_curriculum"]:
            if not _collection_exists(coll):
                continue
            for hit in _qdrant_search(coll, vector, limit=10):
                for img in hit.get("payload", {}).get("image_links", []):
                    if img not in image_links:
                        image_links.append(img)

    results: list[dict] = []
    for img_path in image_links:
        meta        = approval_meta.get(img_path, {})
        is_approved = img_path in approved_set
        if approved_only and not is_approved:
            continue
        if book_filter and meta.get("book", "") != book_filter:
            continue
        results.append({
            "path":          img_path,
            "url":           f"/images/file/{Path(img_path).name}",
            "source_file":   meta.get("book", ""),
            "page":          meta.get("page", 0),
            "approved":      is_approved,
            "ai_suggestion": meta.get("ai_suggestion"),
            "ai_confidence": meta.get("ai_confidence"),
        })

    return results


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="RAG query engine")
    parser.add_argument("--query",       required=True,                   help="Search query")
    parser.add_argument("--collections", default=",".join(ALL_COLLECTIONS), help="Comma-separated collection names")
    parser.add_argument("--output",      default=None,                    help="Write result JSON to file")
    args = parser.parse_args()

    collections = [c.strip() for c in args.collections.split(",") if c.strip()]
    result      = rag_query(args.query, collections)

    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"Written: {args.output}")
        print(f"Answer ({len(result['answer'])} chars): {result['answer'][:200]}")
        print(f"Sources: {len(result['sources'])}")
        print(f"Images:  {len(result['images'])}")
        print(f"Time:    {result['query_time_ms']} ms")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
