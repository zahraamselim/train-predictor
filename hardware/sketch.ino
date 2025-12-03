#include <Servo.h>
#include <TM1637Display.h>
#include "train_models.h"
#include "scale_config.h"
#include "thresholds_config.h"

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

#define GATE_OPEN_ANGLE 90
#define GATE_CLOSED_ANGLE 0
#define BUZZER_INTERVAL 500

#define SENSOR_0_POS 20.0f
#define SENSOR_1_POS 15.0f
#define SENSOR_2_POS 10.0f
#define TRAIN_LENGTH 10.0f

#define CLOSURE_THRESHOLD 2.0f
#define OPENING_THRESHOLD 1.0f
#define NOTIFICATION_THRESHOLD 3.0f

Servo gateServo;
TM1637Display display(TM1637_CLK, TM1637_DIO);

unsigned long sensor_times[3] = {0, 0, 0};
bool sensor_triggered[3] = {false, false, false};
float predicted_eta = 0;
float predicted_etd = 0;
unsigned long prediction_time = 0;

enum SystemState {
    IDLE,
    TRAIN_DETECTED,
    INTERSECTION_NOTIFIED,
    GATES_CLOSING,
    GATES_CLOSED,
    GATES_OPENING
};

SystemState current_state = IDLE;
unsigned long last_buzzer = 0;
bool buzzer_state = false;

void printTime() {
    unsigned long s = millis() / 1000;
    unsigned long m = s / 60;
    s = s % 60;
    Serial.print("[");
    if (m < 10) Serial.print("0");
    Serial.print(m);
    Serial.print(":");
    if (s < 10) Serial.print("0");
    Serial.print(s);
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
    digitalWrite(INTER_GREEN_LED, HIGH);
    digitalWrite(CROSSING_RED_LED, LOW);
    digitalWrite(INTER_RED_LED, LOW);
    digitalWrite(BUZZER_PIN, LOW);
    
    printTime();
    Serial.println("Demonstration Level Crossing System");
    printTime();
    Serial.println("Scale: 5cm between sensors, 20cm to crossing");
    printTime();
    Serial.println("Ready - waiting for train detection");
}

void loop() {
    checkSensors();
    
    if (current_state == TRAIN_DETECTED) {
        if (sensor_triggered[0] && sensor_triggered[1] && sensor_triggered[2]) {
            calculatePredictions();
            current_state = IDLE;
            
            float time_to_closure = predicted_eta - CLOSURE_THRESHOLD;
            if (time_to_closure > 0) {
                updateCountdown(time_to_closure);
            }
        }
    }
    
    if (predicted_eta > 0) {
        float elapsed = (millis() - prediction_time) / 1000.0;
        float remaining_eta = predicted_eta - elapsed;
        float remaining_etd = predicted_etd - elapsed;
        
        if (current_state == IDLE && remaining_eta <= NOTIFICATION_THRESHOLD) {
            notifyIntersections(remaining_eta);
            current_state = INTERSECTION_NOTIFIED;
        }
        
        if (current_state == INTERSECTION_NOTIFIED && remaining_eta <= CLOSURE_THRESHOLD) {
            closeGates();
            current_state = GATES_CLOSED;
        }
        
        if (current_state == INTERSECTION_NOTIFIED) {
            updateBuzzer();
            float time_to_closure = remaining_eta - CLOSURE_THRESHOLD;
            if (time_to_closure > 0) {
                updateCountdown(time_to_closure);
            } else {
                updateCountdown(0);
            }
        }
        
        if (current_state == GATES_CLOSED) {
            updateBuzzer();
            float time_to_open = remaining_etd + OPENING_THRESHOLD;
            if (time_to_open > 0) {
                updateCountdown(time_to_open);
            } else {
                updateCountdown(0);
            }
            
            if (remaining_etd + OPENING_THRESHOLD <= 0) {
                openGates();
                resetSystem();
            }
        }
    }
    
    delay(50);
}

void checkSensors() {
    for (int i = 0; i < 3; i++) {
        if (digitalRead(SENSOR_0_PIN + i) == HIGH && !sensor_triggered[i]) {
            sensor_triggered[i] = true;
            sensor_times[i] = millis();
            
            if (current_state == IDLE) {
                current_state = TRAIN_DETECTED;
            }
            
            printTime();
            Serial.print("Sensor ");
            Serial.print(i);
            Serial.print(" triggered");
            
            if (i == 0) {
                Serial.print(" (20cm from crossing)");
            } else if (i == 1) {
                Serial.print(" (15cm from crossing)");
            } else if (i == 2) {
                Serial.print(" (10cm from crossing)");
            }
            Serial.println();
        }
    }
}

