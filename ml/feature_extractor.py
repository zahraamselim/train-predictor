"""
Extract features from trajectory data
Run: python -m ml.feature_extractor
"""
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from utils.logger import Logger

class FeatureExtractor:
    def __init__(self, config_path='config/ml.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.sensors = self.config['sensors']
        self.output_dir = Path('outputs/data')
        
    def calculate_physics_eta(self, speed, accel, distance):
        """Calculate ETA using kinematic equations: d = v*t + 0.5*a*t^2"""
        if abs(accel) > 0.01:
            discriminant = speed**2 + 2*accel*distance
            if discriminant >= 0:
                t1 = (-speed + np.sqrt(discriminant)) / accel
                t2 = (-speed - np.sqrt(discriminant)) / accel
                eta = max(t1, t2) if t1 > 0 or t2 > 0 else distance / speed if speed > 0 else 0
            else:
                eta = distance / speed if speed > 0 else 0
        else:
            eta = distance / speed if speed > 0 else 0
        
        return max(0, eta)
    
    def extract_from_trajectory(self, run_df):
        """Extract features from single trajectory"""
        run_df = run_df.sort_values('time')
        
        train_length = run_df['length'].iloc[0] if 'length' in run_df.columns else 150
        
        triggers = {}
        for sensor_id, sensor_pos in self.sensors.items():
            mask = run_df['pos'] >= sensor_pos
            if mask.any():
                idx = mask.idxmax()
                triggers[sensor_id] = {
                    'time': run_df.loc[idx, 'time'],
                    'speed': run_df.loc[idx, 'speed'],
                    'accel': run_df.loc[idx, 'acceleration'],
                    'pos': sensor_pos
                }
        
        if len(triggers) != len(self.sensors):
            return None
        
        sensor_ids = sorted([k for k in self.sensors.keys() if k != 'crossing'])
        crossing_id = 'crossing'
        
        times = [triggers[sid]['time'] for sid in sensor_ids]
        speeds = [triggers[sid]['speed'] for sid in sensor_ids]
        accels = [triggers[sid]['accel'] for sid in sensor_ids]
        positions = [triggers[sid]['pos'] for sid in sensor_ids]
        
        crossing_time = triggers[crossing_id]['time']
        crossing_pos = triggers[crossing_id]['pos']
        
        rear_crossing_mask = run_df['pos'] >= (crossing_pos + train_length)
        if rear_crossing_mask.any():
            rear_crossing_time = run_df.loc[rear_crossing_mask.idxmax(), 'time']
        else:
            rear_crossing_time = None
        
        if rear_crossing_time is None:
            return None
        
        dt_intervals = [times[i+1] - times[i] for i in range(len(times)-1)]
        
        avg_speeds = [
            (positions[i+1] - positions[i]) / dt_intervals[i] 
            for i in range(len(dt_intervals))
        ]
        
        last_sensor_idx = -1
        eta_actual = crossing_time - times[last_sensor_idx]
        etd_actual = rear_crossing_time - times[last_sensor_idx]
        
        distance_remaining = crossing_pos - positions[last_sensor_idx]
        last_speed = speeds[last_sensor_idx]
        last_accel = accels[last_sensor_idx]
        
        eta_physics = self.calculate_physics_eta(last_speed, last_accel, distance_remaining)
        etd_physics = self.calculate_physics_eta(last_speed, last_accel, distance_remaining + train_length)
        
        speed_trend = (speeds[-1] - speeds[0]) / (times[-1] - times[0]) if times[-1] > times[0] else 0
        speed_variance = np.var(speeds)
        time_variance = np.var(dt_intervals)
        
        length_speed_ratio = train_length / last_speed if last_speed > 0 else 0
        distance_length_ratio = distance_remaining / train_length if train_length > 0 else 0
        
        features = {
            'distance_remaining': distance_remaining,
            'train_length': train_length,
            'last_speed': last_speed,
            'last_accel': last_accel,
            'speed_trend': speed_trend,
            'speed_variance': speed_variance,
            'time_variance': time_variance,
            'avg_speed_overall': np.mean(avg_speeds),
            'length_speed_ratio': length_speed_ratio,
            'distance_length_ratio': distance_length_ratio,
            'eta_actual': eta_actual,
            'etd_actual': etd_actual,
            'eta_physics': eta_physics,
            'etd_physics': etd_physics
        }
        
        for i, dt in enumerate(dt_intervals):
            features[f'dt_interval_{i}'] = dt
        
        for i, spd in enumerate(avg_speeds):
            features[f'avg_speed_{i}'] = spd
        
        return features
    
    def extract(self, trajectory_path=None):
        """Extract features from all trajectories"""
        if trajectory_path is None:
            trajectory_path = self.output_dir / 'raw_trajectories.csv'
        
        Logger.section("Extracting features from trajectories")
        
        if not Path(trajectory_path).exists():
            Logger.log(f"Trajectory file not found: {trajectory_path}")
            return None
        
        trajectory_df = pd.read_csv(trajectory_path)
        features_list = []
        
        for run_id in trajectory_df['run_id'].unique():
            run_df = trajectory_df[trajectory_df['run_id'] == run_id]
            features = self.extract_from_trajectory(run_df)
            
            if features is not None:
                features['run_id'] = run_id
                features_list.append(features)
        
        if not features_list:
            Logger.log("No features extracted")
            return None
        
        features_df = pd.DataFrame(features_list)
        
        output_path = self.output_dir / 'features.csv'
        features_df.to_csv(output_path, index=False)
        
        eta_physics_mae = np.mean(np.abs(features_df['eta_actual'] - features_df['eta_physics']))
        etd_physics_mae = np.mean(np.abs(features_df['etd_actual'] - features_df['etd_physics']))
        
        Logger.log(f"Extracted {len(features_df)} feature sets")
        Logger.log(f"ETA physics baseline MAE: {eta_physics_mae:.3f}s")
        Logger.log(f"ETD physics baseline MAE: {etd_physics_mae:.3f}s")
        Logger.log(f"Saved to {output_path}")
        
        return features_df

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract features from trajectories')
    parser.add_argument('--input', help='Input trajectory CSV file')
    parser.add_argument('--config', default='config/ml.yaml', help='Config file path')
    args = parser.parse_args()
    
    extractor = FeatureExtractor(args.config)
    extractor.extract(args.input)