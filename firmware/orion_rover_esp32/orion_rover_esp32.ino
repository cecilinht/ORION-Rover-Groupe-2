#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// 1. CONFIGURATION WI-FI & SERVEUR FLASK
const char* WIFI_SSID     = "Cecilin-HT";
const char* WIFI_PASSWORD = "herinjaratanjonacecilinhh1551";
const char* SERVER_URL    = "http://10.58.213.81:5000";

// 2. BROCHES MATERIELLES (GPIO ESP32)
const int ENA_PIN = 25, IN1_PIN = 26, IN2_PIN = 27;
const int ENB_PIN = 14, IN3_PIN = 12, IN4_PIN = 13;

const int ENC_LEFT_PIN  = 34;
const int ENC_RIGHT_PIN = 35;

const int TRIG_FRONT = 5,  ECHO_FRONT = 18;
const int TRIG_LEFT  = 19, ECHO_LEFT  = 21;
const int TRIG_RIGHT = 22, ECHO_RIGHT = 23;

const int IR_S1 = 32, IR_S2 = 33, IR_S3 = 36, IR_S4 = 39, IR_S5 = 4;

const int BUZZER_PIN = 15;
const int LED_R_PIN  = 16, LED_G_PIN = 17, LED_B_PIN = 2;

// 3. CONSTANTES PHYSIQUES & PID
const float SOUND_SPEED_CM_US = 0.0343;
const float WHEEL_RADIUS_CM   = 3.25;
const float WHEEL_BASE_CM     = 15.0;
const int   TICKS_PER_REV     = 20;

float Kp = 28.0, Ki = 0.5, Kd = 12.0;
float pidIntegral = 0.0, pidPrevError = 0.0;
int   baseSpeed = 165;

// 4. ETAT DU ROBOT & ODOMETRIE
enum RobotState { STATE_ATTENTE, STATE_ROUTE, STATE_EVITEMENT, STATE_LIVRAISON, STATE_RETOUR };
RobotState currentState = STATE_ATTENTE;
bool emergencyStop = false;

volatile long leftTicks = 0, rightTicks = 0;
long prevLeftTicks = 0, prevRightTicks = 0;
float posX = 0.0, posY = 0.0, theta = 0.0;

// Moyenne glissante sur 3 mesures par capteur ultrason
float f0 = 100.0, f1 = 100.0, f2 = 100.0;
float l0 = 100.0, l1 = 100.0, l2 = 100.0;
float r0 = 100.0, r1 = 100.0, r2 = 100.0;

unsigned long lastControlTime = 0, lastHttpTime = 0;
const unsigned long CONTROL_DT_MS = 50;
const unsigned long HTTP_DT_MS    = 300;

void IRAM_ATTR onLeftEncoder()  { leftTicks++; }
void IRAM_ATTR onRightEncoder() { rightTicks++; }

void setLedRGB(bool r, bool g, bool b) {
  digitalWrite(LED_R_PIN, r ? HIGH : LOW);
  digitalWrite(LED_G_PIN, g ? HIGH : LOW);
  digitalWrite(LED_B_PIN, b ? HIGH : LOW);
}

void setMotors(int leftPWM, int rightPWM) {
  leftPWM  = constrain(leftPWM,  -255, 255);
  rightPWM = constrain(rightPWM, -255, 255);

  digitalWrite(IN1_PIN, leftPWM >= 0 ? HIGH : LOW);
  digitalWrite(IN2_PIN, leftPWM >= 0 ? LOW  : HIGH);
  analogWrite(ENA_PIN, abs(leftPWM));

  digitalWrite(IN3_PIN, rightPWM >= 0 ? HIGH : LOW);
  digitalWrite(IN4_PIN, rightPWM >= 0 ? LOW  : HIGH);
  analogWrite(ENB_PIN, abs(rightPWM));
}

void stopMotors() { setMotors(0, 0); }

