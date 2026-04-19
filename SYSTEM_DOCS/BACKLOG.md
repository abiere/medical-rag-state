# BACKLOG — NRT-Amsterdam.nl
> Bijgewerkt: 2026-04-19 | Inventarisatie sessie — geen herstel uitgevoerd
> Volgende architect-sessie pakt dit op.
> Open issues: zie OPEN_ISSUES.md | Design queue: zie DESIGN_QUEUE.md

---

## 🔴 EERST — framework & governance

- [ ] **Framework voor verdere werkwijze — door architect uit te werken**
  - 5-stappen werkwijze technisch borgen (Design → Goedkeuring → Implementatie → Review → Afsluiting)
  - LESSONS_LEARNED.md structuur + update-triggers
  - Feedback loop Claude Code → Architect (zie ISSUE-012)
  - Drive-sync voor design-documenten (zie ISSUE-014)
  - Governance-document: DESIGN-Governance-v1 (zie DESIGN_QUEUE.md)

- [ ] **CLAUDE.md drift structureel oplossen**
  - ISSUE-001: Qdrant-counts stale (medical_library 10428 vs 17522, qat_video_transcripts 0 vs 443)
  - ISSUE-002: Verwijzing naar medical-rag-sync.timer (bestaat niet — is sync-status.timer)
  - CLAUDE.md wordt niet automatisch bijgewerkt door sync-scripts
  - Oplossing: handmatige update OF automatische sync opnemen in sync_context.py

---

## 🟠 DAN — data & pipeline herstel

Zie OPEN_ISSUES.md voor volledig issue-formaat en root cause analyses.

- [ ] **ISSUE-004** — Transcriptie→ingestion pipeline herstellen voor 13 NRT video's
  - `_partNNN.json` bestanden worden niet samengevoegd naar `{video}.json`
  - Ingest-stap verwacht enkelvoudig JSON — faalt altijd voor gesegmenteerde video's
  - Fix: merge-stap toevoegen in transcription_queue.py of ingest_transcript.py aanpassen

- [ ] **ISSUE-005** — 4 permanently failed ingests opruimen
  - FlexBeam Knees, Neck, Stomach + Levels Mat
  - Watchdog herstart queue elke minuut onnodig (60× per uur logvervuiling)
  - Fix: permanently_failed entries verwijderen OF watchdog "clean exit = geen restart" laten herkennen

- [ ] **ISSUE-006** — 3 boeken in state.json maar niet in Qdrant
  - Orthopedic Physical Assessment, Touch for Health, Bates Guide
  - Diagnose: root cause onbekend — eerst onderzoeken
  - Mogelijk: parse opnieuw starten na diagnose

- [ ] **ISSUE-007** — 1 orphan state.json (Levels Mat, Pillow, Pen.pdf — ook permanently_failed)
  - book_classifications.json heeft geen filename_pattern voor dit boek

- [ ] **ISSUE-009** — Applied Kinesiology title = 'APPLIED KINESIOLOGY' (all-caps, niet manually_reviewed)
  - Corrigeren via ✏ knop in /library

- [ ] **ISSUE-016** — data/ingest_cache/ wordt niet gecommit door sync-timer
  - 45 uncommitted bestanden stapelen op tussen commits
  - Architect beslissing nodig: commit ingest_cache wel/niet

---

## 🟡 ONTWERP — design-queue

Zie DESIGN_QUEUE.md voor volledige beschrijving en afhankelijkheden.

Volgorde (afhankelijkheidsvolgorde, architect beslist prioriteit):

1. DESIGN-Architectuur-v1 — fundament, alle anderen wachten hierop
2. DESIGN-Governance-v1 — werkwijze borgen
3. Migratie NRT server bestanden (3 designs, 51 bestanden totaal)
4. DESIGN-Import-v1
5. DESIGN-Videos-v1
6. DESIGN-Afbeeldingen-v1
7. DESIGN-Protocollen-v1
8. DESIGN-Nachtbatch-v1
9. DESIGN-API-v1

