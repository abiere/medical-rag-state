#!/usr/bin/env python3
"""
sync_context.py — Auto-generates SYSTEM_DOCS/CONTEXT.md from live server data.
Called by: post-commit hook + sync_status.py (every 5 min)
"""

import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE         = Path("/root/medical-rag")
CONTEXT_PATH = BASE / "SYSTEM_DOCS" / "CONTEXT.md"
BACKLOG_PATH = BASE / "SYSTEM_DOCS" / "BACKLOG.md"

QDRANT_COLLECTIONS = [
    ("medical_library",       "Boekchunks (PDF/EPUB)"),
    ("nrt_curriculum",        "NRT curriculum (Lawrence Woods)"),
    ("qat_curriculum",        "QAT curriculum"),
    ("rlt_flexbeam",          "Red Light Therapy docs"),
    ("pemf_qrs",              "PEMF QRS-101 docs"),
    ("nrt_video_transcripts", "NRT video transcripties"),
    ("qat_video_transcripts", "QAT video transcripties"),
]


def _qdrant_count(collection: str) -> str:
    try:
        req = urllib.request.Request(f"http://localhost:6333/collections/{collection}")
        with urllib.request.urlopen(req, timeout=4) as resp:
            d = json.loads(resp.read())
            n = d.get("result", {}).get("points_count", 0)
            return f"{n:,}".replace(",", ".")
    except Exception:
        return "?"


def _open_issues() -> str:
    """Extract top open ([ ]) items from the 🔴 priority section of BACKLOG.md."""
    try:
        text = BACKLOG_PATH.read_text()
        items = []
        in_prio = False
        for line in text.splitlines():
            if re.search(r"Prioriteit|🔴", line) and line.startswith("##"):
                in_prio = True
                continue
            if line.startswith("## ") and in_prio:
                in_prio = False
            if in_prio and re.match(r"\s*- \[ \]", line):
                item = re.sub(r"^\s*- \[ \]\s*\*\*(.+?)\*\*.*", r"\1", line)
                if item == line:
                    item = re.sub(r"^\s*- \[ \]\s*", "", line)
                clean = f"- {item[:120].strip()}"
                if clean not in items:
                    items.append(clean)
                if len(items) >= 6:
                    break
        return "\n".join(items) if items else "- Geen open prioriteiten"
    except Exception:
        return "- (BACKLOG.md niet leesbaar)"


