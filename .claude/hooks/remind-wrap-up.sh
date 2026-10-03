#!/bin/sh
# PostToolUse hook (Edit|Write): the first time code changes in a session, remind Claude
# of this project's wrap-up steps. Never blocks. Stores the session id so the
# reminder shows once per session.

INPUT=$(cat)
eval "$(echo "$INPUT" | python3 -c "
import sys, json, shlex
d = json.load(sys.stdin)
print('FILE=' + shlex.quote(d.get('tool_input', {}).get('file_path', '')))
print('SESSION=' + shlex.quote(d.get('session_id', '')))
" 2>/dev/null)"

case "$FILE" in
  *.py|*.cpp|*.h|*.ino|*.html|*.css|*.js) ;;
  *) exit 0 ;;
esac

# No session id means we can't dedupe — stay quiet rather than remind on every edit
[ -z "$SESSION" ] && exit 0
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
MARKER="$ROOT/.claude/.reminded-session"
[ "$(cat "$MARKER" 2>/dev/null)" = "$SESSION" ] && exit 0
printf '%s' "$SESSION" > "$MARKER"

cat <<'REMIND'
{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Code changed this session. When this work wraps up: update .claude/HANDOFF.md, log any bugs to BUGS.md, and if the user gave product direction, have the product-owner agent update PRD.md. For non-trivial changes, run the relevant review agents."}}
REMIND
exit 0
