Build and flash the firmware to the Feather S3.

Pre-flight:
- Confirm `eink-calendar/firmware/src/secrets.h` has real WiFi creds and the correct `RENDER_URL` (the IP of the machine running `server.py`, not localhost).
- Confirm the device is connected via USB-C and visible: `ls /dev/cu.usbmodem*`. The Feather S3 uses native USB-CDC (no separate USB-to-serial chip).
- **Disconnect the LiPo battery before flashing** — the charge IC and USB power can fight if both are connected. Reconnect after flashing finishes.

Build + flash:
1. `cd eink-calendar/firmware`
2. `pio run -t upload` — builds and flashes in one shot. First build downloads the toolchain (~5 min); subsequent builds are fast.
3. `pio device monitor` — open the serial monitor at 115200. You should see:
   ```
   === boot #N ===
   free heap: ... (PSRAM: ...)
   WiFi: connecting to ...
   WiFi: connected, IP=...
   HTTP: GET http://.../calendar.png
   HTTP: NNNN bytes
   e-ink: refreshing...
   e-ink: done
   Sleeping for 900 sec.
   ```
4. After boot, the device deep-sleeps. Press the button on `PIN_BUTTON=13` to wake it manually for the next test.

If `pio` isn't installed: `pip install platformio` (or use the PlatformIO VS Code extension).

If upload fails with "no such file /dev/cu.usbmodem...": double-tap the reset button on the Feather to enter bootloader mode, then re-run upload.
