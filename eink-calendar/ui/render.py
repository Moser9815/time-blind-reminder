#!/usr/bin/env python3
"""
render.py — fetch calendar events, render the layout to an 800x480 PNG.

Usage:
    python render.py --sample --out test.png        # mock data, no OAuth needed
    python render.py --auth                         # one-time Google auth flow
    python render.py --live --out calendar.png      # real calendar
    python render.py --list-calendars               # show available calendars

The render pipeline:
    Google Calendar API (or sample) → derive `now`, current/next event,
    timeline events → inject into index.html → headless Chromium screenshot
    of #canvas → PNG (paletted to e-ink's 3-color palette).

Run `pip install -r requirements.txt` first. Headless Chromium is provided
by Playwright; if first run fails with a missing-browser error, run
`playwright install chromium`.
"""

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
HTML_TEMPLATE = HERE / "index.html"
SAMPLE_PATH = HERE / "sample_data.json"
TOKEN_PATH = HERE / "token.json"
CREDENTIALS_PATH = HERE / "credentials.json"
CONFIG_PATH = HERE / "config.json"

# E-ink three-color palette: paper, ink, red.
EINK_PALETTE = [(0xEF, 0xEB, 0xDF), (0x1F, 0x1B, 0x16), (0xB8, 0x3C, 0x2C)]


# ---------------------------------------------------------------------------
# Data shaping
# ---------------------------------------------------------------------------

def load_sample():
    with open(SAMPLE_PATH) as f:
        return json.load(f)


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {
        "calendars": ["primary"],
        "working_hours": {"start": 9, "end": 17},
        "refresh_minutes": 15,
    }


