# CONTEXT — Session Loader
> Read at start of every session. Full detail in BACKLOG.md + LIVE_STATUS.md.

## What this system is
Private, fully-local RAG system for medical/acupuncture literature.
Tailscale only (100.66.194.55). All inference on Hetzner server.
Outputs: Word behandelprotocollen | NRT-Amsterdam.nl blog | Ad hoc Q&A

## Server
| Property | Value |
|---|---|
| Host | Hetzner CX53 — Tailscale 100.66.194.55 |
| vCPUs / RAM / Disk | 16 / 32 GiB / 322 GB |
| Python | 3.12 — pip install --break-system-packages |
| Node.js | 18+ — npm install -g docx |

## Running services
| Service | Port | State |
|---|---|---|
| FastAPI (medical-rag-web) | 8000 | ✅ Active |
| Qdrant | 6333 | ✅ Healthy |
| Ollama (llama3.1:8b) | 11434 | ✅ Active |
| book-ingest-queue | — | ✅ Active |
| transcription-queue | — | ⏸ Paused (20 NRT + 15 QAT waiting) |
| ttyd terminal | 7682 | ✅ Active |
| sync-status.timer | — | ✅ Every 5 min |
| queue-watchdog.timer | — | ✅ Every 10 min (BOOK=120min, TRANS=30min) |

## Book Ingest Queue
| Slot | Book | Status |
|---|---|---|
| Processing | Travell+Simons Vol 1 (63MB) | Native PDF via Docling |
| Queue #1 | Trail Guide to the Body (108MB) | Waiting |
| Queue #2 | Deadman — Manual of Acupuncture (47MB) | Re-queued after audit fix |

Note: Deadman had 987 chunks but audit blocked embedding (Ollama timeout).
Fix applied: audit non-blocking. Deadman re-queued for clean reprocessing.

## Qdrant Collections
| Collection | Vectors | Notes |
|---|---|---|
| medical_library | 2 (test only) | Filling as books complete |
| video_transcripts | 6 | Connection_to_the_Brain |
| nrt_qat_curriculum | 0 | Awaiting QAT upload |
| device_documentation | 0 | Awaiting PEMF/RLT docs |

## Key paths
/root/medical-rag/
├── books/medical_literature/     ← PDFs being ingested
├── videos/nrt/ + qat/            ← 35 videos (paused)
├── data/
│   ├── transcripts/              ← Whisper JSON
│   ├── acupuncture_points/       ← 476 Deadman PNGs + point_index.json
│   ├── extracted_images/         ← Book figures
│   ├── book_quality/             ← Audit reports + calibration_cache.json
│   ├── protocols/                ← Generated protocols + metadata JSON
│   └── image_approvals.json
├── config/
│   ├── book_classifications.json ← K/A/I per book (30+ books)
│   └── ai_instructions/
│       ├── nrt_standaard_protocol_v3.md ← Full NRT treatment protocol
│       ├── meridian_mapping.md   ← Deadman standard + QAT conversion
│       ├── tagging_rules.md      ← K/A/I system
│       ├── learning_log.md       ← OCR learning log
│       └── feedback_history.md
├── scripts/
│   ├── transcription_queue.py
│   ├── book_ingest_queue.py      ← Heartbeat + startup guard
│   ├── parse_pdf.py              ← Native: Docling / Scan: cascade OCR
│   ├── parse_epub.py
│   ├── ocr_preprocess.py         ← Deskew, denoise, CLAHE, Otsu
│   ├── ocr_calibrate.py          ← Per-book OCR calibration via Ollama
│   ├── ocr_postcorrect.py        ← Ollama OCR post-correction
│   ├── audit_book.py             ← Non-blocking audit (skips on timeout)
│   ├── normalize_points.py       ← All notations → Deadman standard
│   ├── protocol_metadata.py      ← Literature tracking + earmarking
│   ├── generate_protocol.py      ← Protocol generator (RAG→Ollama→Word)
│   ├── ingest_transcript.py
│   ├── rag_query.py
│   ├── queue_watchdog.py
│   ├── nightly_maintenance.py    ← Consistency check + retroactive audit
│   └── sync_status.py            ← GitHub sync (3 retries)
└── web/app.py                    ← FastAPI all routes

