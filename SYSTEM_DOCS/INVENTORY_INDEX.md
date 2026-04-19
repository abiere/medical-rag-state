# INVENTORY INDEX — SYSTEM_DOCS/
> Opgesteld: 2026-04-19 | Status: documentatie — geen wijziging
> Herstel komt later. Dit bestand legt vast wat er is.

---

## Index van inventarisdocumenten

| Bestand | Type | Beschrijving |
|---|---|---|
| [DATA_SNAPSHOT_2026-04-19.md](DATA_SNAPSHOT_2026-04-19.md) | Inventaris | Objectieve momentopname data: Qdrant, state.json, classifications, transcripts, video's |
| [OPEN_ISSUES.md](OPEN_ISSUES.md) | Probleemregistratie | Alle bekende open issues (ISSUE-001 t/m ISSUE-016) — geen herstel |
| [DESIGN_QUEUE.md](DESIGN_QUEUE.md) | Design tracking | Welke design-documenten bestaan, welke ontbreken |
| [BACKLOG.md](BACKLOG.md) | Takenlijst | Geprioriteerde werklijst + volledig afgeronde sessiehistorie |
| [INVENTORY_INDEX.md](INVENTORY_INDEX.md) | Dit bestand | Index van alle inventaris- en werkdocumenten |

---

## Alle .md bestanden in SYSTEM_DOCS/ (momentopname 2026-04-19 ~19:20 UTC)

| Bestand | Regels | Laatste wijziging | Beheerder |
|---|---|---|---|
| AI_STATUS.md | 21 | 2026-04-19 19:14 | Auto: sync_context.py |
| BACKLOG.md | 1099 | 2026-04-19 10:07 | Claude Code (handmatig) |
| CONTEXT.md | 114 | 2026-04-19 19:14 | Auto: sync_context.py |
| DATA_SNAPSHOT_2026-04-19.md | — | 2026-04-19 (nieuw) | Claude Code (inventarisatie) |
| DESIGN_QUEUE.md | — | 2026-04-19 (nieuw) | Claude Code (inventarisatie) |
| INVENTORY_INDEX.md | — | 2026-04-19 (nieuw) | Claude Code (inventarisatie) |
| LIVE_STATUS.md | 72 | 2026-04-19 19:10 | Auto: sync_status.timer (5 min) |
| MAINTENANCE_REPORT.md | 372 | 2026-04-19 00:45 | Auto: nightly_maintenance.py |
| OPEN_ISSUES.md | — | 2026-04-19 (nieuw) | Claude Code (inventarisatie) |
| OPERATIONS.md | 132 | 2026-04-17 06:16 | Claude Code (handmatig) |
| PRACTICE_CONTEXT.md | 113 | 2026-04-14 16:17 | Handmatig |
| TECHNICAL.md | 321 | 2026-04-17 20:22 | Claude Code (handmatig) |
| TEST_REPORT.md | 81 | 2026-04-19 19:03 | Auto: run_tests.py |
| WATCHDOG_LOG.md | 19 | 2026-04-19 19:14 | Auto: queue-watchdog.timer |
| entities.json | 179b | 2026-04-16 12:54 | MemPalace intern |
| mempalace.yaml | 89b | 2026-04-16 12:54 | MemPalace intern |

### Observaties op SYSTEM_DOCS inhoud

- **CONTEXT.md** — 114 regels, correct (max 150). Qdrant-counts kloppen met live data. ✅
- **BACKLOG.md** — 1099 regels. Structuur groeit onbeheersbaar. Open issues zijn verstopt tussen afgeronde items. → Herschreven versie in dit commit.
- **TECHNICAL.md** — Laatste update 2026-04-17. Twee sessies stale (sessies 18–26 niet bijgewerkt).
- **OPERATIONS.md** — Laatste update 2026-04-17. Twee sessies stale.
- **MAINTENANCE_REPORT.md** — Nachtrun 19-apr 00:31, uitslag ⚠️ WARNING. 4 boeken ontbreken in Qdrant. 93 pip-pakketten verouderd.
- **CLAUDE.md** (repo root, niet in SYSTEM_DOCS/) — Qdrant-counts stale (zie ISSUE-001). Verwijzing naar niet-bestaande `medical-rag-sync.timer` (zie ISSUE-002).

---

## Nieuw toegevoegd in dit commit (documentatie — geen herstel)

| Bestand | Reden aanmaak |
|---|---|
| INVENTORY_INDEX.md | Trigger: CLAUDE.md "Orphan-vrij beleid" — dit bestand heeft trigger: inventarisatie sessie 2026-04-19 |
| DATA_SNAPSHOT_2026-04-19.md | Trigger: inventarisatie sessie 2026-04-19 |
| OPEN_ISSUES.md | Trigger: inventarisatie sessie 2026-04-19 — vervangt verstrooide issue-vermeldingen in BACKLOG.md |
| DESIGN_QUEUE.md | Trigger: inventarisatie sessie 2026-04-19 — design-tracking ontbrak |
