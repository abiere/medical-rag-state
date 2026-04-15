#!/bin/bash
# Usage: notify.sh "event_name" "Human readable message"
# Appends to /var/log/markers.json — kept to last 50 entries.
MARKER_FILE="/var/log/markers.json"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%S)
EVENT="${1:-unknown}"
MESSAGE="${2:-}"

python3 - <<PYEOF
import json
from pathlib import Path

f = Path("$MARKER_FILE")
data = json.loads(f.read_text()) if f.exists() else []
data.append({"event": "$EVENT", "message": "$MESSAGE", "timestamp": "$TIMESTAMP"})
data = data[-50:]
f.write_text(json.dumps(data, indent=2))
PYEOF

echo "[MARKER] ${EVENT}: ${MESSAGE}"
