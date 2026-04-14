# Claude Code — Standing Instructions for medical-rag

## State tracking

After every significant task, commit and push the updated project state:

```bash
git add PROJECT_STATE.md && git commit -m "state: [description of what was done]" && git push
```

`PROJECT_STATE.md` is the Architect's single source of truth for current server status. Keep it accurate — update the relevant sections (containers, models, books, pending tasks, known issues) before committing.
