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

**UI design audit completed against the eight principles. Findings:**

Two real bugs logged in `BUGS.md`:
- `PALETTE-RED-LEAK` — `#6B645A` quantizes to red, breaking Principle 8 (reserve red for one thing). Visible in any rendered PNG.
- `IMMINENT-NOOP` — `.next-countdown.imminent` CSS does nothing visually. Breaks Principle 5 in the most critical 5-min window.

Design gaps (not bugs, future work):
- **Past events look identical to upcoming events on the timeline** — Principle 3 partial. Add `"past"` state in `derive_view_data` (`render.py:166-177`) + dimmed CSS for `.event.past`.
- **No "depleting" visual element** — Principle 2 partial. Numeric countdown alone doesn't convey "time as depleting resource." Consider a draining bar inside `.next-block` whose width tracks `(minutesUntil / windowMinutes)`.
- **All future events on timeline are equal weight** — Principle 4 partial. Apply opacity decay or strip titles past T+2h horizon in `renderTimeline()` (`index.html:373-391`).

What the UI gets right (verified by audit):
- Two-tier escalation architecture (.event.imminent at 30 min + .next-countdown.imminent at 5 min) is structurally correct, even though the leaf is broken.
- 92px red NEXT countdown vs 32px ink NOW title is the right pixel allocation per Altgassen et al. (next/prospective beats current/in-progress).
- Skipping all-day events in `render.py` is correct.

**Suggested order for the next session:**
1. Fix `PALETTE-RED-LEAK` first — single search-replace in `index.html`, immediate large visual improvement, plus update `.claude/hooks/check-palette.sh` allowlist. Then re-render and confirm ink > red pixel count.
2. Fix `IMMINENT-NOOP` — pick a visual treatment for the <5 min state.
3. Tackle the design gaps in priority order (past events → depleting element → future-event decay).
4. Then tackle `PNG-DECODE-STUB` and `BLIT-PLACEHOLDER` when hardware is in hand.

## Parking Lot
- Render server deployment to a Pi or Cloudflare Worker (so calendar updates when laptop is closed)
- Empty-state mode (post-meetings, show tomorrow's first event)
- Pomodoro / focus mode (long-press button)
- Battery voltage display + low-battery warning at <3.6V
- 3D-printed enclosure with kickstand + window suction mount
