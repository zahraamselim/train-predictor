#ifndef ARDUINO_SCALE_CONFIG_H
#define ARDUINO_SCALE_CONFIG_H

// Demonstration scale configuration (centimeters)
#define SENSOR_0_POS 20.0f
#define SENSOR_1_POS 15.0f
#define SENSOR_2_POS 10.0f
#define CROSSING_POS 0.0f

// Train parameters
#define TRAIN_LENGTH 10.0f
#define TYPICAL_SPEED 5.0f

// Control thresholds (seconds)
#define CLOSURE_THRESHOLD 2.0f
#define OPENING_THRESHOLD 1.0f
#define NOTIFICATION_THRESHOLD 3.0f
#define ENGINE_OFF_THRESHOLD 3.0f

// Timing parameters
#define BUZZER_INTERVAL 500
#define GATE_OPEN_ANGLE 90
#define GATE_CLOSED_ANGLE 0

#endif
