#!/usr/bin/env python3
"""
normalize_points.py — Canonical acupuncture point code normalization.

Converts any variant notation to the canonical form used in this system:
  BL-40, ST-36, GV-20, CV-6, KID-3, HE-7, LIV-3, P-6, etc.

Usage:
    from normalize_points import normalize_point, normalize_point_list
    normalize_point("UB 40")   → "BL-40"
    normalize_point("KI3")     → "KID-3"
    normalize_point("Ren-6")   → "CV-6"
"""

from __future__ import annotations

import re

# ── Meridian abbreviation → canonical form ────────────────────────────────────
# Canonical abbreviations used in this system (matching Deadman + point_index.json)

MERIDIAN_MAP: dict[str, str] = {
    # Bladder / Urinary Bladder variants
    "UB":  "BL",
    "V":   "BL",   # French notation

    # Heart variants
    "HT":  "HE",
    "H":   "HE",

    # Kidney variants
    "KI":  "KID",
    "K":   "KID",
    "KD":  "KID",
    "R":   "KID",   # French (Rein)

    # Liver variants
    "LV":  "LIV",
    "LR":  "LIV",
    "F":   "LIV",   # French (Foie)

    # Pericardium variants
    "PC":  "P",
    "HC":  "P",
    "MH":  "P",
    "MC":  "P",

    # Triple Warmer / Sanjiao variants
    "TW":  "SJ",
    "TB":  "SJ",
    "TE":  "SJ",
    "TH":  "SJ",
    "TR":  "SJ",
    "TF":  "SJ",   # French (Triple Foyer)

    # Gallbladder variants
    "VB":  "GB",   # French (Vésicule Biliaire)

    # Governing Vessel variants
    "GV":  "GV",
    "VG":  "GV",   # French
    "DU":  "GV",
    "DM":  "GV",

    # Conception Vessel variants
    "CV":  "CV",
    "VC":  "CV",   # French
    "REN": "CV",
    "RM":  "CV",

    # Large Intestine variants
    "CO":  "LI",   # French (Côlon)
    "DI":  "LI",   # German (Dickdarm)

    # Small Intestine variants
    "IG":  "SI",   # French (Intestin Grêle)
    "DU_SI": "SI", # German

    # Full English name variants
    "LUNG":        "LU",
    "HEART":       "HE",
    "LIVER":       "LIV",
    "STOMACH":     "ST",
    "SPLEEN":      "SP",
    "KIDNEY":      "KID",
    "BLADDER":     "BL",
    "PERICARDIUM": "P",
    "GALLBLADDER": "GB",

    # German abbreviation variants (some Thieme books)
    "MA":  "ST",   # Magen
    "MI":  "SP",   # Milz
    "NI":  "KID",  # Niere
    "LE":  "LIV",  # Leber
    "GA":  "GB",   # Gallenblase
    "LA":  "LU",   # Lunge
    "HE_DE": "HE", # Herz (collision with HE canonical, handled in lookup order)
    "PE":  "P",    # Perikard
    "3E":  "SJ",   # Drei Erwärmer
    "DI_DE": "LI", # Dickdarm (German)
    "DU_DE": "GV", # Du Mai
}

# Pass-through: canonical names need no remapping
_CANONICAL = {"LU", "LI", "ST", "SP", "HE", "SI", "BL", "KID",
              "P", "SJ", "GB", "LIV", "GV", "CV"}

# QAT luo-connecting point for each meridian (2026 verified mapping)
QAT_BALANCE_2026: dict[str, str] = {
    "CV":  "SP-21",
    "GV":  "SP-21",
    "BL":  "BL-58",
    "SJ":  "SJ-5",
    "KID": "KID-4",
    "P":   "P-6",
    "GB":  "GB-37",
    "ST":  "ST-40",
    "LI":  "LI-6",
    "SI":  "SI-7",
    "LU":  "LU-7",
    "SP":  "SP-4",
    "HE":  "HE-5",
    "LIV": "LIV-5",
}

# ── Regex for raw point extraction ────────────────────────────────────────────
# Matches: ST 36, BL-40, KI.3, UB40, ren6, du20, etc.
_POINT_PATTERN = re.compile(
    r"\b([A-Za-z]{1,12})[.\s\-_]?(\d{1,3})\b",
    re.IGNORECASE,
)


def normalize_meridian(raw: str) -> str | None:
    """
    Normalize a meridian abbreviation to canonical form.
    Returns None if unrecognized.
    """
    upper = raw.upper().strip()
    if upper in _CANONICAL:
        return upper
    return MERIDIAN_MAP.get(upper)


def normalize_point(raw: str) -> str | None:
    """
    Normalize a raw point string like 'UB 40', 'KI3', 'Ren-6' to 'BL-40'.
    Returns None if unrecognized.
    """
    m = _POINT_PATTERN.match(raw.strip())
    if not m:
        return None
    meridian_raw, number = m.group(1), m.group(2)
    canonical = normalize_meridian(meridian_raw)
    if canonical is None:
        return None
    return f"{canonical}-{int(number)}"


def normalize_point_list(raw_list: list[str]) -> list[str]:
    """Normalize a list of raw point strings, dropping unrecognized entries."""
    result = []
    for raw in raw_list:
        norm = normalize_point(raw)
        if norm:
            result.append(norm)
    return result


def extract_and_normalize(text: str) -> list[str]:
    """
    Extract all point codes from free text and return normalized list.
    Deduplicates while preserving order.
    """
    seen: set[str] = set()
    result: list[str] = []
    for m in _POINT_PATTERN.finditer(text):
        meridian_raw, number = m.group(1), m.group(2)
        canonical = normalize_meridian(meridian_raw)
        if canonical is None:
            continue
        point = f"{canonical}-{int(number)}"
        if point not in seen:
            seen.add(point)
            result.append(point)
    return result


def get_balance_point(meridian: str) -> str | None:
    """Return the QAT luo-connecting balance point for a canonical meridian."""
    canonical = normalize_meridian(meridian)
    if canonical is None:
        return None
    return QAT_BALANCE_2026.get(canonical)


# ── Self-test ──────────────────────────────────────────────────────────────────

def _self_test() -> None:
    cases = [
        ("UB 40",   "BL-40"),
        ("UB-40",   "BL-40"),
        ("KI3",     "KID-3"),
        ("KI-3",    "KID-3"),
        ("KD3",     "KID-3"),
        ("Ren-6",   "CV-6"),
        ("ren6",    "CV-6"),
        ("Du20",    "GV-20"),
        ("GV 20",   "GV-20"),
        ("HT7",     "HE-7"),
        ("LV-3",    "LIV-3"),
        ("LR3",     "LIV-3"),
        ("PC6",     "P-6"),
        ("TW5",     "SJ-5"),
        ("TB5",     "SJ-5"),
        ("TE5",     "SJ-5"),
        ("VB-37",   "GB-37"),
        ("ST36",    "ST-36"),
        ("ST-36",   "ST-36"),
        ("BL-40",   "BL-40"),
        ("SP21",    "SP-21"),
    ]

    failures = 0
    for raw, expected in cases:
        got = normalize_point(raw)
        status = "OK" if got == expected else "FAIL"
        if status == "FAIL":
            failures += 1
        print(f"  {status}  normalize_point({raw!r}) = {got!r}  (expected {expected!r})")

    # Balance points
    print()
    for meridian in ["BL", "ST-40", "KID", "GB"]:
        print(f"  balance({meridian!r}) = {get_balance_point(meridian)!r}")

    print()
    print(f"Result: {len(cases) - failures}/{len(cases)} passed")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")


if __name__ == "__main__":
    _self_test()
