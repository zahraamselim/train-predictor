"""
Export thresholds as Arduino header file
Run: python -m exporters.threshold_exporter
"""
import yaml
from pathlib import Path
from utils.logger import Logger


class ThresholdExporter:
    def __init__(self):
        self.results_dir = Path('outputs/results')
        self.models_dir = Path('outputs/models')
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self):
        """Export thresholds as C header file"""
        Logger.section("Exporting thresholds for Arduino")
        
        thresholds_file = self.results_dir / 'thresholds.yaml'
        if not thresholds_file.exists():
            Logger.log(f"File not found: {thresholds_file}")
            Logger.log("Run 'make th-analyze' first to generate thresholds")
            return False
        
        with open(thresholds_file) as f:
            thresholds = yaml.safe_load(f)
        
        header = self._generate_header(thresholds)
        
        output_path = self.models_dir / 'thresholds_config.h'
        output_path.write_text(header)
        
        Logger.log(f"Thresholds exported to {output_path}")
        Logger.log(f"Closure: {thresholds['closure_before_eta']:.2f}s, Opening: {thresholds['opening_after_etd']:.2f}s")
        Logger.log(f"Notification: {thresholds['notification_time']:.2f}s")
        
        sensor_str = ', '.join([f"{s:.1f}m" for s in thresholds['sensor_positions']])
        Logger.log(f"Sensors: [{sensor_str}]")
        
        return True
    
    def _generate_header(self, t):
        """Generate C header file content"""
        sensors = t['sensor_positions']
        
        header = f"""#ifndef THRESHOLDS_CONFIG_H
#define THRESHOLDS_CONFIG_H

#define SENSOR_0_POS {sensors[0]:.2f}f
#define SENSOR_1_POS {sensors[1]:.2f}f
#define SENSOR_2_POS {sensors[2]:.2f}f

#define CLOSURE_THRESHOLD {t['closure_before_eta']:.2f}f
#define OPENING_THRESHOLD {t['opening_after_etd']:.2f}f
#define NOTIFICATION_THRESHOLD {t['notification_time']:.2f}f

#define ENGINE_OFF_THRESHOLD {t['engine_off_threshold']:.2f}f
#define MAX_TRAIN_SPEED {t['max_train_speed']:.2f}f

#endif
"""
        return header


if __name__ == '__main__':
    exporter = ThresholdExporter()
    exporter.export()