# CONTEXT — Session Loader
> Read this file at the start of every session.
> Full detail lives in SYSTEM_DOCS/BACKLOG.md and SYSTEM_DOCS/LIVE_STATUS.md

---

## What this system is

Private, fully-local RAG system for medical and acupuncture literature.
Access via Tailscale only (100.66.194.55). All inference on Hetzner server.

Primary outputs:
1. Word documents — behandelprotocollen with acupuncture points, images, citations
2. Blog articles for NRT-Amsterdam.nl — grounded in retrieved literature
3. Ad hoc Q&A — questions answered from book database with citations

---

## Server

| Property | Value |
|---|---|
| Host | Hetzner CX53 — Tailscale IP 100.66.194.55 |
| vCPUs / RAM / Disk | 16 / 32 GiB / 322 GB |
| OS | Ubuntu 24.04 |
| Python | 3.12 — pip install --break-system-packages |
| Node.js | 18+ — npm install -g docx |

---

## Running services

| Service | Port | State |
|---|---|---|
| FastAPI (medical-rag-web) | 8000 | ✅ Active |
| Qdrant | 6333 | ✅ Healthy |
| Ollama (llama3.1:8b) | 11434 | ✅ Active |
| book-ingest-queue | — | ✅ Active — Travell+Simons bezig |
| transcription-queue | — | ⏸ Gepauzeerd (20 NRT + 15 QAT wachten) |
| ttyd terminal | 7682 | ✅ Active (iframe bug open) |
| sync-status.timer | — | ✅ Active elke 5 min |
| queue-watchdog.timer | — | ✅ Active elke 10 min |

---

## Book Ingest Queue (huidige staat)

| Slot | Boek | Status |
|---|---|---|
| Processing | Travell+Simons Vol 1 (63MB) | Bezig — native PDF via Docling |
| Queue #1 | Trail Guide to the Body (108MB) | Wachten |
| Queue #2 | Deadman — Manual of Acupuncture (47MB) | Wachten (opnieuw na audit fix) |

Deadman had 987 chunks aangemaakt maar audit blokkeerde embedding.
Fix: audit non-blocking bij Ollama timeout. Deadman wordt opnieuw verwerkt.

---

## Qdrant Collections

| Collection | Vectors | Status |
|---|---|---|
| medical_library | 2 (test only) | Travell+Simons vult dit op |
| video_transcripts | 6 | Connection_to_the_Brain chunks |
| nrt_qat_curriculum | 0 | Wacht op QAT curriculum upload |
| device_documentation | 0 | Wacht op PEMF/RLT docs |

---

## Key paths

/root/medical-rag/
├── books/medical_literature/     ← Deadman, Travell+Simons, Trail Guide PDFs
├── videos/nrt/ + qat/            ← 20+15 videos (gepauzeerd)
├── data/
│   ├── transcripts/              ← Whisper JSON output
│   ├── acupuncture_points/       ← 476 Deadman PNG afbeeldingen + point_index.json
│   ├── extracted_images/         ← Figuren uit boeken
│   ├── book_quality/             ← Audit rapporten + calibratie_cache.json
│   ├── protocols/                ← Gegenereerde protocollen + metadata JSON
│   └── image_approvals.json
├── config/
│   ├── book_classifications.json ← K/A/I classificaties per boek (HYBRID systeem)
│   ├── usability_tags.json
│   └── ai_instructions/
│       ├── nrt_qat_bridge.md
│       ├── protocol_structure.md
│       ├── tagging_rules.md      ← K/A/I systeem toegevoegd
│       ├── meridian_mapping.md   ← Deadman standaard + QAT conversie
│       ├── learning_log.md       ← OCR learning log
│       ├── feedback_history.md
│       └── nrt_standaard_protocol_v3.md ← Volledig behandelprotocol v3
├── scripts/
│   ├── transcription_queue.py    ← Whisper queue
│   ├── book_ingest_queue.py      ← Book ingest met heartbeat + startup guard
│   ├── parse_pdf.py              ← Native: pdfplumber+Docling / Scan: cascade OCR
│   ├── parse_epub.py             ← EPUB parsing
│   ├── ocr_preprocess.py         ← Deskew, denoise, CLAHE, Otsu
│   ├── ocr_calibrate.py          ← Per-boek OCR kalibratie via Ollama
│   ├── ocr_postcorrect.py        ← Ollama OCR post-correctie
│   ├── audit_book.py             ← LLM audit (non-blocking bij timeout)
│   ├── normalize_points.py       ← Meridiaanpunt normalisatie → Deadman standaard
│   ├── protocol_metadata.py      ← Literatuur tracking + earmarking per protocol
│   ├── generate_protocol.py      ← Protocol generator (RAG → Ollama → Word)
│   ├── ingest_transcript.py      ← Transcript → Qdrant
│   ├── rag_query.py              ← RAG query engine
│   ├── queue_watchdog.py         ← Herstart stale queues (BOOK=120min, TRANS=30min)
│   ├── nightly_maintenance.py    ← Consistentie check + retroactive audit
│   └── sync_status.py            ← GitHub state sync (retry 3x)
└── web/app.py                    ← FastAPI alle routes

