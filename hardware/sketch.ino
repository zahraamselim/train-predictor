/*
 * Level Crossing System - Physical Demo
 * 
 * Behavior:
 * 1. Train triggers S0, S1, S2 → Calculate ETA/ETD
 * 2. Display shows countdown until gate closes (ETA)
 * 3. When gate closes → Display shows countdown until gate opens (ETD)
 * 4. Crossing LEDs: Green when open, Red when closed
 * 5. Intersection: Red + buzzer when notification active
 */

#include <Servo.h>
#include <TM1637Display.h>
#include "eta_model.h"
#include "crossing_config.h"

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

// Sensor state
unsigned long sensor0_time = 0;
unsigned long sensor1_time = 0;
unsigned long sensor2_time = 0;
bool sensor0_triggered = false;
bool sensor1_triggered = false;
bool sensor2_triggered = false;

// Prediction state
float predicted_eta = 0;
float predicted_etd = 0;
unsigned long prediction_time = 0;
bool predictions_calculated = false;

// Control state
bool intersection_notified = false;
bool gates_closed = false;
unsigned long gate_close_time = 0;

// Display/buzzer state
unsigned long last_display_update = 0;
unsigned long last_buzzer_toggle = 0;
bool buzzer_state = false;

void printTimestamp() {
    unsigned long seconds = millis() / 1000;
    unsigned long minutes = seconds / 60;
    seconds = seconds % 60;
    Serial.print("[");
    if (minutes < 10) Serial.print("0");
    Serial.print(minutes);
    Serial.print(":");
    if (seconds < 10) Serial.print("0");
    Serial.print(seconds);
    Serial.print("] ");
}

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
    
    // Initial state: All clear
    digitalWrite(CROSSING_GREEN_LED, HIGH);
    digitalWrite(CROSSING_RED_LED, LOW);
    digitalWrite(INTER_GREEN_LED, HIGH);
    digitalWrite(INTER_RED_LED, LOW);
    digitalWrite(BUZZER_PIN, LOW);
    
    printTimestamp();
    Serial.println("Level Crossing System Ready");
    printTimestamp();
    Serial.print("Sensors at: S0=");
    Serial.print(getSensor0Position(), 2);
    Serial.print("m, S1=");
    Serial.print(getSensor1Position(), 2);
    Serial.print("m, S2=");
    Serial.print(getSensor2Position(), 2);
    Serial.println("m");
    printTimestamp();
    Serial.print("Gate close: ");
    Serial.print(getGateCloseThreshold(), 1);
    Serial.print("s, Notify: ");
    Serial.print(getNotificationThreshold(), 1);
    Serial.println("s");
}

void loop() {
    checkSensors();
    
    // After all sensors triggered, calculate predictions
    if (sensor0_triggered && sensor1_triggered && sensor2_triggered && !predictions_calculated) {
        calculatePredictions();
    }
    
    // Once we have predictions, control the system
    if (predictions_calculated) {
        float elapsed = (millis() - prediction_time) / 1000.0;
        float eta_remaining = predicted_eta - elapsed;
        float etd_remaining = predicted_etd - elapsed;
        
        // Stage 1: Before gate close - show ETA countdown
        if (!gates_closed) {
            updateETACountdown(eta_remaining);
            
            // Check if should notify intersection
            if (eta_remaining <= getNotificationThreshold() && !intersection_notified) {
                notifyIntersection();
            }
            
            // Check if should close gates
            if (eta_remaining <= getGateCloseThreshold()) {
                closeGates();
            }
        }
        
        // Stage 2: After gate close - show ETD countdown
        if (gates_closed) {
            updateETDCountdown(etd_remaining);
            
            // Check if should open gates
            if (etd_remaining <= 0) {
                openGates();
                resetSystem();
            }
        }
        
        // Update buzzer while notification active
        if (intersection_notified) {
            updateBuzzer();
        }
    }
    
    delay(10);
}

void checkSensors() {
    if (digitalRead(SENSOR_0_PIN) == HIGH && !sensor0_triggered) {
        sensor0_triggered = true;
        sensor0_time = millis();
        printTimestamp();
        Serial.println("[SENSOR 0] Train detected (furthest)");
    }
    
    if (digitalRead(SENSOR_1_PIN) == HIGH && !sensor1_triggered && sensor0_triggered) {
        sensor1_triggered = true;
        sensor1_time = millis();
        printTimestamp();
        Serial.println("[SENSOR 1] Train detected (middle)");
        printTimestamp();
        Serial.print("[TIMING] S0->S1: ");
        Serial.print((sensor1_time - sensor0_time) / 1000.0, 3);
        Serial.println("s");
    }
    
    if (digitalRead(SENSOR_2_PIN) == HIGH && !sensor2_triggered && sensor1_triggered) {
        sensor2_triggered = true;
        sensor2_time = millis();
        printTimestamp();
        Serial.println("[SENSOR 2] Train detected (nearest)");
        printTimestamp();
        Serial.print("[TIMING] S1->S2: ");
        Serial.print((sensor2_time - sensor1_time) / 1000.0, 3);
        Serial.println("s");
    }
}

