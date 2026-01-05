"""
Export thresholds to Arduino C header (Physical Demo Scale)
Run: python -m hardware.exporters.threshold
"""
import yaml
from pathlib import Path
from utils.logger import Logger


def export_thresholds_demo(config_path='outputs/results/thresholds.yaml', 
                           output_path='hardware/thresholds.h',
                           demo_mode=True):
    """Export thresholds for physical demo or simulation"""
    
    Logger.section("Exporting thresholds to Arduino")
    
    if demo_mode:
        Logger.log("DEMO MODE: Using physical tabletop scale")
        export_demo_scale(output_path)
    else:
        Logger.log("SIMULATION MODE: Using SUMO scale")
        export_simulation_scale(config_path, output_path)


def export_demo_scale(output_path):
    """Export thresholds for physical tabletop demo"""
    
    Logger.log("Physical layout:")
    Logger.log("  S0 --10cm-- S1 --10cm-- S2 --20cm-- Crossing --20cm-- Intersection")
    
    header = """#ifndef THRESHOLDS_H
#define THRESHOLDS_H

/*
 * Physical Demo Configuration
 * Scale: Tabletop model (~60cm total)
 * Movement: Hand-moved toy train/cars
 */

// Physical demo mode flag
#define DEMO_MODE true

// Sensor positions (meters from crossing)
// Layout: S0 --10cm-- S1 --10cm-- S2 --20cm-- Crossing
#define SENSOR_0_POS 0.40f    // 40cm from crossing
#define SENSOR_1_POS 0.30f    // 30cm from crossing
#define SENSOR_2_POS 0.20f    // 20cm from crossing

// Physical distances (meters)
#define SENSOR_SPACING 0.10f           // 10cm between sensors
#define LAST_SENSOR_TO_CROSSING 0.20f  // 20cm from S2 to crossing
#define CROSSING_TO_INTERSECTION 0.20f // 20cm from crossing to intersection

// Demo timing (seconds) - Fixed for hand movement
// These provide predictable demonstration regardless of hand speed
#define DEMO_NOTIFICATION_TIME 3.0f    // Warn intersection 3s after S0
#define DEMO_GATE_CLOSE_TIME 5.0f      // Close gates 5s after S0
#define DEMO_GATE_OPEN_DELAY 3.0f      // Wait 3s after train passes
#define DEMO_TOTAL_CYCLE 12.0f         // Total demo cycle time

// Expected hand movement speed (m/s)
#define EXPECTED_HAND_SPEED 0.5f       // Slow walking speed

// Gate servo angles
#define GATE_OPEN_ANGLE 90
#define GATE_CLOSED_ANGLE 0

// Buzzer timing
#define BUZZER_INTERVAL 500            // 500ms beep interval

#endif
"""
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(header)
    
    Logger.log(f"Saved: {output_path}")
    Logger.log("")
    Logger.log("Demo sequence:")
    Logger.log("  T+0s: Train triggers S0")
    Logger.log("  T+3s: Intersection notified (red light)")
    Logger.log("  T+5s: Gates close, countdown starts")
    Logger.log("  T+12s: Gates open, system resets")
    Logger.log("")
    Logger.log("Hand movement: Move train smoothly across sensors")


def export_simulation_scale(config_path, output_path):
    """Export thresholds for SUMO simulation scale"""
    
    config_file = Path(config_path)
    if not config_file.exists():
        Logger.log(f"ERROR: Thresholds file not found: {config_path}")
        Logger.log("Run: make th-pipeline or python -m thresholds.analyzer")
        Logger.log("Falling back to demo scale")
        export_demo_scale(output_path)
        return
    
    with open(config_file) as f:
        thresholds = yaml.safe_load(f)
    
    sensor_positions = thresholds['sensor_positions']
    
    header = f"""#ifndef THRESHOLDS_H
#define THRESHOLDS_H

/*
 * SUMO Simulation Configuration
 * Scale: Full-scale network (1000+ meter distances)
 * Movement: Simulated trains with realistic physics
 */

// Simulation mode flag
#define DEMO_MODE false

// Sensor positions (meters from crossing) - Full scale
#define SENSOR_0_POS {sensor_positions[0]:.2f}f
#define SENSOR_1_POS {sensor_positions[1]:.2f}f
#define SENSOR_2_POS {sensor_positions[2]:.2f}f

// Calculated thresholds (seconds)
#define GATE_CLOSE_THRESHOLD {thresholds['closure_before_eta']:.2f}f
#define NOTIFICATION_THRESHOLD {thresholds['notification_time']:.2f}f
#define GATE_OPEN_DELAY {thresholds['opening_after_etd']:.2f}f

// Train parameters
#define MAX_TRAIN_SPEED {thresholds['max_train_speed']:.2f}f

// Statistics
// Clearance 95th: {thresholds['statistics']['clearance_p95']:.2f}s
// Travel 95th: {thresholds['statistics']['travel_p95']:.2f}s
// Data: {thresholds['statistics']['n_clearances']} clearances, {thresholds['statistics']['n_travels']} travels

#endif
"""
    
    output_file = Path(output_path)
    output_file.write_text(header)
    
    Logger.log(f"Saved: {output_path}")
    Logger.log(f"Sensor 0: {sensor_positions[0]:.0f}m")
    Logger.log(f"Sensor 1: {sensor_positions[1]:.0f}m")
    Logger.log(f"Sensor 2: {sensor_positions[2]:.0f}m")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export thresholds to Arduino')
    parser.add_argument('--input', default='outputs/results/thresholds.yaml',
                       help='Input YAML file (simulation mode)')
    parser.add_argument('--output', default='hardware/thresholds.h',
                       help='Output C header file')
    parser.add_argument('--demo', action='store_true',
                       help='Use physical demo scale (default: auto-detect)')
    parser.add_argument('--sim', action='store_true',
                       help='Use SUMO simulation scale')
    args = parser.parse_args()
    
    if args.sim:
        demo_mode = False
    elif args.demo:
        demo_mode = True
    else:
        demo_mode = not Path(args.input).exists()
        if demo_mode:
            Logger.log("No simulation data found, using demo mode")
    
    export_thresholds_demo(args.input, args.output, demo_mode)