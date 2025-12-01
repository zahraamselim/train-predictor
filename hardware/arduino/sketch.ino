/*
 * Intelligent Level Crossing Control System
 * Uses ML-based ETA prediction for optimal gate timing
 * Features: Engine-off notification, intersection alerts, countdown display
 */

#include <Servo.h>
#include <TM1637Display.h>
#include "eta_model.h"
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
    Serial.println("Level Crossing Control System");
    printTimestamp();
    Serial.println("ML-based ETA prediction active");
}

void loop() {
    checkSensors();
    
    if (sensor0_triggered && sensor1_triggered && sensor2_triggered) {
        if (predicted_eta == 0) {
            calculateETA();
        }
        
        if (predicted_eta > 0) {
            float elapsed = (millis() - eta_calculated_time) / 1000.0;
            float remaining_eta = predicted_eta - elapsed;
            
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
                updateCountdown(remaining_eta);
            }
        }
    }
    
    delay(50);
}

void checkSensors() {
    if (digitalRead(SENSOR_0_PIN) == HIGH && !sensor0_triggered) {
        sensor0_triggered = true;
        sensor0_time = millis();
        printTimestamp();
        Serial.println("Train detected at sensor 0");
    }
    
    if (digitalRead(SENSOR_1_PIN) == HIGH && !sensor1_triggered) {
        sensor1_triggered = true;
        sensor1_time = millis();
        printTimestamp();
        Serial.println("Train detected at sensor 1");
    }
    
    if (digitalRead(SENSOR_2_PIN) == HIGH && !sensor2_triggered) {
        sensor2_triggered = true;
        sensor2_time = millis();
        printTimestamp();
        Serial.println("Train detected at sensor 2");
    }
}

void calculateETA() {
    float time_0_to_1 = (sensor1_time - sensor0_time) / 1000.0;
    float time_1_to_2 = (sensor2_time - sensor1_time) / 1000.0;
    
    if (time_0_to_1 <= 0 || time_1_to_2 <= 0) {
        printTimestamp();
        Serial.println("ERROR: Invalid timing");
        resetSystem();
        return;
    }
    
    float distance_0_to_1 = SENSOR_0_POS - SENSOR_1_POS;
    float distance_1_to_2 = SENSOR_1_POS - SENSOR_2_POS;
    
    float speed_0_to_1 = distance_0_to_1 / time_0_to_1;
    float speed_1_to_2 = distance_1_to_2 / time_1_to_2;
    float acceleration = (speed_1_to_2 - speed_0_to_1) / time_1_to_2;
    float distance = SENSOR_2_POS;
    
    float avg_speed = (speed_0_to_1 + speed_1_to_2) / 2.0;
    float speed_variance = (pow(speed_0_to_1 - avg_speed, 2) + pow(speed_1_to_2 - avg_speed, 2)) / 2.0;
    float decel_rate = acceleration < 0 ? -acceleration : 0;
    
    float features[9] = {
        time_0_to_1,
        time_1_to_2,
        speed_0_to_1,
        speed_1_to_2,
        acceleration,
        distance,
        avg_speed,
        speed_variance,
        decel_rate
    };
    
    float ml_eta = predictETA(features);
    float physics_eta = distance / speed_1_to_2;
    
    if (ml_eta > 0 && ml_eta < 200) {
        predicted_eta = ml_eta;
        printTimestamp();
        Serial.print("ML ETA: ");
    } else {
        predicted_eta = physics_eta;
        printTimestamp();
        Serial.print("Physics ETA: ");
    }
    
    Serial.print(predicted_eta, 1);
    Serial.println("s");
    
    eta_calculated_time = millis();
    
    printTimestamp();
    Serial.print("Train speed: ");
    Serial.print(speed_1_to_2 * 3.6, 1);
    Serial.println(" km/h");
}

void activateIntersectionNotification() {
    intersection_notified = true;
    digitalWrite(INTER_GREEN_LED, LOW);
    digitalWrite(INTER_RED_LED, HIGH);
    printTimestamp();
    Serial.println("Intersections notified");
    
    float wait_time = predicted_eta - (millis() - eta_calculated_time) / 1000.0 + getGateOpenThreshold();
    if (wait_time >= getEngineOffThreshold()) {
        printTimestamp();
        Serial.print("Recommended: Engine off (wait ");
        Serial.print(wait_time, 0);
        Serial.println("s)");
    }
}

void closeGates() {
    gates_closed = true;
    gate_close_time = millis();
    
    gateServo.write(GATE_CLOSED_ANGLE);
    digitalWrite(CROSSING_GREEN_LED, LOW);
    digitalWrite(CROSSING_RED_LED, HIGH);
    
    printTimestamp();
    Serial.println("Gates CLOSED");
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
    Serial.println("Gates OPEN");
}

void updateCountdown(float remaining_eta) {
    int remaining = (int)(remaining_eta + getGateOpenThreshold());
    
    if (remaining < 0) remaining = 0;
    
    int minutes = remaining / 60;
    int seconds = remaining % 60;
    display.showNumberDecEx(minutes * 100 + seconds, 0b01000000, true);
    
    if (remaining == 0 && gates_closed) {
        printTimestamp();
        Serial.println("Train passed");
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
    
    printTimestamp();
    Serial.println("System reset");
}