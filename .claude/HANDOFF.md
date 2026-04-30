# Session Handoff

Last updated: 2026-04-30

## Last Session
1. Project infrastructure set up (CLAUDE.md, review agents, enforcement hooks, tracking files, commands).
2. Render pipeline verified end-to-end.
3. PRD rewritten to be evidence-grounded — eight cognitive principles with citations.
4. Fixed `PALETTE-RED-LEAK` — `#6B645A` was quantizing to red.
5. Added Principles 9 and 10 to the PRD (panel-resolution minimums + TE visual language).
6. First UI redesign with two-zone layout (504px NEXT hero + 276px today rail), JetBrains Mono numerals, three salience tiers, past-event dimming.
7. Replaced `Image.quantize` with a saturation-aware classifier so anti-aliased text edges land in ink.
8. Researched ADHD time-blindness literature deeply; user pushed back that the design was "shallow" — surfaced 8 higher-leverage adds tied to specific cognitive deficits.
9. Researched partial-refresh capability for the Waveshare 7.5" tri-color panel — discovered GxEPD2 supports `refresh_bw()` (~1-2 sec, no flash) on this controller. Capability sat unused. Saved to memory.
10. Pushed project to public GitHub: https://github.com/Moser9815/time-blind-reminder
11. Designed and built a Nothing × TE design-token system; rendered 10 hi-fi concepts at `/tmp/tbr-concepts.html`; user picked concepts 1 (dot matrix hero) and 7 (stacked typography); built 3 variations of each at `/tmp/tbr-variations.html`.
12. **Second redesign — variation 1B (grid day) is now the production layout.** Doto 240px hero on the left, 8×4 dot-grid on the right (32 cells × 15-min granularity over 8 working hours), salience escalation through cell-border color migration. PRD-10 updated to formally allow one display face (Doto) for the hero numeral.
13. Verified across all three scenarios (standard, imminent, late-afternoon). 3 colors only, ink leads red in all states.
14. Switched the technical mono family from Space Mono to JetBrains Mono (chunkier strokes at small sizes) and bumped all 16px text to 18px — at panel resolution Space Mono's thin glyphs were losing detail through quantization. Re-rendered all three scenarios; small text is now visibly cleaner.
15. **Built a digital simulator** — browser-based preview server at `/`. Auto-refresh, time-warp slider (scrub through the workday), source toggle (sample / live), quick-jump buttons. `?at=HH:MM` query param re-renders at any simulated time; `?source=live` switches to Google Calendar (requires OAuth setup). Stands in for hardware while it's in transit. Use the `/simulator` slash command (or `python server.py` from `ui/`).
16. Fixed an edge case in `derive_view_data`: events whose end equals `now` now correctly classify as past (changed `<` to `<=`). Surfaced by the simulator scrubbing to exactly the boundary of an event.
17. **Live Google Calendar integration ended up working through Apps Script + Chrome cookies.** Direct OAuth was blocked (no personal GCP allowed at Whirlpool). Apps Script web app deployed as "Anyone within Whirlpool Corporation" — can't accept Bearer tokens (Google issue #36763858), so render.py uses `browser-cookie3` to read Chrome's encrypted Whirlpool session cookies and authenticate via cookies. Working end-to-end: Apps Script → Chrome cookies → render.py → simulator. Real Whirlpool calendar rendering through the production code path. URL stored in gitignored `eink-calendar/ui/config.json`.
18. Fixed `_parse_local` for Apps Script's UTC-Z ISO format vs sample data's naive ISO. Both now parse correctly and end up as naive local datetimes for downstream comparison.
19. Fixed `classifyCell` overlap detection: current events extending into future cells now render as occupied (was treating them as future-empty). Surfaced by live data with multi-hour DNS blocks.
20. Decided to deploy render server on a Raspberry Pi 5 (4GB) for laptop-free operation. Hardware ordered (or to-order). Same Chrome-cookie auth model — Pi just runs always-on.

The actual product code (`eink-calendar/`) was already in place — render server, sample data, HTML canvas, firmware skeleton. Hardware (Feather S3 + Waveshare panel) not yet assembled.

