"""
Calculate control thresholds from collected data
Run: python -m simulation.threshold_analyzer
"""
import pandas as pd
import yaml
from pathlib import Path
from utils.logger import Logger

class ThresholdAnalyzer:
    def __init__(self, config_path='config/simulation.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.data_dir = Path('outputs/data')
        self.output_file = Path('config/thresholds.yaml')
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        net_cfg = self.config['network']
        self.crossing_pos = net_cfg['crossing_w']
        self.intersections = net_cfg['intersections']
        
        safety_cfg = self.config['safety']
        self.safety_margin_open = safety_cfg['margin_open']
        self.safety_margin_close = safety_cfg['margin_close']
        self.driver_reaction = safety_cfg['driver_reaction']
        self.engine_off_threshold = safety_cfg['engine_off_threshold']
    
    def analyze(self):
        """Calculate all thresholds from collected data"""
        Logger.section("Analyzing control thresholds")
        
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
            Logger.log(f"{inter_name.capitalize()} notification: {notification:.2f}s")
        
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze control thresholds')
    parser.add_argument('--config', default='config/simulation.yaml', help='Config file path')
    args = parser.parse_args()
    
    analyzer = ThresholdAnalyzer(args.config)
    analyzer.analyze()