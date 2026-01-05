"""
Export models and configuration to Arduino C headers
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
        
        demo = self.config['demo']
        
        # Calculate sensor positions from crossing
        sensor_2_pos = demo['last_sensor_to_crossing']
        sensor_1_pos = sensor_2_pos + demo['sensor_spacing']
        sensor_0_pos = sensor_1_pos + demo['sensor_spacing']
        
        header = f"""#ifndef THRESHOLDS_H
#define THRESHOLDS_H

#define DEMO_MODE true

#define SENSOR_0_POS {sensor_0_pos}f
#define SENSOR_1_POS {sensor_1_pos}f
#define SENSOR_2_POS {sensor_2_pos}f

#define GATE_CLOSE_THRESHOLD {demo['gate_close_time']}f
#define NOTIFICATION_THRESHOLD {demo['notification_time']}f
#define GATE_OPEN_DELAY {demo['gate_open_delay']}f

#define SENSOR_SPACING {demo['sensor_spacing']}f
#define LAST_SENSOR_TO_CROSSING {demo['last_sensor_to_crossing']}f
#define CROSSING_TO_INTERSECTION {demo['crossing_to_intersection']}f

#define EXPECTED_HAND_SPEED {demo['expected_hand_speed']}f

#endif
"""
        
        output_path = self.hardware_dir / 'thresholds.h'
        output_path.write_text(header)
        
        Logger.log(f"Saved: {output_path}")
        Logger.log(f"  Sensor 0: {sensor_0_pos}m ({sensor_0_pos*100:.0f}cm from crossing)")
        Logger.log(f"  Sensor 1: {sensor_1_pos}m ({sensor_1_pos*100:.0f}cm from crossing)")
        Logger.log(f"  Sensor 2: {sensor_2_pos}m ({sensor_2_pos*100:.0f}cm from crossing)")
        Logger.log(f"  Gate close: {demo['gate_close_time']}s before arrival")
        Logger.log(f"  Notification: {demo['notification_time']}s before arrival")
        Logger.log(f"  Train length: {demo['train_length']}m ({demo['train_length']*100:.0f}cm)")
        Logger.log(f"  Expected speed: {demo['expected_hand_speed']}m/s ({demo['expected_hand_speed']*100:.0f}cm/s)")
    
    def export_model(self):
        """Export ML model functions"""
        Logger.section("Exporting ML model")
        
        eta_path = self.output_dir / 'eta_model.pkl'
        etd_path = self.output_dir / 'etd_model.pkl'
        
        if eta_path.exists() and etd_path.exists():
            Logger.log("Found trained Random Forest models")
            Logger.log("NOTE: Full models too large for Arduino Uno")
            Logger.log("Generating physics-based fallback")
        else:
            Logger.log("No trained models found")
            Logger.log("Generating physics-based predictions")
        
        header = """#ifndef MODEL_H
#define MODEL_H

#define FEAT_TIME_01 0
#define FEAT_TIME_12 1
#define FEAT_SPEED_01 2
#define FEAT_SPEED_12 3
#define FEAT_ACCEL 4
#define FEAT_DISTANCE 5

#define FEAT_ETD_TIME_01 0
#define FEAT_ETD_TIME_12 1
#define FEAT_ETD_SPEED_01 2
#define FEAT_ETD_SPEED_12 3
#define FEAT_ETD_ACCEL 4
#define FEAT_ETD_DISTANCE 5
#define FEAT_ETD_TRAIN_LENGTH 6

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

float estimateETD(float eta, float last_speed) {
    const float AVG_TRAIN_LENGTH = 0.15f;
    
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

inline float getGateCloseThreshold() {
    return GATE_CLOSE_THRESHOLD;
}

inline float getNotificationThreshold() {
    return NOTIFICATION_THRESHOLD;
}

inline float getGateOpenDelay() {
    return GATE_OPEN_DELAY;
}

inline float getSensor0Position() {
    return SENSOR_0_POS;
}

inline float getSensor1Position() {
    return SENSOR_1_POS;
}

inline float getSensor2Position() {
    return SENSOR_2_POS;
}

inline unsigned long getBuzzerInterval() {
    return 500;
}

inline unsigned long getDisplayUpdateInterval() {
    return 100;
}

inline float getDefaultTrainLength() {
    return 0.15f;
}

#define GATE_OPEN_ANGLE 90
#define GATE_CLOSED_ANGLE 0
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
        Logger.log(f"  {self.hardware_dir / 'model.h'}")
        Logger.log(f"  {self.hardware_dir / 'thresholds.h'}")
        Logger.log(f"  {self.hardware_dir / 'config.h'}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export to Arduino')
    parser.add_argument('--config', default='config.yaml', help='Config file path')
    args = parser.parse_args()
    
    exporter = ArduinoExporter(args.config)
    exporter.export_all()