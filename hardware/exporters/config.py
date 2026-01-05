"""
Export crossing configuration to Arduino C header
Run: python -m hardware.exporters.config
"""
from pathlib import Path
from utils.logger import Logger


def export_config(output_path='hardware/crossing_config.h'):
    """Export crossing configuration as C header"""
    
    Logger.section("Exporting crossing configuration")
    
    header = """#ifndef CROSSING_CONFIG_H
#define CROSSING_CONFIG_H

#include "thresholds.h"

/*
 * Crossing Control Configuration
 * Helper functions for Arduino sketch
 */

// Get gate close threshold (seconds before train arrival)
inline float getGateCloseThreshold() {
    return GATE_CLOSE_THRESHOLD;
}

// Get notification threshold (seconds before train arrival  )
inline float getNotificationThreshold() {
    return NOTIFICATION_THRESHOLD;
}

// Get gate opening delay (seconds after train clears)
inline float getGateOpenDelay() {
    return GATE_OPEN_DELAY;
}

// Get sensor positions (meters from crossing)
inline float getSensor0Position() {
    return SENSOR_0_POS;
}

inline float getSensor1Position() {
    return SENSOR_1_POS;
}

inline float getSensor2Position() {
    return SENSOR_2_POS;
}

// Buzzer beep interval (milliseconds)
inline unsigned long getBuzzerInterval() {
    return 500;  // 0.5 second beeps
}

// Display update interval (milliseconds)
inline unsigned long getDisplayUpdateInterval() {
    return 100;  // Update 10 times per second for smooth countdown
}

// Train length estimation for demo (meters)
inline float getDefaultTrainLength() {
    return 0.30f;  // 30cm for physical demo, 150m for simulation
}

// Servo angles
#define GATE_OPEN_ANGLE 90
#define GATE_CLOSED_ANGLE 0

// Display brightness (0-15)
#define DISPLAY_BRIGHTNESS 0x0f

#endif
"""
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(header)
    
    Logger.log(f"Saved: {output_path}")
    Logger.log("Configuration ready for Arduino")
    Logger.log("Includes: ETA/ETD thresholds, sensor positions, timing helpers")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export configuration to Arduino')
    parser.add_argument('--output', default='hardware/crossing_config.h',
                       help='Output C header file')
    args = parser.parse_args()
    
    export_config(args.output)