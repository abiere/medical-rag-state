# Claude Code — Standing Instructions for medical-rag

## State tracking

After every significant task, commit and push the updated project state:

```bash
git add PROJECT_STATE.md && git commit -m "state: [description of what was done]" && git push
```

`PROJECT_STATE.md` is the Architect's single source of truth for current server status. Keep it accurate — update the relevant sections (containers, models, books, pending tasks, known issues) before committing.

## Before any deploy

Run the full test suite and verify no failures (skipped tests for uninstalled deps are acceptable):

```bash
python3 scripts/run_tests.py
```

Results are written to `SYSTEM_DOCS/TEST_REPORT.md`. Do not deploy if any test has status FAIL or ERROR.
