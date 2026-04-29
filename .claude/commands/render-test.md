Render the calendar UI to a PNG using sample data, then inspect the result.

1. `cd eink-calendar/ui`
2. If first run ever, `pip install -r requirements.txt` and `playwright install chromium`. The Playwright Python package alone is not enough — the browser binary has to be installed separately.
3. `python render.py --sample --out /tmp/render-test.png`
4. Open `/tmp/render-test.png` so the user can see it: `open /tmp/render-test.png`
5. Verify with PIL: 800×480, ≤3 distinct colors, all colors match the e-ink palette `#EFEBDF`/`#1F1B16`/`#B83C2C` within ±1 per channel.
6. Report dimensions, color count, and any palette violations.

If the user asks for a live render (real Google Calendar), use `python render.py --live --out /tmp/render-test.png` instead — requires `token.json` from a prior `--auth` run.