void calculatePredictions() {
    printTimestamp();
    Serial.println("[CALCULATING] Computing ETA and ETD...");
    
    // Calculate timing and speeds from sensors
    float time_01 = (sensor1_time - sensor0_time) / 1000.0;
    float time_12 = (sensor2_time - sensor1_time) / 1000.0;
    
    if (time_01 <= 0 || time_12 <= 0) {
        printTimestamp();
        Serial.println("[ERROR] Invalid sensor timing");
        resetSystem();
        return;
    }
    
    float distance_01 = getSensor0Position() - getSensor1Position();
    float distance_12 = getSensor1Position() - getSensor2Position();
    
    float speed_01 = distance_01 / time_01;
    float speed_12 = distance_12 / time_12;
    float acceleration = (speed_12 - speed_01) / time_12;
    float distance = getSensor2Position();
    
    // Build features for ETA prediction
    float eta_features[6] = {
        time_01,
        time_12,
        speed_01,
        speed_12,
        acceleration,
        distance
    };
    
    // Predict ETA
    float eta = predictETA(eta_features);
    if (eta <= 0 || eta > 1000) {
        printTimestamp();
        Serial.println("[WARNING] Invalid ETA, using fallback");
        eta = distance / speed_12;
    }
    
    // Predict ETD (simplified - estimate from ETA)
    float etd = estimateETD(eta, speed_12);
    if (etd <= 0 || etd > 1000) {
        printTimestamp();
        Serial.println("[WARNING] Invalid ETD, using fallback");
        float train_length = getDefaultTrainLength();
        etd = (distance + train_length) / speed_12;
    }
    
    predicted_eta = eta;
    predicted_etd = etd;
    prediction_time = millis();
    predictions_calculated = true;
    
    printTimestamp();
    Serial.print("[PREDICTION] ETA: ");
    Serial.print(predicted_eta, 1);
    Serial.print("s, ETD: ");
    Serial.print(predicted_etd, 1);
    Serial.println("s");
    printTimestamp();
    Serial.print("[INFO] Train speed: ");
    Serial.print(speed_12 * 3.6, 1);
    Serial.print(" km/h, Accel: ");
    Serial.print(acceleration, 3);
    Serial.println(" m/s^2");
}

void notifyIntersection() {
    intersection_notified = true;
    
    digitalWrite(INTER_GREEN_LED, LOW);
    digitalWrite(INTER_RED_LED, HIGH);
    
    printTimestamp();
    Serial.println("[NOTIFICATION] Intersection alerted - Red light + Buzzer");
}

void closeGates() {
    gates_closed = true;
    gate_close_time = millis();
    
    gateServo.write(GATE_CLOSED_ANGLE);
    
    digitalWrite(CROSSING_GREEN_LED, LOW);
    digitalWrite(CROSSING_RED_LED, HIGH);
    
    printTimestamp();
    Serial.println("[GATE] CLOSED - Crossing red, now showing ETD countdown");
}

void openGates() {
    gateServo.write(GATE_OPEN_ANGLE);
    
    digitalWrite(CROSSING_GREEN_LED, HIGH);
    digitalWrite(CROSSING_RED_LED, LOW);
    digitalWrite(INTER_GREEN_LED, HIGH);
    digitalWrite(INTER_RED_LED, LOW);
    
    digitalWrite(BUZZER_PIN, LOW);
    buzzer_state = false;
    
    display.clear();
    
    printTimestamp();
    Serial.println("[GATE] OPENED - All clear, buzzer stopped");
}

void updateETACountdown(float eta_remaining) {
    unsigned long now = millis();
    
    if (now - last_display_update >= getDisplayUpdateInterval()) {
        int remaining = (int)eta_remaining;
        if (remaining < 0) remaining = 0;
        
        int minutes = remaining / 60;
        int seconds = remaining % 60;
        
        display.showNumberDecEx(minutes * 100 + seconds, 0b01000000, true);
        
        last_display_update = now;
    }
}

void updateETDCountdown(float etd_remaining) {
    unsigned long now = millis();
    
    if (now - last_display_update >= getDisplayUpdateInterval()) {
        int remaining = (int)etd_remaining;
        if (remaining < 0) remaining = 0;
        
        int minutes = remaining / 60;
        int seconds = remaining % 60;
        
        display.showNumberDecEx(minutes * 100 + seconds, 0b01000000, true);
        
        last_display_update = now;
    }
}

void updateBuzzer() {
    unsigned long now = millis();
    
    if (now - last_buzzer_toggle >= getBuzzerInterval()) {
        buzzer_state = !buzzer_state;
        digitalWrite(BUZZER_PIN, buzzer_state ? HIGH : LOW);
        last_buzzer_toggle = now;
    }
}

void resetSystem() {
    sensor0_triggered = false;
    sensor1_triggered = false;
    sensor2_triggered = false;
    
    sensor0_time = 0;
    sensor1_time = 0;
    sensor2_time = 0;
    
    predicted_eta = 0;
    predicted_etd = 0;
    prediction_time = 0;
    predictions_calculated = false;
    
    intersection_notified = false;
    gates_closed = false;
    gate_close_time = 0;
    
    printTimestamp();
    Serial.println("[SYSTEM] Reset - Ready for next train");
}