---

## 🟢 VERBETERINGEN — laag prioriteit

- [ ] **ISSUE-013** — ttyd iframe laadt niet in /terminal pagina
- [ ] **ISSUE-014** — Google Drive MCP tools niet beschikbaar
- [ ] **ISSUE-015** — medical-rag-maintenance.service en medical-rag-tests.service tonen als "failed"
- [ ] **ISSUE-011** — Boekweergave inconsistent over /library, /ingest, /images
- [ ] **Playwright regressietests** — 8 nav-items + kritieke pagina's automatisch testen
- [ ] **gstack installeren** — `/cso`, `/investigate`, `/careful`, `/guard` skills

---

## 🧠 KENNISSYNTHESELAAG — gepland (niet gestart)

### Fase 1 — Appendices (eerste concrete deliverable)

- [ ] Appendix-Autoimmuun.md — HPA-as, pijnappelklier, hypofyse, thymus
- [ ] Appendix-NervusVagus.md — vagustonus, polyvagale theorie
- [ ] Appendix-Endocrien.md — hypofyse, bijnier, schildklier
- [ ] Appendix-Sympathicus.md — SNS hyperactiviteit

### Fase 2 — QAT en NRT samenvattingen

- [ ] QAT-Samenvatting.md — balancepunten, visualisatie, werkwijze (handmatig schrijven)
- [ ] NRT-Samenvatting.md — spiergroepen, resetvolgorde, techniek (handmatig schrijven)

### Fase 3 — Domain-Klinisch.md (kennisgeheugen)

- [ ] Domain-Klinisch.md aanmaken — skeleton aanwezig, handmatig in te vullen met Axel

### Fase 4 — /protocollen UI uitbreiden

- [ ] Tabblad "Kennisbank" toevoegen
- [ ] Protocolgenerator appendix-triggerlogica
- [ ] QAT/NRT summaries als context meesturen

### Fase 5 — Zelflerende kennisgraaf (GEPARKEERD)

BESLUIT: Nu niet bouwen. Opnieuw evalueren na Fase 1–3.

---

## ⚙️ Hardware (gepland)

- [ ] **Mac Studio M5 Max** — verwacht WWDC juni 2026
  ~€2.299–€2.499 | 96/128GB RAM | 546 GB/s bandbreedte
  Hetzner CX53 blijft als backup/Tailscale endpoint

---

## 🟢 IDEEËN — nog niet besloten

- [ ] Interactieve afbeelding selectie UI
- [ ] Protocol regeneratie per sectie
- [ ] Protocol versie management
- [ ] Blog generator NRT-Amsterdam.nl (RAG → Ollama → WordPress MCP)
- [ ] Visueel zoeken (upload afbeelding → vergelijkbare)
- [ ] Officiële Deadman digitale versie (DRM-vrij via Eastland Press)
- [ ] Protocol pre-validatie (Ollama checkt dekking voor generatie)
- [ ] Consistentie guardian cross-collectie
- [ ] /search pagina verbeteren (RAG query interface UI)
- [ ] Protocol taal optie (standaard NL, optie EN)
- [ ] Streaming protocol generatie (SSE progress per sectie)

---

---

## ✅ AFGEROND

### ✅ Afgerond — 2026-04-19 (sessie 27 — inventarisatie)

