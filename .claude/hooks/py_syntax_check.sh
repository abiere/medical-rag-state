#!/bin/bash
# PostToolUse hook: run python3 -m py_compile on any .py file that was written or edited.
# Receives Claude tool-use JSON on stdin.
# Silent on success; prints the syntax error and exits non-zero on failure.

input=$(cat)

file_path=$(printf '%s' "$input" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))")

# Only act on .py files
[[ "$file_path" == *.py ]] || exit 0

# File must exist (could be a deletion or path mismatch)
[[ -f "$file_path" ]] || exit 0

output=$(python3 -m py_compile "$file_path" 2>&1)
rc=$?

if [ $rc -ne 0 ]; then
    echo "Syntax error in $file_path:"
    echo "$output"
    exit $rc
fi
