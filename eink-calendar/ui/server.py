#!/usr/bin/env python3
"""
server.py — tiny HTTP server that the firmware GETs once per refresh,
plus a browser-friendly preview/simulator at `/`.

Routes:
  GET /                             →  HTML preview page (the simulator)
  GET /calendar.png                 →  fresh PNG (default behavior — firmware contract)
  GET /calendar.png?at=HH:MM        →  PNG rendered as if `now` were HH:MM (today)
  GET /calendar.png?source=live     →  use Google Calendar instead of sample
  GET /calendar.png?source=sample   →  force sample data (default unless --live)
  GET /health                       →  "ok"

Usage:
    python server.py                # listens on :8000, sample data
    python server.py --port 8080
    python server.py --live         # default source = live calendar
    python server.py --cache 60     # cache PNG for 60 sec instead of regen-per-request

Open http://localhost:8000 in a browser to use the simulator.

The firmware calls `/calendar.png` with no params and gets the same
behavior as before — preview/simulator features are additive.
"""

import argparse
import datetime as dt
import http.server
import io
import socketserver
import sys
import threading
import time
import traceback
import urllib.parse
from pathlib import Path

import render

HERE = Path(__file__).parent
CACHE_PATH = HERE / "_cache.png"
_render_lock = threading.Lock()

PREVIEW_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Time Blind Reminder — Simulator</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&family=JetBrains+Mono:wght@500;700&display=swap">
<style>
  :root {
    --paper: #EFEBDF;
    --ink: #1F1B16;
    --muted: #4A4540;
    --red: #B83C2C;
    --bezel: #2A2724;
    --page-bg: #DCD7C9;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    background: var(--page-bg);
    font-family: 'Inter', system-ui, sans-serif;
    color: var(--ink);
  }
  .page {
    max-width: 960px;
    margin: 0 auto;
    padding: 48px 24px 96px;
  }
  header { margin-bottom: 32px; }
  .eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: var(--red);
    margin-bottom: 8px;
  }
  h1 {
    font-size: 48px;
    font-weight: 700;
    line-height: 1;
    margin: 0 0 12px;
    letter-spacing: -0.02em;
  }
  .meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
  }
  .device {
    display: inline-block;
    background: var(--bezel);
    padding: 24px;
    border-radius: 22px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
  }
  #canvas-img {
    display: block;
    width: 800px;
    height: 480px;
    background: var(--paper);
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
  }
  .controls {
    margin-top: 32px;
    padding: 24px;
    border: 2px solid var(--ink);
    border-radius: 6px;
    background: var(--paper);
    display: grid;
    gap: 24px;
  }
  .control-row {
    display: grid;
    grid-template-columns: 140px 1fr 100px;
    gap: 16px;
    align-items: center;
  }
  .control-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
  }
  .control-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px;
    font-weight: 700;
    text-align: right;
  }
  input[type=range] {
    width: 100%;
    accent-color: var(--red);
  }
  .button-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  button {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 8px 16px;
    border: 2px solid var(--ink);
    background: var(--paper);
    color: var(--ink);
    cursor: pointer;
    border-radius: 4px;
  }
  button.active { background: var(--ink); color: var(--paper); }
  button.alarm { border-color: var(--red); color: var(--red); }
  button.alarm.active { background: var(--red); color: var(--paper); }
  button:hover { background: var(--ink); color: var(--paper); }
  button.alarm:hover { background: var(--red); color: var(--paper); }
  .status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    text-align: right;
  }
  .status.error { color: var(--red); }
</style>
</head>
<body>
<div class="page">

  <header>
    <div class="eyebrow">Time Blind Reminder · Simulator</div>
    <h1>Live preview</h1>
    <div class="meta">800 × 480 — refreshed on demand · scrub time with the slider</div>
  </header>

  <div class="device">
    <img id="canvas-img" alt="rendered calendar"
         src="/calendar.png?cache_bust=0">
  </div>

  <div class="controls">

    <div class="control-row">
      <div class="control-label">Source</div>
      <div class="button-row">
        <button id="src-sample" class="active" data-source="sample">Sample</button>
        <button id="src-live" data-source="live">Live calendar</button>
      </div>
      <div></div>
    </div>

    <div class="control-row">
      <div class="control-label">Time</div>
      <input type="range" id="time-slider" min="0" max="1439" value="637">
      <div class="control-value" id="time-display">10:37</div>
    </div>

    <div class="control-row">
      <div class="control-label">Quick jumps</div>
      <div class="button-row">
        <button data-at="540">9:00</button>
        <button data-at="630">10:30</button>
        <button data-at="657">10:57 (imminent)</button>
        <button data-at="690">11:30</button>
        <button data-at="780">1:00 PM</button>
        <button data-at="990">4:30 PM (late)</button>
      </div>
      <button id="snap-now" class="alarm">Real now</button>
    </div>

    <div class="control-row">
      <div class="control-label">Auto-refresh</div>
      <div class="button-row">
        <button id="auto-off" class="active">Off</button>
        <button id="auto-5">Every 5s</button>
        <button id="auto-30">Every 30s</button>
      </div>
      <div></div>
    </div>

    <div class="control-row">
      <div class="control-label">Status</div>
      <div></div>
      <div class="status" id="status">Ready</div>
    </div>

  </div>
</div>

<script>
let source = "sample";
let atMin = 637;  // minutes since midnight; 10:37
let autoTimer = null;

const img = document.getElementById("canvas-img");
const slider = document.getElementById("time-slider");
const timeDisplay = document.getElementById("time-display");
const status = document.getElementById("status");

