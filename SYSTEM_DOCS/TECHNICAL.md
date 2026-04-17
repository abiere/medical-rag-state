# TECHNICAL — Systeem Architectuur & Pipeline Referentie
> Bijgewerkt door Claude Code na relevante codewijzigingen.
> Trigger: zie CLAUDE.md § Documentatie triggers

---

## 1. Boekimport Pipeline

### 1.1 PDF Type Detectie
`scripts/parse_pdf.py` — `detect_pdf_type()`

pdfplumber samplet 5 pagina's (posities 1, 10, 50, 100, 200):

| Gemiddeld woorden/pag | Type | Parser |
|---|---|---|
| ≥ 50 | `native` | PyMuPDF — directe tekstlaag, ~92 pag/sec |
| 15–49 | `mixed` | pdfplumber per pagina + OCR cascade voor dunne pagina's |
| < 15 | `scanned` | OCR cascade op elke pagina |

### 1.2 OCR Engine Cascade
`scripts/parse_pdf.py` — `_build_engines()`

Volgorde bij scanned/mixed (snelste eerst):

| Positie | Engine | Type | Snelheid |
|---|---|---|---|
| 1 | RapidOCR (ONNX) | Lokaal | Snel (CPU) |
| 2 | EasyOCR | Lokaal | Middel |
| 3 | Surya | Lokaal | Middel |
| 4 | Tesseract | Lokaal | Snel |
| 5 | Google Vision | Cloud API | Langzaam maar meest accuraat |

**Kalibratiecache:** `data/book_quality/calibration_cache.json`
Ollama bepaalt de beste engine per boek via 5 steekproefpagina's. Resultaat gecacht op `pdf_path.stem`.

**force_ocr_engine override:** Sla kalibratie over voor atlas-stijl boeken:
```json
// config/book_classifications.json
"trail_guide": { "force_ocr_engine": "google_vision" }
```
In `parse_pdf()` wordt dit gelezen vóór `detect_pdf_type()` — kalibratie volledig overgeslagen.
**Bijwerking:** `force_ocr_engine` bypast ook `_is_mostly_image()` check — atlas pagina's worden anders allemaal overgeslagen (diagnose 2026-04-17). RapidOCR werkt als fallback wanneer Vision credentials ontbreken.

**Google Vision parallel:** Wanneer google_vision de eerste engine is, worden alle pagina's parallel verwerkt via `_parse_scanned_parallel_vision()`.
Parameters instelbaar via `config/settings.json` sectie `google_vision` (zie §5) en via /settings UI:

| Parameter | Default | Omschrijving |
|---|---|---|
| `dpi` | 300 | Renderresolutie (72–600) |
| `language_hints` | `["en"]` | Taalhinten voor Vision API |
| `min_words_per_page` | 1 | Pagina's met minder woorden gefilterd |
| `max_workers` | 8 | Parallelle ThreadPoolExecutor workers |
| `enable_confidence_scores` | false | Confidence scores berekenen |
| `confidence_threshold` | 0.0 | Min. confidence (alleen bij enable_confidence_scores=true) |
| `advanced_ocr_options` | `[]` | Extra Vision API feature flags |

Per-boek overrides in `book_classifications.json`: `vision_dpi`, `vision_min_words`.
**Vereiste:** `config/google_vision_key.json` moet aanwezig zijn — wordt gitignored maar niet meegeleverd.

**startup_scan() max retries:** Na 3 parse-mislukkingen → `status="permanently_failed"` in state.json → nooit meer ge-enqueuet. Counter `parse_retry_count` in state.json; reset bij succes.

### 1.3 Pipeline Fasen
State machine per boek: `data/ingest_cache/{book_hash}/state.json`

| Fase | Script | Output |
|---|---|---|
| 1 Parse | `parse_pdf.py` / `parse_epub.py` | `phase1_chunks.json` |
| 2 Audit | `audit_book.py` + `claude_audit.py` | `phase2_audited.json` |
| 3 Embedding | `book_ingest_queue.py` (BAAI/bge) | `phase3_vectors.npy` |
| 4 Qdrant upload | `book_ingest_queue.py` | Qdrant collectie |
| 5 Afbeelding extractie | `image_extractor.py` (background thread) | `data/extracted_images/{hash}/` |

**State resume:** Bij herstart pikt de queue op bij de laatste voltooide fase.
**Heartbeat:** state.json bijgewerkt elke pagina — queue-watchdog detecteert vastgelopen runs (BOOK_STALE=120min).

### 1.6 Afbeelding Pipeline
`scripts/image_extractor.py`

