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

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Section labels (NOW, NEXT, TODAY) | 14pt | 500 | #6B645A (muted) |
| Clock + date | 20pt | 500 | #1F1B16 (ink) |
| Current event title | 32pt | 500 | #1F1B16 |
| Current event subtitle | 20pt | 400 | #6B645A |
| Next event title | 28pt | 500 | #1F1B16 |
| **Hero countdown** | **92pt** | **500** | **#B83C2C (red)** |
| Next event subtitle | 18pt | 400 | #6B645A |
| Timeline hour labels | 13pt | 400 | #6B645A |
| Timeline event titles | 12pt | 500 | #1F1B16 |

Two weights only (400 regular, 500 medium). Three colors only (ink, muted, red). E-ink doesn't do gradients or shadows, so the typographic hierarchy has to do all the work.

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
