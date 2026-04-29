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
