#!/bin/sh
# PostToolUse hook on Edit|Write. Syntax-check Python files after edits.
# Exit 2 = alert.

INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', d.get('input', {}))
print(ti.get('file_path', ''))
" 2>/dev/null)

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then exit 0; fi

case "$FILE" in
  *.py)
    ERR=$(python3 -m py_compile "$FILE" 2>&1)
    if [ $? -ne 0 ]; then
      echo "PYTHON SYNTAX ERROR in $FILE:" >&2
      echo "$ERR" >&2
      exit 2
    fi
    ;;
esac
exit 0
