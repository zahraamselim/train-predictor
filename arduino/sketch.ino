/*
 * Railway Crossing Control System
 * Uses ML models for ETA/ETD prediction
 * 
 * Hardware:
 * - 3 IR sensors (pins 2, 3, 4)
 * - Servo motor for gate (pin 5)
 * - 4 LEDs: crossing (6, 7), intersection (8, 9)
 * - Buzzer (pin 10)
 * - TM1637 display (pins 11, 12)
 */

#include <Servo.h>
#include <TM1637Display.h>
#include "model.h"
#include "config.h"

#define SENSOR_0_PIN 2
#define SENSOR_1_PIN 3
#define SENSOR_2_PIN 4
#define SERVO_PIN 5
#define CROSSING_GREEN_LED 6
#define CROSSING_RED_LED 7
#define INTER_GREEN_LED 8
#define INTER_RED_LED 9
#define BUZZER_PIN 10
#define TM1637_CLK 11
#define TM1637_DIO 12

Servo gateServo;
TM1637Display display(TM1637_CLK, TM1637_DIO);

bool sensor_triggered[3] = {false, false, false};
unsigned long sensor_times[3] = {0, 0, 0};

float predicted_eta = 0;
float predicted_etd = 0;
unsigned long prediction_time = 0;
bool predictions_ready = false;

bool intersection_notified = false;
bool gates_closed = false;

unsigned long last_display_update = 0;
unsigned long last_buzzer_toggle = 0;
unsigned long last_led_flash = 0;
bool buzzer_state = false;
bool led_flash_state = false;

