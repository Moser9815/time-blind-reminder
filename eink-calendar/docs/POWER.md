# Power budget

## Daily consumption

| Phase | Current | Duration per cycle | Cycles/day | Total |
|-------|---------|-------------------|------------|-------|
| Deep sleep | 10 µA | 14 min 45 s | 96 | 0.24 mAh |
| WiFi connect | 80 mA | 3 s | 96 | 6.4 mAh |
| HTTP fetch (~50 KB) | 100 mA | 4 s | 96 | 10.7 mAh |
| E-ink full refresh | 30 mA | 5 s | 96 | 4.0 mAh |
| Idle in active mode | 25 mA | 3 s | 96 | 2.0 mAh |
| **Total** | | | | **~23 mAh/day** |

Conservative estimate, rounding everything up: budget **48 mAh/day**.

## Daily generation (worst case)

Voltaic P126 panel: 6V × 330mA = 2W peak.

Behind glass, indoor through a window:
- Direct sun (south-facing window, summer noon): ~250 mA
- Bright cloudy day: ~80 mA
- Overcast: ~20 mA
- Average over a year in St. Joseph, MI (latitude 42°N): ~110 mA × 5 useful daylight hours = 550 mAh/day

Apply 30% margin for window glass loss and dirt: **~385 mAh/day generation**.

## Net result

Generated 385 mAh/day − Consumed 48 mAh/day = **+337 mAh/day surplus**.

2500 mAh battery, fully charged, can run **52 days with zero generation**. Even a week of solid overcast (assume 20% generation) only nets −10 mAh/day, which the battery absorbs trivially.

## Edge cases worth noting

**Long winter cloudy stretch.** January in MI can be 7 days at <20% normal sun. That's 7 × −10 = −70 mAh, which is 3% of battery. Recovers in a single sunny day.

**Display facing wrong direction.** If the panel is on the back facing the room (not the window), generation drops by 80%. Check panel orientation when mounting.

**Battery degradation.** LiPo cells lose ~20% capacity over 3 years of normal use. At 2000 mAh effective the surplus is still huge.

**WiFi reconnect storms.** If your router restarts and the device fails connection for 3 minutes, that's ~150 mA × 180 s = 7.5 mAh — a single bad cycle. Not a problem, but the firmware should `esp_deep_sleep` after 30 s of failed connect to avoid eating the battery during prolonged WiFi outages.

## Verifying in practice

Once running, the Feather can report its battery voltage on each wake. Code is in `firmware/src/main.cpp`:

```cpp
float voltage = analogReadMilliVolts(VBAT_PIN) * 2 / 1000.0;
```

Add this to your render server log and you can plot voltage over time. Healthy LiPo sits between 3.7V (nearly empty) and 4.2V (full). If you see it dropping below 3.6V daily, you're net-negative on power and need to increase refresh interval or check panel orientation.