- [x] **Inventarisatie open state 2026-04-19** — geen herstel, alleen vastleggen
  - INVENTORY_INDEX.md aangemaakt
  - DATA_SNAPSHOT_2026-04-19.md aangemaakt (Qdrant, state.json, transcripts, video's)
  - OPEN_ISSUES.md aangemaakt (ISSUE-001 t/m ISSUE-016)
  - DESIGN_QUEUE.md aangemaakt (3 bestaande, 7 ontbrekende designs)
  - BACKLOG.md herschreven (structuur vereenvoudigd, issues verplaatst naar OPEN_ISSUES.md)

### ✅ Afgerond — 2026-04-19 (sessie 26)

- [x] **Fix 1: _is_bad_title() in metadata merge — foute titels overgeslagen**
      - Root cause: merge-logica sloeg no slechte titels over (ALL CAPS, 1-woord, telefoonnummers)
      - `_is_bad_title()` functie toegevoegd: isupper+kort, 1-woord-kort, regex telefoonnummer, copyright
      - `_merge_metadata()` past check toe voor title-veld, logt overgeslagen waarden
      - Anatomy Trains: ANATOMY TRAINS → Anatomy Trains
      - Sobotta Tables: Sobotta → Sobotta Lerntabellen Anatomie Muskeln, Gelenke und Nerven

- [x] **Fix 2: 4 dode device/ cache-entries verwijderd**
      - FlexBeam Neck/Knees/Stomach + Levels Mat entries in books/device/ (niet op disk)
      - Levende entries in rlt_flexbeam/ en pemf_qrs/ onaangeroerd

- [x] **Fix 3: 3 NRT ghost classificaties verwijderd uit book_classifications.json**
      - body_keeps_score, emotion_code, body_code — geen cache-entries, geen vectoren
      - Ingest cache was al schoon; alleen book_classifications.json opgeruimd
      - Tests: 39/39 GESLAAGD

### ✅ Afgerond — 2026-04-19 (sessie 25)

- [x] **Fix 1: manually_reviewed flag bij handmatige invoer**
      - `POST /api/library/book/{hash}/metadata-manual`: zet nu `manually_reviewed=True`

- [x] **Fix 2: Banner filter — sluit manually_reviewed boeken uit**
      - `needs_attention = not has_isbn AND not manually_reviewed AND not (has_minimum_data AND manual_entry)`

- [x] **Fix 3: Backfill 14 bestaande entries**
      - 14 boeken gemarkeerd met `manually_reviewed=True` (method='manual' + ASIN-boeken)

### ✅ Afgerond — 2026-04-19 (sessie 24)

- [x] **Feature: "Handmatig invoeren" knop in amber ISBN banner**
      - togglebaar formulier per rij, 6 velden, `POST /api/library/book/{hash}/metadata-manual` endpoint
      - Tests: 39/39 GESLAAGD

### ✅ Afgerond — 2026-04-19 (sessie 23)

- [x] **Bugfix: Firecrawl scrape mislukt — FirecrawlApp is lege alias**
      - Fix: `V1FirecrawlApp` (heeft `scrape_url`, `V1ScrapeResponse` response)
      - Tests: 39/39 GESLAAGD

### ✅ Afgerond — 2026-04-19 (sessie 22)

- [x] **Firecrawl integratie — bot-detectie bypass voor Amazon + ISBNsearch**
      - `pip install firecrawl-py` — v4.22.2 geïnstalleerd
      - Tests: 39/39 GESLAAGD

### ✅ Afgerond — 2026-04-19 (sessie 21)

- [x] **Feature 1: Banner toont alleen boeken zonder ISBN**
- [x] **Feature 2: ASIN lookup via Amazon**
- [x] **Bugfix: surrogate pair unicode error**
      - Tests: 39/39 GESLAAGD

### ✅ Afgerond — 2026-04-19 (sessie 20)

- [x] **GitHub sync observability: diagnose + /api/status/sync + nav badge**
      - Added `data/sync_errors.log`, GET `/api/status/sync`, sync badge in nav
      - CLAUDE.md bijgewerkt met sync health check sectie
      - Tests: 39/39 GESLAAGD

### ✅ Afgerond — 2026-04-19 (sessie 19)

- [x] **JS SyntaxError bugfix /library + structurele event handler standaard**
      - Root cause: `oninput="...replace(/[^0-9]/g,'')"` — `''` als twee JS string literals
      - Structureel: CLAUDE.md "HTML event handler standaard" (uitgebreid naar alle on* handlers)
      - Test toegevoegd: `test_no_quotes_in_event_handler_attrs`
      - Tests: 39/39 GESLAAGD

### ✅ Afgerond — 2026-04-19 (sessie 18)

- [x] **test_acupuncture.pdf volledig verwijderd** (uncommitted deletion aanwezig in git)
      - 2 Qdrant vectors, cache, images, file, classifications entry verwijderd

### ✅ Afgerond — 2026-04-18 (sessie 17)

- [x] **ISBNsearch.org scraper + Library of Congress API**
- [x] **ISBN-10 → ISBN-13 conversie + copy-paste friendliness**
- [x] **FIELD_PRIORITY bijgewerkt met 5 bronnen**
- [x] **ISBN invoerveld auto-strip + server-side cleanup**
      - 38/38 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 16)

