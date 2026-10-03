#!/bin/sh
# Stop hook. Runs when Claude tries to finish responding.
# Block completion if code changes happened but HANDOFF.md wasn't updated since.
# An unfinished PLAN.md is a reminder only (never blocks on its own) — plans can
# legitimately span sessions, and blocking every reply on them traps Claude.
# Exit 2 = block. Exit 0 = let Claude finish.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
MARKER="$PROJECT_DIR/.claude/.needs-review"
HANDOFF="$PROJECT_DIR/.claude/HANDOFF.md"
PLAN="$PROJECT_DIR/.claude/PLAN.md"

PROBLEMS=""

# Code changed this session — was HANDOFF.md updated?
if [ -f "$MARKER" ]; then
  # HANDOFF must exist and be newer than the marker.
  if [ ! -f "$HANDOFF" ]; then
    PROBLEMS="$PROBLEMS
  - .claude/HANDOFF.md is missing. Update it with what you did and what's next."
  elif [ "$MARKER" -nt "$HANDOFF" ]; then
    PROBLEMS="$PROBLEMS
  - Code changed but .claude/HANDOFF.md wasn't updated since. Update Last Session, Open Bugs, What's Next."
  fi
fi

if [ -z "$PROBLEMS" ]; then
  # Clean exit — clear the marker so the next session starts fresh.
  rm -f "$MARKER" "$PROJECT_DIR/.claude/.docs-verified"
  exit 0
fi

cat >&2 <<MSG
BLOCKED: cannot finish yet.
$PROBLEMS

Before finishing you must:
  1. Run review agents from .claude/agents/ in parallel and address findings.
  2. Update .claude/HANDOFF.md (Last Session, Open Bugs, What's Next).
  3. Log any bugs found or discussed to BUGS.md.
  4. If user gave product direction, invoke product-owner agent to update PRD.md.
  5. Check off completed items in .claude/PLAN.md (unchecked items for later sessions are fine).
MSG
exit 2
