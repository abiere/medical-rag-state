#!/bin/bash
# Auto-triggered after editing pipeline-relevant files.
# Calls /api/pipeline-diagrams/refresh so the Schema's tab stays accurate.
TOOL_NAME="$1"
FILE_PATH="$2"

PIPELINE_FILES=(
  "parse_pdf.py"
  "claude_audit.py"
  "audit_book.py"
  "nightly_maintenance.py"
  "settings.json"
)

for f in "${PIPELINE_FILES[@]}"; do
  if [[ "$FILE_PATH" == *"$f"* ]]; then
    echo "Pipeline file changed: $f — refreshing diagrams..."
    curl -s -X GET http://localhost:8000/api/pipeline-diagrams/refresh \
      > /dev/null 2>&1 || true
    break
  fi
done

exit 0
