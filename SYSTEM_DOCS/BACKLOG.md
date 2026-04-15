# BACKLOG — Medical RAG
> Auto-updated by Claude Code after each session.

## 🔴 Prioriteit — volgende sessie
- [ ] Browser terminal (ttyd) — iframe laadt niet ondanks actieve service op poort 7682
- [ ] /library pagina bouwen — Fase 1: parse_pdf.py + parse_epub.py + kwaliteitsvalidatie

## 🟡 Backlog — gepland
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
