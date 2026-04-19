# Claude Code — Standing Instructions for medical-rag

## System overview

Private, fully-local RAG system for medical/acupuncture literature.
**Server:** Hetzner CX53 — Tailscale only: `100.66.194.55`
**Repo:** https://github.com/abiere/medical-rag-state (private)
`/root/medical-rag` IS the repo. `/root/medical-rag-state` is a symlink to it.

## State tracking

After every significant task, commit and push:

```bash
cd /root/medical-rag && git add -A && \
git commit -m "state: [description]" && git push
python3 /root/medical-rag/scripts/sync_status.py
```

Keep `SYSTEM_DOCS/CONTEXT.md` and `SYSTEM_DOCS/BACKLOG.md` accurate — they are the session handover documents. Update them before committing.

## UI taken

Lees altijd eerst `.claude/skills/nrt-ui-standards/SKILL.md` via de Read tool voordat je HTML, CSS of UI-gerelateerde Python code schrijft. Dit bestand bevat de NRT kleurstandaarden (`#1A6B72` teal), componenten en schrijfregels.

De Skill tool werkt niet voor deze skill — gebruik direct: `Read("/root/medical-rag/.claude/skills/nrt-ui-standards/SKILL.md")`.

## Before any deploy

Run the full test suite and verify no failures:

```bash
python3 scripts/run_tests.py
```

Results are written to `SYSTEM_DOCS/TEST_REPORT.md`. Do not deploy if any test has status FAIL or ERROR. Skipped tests for uninstalled deps are acceptable.

## Running services

| Service | Port | State |
|---|---|---|
| FastAPI (medical-rag-web) | 8000 | ✅ Active |
| Qdrant | 6333 | ✅ Healthy |
| Ollama (llama3.1:8b) | 11434 | ✅ Active |
| book-ingest-queue | — | ✅ Active (systemd) |
| transcription-queue | — | ✅ Active (19 videos in queue) |
| ttyd terminal | 7682 | ✅ Active |
| sync-status.timer | — | ✅ Every 5 min |
| queue-watchdog.timer | — | ✅ Every 10 min |

Restart web only: `systemctl restart medical-rag-web`
**NEVER** restart book-ingest-queue during embedding — vectors will be lost.

## Qdrant collections

| Collection | Embedding dims | Use |
|---|---|---|
| medical_library | 1024 | Books (PDF/EPUB) — 10428 vectors |
| nrt_curriculum | 1024 | NRT curriculum (Lawrence Woods) — 425 vectors |
| qat_curriculum | 1024 | QAT curriculum — 125 vectors |
| rlt_flexbeam | 1024 | Red Light Therapy docs — 160 vectors |
| pemf_qrs | 1024 | PEMF QRS-101 docs — 64 vectors |
| nrt_video_transcripts | 1024 | NRT video transcripts — 241 vectors |
| qat_video_transcripts | 1024 | QAT video transcripts — 0 vectors |

**Embedding model: BAAI/bge-large-en-v1.5 (1024 dims)**
⚠ NOT nomic-embed-text — using nomic causes 0 RAG results.

## Key paths

```
/root/medical-rag/
├── web/app.py                    ← FastAPI — all routes
├── scripts/                      ← All pipeline scripts
├── books/
│   ├── medical_literature/       ← General medical PDF/EPUB
│   ├── nrt_curriculum/           ← NRT Lawrence Woods sources
│   ├── qat_curriculum/           ← QAT sources
│   ├── rlt_flexbeam/             ← FlexBeam RLT sources
│   └── pemf_qrs/                 ← PEMF QRS-101 sources
├── videos/nrt/ + qat/            ← 35 videos (paused)
├── data/
│   ├── transcripts/              ← Whisper JSON
│   ├── acupuncture_points/       ← 476 Deadman PNGs + point_index.json
│   ├── extracted_images/         ← Book figures
│   ├── book_quality/             ← Audit reports
│   └── protocols/                ← Generated .docx + metadata
├── config/
│   ├── book_classifications.json ← K/A/I per book (35 books, v1.1)
│   └── ai_instructions/          ← Protocol rules, meridian maps, tagging
├── SYSTEM_DOCS/
│   ├── CONTEXT.md                ← Session loader (read first)
│   ├── BACKLOG.md                ← Prioritised task list
│   └── LIVE_STATUS.md            ← Auto-synced status
└── .claude/
    ├── settings.json             ← Hooks config
    ├── skills/nrt-ui-standards/  ← Design system skill (read before UI work)
    └── hooks/
        ├── py_syntax_check.sh    ← PostToolUse: python3 -m py_compile
        └── security_check.sh     ← PreToolUse: secrets/injection scan
```

## Active hooks

| Event | Trigger | Script | Behaviour |
|---|---|---|---|
| PreToolUse | Write\|Edit\|MultiEdit | security_check.sh | Scans for hardcoded secrets/injection — warns, never blocks (exit 0) |
| PostToolUse | Write\|Edit\|MultiEdit | py_syntax_check.sh | Runs py_compile on .py files — exits 1 + shows error on failure |
| Stop | session end | mempalace_save.sh | Mines SYSTEM_DOCS into MemPalace palace |

