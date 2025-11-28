#include <Servo.h>

// SENSORS
const int IR1_PIN = 3;
const int IR2_PIN = 4;
const int IR3_PIN = 5;

// LEDS
const int RED_PIN = 7;
const int GREEN_PIN = 8; 

// BUZZER
const int BUZZER_PIN = 9; 

// SENSROS VARIBALES
int prev_IR1 = LOW;
int prev_IR2 = LOW;
int prev_IR3 = LOW;

// TIMER VARIABLES
unsigned long startTime = 0;
bool timerRunning = false;
unsigned long IR1_time = 0;
unsigned long IR2_time = 0;
unsigned long IR3_time = 0;

// ROAD VARIABLES
bool roadClosed = false;

void setup() {
  Serial.begin(9600);
  pinMode(IR1_PIN, INPUT);
  pinMode(IR2_PIN, INPUT);
  pinMode(IR3_PIN, INPUT);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT); 

  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  int IR1 = digitalRead(IR1_PIN);
  int IR2 = digitalRead(IR2_PIN);
  int IR3 = digitalRead(IR3_PIN);
  
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 's' || command == 'S') {
      startTime = millis();

      timerRunning = true;
      roadClosed = false;

      IR1_time = 0;
      IR2_time = 0;
      IR3_time = 0;

      prev_IR1 = LOW;
      prev_IR2 = LOW;
      prev_IR3 = LOW;
      
      Serial.println("Timer started!");
    }
    else if (command == 'r' || command == 'R') {
      startTime = 0;

      timerRunning = true;
      roadClosed = false;
      
      IR1_time = 0;
      IR2_time = 0;
      IR3_time = 0;
      
      Serial.println("Timer reset!");
    }
  }
  
  if (timerRunning) {
    unsigned long currentTime = millis() - startTime;

    if (IR1 == HIGH && prev_IR1 == LOW) {
      IR1_time = currentTime;
      Serial.print("IR1 triggered at: ");
      Serial.print(IR1_time);
      Serial.println(" ms");
      roadClosed = false;
    }
    if (IR2 == HIGH && prev_IR2 == LOW) {
      IR2_time = currentTime;
      Serial.print("IR2 triggered at: ");
      Serial.print(IR2_time);
      Serial.println(" ms");
    }
    if (IR3 == HIGH && prev_IR3 == LOW) {
      IR3_time = currentTime;
      Serial.print("IR3 triggered at: ");
      Serial.print(IR3_time);
      Serial.println(" ms");
      roadClosed = true;
    }

    if (roadClosed) {
      digitalWrite(GREEN_PIN, LOW);
      digitalWrite(RED_PIN, HIGH);
      tone(BUZZER_PIN, 1000);
      delay(50); 
      noTone(BUZZER_PIN);
      // delay(900); 
    }
    else {
      digitalWrite(GREEN_PIN, HIGH);
      digitalWrite(RED_PIN, LOW);
    }

    prev_IR1 = IR1;
    prev_IR2 = IR2;
    prev_IR3 = IR3;
  }
  
  delay(50);
}