| Bron | Methode | Kwaliteit |
|---|---|---|
| PDF (pdf_cropped) | Google Vision PICTURE blocks → PyMuPDF crop 300 DPI | Normaal |
| EPUB | ebooklib directe extractie + figcaption metadata | Hoog |
| Geen | — | Overgeslagen |

**Output:** `data/extracted_images/{book_hash}/fig_PPPP_NN.png` + `images_metadata.json`
**Prioriteitssysteem:** `book_classifications.json` veld `image_priority` (high/normal/low/skip)
**Override:** `image_priority_override` — handmatig via /images pagina → "Prioriteit wijzigen"
**Extractie timing:** Draait als background thread direct na qdrant fase (overdag). Nachtrun verwerkt dit NIET meer.
**Live voortgang:** `/tmp/image_extraction_{book_hash}.json` tijdens extractie (geschreven door `_write_extraction_progress`, verwijderd bij voltooiing)
  Getoond als 5e fase-rij in /library drawer en /library/ingest widget — status: pending/running/done/not_applicable

### 1.4 Audit Mechanisme
- **Primair:** Claude Haiku API (instelbaar — `settings.json claude_api.enabled`)
- **Fallback:** Ollama llama3.1:8b — non-blocking: 3× timeout → `audit_status="skipped_ollama_timeout"` → chunk toch geëmbed
- **Retroaudit:** `/api/retroaudit/start` widget op /library/ingest — verwerkt overgeslagen chunks via Claude API
  - Doorzoekt ALLE 3 text-collecties: `medical_library`, `nrt_qat_curriculum`, `device_documentation`
  - `video_transcripts` uitgesloten (andere schema — geen KAI-tagging nodig)
  - Na succesvolle run: `chunks_skipped` in state.json gereset naar 0 → `audit_lopend` status verdwijnt
  - Per-boek reaudit (Heraudit-knop): leest `state.collection` uit state.json — niet hardcoded
- **Permanente fallback:** Chunks met lege tekst (<10 chars) → `tagged_claude_default` (k=3,a=3,i=3) zonder API-aanroep
  Chunks die 3× falen → `tagged_claude_default` automatisch. Geen chunk blijft permanent in skipped status.
- **retroaudit_skipped()** verwerkt ook chunks zonder `audit_status` (bijv. `<none>`) en gebruikt index-gebaseerde merge voor chunks zonder `chunk_id`

### 1.5 OCR Hulpmodules
| Module | Functie |
|---|---|
| `ocr_preprocess.py` | Deskew, denoise, CLAHE, Otsu binarisatie |
| `ocr_calibrate.py` | Per-boek kalibratie via Ollama, cache in `data/book_quality/` |
| `ocr_postcorrect.py` | Rule-based + Ollama correctie voor lage confidence chunks |

---

## 2. Video Transcriptie Pipeline
`scripts/transcription_queue.py`

- **Engine:** Whisper (lokaal)
- **Queue:** `/tmp/transcription_queue.json` — sequentieel (1 video tegelijk)
- **Huidige staat:** actief, 19 video's in queue
- **Skip mechanisme:**
  ```json
  // config/settings.json (gitignored)
  "transcription": {
    "skip_files": ["1.Upper_Body_Techniques.mp4"],
    "max_file_size_mb": 400
  }
  ```
- **ETA model:** `data/transcription_stats.json` — gewogen gemiddelde sec/MB (recency-weighted: w = 1/(days+1))
- **Pauze:** touch `/tmp/transcription_pause`

---

## 3. Nachtrun (nightly_maintenance.py)
Tijdvenster: `settings.json nightly.start_time/end_time` (Amsterdam tijd — server = UTC)

| Fase | Actie |
|---|---|
| Pre-checks | Schijfruimte, services check |
| Pauzeer queues | book-ingest + transcriptie gepauzeerd |
| Qdrant maintenance | Optimizer check, lege collecties |
| Data consistentie | Qdrant vs state.json vergelijken |
| Retroaudit | Overgeslagen chunks verwerken (budget proportioneel) |
| State integriteit | Fase-bestanden vs state.json valideren |
| Cleanup | `/tmp` oudere dan 7 dagen, fase-bestanden >30 dagen |
| Hervat queues | Pauze opgeheven |

**Slim tijdbudget:** `scripts/nightly_stats.py` — budgetberekening proportioneel op backlog.

---

## 4. K/A/I Classificatiesysteem
- **K** = Klinisch/weefsel | **A** = Acupunctuur | **I** = Afbeeldingen
- **1** = Primair | **2** = Ondersteunend | **3** = Achtergrond
- **Boek-niveau:** `config/book_classifications.json` (v1.1 — 35+ boeken)
- **Chunk-niveau:** Ollama/Claude override tijdens audit

