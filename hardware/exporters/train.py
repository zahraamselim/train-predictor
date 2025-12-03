"""
Export train parameters from ML training data
Run: python -m exporters.train_params_exporter
"""
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from utils.logger import Logger


class TrainParamsExporter:
    def __init__(self):
        self.data_dir = Path('outputs/data')
        self.results_dir = Path('outputs/results')
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self):
        """Export train parameters from trajectory data"""
        Logger.section("Extracting train parameters from ML data")
        
        trajectory_file = self.data_dir / 'raw_trajectories.csv'
        if not trajectory_file.exists():
            Logger.log(f"File not found: {trajectory_file}")
            Logger.log("Run 'make ml-data' first to generate training data")
            return None
        
        df = pd.read_csv(trajectory_file)
        
        max_speed = df['speed'].max()
        avg_speed = df['speed'].mean()
        max_accel = df['acceleration'].max()
        min_accel = df['acceleration'].min()
        
        lengths = df.groupby('run_id')['length'].first()
        unique_lengths = lengths.unique()
        avg_length = lengths.mean()
        
        params = {
            'max_speed': float(max_speed),
            'avg_speed': float(avg_speed),
            'max_acceleration': float(max_accel),
            'max_deceleration': float(abs(min_accel)),
            'train_lengths': [float(l) for l in sorted(unique_lengths)],
            'avg_length': float(avg_length),
            'n_samples': int(df['run_id'].nunique())
        }
        
        output_file = self.results_dir / 'train_params.yaml'
        with open(output_file, 'w') as f:
            yaml.dump(params, f, default_flow_style=False, sort_keys=False)
        
        Logger.log(f"Train parameters saved to {output_file}")
        Logger.log(f"Max speed: {max_speed:.2f} m/s ({max_speed*3.6:.1f} km/h)")
        Logger.log(f"Avg speed: {avg_speed:.2f} m/s ({avg_speed*3.6:.1f} km/h)")
        Logger.log(f"Max acceleration: {max_accel:.2f} m/s²")
        Logger.log(f"Max deceleration: {abs(min_accel):.2f} m/s²")
        Logger.log(f"Train lengths: {unique_lengths}")
        Logger.log(f"Avg length: {avg_length:.1f}m")
        
        return params


if __name__ == '__main__':
    exporter = TrainParamsExporter()
    exporter.export()