"""
Export thresholds as Arduino header file
Run: python -m hardware.exporters.threshold
"""
import yaml
from pathlib import Path
from utils.logger import Logger


class ThresholdExporter:
    def __init__(self):
        self.results_dir = Path('outputs/results')
        self.hardware_dir = Path('hardware')
        self.hardware_dir.mkdir(exist_ok=True)
    
    def export(self):
        """Export thresholds as C header file"""
        Logger.section("Exporting thresholds for Arduino")
        
        thresholds_file = self.results_dir / 'thresholds.yaml'
        if not thresholds_file.exists():
            Logger.log(f"File not found: {thresholds_file}")
            Logger.log("Run 'make th-pipeline' first to generate thresholds")
            return False
        
        with open(thresholds_file) as f:
            thresholds = yaml.safe_load(f)
        
        # Validate sensor ordering
        sensors = thresholds['sensor_positions']
        if not (sensors[0] >= sensors[1] >= sensors[2]):
            Logger.log("WARNING: Sensor positions not in descending order!")
            Logger.log(f"Current: S0={sensors[0]:.0f}m, S1={sensors[1]:.0f}m, S2={sensors[2]:.0f}m")
            Logger.log("Fixing sensor ordering...")
            
            # Fix sensor 2 to be less than sensor 1
            if sensors[2] >= sensors[1]:
                sensors[2] = sensors[1] * 0.8
                sensors[2] = max(sensors[2], 300)  # Keep minimum
                thresholds['sensor_positions'] = sensors
                Logger.log(f"Corrected S2 to {sensors[2]:.0f}m")
        
        header = self._generate_header(thresholds)
        
        output_path = self.hardware_dir / 'thresholds.h'
        output_path.write_text(header)
        
        Logger.log(f"Exported to: {output_path}")
        Logger.log(f"Closure: {thresholds['closure_before_eta']:.2f}s")
        Logger.log(f"Opening: {thresholds['opening_after_etd']:.2f}s")
        Logger.log(f"Notification: {thresholds['notification_time']:.2f}s")
        
        sensors = thresholds['sensor_positions']
        Logger.log(f"Sensors: {sensors[0]:.0f}m, {sensors[1]:.0f}m, {sensors[2]:.0f}m")
        
        return True
    
    def _generate_header(self, t):
        """Generate C header file content"""
        sensors = t['sensor_positions']
        
        header = f"""#ifndef THRESHOLDS_H
#define THRESHOLDS_H

// Sensor positions (meters before crossing)
#define SENSOR_0_POS {sensors[0]:.2f}f
#define SENSOR_1_POS {sensors[1]:.2f}f
#define SENSOR_2_POS {sensors[2]:.2f}f

// Gate control thresholds (seconds)
#define CLOSURE_THRESHOLD {t['closure_before_eta']:.2f}f
#define OPENING_THRESHOLD {t['opening_after_etd']:.2f}f

// Traffic notification threshold (seconds)
#define NOTIFICATION_THRESHOLD {t['notification_time']:.2f}f

// Train parameters
#define MAX_TRAIN_SPEED {t['max_train_speed']:.2f}f

#endif
"""
        return header


if __name__ == '__main__':
    exporter = ThresholdExporter()
    exporter.export()