Query profielen:
| Profiel | Filter | Primaire bronnen |
|---|---|---|
| Weefsel (§2) | kai_k=1 | Sobotta, Travell, AnatomyTrains, Trail Guide, Guyton |
| Acupunctuur (§3) | kai_a=1 | Deadman, Cecil-Sterman, Maciocia |
| Afbeeldingen | kai_i=1 | Sobotta, AnatomyTrains, Travell |

---

## 5. Configuratie Bestanden

| Bestand | Inhoud | Gitignored |
|---|---|---|
| `config/settings.json` | Claude API, nachtrun tijden, transcriptie skip | ✅ JA |
| `config/book_classifications.json` | K/A/I + metadata + force_ocr_engine per boek | Nee |
| `config/pipeline_diagrams.json` | Schema's tab data (auto-bijgewerkt via hook) | Nee |
| `config/ai_instructions/` | Protocol structuur, tagging regels, NRT/QAT bridge | Nee |

**settings.json structuur:**
```json
{
  "claude_api": { "enabled": true, "model": "claude-haiku-4-5-20251001", "max_workers": 10 },
  "nightly": { "start_time": "00:00", "end_time": "07:00", "image_screen_limit": 200 },
  "transcription": { "skip_files": ["..."], "max_file_size_mb": 400 },
  "google_vision": { "dpi": 300, "language_hints": ["en"], "min_words_per_page": 1,
                     "max_workers": 8, "enable_confidence_scores": false,
                     "confidence_threshold": 0.0, "advanced_ocr_options": [] }
}
```

---

## 6. Qdrant Collecties (stand 2026-04-17)

| Collectie | Vectoren | Embedding dims | Gebruik |
|---|---|---|---|
| medical_library | 2.775 | 1024 | Boekchunks (PDF/EPUB) |
| video_transcripts | 158 | 1024 | NRT/QAT transcripties |
| nrt_qat_curriculum | 546 | 1024 | QAT curriculum |
| device_documentation | 164 | 1024 | PEMF/RLT handleidingen |

**Embedding model:** `BAAI/bge-large-en-v1.5` (1024 dim) — NOOIT nomic-embed-text.

---

## 7. Services & Systemd Units

| Service | Unit | Poort | Auto-restart |
|---|---|---|---|
| FastAPI web | `medical-rag-web.service` | 8000 | Ja |
| Qdrant | `qdrant.service` | 6333 | Ja |
| Ollama | `ollama.service` | 11434 | Ja |
| Book ingest | `book-ingest-queue.service` | — | Ja |
| Transcriptie | `transcription-queue.service` | — | Ja |
| ttyd terminal | `ttyd.service` | 7682 | Ja |
| Status sync | `sync-status.timer` | — | Elke 5 min |
| Queue watchdog | `queue-watchdog.timer` | — | Elke 10 min |

**NOOIT book-ingest-queue herstarten tijdens embedding fase** — embeddings gaan verloren.
Gebruik alleen: `systemctl restart medical-rag-web` voor web-only wijzigingen.

---

## 7b. Status Systeem (single source of truth)

`web/app.py` — `_compute_book_status(state: dict) -> str`

| Status | Label | Achtergrond | Conditie |
|---|---|---|---|
| `permanent_fout` | Permanent fout | `#fee2e2` | `state.status == "permanently_failed"` |
| `fout` | Fout | `#fee2e2` | parse fase `status == "failed"` |
| `bezig` | Bezig… | `#e8f4f5` | enige fase heeft `status == "running"` |
| `in_wachtrij` | In wachtrij | `#f3f4f6` | qdrant fase nog niet `done` |
| `audit_lopend` | Audit lopend | `#fde68a` | qdrant done + `chunks_skipped > 0` |
| `afb_lopend` | Afb. lopend | `#ddf2f3` | qdrant done + geen of lege images_metadata.json |
| `afb_bezig` | Afb. bezig… | `#ddf2f3` | `/tmp/image_extraction_{hash}.json` bestaat |
| `klaar` | Klaar | `#dcfce7` | alle fasen klaar + images > 0 (of geen images verwacht) |

Prioriteit (hoog→laag): `permanent_fout > fout > bezig > in_wachtrij > audit_lopend > afb_bezig > afb_lopend > klaar`

