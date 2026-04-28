# CONTEXT — Session Loader
> Lees dit aan het begin van elke sessie. Max 150 regels.
> Volledige technische detail: SYSTEM_DOCS/TECHNICAL.md
> **Auto-gegenereerd:** 2026-04-28 04:27 UTC

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

## Qdrant collecties (stand 2026-04-28)
| Collectie | Vectors | Gebruik |
|---|---|---|
| medical_library | 17.522 | Boekchunks (PDF/EPUB) |
| nrt_curriculum | 425 | NRT curriculum (Lawrence Woods) |
| qat_curriculum | 125 | QAT curriculum |
| rlt_flexbeam | 160 | Red Light Therapy docs |
| pemf_qrs | 64 | PEMF QRS-101 docs |
| nrt_video_transcripts | 250 | NRT video transcripties |
| qat_video_transcripts | 443 | QAT video transcripties |

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
│   ├── ingest_cache/{hash}/  ← state.json + fase-bestanden per boek
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

- Framework voor verdere werkwijze — door architect uit te werken
- CLAUDE.md drift structureel oplossen

---

## State docs (GitHub)

Lees ALTIJD deze bestanden aan het begin van elke sessie:
- CONTEXT.md  → dit bestand (automatisch bijgewerkt)
- LIVE_STATUS.md → elke 5 min bijgewerkt door sync_status.py
- BACKLOG.md  → open taken + architectuurbeslissingen
- TECHNICAL.md → volledige technische documentatie

URL: https://raw.githubusercontent.com/abiere/medical-rag-state/main/SYSTEM_DOCS/
