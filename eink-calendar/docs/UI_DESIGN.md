# UI design rationale

## The problem

ADHD time blindness is not "I can't read a clock." It's "10:45 doesn't feel close to 11:00 until I'm already late." The future stays abstract; transitions sneak up; hyperfocus eats hours invisibly. A calendar that just *displays events* doesn't help — you already see them in your phone.

What helps is making time **visceral, spatial, and unavoidable**.

## Principles

The full set lives in `PRD.md` — eight cognitive principles tied to the ADHD time-blindness literature, plus two aesthetic principles (panel-resolution minimums and Teenage Engineering language). This doc covers how those principles get realized in pixels.

The shape of the result:

- **Hero countdown is the device.** A 200px red JetBrains Mono numeral answers "how much time do I have?" without subtraction. Wall-clock time is the small thing in the corner (PRD Principle 4 — surface "next," de-emphasize "later").
- **Day-as-space rail.** A vertical timeline from work-start to work-end shows where you are in the day. Past events go to a dashed outline (subordinate); current events get a red border; the next event within 30 min flips to ink-fill (escalation tier 1). The day's shape is literally visible (PRD Principle 3).
- **Three escalation tiers as the next event approaches.** Default: red numeral on paper. <30 min: a red depletion bar appears below the numeral and shrinks linearly. <5 min: the whole hero block flips to a red panel with paper-color numeral — the alarm-bell state (PRD Principle 5).
- **Red is never decoration.** Only the hero countdown, depletion bar, current-event border, and now-marker on the rail edge are red — the salience budget (PRD Principle 8).
- **Glanceable from 6+ feet.** Type minimums and stroke minimums make every element survive the panel's 100 ppi quantization without aliasing artifacts (PRD Principle 9).

## Layout

Total canvas: 800 × 480 (the panel's native resolution). Two zones plus a header strip.

```
0                                                504  524                       800
┌─────────────────────────────────────────────────┬────┬─────────────────────────┐ 0
│  10:37 AM  |  WED · APR 29                      │    │                         │
├─────────────────────────────────────────────────┤    │  9 AM ───────           │ 72
│                                                 │    │                         │
│  NEXT IN                                        │    │  ┌─────────────────┐    │
│                                                 │    │  │ DESIGN REVIEW … │    │
│  ┌────────────────────┐                         │    │  └─────────────────┘    │
│  │                    │                         │    │  11                     │
│  │      23            │ MIN                     │    │  ┌─────────────────┐    │
│  │                    │                         │    │  │ STANDUP         │    │
│  └────────────────────┘                         │    │  └─────────────────┘    │
│                                                 │    │  ┌─────────────────┐    │
│  ━━━━━━━━━━━━━━━━━━━━━ ←— depletion bar (red)   │    │  │ LUNCH           │    │
│                                                 │    │  └─────────────────┘    │
│  Standup                                        │    │  1 PM                   │
│  AT 11:00 AM · WITH TEAM-ENG                    │    │  ┌─────────────────┐    │
│                                                 │    │  │ FOCUS BLOCK — … │   ▌│ ←— now-marker
│                                                 │    │  └─────────────────┘    │
│                                                 │    │  3                      │
│                                                 │    │  ┌─────────────────┐    │
│                                                 │    │  │ 1:1 WITH ALEX   │    │
│                                                 │    │  └─────────────────┘    │
│                                                 │    │  5                      │
└─────────────────────────────────────────────────┴────┴─────────────────────────┘ 480
       ←— left zone (NEXT hero) 504px            gap   ←— right rail (today) 276px
```

Header strip is 72px tall, full canvas width, ink-rule divider at y=72. The left zone holds the NEXT hero countdown + event meta + (optional) depletion bar. The right rail holds the day timeline with hour ticks every 2 hours, event blocks positioned by start time, and a NOW marker on the rail's right edge.

## Type scale

| Element | Family | Size | Weight | Case | Color |
|---------|--------|------|--------|------|-------|
| Clock numerals | JetBrains Mono | 28px | 500 | — | #1F1B16 (ink) |
| Clock AM/PM | Inter | 18px | 600 | UPPER, 0.12em | #1F1B16 |
| Date | Inter | 18px | 600 | UPPER, 0.12em | #1F1B16 |
| "NEXT IN" label | Inter | 18px | 600 | UPPER, 0.18em | #1F1B16 |
| **Hero countdown** | **JetBrains Mono** | **200px** | **700** | — | **#B83C2C (red)** |
| Hero unit "MIN" | Inter | 24px | 600 | UPPER, 0.12em | #1F1B16 |
| Next event title | Inter | 32px | 600 | — | #1F1B16 |
| Next event meta numerals | JetBrains Mono | 18px | 500 | UPPER, 0.12em | #1F1B16 |
| Next event meta sans | Inter | 18px | 600 | UPPER, 0.12em | #1F1B16 |
| Rail hour-tick numerals | JetBrains Mono | 16px | 500 | UPPER, 0.12em | #1F1B16 |
| Rail hour-tick AM/PM | Inter | 16px | 600 | UPPER, 0.12em | #1F1B16 |
| Rail event title | Inter | 16px | 600 | UPPER, 0.1em | #1F1B16 |

Every value meets PRD-9 floors. No weight below 500. No italics, no serifs.

## Typography family

PRD Principle 10 pairing: **JetBrains Mono** for all numeric content (clock, hero countdown, hour ticks, event-meta times) — `font-feature-settings: "tnum" 1` is on `#canvas` so tabular figures apply by inheritance. **Inter** for labels and event titles, ALL CAPS with letter-spacing ≥0.1em.

Both load via Google Fonts CDN; `render.py` waits on `document.fonts.ready` before screenshotting so the PNG never ships a fallback face. To swap to a paid family (Berkeley Mono, NB Architekt) for production, drop the `<link>` in `index.html` and self-host the woff2.

Two weights only (500 medium for body/numerals, 600 semibold for labels/titles, 700 bold for the hero numeral). Three colors at design time (ink `#1F1B16`, muted `#4A4540`, red `#B83C2C`); after quantize the muted color snaps to ink, leaving exactly two colors on screen plus the red accent. **Do not use `#6B645A` or any color with smaller RGB-distance to red than to ink** — it will quantize to red and break the salience budget (see `BUGS.md` PALETTE-RED-LEAK).

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
