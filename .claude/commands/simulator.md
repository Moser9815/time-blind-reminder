---
description: Start the browser-based simulator at localhost:8000 — time-warp slider, live/sample toggle, auto-refresh
---

Run the digital simulator (browser-based preview server) so the user can iterate on the UI and Google Calendar integration without hardware.

1. `cd eink-calendar/ui`
2. `.venv/bin/python server.py` — listens on `:8000` by default. Use `--port 8765` if 8000 is busy.
3. Print: `open http://localhost:8000` so the user can click into the simulator.

The simulator page has:
- Live-rendering 800×480 device preview (the same PNG the firmware fetches)
- **Source toggle** — sample data vs live Google Calendar (live needs OAuth set up first; see `docs/GOOGLE_API.md`)
- **Time slider** (0–24:00) — scrub through the day, render updates on slider release
- **Quick-jump buttons** — 9:00, 10:30, 10:57 (imminent), 11:30, 1:00 PM, 4:30 PM (late afternoon)
- **Real now** — snap the slider to the actual current time
- **Auto-refresh** — Off / 5s / 30s

Background-running tip: `python server.py > /tmp/tbr-server.log 2>&1 &` to keep it running across sessions; `pkill -f "server.py"` to stop.

If the firmware contract endpoints break: `/calendar.png` with no params still returns the default render, `/health` still returns "ok". The simulator features (`/`, `?at=`, `?source=`) are additive.
