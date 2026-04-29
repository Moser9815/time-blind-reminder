# Session Handoff

Last updated: 2026-04-29

## Last Session
Project infrastructure set up: CLAUDE.md, review agents (developer-review, embedded-reviewer, ui-renderer-reviewer, product-owner), enforcement hooks (destructive-guard, json/syntax/palette validators, document-first gate, completion gate), tracking files (HANDOFF, BUGS, PRD seeded), commands (check, render-test, flash, wrap-up).

The actual product code (`eink-calendar/`) was already in place — render server, sample data, HTML canvas, firmware skeleton. Hardware not yet assembled.

## Open Bugs
See `BUGS.md`. Two open items carried in from initial state:
- **PNG decode is stubbed** — `firmware/src/main.cpp::fetch_and_decode` only sniffs 16 bytes; doesn't write to framebuffers.
- **Bitmap blit not wired** — `push_to_display` paints a placeholder string, not the fetched image.

## What's Next
The product README's "order of operations" is the sequence:
1. Hardware arrives → assemble per `docs/ASSEMBLY.md`
2. Wire per `docs/WIRING.md`
3. First UI render with sample data (`cd eink-calendar/ui && python render.py --sample --out test.png`) — likely first action when next session opens
4. Implement streaming PNG decode (PNGdec lib) → fix the two open bugs above
5. Google OAuth setup → live calendar test
6. Power-up test on real device

## Parking Lot
- Render server deployment to a Pi or Cloudflare Worker (so calendar updates when laptop is closed)
- Empty-state mode (post-meetings, show tomorrow's first event)
- Pomodoro / focus mode (long-press button)
- Battery voltage display + low-battery warning at <3.6V
- 3D-printed enclosure with kickstand + window suction mount
