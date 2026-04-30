# Apps Script calendar feed

The render server reads today's events from a Google Apps Script Web App that runs as you and returns JSON. This bypasses GCP entirely — no client secrets, no OAuth project. Best for users on locked-down Workspace domains.

## One-time deployment (~5 min)

### 1. Create the script project

1. Go to https://script.google.com (sign in with the Google account whose calendar you want to read)
2. Click **New project**
3. Rename it to "time-blind-reminder" (top-left, click "Untitled project")
4. Replace the default `function myFunction() { … }` with the entire contents of `Code.gs` from this directory
5. Save (⌘S or the disk icon)

### 2. (Optional) Set a secret token

Open `Code.gs` in the editor and edit the `SECRET_TOKEN` constant near the top. Set it to a long random string:

```js
const SECRET_TOKEN = "<long-random-string>";
```

Generate one in a terminal: `openssl rand -hex 24` — that's 48 hex chars.

If you leave `SECRET_TOKEN = ""`, the script accepts any request to its URL. The URL itself is already a long random secret, so this is acceptable for personal use, but the token adds a second layer.

### 3. (Optional) Test before deploying

In the Apps Script editor:
1. Top dropdown → select `testFeed`
2. Click **Run** (▶)
3. First run: Google asks for permissions — click **Review permissions**, pick your account, click **Advanced → Go to time-blind-reminder (unsafe)** (it's your own script — safe), grant calendar access
4. After it runs, click **View execution log** (or **Logs**). You should see a JSON object with today's events.

If it complains about permissions or the calendar API not being enabled, click any "enable" prompts and re-run.

### 4. Deploy as a Web App

1. Click **Deploy → New deployment** (top-right)
2. Click the gear icon → **Web app**
3. Fill in:
   - **Description**: `Time Blind Reminder feed`
   - **Execute as**: **Me** (your account)
   - **Who has access**: **Anyone**
     - "Anyone" means anyone with the URL can hit it. Combined with the long random URL + `SECRET_TOKEN`, this is the right balance for personal use.
     - "Anyone with Google account" requires OAuth from the caller — won't work for the render server.
4. Click **Deploy**
5. Copy the **Web app URL** — looks like `https://script.google.com/macros/s/AKfycb…/exec`. **This URL is sensitive** — anyone with it can read your calendar. Don't paste it into Slack, GitHub, etc.

### 5. Wire it into the render server

Edit `eink-calendar/ui/config.json` (create it if missing) to look like:

```json
{
  "calendars": ["primary"],
  "working_hours": { "start": 9, "end": 17 },
  "refresh_minutes": 15,
  "apps_script_url": "https://script.google.com/macros/s/AKfycb.../exec",
  "apps_script_token": ""
}
```

If you set a `SECRET_TOKEN` in step 2, paste it as `apps_script_token`. Otherwise leave it as `""`.

`config.json` is gitignored — the URL won't leak to the repo.

### 6. Test

```bash
cd eink-calendar/ui
.venv/bin/python render.py --live --out /tmp/live.png && open /tmp/live.png
```

You should see your real calendar rendered. Or fire up the simulator and toggle to "Live calendar":

```bash
python server.py
# open http://localhost:8000, click "Live calendar"
```

## Updating the script later

If you change `Code.gs` (e.g. to add more calendars), you must redeploy:

1. **Deploy → Manage deployments**
2. Click the pencil ✏️ icon on the existing deployment
3. **Version** → "New version"
4. Click **Deploy**

The URL stays the same. If you create a "New deployment" instead of editing, you get a new URL — usually you don't want that.

## Picking which calendars to fetch

By default the script reads your **primary** calendar. To add more:

1. In the Apps Script editor, run `listCalendars` (top dropdown → `listCalendars` → ▶)
2. Open the execution log to see all calendar names + IDs
3. Edit the `CALENDARS` array in `Code.gs`:
   ```js
   const CALENDARS = ["primary", "family@group.calendar.google.com"];
   ```
4. Save and redeploy (step 6 of "Updating")

## Quotas

Apps Script free tier: ~6 minutes per execution, ~20,000 executions/day for consumer accounts (lower on Workspace). One device polling every 15 min = 96 calls/day. Plenty of headroom.

## Privacy

The script runs as you. The Web App URL grants whoever has it the ability to read events from your configured calendars (today only — the script doesn't expose other dates or any write access).

The script reads only:
- Calendar events for today's date range
- Event title, start time, end time, guest list

It never:
- Writes or modifies events
- Reads other days, other calendars, or other Google services
- Exfiltrates data anywhere except the response to the calling HTTP client
