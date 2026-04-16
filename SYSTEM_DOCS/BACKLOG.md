# BACKLOG — Medical RAG
> Auto-updated by Claude Code after each session.
> Last updated: 2026-04-16 — /library catalogus pagina gebouwd

## 🔴 Prioriteit — volgende sessie

- [ ] Travell+Simons valideren na ingest
      Check: curl localhost:6333/collections/medical_library | grep points_count
      Verwacht: 1000+ chunks voor een 63MB medisch boek

- [ ] Deadman valideren na herverwerking
      987 chunks aangemaakt maar niet in Qdrant door audit timeout
      Audit fix toegepast — Deadman opnieuw in queue
      Check: source_file="deadman" chunks in medical_library
      Verwacht: 987 chunks correct embedded

- [ ] Eerste protocol genereren via /protocols pagina
      Klacht: "Etalagebenen" (gold standard beschikbaar als referentie)
      Vereiste: Deadman chunks in Qdrant (kai_a=1)
      Test: python3 /root/medical-rag/scripts/generate_protocol.py "Etalagebenen"
      Vergelijk output met /data/protocols/gold_standard referentie

## 🟡 Backlog — gepland

- [ ] Video transcriptie hervatten
      systemctl start transcription-queue
      20 NRT + 15 QAT videos wachten — eerst na boek verwerking

- [ ] QAT curriculum uploaden (Axel)
      Upload via /library → nrt_qat_curriculum collectie
      Sectie 4 protocol generator wordt dan gevuld

- [ ] Interactieve afbeelding selectie UI
      Per weefselrij: 3-5 kandidaat afbeeldingen tonen (groter dan thumbnails)
      Axel selecteert 0-3 per weefsel, fullscreen knop
      AI geeft waarschijnlijkheidsscore per kandidaat
      Per boek aan/uit schakelaar bruikbaarheid

- [ ] Streaming protocol generatie
      SSE progress events per sectie
      UI toont "Genereren klachtbeeld... ✅ Genereren oorzaken..."

- [ ] Meer boeken uploaden
      Sobotta Vol 1/2/3 (EPUB) — kai_k=1 kai_i=1 primaire anatomie
      Maciocia TCM 3 boeken — kai_k=1 kai_a=1 volledigste TCM bron
      Campbell acupunctuur — kai_k=1 kai_a=2 anatomy-acupuncture bridge
      AnatomyTrains (EPUB) — kai_k=1 kai_i=1 fascia
      Magee orthopedic assessment

- [ ] /search testen met echte Deadman data
      Verwacht: ST-36 Zusanli chunks bij "acupunctuur been"

- [ ] Protocol taal optie
      Standaard: Nederlands
      Optie: Amerikaans Engels

- [ ] Protocol versie management
      v1, v2 naast elkaar bewaren
      Versiegeschiedenis tonen in /protocols tab

- [ ] Protocol regeneratie per sectie
      Alleen één sectie opnieuw genereren zonder alles te herschrijven

- [ ] Nightly AI review transcripts + chunks kwaliteitsrapport

## 🟢 Ideeën — nog niet besloten

- [ ] Officiële Deadman digitale versie aanschaffen
      Huidige versie is een scan — officieel betere kwaliteit
      Eastland Press — controleer of DRM-vrij beschikbaar

- [ ] PEMF/RLT documentatie uploaden
      FlexBeam behandelplannen (Axel downloadt van recharge.health)

- [ ] Consistentie guardian cross-collectie

- [ ] Protocol pre-validatie (Ollama checkt dekking voor generatie)

- [ ] Blog generator NRT-Amsterdam.nl
      RAG query → Ollama → WordPress MCP post

- [ ] Visueel zoeken — upload afbeelding, vind vergelijkbare

- [ ] Scraper recharge.health blog (publieke content)

## ✅ Afgerond sessie 2026-04-15/16

