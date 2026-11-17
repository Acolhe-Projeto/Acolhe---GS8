/* Acolhe: Arduino UNO + LCD I2C + DHT11 + L298N.
 * ENA/ENB jumpers INSTALLED. No Arduino wires on ENA/ENB or D5/D6.
 * Remove the 5V-regulator jumper when supplying the L298N logic externally.
 * Motors run at full supply while pulsing; only duration/direction are controlled.
 * Keep motor power OFF during upload/reset. GPIOs float until setup executes.
 * Protocol ACOLHE_V2, 115200 baud, newline. ACK never proves physical movement.
 */
#include <Arduino.h>
#include <Wire.h>
#include <DHT.h>
#include <hd44780.h>
#include <hd44780ioClass/hd44780_I2Cexp.h>

#if !defined(ARDUINO_AVR_UNO)
#error "Select Arduino Uno: this firmware matches the Uno wiring without enable wires."
#endif

const uint8_t CABECA_IN1 = 2, CABECA_IN2 = 3;
const uint8_t BRACO_IN3 = 4, BRACO_IN4 = 7;
const uint8_t DHT_PIN = 8;
const uint8_t IN_A[] = {CABECA_IN1, BRACO_IN3};
const uint8_t IN_B[] = {CABECA_IN2, BRACO_IN4};
DHT dht(DHT_PIN, DHT11);
hd44780_I2Cexp lcd; // Uno: SDA=A4, SCL=A5; backpack address auto-detected.

struct Motor { uint16_t ms; int8_t direction; bool configured; };
Motor motors[2] = {{100, 1, false}, {100, 1, false}};
bool lcdOK = false, valid = false, moving = false, haveGesture = false, lcdDirty = false;
float temperature = 0, humidity = 0;
uint32_t lastSample = 0, lastPing = 0, gestureStart = 0, gestureDuration = 0, lastGesture = 0;
char line[80]; uint8_t used = 0; bool overflow = false;
char displayState[17] = "Acolhe pronto";

