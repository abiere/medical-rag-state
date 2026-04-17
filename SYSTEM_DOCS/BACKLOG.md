# BACKLOG — Medical RAG
> Bijgewerkt door Claude Code na elke sessie.
> Laatste update: 2026-04-17 — Trail Guide loop fix + Vision parameters

---

## 🔴 Prioriteit — volgende sessie

- [ ] **Trail Guide ingest valideren** — RapidOCR run actief (gestart 08:32)
      ```bash
      curl localhost:6333/collections/medical_library | python3 -c \
        "import json,sys; d=json.load(sys.stdin); print(d['result']['points_count'])"
      journalctl -u book-ingest-queue --no-pager -n 50 | grep -E "trail|Produced|chunks"
      ```
      Verwacht: 500+ chunks (460 pagina's, RapidOCR 151-404 words/pagina in test)
      Vision credentials: `config/google_vision_key.json` ontbreekt — handmatig herstellen voor Vision path

- [ ] **Deadman + Travell chunk counts valideren in Qdrant**
      Verwacht: Deadman 1000+ chunks (673p), Travell 800+ chunks (838p)

- [ ] **Eerste protocol genereren via /protocols** (Etalagebenen als testklacht)
      Vereiste: Deadman chunks in Qdrant (kai_a=1)
      Test: `python3 /root/medical-rag/scripts/generate_protocol.py "Etalagebenen"`

- [ ] **1.Upper_Body_Techniques.mp4 opsplitsen + herverwerken**
      Bestand: 525MB — te groot voor Whisper in één pass
      Oplossing: ffmpeg opsplitsen in 400MB segmenten

---

## 🟡 Gepland

- [ ] **Playwright regressietests** — 8 nav-items + kritieke pagina's automatisch testen
- [ ] **QAT curriculum valideren** — 546 vectors in nrt_qat_curriculum — zijn dit de juiste chunks?
- [ ] **EPUB image extractie testen** — Sobotta/AnatomyTrains nog niet geïngesteerd; na upload nachtrun testen
- [ ] **PDF Vision API extractie valideren** — Deadman + Travell na nachtrun: verwacht 400+ figuren per boek
- [ ] **Video transcriptie 19 NRT video's** — queue actief, 1.Upper_Body overgeslagen
- [ ] **Meer boeken uploaden:**
      - Sobotta Vol 1/2/3 (EPUB) — kai_k=1 kai_i=1 primaire anatomie
      - Maciocia TCM 3 boeken — kai_k=1 kai_a=1 volledigste TCM bron
      - Campbell acupunctuurpuntenbrug — kai_k=1 kai_a=2
      - AnatomyTrains (EPUB) — kai_k=1 kai_i=1 fascia
- [ ] **gstack installeren** — `/cso`, `/investigate`, `/careful`, `/guard` skills
- [ ] **/search pagina verbeteren** — RAG query interface UI
- [ ] **Protocol taal optie** — standaard NL, optie EN
- [ ] **Streaming protocol generatie** — SSE progress events per sectie
- [ ] **Python-docx skill** — voor protocol generator alternatieven

---

## ⚙️ Hardware (gepland)

- [ ] **Mac Studio M5 Max** — verwacht WWDC juni 2026
      ~€2.299-€2.499 | 96/128GB RAM | 546 GB/s bandbreedte
      Hetzner CX53 blijft als backup/Tailscale endpoint + nachtrun server

---

## 🟢 Ideeën — nog niet besloten

- [ ] Interactieve afbeelding selectie UI (3-5 kandidaten per weefselrij)
- [ ] Protocol regeneratie per sectie (alleen één sectie herschrijven)
- [ ] Protocol versie management (v1/v2 naast elkaar)
- [ ] Blog generator NRT-Amsterdam.nl (RAG → Ollama → WordPress MCP)
- [ ] Visueel zoeken (upload afbeelding → zoek vergelijkbare)
- [ ] Officiële Deadman digitale versie aanschaffen (DRM-vrij via Eastland Press)
- [ ] Consistentie guardian cross-collectie
- [ ] Protocol pre-validatie (Ollama checkt dekking voor generatie)

---

## ✅ Afgerond — sessie 2026-04-17 (Trail Guide loop fix + Vision parameters)

- [x] **Infinite loop diagnose** — root cause: `startup_scan()` re-enqueuet failed books (geen completed_at)
      `Restart=on-failure` triggert bij service exit; 234 log mentions → ~39 runs × 460 pages = ~$27 Vision kosten
- [x] **FIX A — max retries** — `parse_retry_count` in state.json; na 3 pogingen → `permanently_failed`
      `startup_scan()` slaat permanently_failed books over; counter reset bij succesvolle parse
- [x] **FIX B — Vision parameters** — 300 DPI (was 150), `language_hints=["en"]`, lege-filter ipv `< 3 words`
      Actief zodra `config/google_vision_key.json` hersteld is (gitignored, handmatig)
- [x] **FIX D — is_mostly_image() bypass** — werkelijke root cause 0 chunks: atlas-detector vlagde alle pagina's
      `force_ocr_engine` bypast nu `_is_mostly_image()` in `_parse_scanned()` — RapidOCR werkt als fallback
      Test bevestigd: 151-404 words/pagina, 3 chunks uit 3 testpagina's via RapidOCR
- [x] **Trail Guide state reset** — `parse_retry_count=0`, parse phase pending, frisse start
- [x] **Queue herstart** — 08:32 gestart, Trail Guide 460 pagina's via RapidOCR cascade

---

## ✅ Afgerond — sessie 2026-04-17 (audit_score + category_scores fix)

- [x] **GitHub CONTEXT.md sync check** — lokaal en GitHub waren identiek, geen actie nodig
- [x] **audit_score Deadman + Travell** — was `None`/fout door Ollama timeouts; Claude API quality scorer gerund op 15 sample chunks
      Deadman: `quality_score=2.6` | Travell: `quality_score=2.56`
- [x] **category_scores beide boeken** — was `{}` door architectuurmismatch (Claude API zet `tags/kai_*`, Ollama zet `usability_tags`)
      Fix: KAI-derived usability profile synthetisch berekend uit kai_k/kai_a/kai_i chunk-verdeling
      Deadman: `protocol=5, diagnose=5, anatomie=5, literatuur=5`
      Travell: `protocol=5, diagnose=2, anatomie=5, literatuur=5`
- [x] **Background audit_book.py process gekilld** — voorkomen dat het Claude-scores overschreef na Ollama-timeouts

---

## ✅ Afgerond — sessie 2026-04-17 (5e fase + audit diagnose)

- [x] **5e fase "Afbeeldingen" in phase table** — /library drawer (buildPhaseTable) + /library/ingest widget
      `image_extraction_info` toegevoegd aan `/api/library/book/{hash}/detail` + `/api/library/progress/active`
      Voortgang via `/tmp/image_extraction_{hash}.json` (live progress file per boek)
      States: pending / running (+ progress bar) / done ({n} figuren geëxtraheerd) / not_applicable (skip rij)
- [x] **audit_score diagnose**
      - Deadman: `quality_score=None` in audit JSON — audit API-fout tijdens book audit run
      - Travell: `quality_score=4.85` — werkt correct
      - category_scores: `usability_profile.scores={}` voor beide — audit liep toen chunks nog `skipped_ollama_timeout` waren
      - Fix: re-run `audit_book.py` voor beide boeken (nu chunks zijn getagd)

---

## ✅ Afgerond — sessie 2026-04-17 (audit fallback + retroaudit)

- [x] **audit_chunk() permanente fallback** — lege tekst (<10 chars) → `tagged_claude_default` direct
      Na 3× falen → `tagged_claude_default` (k=3,a=3,i=3) + log warning met chunk preview
- [x] **retroaudit_skipped() fix** — vangt ook `<none>` status chunks op (niet alleen `startswith("skipped")`)
      Index-gebaseerde merge voor chunks zonder chunk_id
- [x] **Drawer info box** — Claude API aan → paars "Nu uitvoeren" bericht; uit → amber met tijdvenster zonder "200/nacht"
      `claude_api_enabled` toegevoegd aan `/api/library/book/{hash}/detail` response
- [x] **2773 chunks getagd** — Deadman 1013/1013 + Travell 1760/1760 volledig getagd na retroaudit
      Waren allemaal `skipped_ollama_timeout` of `<none>` — state.json gecorrigeerd

---

## ✅ Afgerond — sessie 2026-04-17 (extractie uit nachtrun)

- [x] **_phase_image_extract() verwijderd uit nightly_maintenance.py** — `_count_books_needing_extraction()`, alloc dict entry, fase-tuple en de volledige method weg
      Reden: extractie draait al als background thread direct na qdrant fase; nachtrun is overbodig
- [x] **Backfill gestart** — bestaande boeken met qdrant=done maar nog geen images_metadata.json worden nu bijgewerkt

---

## ✅ Afgerond — sessie 2026-04-17 (image pipeline refactor)

- [x] **Goedkeuringslogica verwijderd** — image_approvals.json, prescreeen_images(), screen_images_background() volledig weg
      `audit_book.py`, `book_ingest_queue.py`, `nightly_maintenance.py`, `web/app.py` opgeschoond
- [x] **Prioriteitssysteem** — `image_source`, `image_priority`, `image_priority_override`, `image_evaluated` in alle 54 boekentries
      epub → high | pdf → normal | override via /images UI → POST /api/images/priority
- [x] **image_extractor.py** — nieuw script: Vision API PICTURE blocks + PyMuPDF crop (PDF) + ebooklib (EPUB)
      `extract_figures_from_pdf()` + `extract_images_from_epub()` — parallel (8 workers)
      Output: `data/extracted_images/{book_hash}/images_metadata.json`
- [x] **Pipeline integratie** — background thread na qdrant fase start extractie automatisch
- [x] **Nachtrun fase vervangen** — `_phase_image_screening` → `_phase_image_extract()`
      Verwerkt boeken zonder images_metadata.json binnen tijdsbudget
- [x] **/images pagina herschreven** — prioriteitsbadges (Hoog/Normaal/Laag/Overslaan), evaluatie status, "Prioriteit wijzigen" dropdown
      Filters: Alle / Hoog / Normaal / Laag / Niet beoordeeld
      GET /api/images/library + POST /api/images/priority API endpoints

---

## ✅ Afgerond — sessie 2026-04-17

- [x] **git filter-branch** — google_vision_key.json volledig uit git history verwijderd
      700 commits herschreven, force push geslaagd, GitHub push protection opgeheven
- [x] **Trail Guide force_ocr_engine** — google_vision override in book_classifications.json
      EasyOCR kalibratie cache gewist, state gereset, Google Vision parallel mode actief
- [x] **Transcriptie skip mechanisme** — settings.json transcription.skip_files + max_file_size_mb
      1.Upper_Body_Techniques.mp4 (525MB) overgeslagen, queue hervat met 16_Expanded...
- [x] **Documentatie overhaul** — CONTEXT/TECHNICAL/OPERATIONS volledig herschreven
      BACKLOG bijgewerkt, CLAUDE.md documentatie triggers toegevoegd
      Orphan bestanden verwijderd (ARCHITECTURE/CHANGELOG/REQUIREMENTS/TECHNICAL_DESIGN/PROJECT_STATE)

---

## ✅ Afgerond — sessie 2026-04-16 (parse speed fix)

- [x] Native PDFs: PyMuPDF als primaire parser i.p.v. Docling (377× sneller, 92 pag/sec)
- [x] Scanned PDFs: RapidOCR als eerste engine in cascade
- [x] Deadman + Travell parse fase gereset (stonden op "running" met Docling)

---

## ✅ Afgerond — sessie 2026-04-16 (pipeline rebuild)

- [x] State machine per boek (state.json + fase-bestanden + resume logic)
- [x] ollama_manager.py (OllamaManager singleton met health checks + auto-restart)
- [x] Image screening ontkoppeld van hoofdpipeline (nightly job)
- [x] Autonoom watchdog service (watchdog.py + book-ingest-watchdog.service)
- [x] WATCHDOG_LOG.md auto-bijgewerkt en gesynchroniseerd naar GitHub
- [x] Progress widget fase-voor-fase display (parse → audit → embed → qdrant)
- [x] nightly_maintenance.py volledige implementatie (7 fasen)
- [x] STAP 0 schone start (collection deleted, caches cleared, PDFs hernoemd 01/02/03)

---

## ✅ Afgerond — sessies 2026-04-14/15/16

- [x] OCR cascade (RapidOCR → EasyOCR → Surya → Tesseract → Google Vision)
- [x] OCR preprocessing (deskew, denoise, CLAHE, Otsu)
- [x] Per-boek OCR kalibratie via Ollama (kalibratiecache)
- [x] Smart PDF type detectie (native/mixed/scanned)
- [x] K/A/I classificatiesysteem (35+ boeken, chunk-niveau payload)
- [x] Protocol generator (RAG + K/A/I filter + Ollama + Word .docx)
- [x] 476 Deadman punt afbeeldingen + point_index.json
- [x] normalize_points.py (alle varianten → Deadman standaard)
- [x] MemPalace MCP server (116+ drawers)
- [x] Playwright MCP server
- [x] nrt-ui-standards skill (design tokens + schrijfregels)
- [x] PostToolUse hook (py_syntax_check.sh)
- [x] PreToolUse hook (security_check.sh)
- [x] Stop hook (mempalace_save.sh)
- [x] Design audit (#2563eb → #1A6B72 teal in alle pagina's)
- [x] Video transcriptie queue (systemd, Whisper)
- [x] /library catalogus (6 tabs, K/A/I badges, zoekbalk, sortering)
- [x] FastAPI web interface volledig (9 routes)
- [x] Live status sync GitHub (LIVE_STATUS.md elke 5 min)
