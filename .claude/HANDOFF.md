# Session Handoff

Last updated: 2026-04-29

## Last Session
1. Project infrastructure set up (CLAUDE.md, review agents, enforcement hooks, tracking files, commands).
2. Render pipeline verified end-to-end.
3. PRD rewritten to be evidence-grounded — eight cognitive principles with citations + anti-patterns + honest evidence-strength scoping. Literature synthesis saved to project memory.
4. Fixed `PALETTE-RED-LEAK` — `#6B645A` was quantizing to red because of RGB-distance to ink vs red. Replaced with `#4A4540`.
5. Added Principles 9 and 10 to the PRD: panel-resolution minimums (≥18px body, ≥16px CAPS labels with ≥0.1em tracking, ≥28px headlines, ≥92px hero, no strokes <2px, weight floor 500) and Teenage Engineering visual language (one mono family for all numerals, ALL CAPS labels, 6px corner radius, no shadows/gradients).
6. **Full UI redesign of `eink-calendar/ui/index.html` to match Principles 9 + 10.** Two-zone layout (504px NEXT hero + 276px today rail), JetBrains Mono numerals via Google Fonts, Inter labels in ALL CAPS, three escalation tiers for the next event (default → depletion-bar at <30 min → full red panel at <5 min). Past events show as dashed outlines (closes the past-event-dimming gap). Now-marker is a 12×40 red wedge on the rail's right edge — never crosses event text. Verified across three scenarios (standard, imminent at 3 min, late afternoon with past events).
7. Replaced `Image.quantize` with a saturation-aware classifier in `render.py` so anti-aliased text edges land in ink, not red. Fixed `document.fonts.ready` wait so webfonts load before screenshot.
8. Closed BUGS: `IMMINENT-NOOP` and `PALETTE-RED-LEAK`.

The actual product code (`eink-calendar/`) was already in place — render server, sample data, HTML canvas, firmware skeleton. Hardware not yet assembled.

## Open Bugs
See `BUGS.md`. Two open items carried in from initial state:
- **PNG decode is stubbed** — `firmware/src/main.cpp::fetch_and_decode` only sniffs 16 bytes; doesn't write to framebuffers.
- **Bitmap blit not wired** — `push_to_display` paints a placeholder string, not the fetched image.

## What's Next
The product README's "order of operations" is the sequence:
1. Hardware arrives → assemble per `docs/ASSEMBLY.md`
2. Wire per `docs/WIRING.md`
3. First UI render with sample data — already verified, repeat after any UI change
4. Implement streaming PNG decode (PNGdec lib) → fix the two open BUGS
5. Google OAuth setup → live calendar test
6. Power-up test on real device

**Resolved this session:**
- `PALETTE-RED-LEAK`: secondary text quantize-to-red, fixed.
- `IMMINENT-NOOP`: <5 min escalation now flips the hero to a full red panel.
- Past-event dimming: `state="past"` in view model + dashed outline CSS.
- Now-line crossing event titles: removed the line entirely; replaced with a 12×40 red wedge on the rail's right edge that never overlaps text.

**Still open in BUGS.md:**
- `PNG-DECODE-STUB`: firmware doesn't decode the fetched PNG. Blocker for first power-on. Needs streaming decoder (PNGdec recommended).
- `BLIT-PLACEHOLDER`: firmware draws placeholder text instead of bitmap. Wires up after PNG-DECODE-STUB.

## Parking Lot
- Render server deployment to a Pi or Cloudflare Worker (so calendar updates when laptop is closed)
- Proper "rest" view post-workday (currently a minimal "No more meetings today" placeholder)
- "Free between meetings" treatment for gaps >30 min on the rail
- Pomodoro / focus mode (long-press button) — opt-in only per PRD anti-pattern guidance
- Battery voltage display + low-battery warning at <3.6V
- 3D-printed enclosure with kickstand + window suction mount
- Self-host JetBrains Mono woff2 instead of relying on Google Fonts CDN — faster render, works offline, eliminates a network dependency in the render server
