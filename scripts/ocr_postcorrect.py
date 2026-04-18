#!/usr/bin/env python3
"""
ocr_postcorrect.py — Ollama-based post-correction for OCR errors in medical text.

Focus:
  - Acupuncture point code normalisation  (ST36 / "ST 36" → ST-36)
  - Common OCR character confusions       (l→1, O→0, rn→m …)
  - Ollama full-text correction for low-confidence pages

Entry points:
  needs_correction(text, confidence) -> bool
  correct_with_ollama(text) -> str
  batch_correct(chunks) -> list[dict]   (modifies in-place, returns same list)
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))
from ai_client import AIClient
_ai = AIClient()

# OCR quality thresholds
CORRECTION_CONFIDENCE_THRESHOLD = 0.65
MIN_WORDS_FOR_CORRECTION        = 30
MAX_CHARS_PER_CALL               = 1500

# Regex: match meridian abbreviations followed (loosely) by digits
_POINT_NORMALISE_RE = re.compile(
    r"\b(LU|LI|ST|SP|HT|SI|BL|KD|PC|SJ|GB|LR|GV|CV|TH|TW|TB|TE|TR|KI|UB"
    r"|VG|VC|RM|DU|RN)"
    r"[\s\.]?(\d+)\b",
    re.IGNORECASE,
)


# ── public API ────────────────────────────────────────────────────────────────

def needs_correction(text: str, confidence: float) -> bool:
    """
    Return True if this chunk should be sent to Ollama for correction.

    Triggers:
    - confidence below threshold
    - more than 25% non-alphanumeric, non-punctuation characters (garbled OCR)
    """
    if confidence < CORRECTION_CONFIDENCE_THRESHOLD:
        return True
    if len(text) > 20:
        noise = sum(
            1 for c in text
            if not c.isalnum() and c not in " \n\t.,;:()-'\"/\\[]{}|"
        )
        if noise / len(text) > 0.25:
            return True
    return False


def correct_with_ollama(text: str) -> str:
    """
    Send text to AIClient for medical OCR error correction.
    Falls back to rule_correct on any error.
    """
    if len(text.split()) < MIN_WORDS_FOR_CORRECTION:
        return rule_correct(text)

    prompt = (
        "You are correcting OCR output from a scanned medical/acupuncture textbook. "
        "Fix OCR errors: garbled characters, split words, misread letters (l→1, 0→O, rn→m). "
        "Standardise acupuncture point codes to format 'XX-NN' (e.g. ST-36, SP-10, BL-40). "
        "Keep ALL original content — do not add or remove information. "
        "Return only the corrected text, nothing else.\n\n"
        f"{text[:MAX_CHARS_PER_CALL]}"
    )
    try:
        corrected = _ai.generate(
            "ocr_correction", prompt, max_tokens=600,
            extra_options={"temperature": 0.1},
        ).strip()
        if corrected and len(corrected.split()) >= MIN_WORDS_FOR_CORRECTION // 2:
            return corrected
        logger.debug("AI returned empty/short result — using rules only")
    except Exception as e:
        logger.warning("AI correction failed (%s) — rules only", e)

    return rule_correct(text)


def rule_correct(text: str) -> str:
    """
    Apply fast deterministic OCR fixes for medical text.
    No network call.
    """
    # Normalise point codes: "ST36", "ST 36", "ST.36" → "ST-36"
    text = _POINT_NORMALISE_RE.sub(
        lambda m: f"{m.group(1).upper()}-{m.group(2)}",
        text,
    )
    # Isolated 'l' followed by digit: "l0" → "10"
    text = re.sub(r"\bl(\d)", r"1\1", text)
    # Common word-level OCR confusions
    _word_fixes = [
        (r"\btreatrnent\b", "treatment"),
        (r"\bsyrnptorn\b",  "symptom"),
        (r"\brnedical\b",   "medical"),
        (r"\bacupuncture\b", "acupuncture"),  # protect correct spelling
        (r"\brnethod\b",    "method"),
        (r"\bpatient\b",    "patient"),
    ]
    for pattern, replacement in _word_fixes:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def batch_correct(chunks: list[dict]) -> list[dict]:
    """
    Apply post-correction to OCR chunks that need it.
    - rule_correct() is applied to all non-native chunks (fast, always)
    - correct_with_ollama() applied only when needs_correction() is True

    Modifies chunks in-place.  Returns the same list.
    """
    ollama_count = 0

    for chunk in chunks:
        engine = chunk.get("ocr_engine", "native")
        if engine == "native":
            continue

        text = chunk.get("text", "")
        conf = chunk.get("ocr_confidence", 1.0)

        # Always apply rules (zero-cost)
        corrected = rule_correct(text)

        # Ollama for low-quality pages
        if needs_correction(text, conf):
            corrected = correct_with_ollama(corrected)
            ollama_count += 1

        if corrected != text:
            chunk["text"]              = corrected
            chunk["ocr_postcorrected"] = True

    if ollama_count:
        logger.info("Ollama post-correction applied to %d chunk(s)", ollama_count)

    return chunks