float readUltrasonicRaw(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 25000);
  if (duration == 0) return 200.0;
  return constrain((duration * SOUND_SPEED_CM_US) / 2.0, 0.0, 400.0);
}

void updateOdometry() {
  long dL = leftTicks - prevLeftTicks;
  long dR = rightTicks - prevRightTicks;
  prevLeftTicks = leftTicks; prevRightTicks = rightTicks;

  float distPerTick = (2.0 * PI * WHEEL_RADIUS_CM) / TICKS_PER_REV;
  float dG = dL * distPerTick;
  float dD = dR * distPerTick;
  float deltaS = (dD + dG) / 2.0;
  float deltaTheta = (dD - dG) / WHEEL_BASE_CM;

  posX += deltaS * cos(theta);
  posY += deltaS * sin(theta);
  theta += deltaTheta;
}

float computeLineError(int s1, int s2, int s3, int s4, int s5) {
  int sum = 0, active = 0;
  if (s1 == 0) { sum += -2; active++; }
  if (s2 == 0) { sum += -1; active++; }
  if (s3 == 0) { sum +=  0; active++; }
  if (s4 == 0) { sum +=  1; active++; }
  if (s5 == 0) { sum +=  2; active++; }
  if (active == 0) return pidPrevError;
  return (float)sum / (float)active;
}

void syncWithFlask(float dFront, float dLeft, float dRight, int s1, int s2, int s3, int s4, int s5) {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;

  http.begin(String(SERVER_URL) + "/api/sensors");
  http.addHeader("Content-Type", "application/json");
  JsonDocument doc;
  JsonObject us = doc["ultrasonic"].to<JsonObject>();
  us["front"] = round(dFront * 10.0) / 10.0;
  us["left"]  = round(dLeft  * 10.0) / 10.0;
  us["right"] = round(dRight * 10.0) / 10.0;

  JsonObject irObj = doc["infrared"].to<JsonObject>();
  irObj["s1"] = s1; irObj["s2"] = s2; irObj["s3"] = s3;
  irObj["s4"] = s4; irObj["s5"] = s5;

  String payload;
  serializeJson(doc, payload);
  int code = http.POST(payload);
  Serial.println("POST /api/sensors -> HTTP " + String(code));
  http.end();

  http.begin(String(SERVER_URL) + "/api/status");
  if (http.GET() == 200) {
    JsonDocument statusDoc;
    deserializeJson(statusDoc, http.getString());
    emergencyStop = statusDoc["data"]["emergency_stop"] | false;
  }
  http.end();

  if (currentState == STATE_ATTENTE && !emergencyStop) {
    http.begin(String(SERVER_URL) + "/api/deliveries");
    if (http.GET() == 200) {
      JsonDocument delivDoc;
      deserializeJson(delivDoc, http.getString());
      if (!delivDoc["current_delivery"].isNull()) {
        currentState = STATE_ROUTE;
        tone(BUZZER_PIN, 1200, 200);
      }
    }
    http.end();
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ENA_PIN, OUTPUT); pinMode(IN1_PIN, OUTPUT); pinMode(IN2_PIN, OUTPUT);
  pinMode(ENB_PIN, OUTPUT); pinMode(IN3_PIN, OUTPUT); pinMode(IN4_PIN, OUTPUT);
  pinMode(TRIG_FRONT, OUTPUT); pinMode(ECHO_FRONT, INPUT);
  pinMode(TRIG_LEFT, OUTPUT);  pinMode(ECHO_LEFT, INPUT);
  pinMode(TRIG_RIGHT, OUTPUT); pinMode(ECHO_RIGHT, INPUT);
  pinMode(IR_S1, INPUT); pinMode(IR_S2, INPUT); pinMode(IR_S3, INPUT);
  pinMode(IR_S4, INPUT); pinMode(IR_S5, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_R_PIN, OUTPUT); pinMode(LED_G_PIN, OUTPUT); pinMode(LED_B_PIN, OUTPUT);

  attachInterrupt(digitalPinToInterrupt(ENC_LEFT_PIN),  onLeftEncoder,  RISING);
  attachInterrupt(digitalPinToInterrupt(ENC_RIGHT_PIN), onRightEncoder, RISING);

  setLedRGB(false, false, true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connexion Wi-Fi");
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 25) {
    delay(500);
    Serial.print(".");
    tries++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi connecte ! IP ESP32 : " + WiFi.localIP().toString());
    setLedRGB(false, true, false);
  } else {
    Serial.println("\nEchec Wi-Fi (mode autonome actif)");
    setLedRGB(true, false, false);
  }
}

