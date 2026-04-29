#!/usr/bin/env python3
"""
server.py — tiny HTTP server that the firmware GETs once per refresh.

GET /calendar.png  →  fresh PNG (regenerated on each request, ~3 sec)
GET /health        →  "ok"

Usage:
    python server.py                # listens on :8000
    python server.py --port 8080
    python server.py --cache 60     # cache PNG for 60 sec instead of regen-per-request

Run on the same wifi as the device (your laptop, a Pi, etc.) and point the
firmware's `RENDER_URL` at http://<this-machine-ip>:8000/calendar.png.
"""

import argparse
import datetime as dt
import http.server
import io
import socketserver
import threading
import time
from pathlib import Path

import render

HERE = Path(__file__).parent
CACHE_PATH = HERE / "_cache.png"
_cache_mtime = 0
_cache_lock = threading.Lock()


def regenerate(use_live: bool):
    raw = render.fetch_live_events(render.load_config()) if use_live else render.load_sample()
    view = render.derive_view_data(raw)
    render.render_to_png(view, CACHE_PATH)


class Handler(http.server.BaseHTTPRequestHandler):
    use_live = True
    cache_seconds = 0

    def log_message(self, fmt, *args):
        # quieter than the default
        print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {self.client_address[0]} {fmt % args}")

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok\n")
            return

        if self.path == "/calendar.png":
            global _cache_mtime
            with _cache_lock:
                stale = (time.time() - _cache_mtime) > self.cache_seconds
                if stale or not CACHE_PATH.exists():
                    try:
                        regenerate(self.use_live)
                        _cache_mtime = time.time()
                    except Exception as e:
                        self.send_error(500, f"render failed: {e}")
                        return
                data = CACHE_PATH.read_bytes()

            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_error(404)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--sample", action="store_true",
                    help="Use sample data instead of live calendar (skip OAuth)")
    ap.add_argument("--cache", type=int, default=0,
                    help="Cache the PNG for N seconds (0 = regen per request)")
    args = ap.parse_args()

    Handler.use_live = not args.sample
    Handler.cache_seconds = args.cache

    with socketserver.ThreadingTCPServer(("0.0.0.0", args.port), Handler) as httpd:
        print(f"Serving on http://0.0.0.0:{args.port}")
        print(f"  GET /calendar.png  →  rendered PNG ({'live' if Handler.use_live else 'sample'} data)")
        print(f"  GET /health        →  ok")
        print("Ctrl-C to stop.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
