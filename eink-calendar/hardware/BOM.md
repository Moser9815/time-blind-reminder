# Bill of materials

Two carts, ~$149.84 total shipped. Stock-verified Apr 29 2026.

## Cart 1 — DigiKey (~$80)

| Item | Mfr P/N | Qty | Price | Link |
|------|---------|-----|-------|------|
| Adafruit ESP32-S3 Feather (4MB Flash, 2MB PSRAM) | 5477 | 1 | $17.50 | https://www.digikey.com/en/products/detail/adafruit-industries-llc/5477/16583982 |
| Adafruit Universal USB/DC/Solar LiPo charger (bq24074) | 4755 | 1 | $14.95 | https://www.digikey.com/en/products/detail/adafruit-industries-llc/4755/13231325 |
| Voltaic P126 6V 2W ETFE solar panel | P126 | 1 | $21.00 | https://www.digikey.com/en/products/detail/voltaic-systems/P126/18069490 |
| Adafruit LiPo battery 3.7V 2500mAh | 328 | 1 | ~$14.95 | https://www.digikey.com/en/products/detail/adafruit-industries-llc/328/5054542 |
| Adafruit Premium F/F jumper wires (40-pack) | 266 | 1 | $3.95 | https://www.digikey.com/en/products/detail/adafruit-industries-llc/266/5629427 |
| Adafruit tactile buttons (10-pack) | 1119 | 1 | $2.50 | https://www.digikey.com/en/products/detail/adafruit-industries-llc/1119/7241449 |

DigiKey subtotal: ~$74.85
Standard ground shipping to MI: ~$5
**DigiKey total: ~$79.85**

## Cart 2 — Amazon (~$70)

| Item | ASIN | Qty | Price | Link |
|------|------|-----|-------|------|
| Waveshare 7.5" tri-color e-Paper Module (B), 800×480 red/black/white | B097DMQ5FM | 1 | $69.99 | https://www.amazon.com/dp/B097DMQ5FM |

Amazon total: $69.99 (free Prime shipping)

## Grand total: ~$149.84

## What we deliberately skipped

- **DC adapter (Adafruit 4287).** Not needed — the 4755 charger has DC IN screw terminals on the back, so the panel's wires connect directly. Simpler, cheaper, and avoided a backorder.
- **DS3231 RTC.** ESP32-S3 + WiFi NTP gives accurate time on every wake.
- **TPL5110 timer.** ESP32-S3's native deep sleep is ~10 µA, well within the solar power budget.
- **6W solar panel.** 2W is plenty for the daily duty cycle; 4× the cost wasn't worth it for behind-glass deployment.

## What's missing that you'll add later

- **3D-printed enclosure.** Not on the BOM yet — depends on what shape you want for the windowsill. Roughly: 220 × 130 × 12 mm, four screw bosses for the display, channel for the panel cable, optional kickstand.
- **Window mount.** Either a 3M Command strip on the bottom edge, or a small suction cup on the back.
- **USB-C cable.** Used for programming the Feather. Almost certainly already in your house.
