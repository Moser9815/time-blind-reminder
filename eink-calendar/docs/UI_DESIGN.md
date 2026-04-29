# UI design rationale

## The problem

ADHD time blindness is not "I can't read a clock." It's "10:45 doesn't feel close to 11:00 until I'm already late." The future stays abstract; transitions sneak up; hyperfocus eats hours invisibly. A calendar that just *displays events* doesn't help — you already see them in your phone.

What helps is making time **visceral, spatial, and unavoidable**.

## Three principles

### 1. Countdown beats clock

"23 min" is a stronger time prompt than "11:00." The countdown answers the question your brain is actually asking: *how much time do I have?* — without requiring any subtraction. It also forces an emotional update: at 25 it's "fine"; at 5 it's "go now"; at 1 it's "running."

The hero pixel allocation — 92pt red type — is the countdown to the next event. Wall-clock time of that event is small (18pt, muted) underneath, present but secondary. The current time of day is in 20pt at the top corner — there for orientation, not emphasis.

### 2. Time as space

The right side of the screen is a vertical day timeline from morning to evening. Each hour is a fixed vertical interval. Meetings appear as filled rectangles whose height encodes their duration. A red horizontal line marks "now."

This makes the day a physical object. "I have a wall of meetings this afternoon" becomes literally visible as a wall. "I have nothing until 3" becomes a visible expanse of empty timeline. From across the room you don't read the screen — you *see* the shape of your day.

### 3. Glanceable from 6+ feet

The two-zone layout (now/next on the left, today on the right) means there's never a question of where to look. The hero countdown is readable from across a small office. Event titles in the timeline are small but still legible at desk distance. No icons to decode, no icons to ignore, no toolbar.

## Layout