void motorStop() {
  // With enables held HIGH by jumpers, equal inputs brake each motor.
  for (uint8_t i = 0; i < 2; i++) { digitalWrite(IN_A[i], LOW); digitalWrite(IN_B[i], LOW); }
  moving = false;
}
void disarm() { motorStop(); motors[0].configured = false; motors[1].configured = false; }
void error(const __FlashStringHelper *text) {
  Serial.print(F("{\"type\":\"error\",\"message\":\"")); Serial.print(text); Serial.println(F("\"}"));
}
void refreshLCD() {
  if (!lcdOK) return;
  if (moving) { lcdDirty = true; return; }
  lcdDirty = false;
  lcd.setCursor(0, 0); lcd.print(F("                ")); lcd.setCursor(0, 0); lcd.print(displayState);
  lcd.setCursor(0, 1); lcd.print(F("                ")); lcd.setCursor(0, 1);
  if (valid) { lcd.print(temperature, 0); lcd.print(F("C Umid:")); lcd.print(humidity, 0); lcd.print('%'); }
  else lcd.print(F("DHT indisponivel"));
}
void hello() {
  Serial.print(F("{\"type\":\"hello\",\"version\":\"ACOLHE_V2\",\"board\":\"UNO\",\"motor_control\":\"direction_only\",\"pwm_supported\":false,\"lcd_enabled\":true,\"lcd_ok\":"));
  Serial.print(lcdOK ? F("true") : F("false")); Serial.println(F(",\"motors_enabled\":false}"));
}
void sample() {
  humidity = dht.readHumidity(); temperature = dht.readTemperature();
  valid = !isnan(humidity) && !isnan(temperature) && temperature >= 0 && temperature <= 50 && humidity >= 0 && humidity <= 100;
  Serial.print(F("{\"type\":\"sensor\",\"version\":\"ACOLHE_V2\",\"valid\":"));
  Serial.print(valid ? F("true") : F("false"));
  Serial.print(F(",\"temperature\":")); if (valid) Serial.print(temperature, 1); else Serial.print(F("null"));
  Serial.print(F(",\"humidity\":")); if (valid) Serial.print(humidity, 1); else Serial.print(F("null"));
  Serial.println('}'); refreshLCD();
}
int motorIndex(const char *name) { return !strcmp(name, "head") ? 0 : !strcmp(name, "arm") ? 1 : -1; }
void pulse(uint8_t index, uint16_t ms, int8_t direction) {
  uint32_t now = millis();
  if (now - lastPing >= 2000UL) { error(F("heartbeat_required")); return; }
  if (moving || (haveGesture && now - lastGesture < 2000UL)) { error(F("cooldown")); return; }
  motorStop();
  digitalWrite(IN_A[index], direction == 1 ? HIGH : LOW);
  digitalWrite(IN_B[index], direction == 1 ? LOW : HIGH);
  gestureStart = lastGesture = now; gestureDuration = ms; moving = haveGesture = true;
  Serial.println(F("{\"type\":\"ack\",\"command\":\"pulse_started\",\"physical_verified\":false}"));
}
void command(char *text) {
  if (!strcmp(text, "PING")) { lastPing = millis(); Serial.println(F("{\"type\":\"pong\"}")); return; }
  if (!strcmp(text, "HELLO")) { disarm(); hello(); return; }
  if (!strcmp(text, "STOP")) { disarm(); strcpy(displayState, "Acolhe parado"); refreshLCD(); Serial.println(F("{\"type\":\"ack\",\"command\":\"stop\"}")); return; }
  if (!strncmp(text, "STATE ", 6)) {
    const char *state = text + 6;
    if (!strcmp(state,"READY")) strcpy(displayState,"Acolhe pronto");
    else if (!strcmp(state,"LISTEN")) strcpy(displayState,"Acolhe ouvindo");
    else if (!strcmp(state,"THINK")) strcpy(displayState,"Acolhe pensando");
    else if (!strcmp(state,"SPEAK")) strcpy(displayState,"Acolhe falando");
    else if (!strcmp(state,"ERROR")) strcpy(displayState,"Acolhe verificar");
    else { error(F("invalid_state")); return; }
    refreshLCD(); return;
  }
  char action[8], name[8], extra; int ms, direction;
  if (sscanf(text, "%7s %7s %d %d %c", action, name, &ms, &direction, &extra) == 4 && (!strcmp(action,"TEST") || !strcmp(action,"CONFIG"))) {
    int index = motorIndex(name);
    if (index < 0 || ms < 1 || ms > 150 || (direction != -1 && direction != 1)) { error(F("invalid_limits")); return; }
    if (!strcmp(action, "TEST")) pulse(index, ms, direction);
    else {
      motors[index].ms = ms; motors[index].direction = direction; motors[index].configured = true;
      Serial.print(F("{\"type\":\"ack\",\"command\":\"config\",\"motor\":\"")); Serial.print(name); Serial.println(F("\"}"));
    }
    return;
  }
  if (sscanf(text, "%7s %7s %c", action, name, &extra) == 2 && !strcmp(action, "GESTURE")) {
    int index = motorIndex(name);
    if (index < 0 || !motors[0].configured || !motors[1].configured) { error(F("motors_locked")); return; }
    pulse(index, motors[index].ms, motors[index].direction); return;
  }
  error(F("unknown_command"));
}
void setup() {
  for (uint8_t i=0; i<2; i++) {
    digitalWrite(IN_A[i],LOW); digitalWrite(IN_B[i],LOW);
    pinMode(IN_A[i],OUTPUT); pinMode(IN_B[i],OUTPUT);
  }
  disarm(); Serial.begin(115200); dht.begin(); Wire.begin();
#if defined(WIRE_HAS_TIMEOUT)
  Wire.setWireTimeout(25000, true);
#endif
  lcdOK = lcd.begin(16, 2) == 0;
  if (lcdOK) lcd.backlight();
  refreshLCD(); lastPing = millis(); hello();
}
void loop() {
  uint32_t now = millis();
  if (moving && now - gestureStart >= gestureDuration) motorStop();
  if (!moving && lcdDirty) refreshLCD();
  if (now - lastPing >= 2000UL) disarm();
  // Never perform a sensor read or I2C update while a motor pulse is active.
  if (!moving && now - lastSample >= 2000UL) { lastSample = now; sample(); }
  uint8_t budget = 80;
  while (budget-- && Serial.available()) {
    char c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      if (overflow) error(F("command_too_long"));
      else if (used) { line[used] = 0; command(line); }
      used = 0; overflow = false;
    } else if (used < sizeof(line)-1 && !overflow) line[used++] = c;
    else overflow = true;
  }
}