void loop() {
  unsigned long now = millis();
  if (now - lastControlTime >= CONTROL_DT_MS) {
    float dt = (now - lastControlTime) / 1000.0;
    lastControlTime = now;

    // Decalage moyenne glissante sur 3 mesures
    f2 = f1; f1 = f0; f0 = readUltrasonicRaw(TRIG_FRONT, ECHO_FRONT);
    l2 = l1; l1 = l0; l0 = readUltrasonicRaw(TRIG_LEFT,  ECHO_LEFT);
    r2 = r1; r1 = r0; r0 = readUltrasonicRaw(TRIG_RIGHT, ECHO_RIGHT);

    float dFront = (f0 + f1 + f2) / 3.0;
    float dLeft  = (l0 + l1 + l2) / 3.0;
    float dRight = (r0 + r1 + r2) / 3.0;

    int s1 = digitalRead(IR_S1);
    int s2 = digitalRead(IR_S2);
    int s3 = digitalRead(IR_S3);
    int s4 = digitalRead(IR_S4);
    int s5 = digitalRead(IR_S5);

    updateOdometry();

    if (emergencyStop) { stopMotors(); setLedRGB(true, false, false); return; }

    switch (currentState) {
      case STATE_ATTENTE:
        stopMotors(); setLedRGB(false, false, true);
        break;
      case STATE_ROUTE: {
        int zone = (dFront < 15.0) ? 2 : ((dFront <= 40.0) ? 1 : 0);
        switch (zone) {
          case 2:
            stopMotors(); setLedRGB(true, false, false);
            tone(BUZZER_PIN, 2000, 150);
            currentState = STATE_EVITEMENT;
            break;
          case 1: {
            setLedRGB(true, true, false);
            float ratio = (dFront - 15.0) / 25.0;
            int spd = (int)(90 + ratio * (baseSpeed - 90));
            float err = computeLineError(s1, s2, s3, s4, s5);
            pidIntegral += err * dt;
            float deriv = (err - pidPrevError) / dt;
            pidPrevError = err;
            int corr = (int)(Kp * err + Ki * pidIntegral + Kd * deriv);
            setMotors(spd + corr, spd - corr);
            break;
          }
          default: {
            setLedRGB(false, true, false);
            float err = computeLineError(s1, s2, s3, s4, s5);
            pidIntegral += err * dt;
            float deriv = (err - pidPrevError) / dt;
            pidPrevError = err;
            int corr = (int)(Kp * err + Ki * pidIntegral + Kd * deriv);
            setMotors(baseSpeed + corr, baseSpeed - corr);
            break;
          }
        }
        break;
      }
      case STATE_EVITEMENT:
        setLedRGB(true, false, true);
        if (dLeft >= dRight) setMotors(-130, 130); else setMotors(130, -130);
        delay(350); setMotors(150, 150); delay(500);
        currentState = STATE_ROUTE;
        break;
      case STATE_LIVRAISON:
        stopMotors(); setLedRGB(false, true, true);
        tone(BUZZER_PIN, 1500, 400); delay(2000);
        currentState = STATE_ATTENTE;
        break;
      case STATE_RETOUR:
        setLedRGB(false, true, false);
        break;
    }

    if (now - lastHttpTime >= HTTP_DT_MS) {
      lastHttpTime = now;
      syncWithFlask(dFront, dLeft, dRight, s1, s2, s3, s4, s5);
    }
  }
}
