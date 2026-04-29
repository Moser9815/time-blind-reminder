# Hardware assembly

Estimated time: 30 minutes. No soldering required if you skip the optional steps.

## Tools you'll need

- Small Phillips screwdriver (for the 4755 charger's screw terminals).
- Wire strippers (for trimming the solar panel wires).
- USB-C cable (for programming the Feather).
- Optional: soldering iron (only if you want to attach the tactile button to the Feather; not needed for first power-on).

## Bench layout

Lay everything out before connecting anything. You should have:

| Item | Source | Looks like |
|------|--------|-----------|
| Adafruit ESP32-S3 Feather (5477) | DigiKey | Small dev board, ~2"×0.9", USB-C on one end |
| Adafruit Universal USB/DC/Solar Charger (4755) | DigiKey | Small board with USB-C, DC barrel jack, JST-PH connector |
| Voltaic P126 6V 2W solar panel | DigiKey | Black panel ~5"×3" with a thin cable ending in a 3.5/1.1mm DC plug |
| 2500 mAh LiPo battery (Adafruit 328) | DigiKey | Soft black pouch with a JST-PH connector |
| Waveshare 7.5" tri-color e-paper module (B097DMQ5FM) | Amazon | Display panel + driver PCB connected by ribbon cable |
| F/F jumper wires (Adafruit 266) | DigiKey | Strip of 40 colored wires |
| Tactile buttons 10-pack (Adafruit 1119) | DigiKey | Small black square buttons (set aside for now) |

## Step 1 — Prep the solar panel

The panel ships with a 3.5/1.1mm DC plug. We're skipping the adapter and going direct to the charger's screw terminals.

1. Hold the cable about 4 inches from the plug end.
2. **Snip the plug off** with wire cutters or a sharp knife.
3. Strip about 8 mm of insulation from each of the two wires.
4. Twist each wire's strands so they don't fray.
5. Identify polarity: most Voltaic panels mark + with a stripe or red sleeve, or you can plug it briefly into a multimeter (red probe to one wire, black to the other; if you see ~6V, red probe = +).

## Step 2 — Wire panel to charger

The Adafruit 4755 has two screw terminals on the back labeled **DC IN** with **+** and **−** marks.

1. Make sure no battery or USB is connected to the charger yet.
2. Loosen both DC IN screws.
3. Insert + wire into the **+** terminal, tighten.
4. Insert − wire into the **−** terminal, tighten.
5. Tug gently on each wire to confirm they're held firmly.

Don't connect anything else yet — we'll verify the panel is producing voltage before we hook up the battery.

## Step 3 — Verify the solar panel works

1. Take the assembly somewhere with light (a sunny window, or just a bright room).
2. The 4755 has a small **CHRG** LED. With no battery connected, it won't light, but you can verify input voltage another way:
3. *(Optional but nice)* Touch a multimeter to the BAT JST-PH pins on the charger — you should read 4–7 V depending on lighting. If you see 0V, polarity is reversed; flip the wires.

## Step 4 — Connect the battery

1. The LiPo battery has a JST-PH plug.
2. The 4755 has a JST-PH socket labeled **BAT**.
3. Plug battery into BAT. The plug only fits one way — don't force it.
4. The CHRG LED on the charger should now glow if the panel is in light. (If you're in a dim room, plug a USB-C cable into the charger's USB-C port instead — same LED behavior.)

## Step 5 — Connect the Feather

The Feather will draw power from the charger's **LOAD** output (or alternatively its own JST-PH from the battery — but for solar we want the charger in front).

1. The 4755's LOAD output is a JST-PH socket on the opposite side from BAT, labeled **LOAD**.
2. *(Recommended path — uses the LOAD output, which only powers the Feather when the system is running)*: cut a JST-PH cable, strip wires, solder one end to LOAD socket pads on the charger and the other end to the Feather's BAT pads. *Skip if you don't want to solder.*
3. *(Easy path — uses Feather's own LiPo connector)*: unplug the LiPo from the charger's BAT, plug it into the Feather's JST-PH instead. The Feather will run from battery and the charger only does charging when USB or solar is connected. **This is the path I recommend for first power-on** — comes back to the cleaner LOAD-output wiring later if you want.

For first boot, use the easy path: battery → Feather JST-PH directly.

## Step 6 — Wire the e-paper module to the Feather

See `WIRING.md` for the full pin map. Eight female-female jumpers from the Waveshare module to the Feather.

## Step 7 — First power-on

1. Plug a USB-C cable from your computer to the Feather. The on-board LED should blink.
2. The e-paper module won't show anything yet (no firmware), but should make a faint click sound when first powered (normal).
3. If the Feather doesn't show up as a USB serial device, try a different cable — many USB-C cables are charge-only.

You're ready to flash firmware. See the `firmware/` README.

## Mounting (later, after software works)

For the windowsill version:
- Solar panel goes on the window-facing side, glued to a thin 3D-printed back plate.
- Display goes on the room-facing side.
- Charger + Feather + battery sandwich between them.
- Total thickness target: ~12 mm.
- A 3M Command strip on the bottom edge holds it to the sill without permanent damage.

For desk-corner version:
- Same sandwich, kickstand on the bottom angled at ~20°.
- Solar still works behind the display in indirect light, but you'll likely want to top up via USB-C every few days.
