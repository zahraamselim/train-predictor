import pandas as pd
import yaml
from pathlib import Path
from simulation.utils.logger import Logger
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class ThresholdAnalyzer:
    """Calculate control thresholds from collected data"""
    
    def __init__(self, data_dir="outputs/data", output_file="config/thresholds.yaml"):
        self.data_dir = Path(data_dir)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.crossing_pos = -200.0
        self.intersections = {'west': -200.0, 'east': 200.0}
        
        self.safety_margin_open = 3.0
        self.safety_margin_close = 2.0
        self.driver_reaction = 2.5
        self.engine_off_threshold = 15.0
    
    def analyze(self):
        Logger.section("Analyzing thresholds")
        
        clearance = pd.read_csv(self.data_dir / 'gate_clearance.csv')
        clearance_95 = float(clearance['clearance_time'].quantile(0.95))
        closure_threshold = float(clearance_95 + self.safety_margin_close)
        
        Logger.log(f"Gate closure threshold: {closure_threshold:.2f}s")
        
        trains = pd.read_csv(self.data_dir / 'train_passages.csv')
        passage_max = float(trains['passage_time_w'].max())
        opening_threshold = float(passage_max + self.safety_margin_open)
        
        Logger.log(f"Gate opening threshold: {opening_threshold:.2f}s")
        
        travels = pd.read_csv(self.data_dir / 'vehicle_travels.csv')
        notification_times = {}
        
        for inter_name, inter_pos in self.intersections.items():
            inter_df = travels[travels['intersection'] == inter_name]
            
            if len(inter_df) == 0:
                distance = abs(self.crossing_pos - inter_pos)
                travel_time = distance / 15.0
                notification = float(travel_time + self.driver_reaction + closure_threshold)
            else:
                travel_95 = float(inter_df['travel_time'].quantile(0.95))
                notification = float(travel_95 + self.driver_reaction + closure_threshold)
            
            notification_times[inter_name] = notification
            Logger.log(f"{inter_name} notification: {notification:.2f}s")
        
        max_notification = max(notification_times.values())
        max_speed = float(trains['max_speed'].max())
        
        sensor_margin = 1.2
        nearest_sensor = max_notification * max_speed * sensor_margin
        
        sensor_positions = [
            float(nearest_sensor * 3.5),
            float(nearest_sensor * 2.0),
            float(nearest_sensor)
        ]
        
        max_sensor = max(sensor_positions)
        if max_sensor > 1300:
            scale = 1300 / max_sensor
            sensor_positions = [s * scale for s in sensor_positions]
        
        Logger.log(f"Sensor positions: {[f'{p:.1f}m' for p in sensor_positions]}")
        
        thresholds = {
            'closure_before_eta': closure_threshold,
            'opening_after_etd': opening_threshold,
            'notification_times': notification_times,
            'sensor_positions': sensor_positions,
            'max_train_speed': max_speed,
            'engine_off_threshold': self.engine_off_threshold
        }
        
        with open(self.output_file, 'w') as f:
            yaml.dump(thresholds, f, default_flow_style=False)
        
        Logger.log(f"Saved to {self.output_file}")
        
        return thresholds

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    analyzer = ThresholdAnalyzer()
    analyzer.analyze()