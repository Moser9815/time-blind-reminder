# Bug Log

Every bug gets logged here the moment it's mentioned, before any fix attempt. Update with resolution after the fix.

## Format

```
### [SHORT-ID] One-line title
- **Reported**: YYYY-MM-DD
- **Status**: open | in-progress | fixed | wontfix
- **Severity**: blocker | high | medium | low
- **Where**: file:line or area
- **Symptom**: what's actually happening
- **Root cause**: (after diagnosis) the underlying reason
- **Fix**: (after fix) what was changed and why
```

---

## Open

### [PALETTE-RED-LEAK] Secondary text quantizes to red instead of ink
- **Reported**: 2026-04-29 (UI audit)
- **Status**: open
- **Severity**: high (silently violates PRD Principle 8 — "reserve red for one thing")
- **Where**: `eink-calendar/ui/index.html` — every reference to `#6B645A` (date label, NOW/NEXT/TODAY headers, hour labels on timeline, subtitle lines)
- **Symptom**: After `Image.quantize` in `render.py:215-222`, all secondary brown text snaps to red `#B83C2C`. Confirmed in render output — red has more pixels than ink (10,759 vs 8,839 in the sample render), which only makes sense if the labels are landing in red. Visually, the device looks awash in red rather than budgeted.
- **Root cause**: `#6B645A` (107, 100, 90) has RGB Euclidean distance ~98 to red (184, 60, 44) but ~125 to ink (31, 27, 22). The quantizer correctly picks red as the nearest palette color. The CSS color was chosen for browser preview without considering the quantizer's behavior — this is exactly the "browser preview lies" gotcha in CLAUDE.md.
- **Fix**: TODO. Two viable options: (a) replace `#6B645A` with a darker grey that quantizes to ink — `#4A4540` is RGB-distance ~73 to ink vs ~112 to red, would work; (b) use ink at reduced font-weight/size for hierarchy instead of a separate color. Option (a) is one search-replace; preferred. After fix, also update `.claude/hooks/check-palette.sh` allowlist (currently includes `#6B645A`).
- **Verify**: render with `python render.py --sample --out /tmp/x.png` then check that ink pixel count > red pixel count (red should only be the countdown numeral and the now-line marker).

### [IMMINENT-NOOP] The <5 min countdown escalation does nothing visually
- **Reported**: 2026-04-29 (UI audit)
- **Status**: open
- **Severity**: high (silently breaks PRD Principle 5 — "escalate salience as deadlines approach", in the most critical 5-minute window)
- **Where**: `eink-calendar/ui/index.html:325-327` — `.next-countdown.imminent` rule
- **Symptom**: When `minutesUntil < 5`, the only style change is `font-weight: 500`, but the base `.next-countdown` is already `font-weight: 500`. The class is a no-op. The countdown looks identical at 23 minutes and 3 minutes. Verified by rendering a sample with `now` near a meeting start.
- **Root cause**: The CSS rule was written but never given a meaningful visual delta.
- **Fix**: TODO. Give `.next-countdown.imminent` an actual treatment — candidates: paper-on-red block (red background, paper text), scale to ~110px, or a depleting horizontal bar inside the block. Whatever's chosen should be visually distinct from both the default 92px-red and the `.event.imminent` (which is paper-on-ink at 30-min threshold). Consider also adding a mid-tier escalation at <15 min.

### [PNG-DECODE-STUB] Firmware doesn't actually decode the PNG
- **Reported**: 2026-04-29 (acknowledged in source comment)
- **Status**: open
- **Severity**: blocker (nothing displays without it)
- **Where**: `eink-calendar/firmware/src/main.cpp::fetch_and_decode`
- **Symptom**: HTTP GET succeeds, function sniffs 16 bytes for debugging, returns true. The framebuffers never receive pixel data.
- **Root cause**: Streaming PNG decode is left as a TODO — the file comment recommends `bitbank2/PNGdec` (https://github.com/bitbank2/PNGdec).
- **Fix**: TODO. Must stream-decode row-by-row directly into 1bpp `bw_buffer` and `red_buffer` (mapping the 3-color palette to two 1bpp planes). Do NOT allocate a full RGBA buffer — won't fit in PSRAM alongside WiFi/HTTP stacks.

### [BLIT-PLACEHOLDER] Display shows placeholder text instead of fetched image
- **Reported**: 2026-04-29 (acknowledged in source comment)
- **Status**: open
- **Severity**: blocker
- **Where**: `eink-calendar/firmware/src/main.cpp::push_to_display`
- **Symptom**: Display draws "eink-calendar online" + boot count instead of the fetched calendar image.
- **Root cause**: `display.drawBitmap(bw_buffer, ...)` calls are stubbed pending PNG-DECODE-STUB fix.
- **Fix**: TODO. After PNG-DECODE-STUB, wire two `display.drawBitmap` calls — one for ink-on-paper plane, one for red plane. Order matters: paint ink first, red on top, since red shares the same bit position in the controller.

---

## Fixed

_(none yet)_
