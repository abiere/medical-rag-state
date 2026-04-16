#!/bin/bash
# PreToolUse security hook: scan content being written/edited for secrets,
# command injection, and hardcoded credentials.
# Receives Claude tool-use JSON on stdin.
# NON-BLOCKING: always exits 0 — prints warnings but never blocks the write.

input=$(cat)

# Extract file path and content from the tool input
file_path=$(printf '%s' "$input" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))")

# Get content: 'content' (Write) or 'new_string' (Edit/MultiEdit)
content=$(printf '%s' "$input" \
  | python3 -c "
import json,sys
d = json.load(sys.stdin)
ti = d.get('tool_input', {})
print(ti.get('content') or ti.get('new_string') or '')
" 2>/dev/null)

# Nothing to check if no content
if [[ -z "$content" ]]; then
    exit 0
fi

warnings=()

# ── 1. Hardcoded secrets (API keys, tokens, passwords) ───────────────────────
# Pattern: KEY/TOKEN/SECRET/PASSWORD = "..." or : "..." with non-trivial value
while IFS= read -r match; do
    [[ -n "$match" ]] && warnings+=("⚠ Possible hardcoded secret: $match")
done < <(printf '%s\n' "$content" | grep -in \
    -E '(api_key|apikey|api_token|access_token|secret_key|auth_token|private_key|password|passwd|pwd)\s*[=:]\s*['"'"'"][^'"'"'"]{6,}['"'"'"]' \
    | head -5)

# ── 2. Hardcoded bearer/basic auth strings ────────────────────────────────────
while IFS= read -r match; do
    [[ -n "$match" ]] && warnings+=("⚠ Possible hardcoded auth header: $match")
done < <(printf '%s\n' "$content" | grep -in \
    -E 'Authorization:\s*(Bearer|Basic)\s+[A-Za-z0-9+/=]{8,}' \
    | head -3)

# ── 3. Command injection patterns (shell subshell + dangerous executables) ────
# Look for $(...) subshells or semicolons before dangerous commands in strings
while IFS= read -r match; do
    [[ -n "$match" ]] && warnings+=("⚠ Possible command injection: $match")
done < <(printf '%s\n' "$content" | grep -in \
    -E '\$\([^)]+\)' \
    | grep -v '^[[:space:]]*#' \
    | grep -v 'echo\|print\|format\|len\|str\|int\|f"' \
    | head -3)

while IFS= read -r match; do
    [[ -n "$match" ]] && warnings+=("⚠ Semicolon injection near shell command: $match")
done < <(printf '%s\n' "$content" | grep -in \
    -E ';\s*(rm\s+-|curl\s+http|wget\s+http|bash\s+-|nc\s+[0-9])' \
    | grep -v '^[[:space:]]*#' \
    | head -3)

# ── 4. Hardcoded public IP addresses (non-RFC-1918, non-loopback) ─────────────
while IFS= read -r match; do
    [[ -n "$match" ]] && warnings+=("⚠ Hardcoded public IP (use env var?): $match")
done < <(printf '%s\n' "$content" | grep -in \
    -E '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' \
    | grep -v '^[[:space:]]*#' \
    | grep -vE '(127\.|0\.0\.0\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|localhost|100\.66\.)' \
    | head -3)

# ── Report ─────────────────────────────────────────────────────────────────────
if [[ ${#warnings[@]} -gt 0 ]]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║  🔐 SECURITY CHECK — ${file_path##*/}"
    echo "╚══════════════════════════════════════════════════════╝"
    for w in "${warnings[@]}"; do
        echo "  $w"
    done
    echo ""
    echo "  File: $file_path"
    echo "  Action: write continues (non-blocking guardrail)"
    echo ""
fi

# Always exit 0 — warning-only hook
exit 0
