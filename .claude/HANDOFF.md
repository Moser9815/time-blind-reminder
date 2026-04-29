# Session Handoff

Last updated: 2026-04-29

## Last Session
1. Project infrastructure set up: CLAUDE.md, review agents (developer-review, embedded-reviewer, ui-renderer-reviewer, product-owner), enforcement hooks (destructive-guard, json/syntax/palette validators, document-first gate, completion gate), tracking files, commands (check, render-test, flash, wrap-up).
2. Render pipeline verified end-to-end — sample render produces 800×480 PNG with exactly 3 colors matching the e-ink palette.
3. **PRD rewritten to be evidence-grounded.** Replaced the original three intuition-based principles ("countdown beats clock", etc.) with eight principles, each tied to a specific cognitive deficit and a peer-reviewed source (Barkley, Altgassen, Janeslätt, Kushlev, Hauser, Sonuga-Barke). Added an Anti-patterns section with counter-evidence citations and an Evidence base section with honest scoping (most principles are clinical-consensus, not direct UI RCT). README's Design rationale section updated to match. Literature synthesis saved to memory at `time_blind_reminder_evidence_base.md`.

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

**UI work to consider against the new evidence-grounded principles** (see `PRD.md`):
- Current `index.html` has "countdown" and timeline. Does it explicitly de-emphasize "later" events relative to "next"? (Principle 4)
- Is salience escalation tied to time-until-event? Currently `imminent` state triggers when `minutesUntil < 30` — that's a hardcoded threshold; check whether it should be configurable. (Principle 5)
- "Time as depleting resource" — current countdown is numeric. Consider whether a shrinking visual element (bar, vanishing slot on the timeline) should accompany it. (Principle 2)
None of these are bugs; they're design audits worth doing once you can see the rendered PNG and assess.

## Parking Lot
- Render server deployment to a Pi or Cloudflare Worker (so calendar updates when laptop is closed)
- Empty-state mode (post-meetings, show tomorrow's first event)
- Pomodoro / focus mode (long-press button)
- Battery voltage display + low-battery warning at <3.6V
- 3D-printed enclosure with kickstand + window suction mount
