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

The ADHD time blindness problem isn't reading a clock — it's that "11:00 standup" feels imaginary until 10:58. "Time blindness" itself decomposes into measurable, partly dissociable deficits — perceptual time estimation, time-based prospective memory, temporal/delay discounting, and a collapsed working-memory representation of future time horizons (Barkley, 1997, 2012; Altgassen et al., 2013; Jackson & MacKillop, 2016).

The full evidence-grounded principle set is in `PRD.md`. The headline ones the UI bakes in:

1. **Externalize time into the environment** — the unifying principle of CBT for adult ADHD: move regulatory information out of working memory and into a passive cue at the "point of performance" (Barkley, 2012; Solanto, 2011).
2. **Show time as a depleting resource** — countdown numerals and shrinking spatial elements, not abstract digital wall-clock time. One small RCT directly supports this for ADHD time-management (Janeslätt et al., 2017).
3. **Externalize the day's structure spatially** — vertical timeline showing where in the day you are, with completed slots distinct from upcoming ones (Barkley, 1997; CHADD, 2024).
4. **Surface "next," de-emphasize "later"** — time-based prospective memory is the single most consistently impaired PM type in ADHD (Altgassen et al., 2013).
5. **Escalate salience as deadlines approach** — counteracts temporal discounting; red is reserved for the imminent thing only (Jackson & MacKillop, 2016; Hauser et al., 2015).
6. **Peripheral resource, not attention demand** — no buzzer, no LED, no notifications. Smartphone notifications worsen inattention even in non-ADHD users (Kushlev et al., 2016); ADHD users habituate faster (Massa & O'Desky, 2012).

Tri-color discipline (paper / ink / red) is itself a salience budget — red marks one thing at a time so it stays meaningful.

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