function fmtTime(min) {
  const h = Math.floor(min / 60);
  const m = min % 60;
  const period = h >= 12 ? "PM" : "AM";
  const h12 = h === 0 ? 12 : (h > 12 ? h - 12 : h);
  return `${h12}:${String(m).padStart(2, "0")} ${period}`;
}
function fmtAt(min) {
  return `${String(Math.floor(min / 60)).padStart(2, "0")}:${String(min % 60).padStart(2, "0")}`;
}

function refresh() {
  const params = new URLSearchParams();
  params.set("source", source);
  params.set("at", fmtAt(atMin));
  params.set("cache_bust", Date.now());
  status.textContent = "Rendering…";
  status.classList.remove("error");
  const url = "/calendar.png?" + params.toString();
  const probe = new Image();
  probe.onload = () => {
    img.src = url;
    status.textContent = `${fmtTime(atMin)} · ${source}`;
    status.classList.remove("error");
  };
  probe.onerror = () => {
    status.textContent = "Render failed (check server log)";
    status.classList.add("error");
  };
  probe.src = url;
}

slider.addEventListener("input", e => {
  atMin = parseInt(e.target.value, 10);
  timeDisplay.textContent = fmtTime(atMin);
});
slider.addEventListener("change", refresh);  // fires on mouseup (debounced)

document.querySelectorAll("[data-at]").forEach(b => {
  b.addEventListener("click", () => {
    atMin = parseInt(b.dataset.at, 10);
    slider.value = atMin;
    timeDisplay.textContent = fmtTime(atMin);
    refresh();
  });
});

document.querySelectorAll("[data-source]").forEach(b => {
  b.addEventListener("click", () => {
    source = b.dataset.source;
    document.querySelectorAll("[data-source]").forEach(x =>
      x.classList.toggle("active", x.dataset.source === source));
    refresh();
  });
});

document.getElementById("snap-now").addEventListener("click", () => {
  const now = new Date();
  atMin = now.getHours() * 60 + now.getMinutes();
  slider.value = atMin;
  timeDisplay.textContent = fmtTime(atMin);
  refresh();
});

function setAuto(seconds, btn) {
  if (autoTimer) { clearInterval(autoTimer); autoTimer = null; }
  document.querySelectorAll("#auto-off, #auto-5, #auto-30")
    .forEach(x => x.classList.remove("active"));
  btn.classList.add("active");
  if (seconds > 0) {
    autoTimer = setInterval(refresh, seconds * 1000);
  }
}
document.getElementById("auto-off").addEventListener("click", e => setAuto(0, e.target));
document.getElementById("auto-5").addEventListener("click", e => setAuto(5, e.target));
document.getElementById("auto-30").addEventListener("click", e => setAuto(30, e.target));

// Initial render
refresh();
</script>
</body>
</html>
"""


def parse_at(at_str):
    """Parse 'HH:MM' (24-hour) into a datetime for today."""
    if not at_str:
        return None
    try:
        h, m = at_str.split(":")
        h, m = int(h), int(m)
        today = dt.date.today()
        return dt.datetime(today.year, today.month, today.day, h, m, 0)
    except (ValueError, AttributeError):
        return None


def regenerate(use_live: bool, override_now=None):
    raw = render.fetch_live_events(render.load_config()) if use_live else render.load_sample()
    view = render.derive_view_data(raw, override_now=override_now)
    render.render_to_png(view, CACHE_PATH)


class Handler(http.server.BaseHTTPRequestHandler):
    default_use_live = False
    cache_seconds = 0
    _last_mtime = 0

    def log_message(self, fmt, *args):
        print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {self.client_address[0]} {fmt % args}")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self._send_html(PREVIEW_HTML)
            return

        if path == "/health":
            self._send_text("ok\n")
            return

        if path == "/calendar.png":
            source = params.get("source", [None])[0]
            at = params.get("at", [None])[0]
            override_now = parse_at(at)
            if at and override_now is None:
                self.send_error(400, f"Bad ?at value: {at!r} (expected HH:MM)")
                return
            use_live = (source == "live") if source in ("live", "sample") else self.default_use_live

            try:
                with _render_lock:
                    # If params are non-default OR cache is stale, regen.
                    is_param_render = bool(at or source)
                    stale = (time.time() - Handler._last_mtime) > self.cache_seconds
                    if is_param_render or stale or not CACHE_PATH.exists():
                        regenerate(use_live, override_now=override_now)
                        if not is_param_render:
                            Handler._last_mtime = time.time()
                    data = CACHE_PATH.read_bytes()
            except Exception as e:
                traceback.print_exc()
                self.send_error(500, f"render failed: {e}")
                return

            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_error(404)

    def _send_html(self, body):
        body_b = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body_b)))
        self.end_headers()
        self.wfile.write(body_b)

    def _send_text(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--live", action="store_true",
                    help="Default source=live (firmware contract uses live calendar)")
    ap.add_argument("--cache", type=int, default=0,
                    help="Cache the (no-param) PNG for N seconds")
    args = ap.parse_args()

    Handler.default_use_live = args.live
    Handler.cache_seconds = args.cache

    with socketserver.ThreadingTCPServer(("0.0.0.0", args.port), Handler) as httpd:
        print(f"Serving on http://0.0.0.0:{args.port}")
        print(f"  GET /                 →  Simulator preview page")
        print(f"  GET /calendar.png     →  rendered PNG ({'live' if Handler.default_use_live else 'sample'} default)")
        print(f"  GET /health           →  ok")
        print(f"  Open http://localhost:{args.port} in a browser to use the simulator.")
        print("Ctrl-C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
