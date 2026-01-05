/*
 * Railway Crossing Control System
 * Uses Random Forest ML models for ETA/ETD prediction
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

// Pin definitions
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
bool sensor_triggered[3] = {false, false, false};
unsigned long sensor_times[3] = {0, 0, 0};
float sensor_speeds[3] = {0, 0, 0};

// Prediction state
float predicted_eta = 0;
float predicted_etd = 0;
unsigned long prediction_time = 0;
bool predictions_ready = false;

// Control state
bool intersection_notified = false;
bool gates_closed = false;

// Display/buzzer state
unsigned long last_display_update = 0;
unsigned long last_buzzer_toggle = 0;
bool buzzer_state = false;

void setup() {
    Serial.begin(9600);
    
    // Configure pins
    pinMode(SENSOR_0_PIN, INPUT);
    pinMode(SENSOR_1_PIN, INPUT);
    pinMode(SENSOR_2_PIN, INPUT);
    pinMode(CROSSING_RED_LED, OUTPUT);
    pinMode(CROSSING_GREEN_LED, OUTPUT);
    pinMode(INTER_RED_LED, OUTPUT);
    pinMode(INTER_GREEN_LED, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    
    // Setup servo and display
    gateServo.attach(SERVO_PIN);
    gateServo.write(GATE_OPEN_ANGLE);
    display.setBrightness(DISPLAY_BRIGHTNESS);
    display.clear();
    
    // Initial state: all clear
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
}

void loop() {
    checkSensors();
    
    // Calculate predictions after all 3 sensors triggered
    if (sensor_triggered[0] && sensor_triggered[1] && sensor_triggered[2] && !predictions_ready) {
        calculatePredictions();
    }
    
    // Control system based on predictions
    if (predictions_ready) {
        float elapsed = (millis() - prediction_time) / 1000.0;
        float eta_remaining = predicted_eta - elapsed;
        float etd_remaining = predicted_etd - elapsed;
        
        // Stage 1: Before gate closes
        if (!gates_closed) {
            updateDisplay(eta_remaining);
            
            // Notify intersection
            if (eta_remaining <= getNotificationThreshold() && !intersection_notified) {
                notifyIntersection();
            }
            
            // Close gate
            if (eta_remaining <= getGateCloseThreshold()) {
                closeGates();
            }
        }
        // Stage 2: Gate closed, showing ETD countdown
        else {
            updateDisplay(etd_remaining);
            
            // Open gate when train clears
            if (etd_remaining <= 0) {
                openGates();
                resetSystem();
            }
        }
        
        // Update buzzer
        if (intersection_notified) {
            updateBuzzer();
        }
    }
    
    delay(10);
}

void checkSensors() {
    // Check sensor 0 (furthest)
    if (digitalRead(SENSOR_0_PIN) == HIGH && !sensor_triggered[0]) {
        sensor_triggered[0] = true;
        sensor_times[0] = millis();
        Serial.println("[S0] Train detected (furthest sensor)");
    }
    
    // Check sensor 1 (middle)
    if (digitalRead(SENSOR_1_PIN) == HIGH && !sensor_triggered[1] && sensor_triggered[0]) {
        sensor_triggered[1] = true;
        sensor_times[1] = millis();
        
        // Calculate speed between S0 and S1
        float time_01 = (sensor_times[1] - sensor_times[0]) / 1000.0;
        float distance_01 = getSensor0Position() - getSensor1Position();
        sensor_speeds[0] = distance_01 / time_01;
        
        Serial.println("[S1] Train detected (middle sensor)");
        Serial.print("[SPEED] S0->S1: ");
        Serial.print(sensor_speeds[0], 2);
        Serial.println(" m/s");
    }
    
    // Check sensor 2 (nearest)
    if (digitalRead(SENSOR_2_PIN) == HIGH && !sensor_triggered[2] && sensor_triggered[1]) {
        sensor_triggered[2] = true;
        sensor_times[2] = millis();
        
        // Calculate speed between S1 and S2
        float time_12 = (sensor_times[2] - sensor_times[1]) / 1000.0;
        float distance_12 = getSensor1Position() - getSensor2Position();
        sensor_speeds[1] = distance_12 / time_12;
        
        Serial.println("[S2] Train detected (nearest sensor)");
        Serial.print("[SPEED] S1->S2: ");
        Serial.print(sensor_speeds[1], 2);
        Serial.println(" m/s");
    }
}

void calculatePredictions() {
    Serial.println("\n[ML] Computing ETA and ETD...");
    
    // Calculate timing between sensors
    float time_01 = (sensor_times[1] - sensor_times[0]) / 1000.0;
    float time_12 = (sensor_times[2] - sensor_times[1]) / 1000.0;
    
    if (time_01 <= 0 || time_12 <= 0) {
        Serial.println("[ERROR] Invalid sensor timing");
        resetSystem();
        return;
    }
    
    // Calculate distances
    float distance_01 = getSensor0Position() - getSensor1Position();
    float distance_12 = getSensor1Position() - getSensor2Position();
    float distance_to_crossing = getSensor2Position();
    
    // Calculate speeds
    float speed_01 = distance_01 / time_01;
    float speed_12 = distance_12 / time_12;
    
    // Calculate acceleration
    float accel = (speed_12 - speed_01) / time_12;
    
    // Prepare features for ETA model (6 features)
    float eta_features[6] = {
        time_01,
        time_12,
        speed_01,
        speed_12,
        accel,
        distance_to_crossing
    };
    
    // Predict ETA
    float eta = predictETA(eta_features);
    
    // Validate ETA
    if (eta <= 0 || eta > 1000) {
        Serial.println("[WARNING] Invalid ETA, using fallback");
        eta = distance_to_crossing / speed_12;
    }
    
    // Prepare features for ETD model (7 features)
    float etd_features[7] = {
        time_01,
        time_12,
        speed_01,
        speed_12,
        accel,
        distance_to_crossing,
        getDefaultTrainLength()
    };
    
    // Predict ETD
    float etd = predictETD(etd_features);
    
    // Validate ETD
    if (etd <= 0 || etd > 1000 || etd < eta) {
        Serial.println("[WARNING] Invalid ETD, using estimate");
        etd = estimateETD(eta, speed_12);
    }
    
    // Store predictions
    predicted_eta = eta;
    predicted_etd = etd;
    prediction_time = millis();
    predictions_ready = true;
    
    // Log results
    Serial.print("[ML RESULTS] ETA: ");
    Serial.print(predicted_eta, 2);
    Serial.print("s, ETD: ");
    Serial.print(predicted_etd, 2);
    Serial.println("s");
    Serial.print("[INFO] Speed: ");
    Serial.print(speed_12 * 3.6, 1);
    Serial.print(" km/h, Accel: ");
    Serial.print(accel, 3);
    Serial.println(" m/s^2\n");
}

void notifyIntersection() {
    intersection_notified = true;
    digitalWrite(INTER_GREEN_LED, LOW);
    digitalWrite(INTER_RED_LED, HIGH);
    Serial.println("[NOTIFY] Intersection alerted - Red light + Buzzer");
}

void closeGates() {
    gates_closed = true;
    
    gateServo.write(GATE_CLOSED_ANGLE);
    digitalWrite(CROSSING_GREEN_LED, LOW);
    digitalWrite(CROSSING_RED_LED, HIGH);
    
    Serial.println("[GATE] CLOSED - Now showing ETD countdown");
}

void openGates() {
    gateServo.write(GATE_OPEN_ANGLE);
    
    digitalWrite(CROSSING_GREEN_LED, HIGH);
    digitalWrite(CROSSING_RED_LED, LOW);
    digitalWrite(INTER_GREEN_LED, HIGH);
    digitalWrite(INTER_RED_LED, LOW);
    digitalWrite(BUZZER_PIN, LOW);
    
    display.clear();
    
    Serial.println("[GATE] OPENED - All clear\n");
}

void updateDisplay(float time_remaining) {
    unsigned long now = millis();
    
    if (now - last_display_update >= getDisplayUpdateInterval()) {
        int remaining = (int)time_remaining;
        if (remaining < 0) remaining = 0;
        
        // Display as MM:SS
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
    // Reset sensors
    for (int i = 0; i < 3; i++) {
        sensor_triggered[i] = false;
        sensor_times[i] = 0;
        sensor_speeds[i] = 0;
    }
    
    // Reset predictions
    predicted_eta = 0;
    predicted_etd = 0;
    prediction_time = 0;
    predictions_ready = false;
    
    // Reset control state
    intersection_notified = false;
    gates_closed = false;
    
    Serial.println("[RESET] System ready for next train");
}