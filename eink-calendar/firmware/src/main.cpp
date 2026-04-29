/*
 * Time Blind Reminder — firmware
 *
 * Wakes from deep sleep, connects to WiFi, fetches a 800x480 PNG from the
 * render server, decodes it, pushes it to the Waveshare 7.5" tri-color panel,
 * goes back to deep sleep.
 *
 * Total active time per cycle: ~15 seconds (mostly WiFi connect + e-ink refresh).
 * Total deep-sleep current: ~10 µA on this Feather S3.
 *
 * Build with PlatformIO. See ../platformio.ini.
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <GxEPD2_3C.h>           // tri-color (B/W/R) driver
#include "secrets.h"

// 7.5" 800x480 tri-color panel — Waveshare module B097DMQ5FM uses the
// GDEY075Z08 / GDEW075Z09 controller. The "B" variant is what we're targeting.
GxEPD2_3C<GxEPD2_750c_Z08, GxEPD2_750c_Z08::HEIGHT> display(
    GxEPD2_750c_Z08(/*CS=*/ PIN_EPD_CS,
                    /*DC=*/ PIN_EPD_DC,
                    /*RST=*/ PIN_EPD_RST,
                    /*BUSY=*/ PIN_EPD_BUSY)
);

RTC_DATA_ATTR int boot_count = 0;
RTC_DATA_ATTR int consecutive_failures = 0;

// ---------------------------------------------------------------------------
// WiFi
// ---------------------------------------------------------------------------

bool connect_wifi() {
    Serial.printf("WiFi: connecting to %s...\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - start > 30000) {
            Serial.println("WiFi: timeout");
            return false;
        }
        delay(250);
    }
    Serial.printf("WiFi: connected, IP=%s, RSSI=%d\n",
                  WiFi.localIP().toString().c_str(), WiFi.RSSI());
    return true;
}

// ---------------------------------------------------------------------------
// Image fetch + decode
//
// The render server returns a paletted PNG (3 colors: paper/ink/red). We
// decode it streamingly and push pixels to the panel as we go to keep RAM
// under 50 KB. Full 800x480 RGBA buffer would be 1.5 MB and OOM the chip.
//
// Full streaming decode is left as a TODO; for the first working version we
// allocate a B/W bitmap (48 KB) and a separate red bitmap (48 KB), decode the
// PNG into both, then call display.drawBitmap twice.
// ---------------------------------------------------------------------------

const int W = 800;
const int H = 480;
uint8_t *bw_buffer  = nullptr;   // 1bpp, 0=ink 1=paper, 48 KB
uint8_t *red_buffer = nullptr;   // 1bpp, 0=red 1=transparent, 48 KB

bool allocate_buffers() {
    bw_buffer  = (uint8_t*)heap_caps_malloc(W * H / 8, MALLOC_CAP_SPIRAM);
    red_buffer = (uint8_t*)heap_caps_malloc(W * H / 8, MALLOC_CAP_SPIRAM);
    if (!bw_buffer || !red_buffer) {
        Serial.println("malloc failed for framebuffers (need PSRAM)");
        return false;
    }
    memset(bw_buffer,  0xFF, W * H / 8);   // start as paper
    memset(red_buffer, 0xFF, W * H / 8);
    return true;
}

bool fetch_and_decode() {
    HTTPClient http;
    Serial.printf("HTTP: GET %s\n", RENDER_URL);
    http.begin(RENDER_URL);
    http.setTimeout(15000);

    int code = http.GET();
    if (code != HTTP_CODE_OK) {
        Serial.printf("HTTP: status %d\n", code);
        http.end();
        return false;
    }

    int total = http.getSize();
    Serial.printf("HTTP: %d bytes\n", total);

    // TODO: stream-decode PNG into bw_buffer + red_buffer.
    // For now, dump a few bytes to confirm the pipe works.
    // Recommended PNG library: https://github.com/bitbank2/PNGdec
    WiFiClient *stream = http.getStreamPtr();
    int sniff = stream->available() > 16 ? 16 : stream->available();
    for (int i = 0; i < sniff && stream->available(); i++) {
        Serial.printf("%02x ", stream->read());
    }
    Serial.println();

    http.end();
    return true;
}

// ---------------------------------------------------------------------------
// Display
// ---------------------------------------------------------------------------

void push_to_display() {
    Serial.println("e-ink: refreshing...");
    display.init(115200, true, 2, false);
    display.setRotation(0);
    display.setFullWindow();

    display.firstPage();
    do {
        display.fillScreen(GxEPD_WHITE);
        // TODO: blit bw_buffer + red_buffer here.
        // For first power-on test, draw something visible:
        display.setTextColor(GxEPD_BLACK);
        display.setCursor(40, 60);
        display.setTextSize(3);
        display.print("eink-calendar online");
        display.setCursor(40, 100);
        display.setTextSize(2);
        display.printf("boot count: %d", boot_count);
    } while (display.nextPage());

    display.hibernate();
    Serial.println("e-ink: done");
}

// ---------------------------------------------------------------------------
// Sleep
// ---------------------------------------------------------------------------

void deep_sleep_for(uint32_t seconds) {
    Serial.printf("Sleeping for %u sec.\n", seconds);
    Serial.flush();
    esp_sleep_enable_timer_wakeup((uint64_t)seconds * 1000000ULL);
    // Wake on button press as well.
    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_BUTTON, 0);
    esp_deep_sleep_start();
}

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------

void setup() {
    Serial.begin(115200);
    delay(200);  // let CDC enumerate
    boot_count++;
    Serial.printf("\n=== boot #%d ===\n", boot_count);
    Serial.printf("free heap: %u bytes (PSRAM: %u)\n",
                  ESP.getFreeHeap(), ESP.getFreePsram());

    pinMode(PIN_BUTTON, INPUT_PULLUP);

    if (!allocate_buffers()) {
        deep_sleep_for(RETRY_SECONDS);
        return;
    }

    if (!connect_wifi()) {
        consecutive_failures++;
        if (consecutive_failures >= MAX_RETRIES) {
            consecutive_failures = 0;
            deep_sleep_for(REFRESH_SECONDS);
        } else {
            deep_sleep_for(RETRY_SECONDS);
        }
        return;
    }

    if (!fetch_and_decode()) {
        consecutive_failures++;
        deep_sleep_for(consecutive_failures >= MAX_RETRIES ? REFRESH_SECONDS : RETRY_SECONDS);
        return;
    }

    consecutive_failures = 0;
    push_to_display();

    deep_sleep_for(REFRESH_SECONDS);
}

void loop() {
    // Never reached — setup() always sleeps. loop() exists because Arduino
    // requires it.
}