def fetch_live_events(config):
    """Fetch today's events from Google Calendar. Returns the same shape as sample_data.json."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    if not TOKEN_PATH.exists():
        sys.exit("No token.json — run `python render.py --auth` first.")

    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), [
        "https://www.googleapis.com/auth/calendar.readonly"
    ])
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
        else:
            sys.exit("Credentials expired and not refreshable — re-run --auth.")

    service = build("calendar", "v3", credentials=creds)

    now = dt.datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + dt.timedelta(days=1)

    all_events = []
    for cal_id in config["calendars"]:
        result = service.events().list(
            calendarId=cal_id,
            timeMin=start_of_day.isoformat() + "Z",
            timeMax=end_of_day.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        for ev in result.get("items", []):
            # Skip all-day events — they don't fit the timeline view
            if "dateTime" not in ev["start"]:
                continue
            all_events.append({
                "title": ev.get("summary", "(no title)"),
                "start": ev["start"]["dateTime"],
                "end": ev["end"]["dateTime"],
                "attendees": ", ".join(
                    a.get("displayName", a.get("email", ""))
                    for a in ev.get("attendees", [])
                    if not a.get("self")
                )[:60],
            })

    all_events.sort(key=lambda e: e["start"])
    return {
        "now": now.isoformat(),
        "working_hours": config["working_hours"],
        "events": all_events,
    }


def derive_view_data(raw, override_now=None):
    """Take the raw event data and derive the layout-ready view model.

    `override_now` (datetime or None): if provided, replaces the `now` in raw.
    Used by the simulator's time-warp feature to render as if it were a
    different time of day. Only the TIME portion of override_now is used —
    the date is always taken from raw["now"] so that fixed-date sample data
    stays aligned with the override regardless of today's actual date.
    """
    if override_now is not None:
        canonical_date = dt.datetime.fromisoformat(raw["now"]).date()
        now = dt.datetime.combine(canonical_date, override_now.time())
    else:
        now = dt.datetime.fromisoformat(raw["now"])
    events = []
    for e in raw["events"]:
        start = dt.datetime.fromisoformat(e["start"].replace("Z", ""))
        end = dt.datetime.fromisoformat(e["end"].replace("Z", ""))
        events.append({**e, "_start": start, "_end": end})

    # Strip timezone info if present so naive comparisons work
    if events and events[0]["_start"].tzinfo:
        if now.tzinfo is None:
            now = now.replace(tzinfo=events[0]["_start"].tzinfo)

    current = next((e for e in events if e["_start"] <= now < e["_end"]), None)
    upcoming = [e for e in events if e["_start"] > now]
    next_event = upcoming[0] if upcoming else None

    def fmt_time(dtv):
        h, m = dtv.hour, dtv.minute
        period = "pm" if h >= 12 else "am"
        h12 = h - 12 if h > 12 else (12 if h == 0 else h)
        return f"{h12}:{m:02d} {period}"

    view = {
        "now": {"hour": now.hour, "minute": now.minute},
        "date": now.strftime("%a, %b %-d"),
        "workingHours": raw["working_hours"],
        "current": None,
        "next": None,
        "events": [],
    }

    if current:
        minutes_left = max(0, int((current["_end"] - now).total_seconds() / 60))
        view["current"] = {
            "title": current["title"],
            "endHour": current["_end"].hour,
            "endMinute": current["_end"].minute,
            "minutesLeft": minutes_left,
        }
    if next_event:
        minutes_until = max(0, int((next_event["_start"] - now).total_seconds() / 60))
        view["next"] = {
            "title": next_event["title"],
            "startHour": next_event["_start"].hour,
            "startMinute": next_event["_start"].minute,
            "minutesUntil": minutes_until,
            "subtitle": f"with {next_event['attendees']}" if next_event["attendees"] else "",
        }
    for e in events:
        state = "normal"
        if e is current:
            state = "current"
        elif e["_end"] <= now:
            # An event whose end equals now is past — it just ended this minute.
            state = "past"
        elif e is next_event and view["next"] and view["next"]["minutesUntil"] < 30:
            state = "imminent"
        view["events"].append({
            "title": e["title"],
            "startH": e["_start"].hour, "startM": e["_start"].minute,
            "endH": e["_end"].hour, "endM": e["_end"].minute,
            "state": state,
        })
    return view


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_to_png(view, out_path):
    """Inject view data into index.html, screenshot at 800x480, palette to e-ink colors."""
    from playwright.sync_api import sync_playwright
    from PIL import Image

    template = HTML_TEMPLATE.read_text()
    # Replace the SAMPLE constant with our view data so the page's JS uses real data.
    payload = json.dumps(view)
    rendered = template.replace(
        "const SAMPLE = {",
        f"const SAMPLE = (function(){{ return {payload}; }})(); const _UNUSED_SAMPLE_PLACEHOLDER = {{",
        1,
    )

    tmp_html = out_path.with_suffix(".tmp.html")
    tmp_html.write_text(rendered)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1024, "height": 768})
        page.goto(f"file://{tmp_html.resolve()}")
        page.wait_for_load_state("networkidle")
        # Webfonts (JetBrains Mono, Inter) load asynchronously from Google
        # Fonts; networkidle alone doesn't guarantee they're ready to paint.
        # Without this wait the screenshot can ship a fallback face.
        # `page.evaluate` auto-awaits returned promises — `wait_for_function`
        # would see the Promise itself (always truthy) and return immediately.
        page.evaluate("document.fonts.ready")
        canvas = page.locator("#canvas")
        canvas.screenshot(path=str(out_path))
        browser.close()

    tmp_html.unlink()

    # Quantize to the e-ink three-color palette so what you see in preview
    # matches what the panel can actually display.
    #
    # We use a saturation-aware classifier instead of PIL's nearest-color
    # quantize because the PNG has anti-aliased text edges. Mid-grey
    # antialiasing pixels are RGB-closer to red (#B83C2C) than to ink
    # (#1F1B16) — nearest-color would snap glyph edges to red and leak
    # the salience signal across all text. The classifier instead routes:
    #   high-saturation reddish pixels → red (intentional red elements)
    #   any dark pixel (low luminance)  → ink (text + dark UI)
    #   everything else                 → paper
    img = Image.open(out_path).convert("RGB")
    arr = np.asarray(img, dtype=np.int16)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    redness = r - np.maximum(g, b)
    is_red = (redness > 40) & (r > 100)
    is_ink = ~is_red & (luminance < 160)
    out = np.empty_like(arr, dtype=np.uint8)
    out[..., :] = EINK_PALETTE[0]   # default: paper
    out[is_ink] = EINK_PALETTE[1]
    out[is_red] = EINK_PALETTE[2]
    Image.fromarray(out, "RGB").save(out_path)
    print(f"Wrote {out_path} ({out_path.stat().st_size:,} bytes)")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def run_auth():
    """One-time OAuth flow. Writes token.json."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not CREDENTIALS_PATH.exists():
        sys.exit(
            "credentials.json not found. Download it from Google Cloud Console "
            "(see docs/GOOGLE_API.md) and save it as credentials.json in this dir."
        )
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_PATH),
        ["https://www.googleapis.com/auth/calendar.readonly"],
    )
    creds = flow.run_local_server(port=0)
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    print(f"Authorized. Wrote {TOKEN_PATH}.")


def list_calendars():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    if not TOKEN_PATH.exists():
        sys.exit("Run --auth first.")
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    service = build("calendar", "v3", credentials=creds)
    cals = service.calendarList().list().execute()
    for c in cals.get("items", []):
        print(f"  {c['id']:50s}  {c.get('summary', '')}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Render e-ink calendar PNG")
    ap.add_argument("--sample", action="store_true", help="Use sample_data.json")
    ap.add_argument("--live", action="store_true", help="Fetch from Google Calendar")
    ap.add_argument("--auth", action="store_true", help="Run OAuth flow")
    ap.add_argument("--list-calendars", action="store_true")
    ap.add_argument("--out", type=Path, default=Path("calendar.png"))
    args = ap.parse_args()

    if args.auth:
        run_auth()
        return
    if args.list_calendars:
        list_calendars()
        return

    if args.live:
        raw = fetch_live_events(load_config())
    elif args.sample:
        raw = load_sample()
    else:
        sys.exit("Pick one: --sample, --live, --auth, or --list-calendars")

    view = derive_view_data(raw)
    render_to_png(view, args.out)


if __name__ == "__main__":
    main()
