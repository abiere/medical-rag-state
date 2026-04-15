# BACKLOG — Medical RAG
> Auto-updated by Claude Code after each session.

## 🔴 Prioriteit — volgende sessie
- [ ] Browser terminal (ttyd) — iframe laadt niet ondanks actieve service op poort 7682
- [ ] Upload NRT standaard behandelprotocol v3
- [ ] Upload QAT cursusmateriaal
- [ ] Upload eerste echte medische boek (Deadman of Sobotta)

## 🟡 Backlog — gepland
- [ ] Nightly re-tagging job wanneer tagging_rules.md wijzigt
- [ ] Feedback loop implementeren (implicit + explicit learning)
- [ ] Interactieve afbeeldingsselectie bij protocol generatie
- [ ] /search pagina — RAG query interface
- [ ] Eerste behandelprotocol genereren via RAG
- [ ] Multi-file upload in /videos (UI only)
- [ ] NRT video's uploaden en transcriberen

## 🟢 Ideeën — nog niet besloten
- [ ] Auto-classificatie override in /library UI
- [ ] Nightly kwaliteitsrapport

## ✅ Afgerond
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