## Active MCP servers (.mcp.json)

| Name | Command | Purpose |
|---|---|---|
| mempalace | `python3 -m mempalace.mcp_server` | Persistent memory — 116 drawers from SYSTEM_DOCS |
| playwright | `playwright-mcp --headless` | UI testing — Chromium headless against port 8000 |

## Active skills (.claude/skills/)

| Skill | Path | Auto-invoke when |
|---|---|---|
| nrt-ui-standards | skills/nrt-ui-standards/SKILL.md | Building any HTML page, UI component, or public content |

Read this skill before ANY UI task. Key tokens: teal `#1A6B72`, nav `NAV_ITEMS` single source of truth, table `th` background `#1A6B72`.

## Web interface routes

| Route | Description |
|---|---|
| / | Dashboard — CPU/RAM/services/Qdrant stats |
| /library | Catalog — 6 tabs, K/A/I badges, chunk counts, delete |
| /library/ingest | Upload + ingest queue + progress |
| /search | RAG search + image search + streaming |
| /images | Image browser + approval |
| /videos | Upload + transcription queue |
| /protocols | NRT protocol v3 + behandelprotocollen + generator |
| /terminal | ttyd browser terminal (port 7682) |

## Critical rules

1. **Nav:** `NAV_ITEMS` is the single source of truth. Never hardcode nav in individual page functions.
2. **Embedding:** Always use `BAAI/bge-large-en-v1.5` — never nomic-embed-text.
3. **Acupuncture notation:** HE / KID / LIV / P / SJ (Deadman standard). Never HT/KI/LV/PC/TW.
4. **Teal primary color:** `#1A6B72`. Never `#2563eb` for primary buttons/headers.
5. **Destructive actions:** Always show confirmation dialog with chunk count first.
6. **Terminology:** NRT-Amsterdam.nl (with hyphen + .nl). Never "NRT Amsterdam".

## HTML event handler standaard — ALTIJD VOLGEN

Gebruik NOOIT quotes van welke soort dan ook in JS event
handler attributen die via Python f-strings worden gegenereerd.
Dit geldt voor: onclick, oninput, onchange, onkeyup, onsubmit,
en ALLE andere on* attributen.

VERBODEN patronen in f-string gegenereerde HTML:
  onclick="myFunc('{var}')"      ← f-string var in quotes → escape hell
  oninput="...replace(/x/,'')"  ← '' → twee JS string literals → SyntaxError
  onclick="confirm('tekst')"     ← quotes in attribuut → SyntaxError
  onclick="myFunc(\"{var}\")"    ← dubbele quotes → attribuut eindigt te vroeg
  onchange="...'\n'..."          ← \n in f-string → literal newline → SyntaxError

VERPLICHTE patronen:
  Waarden doorgeven:    data-value="{var}" onclick="myFunc(this.dataset.value)"
  Lege string nodig:    gebruik named JS function in <script> blok
  Bevestiging:          data-msg="Weet je het zeker?" onclick="confirmAction(this)"
  Escape-sequenties:    nooit \n in f-string JS — gebruik \\n of named function

REGEL: Als een event handler iets anders bevat dan een
functienaam + this, is het bijna zeker fout.

GOED:   onclick="deleteBook(this)"
GOED:   oninput="stripNonNumeric(this)"
GOED:   onchange="onProviderChange(this)"
FOUT:   onclick="deleteBook('{hash}')"
FOUT:   oninput="this.value=this.value.replace(/[^0-9]/g,'')"

Reden: data-* attributen zijn veilig voor alle tekens.
JS template literals (${}) in backtick-strings zijn wél
toegestaan — die worden door de browser geëvalueerd.

## Pipeline diagram updates

After ANY change to these files:
- `scripts/parse_pdf.py`
- `scripts/claude_audit.py`
- `scripts/audit_book.py`
- `scripts/nightly_maintenance.py`
- `config/settings.json`

Always update `config/pipeline_diagrams.json`:
1. Re-read the changed file to extract current values
2. Update the relevant section:
   - `parse_pdf.py` → `pdf_type_detection` + `ocr_cascade` sections
   - `claude_audit.py` / `audit_book.py` → `audit` section
   - `nightly_maintenance.py` → `nightly.phases` section
   - `settings.json` → `nightly.start_time/end_time`, `audit.primary.model/workers`, `image_screen_limit`
3. Update `updated_at` to current ISO timestamp
4. Update `updated_by` to describe what changed, e.g. `"Claude Code — added PaddleOCR to OCR cascade"`

The PostToolUse hook `.claude/hooks/update_pipeline_diagrams.sh` calls
`GET /api/pipeline-diagrams/refresh` automatically, but also update
`pipeline_diagrams.json` manually when adding new engines or phases.

## SYSTEM_DOCS bestanden

