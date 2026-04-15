# BACKLOG — Medical RAG
> Auto-updated by Claude Code after each session.

## 🔴 Prioriteit — volgende sessie
- [ ] Browser terminal (ttyd) — iframe laadt niet ondanks actieve service op poort 7682
- [ ] Upload eerste echte boek en valideer kwaliteit (Deadman, Sobotta, etc.)

## 🟡 Backlog — gepland
- [ ] book-ingest-queue.service starten zodra eerste echte boek geüpload is
- [ ] /search pagina — RAG query interface
- [ ] Eerste behandelprotocol genereren via RAG
- [ ] Multi-file upload in /videos (UI only)
- [ ] NRT video's uploaden en transcriberen
- [ ] /images pagina — afbeeldingen browser

## 🟢 Ideeën — nog niet besloten
- [ ] Cross-collectie consistentie check
- [ ] Auto-classificatie override in /library UI
- [ ] Nightly kwaliteitsrapport per collectie

## ✅ Afgerond
- [x] /library pagina gebouwd — upload, status, audit rapport per collectie
- [x] parse_pdf.py — Docling + PyMuPDF fallback, chunking, punten, figuren, vertaling
- [x] parse_epub.py — 3 strategieën (ebooklib, raw ZIP, text fallback)
- [x] audit_book.py — structureel + LLM kwaliteitsaudit + auto-classificatie
- [x] book_ingest_queue.py — sequentiële queue, startup scan, Qdrant upsert
- [x] book-ingest-queue.service — systemd (enabled, NOT started)
- [x] /status/snapshot uitgebreid met books + qdrant_collections
- [x] sync_status.py uitgebreid met Books sectie in LIVE_STATUS.md
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