## Open Bugs
See `BUGS.md`. Two open items carried in from initial state:
- **PNG decode is stubbed** — `firmware/src/main.cpp::fetch_and_decode` only sniffs 16 bytes; doesn't write to framebuffers.
- **Bitmap blit not wired** — `push_to_display` paints a placeholder string, not the fetched image.

## What's Next
**Two parallel hardware tracks:**

A) **Pi 5 4GB arrives** (the always-on render-server box):
1. Flash Pi OS, run OOBE
2. Install Chromium + Python deps + Playwright Chromium binary
3. Sign into Google in Chromium with `robert_s_moser@whirlpool.com`
4. Clone repo, set up venv, drop in `config.json` (with the Apps Script URL)
5. Test render → simulator on Pi works
6. Set up systemd service for auto-start + restart on failure
7. Static IP or hostname so the device firmware can find it

B) **Feather S3 + Waveshare panel arrive** (the actual e-ink device):
1. Hardware assembly per `docs/ASSEMBLY.md`
2. Wire per `docs/WIRING.md`
3. Implement streaming PNG decode (PNGdec lib) → fixes `PNG-DECODE-STUB`
4. Wire bitmap blit → fixes `BLIT-PLACEHOLDER`
5. Edit `firmware/src/secrets.h` with WiFi creds + Pi's URL
6. `pio run -t upload` → power-up test
7. Then iterate on partial-refresh logic for per-minute hero updates (see memory: `time_blind_reminder_partial_refresh.md`)

**Resolved this session:**
- `PALETTE-RED-LEAK`: secondary text quantize-to-red, fixed.
- `IMMINENT-NOOP`: <5 min escalation now flips the hero to a thick red frame; depletion bar visible at <30 min.
- Past-event dimming: now done by cell-state classification — past cells solid ink, future-event cells outlined with inner-square mark.
- Now-line crossing event titles: rail concept dropped entirely in 1B redesign — now-cell on the grid is just a red filled cell, no line crossing anything.

**Still open in BUGS.md:**
- `PNG-DECODE-STUB`: firmware doesn't decode the fetched PNG. Blocker for first power-on. Needs streaming decoder (PNGdec recommended).
- `BLIT-PLACEHOLDER`: firmware draws placeholder text instead of bitmap. Wires up after PNG-DECODE-STUB.

**Future work surfaced this session (not yet logged as bugs):**
- Adaptive refresh cadence (5-min adaptive in active windows, 1-min via partial B/W in last 30 min) — needs firmware logic + an HTTP header from the render server hinting `next_refresh_seconds`.
- Implementation-intentions surfacing (per-event prep checklist parsed from calendar event description).
- Hyperfocus-aware empty state (large elapsed-time display when next event is >2 hours away).
- Partial B/W refresh for the hero numeral + depletion bar (per-minute updates without flash). Capability is in GxEPD2's `refresh_bw()` for this exact panel — see memory file.

## Parking Lot
- Filter `DNS` / `OOO` events from the rail (config-driven `filter_titles` list, applied in Apps Script for cleanliness)
- Bump working hours to 7-19 to capture early-morning DNS and after-hours personal events
- Multi-calendar support — add `c_e7da71...@group.calendar.google.com` (DLT travel/WFH schedule) to `CALENDARS` in `Code.gs`
- Smarter title truncation in Apps Script (e.g., drop parenthetical suffixes like "(HA/DR/VA)")
- Proper "rest" view post-workday (currently a minimal "No more meetings today" placeholder)
- "Free between meetings" treatment for gaps >30 min on the rail
- Pomodoro / focus mode (long-press button) — opt-in only per PRD anti-pattern guidance
- Battery voltage display + low-battery warning at <3.6V
- 3D-printed enclosure with kickstand + window suction mount
- Self-host JetBrains Mono woff2 instead of relying on Google Fonts CDN — faster render, works offline, eliminates a network dependency in the render server
- Adaptive refresh cadence (5-min adaptive in active windows, 1-min via partial B/W in last 30 min) — render server hints `next_refresh_seconds` via HTTP header; firmware reads it
- Implementation-intentions surfacing (per-event prep checklist parsed from calendar event description)
- Hyperfocus-aware empty state (large elapsed-time display when next event is >2 hours away)
