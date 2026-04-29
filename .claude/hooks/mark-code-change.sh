#!/bin/sh
# PostToolUse hook on Edit|Write. When a code file is changed, drop a marker
# so the Stop hook knows to demand HANDOFF.md / agent runs before completion.
# Exit 0 always — this is observational, not blocking.

INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', d.get('input', {}))
print(ti.get('file_path', ''))
" 2>/dev/null)

if [ -z "$FILE" ]; then exit 0; fi

case "$FILE" in
  *.py|*.cpp|*.h|*.ino|*.html|*.css|*.js)
    PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
    mkdir -p "$PROJECT_DIR/.claude"
    touch "$PROJECT_DIR/.claude/.needs-review"
    ;;
esac
exit 0
