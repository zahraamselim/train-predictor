/*
 * Level Crossing Notification System - Arduino Implementation
 * 
 * Hardware:
 * - 3x IR Obstacle Avoidance Sensors (railway sensors)
 * - 1x Servo Motor (crossing gate)
 * - 1x TM1637 7-segment Display (countdown timer)
 * - 4x LEDs (2 red, 2 green - crossing and intersection)
 * - 1x Buzzer (warning sound)
 */

#include <Servo.h>
#include <TM1637Display.h>

// Pin definitions
#define SENSOR_0_PIN 2    // Furthest sensor
#define SENSOR_1_PIN 3    // Middle sensor
#define SENSOR_2_PIN 4    // Nearest sensor

#define SERVO_PIN 5       // Gate servo

#define CROSSING_RED_LED 6
#define CROSSING_GREEN_LED 7

#define INTERSECTION_RED_LED 8
#define INTERSECTION_GREEN_LED 9

#define BUZZER_PIN 10

#define TM1637_CLK 11
#define TM1637_DIO 12

// Sensor positions (meters from crossing)
const float SENSOR_0_POS = 2700.0;
const float SENSOR_1_POS = 1620.0;
const float SENSOR_2_POS = 810.0;

// Objects
Servo gateServo;
TM1637Display display(TM1637_CLK, TM1637_DIO);

// State variables
unsigned long sensor0_time = 0;
unsigned long sensor1_time = 0;
unsigned long sensor2_time = 0;

bool sensor0_triggered = false;
bool sensor1_triggered = false;
bool sensor2_triggered = false;

float calculated_eta = 0;
bool gates_closed = false;

unsigned long countdown_start = 0;
int countdown_seconds = 0;

// Gate control
const int GATE_OPEN_ANGLE = 90;
const int GATE_CLOSED_ANGLE = 0;

void setup() {
  Serial.begin(9600);
  
  // Initialize sensors
  pinMode(SENSOR_0_PIN, INPUT);
  pinMode(SENSOR_1_PIN, INPUT);
  pinMode(SENSOR_2_PIN, INPUT);
  
  // Initialize LEDs
  pinMode(CROSSING_RED_LED, OUTPUT);
  pinMode(CROSSING_GREEN_LED, OUTPUT);
  pinMode(INTERSECTION_RED_LED, OUTPUT);
  pinMode(INTERSECTION_GREEN_LED, OUTPUT);
  
  // Initialize buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize servo
  gateServo.attach(SERVO_PIN);
  gateServo.write(GATE_OPEN_ANGLE);
  
  // Initialize display
  display.setBrightness(0x0f);
  display.clear();
  
  // Initial state: all clear
  digitalWrite(CROSSING_GREEN_LED, HIGH);
  digitalWrite(CROSSING_RED_LED, LOW);
  digitalWrite(INTERSECTION_GREEN_LED, HIGH);
  digitalWrite(INTERSECTION_RED_LED, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  
  Serial.println("Level Crossing System Ready");
}

void loop() {
  checkSensors();
  
  if (sensor0_triggered && sensor1_triggered && sensor2_triggered && !gates_closed) {
    calculateETA();
    
    if (calculated_eta < 15.0) {
      closeGates();
    }
  }
  
  if (gates_closed) {
    updateCountdown();
  }
  
  delay(100);
}

void checkSensors() {
  // Sensor 0 (furthest)
  if (!sensor0_triggered && digitalRead(SENSOR_0_PIN) == LOW) {
    sensor0_triggered = true;
    sensor0_time = millis();
    Serial.println("Sensor 0 triggered");
  }
  
  // Sensor 1 (middle)
  if (!sensor1_triggered && digitalRead(SENSOR_1_PIN) == LOW) {
    sensor1_triggered = true;
    sensor1_time = millis();
    Serial.println("Sensor 1 triggered");
  }
  
  // Sensor 2 (nearest)
  if (!sensor2_triggered && digitalRead(SENSOR_2_PIN) == LOW) {
    sensor2_triggered = true;
    sensor2_time = millis();
    Serial.println("Sensor 2 triggered");
  }
}

void calculateETA() {
  // Calculate speed between sensors 1 and 2
  float time_1_to_2 = (sensor2_time - sensor1_time) / 1000.0; // seconds
  float distance_1_to_2 = SENSOR_1_POS - SENSOR_2_POS; // meters
  
  if (time_1_to_2 > 0) {
    float speed = distance_1_to_2 / time_1_to_2; // m/s
    
    // Calculate ETA from sensor 2 to crossing
    calculated_eta = SENSOR_2_POS / speed; // seconds
    
    Serial.print("Speed: ");
    Serial.print(speed * 3.6); // km/h
    Serial.println(" km/h");
    
    Serial.print("ETA: ");
    Serial.print(calculated_eta);
    Serial.println(" seconds");
  }
}

void closeGates() {
  gates_closed = true;
  
  // Close gate
  gateServo.write(GATE_CLOSED_ANGLE);
  
  // Turn on red lights
  digitalWrite(CROSSING_RED_LED, HIGH);
  digitalWrite(CROSSING_GREEN_LED, LOW);
  digitalWrite(INTERSECTION_RED_LED, HIGH);
  digitalWrite(INTERSECTION_GREEN_LED, LOW);
  
  // Start countdown
  countdown_seconds = (int)calculated_eta;
  countdown_start = millis();
  
  // Activate buzzer (blinking pattern in separate function)
  activateBuzzer();
  
  Serial.println("Gates closed");
}

void openGates() {
  gates_closed = false;
  
  // Open gate
  gateServo.write(GATE_OPEN_ANGLE);
  
  // Turn on green lights
  digitalWrite(CROSSING_RED_LED, LOW);
  digitalWrite(CROSSING_GREEN_LED, HIGH);
  digitalWrite(INTERSECTION_RED_LED, LOW);
  digitalWrite(INTERSECTION_GREEN_LED, HIGH);
  
  // Stop buzzer
  digitalWrite(BUZZER_PIN, LOW);
  
  // Clear display
  display.clear();
  
  // Reset sensors for next train
  sensor0_triggered = false;
  sensor1_triggered = false;
  sensor2_triggered = false;
  
  Serial.println("Gates opened");
}

void updateCountdown() {
  unsigned long elapsed = (millis() - countdown_start) / 1000;
  int remaining = countdown_seconds - elapsed;
  
  if (remaining < 0) {
    remaining = 0;
  }
  
  // Display MM:SS format
  int minutes = remaining / 60;
  int seconds = remaining % 60;
  
  display.showNumberDecEx(minutes * 100 + seconds, 0b01000000, true);
  
  // Check if train has passed (simplified: after countdown)
  if (remaining == 0 && gates_closed) {
    // Wait a bit for train to clear
    delay(5000);
    openGates();
  }
}

void activateBuzzer() {
  // Simple buzzer pattern - can be enhanced
  static unsigned long last_beep = 0;
  static bool beep_state = false;
  
  unsigned long now = millis();
  
  if (gates_closed) {
    if (now - last_beep > 500) {
      beep_state = !beep_state;
      digitalWrite(BUZZER_PIN, beep_state ? HIGH : LOW);
      last_beep = now;
    }
  } else {
    digitalWrite(BUZZER_PIN, LOW);
  }
}