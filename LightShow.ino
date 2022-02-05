// NeoPixel test program showing use of the WHITE channel for RGBW
// pixels only (won't look correct on regular RGB NeoPixel strips).

#include <Adafruit_NeoPixel.h>

#define BAUD       57600

#define LED_PIN    13
#define LED_COUNT  5
// NeoPixel brightness, 0 (min) to 255 (max)
#define BRIGHTNESS .05 * 255 // Set BRIGHTNESS to about 1/5 (max = 255)


// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRBW + NEO_KHZ800);

typedef struct{
  int i = 0;
  int r = 0;
  int g = 0;
  int b = 0;
  int w = 0;
}pixel;

void setup() {
  // Setup LEDs
  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(BRIGHTNESS);
  // Setup serial
  Serial.begin(BAUD); // opens serial port, sets data rate to 9600 bps
  Serial.println("Starting LightShow");
}

int color_option = 0;
void loop() {
}

void serialEvent() {
  // Serial.println("PACKET RECEIVED");
  color_option = (color_option + 1) % 4;
  while (Serial.available()) {
    Serial.find('|');
    long i = Serial.parseInt();
    long r = Serial.parseInt();
    long g = Serial.parseInt();
    long b = Serial.parseInt();
    long w = Serial.parseInt();

    strip.setPixelColor(i, strip.Color(r, g, b, w));
    // printPixel(i, r, g, b, w);
    strip.show();
  }
}

void printPixel(int i, int r, int g, int b, int w) {
    Serial.print(i, DEC);
    Serial.print("-[");
    Serial.print(r, DEC);
    Serial.print(", ");
    Serial.print(g, DEC);
    Serial.print(", ");
    Serial.print(b, DEC);
    Serial.print(", ");
    Serial.print(w, DEC);
    Serial.print("]\n");
}