def generate_context() -> str:
    now  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    qdrant_rows = ""
    for col, desc in QDRANT_COLLECTIONS:
        count = _qdrant_count(col)
        qdrant_rows += f"| {col} | {count} | {desc} |\n"

    issues_text = _open_issues()

    return f"""# CONTEXT — Session Loader
> Lees dit aan het begin van elke sessie. Max 150 regels.
> Volledige technische detail: SYSTEM_DOCS/TECHNICAL.md
> **Auto-gegenereerd:** {now}

## Wat dit systeem is
Privé, volledig lokaal RAG-systeem voor medische en acupunctuurliteratuur.
Alleen via Tailscale (100.66.194.55). Outputs: behandelprotocollen, blogteksten, Q&A.

## Server
| Eigenschap | Waarde |
|---|---|
| SSH | `ssh root@100.66.194.55` |
| Web | `http://100.66.194.55:8000` |
| Terminal | `http://100.66.194.55:7682` |
| Hardware | Hetzner CX53 — 16 vCPU, 32GB RAM, 301GB SSD |
| OS | Ubuntu 24.04 — kernel 6.8.0-107-generic |
| Python | 3.12 — `pip install --break-system-packages` |

## Draaiende services
| Service | Poort | Status |
|---|---|---|
| FastAPI (medical-rag-web) | 8000 | ✅ Active |
| Qdrant | 6333 | ✅ Healthy |
| Ollama (llama3.1:8b) | 11434 | ✅ Active |
| book-ingest-queue | — | ✅ Active (systemd) |
| transcription-queue | — | ✅ Active (Restart=always) |
| ttyd terminal | 7682 | ✅ Active |
| sync-status.timer | — | ✅ Elke 5 min |
| queue-watchdog.timer | — | ✅ Elke 10 min |

## Qdrant collecties (stand {date})
| Collectie | Vectors | Gebruik |
|---|---|---|
{qdrant_rows}
## Stack
- **Embedding:** BAAI/bge-large-en-v1.5 (1024 dim) — NOOIT nomic-embed-text
- **LLM:** Ollama llama3.1:8b (lokaal)
- **Audit:** Claude Haiku API of Ollama (instelbaar in settings.json)
- **Vector DB:** Qdrant (7 collecties)
- **Web:** FastAPI poort 8000
- **OCR cascade:** RapidOCR → EasyOCR → Surya → Tesseract → Google Vision

## Sleutelpaden
```
/root/medical-rag/
├── books/
│   ├── medical_literature/    ← Algemene medische PDF/EPUB
│   ├── nrt_curriculum/        ← NRT Lawrence Woods bronnen
│   ├── qat_curriculum/        ← QAT bronnen
│   ├── rlt_flexbeam/          ← FlexBeam RLT bronnen
│   └── pemf_qrs/              ← PEMF QRS-101 bronnen
├── data/
│   ├── ingest_cache/{{hash}}/  ← state.json + fase-bestanden per boek
│   ├── extracted_images/       ← Boekafbeeldingen
│   ├── book_quality/           ← Audit rapporten
│   └── protocols/              ← Gegenereerde .docx + metadata
├── config/
│   ├── settings.json           ← gitignored (Claude API, nachtrun)
│   └── book_classifications.json ← K/A/I per boek (v1.1)
├── scripts/                    ← Alle pipeline scripts
├── web/app.py                  ← FastAPI + alle UI routes
└── SYSTEM_DOCS/                ← Alle documentatie
```

## Terminologie
- **NRT-Amsterdam.nl** (altijd met koppelteken + .nl)
- NRT = Neural Reset Therapy | QAT = Quantum Alignment Technique
- Acupunctuur: **HE / KID / LIV / P / SJ** (Deadman standaard — NOOIT HT/KI/LV/PC/TW)

## QAT Balancepunten (definitief april 2026 — NIET WIJZIGEN)
```
CV=SP-21R | GV=SP-21L | BL=BL-58  | SJ=SJ-5  | KID=KID-4 | P=P-6
GB=GB-37  | ST=ST-40  | LI=LI-6   | SI=SI-7  | LU=LU-7   | SP=SP-4
HE=HE-5   | LIV=LIV-5
```

## Kritieke regels
1. **Nav:** `NAV_ITEMS` is de enige source of truth — nooit hardcoded in pagina's
2. **Embedding:** Altijd `BAAI/bge-large-en-v1.5` — nooit nomic-embed-text
3. **Kleur:** `#1A6B72` teal — nooit `#2563eb` voor primaire knoppen/headers
4. **Destructief:** Altijd confirmation dialog met chunk count eerst
5. **UI taken:** Lees eerst `.claude/skills/nrt-ui-standards/SKILL.md` via Read tool
6. **onclick:** Nooit f-string variabelen in onclick attrs — gebruik data-* patroon

---

## Open issues (uit BACKLOG.md)

{issues_text}

---

## State docs (GitHub)

Lees ALTIJD deze bestanden aan het begin van elke sessie:
- CONTEXT.md  → dit bestand (automatisch bijgewerkt)
- LIVE_STATUS.md → elke 5 min bijgewerkt door sync_status.py
- BACKLOG.md  → open taken + architectuurbeslissingen
- TECHNICAL.md → volledige technische documentatie

URL: https://raw.githubusercontent.com/abiere/medical-rag-state/main/SYSTEM_DOCS/
"""


def main():
    context = generate_context()
    CONTEXT_PATH.write_text(context)
    print(f"Written: {CONTEXT_PATH}")
    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE / "scripts"))
        from ai_client import update_ai_status_md
        update_ai_status_md()
        print("Written: SYSTEM_DOCS/AI_STATUS.md")
    except Exception as e:
        print(f"AI_STATUS.md update skipped: {e}")


if __name__ == "__main__":
    main()