void calculatePredictions() {
    float dt01 = (sensor_times[1] - sensor_times[0]) / 1000.0;
    float dt12 = (sensor_times[2] - sensor_times[1]) / 1000.0;
    
    if (dt01 <= 0 || dt12 <= 0) {
        printTime();
        Serial.println("ERROR: Invalid timing intervals");
        resetSystem();
        return;
    }
    
    float dist01 = SENSOR_0_POS - SENSOR_1_POS;
    float dist12 = SENSOR_1_POS - SENSOR_2_POS;
    float s01 = dist01 / dt01;
    float s12 = dist12 / dt12;
    float accel = (s12 - s01) / dt12;
    float avg_s = (s01 + s12) / 2.0;
    float var_s = ((s01 - avg_s) * (s01 - avg_s) + (s12 - avg_s) * (s12 - avg_s)) / 2.0;
    float speed_trend = (s12 - s01) / dt12;
    float time_var = ((dt01 - (dt01 + dt12) / 2) * (dt01 - (dt01 + dt12) / 2) + 
                      (dt12 - (dt01 + dt12) / 2) * (dt12 - (dt01 + dt12) / 2)) / 2.0;
    
    float length_speed_ratio = TRAIN_LENGTH / s12;
    float distance_length_ratio = SENSOR_2_POS / TRAIN_LENGTH;
    
    float features[14];
    features[0] = SENSOR_2_POS;
    features[1] = TRAIN_LENGTH;
    features[2] = s12;
    features[3] = accel;
    features[4] = speed_trend;
    features[5] = var_s;
    features[6] = time_var;
    features[7] = avg_s;
    features[8] = length_speed_ratio;
    features[9] = distance_length_ratio;
    features[10] = dt01;
    features[11] = dt12;
    features[12] = s01;
    features[13] = s12;
    
    predicted_eta = predictETA(features);
    predicted_etd = predictETD(features);
    prediction_time = millis();
    
    printTime();
    Serial.println("Train parameters calculated:");
    printTime();
    Serial.print("  Speed: ");
    Serial.print(s12, 2);
    Serial.println(" cm/s");
    printTime();
    Serial.print("  Acceleration: ");
    Serial.print(accel, 2);
    Serial.println(" cm/s²");
    printTime();
    Serial.print("  ETA: ");
    Serial.print(predicted_eta, 1);
    Serial.println("s");
    printTime();
    Serial.print("  ETD: ");
    Serial.print(predicted_etd, 1);
    Serial.println("s");
}

void notifyIntersections(float remaining) {
    digitalWrite(INTER_GREEN_LED, LOW);
    digitalWrite(INTER_RED_LED, HIGH);
    
    printTime();
    Serial.println("INTERSECTION NOTIFIED - Buzzer activated");
    printTime();
    Serial.print("  Time to gate closure: ");
    Serial.print(remaining - CLOSURE_THRESHOLD, 1);
    Serial.println("s");
}

void closeGates() {
    gateServo.write(GATE_CLOSED_ANGLE);
    digitalWrite(CROSSING_GREEN_LED, LOW);
    digitalWrite(CROSSING_RED_LED, HIGH);
    
    printTime();
    Serial.println("GATES CLOSED");
    printTime();
    Serial.print("  Wait time: ");
    Serial.print(predicted_etd + OPENING_THRESHOLD, 1);
    Serial.println("s");
}

void openGates() {
    gateServo.write(GATE_OPEN_ANGLE);
    digitalWrite(CROSSING_GREEN_LED, HIGH);
    digitalWrite(INTER_GREEN_LED, HIGH);
    digitalWrite(CROSSING_RED_LED, LOW);
    digitalWrite(INTER_RED_LED, LOW);
    digitalWrite(BUZZER_PIN, LOW);
    display.clear();
    
    printTime();
    Serial.println("GATES OPEN - System ready");
}

void updateCountdown(float remaining) {
    int r = (int)remaining;
    if (r < 0) r = 0;
    
    int m = r / 60;
    int s = r % 60;
    display.showNumberDecEx(m * 100 + s, 0b01000000, true);
}

void updateBuzzer() {
    unsigned long now = millis();
    if (now - last_buzzer >= BUZZER_INTERVAL) {
        buzzer_state = !buzzer_state;
        digitalWrite(BUZZER_PIN, buzzer_state ? HIGH : LOW);
        last_buzzer = now;
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
    current_state = IDLE;
    buzzer_state = false;
    digitalWrite(BUZZER_PIN, LOW);
    
    printTime();
    Serial.println("System reset - Ready for next train");
    Serial.println();
}