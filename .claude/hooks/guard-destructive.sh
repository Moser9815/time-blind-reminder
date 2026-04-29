#!/bin/sh
# PreToolUse hook on Bash. Block obviously destructive commands.
# Exit 2 = block. Exit 0 = allow. Never use exit 1 (silently dropped).

INPUT=$(cat)
CMD=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', d.get('input', {}))
print(ti.get('command', ''))
" 2>/dev/null)

if [ -z "$CMD" ]; then exit 0; fi

# rm -rf with broad targets
case "$CMD" in
  *"rm -rf /"*|*"rm -rf ~"*|*"rm -rf \$HOME"*|*"rm -rf *"*)
    echo "BLOCKED: refusing rm -rf with broad target. If you really need this, run it yourself." >&2
    exit 2
    ;;
esac

# git push --force on main
case "$CMD" in
  *"git push --force"*|*"git push -f"*)
    case "$CMD" in
      *" main"*|*" master"*|*"origin main"*|*"origin master"*)
        echo "BLOCKED: refusing force-push to main/master. Confirm with the user." >&2
        exit 2
        ;;
    esac
    ;;
esac

# git reset --hard, git clean -fd, git checkout . — all overwrite uncommitted work
case "$CMD" in
  *"git reset --hard"*|*"git clean -fd"*|*"git clean -f "*|*"git checkout ."*|*"git checkout -- ."*|*"git restore ."*)
    echo "BLOCKED: this discards uncommitted changes. Confirm intent with the user before running it." >&2
    exit 2
    ;;
esac

# --no-verify bypasses our hooks
case "$CMD" in
  *"--no-verify"*|*"--no-gpg-sign"*)
    echo "BLOCKED: --no-verify / --no-gpg-sign bypasses safety checks. Fix the underlying issue instead." >&2
    exit 2
    ;;
esac

# Stamping over secrets.h
case "$CMD" in
  *"> "*"secrets.h"*|*">> "*"secrets.h"*)
    echo "BLOCKED: don't overwrite firmware/src/secrets.h via shell redirect — edit it explicitly." >&2
    exit 2
    ;;
esac

exit 0
