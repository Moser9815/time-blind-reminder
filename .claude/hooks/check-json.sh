#!/bin/sh
# PostToolUse hook on Edit|Write. Validate JSON files after edits.
# Exit 2 = alert (file already changed; fix immediately).

INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', d.get('input', {}))
print(ti.get('file_path', ''))
" 2>/dev/null)

if [ -z "$FILE" ]; then exit 0; fi

case "$FILE" in
  *.json)
    if [ -f "$FILE" ]; then
      ERR=$(python3 -m json.tool "$FILE" 2>&1 >/dev/null)
      if [ $? -ne 0 ]; then
        echo "INVALID JSON in $FILE — $ERR. Fix this before continuing." >&2
        exit 2
      fi
    fi
    ;;
esac
exit 0