**`_get_image_progress(book_hash)`** — leest live voortgang uit `/tmp/image_extraction_{hash}.json`.
**`_build_image_extraction_info()`** — progress FIRST dan metadata (anders stale done bij herstart).
**`klaar`** vereist: `image_source == "none"` OF `images_metadata.json` met `images > 0`.
**`afb_lopend`** ook bij lege metadata (0 images) — herextractie nodig.

Gebruikt door:
- `api_library_items` — `status` + `image_progress` veld per item
- `api_library_progress_all` — `computed_status` veld
- `api_library_progress_active` — `computed_status` veld
- `api_library_book_detail` — `computed_status` + `image_extraction` veld
- `_book_status()` — ingest pagina boekenlijst (incl. `book_hash`)

JS: `STATUS_PILLS` object + `statusPill(status)` function in `/library` pagina.
Auto-refresh: elke 15 sec als `afb_bezig` item aanwezig; stopt automatisch.
Fase 5 drawer: `not_applicable` → "N.v.t.", `running` → "Bezig" + progressbalk, `done/0` → "Geen", `done/>0` → "Klaar".

---

## 8. Web UI Pagina's (web/app.py)

| Route | Beschrijving |
|---|---|
| `/` | Dashboard — CPU/RAM/services/Qdrant stats |
| `/library` | Catalogus — legenda bovenaan (K/A/I, gebruiksprofiel, audit score), K/A/I badges met inline beschrijving (verticaal gestapeld), 6 tabs, chunk counts, delete |
| `/library/ingest` | Upload + ingest queue + voortgang widget |
| `/library/overview` | Literatuuroverzicht met audit scores |
| `/search` | RAG zoeken + afbeelding zoeken + streaming |
| `/images` | Afbeeldingen browser + goedkeuring |
| `/videos` | Upload + transcriptie queue |
| `/protocols` | NRT protocol v3 + behandelprotocollen + generator |
| `/terminal` | ttyd browser terminal (poort 7682) |

**NAV_ITEMS** is de enige source of truth voor navigatie — nooit hardcoded in individuele pagina functies.

---

## 9. Bekende Issues & Oplossingen

| Issue | Oorzaak | Oplossing |
|---|---|---|
| Trail Guide 0 chunks (opgelost) | `_is_mostly_image()` vlagde alle atlas-pagina's als image-only → OCR overgeslagen; Vision credentials ook ontbrekend | FIX: `force_ocr_engine` bypast nu `_is_mostly_image()`; RapidOCR werkt als fallback. Vision vereist `config/google_vision_key.json` (gitignored, handmatig te herstellen) |
| Infinite loop bij 0 chunks (opgelost) | `startup_scan()` slaat failed-parse boeken opnieuw in de queue | FIX: `parse_retry_count` in state.json; na 3 pogingen `permanently_failed` |
| Upper_Body 525MB hangt | Te groot voor Whisper in één pass | `transcription.skip_files` in settings.json |
| Audit overgeslagen | Ollama timeout / Claude API uit | Claude API retroaudit on-demand via /library/ingest widget |
| GitHub push geblokkeerd | Secrets in git history | git filter-branch + --force push (zie eerdere sessie) |
| 0 RAG resultaten | Verkeerde embedding model | Controleer: altijd BAAI/bge-large-en-v1.5 |
| /images leeg | Nog geen images_metadata.json (nachtrun vult aan) | Nachtrun verwerkt automatisch: `_phase_image_extract()` |

---

## 10. Schrijfregels NRT-Amsterdam.nl

1. Geen we/wij/ons/onze als subject
2. Geen fysiotherapie/fysiotherapeut → gebruik: behandelaar, reset-therapeut
3. Aanspreekvorm: je/jij/jouw — nooit u/uw
4. Bedrijfsnaam: altijd **NRT-Amsterdam.nl** (koppelteken + .nl)
5. Uitkomsten: "verbeteren", niet "verdwijnen"
6. Toon: warm, informatief, niet-zweverig, wetenschappelijk onderbouwd

---

## 11. Protocol Generator
`scripts/generate_protocol.py`

**Word output stijl (Etalagebenen v1.1 standaard):**
- Kleuren: `#1A6B72` teal | `#FCE4D6` QAT oranje | `#FFF2CC` geel
- Kolombreedtes: `1500 | 1900 | 4706 | 2200` DXA
- Secties: klachtbeeld, oorzaken, gevolgen, QAT balancering, acupunctuur, aanvullend, literatuur

**Input:** klacht naam (NL of EN) → RAG queries met K/A/I filtering → Ollama sectie-voor-sectie → Word .docx

**Referentie:** 9 gold standard protocollen beschikbaar in `data/protocols/`
