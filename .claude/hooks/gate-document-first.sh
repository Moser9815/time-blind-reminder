#!/bin/sh
# PreToolUse hook on Edit|Write. Block code edits if no tracking doc has been
# touched in this session. After the first allowed edit, write a marker so
# subsequent edits aren't gated.
# Exit 2 = block.

INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', d.get('input', {}))
print(ti.get('file_path', ''))
" 2>/dev/null)

if [ -z "$FILE" ]; then exit 0; fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
MARKER="$PROJECT_DIR/.claude/.docs-verified"

# Already verified this session — let the edit through.
if [ -f "$MARKER" ]; then exit 0; fi

# Only gate code files. Edits to docs, configs, and tracking files are exempt.
case "$FILE" in
  *.py|*.cpp|*.h|*.ino|*.html|*.css|*.js)
    ;;
  *)
    # Edit is to a doc/config — touch the marker so subsequent code edits pass.
    if echo "$FILE" | grep -qE '(PLAN|BUGS|PRD|HANDOFF)\.md$|README\.md$'; then
      mkdir -p "$PROJECT_DIR/.claude"
      touch "$MARKER"
    fi
    exit 0
    ;;
esac

# Look for any tracking doc that's been modified in the last hour. If we see
# one, this code edit is fine and we set the marker.
RECENT=$(find "$PROJECT_DIR" -maxdepth 3 \
  \( -name "PLAN.md" -o -name "BUGS.md" -o -name "PRD.md" -o -name "HANDOFF.md" \) \
  -mmin -60 2>/dev/null | head -1)

if [ -n "$RECENT" ]; then
  mkdir -p "$PROJECT_DIR/.claude"
  touch "$MARKER"
  exit 0
fi

cat >&2 <<'MSG'
BLOCKED: code edit before documentation.

This project gates code on docs. Before editing code, update one of:
  - PRD.md (if user gave product direction)
  - BUGS.md (if you're fixing a bug — log it FIRST)
  - .claude/PLAN.md (for any multi-step task — write the plan FIRST)

Once a tracking doc is updated, this gate releases for the rest of the session.
If this is a one-line trivial fix and a plan really isn't warranted, say so to
the user and have them confirm before bypassing.
MSG
exit 2
