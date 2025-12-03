"""
Analyze collected data and calculate control thresholds
Run: python -m thresholds.analyzer
"""
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from utils.logger import Logger

class ThresholdAnalyzer:
    def __init__(self, config_path='config/thresholds.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.data_dir = Path('outputs/data')
        self.output_file = Path('config/thresholds_calculated.yaml')
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.crossing_pos = 0.0
        self.intersection_west = -300.0
        self.intersection_east = 300.0
        
        safety = self.config['safety']
        self.margin_close = safety['margin_close']
        self.margin_open = safety['margin_open']
        self.driver_reaction = safety['driver_reaction']
        self.engine_off_threshold = safety['engine_off_threshold']
        
        self.train_params = self._load_train_params()
    
    def _load_train_params(self):
        """Load train parameters from ML training"""
        train_params_file = Path('config/train_params.yaml')
        if train_params_file.exists():
            with open(train_params_file) as f:
                params = yaml.safe_load(f)
                return params
        else:
            train = self.config['data_collection']['train']
            return {
                'max_speed': train['max_speed'],
                'avg_speed': train['typical_speed'],
                'max_acceleration': 2.5,
                'max_deceleration': 2.5,
                'avg_length': train['length']
            }
    
    def analyze(self):
        """Calculate all control thresholds"""
        Logger.section("Analyzing threshold data")
        
        clearance_df = self._load_data('gate_clearance.csv')
        trains_df = self._load_data('train_passages.csv')
        travels_df = self._load_data('vehicle_travels.csv')
        
        if clearance_df is None or trains_df is None or travels_df is None:
            Logger.log("ERROR: Missing required data files")
            return None
        
        Logger.log(f"Data samples: clearance={len(clearance_df)}, trains={len(trains_df)}, travels={len(travels_df)}")
        
        self._check_data_quality(clearance_df, trains_df, travels_df)
        
        closure_threshold = self._calculate_closure_threshold(clearance_df)
        opening_threshold = self._calculate_opening_threshold(trains_df)
        notification_time = self._calculate_notification_time(travels_df, closure_threshold)
        sensor_positions = self._calculate_sensor_positions(trains_df, notification_time)
        
        observed_max_speed = trains_df['max_speed'].max() if len(trains_df) > 0 else 0
        max_train_speed = max(observed_max_speed, self.train_params['max_speed'])
        
        thresholds = {
            'closure_before_eta': float(closure_threshold),
            'opening_after_etd': float(opening_threshold),
            'notification_time': float(notification_time),
            'sensor_positions': [float(x) for x in sensor_positions],
            'max_train_speed': float(max_train_speed),
            'engine_off_threshold': float(self.engine_off_threshold),
            'statistics': {
                'clearance_samples': len(clearance_df),
                'train_samples': len(trains_df),
                'travel_samples': len(travels_df),
                'clearance_mean': float(clearance_df['clearance_time'].mean()) if len(clearance_df) > 0 else 0.0,
                'clearance_95th': float(clearance_df['clearance_time'].quantile(0.95)) if len(clearance_df) > 0 else 0.0,
                'clearance_max': float(clearance_df['clearance_time'].max()) if len(clearance_df) > 0 else 0.0,
                'passage_mean': float(trains_df['passage_time'].mean()) if len(trains_df) > 0 else 0.0,
                'passage_max': float(trains_df['passage_time'].max()) if len(trains_df) > 0 else 0.0,
                'travel_mean': float(travels_df['travel_time'].mean()) if len(travels_df) > 0 else 0.0,
                'travel_95th': float(travels_df['travel_time'].quantile(0.95)) if len(travels_df) > 0 else 0.0,
                'observed_max_speed': float(observed_max_speed),
                'ml_max_speed': float(self.train_params['max_speed']),
                'used_max_speed': float(max_train_speed)
            }
        }
        
        with open(self.output_file, 'w') as f:
            yaml.dump(thresholds, f, default_flow_style=False, sort_keys=False)
        
        Logger.log(f"Thresholds saved to {self.output_file}")
        self._print_summary(thresholds)
        
        return thresholds
    
    def _load_data(self, filename):
        """Load data file with error handling"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            Logger.log(f"ERROR: {filepath} not found")
            return None
        
        df = pd.read_csv(filepath)
        return df
    
    def _check_data_quality(self, clearance_df, trains_df, travels_df):
        """Check if sufficient data was collected"""
        min_clearance = 100
        min_trains = 10
        min_travels = 50
        
        warnings = []
        if len(clearance_df) < min_clearance:
            warnings.append(f"Low clearance samples: {len(clearance_df)} (need {min_clearance}+)")
        if len(trains_df) < min_trains:
            warnings.append(f"Low train samples: {len(trains_df)} (need {min_trains}+)")
        if len(travels_df) < min_travels:
            warnings.append(f"Low travel samples: {len(travels_df)} (need {min_travels}+)")
        
        if warnings:
            Logger.log("Data quality warnings:")
            for warning in warnings:
                Logger.log(f"  {warning}")
            Logger.log("Consider increasing simulation duration for better accuracy")
    
    def _calculate_closure_threshold(self, df):
        """Calculate when to close gates before train arrival"""
        if len(df) == 0:
            fallback = 8.0 + self.margin_close
            Logger.log(f"No clearance data, using fallback: {fallback:.2f}s")
            return fallback
        
        clearance_95 = df['clearance_time'].quantile(0.95)
        clearance_max = df['clearance_time'].max()
        
        if len(df) >= 100:
            threshold = clearance_95 + self.margin_close
        else:
            threshold = clearance_max + self.margin_close
        
        return threshold
    
    def _calculate_opening_threshold(self, df):
        """Calculate when to open gates after train departure"""
        if len(df) == 0:
            return self.margin_open
        
        return self.margin_open
    
    def _calculate_notification_time(self, df, closure_threshold):
        """Calculate when to notify intersection"""
        if len(df) >= 50:
            travel_time = df['travel_time'].quantile(0.95)
        elif len(df) > 0:
            travel_time = df['travel_time'].max()
        else:
            distance = abs(self.crossing_pos - self.intersection_west)
            assumed_speed = 12.0
            travel_time = distance / assumed_speed
        
        notification = travel_time + self.driver_reaction + closure_threshold
        return notification
    
    def _calculate_sensor_positions(self, df, notification_time):
        """Calculate optimal sensor positions"""
        if len(df) > 0 and df['max_speed'].max() > 0:
            observed_max_speed = df['max_speed'].max()
        else:
            observed_max_speed = 0
        
        ml_max_speed = self.train_params['max_speed']
        max_speed = max(observed_max_speed, ml_max_speed)
        
        safety_factor = 1.3
        detection_distance = notification_time * max_speed * safety_factor
        
        sensor_0 = detection_distance * 3.0
        sensor_1 = detection_distance * 1.8
        sensor_2 = detection_distance * 0.9
        
        sensor_positions = [sensor_0, sensor_1, sensor_2]
        
        max_practical = 1500.0
        if sensor_positions[0] > max_practical:
            scale = max_practical / sensor_positions[0]
            sensor_positions = [s * scale for s in sensor_positions]
        
        min_practical = 300.0
        if sensor_positions[-1] < min_practical:
            scale = min_practical / sensor_positions[-1]
            sensor_positions = [s * scale for s in sensor_positions]
        
        return sensor_positions
    
    def _print_summary(self, t):
        """Print threshold summary"""
        Logger.section("Threshold Summary")
        
        print(f"\nGate Control:")
        print(f"  Close gates: {t['closure_before_eta']:.2f}s before ETA")
        print(f"  Open gates: {t['opening_after_etd']:.2f}s after ETD")
        print(f"  Engine off threshold: {t['engine_off_threshold']:.2f}s")
        
        print(f"\nIntersection Notification:")
        print(f"  Notify: {t['notification_time']:.2f}s before ETA")
        
        print(f"\nSensor Positions (meters before crossing):")
        for i, pos in enumerate(t['sensor_positions']):
            print(f"  Sensor {i}: {pos:.1f}m")
        
        print(f"\nTrain Parameters:")
        print(f"  Maximum speed: {t['max_train_speed']:.2f} m/s ({t['max_train_speed']*3.6:.1f} km/h)")
        
        print(f"\nData Quality:")
        s = t['statistics']
        quality = []
        quality.append(f"sufficient" if s['clearance_samples'] >= 100 else "low")
        quality.append(f"sufficient" if s['train_samples'] >= 10 else "low")
        quality.append(f"sufficient" if s['travel_samples'] >= 50 else "low")
        
        print(f"  Clearance samples: {s['clearance_samples']} ({quality[0]})")
        print(f"  Train samples: {s['train_samples']} ({quality[1]})")
        print(f"  Travel samples: {s['travel_samples']} ({quality[2]})")
        print()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze threshold data')
    parser.add_argument('--config', default='config/thresholds.yaml', help='Config file path')
    args = parser.parse_args()
    
    analyzer = ThresholdAnalyzer(args.config)
    analyzer.analyze()