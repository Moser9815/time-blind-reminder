#!/bin/sh
# PostToolUse hook on Edit|Write. Block hex colors inside #canvas styles
# that aren't part of the e-ink 3-color palette. The bezel/preview-only
# section is exempt.
# Exit 2 = alert.

INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ti = d.get('tool_input', d.get('input', {}))
print(ti.get('file_path', ''))
" 2>/dev/null)

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then exit 0; fi

# Only check ui/index.html — that's the design canvas. CSS color in render.py
# is fine (the EINK_PALETTE constant).
case "$FILE" in
  */ui/index.html)
    ;;
  *)
    exit 0
    ;;
esac

# Allowed colors (case-insensitive):
#   #EFEBDF paper, #1F1B16 ink, #B83C2C red,
#   #6B645A muted grey (used for secondary text — survives quantize to ink),
#   #d0cec5 page background (outside canvas), #2A2724 bezel (outside canvas).
# Any other 3- or 6-digit hex is suspect.
BAD=$(python3 - "$FILE" <<'PY'
import re, sys, pathlib
allowed = {"#efebdf", "#1f1b16", "#b83c2c", "#6b645a", "#d0cec5", "#2a2724"}
text = pathlib.Path(sys.argv[1]).read_text()
hits = []
for m in re.finditer(r"#[0-9a-fA-F]{3,6}\b", text):
    color = m.group(0).lower()
    # Expand 3-digit shorthand to 6-digit for comparison
    if len(color) == 4:
        color = "#" + "".join(c*2 for c in color[1:])
    if color in allowed:
        continue
    line = text[:m.start()].count("\n") + 1
    hits.append(f"  line {line}: {m.group(0)}")
if hits:
    print("\n".join(hits))
    sys.exit(1)
PY
)
if [ $? -ne 0 ]; then
  echo "PALETTE VIOLATION in $FILE — colors outside the 3-color e-ink palette will look broken after quantize:" >&2
  echo "$BAD" >&2
  echo "Allowed: #EFEBDF (paper), #1F1B16 (ink), #B83C2C (red). Or #6B645A for muted text." >&2
  exit 2
fi
exit 0
