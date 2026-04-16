# BACKLOG — Medical RAG
> Auto-updated by Claude Code after each session.

## 🔴 Prioriteit — volgende sessie
- [ ] Deadman ingest valideren — chunk count + audit score controleren
- [ ] Travell+Simons opnieuw in queue zetten (crashte bij ingest)
- [ ] Trail Guide OCR fix — is_mostly_image drempel te agressief voor anatomie-atlassen
- [ ] K/A/I tags retroactief toepassen op al ingested chunks (Deadman als eerste)
- [ ] Video transcriptie hervatten na boek verwerking
- [ ] Whisper taaldetectie verbeteren — detecteer audiotaal eerst,
      dan transcribe (EN) of translate (NL), sla detected_language op

## 🟡 Backlog — gepland
- [ ] generate_protocol.py bouwen — protocol generator
      (RAG query → K/A/I gefilterd → Ollama → Word document output)
- [ ] /protocols uitbreiden — behandelprotocol generator tab
      (naast standaard protocol: RAG query → Ollama → Word document output)
- [ ] Eerste behandelprotocol genereren via RAG
      (etalagebenen als testcase — gold standard beschikbaar)
- [ ] Streaming antwoord testen met echte boeken in Qdrant
- [ ] LLM kwaliteitsaudit voor video transcripts
      (steekproef chunks → Ollama → rapport in /data/transcript_quality/)
- [ ] Nightly AI review — transcripts + chunks gecontroleerd,
      rapport in LIVE_STATUS.md
- [ ] Query optimizer — Ollama herschrijft zwakke RAG queries
- [ ] NRT/QAT curriculum uploaden
- [ ] FlexBeam behandelplannen uploaden (gedownload van recharge.health)
- [ ] PEMF documentatie uploaden
- [ ] /images pagina verfijnen — goedkeuring workflow testen met echte afbeeldingen

## 🟢 Ideeën — nog niet besloten
- [ ] Consistentie guardian — cross-collectie terminologie check
- [ ] Protocol pre-validatie — Ollama checkt dekking voor protocolgen
- [ ] Dynamische PEMF/RLT settings via Ollama op basis van klachtbeeld
- [ ] Zelf-debuggende pipeline — Ollama analyseert stacktraces
- [ ] Scraper recharge.health blog (publieke content)
- [ ] Schematische lichaamstekening generator voor QAT pad plaatsing
- [ ] Visueel zoeken — upload afbeelding, vind vergelijkbare
- [ ] Officiële digitale versie Deadman aanschaffen
- [ ] EPUBs voor betere afbeeldingskwaliteit (Sobotta EPUB)

## ✅ Afgerond
- [x] /protocols pagina — NRT standaard protocol v3 bekijken + bewerken + git commit (GET/POST/raw endpoints)
- [x] K/A/I classificatiesysteem — config/book_classifications.json (29 boeken), get_kai_scores() in parse_pdf + parse_epub
- [x] normalize_points.py — canonieke puntnormalisatie, 21/21 tests geslaagd, QAT_BALANCE_2026 map
- [x] 476 Deadman acupunctuurpunt-afbeeldingen + point_index.json
- [x] Bladder Channel mappen samengevoegd (BL-01..BL-67)
- [x] Browser terminal (ttyd) — iframe fix: --base-path /terminal/shell + trailing slash + bash shell
- [x] LIVE_STATUS sync betrouwbaar — PATH env toegevoegd, sync loopt elke 5 min
- [x] Queue watchdog (queue_watchdog.py + systemd timer elke 10 min — auto-restart bij vastgelopen queue)
- [x] Sync retry logic (sync_status.py — 3 pogingen, 10s delay, error log, Restart=on-failure)
- [x] Nightly consistency check (transcripts + boeken vs Qdrant — auto her-ingest + log)
- [x] /var/log/nightly_consistency.log — nachtelijke resultaten in LIVE_STATUS.md
- [x] FastAPI web interface (medical-rag-web.service)
- [x] Dashboard — CPU/RAM/disk/services live
- [x] Sequentiële transcriptie queue (systemd, auto-resume na reboot)
- [x] Whisper --task translate — transcripts in Engels
- [x] Auto-ingest transcripts → Qdrant video_transcripts
- [x] Status endpoint — running/queued/waiting/done/queued
- [x] Browser terminal gebouwd (ttyd poort 7682)
- [x] Live status sync → GitHub elke 5 min (LIVE_STATUS.md)
- [x] BACKLOG.md sync naar GitHub
- [x] Claude Code auto-permissions ingesteld
- [x] ANTHROPIC_API_KEY permanent in /root/.bashrc
- [x] Marker systeem (notify.sh + /status/markers)
- [x] Log observer endpoints (/logs/{logname})
- [x] Status snapshot endpoint (/status/snapshot)
- [x] Book ingest pipeline — parse_pdf.py, parse_epub.py
- [x] OCR cascade fallback (EasyOCR → Surya → Tesseract)
- [x] OCR pre-processing (deskew, denoise, CLAHE, Otsu binarization)
- [x] OCR kalibratie per boek via Ollama (5 steekproefpagina's)
- [x] Adaptive DPI per pagina
- [x] Ollama post-correctie OCR output
- [x] Cross-boek learning log (config/ai_instructions/learning_log.md)
- [x] Smart PDF type detectie (native/mixed/scanned)
- [x] Book ingest queue (systemd, sequential, auto-resume)
- [x] LLM kwaliteitsaudit bij boek ingest (steekproef + auto-classificatie)
- [x] AI usability tagging per chunk (Ollama)
- [x] Single medical_library collection (was 6 aparte collecties)
- [x] Image approval systeem (/images pagina, pending/approved/rejected)
- [x] Literatuuroverzicht (/library/overview met usability scores)
- [x] Versiedetectie duplicate boeken
- [x] Multi-file upload bibliotheek + videos
- [x] AI instructie bestanden als MD in Git (nrt_qat_bridge, protocol_structure,
      tagging_rules, learning_log, feedback_history)
- [x] Vereenvoudigde library UI — 3 secties
- [x] nrt_qat_curriculum Qdrant collectie
- [x] sync_status.py synct AI_INSTRUCTIONS/ naar GitHub
- [x] /search pagina — RAG query + image search + streaming antwoord
- [x] Video transcript zoeken met timestamp display
- [x] Dashboard vectoren count fix
- [x] Voortgangsweergave library + videos (progress polling)
- [x] Pause/resume knoppen videos + boeken (schone database bij pauze)
- [x] FlexBeam documentatie PDF aangemaakt
