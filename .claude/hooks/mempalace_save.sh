#!/bin/bash
# Stop hook: mine key project documentation into MemPalace at session end.
# Keeps the memory palace current with CONTEXT.md, BACKLOG.md, LIVE_STATUS.md.

PALACE_DIR="/root/.mempalace/medical-rag"
DOCS_DIR="/root/medical-rag/SYSTEM_DOCS"

# Ensure palace is initialized (idempotent with --yes)
if [[ ! -f "$DOCS_DIR/mempalace.yaml" ]]; then
    python3 -m mempalace.cli --palace "$PALACE_DIR" init --yes "$DOCS_DIR" 2>/dev/null
fi

# Mine updated docs into the palace
python3 -m mempalace.cli --palace "$PALACE_DIR" mine "$DOCS_DIR" 2>/dev/null

exit 0