## Web Interface Routes
| Route | Status | Description |
|---|---|---|
| / | ✅ | Dashboard — CPU/RAM/services/vectors |
| /library | ✅ | Upload + ingest + pause/resume + progress |
| /library/overview | ✅ | Literature overview with K/A/I scores |
| /search | ✅ | RAG search + image search + streaming |
| /images | ✅ | Image browser + approval |
| /videos | ✅ | Upload + transcription + pause/resume |
| /protocols | ✅ | NRT protocol v3 + behandelprotocollen + generator |
| /terminal | ✅ | ttyd browser terminal (port 7682) |

## PDF/OCR Pipeline
Native (≥50 words/page): pdfplumber detect → Docling (do_ocr=False)
Scanned (<15 words/page): PyMuPDF → ocr_preprocess → ocr_calibrate →
  cascade OCR (EasyOCR → Surya → Tesseract) → ocr_postcorrect
Mixed: per-page decision

Audit: Ollama sampling. Non-blocking: 3× timeout →
  audit_status="skipped_ollama_timeout" → chunk still embedded
  Retroactive audit: nightly_maintenance.py (max 200 chunks/night)

## K/A/I Classification (Hybrid)
Book-level static: config/book_classifications.json
Chunk-level dynamic: Ollama override during audit

Protocol query profiles:
  §2 Tissue: kai_k=1 → Sobotta, Travell, AnatomyTrains, Guyton, Trail Guide
  §3 Acupuncture: kai_a=1 → Deadman (primary), Cecil-Sterman, Maciocia
  Images: kai_i=1 → Sobotta, AnatomyTrains, Travell

## Acupuncture Points
476 Deadman PNGs in /data/acupuncture_points/ — point_index.json
normalize_points.py: all notations → Deadman standard
QAT→Deadman: HT→HE, KI→KID, LV→LIV, PC→P, TW→SJ

QAT Balance Points (verified April 2026 — DO NOT CHANGE):
  CV=SP-21r, GV=SP-21l, BL=BL-58, SJ=SJ-5, KID=KID-4, P=P-6
  GB=GB-37, ST=ST-40, LI=LI-6, SI=SI-7, LU=LU-7, SP=SP-4
  HE=HE-5, LIV=LIV-5

## Protocol Generator
generate_protocol.py — fully built:
  Input: klacht name (NL or EN)
  RAG queries with K/A/I filtering (BAAI/bge-large-en-v1.5)
  Section-by-section via Ollama
  Output: Word .docx via Node.js docx library

Word style (exact Etalagebenen v1.1):
  Colors: #1A6B72 (teal), #FCE4D6 (orange), #FFF2CC (yellow)
  Columns: 1500|1900|4706|2200 DXA

9 gold standard protocols available as reference.
Literature tracking: protocol_metadata.py
Earmarking: auto-flag when new literature added (needs_review=true)

## Critical: Embedding Model
BAAI/bge-large-en-v1.5 (1024 dims) — used for BOTH ingest AND search
NOT nomic-embed-text (caused 0 RAG results)

## Terminology
NRT-Amsterdam.nl (always with hyphen + .nl)
NRT=Neural Reset Therapy | QAT=Quantum Alignment Technique
GTR=Golgi Tendon Reflex | PEMF=Pulsed Electromagnetic Field | RLT=Red Light Therapy
Deadman notation: HE | KID | LIV | P | SJ (not HT/KI/LV/PC/TW)

## Git / State Tracking
Repo: https://github.com/abiere/medical-rag-state (private)
/root/medical-rag IS the state repo (same remote)
/root/medical-rag-state is a symlink to /root/medical-rag

After every task:
  cd /root/medical-rag && git add -A && \
  git commit -m "state: [description]" && git push
  python3 /root/medical-rag/scripts/sync_status.py

---

## Test status

**Laatste run:** 16-04-2026 11:30 (62.6s)  
**Uitslag:** ✅ GESLAAGD — 33/33 geslaagd, 0 overgeslagen