- [x] **TypeError: authors.substring is not a function** — fix + backfill 32 entries
- [x] **Metadata status van /instellingen naar /library** — amber banner
      - 38/38 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 15)

- [x] **Handmatige ISBN invoer in Schema's tab**
- [x] **PDF bekijken + externe links**
      - 38/38 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 14)

- [x] **Bug fixes book_metadata_vision.py (3 bugs)** — EPUB rendering, Google Books 429, JSON truncatie
- [x] **`backfill_all_metadata()` + `--all` vlag** — 24/35 volledig (isbn+title+year)
- [x] **Schema's tab: boek metadata status tabel**
- [x] **AI Modellen tab: volgorde op `order` veld**
      - 38/38 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 13)

- [x] **Pipeline A: boek metadata extractie via Gemini Vision + Google Books + OpenLibrary**
      - `scripts/book_metadata_vision.py` aangemaakt
      - 38/38 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 12)

- [x] **"Claude API audit" card verwijderd uit /settings**
      - 37/37 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 11)

- [x] **ANTHROPIC_API_KEY toegevoegd aan systemd service**

### ✅ Afgerond — 2026-04-18 (sessie 10)

- [x] **AI provider abstraction layer Part 2 — volledige migratie**
      - 6 scripts gemigreerd naar AIClient
      - AI Modellen UI gebouwd in `/settings`
      - AI_STATUS.md auto-gegenereerd
      - 37/37 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 9)

- [x] **AI provider abstraction layer Part 1 — scripts/ai_client.py + config/ai_settings.json**
      - 37/37 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 8)

- [x] **GEMINI_API_KEY toegevoegd aan server + Gemini SDK geïnstalleerd**

### ✅ Afgerond — 2026-04-18 (sessie 7)

- [x] **book_classifications.json opschoning — 8 ghost entries verwijderd**
- [x] **Pattern fixes bates + maciocia_foundations**
      - 37/37 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 6)

- [x] **Fix 1 — Prioriteit dropdown /images** — Unicode mismatch opgelost
- [x] **Fix 2 — Touch for Health in verkeerde sectie** — library_category gecorrigeerd
- [x] **Fix 3 — Queue stubs opruimen**

### ✅ Afgerond — 2026-04-18 (sessie 5)

- [x] **Legacy cache cleanup + herstel** — 42 entries verwijderd + 37 hersteld
- [x] **PDF date parsing bug fix** — `D:20` → correcte year-extractie
- [x] **Transcription queue test fix** — assertIn(['active', 'inactive', 'activating'])
      - 36/36 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 4)

- [x] **ISBN-gebaseerde duplicaatdetectie in ingest pipeline** — Fase 0 (4 delen)
      - 36/36 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessie 3)

- [x] **Catalogus sectie-indeling, titels en publicatiejaren** — /library volledig herzien
      - 36/36 tests geslaagd

### ✅ Afgerond — 2026-04-18 (sessies)

