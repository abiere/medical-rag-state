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
| transcription-queue | — | ⏸ Paused (35 videos waiting) |
| ttyd terminal | 7682 | ✅ Active |
| sync-status.timer | — | ✅ Every 5 min |
| queue-watchdog.timer | — | ✅ Every 10 min |

Restart web only: `systemctl restart medical-rag-web`

## Qdrant collections

| Collection | Embedding dims | Use |
|---|---|---|
| medical_library | 1024 | Books (PDF/EPUB) |
| video_transcripts | 1024 | Whisper transcripts |
| nrt_qat_curriculum | 1024 | QAT curriculum (empty — awaiting upload) |
| device_documentation | 1024 | PEMF/RLT docs (empty) |

**Embedding model: BAAI/bge-large-en-v1.5 (1024 dims)**
⚠ NOT nomic-embed-text — using nomic causes 0 RAG results.

## Key paths

```
/root/medical-rag/
├── web/app.py                    ← FastAPI — all routes
├── scripts/                      ← All pipeline scripts
├── books/                        ← PDFs/EPUBs by category
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
| /library/overview | Literature overview with audit scores |
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
