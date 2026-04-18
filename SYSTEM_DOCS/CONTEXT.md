# CONTEXT — Session Loader
> Lees dit aan het begin van elke sessie. Max 150 regels.
> Volledige technische detail: SYSTEM_DOCS/TECHNICAL.md

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
| OS | Ubuntu 24.04 — kernel 6.8.0-107-generic (reboot 2026-04-17) |
| Python | 3.12 — `pip install --break-system-packages` |

## Draaiende services
| Service | Poort | Status |
|---|---|---|
| FastAPI (medical-rag-web) | 8000 | ✅ Active |
| Qdrant | 6333 | ✅ Healthy |
| Ollama (llama3.1:8b) | 11434 | ✅ Active |
| book-ingest-queue | — | ✅ Active (systemd) |
| transcription-queue | — | ✅ Active (19 video's in queue) |
| ttyd terminal | 7682 | ✅ Active |
| sync-status.timer | — | ✅ Elke 5 min |
| queue-watchdog.timer | — | ✅ Elke 10 min |

## Qdrant collecties (stand 2026-04-18)
| Collectie | Vectors | Gebruik |
|---|---|---|
| medical_library | 19.572 | Boekchunks (PDF/EPUB) |
| nrt_curriculum | 425 | NRT curriculum (Lawrence Woods) |
| qat_curriculum | 125 | QAT curriculum |
| rlt_flexbeam | 160 | Red Light Therapy docs |
| pemf_qrs | 64 | PEMF QRS-101 docs |
| nrt_video_transcripts | 241 | NRT video transcripties |
| qat_video_transcripts | 0 | QAT video transcripties (lege collectie) |

## Stack
- **Embedding:** BAAI/bge-large-en-v1.5 (1024 dim) — NOOIT nomic-embed-text
- **LLM:** Ollama llama3.1:8b (lokaal)
- **Audit:** Claude Haiku API of Ollama (instelbaar in settings.json)
- **Vector DB:** Qdrant (7 collecties)
- **Web:** FastAPI poort 8000
- **OCR cascade:** RapidOCR → EasyOCR → Surya → Tesseract → Google Vision
- **Native PDF:** PyMuPDF (~92 pag/sec)
- **Transcriptie:** Whisper (lokaal)
- **Parse drempel:** ≥50 woorden/pag = native | ≥15 = mixed | <15 = scanned

## Rolverdeling
- **Lead Architect (deze chat):** bepaalt wat gebouwd wordt
- **Claude Code (op server):** lost problemen volledig zelf op

## Sleutelpaden
```
/root/medical-rag/
├── books/
│   ├── medical_literature/         ← Algemene medische PDF/EPUB
│   ├── nrt_curriculum/             ← NRT Lawrence Woods bronnen
│   ├── qat_curriculum/             ← QAT bronnen
│   ├── rlt_flexbeam/               ← FlexBeam RLT bronnen
│   └── pemf_qrs/                   ← PEMF QRS-101 bronnen
├── data/
│   ├── ingest_cache/{hash}/        ← state.json + fase-bestanden per boek
│   ├── transcripts/                ← Whisper JSON
│   ├── domain_mds/                 ← Kennissyntheselaag (Domain-*.md)
│   ├── acupuncture_points/         ← 476 Deadman PNGs + point_index.json
│   ├── extracted_images/           ← Boekafbeeldingen
│   ├── book_quality/               ← Audit rapporten + calibration_cache.json
│   └── protocols/                  ← Gegenereerde .docx + metadata
├── config/
│   ├── settings.json               ← gitignored (Claude API, nachtrun, transcriptie)
│   ├── book_classifications.json   ← K/A/I per boek (v1.1)
│   └── pipeline_diagrams.json      ← Schema's tab data
├── scripts/                        ← Alle pipeline scripts
├── web/app.py                      ← FastAPI + alle UI routes
├── SYSTEM_DOCS/                    ← Alle documentatie
│   ├── CONTEXT.md                  ← Dit bestand (session loader)
│   ├── TECHNICAL.md                ← Volledige technische referentie
│   ├── OPERATIONS.md               ← Procedures + dagelijks gebruik
│   ├── BACKLOG.md                  ← Geprioriteerde takenlijst
│   └── LIVE_STATUS.md              ← Auto-bijgewerkt elke 5 min
└── .claude/
    ├── settings.json               ← Hooks config
    ├── skills/nrt-ui-standards/    ← Design systeem skill
    └── hooks/
        ├── py_syntax_check.sh      ← PostToolUse: py_compile
        └── security_check.sh       ← PreToolUse: secrets scan
```

## Na elke significante taak
```bash
cd /root/medical-rag && \
git add -A && \
git commit -m "state: [beschrijving]" && \
git push && \
python3 /root/medical-rag/scripts/sync_status.py
```

## Terminologie
- **NRT-Amsterdam.nl** (altijd met koppelteken + .nl)
- NRT = Neural Reset Therapy | QAT = Quantum Alignment Technique
- GTR = Golgi Tendon Reflex | PEMF = Pulsed Electromagnetic Field | RLT = Red Light Therapy
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

---

## Openstaande issues (2026-04-18)
- Magee duplicaat: 2 boeken met zelfde ASIN — verwijder via /library banner
- Touch for Health PDF+EPUB: beide aanwezig, keuze nog te maken
- Video transcriptie queue: actief (grote files via ffmpeg split, Restart=always)
- EPUB caption re-extractie: loopt in achtergrond
- Test `test_anthropic_api_key_set`: FAIL (API key niet gezet in settings.json)

## Maintenance status

**Laatste run:** 18-04-2026 00:30 (521.1s)  
**Uitslag:** ⚠️ WARNING — 2 waarschuwing(en), 5 OK  


---

## Test status

**Laatste run:** 18-04-2026 00:00 (28.1s)  
**Uitslag:** ❌ MISLUKT — 32/33 geslaagd, 1 mislukt, 0 overgeslagen  
**Mislukt:** `test_anthropic_api_key_set`
