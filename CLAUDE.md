# Time Blind Reminder

Solar-powered e-ink Google Calendar display for ADHD time blindness. Two halves: a Python render server (HTML → PNG) and ESP32-S3 firmware that fetches the PNG and pushes it to a Waveshare 7.5" tri-color e-paper panel.

## Architecture

The split is deliberate — UI iteration happens in a real browser, not on a microcontroller.

- `eink-calendar/ui/index.html` — design canvas, exactly 800×480 px, screenshotted by the renderer
- `eink-calendar/ui/render.py` — fetches Google Calendar, derives view model, screenshots `#canvas` via Playwright, quantizes to 3-color palette
- `eink-calendar/ui/server.py` — HTTP server the firmware GETs `/calendar.png` from
- `eink-calendar/ui/sample_data.json` — offline mock events so UI work doesn't need OAuth
- `eink-calendar/firmware/src/main.cpp` — Arduino-style sketch: wake → WiFi → HTTP GET → e-ink push → deep sleep
- `eink-calendar/firmware/src/secrets.h` — WiFi creds + render server URL (gitignored)
- `eink-calendar/firmware/platformio.ini` — pin assignments live in `build_flags`, NOT in source
- `eink-calendar/docs/` — assembly, wiring, power budget, OAuth, UI design rationale
- `eink-calendar/hardware/BOM.md` — verified parts list

## Patterns I Must Follow

**Pattern**: Pin assignments belong in `platformio.ini`
**Do**: Define `PIN_EPD_CS` etc. via `-D` build flags. Reference them by name in `main.cpp`.
**Don't**: Hardcode `8`, `9`, `10` in C++ source.
**Why**: Wiring docs (`docs/WIRING.md`), `platformio.ini`, and `main.cpp` must agree. One source of truth — the .ini file — makes it impossible to silently drift.

**Pattern**: Render math first, paint last
**Do**: All event derivation (current/next, minutes-left, timeline state) happens in `derive_view_data()` and is handed to the page as a flat view model. The HTML template is dumb and just lays out what it's given.
**Don't**: Compute `minutesUntil` or pick which event is "current" inside `index.html`.
**Why**: The renderer screenshots a static page. JS that queries `Date.now()` at screenshot time will give whatever the rendering laptop's clock says, not the time the firmware wakes. View model is computed once, server-side, with `now` baked in.

**Pattern**: Color through the palette, never raw hex
**Do**: Use `#EFEBDF` (paper), `#1F1B16` (ink), `#B83C2C` (red) — exactly the three colors in `EINK_PALETTE`.
**Don't**: Add `#666`, `#888`, gradients, drop shadows, or any color that won't survive `Image.quantize`.
**Why**: The render quantizes to a 3-color palette before the PNG is sent to the firmware. Anything else gets snapped to the nearest of those three and looks broken. UI changes that look great in the browser preview can fall apart after quantization — always inspect the post-quantize PNG, not the live `index.html`.

**Pattern**: Framebuffers must use PSRAM
**Do**: `heap_caps_malloc(W * H / 8, MALLOC_CAP_SPIRAM)` for both `bw_buffer` and `red_buffer`.
**Don't**: Stack-allocate, `malloc()`, or `new uint8_t[W*H/8]` — all of those go to the 320 KB SRAM.
**Why**: Two 48 KB framebuffers fit in SRAM individually but starve everything else (WiFi, HTTP, PNG decoder) of heap. The Feather S3 has 2 MB PSRAM specifically for this. `BOARD_HAS_PSRAM` is set in `platformio.ini`.

**Pattern**: Stream-decode the PNG, never buffer it whole
**Do**: Decode PNG row-by-row directly into the 1bpp `bw_buffer`/`red_buffer` as bytes arrive from `WiFiClient`.
**Don't**: Allocate an 800×480 RGBA buffer (1.5 MB) anywhere, even temporarily.
**Why**: 1.5 MB exceeds available PSRAM after framebuffers + WiFi stack are allocated. PNG decode currently has a TODO — when implementing, use a streaming decoder (PNGdec is recommended in the file comment) that calls back per-row.

**Pattern**: Skip all-day events in calendar fetch
**Do**: `if "dateTime" not in ev["start"]: continue` — these are date-only events without a time.
**Don't**: Try to render an all-day event on the timeline.
**Why**: The timeline is a working-hours rail (typically 9am–5pm). All-day events have no `dateTime`, only `date`, and would crash `fromisoformat` or render as a 24-hour bar.

