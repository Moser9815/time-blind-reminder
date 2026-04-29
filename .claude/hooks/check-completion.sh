#!/bin/sh
# Stop hook. Runs when Claude tries to finish responding.
# Block completion if: code changes happened but HANDOFF.md wasn't updated,
# or if PLAN.md exists with unchecked items.
# Exit 2 = block. Exit 0 = let Claude finish.

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
MARKER="$PROJECT_DIR/.claude/.needs-review"
HANDOFF="$PROJECT_DIR/.claude/HANDOFF.md"
PLAN="$PROJECT_DIR/.claude/PLAN.md"

PROBLEMS=""

# Unchecked items in PLAN.md
if [ -f "$PLAN" ]; then
  if grep -q '^- \[ \]' "$PLAN" 2>/dev/null; then
    PROBLEMS="$PROBLEMS
  - .claude/PLAN.md has unchecked items. Either complete them or remove the plan if abandoned."
  fi
fi

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
  rm -f "$MARKER"
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
  5. Check off completed items in .claude/PLAN.md, or delete the plan if obsolete.
MSG
exit 2
