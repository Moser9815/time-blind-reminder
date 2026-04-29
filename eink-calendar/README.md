# Time Blind Reminder — E-Ink Calendar

Solar-powered e-ink Google Calendar display. Designed around ADHD time blindness — countdown over clock, time as space, glanceable from across a room. Lives on a windowsill or desk corner; refreshes every 15 minutes; runs forever on sun.

## Architecture

Two pieces, deliberately split:

- **Render server** (Python on your laptop or a Pi) — fetches Google Calendar events, renders the layout to an 800×480 PNG, serves it over HTTP.
- **Firmware** (ESP32-S3) — wakes every 15 minutes, GETs the PNG, pushes it to the e-ink panel, deep sleeps.

Splitting render from firmware lets you iterate on the UI in a normal browser (instant feedback, real fonts, no flash cycle) instead of in C++ on a microcontroller.

## When the parts arrive — order of operations

1. **Hardware assembly** (~30 min) — see `docs/ASSEMBLY.md`.
2. **Wiring** (~10 min) — see `docs/WIRING.md`. Eight wires from Feather to display.
3. **First UI render with sample data** (~10 min) — `cd ui && pip install -r requirements.txt && python render.py --sample --out test.png`. Open `test.png` and verify it looks right.
4. **Google Calendar OAuth** (~30 min) — see `docs/GOOGLE_API.md`.
5. **Live UI render** (~5 min) — `python render.py --live --out test.png`.
6. **Run the render server** — `python server.py` — exposes `http://localhost:8000/calendar.png`.
7. **Flash the firmware** (~15 min) — open `firmware/` in PlatformIO, edit `src/secrets.h` with your WiFi creds and the render server URL, flash to the Feather.
8. **Power up** — connect battery to charger, USB-disconnect, and watch the display refresh in ~15 seconds.

## Power budget (verified math)

| Phase | Current | Time | Charge |
|-------|---------|------|--------|
| Deep sleep | 10 µA | 14 min 45 s | 0.0025 mAh |
| Wake + WiFi + fetch + e-ink refresh | 120 mA | 15 s | 0.5 mAh |

96 cycles/day × 0.5 mAh ≈ **48 mAh/day consumed**.
2W solar × 5h sun behind glass × 50% loss ≈ **660 mAh/day generated**.
2500 mAh battery → multiple weeks of buffer through cloudy weeks.

See `docs/POWER.md` for the full math + sanity checks.

## Design rationale

The ADHD time blindness problem isn't reading a clock — it's that "11:00 standup" feels imaginary until 10:58. The UI fights this with three principles:

1. **Countdown beats clock.** "23 min" in giant red is the hero pixel allocation. Wall-clock time is small.
2. **Time as space.** The right side is a vertical day timeline — your remaining day becomes visible territory, not abstract numbers.
3. **Glanceable from 6+ feet.** Two zones (now/next on the left, today on the right). No icons. No clutter.

Tri-color e-ink (red) means "now" indicators stay quietly emphatic without decoration. The day timeline turns "I have 4 hours of meetings left" into something you *see* without reading.

## Project structure

```
eink-calendar/
├── README.md              # this file
├── docs/
│   ├── ASSEMBLY.md        # physical assembly walkthrough
│   ├── WIRING.md          # pin map, Feather ↔ Waveshare
│   ├── POWER.md           # power budget math + verification
│   ├── GOOGLE_API.md      # OAuth setup
│   └── UI_DESIGN.md       # design rationale, type sizes, color choices
├── hardware/
│   └── BOM.md             # bill of materials with verified links
├── ui/
│   ├── index.html         # standalone preview — open in browser
│   ├── render.py          # CLI: fetch calendar → render PNG
│   ├── server.py          # tiny HTTP server for the firmware
│   ├── sample_data.json   # mock events for offline iteration
│   └── requirements.txt
└── firmware/
    ├── platformio.ini
    └── src/
        ├── main.cpp       # Arduino-style sketch
        └── secrets.h      # WiFi + server URL (edit before flashing)
```

## What's still TODO when you finish this

- Render server deployment (right now it runs on your laptop — fine for testing, but you'll want it on a Pi or Cloudflare Worker eventually so the calendar updates when your laptop is closed).
- Empty-state mode (post-meetings, switch to a "rest" view showing tomorrow's first event).
- Pomodoro / focus mode (long-press the button).
- Battery voltage display (warn at <3.6V).
- 3D-printed enclosure with kickstand and window suction mount.
