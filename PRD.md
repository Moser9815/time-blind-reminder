# Time Blind Reminder — PRD

## Goal
A solar-powered e-ink calendar display for someone with ADHD time blindness. The problem isn't reading a clock — it's that "11:00 standup" feels imaginary until 10:58. The device makes time *visible* and *spatial*: a giant countdown to the next event, plus a vertical day timeline showing the literal shape of remaining hours. Glanceable from across the room. Lives on a windowsill, runs forever on sunlight.

Owner: Robert Moser (personal project; not for distribution).

## User principles

These are non-negotiable. Every UI decision traces back to these.

1. **Countdown beats clock.** Time-until-next-event is the hero. Wall-clock time is small.
2. **Time as space.** The right side is a vertical timeline of working hours — remaining day becomes visible territory, not abstract numbers.
3. **Glanceable from 6+ feet.** Two zones (now/next on the left, today on the right). No icons. No clutter.
4. **Tri-color discipline.** Paper / ink / red only. Red is reserved for "now" emphasis (current event timer, imminent-meeting indicator).

## Behavior

### Display states

- **Active workday with a current event**: hero is "X min" countdown to event end (red). Below: current event title + end time. Right: timeline with current slot highlighted.
- **Active workday between events**: hero is "X min" countdown to next event start (red if <30 min, ink otherwise). Below: next event title + start time + attendees.
- **Active workday with no upcoming events**: hero says "—" or hides; topbar shows date; timeline shows the workday with completed slots greyed.
- **Outside working hours**: TBD (parking lot: "rest" view showing tomorrow's first event)
- **Error / no network**: leave the previous frame on screen (e-ink persists with no power). The firmware retries on `RETRY_SECONDS` cadence.

### Refresh cadence

- Default refresh: every 15 minutes (`REFRESH_SECONDS=900` in `firmware/src/secrets.h`)
- Manual refresh: button press wakes immediately (`PIN_BUTTON=13`)
- Failure backoff: retry after `RETRY_SECONDS=60`. After `MAX_RETRIES=3` consecutive failures, sleep for the full refresh interval to conserve battery during outages.

### Calendar handling

- Source: Google Calendar via `calendar.readonly` OAuth scope
- Calendars used: configurable in `eink-calendar/ui/config.json` (defaults to `["primary"]`)
- All-day events: skipped. They have no `dateTime` and don't fit the timeline view.
- Recurring events: handled via `singleEvents=true` in the API call (Google expands them).
- Working hours window: 9:00–17:00, configurable in `config.json`.
- Attendee display: up to 60 chars of comma-joined non-self attendees on the "next" event. Truncated.

### Power

- Target: multiple weeks of buffer through cloudy weather
- Battery: 2500 mAh LiPo
- Active per cycle: ~15 sec (WiFi + HTTP + e-ink refresh)
- Sleep current target: ~10 µA
- Solar: 2W panel behind window glass, ~660 mAh/day generated assumption (5h sun × 50% loss)
- Daily consumption: ~48 mAh/day at default refresh rate
- Low-battery behavior: TBD (parking lot: warn at <3.6V on display)

## Hardware

- MCU: Adafruit Feather ESP32-S3 (4MB Flash / 2MB PSRAM) — product 5477. PSRAM required for framebuffers.
- Display: Waveshare 7.5" tri-color (B/W/R) e-paper, 800×480, GDEY075Z08 controller
- Battery: 2500 mAh LiPo
- Solar: 2W panel
- Charging: integrated on Feather
- Button: single momentary on `PIN_BUTTON=13`, also wakes from deep sleep
- Form factor: windowsill / desk corner. Eventual 3D-printed enclosure (parking lot).
- Mounting: TBD (kickstand + window suction in parking lot)

## Out of scope (explicit)

- **Multiple users / multi-tenant**: single user, single device. No accounts beyond the owner's Google login.
- **Bidirectional editing**: read-only calendar. Don't add the ability to create/edit events from the device.
- **Notifications / alarms**: the whole point is *passive glanceability*. No buzzer, no LED, no ping.
- **Always-online cloud service**: render server runs on the user's own machine (laptop or Pi). Not deploying a SaaS.
- **Color screen / animations**: tri-color e-ink is the medium. No backlight, no refresh-flash entertainment.
- **Apple Calendar / Outlook**: Google Calendar only for v1.

## Change log

- 2026-04-29: Initial PRD seeded from existing code and `eink-calendar/README.md`. Captures current behavior, not future direction.
