# BACKLOG — Medical RAG
> Auto-updated by Claude Code after each session.
> Last updated: 2026-04-16

## 🔴 Prioriteit — volgende sessie

- [ ] Travell+Simons valideren na ingest — chunk count + audit score
- [ ] Deadman valideren na ingest — 987 chunks correct in Qdrant?
      Controleer: curl localhost:6333/collections/medical_library
      Verwacht: 987+ vectors na herverwerking
- [ ] Eerste protocol testen — "Etalagebenen" genereren via /protocols
      Vereist: Deadman in Qdrant (kai_a=1 chunks)
      Test: python3 scripts/generate_protocol.py "Etalagebenen"
- [ ] Browser terminal iframe fixen — ttyd draait maar iframe laadt niet
- [ ] Retroactive audit implementeren in nightly_maintenance.py
      Chunks met audit_status="skipped_ollama_timeout" alsnog auditoren
      Max 200 chunks per nacht
- [ ] Heraudit knop in /library pagina per boek

## 🟡 Backlog — gepland

- [ ] Video transcriptie hervatten na boek verwerking
      systemctl start transcription-queue (videos gepauzeerd voor CPU)
- [ ] QAT curriculum uploaden (Axel doet dit zelf)
      Upload via /library → nrt_qat_curriculum collectie
- [ ] NRT standaard protocol v3 testen in /protocols
      Bekijken + eventueel aanpassen via edit functie
- [ ] Interactieve afbeelding selectie UI voor weefsel sectie
      Per weefselrij: 3-5 kandidaat afbeeldingen tonen
      Axel selecteert 0-3 per weefsel met fullscreen optie
      AI geeft waarschijnlijkheidsscore per kandidaat
- [ ] Streaming protocol generatie (SSE progress events)
      Elke sectie completion → UI update
- [ ] /search testen met echte Deadman data
      Verwacht: acupunctuurpunten chunks correct ophalen
- [ ] Nightly AI review transcripts
      Steekproef chunks → Ollama → kwaliteitsrapport
- [ ] Query optimizer — Ollama herschrijft zwakke RAG queries
- [ ] Meer boeken uploaden:
      Sobotta Vol 1/2/3 (EPUB) — primaire anatomie + afbeeldingen
      Maciocia TCM (3 boeken) — TCM compleet
      Campbell acupunctuur — anatomy-acupuncture bridge
      Magee orthopedic assessment
      AnatomyTrains (EPUB)
- [ ] Protocol taal optie — Amerikaans Engels naast Nederlands
- [ ] Protocol versie management (v1, v2 naast elkaar bewaren)
- [ ] Protocol regeneratie per sectie (niet alles opnieuw)

## 🟢 Ideeën — nog niet besloten

- [ ] Officiële digitale versie Deadman aanschaffen
      (huidige versie is scan — officieel betere OCR kwaliteit)
- [ ] PEMF/RLT documentatie uploaden (FlexBeam behandelplannen)
- [ ] EPUBs voor betere afbeeldingskwaliteit
- [ ] Consistentie guardian — cross-collectie terminologie check
- [ ] Protocol pre-validatie — Ollama checkt dekking voor generatie
- [ ] Dynamische PEMF/RLT settings via Ollama op basis van klachtbeeld
- [ ] Scraper recharge.health blog (publieke content)
- [ ] Visueel zoeken — upload afbeelding, vind vergelijkbare
- [ ] Blog generator voor NRT-Amsterdam.nl

## ✅ Afgerond deze sessie (2026-04-15/16)

### Pipeline & Ingest
- [x] Book ingest pipeline — parse_pdf.py, parse_epub.py
- [x] Smart PDF type detectie (native/mixed/scanned)
- [x] OCR cascade fallback (EasyOCR → Surya → Tesseract)
- [x] OCR pre-processing (deskew, denoise, CLAHE, Otsu)
- [x] OCR kalibratie per boek via Ollama (5 steekproefpagina's)
- [x] Adaptive DPI per pagina
- [x] Ollama post-correctie OCR output
- [x] Cross-boek learning log
- [x] Book ingest queue (systemd, sequential, heartbeat, startup guard)
- [x] Watchdog fix — BOOK_STALE=120min ipv 30min
- [x] Audit non-blocking bij Ollama timeout
- [x] Embedding fix — BAAI/bge-large voor RAG queries (was nomic-embed-text)

### Monitoring & Sync
- [x] Voortgangsweergave library + videos (progress polling 10s)
- [x] Pagina X van Y progress bar met fase indicator
- [x] Pause/resume knoppen videos + boeken
- [x] Schone database bij pauze (geen halve chunks)
- [x] Sync retry logic (3 pogingen, error log)
- [x] Queue watchdog (auto-restart stale queues)
- [x] Nightly consistency check (Qdrant vs disk)
- [x] LIVE_STATUS.md sync betrouwbaar

### K/A/I & Classificatie
- [x] K/A/I classificatiesysteem (hybride statisch+dynamisch)
- [x] book_classifications.json (30+ boeken geclassificeerd)
- [x] Auto-link bij ingest (exact filepath → classificatie)
- [x] Unclassified detection met waarschuwing
- [x] K/A/I query profielen voor protocol generator

### Acupunctuurpunten
- [x] 476 Deadman punt afbeeldingen geüpload naar server
- [x] point_index.json aangemaakt
- [x] Bladder Channel mappen samengevoegd
- [x] normalize_points.py met complete meridiaanmapping
- [x] meridian_mapping.md met QAT balancepunten

### Protocol Generator
- [x] /protocols tab — NRT standaard protocol v3 bekijken + bewerken
- [x] Auto-commit bij opslaan protocol naar GitHub
- [x] generate_protocol.py — volledig protocol generator
- [x] RAG query met K/A/I filtering
- [x] Word .docx output via Node.js (exacte Etalagebenen stijl)
- [x] Acupunctuurpunt afbeeldingen automatisch uit Deadman index
- [x] QAT balancepunten automatisch berekend
- [x] /protocols/generate + /protocols/download endpoints
- [x] Literatuur tracking per protocol (protocol_metadata.py)
- [x] Earmarking bij nieuwe literatuur (needs_review badge)
- [x] Dashboard oranje banner bij verouderde protocollen
- [x] 8 gold standard protocol metadata records aangemaakt

### Eerder afgerond
- [x] FastAPI web interface (medical-rag-web.service)
- [x] Dashboard CPU/RAM/disk/services live
- [x] Sequentiële transcriptie queue (systemd)
- [x] Whisper --task translate → Engels
- [x] Auto-ingest transcripts → Qdrant
- [x] Browser terminal (ttyd poort 7682)
- [x] Live status sync → GitHub (LIVE_STATUS.md)
- [x] BACKLOG.md sync naar GitHub
- [x] ANTHROPIC_API_KEY in /root/.bashrc
- [x] Marker systeem + log observer endpoints
- [x] /search pagina — RAG + image search + streaming
- [x] Video transcript zoeken met timestamp
- [x] Literatuuroverzicht /library/overview
- [x] Image approval systeem /images
