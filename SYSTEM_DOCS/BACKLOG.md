# BACKLOG — Medical RAG
> Auto-updated by Claude Code after each session.

## 🔴 Prioriteit — volgende sessie
- [ ] Zoekresultaten valideren zodra Deadman klaar is — test op ST-36, trigger points, meridian balancing
- [ ] Upload NRT + QAT cursusmateriaal boeken → `books/nrt/` en `books/qat/`
- [ ] /protocols pagina bouwen — Word (.docx) behandelprotocol output (§1 Klachtbeeld / §2 Behandeling / §3 Bijlagen)
- [ ] Browser terminal (ttyd) — iframe laadt niet ondanks actieve service op poort 7682
- [ ] NRT video transcriptie — 21 videos in wachtrij; voortgang controleren en valideren

## 🟡 Backlog — gepland
- [ ] Streaming antwoord testen met echte boeken (Ollama traag bij concurrente ingest)
- [ ] Zoekresultaten verbeteren na eerste echte boeken ingested
- [ ] Nightly re-tagging job wanneer tagging_rules.md wijzigt
- [ ] Feedback loop implementeren (implicit + explicit learning)
- [ ] Interactieve afbeeldingsselectie bij protocol generatie
- [ ] Word output: python-docx installeren, protocol template maken
- [ ] Multi-file upload in /videos (UI only)
- [ ] Calibratie cache valideren na eerste scanned PDF (ocr_calibrate.py)

## 🟢 Ideeën — nog niet besloten
- [ ] Visueel zoeken — upload afbeelding, vind vergelijkbare (vereist apart image embedding model)
- [ ] Auto-classificatie override in /library UI
- [ ] Nightly kwaliteitsrapport

## ✅ Afgerond
- [x] OCR optimalisatie modules — ocr_preprocess.py (OpenCV deskew/denoise/CLAHE), ocr_calibrate.py (per-boek Ollama kalibratie), ocr_postcorrect.py (regel + Ollama correctie)
- [x] OCR preprocessing geïntegreerd in parse_pdf.py scanned/mixed pad
- [x] Pause/resume knoppen in /library en /videos — POST /library/pause, /library/resume, /videos/pause, /videos/resume + GET /library/paused, /videos/paused
- [x] book_ingest_queue.py + transcription_queue.py — pause flag check vóór elke volgende job
- [x] Cascade OCR: EasyOCR → Surya → Tesseract fallback met preprocessing + per-boek kalibratie
- [x] sync_status.py — HOME=/root env var fix, elapsed-tijd in job display, Qdrant vector counts
- [x] /library/progress + /videos/progress endpoints met 10s auto-refresh in UI
- [x] SSE generator fix — done event altijd verzonden ook bij Ollama fout
- [x] /search pagina met RAG query interface — tabs Zoeken + Afbeeldingen
- [x] Streaming Ollama antwoord token voor token via SSE
- [x] Zoeken in video transcripts met timestamp display
- [x] Afbeeldingen zoeken via tekst (ST-36, Fig 4.155, semantisch)
- [x] /images/file/{filename} — afbeeldingen serveren vanuit Qdrant
- [x] Dashboard "Snel zoeken" widget
- [x] Qdrant vectors_count → points_count fix (al gedaan vorige sessie)
- [x] AI instructie bestanden als MD in Git — nrt_qat_bridge, protocol_structure, tagging_rules
- [x] Vereenvoudigde library UI (3 secties) — Medische Literatuur / NRT+QAT / Apparatuur
- [x] nrt_qat_curriculum Qdrant collectie aangemaakt (nrt + qat samengevoegd)
- [x] sync_status.py synct AI_INSTRUCTIONS/ naar GitHub elke 5 min
- [x] audit_book.py laadt tagging context uit AI instructie MD bestanden
- [x] Refactor naar single collection + AI tagging — medical_library, usability_tags per chunk
- [x] Image approval systeem gebouwd — prescreening via Ollama, /images pagina
- [x] Literatuuroverzicht pagina — /library/overview met usability scores + tag definities
- [x] /library/retag endpoint — heranalyse chunks zonder herparse
- [x] /library pagina gebouwd — upload, status, audit rapport per collectie
- [x] parse_pdf.py — Docling + PyMuPDF fallback, chunking, punten, figuren, vertaling
- [x] parse_epub.py — 3 strategieën (ebooklib, raw ZIP, text fallback)
- [x] audit_book.py — structureel + LLM kwaliteitsaudit + auto-classificatie
- [x] book_ingest_queue.py — sequentiële queue, startup scan, Qdrant upsert
- [x] book-ingest-queue.service — systemd, enabled, getest met test_acupuncture.pdf ✅
- [x] test_acupuncture.pdf — 2 chunks ingestered, quality_score 4.5, medical_library collection ✅
- [x] /status/snapshot uitgebreid met books + qdrant_collections
- [x] sync_status.py uitgebreid met Books + Images sectie in LIVE_STATUS.md
- [x] Sequentiële transcriptie queue via systemd
- [x] Whisper --task translate — alle transcripts in Engels
- [x] Auto-ingest transcripts → Qdrant video_transcripts
- [x] Status endpoint — running/queued/waiting/done
- [x] Browser terminal gebouwd (ttyd poort 7682) — interface werkt, iframe bug open
- [x] Live status sync → GitHub elke 5 min (LIVE_STATUS.md)
- [x] Claude Code auto-permissions ingesteld
- [x] ANTHROPIC_API_KEY permanent in /root/.bashrc
- [x] Marker systeem (notify.sh + /status/markers)
- [x] Log observer endpoints (/logs/{logname})
- [x] Status snapshot endpoint (/status/snapshot)