Total canvas: 800 × 480 (the panel's native resolution).

```
0                                460  470               800
┌─────────────────────────────────┬───┬──────────────────┐ 0
│  10:37 am · Wed, Apr 29         │   │ TODAY            │
│                                 │   │                  │
│  NOW                            │   │ 9 am ───────     │
│  Design review with Sara        │   │                  │
│  Ends in 13 min · 10:50         │   │ 10  ─────────    │
│                                 │   │ ▓ Design review  │
│  ─────────────────              │ │ │ ─── now ─────    │
│                                 │   │ 11  ─────────    │
│  NEXT                           │   │ █ Standup        │
│  Standup                        │   │ 12  ─────────    │
│                                 │   │ ░ Lunch          │
│      23 min                     │   │ 1pm ─────────    │
│                                 │   │ ░ Focus block    │
│  at 11:00 am · with team-eng    │   │ ░                │
│                                 │   │ 2  ─────────     │
│                                 │   │                  │
│                                 │   │ 3  ─────────     │
│                                 │   │ █ 1:1 with Alex  │
│                                 │   │ 4  ─────────     │
└─────────────────────────────────┴───┴──────────────────┘ 480
```

## Type scale

> **Note (2026-04-29):** PRD Principle 9 (Designed at panel resolution) sets concrete minimums that several entries below violate. The "PRD-9 min" column flags compliance. Values that fail are flagged ⚠ — the table records the *current* spec; the implementation gap should be closed in a redesign session, not patched ad hoc. Weight floor under PRD Principle 9 is 500 (no 400 weights).

| Element | Size | Weight | Color | PRD-9 min | OK? |
|---------|------|--------|-------|-----------|-----|
| Section labels (NOW, NEXT, TODAY) | 14pt | 500 | #4A4540 (muted) | ≥16px CAPS, ≥0.1em track | ⚠ undersize |
| Clock + date | 20pt | 500 | #1F1B16 (ink) | ≥18px | OK |
| Current event title | 32pt | 500 | #1F1B16 | ≥28px headline | OK |
| Current event subtitle | 20pt | 400 | #4A4540 | ≥18px, weight ≥500 | ⚠ weight |
| Next event title | 28pt | 500 | #1F1B16 | ≥28px headline | OK |
| **Hero countdown** | **92pt** | **500** | **#B83C2C (red)** | ≥92px | OK |
| Next event subtitle | 18pt | 400 | #4A4540 | ≥18px, weight ≥500 | ⚠ weight |
| Timeline hour labels | 13pt | 400 | #4A4540 | ≥16px CAPS label | ⚠ undersize, weight |
| Timeline event titles | 12pt | 500 | #1F1B16 | ≥18px body | ⚠ undersize |
| Timeline event time-of-day | 11pt | 400 | #4A4540 | ≥18px body, weight ≥500 | ⚠ undersize, weight |

Two weights only (400 regular, 500 medium) — *legacy*; PRD-9 now floors weight at 500 across the whole canvas, so 400 should be retired in the next pass. Three colors at design time (ink, muted, red); after quantize the muted `#4A4540` snaps to ink, leaving exactly two colors on screen plus the red accent. E-ink doesn't do gradients or shadows, so the typographic hierarchy has to do all the work — the muted color exists for browser-preview legibility and disappears in the final render. **Do not use `#6B645A` or any color with smaller RGB-distance to red than to ink — it will quantize to red and break the salience budget (see `BUGS.md` PALETTE-RED-LEAK).**

## Typography family

PRD Principle 10 calls for a Teenage-Engineering-style pairing: a single geometric-sans / monospace family for *all* numerals, and a clean uppercase sans for labels.

- **Numerals** (clock, countdown, hour ticks, durations): pick ONE of — JetBrains Mono, Berkeley Mono, NB Architekt, IBM Plex Mono, Suisse Int'l Mono — and use it everywhere a digit appears. Tabular figures required (`font-feature-settings: "tnum" 1`, already enabled on `#canvas` in the current `index.html`). The countdown and timeline ticks must share the same family so they read as one product.
- **Labels** (NOW, NEXT, TODAY, "now" tag, hour suffixes like `am` / `pm`): same family as numerals OR a paired uppercase sans. ALL CAPS, ≥0.1em letter-spacing, weight ≥500.
- **Body / titles** (event titles, subtitles): geometric sans (Inter, Suisse Int'l, Helvetica Now, system-ui as a fallback). Weight ≥500 throughout — no 400.
- **Forbidden**: serif faces, italics, condensed/compressed cuts, weights below 500, decorative display faces.

The current `index.html` declares `-apple-system, "Inter", "Segoe UI", system-ui, sans-serif` as a single stack for everything. That is acceptable as a temporary stop-gap — the layout work matters more than the family lock-in — but a final pass should specify the numerals family explicitly and load it as a webfont before render.

## Layout grid

PRD Principle 9 sets the spatial floors. Use these as defaults; don't go below them.

- **Outer padding**: 24px from canvas edge to first content (top, left, right, bottom).
- **Inner padding**: 12px minimum between elements within a single zone.
- **Zone separation**: 24px minimum between major zones (NOW vs NEXT, left column vs timeline).
- **Corner radius**: 6px on all rounded rectangles (event blocks, any framed labels). Use the *same* radius everywhere — consistency is the Teenage Engineering tell.
- **Strokes**: 2px minimum for any line, divider, or border. Hairlines (1px, 0.5px) are forbidden — they render as broken segments after panel quantize. Dividers below 2px should be replaced with negative space + grid alignment instead.
- **Element minimum**: ~40×40px for any glanceable region. Anything smaller is invisible from across a room and violates Principle 6.
- **Density ceiling**: ≤6 distinct text elements visible on the canvas at any one time. To add an element, remove one first (PRD anti-pattern: cramming detail).

## Color use

The Waveshare panel is genuine three-color e-ink: black, white, red. We use red sparingly — only for things that mean **right now** or **emphasis**:

- Hero countdown number
- "Now" indicator line on the timeline
- Imminent-event highlight (when countdown drops below 5 min, the event title also flips red)

If we used red on every event, "now" would lose its meaning.

## Empty states

**No more meetings today.** The NEXT block changes to "Done for today" with the time of tomorrow's first event below. The countdown becomes "until tomorrow X:XX am." Less alarming, still useful.

**Free between meetings.** When there's a gap of >30 min before the next event, the NOW block reads "Free until [event]" instead of showing the previous meeting. Removes lingering "ended 20 min ago" noise.

**Full day off.** The whole left zone collapses to "No meetings today" centered. The timeline still draws (gives a sense of the empty day) but with no event blocks.

## What I considered and rejected

- **A week view.** Too much info; the countdown becomes the small element. The phone is fine for week views.
- **Event icons (calendar/zoom/in-person).** Too much to decode at a glance. If it's important, the title says it.
- **A weather widget.** Distracting. Phone has it.
- **Animated/refreshing countdown.** The screen refreshes every 15 min anyway; that's plenty for "is it time yet."
- **All-caps section labels.** "NOW" and "NEXT" in caps were originally tested but read as shouty; sentence case is calmer.
