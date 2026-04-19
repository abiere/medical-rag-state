# OPEN ISSUES — NRT-Amsterdam.nl Medical RAG
> Opgesteld: 2026-04-19 | Status: documentatie — geen wijziging
> Herstel komt later. Dit bestand legt vast wat er is.

---

## Instructie voor gebruik

- Elk issue heeft een nummer (ISSUE-NNN) en een STATUS veld
- STATUS = **OPEN** betekent: vastgelegd, niet hersteld
- Nieuwe issues toevoegen onderaan met oplopend nummer
- Bij herstel: STATUS wijzigen naar `OPGELOST — [datum] [beschrijving]`

---

### ISSUE-001 — CLAUDE.md Qdrant-counts stale

- **Eerste waarneming:** 2026-04-19 sessie (diagnose rapport)
- **Symptoom:** CLAUDE.md §Qdrant collections vermeldt onjuiste punt-aantallen
  - `medical_library`: CLAUDE.md zegt 10.428 — werkelijk 17.522 (+7.094)
  - `nrt_video_transcripts`: CLAUDE.md zegt 241 — werkelijk 250
  - `qat_video_transcripts`: CLAUDE.md zegt 0 — werkelijk 443
  - `book_classifications.json`: CLAUDE.md zegt "35 books" — werkelijk 60 entries
- **Vermoedelijke root cause:** CLAUDE.md wordt niet automatisch bijgewerkt door sync-scripts. Handmatige update werd overgeslagen bij vorige sessiesluitingen.
- **Scope:** Misleidt nieuwe sessies bij het lezen van CLAUDE.md als referentie. CONTEXT.md en LIVE_STATUS.md bevatten wél de juiste aantallen.
- **Reproduceerbaar:** ja
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `CLAUDE.md` regels 58, 63, 64, 89
- **Referenties:** Diagnoserapport sessie 2026-04-19

---

### ISSUE-002 — CLAUDE.md verwijst naar niet-bestaande medical-rag-sync.timer

- **Eerste waarneming:** 2026-04-19 sessie (diagnose rapport)
- **Symptoom:** CLAUDE.md §GitHub sync health check beschrijft een herstelstap die controleert: `systemctl status medical-rag-sync.timer`. Deze unit bestaat **niet**. De werkende sync-timer heet `sync-status.timer`.
- **Vermoedelijke root cause:** Bij een eerdere refactoring of hernoeming van de timer is CLAUDE.md niet bijgewerkt.
- **Scope:** Misleidend bij sessieopening. De sync werkt wél (via sync-status.timer), maar de CLAUDE.md-instructie faalt stil.
- **Reproduceerbaar:** ja — `systemctl status medical-rag-sync.timer` retourneert "could not be found"
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `CLAUDE.md` regels 263–267
- **Referenties:** Diagnoserapport sessie 2026-04-19

---

### ISSUE-003 — book-ingest-queue.service inactive; CLAUDE.md zegt "Active (systemd)"

- **Eerste waarneming:** 2026-04-19 sessie (diagnose rapport)
- **Symptoom:**
  - `book-ingest-queue.service` is `inactive (dead)` — CLAUDE.md zegt `✅ Active (systemd)`
  - Queue start, slaat 4 permanently_failed boeken over, ziet lege queue, stopt in 100ms
  - book-ingest-watchdog herstart de queue elke minuut (ziet "service not active" → RESTART_BOOK_INGEST)
  - Resultaat: ~60 onnodige restarts per uur, logvervuiling
- **Vermoedelijke root cause:**
  - Er staan geen nieuwe boeken in de ingest queue
  - De 4 permanently_failed entries (zie ISSUE-005) worden elke keer opnieuw overgeslagen
  - Watchdog onderscheidt "lege queue, clean exit" niet van "gestorven service"
- **Scope:** Functioneel geen probleem voor eindgebruiker — Qdrant heeft alle ingested boeken. Maar CLAUDE.md is incorrect en de watchdog-logica genereert ruis.
- **Reproduceerbaar:** ja
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `CLAUDE.md` regel 45; `scripts/watchdog.py`; `SYSTEM_DOCS/WATCHDOG_LOG.md`
- **Referenties:** journalctl -u book-ingest-queue; journalctl -u book-ingest-watchdog

