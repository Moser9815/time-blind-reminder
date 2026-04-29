# Google Calendar API setup

The render server uses OAuth 2.0 with a refresh token to read your calendar. One-time setup, ~30 minutes.

## Step 1 — Create a Google Cloud project

1. Go to https://console.cloud.google.com.
2. Click the project dropdown at the top → **New Project**. Name it something like "eink-calendar".
3. Wait ~30 seconds for it to provision.

## Step 2 — Enable the Calendar API

1. In your new project, go to **APIs & Services → Library**.
2. Search for "Google Calendar API".
3. Click it, then click **Enable**.

## Step 3 — Configure OAuth consent

1. **APIs & Services → OAuth consent screen**.
2. Choose **External** user type (unless you're on a Google Workspace domain).
3. Fill in only the required fields:
   - App name: "eink-calendar"
   - Your email as both User support email and Developer contact.
4. Click through Scopes (skip — we'll add them later) and Test users.
5. **Add yourself** (your Google account email) as a test user. Without this, OAuth will refuse to issue tokens.

## Step 4 — Create OAuth credentials

1. **APIs & Services → Credentials → Create credentials → OAuth client ID**.
2. Application type: **Desktop app**.
3. Name: "eink-calendar-cli".
4. Download the JSON file when prompted. Save it as `ui/credentials.json` in this project. **Don't commit it** — it's already in `.gitignore`.

## Step 5 — First-run authorization

From the `ui/` directory:

```bash
python render.py --auth
```

This opens a browser tab. Log in with the Google account whose calendar you want to read, click through the consent screen (it'll warn that the app isn't verified — that's fine for personal use, click "Continue"), and grant calendar read access.

When successful, the script writes `ui/token.json`. This contains your refresh token. Keep it safe; back it up; don't commit it.

After this one-time auth, all future calls (`render.py --live`) use the refresh token automatically — no browser, no interaction.

## Step 6 — Pick which calendar(s) to show

Run:

```bash
python render.py --list-calendars
```

You'll see a list with IDs like `primary`, `you@gmail.com`, `family@group.calendar.google.com`. Edit `ui/config.json` to set which calendar(s) to fetch:

```json
{
  "calendars": ["primary", "family@group.calendar.google.com"],
  "working_hours": {"start": 9, "end": 17},
  "refresh_minutes": 15
}
```

## Troubleshooting

**"Access blocked: eink-calendar has not completed the Google verification process"** — you need to add yourself as a test user (Step 3). Or hit "Advanced → Continue (unsafe)" — it's safe, it's your own app.

**"Token has been expired or revoked"** — re-run `python render.py --auth` to refresh.

**Empty calendar response** — most likely your `working_hours` is filtering out everything. Try widening to 0–24 to debug.

## Privacy note

The OAuth flow uses scope `https://www.googleapis.com/auth/calendar.readonly` — read-only, no write access. The render server only reads events; it never modifies your calendar. The credentials never leave your local machine.
