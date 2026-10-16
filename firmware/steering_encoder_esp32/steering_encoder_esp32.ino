// ESP32-WROOM steering encoder feedback for vehicle_bridge/encoder_node.
// Decodes an incremental A/B quadrature encoder (x4) and streams the running
// count, one integer per line ("1234\r\n"), at 115200 baud over USB serial.
// That is exactly what encoder_node's default line_regex expects.
//
// Wiring: encoder A -> GPIO32, B -> GPIO33, encoder GND -> GND. Use 3.3 V
// logic only (the ESP32 is not 5 V tolerant: level-shift an open-collector
// or 5 V encoder). Internal pull-ups are enabled for open-collector outputs.
//
// Sign: count rises when A leads B. If turning right reads negative on
// /steering/angle, set `invert: true` in config/encoder.yaml (don't edit here).

constexpr uint8_t PIN_A = 32;
constexpr uint8_t PIN_B = 33;
constexpr uint32_t BAUD = 115200;
constexpr uint32_t PERIOD_MS = 10;  // 100 Hz; the bridge's encoder_timeout_s is 0.5 s

volatile int32_t count = 0;
volatile uint8_t prev = 0;

// Index = (prev_AB << 2) | new_AB; value = step. Invalid (skipped-state) jumps are 0.
static const int8_t STEP[16] = {0, 1, -1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0};

void IRAM_ATTR onEdge() {
  uint8_t cur = (digitalRead(PIN_A) << 1) | digitalRead(PIN_B);
  count += STEP[(prev << 2) | cur];
  prev = cur;
}

void setup() {
  Serial.begin(BAUD);
  pinMode(PIN_A, INPUT_PULLUP);
  pinMode(PIN_B, INPUT_PULLUP);
  prev = (digitalRead(PIN_A) << 1) | digitalRead(PIN_B);
  attachInterrupt(digitalPinToInterrupt(PIN_A), onEdge, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_B), onEdge, CHANGE);
}

void loop() {
  static uint32_t last = 0;
  if (millis() - last >= PERIOD_MS) {
    last += PERIOD_MS;
    Serial.println((int32_t)count);  // aligned 32-bit read is atomic on ESP32
  }
}