---

### ISSUE-004 — Transcriptie→ingestion pipeline onderbroken voor 13 NRT video's

- **Eerste waarneming:** 2026-04-19 sessie (diagnose rapport)
- **Symptoom:**
  - `transcription-queue.service` loopt continu en verwerkt 13 NRT video's
  - Logmelding per video: `DONE nrt/{video}.mp4 (0s, N segments)`
  - Direct daarna: `WARNING Transcript not found for ingestion: /root/medical-rag/data/transcripts/{video}.json`
  - Gevolg: `[MARKER] ingest_failed: {video}.mp4 ingest FAILED`
  - 0 nieuwe vectors in `nrt_video_transcripts` voor deze 13 video's
- **Vermoedelijke root cause:**
  - De 13 video's zijn groot en zijn gesplitst in segmenten via ffmpeg (`_segments/` mappen bestaan)
  - Whisper heeft de segmenten getranscribeerd en opgeslagen als `{video}_partNNN.json`
  - `ingest_transcript.py` verwacht `{video}.json` (enkelvoudig) — de part-bestanden worden genegeerd
  - Er is geen merge-stap die de part-JSONs samenvoegt tot een enkel `{video}.json`
  - De "DONE (0s)" bevestigt dat transcription-queue de al-bestaande part-bestanden detecteert als "klaar" maar de ingest-stap mislukt omdat de gecombineerde JSON ontbreekt