| Bestand | Doel | Beheerder |
|---|---|---|
| `CONTEXT.md` | Session loader (max 150 regels) | Claude Code (handmatig) |
| `TECHNICAL.md` | Technische referentie pipeline + stack | Claude Code (handmatig) |
| `OPERATIONS.md` | Dagelijks gebruik + procedures | Claude Code (handmatig) |
| `BACKLOG.md` | Geprioriteerde takenlijst | Claude Code (handmatig) |
| `LIVE_STATUS.md` | Services + queue status | Auto: sync_status.timer (5 min) |
| `MAINTENANCE_REPORT.md` | Nachtrun rapport | Auto: nightly_maintenance.py |
| `TEST_REPORT.md` | Test resultaten | Auto: run_tests.py |
| `WATCHDOG_LOG.md` | Watchdog events | Auto: queue-watchdog.timer |
| `PRACTICE_CONTEXT.md` | Praktijk beschrijving + behandelwijzen | Handmatig bij praktijkwijzigingen |

**Orphan-vrij beleid:** Elk MD bestand heeft een duidelijke trigger hieronder of is auto-gegenereerd. Maak nooit een nieuw MD bestand zonder trigger toe te voegen aan deze sectie.

## Documentatie triggers

**Na ELKE significante taak:**
- Altijd: `SYSTEM_DOCS/BACKLOG.md` bijwerken (✅ item toevoegen aan Afgerond)
- Altijd: `SYSTEM_DOCS/LIVE_STATUS.md` via `python3 scripts/sync_status.py`

**Bij server/service wijzigingen:**
- `SYSTEM_DOCS/CONTEXT.md` → services tabel, Qdrant collectie stats bijwerken

**Bij pipeline codewijzigingen** (`parse_pdf.py`, `claude_audit.py`, `audit_book.py`, `nightly_maintenance.py`, `transcription_queue.py`):
- `SYSTEM_DOCS/TECHNICAL.md` → relevante sectie (§1 parse, §2 transcriptie, §3 nachtrun)
- `config/pipeline_diagrams.json` → via `/api/pipeline-diagrams/refresh`

**Bij UI/procedure wijzigingen** (`web/app.py`, routes, settings.json structuur):
- `SYSTEM_DOCS/OPERATIONS.md` → relevante procedure sectie
- `SYSTEM_DOCS/TECHNICAL.md` § 8 Web UI Pagina's

**Bij configuratie wijzigingen** (settings.json velden, book_classifications.json velden):
- `SYSTEM_DOCS/TECHNICAL.md` § 5 Configuratie Bestanden

**Bij nieuwe bekende issues of oplossingen:**
- `SYSTEM_DOCS/TECHNICAL.md` § 9 Bekende Issues & Oplossingen

**Bij praktijkwijzigingen** (behandelwijzen, QAT balancepunten, terminologie):
- `SYSTEM_DOCS/PRACTICE_CONTEXT.md`
- `SYSTEM_DOCS/CONTEXT.md` § Terminologie / QAT Balancepunten
- ⚠️ QAT Balancepunten zijn definitief april 2026 — NIET WIJZIGEN zonder expliciete instructie

**NOOIT** een nieuw orphan MD bestand aanmaken zonder trigger toe te voegen aan deze sectie.

## GitHub sync health check

At the start of every session, verify sync is working:

```bash
curl -s http://100.66.194.55:8000/api/status/sync | python3 -c "
import json,sys; d=json.load(sys.stdin)
print('push_ok:', d['push_ok'], '| timer:', d['timer_active'])
print('last_commit:', d['last_commit'])
if d['last_error']: print('ERROR:', d['last_error'])
"
```

Als `push_ok=false` of `timer_active=false`:
STOP en herstel sync eerst. Check:
1. `systemctl status sync-status.timer` — timer actief?
2. `git push` — credentials werkend?
3. `cat data/sync_errors.log` — exacte foutmelding

## Anti-hallucinatie regels

Deze regels zijn verplicht voor elke sessie — overtreding leidt
tot verkeerde opdrachten en verloren debugging-tijd.

### Lees voor je beweert
Nooit een uitspraak doen over hoe code werkt zonder het bestand
te hebben gelezen in deze sessie. Geheugen is onbetrouwbaar.

Verplichte leeslijst voor een opdracht:
  - CLAUDE.md (altijd)
  - Het/de bestand(en) die de opdracht raken (scripts/*.py, web/app.py)

### Diagnose-voor-fix patroon
Bij elke bug of onduidelijkheid:
  Stap 1 — Diagnose: lees de code, rapporteer de root cause
  Stap 2 — Fix: schrijf de fix op basis van de root cause
  Nooit direct fixen zonder diagnose.

### Geen aannames over limieten of configuratie
Limieten (chunk-aantallen, tijdvensters, max_workers etc.) lezen
uit de werkelijke code of config — nooit uit geheugen.

### State na elke significante taak
Na elke significante taak: ALTIJD updaten:
  1. SYSTEM_DOCS/BACKLOG.md (✅ item toevoegen)
  2. SYSTEM_DOCS/TECHNICAL.md (relevante sectie)
  3. SYSTEM_DOCS/LIVE_STATUS.md (via sync_status.py)
  4. Commit + push
