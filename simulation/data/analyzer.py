"""
Threshold Analyzer
Calculates control thresholds from collected data
"""
import pandas as pd
import yaml
from pathlib import Path
from datetime import datetime


class ThresholdAnalyzer:
    def __init__(self, data_dir="outputs/data", output_file="config/thresholds.yaml"):
        self.data_dir = Path(data_dir)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.crossing_pos = 0.0
        self.intersections = {
            'west': -200.0,
            'east': 200.0
        }
        
        self.safety_margin_open = 3.0
        self.safety_margin_close = 2.0
        self.driver_reaction = 2.5
        self.engine_off_threshold = 15.0
    
    def analyze(self):
        """Calculate all control thresholds"""
        print(f"[{self._timestamp()}] Analyzing thresholds")
        
        # Gate closure threshold
        clearance = pd.read_csv(self.data_dir / 'gate_clearance.csv')
        clearance_95 = clearance['clearance_time'].quantile(0.95)
        closure_threshold = clearance_95 + self.safety_margin_close
        
        print(f"Gate closure threshold: {closure_threshold:.2f}s")
        print(f"  Vehicle clearance (95th): {clearance_95:.2f}s")
        print(f"  Safety margin: {self.safety_margin_close:.2f}s")
        
        # Gate opening threshold
        trains = pd.read_csv(self.data_dir / 'train_passages.csv')
        passage_max = trains['passage_time_w'].max()
        opening_threshold = passage_max + self.safety_margin_open
        
        print(f"Gate opening threshold: {opening_threshold:.2f}s")
        print(f"  Train passage (max): {passage_max:.2f}s")
        print(f"  Safety margin: {self.safety_margin_open:.2f}s")
        
        # Intersection notification times
        travels = pd.read_csv(self.data_dir / 'vehicle_travels.csv')
        notification_times = {}
        
        print("Intersection notification thresholds:")
        for inter_name, inter_pos in self.intersections.items():
            inter_df = travels[travels['intersection'] == inter_name]
            
            if len(inter_df) == 0:
                continue
            
            distance = abs(self.crossing_pos - inter_pos)
            travel_95 = inter_df['travel_time'].quantile(0.95)
            notification = travel_95 + self.driver_reaction + closure_threshold
            notification_times[inter_name] = notification
            
            print(f"  {inter_name}: {notification:.2f}s")
            print(f"    Travel time (95th): {travel_95:.2f}s")
        
        # Sensor placement
        max_notification = max(notification_times.values())
        max_speed = trains['max_speed'].max()
        
        sensor_margin = 1.2
        nearest_sensor = max_notification * max_speed * sensor_margin
        
        sensor_positions = [
            nearest_sensor * 3.5,
            nearest_sensor * 2.0,
            nearest_sensor
        ]
        
        print(f"Sensor positions:")
        for i, pos in enumerate(sensor_positions):
            print(f"  Sensor {i}: {pos:.1f}m from crossing")
        
        # Save thresholds
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
        
        print(f"[{self._timestamp()}] Saved to {self.output_file}")
        
        return thresholds
    
    def _timestamp(self):
        """Get current timestamp"""
        return datetime.now().strftime("%H:%M:%S")


if __name__ == '__main__':
    analyzer = ThresholdAnalyzer()
    analyzer.analyze()