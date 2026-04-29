# Wiring map — Feather S3 ↔ Waveshare 7.5" e-paper

The Waveshare module has eight pins broken out on its driver PCB. We connect them to GPIOs on the Feather S3 with female-female jumper wires.

## Pin map

| Waveshare pin | Function | Feather S3 pin | Feather GPIO | Notes |
|---------------|----------|----------------|--------------|-------|
| VCC | 3.3V power | 3V | — | use the 3V pin, NOT USB |
| GND | Ground | GND | — | any GND pin |
| DIN | SPI MOSI | MO | GPIO 35 | data |
| CLK | SPI SCK | SCK | GPIO 36 | clock |
| CS | Chip select | A5 | GPIO 8 | active low |
| DC | Data/command | A4 | GPIO 9 | high = data, low = command |
| RST | Reset | A3 | GPIO 10 | active low |
| BUSY | Busy flag | A2 | GPIO 11 | input — display drives this |

These GPIO assignments match the firmware in `firmware/src/main.cpp`. If you change them, also update the `#define` lines at the top of `main.cpp`.

## Visual reference

Holding the Feather with USB-C facing up:

```
                  USB-C
        +---------------------+
   RST  |·                   ·|  VBUS (don't use)
    3V  |·  ●                ·|  GND  ←──── GND  (Waveshare GND)
   3V   |·──── VCC (Waveshare)·|  GND
   GND  |·                   ·|  USB
   A0   |·                   ·|  D13 (LED)
   A1   |·                   ·|  D12
   A2   |·──── BUSY           ·|  D11
   A3   |·──── RST            ·|  D10
   A4   |·──── DC             ·|  D9
   A5   |·──── CS             ·|  D6
   SCK  |·──── CLK            ·|  D5
    MO  |·──── DIN            ·|  SDA (I²C)
    MI  |·                   ·|  SCL (I²C)
   RX   |·                   ·|  STEMMA QT
   TX   |·                   ·|
        +---------------------+
```

## Color suggestion for the jumpers

This makes debugging much easier later. Pick from the rainbow strip:

| Wire | Color |
|------|-------|
| VCC | red |
| GND | black |
| DIN | yellow |
| CLK | green |
| CS | blue |
| DC | white |
| RST | orange |
| BUSY | purple |

## Tactile button (optional, for manual refresh)

When you're ready to add the button:

| Button pin | Feather pin |
|------------|-------------|
| One leg | D13 |
| Other leg | GND |

The firmware uses internal pull-up on D13, so pressing the button pulls the line LOW.

## Common mistakes to avoid

- **Don't power the Waveshare from VBUS or USB** — those are 5V and the panel wants 3.3V.
- **VCC and GND first** — wire those before any signal lines, so if the rest of the wiring is wrong the module isn't damaged by partial power.
- **Don't connect MISO** — there's no MI/MISO line in the e-paper module. Communication is one-way (Feather → display).
- **Double-check GPIO numbers if you change boards** — the Feather S3 silkscreen labels (A0, A2, MO) are stable across the Feather family but the underlying GPIOs vary. The numbers above are correct for product 5477 specifically.