### OCR & Ingest Pipeline
- [x] Smart PDF type detectie (native/mixed/scanned via pdfplumber sampling)
- [x] OCR cascade fallback (EasyOCR → Surya → Tesseract)
- [x] OCR pre-processing (deskew, denoise, CLAHE, Otsu binarization)
- [x] OCR kalibratie per boek via Ollama (5 steekproefpagina's)
- [x] Adaptive DPI per pagina
- [x] Ollama OCR post-correctie (rule-based + LLM voor lage confidence)
- [x] Cross-boek learning log
- [x] Book ingest queue (systemd, heartbeat, startup guard)
- [x] Watchdog fix — BOOK_STALE=120min (was 30min — doodde Docling)
- [x] Audit non-blocking bij Ollama timeout
- [x] Embedding fix — BAAI/bge-large voor RAG (was nomic-embed-text)
- [x] Auto-split PDFs >30MB via pypdf (Travell+Simons)

### Monitoring
- [x] Voortgang library + videos (pagina X/Y, fase, chunks, 10s polling)
- [x] Pause/resume knoppen videos + boeken (schone database bij pauze)
- [x] Sync retry logic (3 pogingen, error log bij totaalmislukking)
- [x] Queue watchdog (auto-restart stale queues elke 10 min)
- [x] Nightly consistency check (Qdrant vs disk)
- [x] LIVE_STATUS.md sync betrouwbaar (HOME=/root fix in systemd)

### K/A/I Systeem
- [x] book_classifications.json (30+ boeken geclassificeerd met K/A/I)
- [x] Auto-link bij ingest (exact server filepath → classificatie)
- [x] Unclassified detection met waarschuwing
- [x] K/A/I query profielen voor protocol generator
- [x] Chunk-niveau K/A/I payload in Qdrant

### Acupunctuurpunten
- [x] 476 Deadman punt afbeeldingen geüpload
- [x] point_index.json aangemaakt (code → filepath + meridiaan)
- [x] Bladder Channel mappen samengevoegd
- [x] normalize_points.py (alle varianten → Deadman standaard)
- [x] meridian_mapping.md (QAT balancepunten + conversietabel)

### Protocol Generator
- [x] /protocols tab (NRT standaard protocol v3 bekijken + bewerken)
- [x] Auto-commit bij opslaan naar GitHub
- [x] generate_protocol.py (RAG + K/A/I filter + Ollama + Word output)
- [x] Word .docx via Node.js (exacte Etalagebenen v1.1 stijl)
- [x] Deadman punt afbeeldingen automatisch per puntcode
- [x] QAT balancepunten automatisch berekend per meridiaan
- [x] /protocols/generate + /protocols/download web endpoints
- [x] protocol_metadata.py (literatuur tracking + earmarking)
- [x] Earmarking bij nieuwe literatuur (needs_review badge)
- [x] Dashboard oranje banner bij verouderde protocollen
- [x] 8 gold standard protocol metadata records

### Developer Tooling & Hooks
- [x] PostToolUse hook — py_syntax_check.sh (python3 -m py_compile na elke Write/Edit)
- [x] PreToolUse hook — security_check.sh (secrets/injection scan, non-blocking, exit 0)
- [x] Stop hook — mempalace_save.sh (auto-mine SYSTEM_DOCS in MemPalace na sessie)
- [x] MemPalace MCP server — .mcp.json, palace /root/.mempalace/medical-rag (116 drawers)
- [x] Playwright MCP server — headless Chromium, alle 8 nav items geverifieerd
- [x] nrt-ui-standards Claude Code skill — design tokens + schrijfregels
- [x] Design audit — #2563eb vervangen door #1A6B72 teal in alle pagina's

### Bibliotheek Catalogus
- [x] /library cataloguspagina — 6 categorie-tabs, zoekbalk, sortering
- [x] /api/library/items — JSON met K/A/I, chunk count, status (35 boeken)
- [x] DELETE /api/library/items/{id} — Qdrant-verwijdering met dry-run
- [x] book_classifications.json v1.1 — library_category voor alle 35 boeken
- [x] Retroaudit nightly phase in nightly_maintenance.py
- [x] Heraudit knop per boek in /library/ingest (POST /library/reaudit/{filename})

### Eerder afgerond
- [x] FastAPI web interface + dashboard
- [x] Sequentiële transcriptie queue (systemd)
- [x] Whisper --task translate → Engels transcripts
- [x] Auto-ingest transcripts → Qdrant video_transcripts
- [x] Browser terminal (ttyd poort 7682)
- [x] Live status sync GitHub (LIVE_STATUS.md)
- [x] /search pagina RAG + image search + streaming
- [x] Video transcript zoeken met timestamp
- [x] Image approval systeem /images
- [x] Literatuuroverzicht /library/overview
- [x] Browser terminal iframe (ttyd poort 7682) — bevestigd werkend in browser
