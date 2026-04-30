/**
 * Time Blind Reminder — Apps Script calendar feed
 *
 * Deploy this script as a Web App. The render server hits its URL and
 * gets back a JSON object matching the shape of `ui/sample_data.json`.
 *
 * No GCP project, no OAuth client secrets, no client-side auth.
 * The script runs as the deploying user; permissions are granted
 * once in the Apps Script editor.
 *
 * See ./README.md for deployment steps.
 */

// ---------------------------------------------------------------------------
// CONFIG — edit these.
// ---------------------------------------------------------------------------

// Calendars to fetch. Use "primary" for your main calendar.
// Add additional IDs (e.g. "you@gmail.com", "shared@group.calendar.google.com")
// if you want events from multiple calendars merged together.
const CALENDARS = ["primary"];

// Working hours used by the rail / hour ticks. Match config.json on the
// render server side. The events feed includes ALL events, not just
// working-hours ones — the renderer does the windowing.
const WORKING_HOURS = { start: 9, end: 17 };

// Optional secret token. If non-empty, the render server must include
// `?token=THIS_VALUE` in the request URL. Acts as a per-deployment
// shared secret on top of the long random Web App URL.
//
// Generate a fresh random string from a terminal:
//   openssl rand -hex 24
//
// Or just pick a long random-looking string. Leave empty to disable
// the token check (the URL itself is still the credential).
const SECRET_TOKEN = "";

// ---------------------------------------------------------------------------
// Web app entry point.
// ---------------------------------------------------------------------------

function doGet(e) {
  if (SECRET_TOKEN) {
    const provided = (e && e.parameter && e.parameter.token) || "";
    if (provided !== SECRET_TOKEN) {
      return _json({ error: "forbidden" }, 403);
    }
  }

  const now = new Date();
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
  const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);

  const events = [];
  for (const calId of CALENDARS) {
    const cal = (calId === "primary")
      ? CalendarApp.getDefaultCalendar()
      : CalendarApp.getCalendarById(calId);
    if (!cal) continue;

    const calEvents = cal.getEvents(startOfDay, endOfDay);
    for (const ev of calEvents) {
      // Skip all-day events — they don't fit the timeline.
      if (ev.isAllDayEvent()) continue;

      const guests = ev.getGuestList()
        .map(g => g.getName() || g.getEmail())
        .filter(n => n)
        .slice(0, 5)
        .join(", ");

      events.push({
        title: ev.getTitle() || "(no title)",
        start: ev.getStartTime().toISOString(),
        end: ev.getEndTime().toISOString(),
        attendees: guests
      });
    }
  }

  events.sort((a, b) => a.start.localeCompare(b.start));

  const payload = {
    now: now.toISOString(),
    working_hours: WORKING_HOURS,
    events: events
  };

  return _json(payload);
}

// ---------------------------------------------------------------------------
// Helpers.
// ---------------------------------------------------------------------------

function _json(obj, statusCode) {
  // Apps Script's ContentService doesn't expose status codes for web apps —
  // 200 is always returned even for errors. Caller should check the body.
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Run this from the Apps Script editor (Run → testFeed) to see what the
 * feed returns BEFORE deploying. Useful for debugging.
 */
function testFeed() {
  const result = doGet({ parameter: { token: SECRET_TOKEN } });
  Logger.log(result.getContent());
}

/**
 * Run from the editor to print all calendar IDs you have access to.
 * Use this to find IDs for additional calendars (paste them into CALENDARS).
 */
function listCalendars() {
  const cals = CalendarApp.getAllCalendars();
  for (const c of cals) {
    Logger.log(c.getName() + "  →  " + c.getId());
  }
}