- [x] **sync_context.py + post-commit hook** — CONTEXT.md auto-genereert
- [x] **Structurele fix onclick XSS** — alle HIGH RISK f-string onclick vervangen
- [x] **Structurele fix onclick LOW RISK** — alle resterende f-string onclick naar data-*
- [x] **Duplicaatdetectie feature** — amber banner, "Bewaar dit" knoppen
- [x] **"Bewaar dit" knop feedback + timeout**

### ✅ Afgerond — 2026-04-17 (Domain MDs kennissyntheselaag)

- [x] **Domain-QAT.md aangemaakt** — /data/domain_mds/Domain-QAT.md
- [x] **Domain-NRT.md aangemaakt** — /data/domain_mds/Domain-NRT.md
- [x] **Domain-RLT.md aangemaakt** — /data/domain_mds/Domain-RLT.md
- [x] **Domain-PEMF.md aangemaakt** — /data/domain_mds/Domain-PEMF.md
- [x] **Domain-Klinisch.md skeleton aangemaakt**

### ✅ Afgerond — 2026-04-17 (Opdracht B: UI collectie-architectuur)

- [x] SECTION_MAP vervangen (3 → 5 secties)
- [x] CAT_LABELS + CAT_ORDER bijgewerkt
- [x] ingest_transcript.py dynamische collectie-routing

### ✅ Afgerond — 2026-04-17 (Opdracht A: Collectie-architectuur migratie)

- [x] **6 nieuwe Qdrant collecties aangemaakt** (1024-dim)
- [x] **1015 chunks gemigreerd** (vector-copy, geen re-embedding)
- [x] **46 state.json bestanden bijgewerkt** met nieuwe collection-naam
- [x] **book_classifications.json volledig geclassificeerd** — 0 entries met `?`
- [x] **Legacy collecties verwijderd:** nrt_qat_curriculum, device_documentation, video_transcripts

### ✅ Afgerond — 2026-04-17 (/images pagina + figcaption + image pipeline)

- [x] /images pagina volledig herschreven (lazy loading, lightbox, multi-select)
- [x] figcaption extractie verbeterd (474/531 Anatomy Trains, 720/1449 Bates)
- [x] image_extractor.py (Vision API + PyMuPDF + ebooklib)
- [x] Goedkeuringslogica verwijderd, prioriteitssysteem geïntroduceerd
- [x] 7 UI verbeteringen /images pagina

### ✅ Afgerond — 2026-04-17 (diverse fixes + refactors)

- [x] Library speed fix (asyncio.gather + 10s TTL cache)
- [x] Video ffmpeg splitting (_split_video_if_needed)
- [x] Status systeem overhaul (_compute_book_status, 7 statussen)
- [x] Retroaudit multi-collection fix
- [x] vision bbox image extraction rewrite
- [x] audit fallback + retroaudit fix — 2773 chunks getagd
- [x] audit_score + category_scores fix (Deadman + Travell)
- [x] Trail Guide loop fix + max_retries
- [x] Google Vision credentials hersteld
- [x] Documentatie overhaul (CONTEXT/TECHNICAL/OPERATIONS herschreven)

### ✅ Afgerond — 2026-04-16

- [x] Parse speed fix (PyMuPDF native, RapidOCR scanned — 377× sneller)
- [x] Pipeline rebuild (state machine, watchdog, nightly maintenance)
- [x] OCR cascade (RapidOCR → EasyOCR → Surya → Tesseract → Google Vision)
- [x] K/A/I classificatiesysteem
- [x] Protocol generator
- [x] 476 Deadman punt afbeeldingen + point_index.json
- [x] MemPalace + Playwright MCP servers
- [x] nrt-ui-standards skill
- [x] Hooks (py_syntax_check, security_check, mempalace_save)
- [x] FastAPI web interface volledig (9 routes)
- [x] Live status sync GitHub (LIVE_STATUS.md elke 5 min)
