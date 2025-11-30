/*
 * Level Crossing System - Standalone Arduino
 * Components: 3x PIR Sensors, 1x Servo, 1x TM1637, 4x LEDs, 1x Buzzer
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

const float SENSOR_0_POS = 54.0;
const float SENSOR_1_POS = 32.4;
const float SENSOR_2_POS = 16.2;

Servo gateServo;
TM1637Display display(TM1637_CLK, TM1637_DIO);

unsigned long sensor0_time = 0;
unsigned long sensor1_time = 0;
unsigned long sensor2_time = 0;
bool sensor0_triggered = false;
bool sensor1_triggered = false;
bool sensor2_triggered = false;

float predicted_eta = 0;
unsigned long eta_calculated_time = 0;
bool gates_closed = false;
bool intersection_notified = false;
unsigned long gate_close_time = 0;

int last_logged_eta = -1;

const int GATE_OPEN_ANGLE = 90;
const int GATE_CLOSED_ANGLE = 0;

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
    
    display.setBrightness(0x0f);
    display.clear();
    
    digitalWrite(CROSSING_GREEN_LED, HIGH);
    digitalWrite(CROSSING_RED_LED, LOW);
    digitalWrite(INTER_GREEN_LED, HIGH);
    digitalWrite(INTER_RED_LED, LOW);
    
    printTimestamp();
    Serial.println("Level Crossing System Ready");
    printTimestamp();
    Serial.println("Standalone Mode - ML Embedded");
    printTimestamp();
    Serial.print("Gate close threshold: ");
    Serial.print(getGateCloseThreshold());
    Serial.println("s");
    printTimestamp();
    Serial.print("Notification threshold: ");
    Serial.print(getNotificationThreshold());
    Serial.println("s");
}

void loop() {
    checkSensors();
    
    if (sensor0_triggered && sensor1_triggered && sensor2_triggered) {
        if (predicted_eta == 0) {
            calculateETAWithML();
        }
        
        if (predicted_eta > 0) {
            float elapsed = (millis() - eta_calculated_time) / 1000.0;
            float remaining_eta = predicted_eta - elapsed;
            
            int current_eta_bucket = ((int)remaining_eta / 10) * 10;
            if (current_eta_bucket != last_logged_eta && current_eta_bucket >= 0) {
                if (last_logged_eta == -1 || current_eta_bucket < last_logged_eta) {
                    printTimestamp();
                    Serial.print("[ETA UPDATE] Remaining: ");
                    Serial.print(current_eta_bucket);
                    Serial.println("s");
                    last_logged_eta = current_eta_bucket;
                }
            }
            
            if (remaining_eta <= getNotificationThreshold() && !intersection_notified) {
                activateIntersectionNotification();
            }
            
            if (remaining_eta <= getGateCloseThreshold() && !gates_closed) {
                closeGates();
            }
            
            if (intersection_notified && !gates_closed) {
                updateBuzzer();
            }
            
            if (gates_closed) {
                updateCountdown();
            }
        }
    }
    
    delay(50);
}

void checkSensors() {
    int curr_sensor0 = digitalRead(SENSOR_0_PIN);
    int curr_sensor1 = digitalRead(SENSOR_1_PIN);
    int curr_sensor2 = digitalRead(SENSOR_2_PIN);
    
    if (curr_sensor0 == HIGH && !sensor0_triggered) {
        sensor0_triggered = true;
        sensor0_time = millis();
        printTimestamp();
        Serial.println("[SENSOR 0] Train detected (furthest)");
    }
    
    if (curr_sensor1 == HIGH && !sensor1_triggered) {
        sensor1_triggered = true;
        sensor1_time = millis();
        printTimestamp();
        Serial.println("[SENSOR 1] Train detected (middle)");
        printTimestamp();
        Serial.print("[TIMING] Sensor 0->1: ");
        Serial.print((sensor1_time - sensor0_time) / 1000.0, 2);
        Serial.println("s");
    }
    
    if (curr_sensor2 == HIGH && !sensor2_triggered) {
        sensor2_triggered = true;
        sensor2_time = millis();
        printTimestamp();
        Serial.println("[SENSOR 2] Train detected (nearest)");
        printTimestamp();
        Serial.print("[TIMING] Sensor 1->2: ");
        Serial.print((sensor2_time - sensor1_time) / 1000.0, 2);
        Serial.println("s");
    }
}

void calculateETAWithML() {
    float time_0_to_1 = (sensor1_time - sensor0_time) / 1000.0;
    float time_1_to_2 = (sensor2_time - sensor1_time) / 1000.0;
    
    if (time_0_to_1 <= 0 || time_1_to_2 <= 0) {
        printTimestamp();
        Serial.println("[ERROR] Invalid sensor timing");
        resetSystem();
        return;
    }
    
    float distance_0_to_1 = SENSOR_0_POS - SENSOR_1_POS;
    float distance_1_to_2 = SENSOR_1_POS - SENSOR_2_POS;
    
    float speed_0_to_1 = distance_0_to_1 / time_0_to_1;
    float speed_1_to_2 = distance_1_to_2 / time_1_to_2;
    float acceleration = (speed_1_to_2 - speed_0_to_1) / time_1_to_2;
    float distance = SENSOR_2_POS;
    
    float features[6] = {
        time_0_to_1,
        time_1_to_2,
        speed_0_to_1,
        speed_1_to_2,
        acceleration,
        distance
    };
    
    float ml_eta = predictETA(features);
    float physics_eta = distance / speed_1_to_2;
    
    if (ml_eta > 0 && ml_eta < 200) {
        predicted_eta = ml_eta;
        printTimestamp();
        Serial.print("[ML] Predicted ETA: ");
    } else {
        predicted_eta = physics_eta;
        printTimestamp();
        Serial.print("[PHYSICS] Fallback ETA: ");
    }
    
    Serial.print(predicted_eta, 1);
    Serial.println(" seconds");
    
    eta_calculated_time = millis();
    last_logged_eta = -1;
    
    printTimestamp();
    Serial.print("[INFO] Train speed: ");
    Serial.print(speed_1_to_2 * 3.6, 1);
    Serial.println(" km/h");
    
    printTimestamp();
    Serial.print("[INFO] Acceleration: ");
    Serial.print(acceleration, 3);
    Serial.println(" m/s^2");
}

void setSystemState(bool crossing_red, bool intersection_red) {
    digitalWrite(CROSSING_GREEN_LED, crossing_red ? LOW : HIGH);
    digitalWrite(CROSSING_RED_LED, crossing_red ? HIGH : LOW);
    digitalWrite(INTER_GREEN_LED, intersection_red ? LOW : HIGH);
    digitalWrite(INTER_RED_LED, intersection_red ? HIGH : LOW);
}

void activateIntersectionNotification() {
    intersection_notified = true;
    digitalWrite(INTER_GREEN_LED, LOW);
    digitalWrite(INTER_RED_LED, HIGH);
    printTimestamp();
    Serial.println("[NOTIFICATION] Intersections alerted");
}

void closeGates() {
    gates_closed = true;
    gate_close_time = millis();
    
    gateServo.write(GATE_CLOSED_ANGLE);
    digitalWrite(CROSSING_GREEN_LED, LOW);
    digitalWrite(CROSSING_RED_LED, HIGH);
    
    printTimestamp();
    Serial.println("[GATE] CLOSED - Train approaching");
}

void openGates() {
    gates_closed = false;
    
    gateServo.write(GATE_OPEN_ANGLE);
    
    digitalWrite(CROSSING_GREEN_LED, HIGH);
    digitalWrite(CROSSING_RED_LED, LOW);
    digitalWrite(INTER_GREEN_LED, HIGH);
    digitalWrite(INTER_RED_LED, LOW);
    
    digitalWrite(BUZZER_PIN, LOW);
    buzzer_state = false;
    display.clear();
    
    printTimestamp();
    Serial.println("[GATE] OPENED - Safe to cross");
}

void updateCountdown() {
    if (gate_close_time == 0) return;
    
    unsigned long elapsed = (millis() - gate_close_time) / 1000;
    int remaining = (int)getGateCloseThreshold() - elapsed;
    
    if (remaining < 0) remaining = 0;
    
    int minutes = remaining / 60;
    int seconds = remaining % 60;
    display.showNumberDecEx(minutes * 100 + seconds, 0b01000000, true);
    
    if (remaining == 0 && gates_closed) {
        printTimestamp();
        Serial.println("[TRAIN] Passed crossing - waiting");
        delay(getTrainClearDelay());
        openGates();
        resetSystem();
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
    eta_calculated_time = 0;
    intersection_notified = false;
    gate_close_time = 0;
    last_logged_eta = -1;
    
    printTimestamp();
    Serial.println("[SYSTEM] Reset - Ready for next train");
}