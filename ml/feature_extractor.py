"""
Feature extraction from trajectory data
"""
import pandas as pd
import numpy as np
from pathlib import Path
from utils import get_logger

class FeatureExtractor:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.sensors = config['sensors']
        self.data_dir = Path(config['output']['data_dir'])
        
    def calculate_physics_eta(self, speed, accel, distance):
        """
        Physics-based ETA calculation using kinematic equations
        d = v*t + 0.5*a*t^2
        """
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
        
        dt_intervals = [times[i+1] - times[i] for i in range(len(times)-1)]
        
        avg_speeds = [
            (positions[i+1] - positions[i]) / dt_intervals[i] 
            for i in range(len(dt_intervals))
        ]
        
        last_sensor_idx = -1
        eta_actual = crossing_time - times[last_sensor_idx]
        
        distance_remaining = crossing_pos - positions[last_sensor_idx]
        last_speed = speeds[last_sensor_idx]
        last_accel = accels[last_sensor_idx]
        
        eta_physics = self.calculate_physics_eta(last_speed, last_accel, distance_remaining)
        
        speed_trend = (speeds[-1] - speeds[0]) / (times[-1] - times[0]) if times[-1] > times[0] else 0
        speed_variance = np.var(speeds)
        time_variance = np.var(dt_intervals)
        
        features = {
            'distance_remaining': distance_remaining,
            'last_speed': last_speed,
            'last_accel': last_accel,
            'speed_trend': speed_trend,
            'speed_variance': speed_variance,
            'time_variance': time_variance,
            'avg_speed_overall': np.mean(avg_speeds),
            'eta_actual': eta_actual,
            'eta_physics': eta_physics
        }
        
        for i, dt in enumerate(dt_intervals):
            features[f'dt_interval_{i}'] = dt
        
        for i, spd in enumerate(avg_speeds):
            features[f'avg_speed_{i}'] = spd
        
        return features
    
    def extract(self, trajectory_df):
        """Extract features from all trajectories"""
        self.logger.info("Extracting features from trajectories")
        
        features_list = []
        
        for run_id in trajectory_df['run_id'].unique():
            run_df = trajectory_df[trajectory_df['run_id'] == run_id]
            features = self.extract_from_trajectory(run_df)
            
            if features is not None:
                features['run_id'] = run_id
                features_list.append(features)
        
        if not features_list:
            self.logger.error("No features extracted")
            return None
        
        features_df = pd.DataFrame(features_list)
        
        output_path = self.data_dir / 'features.csv'
        features_df.to_csv(output_path, index=False)
        
        self.logger.info(f"Extracted {len(features_df)} feature sets")
        self.logger.info(f"Physics baseline MAE: {np.mean(np.abs(features_df['eta_actual'] - features_df['eta_physics'])):.3f}s")
        self.logger.info(f"Saved to {output_path}")
        
        return features_df