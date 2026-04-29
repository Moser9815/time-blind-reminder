# Firmware

ESP32-S3 sketch that wakes, fetches a PNG from the render server, pushes it to the e-ink panel, deep sleeps. Total cycle: ~15 seconds active, then 15 minutes of 10 µA sleep.

## One-time setup

1. Install [PlatformIO](https://platformio.org/) — either the VS Code extension or the CLI (`pip install platformio`).
2. Open `firmware/` as a PlatformIO project (VS Code: File → Open Folder → `firmware/`).
3. Copy `src/secrets.h.example` → `src/secrets.h` if separate. (Currently `src/secrets.h` ships with placeholder values.)
4. Edit `src/secrets.h`:
   - `WIFI_SSID` and `WIFI_PASSWORD` — your home network.
   - `RENDER_URL` — URL of the machine running `ui/server.py`. From the same WiFi, find your laptop's IP with `ipconfig getifaddr en0` (mac) or `hostname -I` (linux). Use port 8000.

## Build & flash

CLI:
```bash
cd firmware
pio run                  # compile only
pio run -t upload        # compile + flash over USB-C
pio device monitor       # serial output (115200 baud)
```

VS Code: bottom-bar PlatformIO icons — checkmark to build, arrow to upload, plug icon for monitor.

## First power-on

After flashing, power-cycle the Feather (unplug/replug USB or hit the reset button). You should see in the serial monitor:

```
=== boot #1 ===
free heap: 274416 bytes (PSRAM: 2097120)
WiFi: connecting to YOUR_WIFI...
WiFi: connected, IP=192.168.1.74, RSSI=-58
HTTP: GET http://192.168.1.100:8000/calendar.png
HTTP: 47820 bytes
89 50 4e 47 0d 0a 1a 0a ...
e-ink: refreshing...
e-ink: done
Sleeping for 900 sec.
```

The `89 50 4e 47` confirms the firmware received a real PNG (PNG magic bytes). The display will show a placeholder "eink-calendar online" message until the PNG decoder is wired in (see TODO below).

## What's working in this skeleton

- WiFi connect with timeout + retry backoff
- HTTPS GET of the PNG
- E-ink driver init + refresh
- Deep sleep with timer wake + button wake (D13)
- Boot counter survives sleep cycles via RTC memory
- PSRAM-allocated framebuffers (96 KB total — too big for SRAM, comfortable in PSRAM)

## What's TODO

The skeleton fetches and verifies the PNG arrives, but does **not** yet decode it onto the framebuffers. Two-step plan:

1. Add the [PNGdec library](https://github.com/bitbank2/PNGdec) to `lib_deps` in `platformio.ini`.
2. In `fetch_and_decode()`, replace the byte-sniff loop with a `PNG.decode()` call that streams pixels into `bw_buffer` and `red_buffer` (the palette has only 3 colors, so the decoder maps each pixel to either ink or red).
3. In `push_to_display()`, replace the placeholder text with `display.drawBitmap(0, 0, bw_buffer, W, H, GxEPD_BLACK)` and a second pass for red.

The render server already produces the right palette — see `ui/render.py`'s `EINK_PALETTE`. Each pixel in the served PNG will be one of three exact RGB values, so decode is deterministic.

## Power profiling

To verify the power budget in `docs/POWER.md`:

```bash
pio device monitor
# Watch the timing of each phase. Multiply by current draw from datasheet.
```

For real-world power measurement, an inline USB power meter (Ruideng UM34 or similar) on the USB-C cable will show average current. With WiFi off, you should see < 100 µA between cycles.
