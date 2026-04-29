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

- `PALETTE-RED-LEAK` — **fixed** by replacing `#6B645A` with `#4A4540`. Render verified: ink now exceeds red. Doc drift cleaned up across 4 files. Two reviews (developer + ui-renderer) signed off clean.
- `IMMINENT-NOOP` — `.next-countdown.imminent` CSS does nothing visually. Breaks Principle 5 in the most critical 5-min window. Still open.

Design gaps (not bugs, future work):
- **Past events look identical to upcoming events on the timeline** — Principle 3 partial. Add `"past"` state in `derive_view_data` (`render.py:166-177`) + dimmed CSS for `.event.past`.
- **No "depleting" visual element** — Principle 2 partial. Numeric countdown alone doesn't convey "time as depleting resource." Consider a draining bar inside `.next-block` whose width tracks `(minutesUntil / windowMinutes)`.
- **All future events on timeline are equal weight** — Principle 4 partial. Apply opacity decay or strip titles past T+2h horizon in `renderTimeline()` (`index.html:373-391`).

What the UI gets right (verified by audit):
- Two-tier escalation architecture (.event.imminent at 30 min + .next-countdown.imminent at 5 min) is structurally correct, even though the leaf is broken.
- 92px red NEXT countdown vs 32px ink NOW title is the right pixel allocation per Altgassen et al. (next/prospective beats current/in-progress).
- Skipping all-day events in `render.py` is correct.

**Open from ui-renderer review (not regressions, queue for later):**
- Now-line crosses event titles in both standard and imminent renders, leaving a thin red rule across text. Functionally correct (now is inside the event) but a small typographic clash. Consider clipping the now-line behind the active event block, or breaking around the title.
- In the imminent render, the now-line crosses an ink-fill block, leaving a faint red bar across near-black. Same observation, separate-context decision needed.

**NEW direction (mid-session, not yet implemented):**
User wants the device redesigned with:
1. **Teenage Engineering aesthetic** (look and feel) — implies: monospace numerals, geometric sans labels with wide tracking + ALL CAPS, generous negative space, strong functional grid, hardware-control feel, limited-palette-as-code (which already aligns with our 3-color e-ink), rounded rectangles with consistent radii, no ornamental decoration.
2. **Designed for low pixel count** — current UI crams too much detail and uses elements that are too small, looking jagged after quantization. Need: bigger type, fewer elements, simpler shapes, generous padding, no thin strokes, 14pt+ minimum where possible at 800x480.

**Status**: PRD update with new principles + aesthetic direction is the next step. After PRD, audit current UI against the new direction to scope a redesign.

**Suggested order for next session:**
1. PRD updated with TE aesthetic + low-pixel-count principle (this session, in progress).
2. Re-audit current `index.html` against the new principles — likely substantial redesign.
3. Fix `IMMINENT-NOOP` as part of the redesign (since it's a visual-treatment decision).
4. Address the now-line/event-block clashes from this session's review.
5. Then tackle `PNG-DECODE-STUB` and `BLIT-PLACEHOLDER` when hardware is in hand.

## Parking Lot
- Render server deployment to a Pi or Cloudflare Worker (so calendar updates when laptop is closed)
- Empty-state mode (post-meetings, show tomorrow's first event)
- Pomodoro / focus mode (long-press button)
- Battery voltage display + low-battery warning at <3.6V
- 3D-printed enclosure with kickstand + window suction mount