**Pattern**: `secrets.h` is the only place credentials live in firmware
**Do**: Edit `firmware/src/secrets.h` for WiFi + `RENDER_URL`. The file is gitignored.
**Don't**: Hardcode in `main.cpp`, commit `secrets.h`, or define via `-D` build flags (those land in the binary metadata).
**Why**: The file is a deliberate seam: one place to grep, one place to gitignore, one place to swap when moving the device to a new network.

## Common Mistakes to AVOID

- **Mixing tz-aware and tz-naive datetimes** — `derive_view_data` strips tzinfo from `now` if events have it. If you change one, change both, or you'll get `TypeError: can't compare offset-naive and offset-aware datetimes` only on live data (sample data is always naive).
- **Trusting browser preview color** — `index.html` opened in Chrome shows hex colors faithfully. The PNG sent to the device has gone through `Image.quantize` with a 3-color palette and dithering disabled. Always inspect `test.png` after a UI change.
- **Forgetting `playwright install chromium`** — `pip install` brings the Playwright Python package but not the browser binary. First render fails with a missing-browser error; the fix is `playwright install chromium`, not pip.
- **Pulling battery while flashing** — the Feather S3 is powered through USB-C while flashing; if the LiPo charger is also connected, the charge IC and USB can fight. Disconnect battery before flashing, reconnect after.
- **Stripping `Z` from ISO timestamps with `.replace("Z", "")`** — current code does this in `derive_view_data` line ~123 to make `fromisoformat` work on Python <3.11. If we ever bump to 3.11+ and someone "cleans this up", the live calendar path breaks on Google's `Z`-suffixed timestamps.
- **Using `--no-verify` to push past hook failures** — hooks exist because something burned us. If a hook blocks an action, fix the underlying issue, don't bypass.

## Tracking Documents (Requirements, Not Suggestions)

These are gates. Document before coding. Update after coding. Never skip.

**Order: document → code → verify → document.**

- **PLAN** (`.claude/PLAN.md`) — Write before implementation begins for any multi-step task. Check off steps. Keep until verified by agents or user.
- **BUGS** (`BUGS.md`) — Log every bug IMMEDIATELY when mentioned, before any fix attempt. Update with resolution after fix.
- **PRD** (`PRD.md`) — When user gives product direction, invoke product-owner agent BEFORE implementing. Code against the written spec, not a verbal description.
- **Memory** — Save non-obvious learnings immediately when discovered, not batched.
- **HANDOFF** (`.claude/HANDOFF.md`) — Update after work is complete. Read at session start.

**Session start**: ALWAYS read `.claude/HANDOFF.md` first — it has what we were working on and what's next.

## Agent Strategy

Keep the main conversation lean. Delegate heavy work to agents.

- **Research/exploration** → Explore agent. Don't read 10 docs in main context.
- **Multi-step code changes** → main conversation with a written PLAN.
- **Independent investigations** → parallel agents (e.g. "is this a render bug or a quantize bug?").
- **Dependent steps** → sequential. Don't start step 2 until step 1 is verified.
- **Risky/experimental changes** → worktree agent (especially anything touching the firmware boot sequence).
- **Review and verification** → always agents. Never self-review — bias is inevitable.
- **Goal**: protect main context from bloat. Large context → compression → quality drops.

## Review Agents

After every fix, run all agents in `.claude/agents/` in parallel. Fix issues found, re-run until clean. Only report "done" after all pass.

- `developer-review` — code quality, dead code, race conditions
- `embedded-reviewer` — firmware-specific: power budget, PSRAM, watchdogs, deep sleep correctness
- `ui-renderer-reviewer` — palette compliance, view-model correctness, post-quantize visual check
- `product-owner` — PRD maintenance when user gives product direction

## Proactive Memory Updates

After resolving any non-trivial issue, IMMEDIATELY update memory files. Triggers: non-obvious bug fix, config discovery (especially around OAuth, PlatformIO, Playwright), failed workaround, stale memory.

## When I Make a Mistake

1. Reflect: what went wrong and why?
2. Abstract: what's the general pattern?
3. Update: add Do/Don't/Why to Patterns or entry to Common Mistakes
4. Save: update memory files immediately
