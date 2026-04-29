Health check the project. Run these in parallel where possible and summarize the results in a short status report.

1. **Python syntax** — `python3 -m py_compile eink-calendar/ui/render.py eink-calendar/ui/server.py`
2. **JSON validity** — `python3 -m json.tool eink-calendar/ui/sample_data.json > /dev/null`
3. **Sample render** — `cd eink-calendar/ui && python render.py --sample --out /tmp/check.png` (then `python3 -c "from PIL import Image; im = Image.open('/tmp/check.png'); print(im.size, len(im.getcolors() or []))"`)
4. **PlatformIO build** (if pio is installed) — `cd eink-calendar/firmware && pio run` ; otherwise note "pio not installed, skipping"
5. **Pin drift** — grep `PIN_EPD_*` in `firmware/platformio.ini` and compare against `firmware/src/main.cpp` and `docs/WIRING.md`. They must agree.
6. **Git status** — `git status` and call out any uncommitted changes to gitignored files (token.json, secrets.h, credentials.json should never appear here).
7. **Hook executability** — `ls -la .claude/hooks/` to confirm all `.sh` files have +x.

Report format: one line per check, ✅ or ❌. End with a one-line summary.