void setup() {
    Serial.begin(9600);
    
    pinMode(SENSOR_0_PIN, INPUT);
    pinMode(SENSOR_1_PIN, INPUT);
    pinMode(SENSOR_2_PIN, INPUT);
    pinMode(CROSSING_RED_LED, OUTPUT);
    pinMode(CROSSING_GREEN_LED, OUTPUT);
    pinMode(INTER_RED_LED, OUTPUT);
    pinMode(INTER_GREEN_LED, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    
    gateServo.attach(SERVO_PIN);
    gateServo.write(GATE_OPEN_ANGLE);
    display.setBrightness(DISPLAY_BRIGHTNESS);
    display.clear();
    
    digitalWrite(CROSSING_GREEN_LED, HIGH);
    digitalWrite(CROSSING_RED_LED, LOW);
    digitalWrite(INTER_GREEN_LED, HIGH);
    digitalWrite(INTER_RED_LED, LOW);
    digitalWrite(BUZZER_PIN, LOW);
    
    Serial.println("Railway Crossing System Ready");
    Serial.print("Sensors: S0=");
    Serial.print(getSensor0Position(), 2);
    Serial.print("m, S1=");
    Serial.print(getSensor1Position(), 2);
    Serial.print("m, S2=");
    Serial.print(getSensor2Position(), 2);
    Serial.println("m");
    Serial.print("Gate close: ");
    Serial.print(getGateCloseThreshold(), 1);
    Serial.print("s, Notification: ");
    Serial.print(getNotificationThreshold(), 1);
    Serial.println("s\n");
}

void loop() {
    checkSensors();
    
    if (sensor_triggered[0] && sensor_triggered[1] && sensor_triggered[2] && !predictions_ready) {
        calculatePredictions();
    }
    
    if (predictions_ready) {
        float elapsed = (millis() - prediction_time) / 1000.0;
        float eta_remaining = predicted_eta - elapsed;
        float etd_remaining = predicted_etd - elapsed;
        
        if (!gates_closed) {
            updateDisplay(eta_remaining);
            
            if (eta_remaining <= getNotificationThreshold() && !intersection_notified) {
                notifyIntersection();
            }
            
            if (eta_remaining <= getGateCloseThreshold()) {
                closeGates();
            }
        } else {
            updateDisplay(etd_remaining);
            updateFlashingLED();
            
            if (etd_remaining <= 0) {
                openGates();
                resetSystem();
            }
        }
        
        if (intersection_notified) {
            updateBuzzer();
        }
    }
    
    delay(30);
}

void checkSensors() {
    if (digitalRead(SENSOR_0_PIN) == HIGH && !sensor_triggered[0]) {
        sensor_triggered[0] = true;
        sensor_times[0] = millis();
        Serial.println("[S0] Train detected (furthest)");
    }
    
    if (digitalRead(SENSOR_1_PIN) == HIGH && !sensor_triggered[1] && sensor_triggered[0]) {
        sensor_triggered[1] = true;
        sensor_times[1] = millis();
        
        float time_01 = (sensor_times[1] - sensor_times[0]) / 1000.0;
        float distance_01 = getSensor0Position() - getSensor1Position();
        float speed_01 = distance_01 / time_01;
        
        Serial.println("[S1] Train detected (middle)");
        Serial.print("[SPEED] S0->S1: ");
        Serial.print(speed_01, 3);
        Serial.print(" m/s (");
        Serial.print(speed_01 * 100, 1);
        Serial.print(" cm/s) in ");
        Serial.print(time_01, 2);
        Serial.println("s");
    }
    
    if (digitalRead(SENSOR_2_PIN) == HIGH && !sensor_triggered[2] && sensor_triggered[1]) {
        sensor_triggered[2] = true;
        sensor_times[2] = millis();
        
        float time_12 = (sensor_times[2] - sensor_times[1]) / 1000.0;
        float distance_12 = getSensor1Position() - getSensor2Position();
        float speed_12 = distance_12 / time_12;
        
        Serial.println("[S2] Train detected (nearest)");
        Serial.print("[SPEED] S1->S2: ");
        Serial.print(speed_12, 3);
        Serial.print(" m/s (");
        Serial.print(speed_12 * 100, 1);
        Serial.print(" cm/s) in ");
        Serial.print(time_12, 2);
        Serial.println("s");
    }
}

void calculatePredictions() {
    Serial.println("\n[ML] Computing ETA and ETD...");
    
    float time_01 = (sensor_times[1] - sensor_times[0]) / 1000.0;
    float time_12 = (sensor_times[2] - sensor_times[1]) / 1000.0;
    
    if (time_01 <= 0 || time_12 <= 0) {
        Serial.println("[ERROR] Invalid sensor timing");
        resetSystem();
        return;
    }
    
    float distance_01 = getSensor0Position() - getSensor1Position();
    float distance_12 = getSensor1Position() - getSensor2Position();
    float distance_to_crossing = getSensor2Position();
    
    float speed_01 = distance_01 / time_01;
    float speed_12 = distance_12 / time_12;
    float accel = (speed_12 - speed_01) / time_12;
    
    float eta_features[6] = {
        time_01, time_12, speed_01, speed_12, accel, distance_to_crossing
    };
    
    float eta = predictETA(eta_features);
    
    if (eta <= 0 || eta > 100) {
        Serial.println("[WARNING] Invalid ETA, using fallback");
        eta = distance_to_crossing / speed_12;
    }
    
    float etd_features[7] = {
        time_01, time_12, speed_01, speed_12, accel,
        distance_to_crossing, getDefaultTrainLength()
    };
    
    float etd = predictETD(etd_features);
    
    if (etd <= 0 || etd > 100 || etd < eta) {
        Serial.println("[WARNING] Invalid ETD, using estimate");
        etd = estimateETD(eta, speed_12);
    }
    
    predicted_eta = eta;
    predicted_etd = etd;
    prediction_time = millis();
    predictions_ready = true;
    
    Serial.print("[ML RESULTS] ETA: ");
    Serial.print(predicted_eta, 2);
    Serial.print("s, ETD: ");
    Serial.print(predicted_etd, 2);
    Serial.println("s");
    Serial.print("[INFO] Speed: ");
    Serial.print(speed_12, 3);
    Serial.print(" m/s (");
    Serial.print(speed_12 * 100, 1);
    Serial.print(" cm/s), Accel: ");
    Serial.print(accel, 4);
    Serial.println(" m/s^2\n");
}

void notifyIntersection() {
    intersection_notified = true;
    digitalWrite(INTER_GREEN_LED, LOW);
    digitalWrite(INTER_RED_LED, HIGH);
    Serial.println("[NOTIFY] Intersection alerted");
}

void closeGates() {
    gates_closed = true;
    gateServo.write(GATE_CLOSED_ANGLE);
    digitalWrite(CROSSING_GREEN_LED, LOW);
    digitalWrite(CROSSING_RED_LED, HIGH);
    led_flash_state = true;
    last_led_flash = millis();
    Serial.println("[GATE] CLOSED");
}

void openGates() {
    gateServo.write(GATE_OPEN_ANGLE);
    digitalWrite(CROSSING_GREEN_LED, HIGH);
    digitalWrite(CROSSING_RED_LED, LOW);
    digitalWrite(INTER_GREEN_LED, HIGH);
    digitalWrite(INTER_RED_LED, LOW);
    digitalWrite(BUZZER_PIN, LOW);
    display.clear();
    Serial.println("[GATE] OPENED\n");
}

void updateDisplay(float time_remaining) {
    unsigned long now = millis();
    unsigned long update_interval = gates_closed ? 50 : 100;
    
    if (now - last_display_update >= update_interval) {
        if (time_remaining < 0) time_remaining = 0;
        
        int seconds = (int)time_remaining;
        int centiseconds = (int)((time_remaining - seconds) * 100);
        
        if (seconds > 99) seconds = 99;
        if (centiseconds > 99) centiseconds = 99;
        if (centiseconds < 0) centiseconds = 0;
        
        int display_value = seconds * 100 + centiseconds;
        
        display.showNumberDecEx(display_value, 0b00100000, true);
        
        last_display_update = now;
    }
}

void updateBuzzer() {
    unsigned long now = millis();
    unsigned long beep_interval = gates_closed ? 200 : 500;
    
    if (now - last_buzzer_toggle >= beep_interval) {
        buzzer_state = !buzzer_state;
        digitalWrite(BUZZER_PIN, buzzer_state ? HIGH : LOW);
        last_buzzer_toggle = now;
    }
}

void updateFlashingLED() {
    unsigned long now = millis();
    
    if (now - last_led_flash >= 200) {
        led_flash_state = !led_flash_state;
        digitalWrite(CROSSING_RED_LED, led_flash_state ? HIGH : LOW);
        last_led_flash = now;
    }
}

void resetSystem() {
    for (int i = 0; i < 3; i++) {
        sensor_triggered[i] = false;
        sensor_times[i] = 0;
    }
    
    predicted_eta = 0;
    predicted_etd = 0;
    prediction_time = 0;
    predictions_ready = false;
    intersection_notified = false;
    gates_closed = false;
    
    Serial.println("[RESET] System ready\n");
}