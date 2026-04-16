# CONTEXT — Session Loader
> Read this file at the start of every session. Max 150 lines.
> Full detail lives in PROJECT_STATE.md and SYSTEM_DOCS/*.

## What this system is

A private, fully-local RAG system for medical and acupuncture literature.
Access via Tailscale only. All inference runs on a single Hetzner server.

Primary outputs:
1. Word documents — treatment protocols with acupuncture points, images, page-cited sources
2. Blog articles for NRT-Amsterdam.nl — grounded in retrieved literature
3. Ad hoc Q&A — free-form questions answered against the book database, with citations

## Server

| Property | Value |
|---|---|
| Host | Hetzner CX53 — Tailscale IP 100.66.194.55 |
| vCPUs / RAM / Disk | 16 / 32 GiB / 322 GB |
| OS | Ubuntu, kernel 6.8.0-79-generic |
| Docker | 29.1.3 — use docker-compose (v1), NOT docker compose |
| Python | 3.12 system — pip install --break-system-packages |

## Running services

| Service | How | Port | State |
|---|---|---|---|
| Qdrant | Docker | 6333 (REST), 6334 (gRPC) | Up, healthy |
| Ollama | Docker | 11434 | Up, healthy — llama3.1:8b loaded |
| FastAPI web interface | systemd medical-rag-web.service | 8000 | Active |
| Transcription queue | systemd transcription-queue.service | — | Paused (videos waiting) |
| Book ingest queue | systemd book-ingest-queue.service | — | Active — Deadman processing |
| ttyd browser terminal | systemd ttyd.service | 7682 | Active (iframe bug open) |
| sync-status timer | systemd sync-status.timer | — | Active — every 5 min |

## Key paths

```
/root/medical-rag/
├── books/
│   ├── medical_literature/   ← PDF/EPUB medische boeken (Deadman, Travell, etc.)
│   ├── nrt/                  ← NRT cursusmateriaal
│   ├── qat/                  ← QAT cursusmateriaal
│   └── device/               ← PEMF/RLT documentatie
├── videos/
│   ├── nrt/                  ← NRT videos (20 in wachtrij)
│   └── qat/                  ← QAT videos (15 — transcriptie gepauzeerd)
├── data/
│   ├── transcripts/          ← Whisper JSON output per video
│   ├── extracted_images/     ← Figuren uit boeken (PNG)
│   ├── book_quality/         ← Audit rapporten + calibratie cache
│   └── image_approvals.json  ← Afbeelding goedkeuring status
├── scripts/
│   ├── transcription_queue.py    ← Whisper queue manager
│   ├── book_ingest_queue.py      ← Book ingest queue manager
│   ├── parse_pdf.py              ← PDF parsing (native + cascade OCR)
│   ├── parse_epub.py             ← EPUB parsing (3 strategieën)
│   ├── audit_book.py             ← LLM kwaliteitsaudit per boek
│   ├── ocr_preprocess.py         ← Image pre-processing (deskew, CLAHE)
│   ├── ocr_calibrate.py          ← Per-boek OCR engine kalibratie
│   ├── ocr_postcorrect.py        ← Ollama OCR post-correctie
│   ├── ingest_transcript.py      ← Transcript → Qdrant
│   ├── rag_query.py              ← RAG query engine
│   └── sync_status.py            ← GitHub state sync
├── config/
│   ├── usability_tags.json       ← AI tagging definities
│   └── ai_instructions/
│       ├── nrt_qat_bridge.md     ← NRT/QAT → literatuur koppeling
│       ├── protocol_structure.md ← Behandelprotocol structuur
│       ├── tagging_rules.md      ← Chunk tagging regels
│       ├── learning_log.md       ← AI zelflerend logboek
│       └── feedback_history.md   ← Goedgekeurde protocollen
└── web/
    └── app.py                    ← FastAPI (alle routes)
```

## Web interface routes

| Route | Status | Description |
|---|---|---|
| / | ✅ Live | Dashboard — CPU/RAM/disk/services/snel zoeken |
| /library | ✅ Live | Boeken upload + ingest + audit + pause/resume |
| /library/overview | ✅ Live | Literatuuroverzicht met usability scores |
| /search | ✅ Live | RAG zoeken + image search + streaming antwoord |
| /images | ✅ Live | Afbeeldingen browser met goedkeuring |
| /videos | ✅ Live | Video upload + transcriptie queue + pause/resume |
| /terminal | ✅ Live | Browser terminal (ttyd iframe — bug open) |
| /protocols | ✅ Live | NRT standaard protocol v3 — bekijken + bewerken + git commit |

## Qdrant collections

| Collection | Purpose | Vectors |
|---|---|---|
| medical_library | Alle medische literatuur | In opbouw (Deadman bezig) |
| nrt_qat_curriculum | NRT + QAT eigen methode | Leeg (wacht op upload) |
| device_documentation | PEMF + RLT apparatuur | Leeg (wacht op upload) |
| video_transcripts | QAT/NRT video transcripts | 6 (Connection_to_the_Brain) |

## PDF/OCR pipeline

```
Native PDF (≥50 words/page avg):
  pdfplumber detectie → Docling (do_ocr=False) → chunks → Qdrant

Scanned PDF (<15 words/page avg):
  PyMuPDF render → pre-processing (deskew/denoise/CLAHE) →
  calibratie (5 pagina's × alle engines → Ollama kiest winner) →
  cascade OCR (EasyOCR → Surya → Tesseract) → post-correctie → Qdrant

Mixed PDF (15-50 words/page):
  Per pagina: pdfplumber eerst, cascade OCR als <15 woorden
```

## Transcription pipeline

```
Upload video → queue (transcription_queue.json) →
Whisper --task translate → Engels transcript JSON →
ingest_transcript.py → Qdrant video_transcripts
```

Currently: 20 NRT + 15 QAT videos queued, PAUSED (CPU voor boeken)

## AI instructions (Lead Architect quality control)

| File | Purpose | URL |
|---|---|---|
| nrt_qat_bridge.md | NRT/QAT → literatuur koppeling | AI_INSTRUCTIONS/ |
| protocol_structure.md | Protocol structuur definitie | AI_INSTRUCTIONS/ |
| tagging_rules.md | Chunk tagging regels | AI_INSTRUCTIONS/ |
| learning_log.md | Zelflerend logboek | AI_INSTRUCTIONS/ |
| feedback_history.md | Gold standard protocollen | AI_INSTRUCTIONS/ |

## Correct terminology

| Term | Correct |
|---|---|
| Bedrijfsnaam | NRT-Amsterdam.nl |
| NRT | Neural Reset Therapy |
| QAT | Quantum Alignment Technique |
| GTR | Golgi Tendon Reflex |
| PEMF | Pulsed Electromagnetic Field |
| RLT | Red Light Therapy |

## Test status

**Laatste run:** 16-04-2026 09:46 (54.9s)  
**Uitslag:** ✅ GESLAAGD — 33/33 geslaagd, 0 overgeslagen

---

## Git / state tracking

- Repo: https://github.com/abiere/medical-rag-state (private)
- Live status: https://raw.githubusercontent.com/abiere/medical-rag-state/main/SYSTEM_DOCS/LIVE_STATUS.md
- Backlog: https://raw.githubusercontent.com/abiere/medical-rag-state/main/SYSTEM_DOCS/BACKLOG.md
- AI instructions: https://raw.githubusercontent.com/abiere/medical-rag-state/main/AI_INSTRUCTIONS/
- After every task: git add -A && git commit -m "state: ..." && git push
- Then: python3 /root/medical-rag/scripts/sync_status.py