- **Scope:** 13 NRT video's — nrt_video_transcripts mist deze transcripties. RAG-zoekopdrachten op NRT inhoud missen de grote NRT video's (alles behalve 7 eenvoudige video's).
- **Reproduceerbaar:** ja — elke restart van transcription-queue doorloopt dit exact
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `scripts/transcription_queue.py`; `scripts/ingest_transcript.py`; `data/transcripts/` (part-JSONs aanwezig)
- **Referenties:** journalctl -u transcription-queue (live, 2026-04-19 19:15)

---

### ISSUE-005 — 4 permanently failed book ingests

- **Eerste waarneming:** 2026-04-19 sessie (diagnose rapport); reeds in BACKLOG sessie 5
- **Symptoom:** 4 boeken worden door book_ingest_queue.py permanent overgeslagen met `Skip (permanently failed — manual intervention required)`. Ze blokkeren de queue niet maar genereren elke minuut een WARNING log.
- **Vermoedelijke root cause:** Parse-retry-count overschreden (3× gefaald). Oorspronkelijk gecategoriseerd als "FlexBeam marketing PDFs" na legacy cleanup sessie 5.
- **Scope:** 4 boeken, allen in `rlt_flexbeam` of `pemf_qrs`. Geen impact op gebruiksfunctionaliteit.
- **Reproduceerbaar:** ja
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** state.json van de betreffende hashes; `scripts/book_ingest_queue.py`
- **Referenties:** Sessie 5 BACKLOG, journalctl -u book-ingest-queue 2026-04-19

Betrokken boeken:
  - How to Use FlexBeam on Knees - Recharge Health.pdf (rlt_flexbeam)
  - How to Use FlexBeam on Neck - Recharge Health.pdf (rlt_flexbeam)
  - How to Use FlexBeam on Stomach - Recharge Health.pdf (rlt_flexbeam)
  - Levels Mat, Pillow, Pen.pdf (pemf_qrs) — tevens enige orphan (zie ISSUE-007)

---

### ISSUE-006 — 3 boeken in state.json maar ontbrekend in Qdrant

- **Eerste waarneming:** Maintenance report nachtrun 2026-04-19 00:31
- **Symptoom:** Nightly maintenance meldt `BOEK ONTBREEKT IN QDRANT` voor 3 boeken. Ze hebben een state.json maar geen vectoren in Qdrant (of onvoldoende).
- **Vermoedelijke root cause:** onbekend — te onderzoeken
- **Scope:** 3 boeken in medical_library. RAG-zoekopdrachten vinden de inhoud van deze boeken niet.
- **Reproduceerbaar:** onbekend
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `SYSTEM_DOCS/MAINTENANCE_REPORT.md`; state.json van de betreffende hashes

Betrokken boeken:
  - Orthopedic Physical Assessment 7e editie - Magee, Mansk... (manually_reviewed=True, title='ORTHOPEDIC PHYSICAL ASSESSMENT')
  - Touch for Health_ The Complete Edition_ A Practical Guide to Natural Health With Acupressure Touch_nodrm.pdf
  - Bates Guide to Physical Examination 14e editie - Bickley.epub (manually_reviewed=True)

**Noot:** test_acupuncture.pdf stond ook in de maintenance report maar is verwijderd in sessie 18 (uncommitted deletion aanwezig in git).

---

### ISSUE-007 — 1 orphan state.json zonder book_classifications entry

- **Eerste waarneming:** 2026-04-19 sessie inventarisatie
- **Symptoom:** 1 state.json bestand in `data/ingest_cache/` wordt niet gematcht door enige `filename_patterns` in `config/book_classifications.json`. Daardoor is er geen `library_category` of classificatie beschikbaar voor dit boek.
- **Vermoedelijke root cause:** Bestand is toegevoegd aan ingest-cache na een upload, maar de bijbehorende entry in book_classifications.json ontbreekt of heeft geen passend filename_pattern.
- **Scope:** 1 boek (Levels Mat, Pillow, Pen.pdf) — tevens permanently_failed (zie ISSUE-005)
- **Reproduceerbaar:** ja
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `data/ingest_cache/e4a45c224e71150e/state.json`; `config/book_classifications.json`

---

### ISSUE-008 — 43 state.json entries met lege of verdachte book_metadata.title

- **Eerste waarneming:** 2026-04-19 sessie inventarisatie
- **Symptoom:** 43 van 80 state.json bestanden hebben een lege, all-caps-korte, of 1-woord book_metadata.title.
- **Vermoedelijke root cause (lege titels — 40 entries):** NRT/QAT/RLT/PEMF PDFs zijn marketing-documenten zonder formele titelpagina. Gemini Vision heeft geen bruikbare metadata kunnen extraheren, of book_metadata-extractie is nooit uitgevoerd voor deze collecties.
- **Vermoedelijke root cause (verdachte titels — 3 medical_library entries):** Gemini Vision of handmatige invoer heeft een onvolledig resultaat opgeslagen.
- **Scope:**
  - 40 lege titels: rlt_flexbeam (21), nrt_curriculum (9), qat_curriculum (5), pemf_qrs (5) — impact op zoekresultaten en bibliotheekweergave
  - 3 medical_library: Applied Kinesiology (all-caps, geen manually_reviewed), WHOLE BRAIN LIVING (all-caps, manually_reviewed), Quantum-Touch (1 woord, manually_reviewed)
- **Reproduceerbaar:** ja — titels zijn statisch in state.json
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `data/ingest_cache/*/state.json` (book_metadata veld); Volledige lijst in DATA_SNAPSHOT_2026-04-19.md §4
- **VRAAG AAN ARCHITECT:** Is book_metadata-extractie via Gemini Vision bewust niet geconfigureerd voor nrt/qat/rlt/pemf collecties? En is de lege title voor deze korte marketing-PDFs acceptabel?

---

### ISSUE-009 — Drie foute titels in medical_library (correct: 1 niet-manually-reviewed)

- **Eerste waarneming:** Sessie 26 BACKLOG; bevestigd 2026-04-19 inventarisatie
- **Symptoom:**
  - `Applied Kinesiology - Frost.pdf` → title = `'APPLIED KINESIOLOGY'` (all-caps, **not** manually_reviewed) — dit is een fout
  - `Whole Brain Living...` → title = `'WHOLE BRAIN LIVING'` (all-caps, manually_reviewed=True) — architectbesluit
  - `Quantum-Touch_ The Power to Heal...` → title = `'Quantum-Touch'` (1 woord, manually_reviewed=True) — architectbesluit
- **Vermoedelijke root cause:** Gemini Vision-extractie voor Applied Kinesiology retourneerde all-caps string; handmatige invoer voor de andere twee.
- **Scope:** `/library` toont onjuiste titels. Applied Kinesiology is de enige die zeker gecorrigeerd moet worden. De twee manually_reviewed entries zijn in principe architect-beslissingen.
- **Reproduceerbaar:** ja
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `data/ingest_cache/{hash}/state.json` voor Applied Kinesiology
- **Referenties:** Sessie 26 BACKLOG

---

### ISSUE-010 — Drie databronnen voor hetzelfde boek lopen uit de pas (architectureel)

- **Eerste waarneming:** Sessies 5–7 (structurele diagnose); bevestigd 2026-04-19
- **Symptoom:** Voor elk boek zijn drie bronnen van waarheid:
  1. `data/ingest_cache/{hash}/state.json` — pipeline-status, metadata, filepath
  2. `config/book_classifications.json` — collectie-routing, K/A/I classificaties, title/authors
  3. Qdrant vector payloads — chunk-niveau metadata
  Deze drie kunnen divergeren (zie ISSUE-001, ISSUE-006, ISSUE-007).
- **Vermoedelijke root cause:** Architecturele beslissing in vroege sessies — drie aparte systemen zijn nooit geconsolideerd in één datamodel.
- **Scope:** Alle boeken, alle collecties. Fundamenteel probleem dat herstel van andere issues bemoeilijkt.
- **Reproduceerbaar:** ja
- **Status:** OPEN — niet hersteld; ontwerp BibliotheekRedesign-Design-v1 adresseert dit
- **Referenties:** Chat 3 (architect); Literatuuranalyse-BibliotheekRedesign-Design-v1 (NRT server)

---

### ISSUE-011 — Boekweergave inconsistent over /library, /library/ingest, /images

- **Eerste waarneming:** Sessies 6–7; bevestigd 2026-04-19 inventarisatie
- **Symptoom:** Drie UI-pagina's tonen boekinformatie met aparte logica en aparte databronnen, waardoor status en titels per pagina kunnen afwijken.
- **Vermoedelijke root cause:** Pagina's zijn afzonderlijk gebouwd zonder gedeeld datamodel.
- **Scope:** UI consistentie — architect ziet mogelijk verschillende statussen op verschillende pagina's.
- **Reproduceerbaar:** onbekend — niet systematisch getest in deze sessie
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `web/app.py` (meerdere routes)

---

### ISSUE-012 — Geen formele feedback loop Claude Code → Architect

- **Eerste waarneming:** Chat 3 (architect, 2026-04-19)
- **Symptoom:** Er is geen gestructureerd mechanisme waarmee Claude Code vragen, onzekerheden of architectuurbeslissingen escaleert naar de architect. Beslissingen worden soms impliciet gemaakt of als "onbekend" achtergelaten zonder escalatiepad.
- **Vermoedelijke root cause:** Governance-framework (DESIGN-Governance-v1) is nog niet uitgewerkt.
- **Scope:** Alle sessies — risico op stille drift of verkeerde implementaties.
- **Reproduceerbaar:** structureel
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** DESIGN_QUEUE.md (DESIGN-Governance-v1)
- **VRAAG AAN ARCHITECT:** Hoe wil je dat Claude Code onzekerheden/vragen markeert? Als sectie in OPEN_ISSUES.md? Als aparte QUESTIONS.md?

---

### ISSUE-013 — ttyd iframe laadt niet in /terminal pagina

- **Eerste waarneming:** eerder vermeld in BACKLOG
- **Symptoom:** ttyd service draait (port 7682, active), maar de iframe op `/terminal` laadt de terminal niet
- **Vermoedelijke root cause:** onbekend — te onderzoeken
- **Scope:** /terminal pagina onbruikbaar via browser
- **Reproduceerbaar:** onbekend — niet getest in deze sessie
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `web/app.py` /terminal route; ttyd.service

---

### ISSUE-014 — Google Drive MCP tools niet beschikbaar via ToolSearch

- **Eerste waarneming:** eerder vermeld in BACKLOG
- **Symptoom:** Google Drive MCP tools laden niet via de ToolSearch interface, waardoor documenten op de NRT server (sterfhuis) niet direct toegankelijk zijn vanuit Claude Code sessies.
- **Vermoedelijke root cause:** onbekend — te onderzoeken
- **Scope:** Migratie van NRT server analysebestanden geblokkeerd
- **Reproduceerbaar:** onbekend
- **Status:** OPEN — niet hersteld
- **Referenties:** Chat 3 (architect, 2026-04-19)

---

### ISSUE-015 — medical-rag-maintenance.service en medical-rag-tests.service tonen als "failed"

- **Eerste waarneming:** 2026-04-19 inventarisatie
- **Symptoom:** `systemctl list-units` toont beide services als `failed`. Maar de test-commit in git (`test: auto-report 2026-04-19 19:03 — 39/39 geslaagd`) bewijst dat de tests succesvol liepen. De maintenance report van 00:31 toont ⚠️ WARNING maar geen crash.
- **Vermoedelijke root cause:** Mogelijk exiteert een of beide services met non-zero exitcode. Maintenance toont WARNING-status → nightly_maintenance.py kan sys.exit(1) bij WARNING. Tests: run_tests.py exitcode onbekend. Alternatief: systemd one-shot pattern waarbij "failed" = "exited with non-zero".
- **Scope:** Visuele vervuiling in systemctl output. Mogelijk maskeert dit echte fouten.
- **Reproduceerbaar:** ja
- **Status:** OPEN — niet hersteld; root cause niet onderzocht
- **Gerelateerde bestanden:** `scripts/nightly_maintenance.py`; `scripts/run_tests.py`; systemd service files
- **VRAAG AAN ARCHITECT:** Is dit bekende gedrag? Moet run_tests.py sys.exit(0) forceren ongeacht testresultaat?

---

### ISSUE-016 — data/ingest_cache/ wordt niet automatisch gecommit

- **Eerste waarneming:** 2026-04-19 inventarisatie
- **Symptoom:** 45 uncommitted bestanden waarvan ~43 in `data/ingest_cache/`. Sync-status.timer commitsonly SYSTEM_DOCS/. De ingest_cache-wijzigingen (modified state.json, deleted legacy entries) stapelen op.
- **Vermoedelijke root cause:** sync_status.py voert `git add SYSTEM_DOCS/ && git commit` uit, niet `git add -A`. CLAUDE.md §State tracking zegt `git add -A` maar de timer-implementatie doet dat anders.
- **Scope:** ingest_cache state.json wijzigingen zijn niet in sync met GitHub. Na een server crash kunnen recente state-wijzigingen verloren gaan.
- **Reproduceerbaar:** ja
- **Status:** OPEN — niet hersteld
- **Gerelateerde bestanden:** `scripts/sync_status.py`; `data/ingest_cache/`
- **VRAAG AAN ARCHITECT:** Wil je dat ingest_cache/ ook automatisch wordt gecommit? Of is het bewust om bandbreedte/commit-frequentie te beperken?

---

## OPEN QUESTIONS (vragen aan architect — geen antwoord bekend)

1. **ISSUE-008 NRT/QAT/RLT/PEMF lege titels:** Is book_metadata-extractie bewust uitgeschakeld voor niet-medische collecties? Is een lege title acceptabel voor marketing-PDFs?
2. **ISSUE-012 Feedback loop:** Hoe wil je dat Claude Code escalatievragen markeert in toekomstige sessies?
3. **ISSUE-015 Service "failed" state:** Is het verwacht gedrag dat maintenance/tests services als "failed" tonen na een succesvolle run?
4. **ISSUE-016 ingest_cache commit:** Moet ingest_cache/ periodiek gecommit worden, of is de huidige SYSTEM_DOCS-only commit bewust?
5. **ISSUE-006 Ontbrekende boeken:** Zijn Touch for Health, Orthopedic PA, en Bates in de wachtrij voor herverwerking, of is er een blokkade?
6. **Design-prioriteit:** In welke volgorde moeten de ontbrekende design-documenten (zie DESIGN_QUEUE.md) worden opgepakt?
