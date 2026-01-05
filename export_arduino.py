"""
Export models and configuration to Arduino C headers
Replaces: hardware/exporters/model.py, hardware/exporters/threshold.py, hardware/exporters/config.py
Usage: python export_arduino.py
"""

import pickle
import yaml
from pathlib import Path
from utils.logger import Logger


class ArduinoExporter:
    def __init__(self, config_path='config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.hardware_dir = Path('arduino')
        self.hardware_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_dir = Path('outputs')
    
    def export_thresholds(self):
        """Export sensor positions and timing thresholds"""
        Logger.section("Exporting thresholds")
        
        sensors = self.config['sensors']
        demo = self.config['demo']
        
        header = f"""#ifndef THRESHOLDS_H
#define THRESHOLDS_H

/*
 * Physical Demo Configuration
 * Scale: Tabletop model
 * Sensors: 3 IR sensors, 10cm apart
 */

#define DEMO_MODE true

// Sensor positions (meters from crossing)
// Physical layout: S0 --10cm-- S1 --10cm-- S2 --20cm-- Crossing
#define SENSOR_0_POS {demo['sensor_spacing'] * 2}f    // 20cm from crossing
#define SENSOR_1_POS {demo['sensor_spacing']}f        // 10cm from crossing
#define SENSOR_2_POS {demo['last_sensor_to_crossing']}f  // At crossing

// Demo timing (seconds)
#define GATE_CLOSE_THRESHOLD {demo['gate_close_time']}f
#define NOTIFICATION_THRESHOLD {demo['notification_time']}f
#define GATE_OPEN_DELAY {demo['gate_open_delay']}f

// Physical measurements
#define SENSOR_SPACING {demo['sensor_spacing']}f
#define LAST_SENSOR_TO_CROSSING {demo['last_sensor_to_crossing']}f
#define CROSSING_TO_INTERSECTION {demo['crossing_to_intersection']}f

// Expected movement speed
#define EXPECTED_HAND_SPEED {demo['expected_hand_speed']}f

#endif
"""
        
        output_path = self.hardware_dir / 'thresholds.h'
        output_path.write_text(header)
        
        Logger.log(f"Saved: {output_path}")
        Logger.log(f"  Sensor 0: {demo['sensor_spacing'] * 2}m")
        Logger.log(f"  Sensor 1: {demo['sensor_spacing']}m")
        Logger.log(f"  Sensor 2: {demo['last_sensor_to_crossing']}m")
    
    def export_model(self):
        """Export ML model functions"""
        Logger.section("Exporting ML model")
        
        eta_path = self.output_dir / 'eta_model.pkl'
        etd_path = self.output_dir / 'etd_model.pkl'
        
        if eta_path.exists() and etd_path.exists():
            Logger.log("Found trained Random Forest models")
            Logger.log("NOTE: Full models too large for Arduino Uno (need Mega/ESP32)")
            Logger.log("Generating physics-based fallback for Arduino compatibility")
        else:
            Logger.log("No trained models found")
            Logger.log("Generating physics-based predictions")
        
        header = """#ifndef MODEL_H
#define MODEL_H

/*
 * ML Model Functions for Railway Crossing Control
 * 
 * Physics-based predictions (Arduino Uno compatible)
 * Full Random Forest models require Arduino Mega or ESP32
 */

// Feature indices for ETA (6 features)
#define FEAT_TIME_01 0
#define FEAT_TIME_12 1
#define FEAT_SPEED_01 2
#define FEAT_SPEED_12 3
#define FEAT_ACCEL 4
#define FEAT_DISTANCE 5

// Feature indices for ETD (7 features)
#define FEAT_ETD_TIME_01 0
#define FEAT_ETD_TIME_12 1
#define FEAT_ETD_SPEED_01 2
#define FEAT_ETD_SPEED_12 3
#define FEAT_ETD_ACCEL 4
#define FEAT_ETD_DISTANCE 5
#define FEAT_ETD_TRAIN_LENGTH 6

/**
 * Predict ETA (Estimated Time of Arrival)
 * Time until train front reaches crossing
 * 
 * @param features[6]: [time_01, time_12, speed_01, speed_12, accel, distance]
 * @return ETA in seconds, or -1 if invalid
 */
float predictETA(float features[6]) {
    float speed = features[FEAT_SPEED_12];
    float accel = features[FEAT_ACCEL];
    float distance = features[FEAT_DISTANCE];
    
    if (speed <= 0 || distance <= 0) return -1;
    
    if (accel > -0.1 && accel < 0.1) {
        return distance / speed;
    }
    
    float discriminant = speed * speed + 2.0 * accel * distance;
    
    if (discriminant < 0) {
        return distance / speed;
    }
    
    float t = (-speed + sqrt(discriminant)) / accel;
    
    if (t > 0 && t < 1000) {
        return t;
    }
    
    return distance / speed;
}

/**
 * Predict ETD (Estimated Time of Departure)
 * Time until train rear clears crossing
 * 
 * @param features[7]: [time_01, time_12, speed_01, speed_12, accel, distance, train_length]
 * @return ETD in seconds, or -1 if invalid
 */
float predictETD(float features[7]) {
    float speed = features[FEAT_ETD_SPEED_12];
    float accel = features[FEAT_ETD_ACCEL];
    float distance = features[FEAT_ETD_DISTANCE];
    float train_length = features[FEAT_ETD_TRAIN_LENGTH];
    
    if (speed <= 0 || distance <= 0 || train_length <= 0) return -1;
    
    float total_distance = distance + train_length;
    
    if (accel > -0.1 && accel < 0.1) {
        return total_distance / speed;
    }
    
    float discriminant = speed * speed + 2.0 * accel * total_distance;
    
    if (discriminant < 0) {
        return total_distance / speed;
    }
    
    float t = (-speed + sqrt(discriminant)) / accel;
    
    if (t > 0 && t < 1000) {
        return t;
    }
    
    return total_distance / speed;
}

/**
 * Simplified ETD estimate from ETA
 * 
 * @param eta: Estimated time of arrival (from predictETA)
 * @param last_speed: Speed at last sensor
 * @return ETD in seconds, or -1 if invalid
 */
float estimateETD(float eta, float last_speed) {
    const float AVG_TRAIN_LENGTH = 0.30f;
    
    if (eta <= 0 || last_speed <= 0) return -1;
    
    float crossing_time = AVG_TRAIN_LENGTH / last_speed;
    return eta + crossing_time;
}

#endif
"""
        
        output_path = self.hardware_dir / 'model.h'
        output_path.write_text(header)
        
        Logger.log(f"Saved: {output_path}")
        Logger.log("  Functions: predictETA(), predictETD(), estimateETD()")
    
    def export_config(self):
        """Export configuration helpers"""
        Logger.section("Exporting configuration")
        
        header = """#ifndef CONFIG_H
#define CONFIG_H

#include "thresholds.h"

/*
 * Configuration Helper Functions
 */

// Timing thresholds
inline float getGateCloseThreshold() {
    return GATE_CLOSE_THRESHOLD;
}

inline float getNotificationThreshold() {
    return NOTIFICATION_THRESHOLD;
}

inline float getGateOpenDelay() {
    return GATE_OPEN_DELAY;
}

// Sensor positions
inline float getSensor0Position() {
    return SENSOR_0_POS;
}

inline float getSensor1Position() {
    return SENSOR_1_POS;
}

inline float getSensor2Position() {
    return SENSOR_2_POS;
}

// Display and buzzer settings
inline unsigned long getBuzzerInterval() {
    return 500;  // 500ms beep interval
}

inline unsigned long getDisplayUpdateInterval() {
    return 100;  // Update 10 times per second
}

// Physical parameters
inline float getDefaultTrainLength() {
    return 0.30f;  // 30cm for demo
}

// Servo angles
#define GATE_OPEN_ANGLE 90
#define GATE_CLOSED_ANGLE 0

// Display brightness (0-15)
#define DISPLAY_BRIGHTNESS 0x0f

#endif
"""
        
        output_path = self.hardware_dir / 'config.h'
        output_path.write_text(header)
        
        Logger.log(f"Saved: {output_path}")
    
    def export_all(self):
        """Export everything to Arduino"""
        Logger.section("Exporting to Arduino")
        
        self.export_thresholds()
        self.export_model()
        self.export_config()
        
        Logger.log("\nArduino export complete!")
        Logger.log("\nGenerated files:")
        Logger.log(f"  {self.hardware_dir / 'model.h'} - ML prediction functions")
        Logger.log(f"  {self.hardware_dir / 'thresholds.h'} - Sensor positions & timing")
        Logger.log(f"  {self.hardware_dir / 'config.h'} - Helper functions")
        Logger.log("\nReady to upload sketch.ino to Arduino")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export to Arduino')
    parser.add_argument('--config', default='config.yaml', help='Config file path')
    args = parser.parse_args()
    
    exporter = ArduinoExporter(args.config)
    exporter.export_all()