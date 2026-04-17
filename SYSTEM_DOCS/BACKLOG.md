# BACKLOG — Medical RAG
> Bijgewerkt door Claude Code na elke sessie.
> Laatste update: 2026-04-17 — image pipeline refactor: Vision API + prioriteitssysteem

---

## 🔴 Prioriteit — volgende sessie

- [ ] **Trail Guide ingest valideren** — Google Vision resultaat controleren
      ```bash
      curl localhost:6333/collections/medical_library | python3 -c \
        "import json,sys; d=json.load(sys.stdin); print(d['result']['points_count'])"
      journalctl -u book-ingest-queue --no-pager -n 50 | grep -E "trail|Produced|chunks"
      ```
      Verwacht: 500+ chunks (460 pagina's, atlas-stijl)

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
