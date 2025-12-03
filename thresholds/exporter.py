"""
Export thresholds as Arduino header file
Run: python -m thresholds.exporter
"""
import yaml
from pathlib import Path
from utils.logger import Logger

class ThresholdExporter:
    def __init__(self, config_path='config/thresholds_calculated.yaml'):
        self.config_path = config_path
        self.output_dir = Path('outputs/arduino')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self):
        """Export thresholds as C header file"""
        Logger.section("Exporting thresholds for Arduino")
        
        config_file = Path(self.config_path)
        if not config_file.exists():
            Logger.log(f"ERROR: {self.config_path} not found")
            Logger.log("Run 'make th-analyze' first to generate thresholds")
            return False
        
        with open(config_file) as f:
            thresholds = yaml.safe_load(f)
        
        header = self._generate_header(thresholds)
        
        output_path = self.output_dir / 'thresholds_config.h'
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Export thresholds for Arduino')
    parser.add_argument('--config', default='config/thresholds_calculated.yaml', help='Config file path')
    args = parser.parse_args()
    
    exporter = ThresholdExporter(args.config)
    exporter.export()