---

## Web Interface Routes

| Route | Status | Beschrijving |
|---|---|---|
| / | ✅ Live | Dashboard — CPU/RAM/services/vectoren |
| /library | ✅ Live | Boeken upload + ingest + pause/resume + heraudit |
| /library/overview | ✅ Live | Literatuuroverzicht met K/A/I scores |
| /search | ✅ Live | RAG zoeken + image search + streaming |
| /images | ✅ Live | Afbeeldingen browser + goedkeuring |
| /videos | ✅ Live | Video upload + transcriptie + pause/resume |
| /protocols | ✅ Live | NRT standaard protocol v3 + behandelprotocollen |
| /terminal | ✅ Live | ttyd iframe (bug: laadt niet) |

---

## PDF/OCR Pipeline

Native PDF (≥50 words/page):
  pdfplumber detectie → Docling (do_ocr=False) → chunks → Qdrant

Scanned PDF (<15 words/page):
  PyMuPDF render → ocr_preprocess (deskew/CLAHE) →
  ocr_calibrate (5 pagina's × alle engines → Ollama kiest winner) →
  cascade OCR (EasyOCR → Surya → Tesseract) →
  ocr_postcorrect (Ollama) → chunks → Qdrant

Mixed PDF: per pagina native of cascade

Audit: Ollama steekproef per boek. Non-blocking: bij 3× timeout →
  audit_status="skipped_ollama_timeout" → chunk nog steeds ingested
  Nightly maintenance heraudit deze chunks (max 200/nacht)

---

## K/A/I Classificatiesysteem (Hybride)

Boek-niveau (statisch): config/book_classifications.json
  K=Klinisch/weefsel, A=Acupunctuur, I=Afbeelding
  1=Primair, 2=Ondersteunend, 3=Achtergrond

Chunk-niveau (dynamisch): Ollama override bij audit
  chunk_k_override, chunk_a_override — alleen bij significante afwijking

Query profielen:
  §2 Weefsel: filter kai_k=1 → Sobotta, Travell, AnatomyTrains
  §3 Acupunctuur: filter kai_a=1 → Deadman (primair), Cecil-Sterman, Maciocia
  Afbeeldingen: filter kai_i=1 → Sobotta, AnatomyTrains, Travell

---

## Acupunctuurpunten

476 Deadman PNG afbeeldingen in /data/acupuncture_points/
Index: point_index.json — alle punten gemapped naar filepath + meridiaan
Bladder Channel samengevoegd (was twee mappen)
Normalisatie: normalize_points.py → alle notaties naar Deadman standaard
QAT→Deadman: HT→HE, KI→KID, LV→LIV, PC→P, TW→SJ

QAT Balancepunten (definitief April 2026):
  CV=SP-21r, GV=SP-21l, BL=BL-58, SJ=SJ-5, KID=KID-4, P=P-6,
  GB=GB-37, ST=ST-40, LI=LI-6, SI=SI-7, LU=LU-7, SP=SP-4,
  HE=HE-5, LIV=LIV-5

---

## Protocol Generator

generate_protocol.py — volledig gebouwd:
  Input: klachtnaam (NL of EN)
  RAG queries met K/A/I filtering (BAAI/bge-large-en-v1.5 embeddings)
  Sectie voor sectie via Ollama (llama3.1:8b)
  Output: Word .docx via Node.js docx library

Word stijl (exact Etalagebenen v1.1):
  Kleuren: #1A6B72 (teal), #FCE4D6 (oranje QAT), #FFF2CC (geel)
  Kolommen: 1500|1900|4706|2200 DXA
  Structuur: 32 tabellen (zelfde als gold standard)

Gold standard protocollen aanwezig (9 stuks):
  Etalagebenen v1.1, OMD v1.5, Vertigo v2.6, Hoofdpijn v1,
  Artrose v1, Hooikoorts v4, Mycobacterium v1, Sclerodermie v1,
  Systemische Sclerodermie v1

Literatuur tracking: protocol_metadata.py
  Elke gegenereerde protocol → metadata.json met gebruikte bronnen
  Bij nieuwe literatuur → automatisch earmarken (needs_review=true)
  /protocols pagina toont oranje badge + reden

---

## Embedding Model

BAAI/bge-large-en-v1.5 (1024 dimensies)
Gebruikt voor ZOWEL ingest ALS zoekopdrachten
NIET nomic-embed-text (verkeerd model — veroorzaakte 0 RAG resultaten)

---

## Correcte Terminologie

NRT-Amsterdam.nl (altijd met koppelteken + .nl)
NRT = Neural Reset Therapy
QAT = Quantum Alignment Technique
GTR = Golgi Tendon Reflex
PEMF = Pulsed Electromagnetic Field
RLT = Red Light Therapy

---

## Git / State Tracking

Repo: https://github.com/abiere/medical-rag-state (private)
/root/medical-rag IS de state repo (zelfde remote)
/root/medical-rag-state is een symlink naar /root/medical-rag

Na elke taak:
  cd /root/medical-rag && \
  git add -A && \
  git commit -m "state: [beschrijving]" && \
  git push
  python3 /root/medical-rag/scripts/sync_status.py
