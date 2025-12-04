"""
Data preparation: generation, feature extraction, and visualization
Run: python -m ml.data_preparation
"""
import subprocess
import pandas as pd
import numpy as np
import yaml
import matplotlib.pyplot as plt
from pathlib import Path
import xml.etree.ElementTree as ET
from utils.logger import Logger
from ml.network import NetworkGenerator

class Data:
    def __init__(self, config_path='ml/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.output_dir = Path('outputs/data')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.plots_dir = Path('outputs/plots')
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        
        self.network_gen = NetworkGenerator(config_path)
        self.sensors = self.config['sensors']
    
    def generate_train_params(self, n_samples):
        """Generate random train parameters with realistic operating profiles"""
        np.random.seed(self.config['training']['random_seed'])
        
        params = []
        for _ in range(n_samples):
            # All trains can go up to 50 m/s (speed_factor = 1.0)
            # Variation comes from depart_speed and accel/decel
            
            # Choose realistic train operating scenario
            scenario = np.random.choice(['fast', 'moderate', 'slow', 'accelerating', 'decelerating'])
            
            if scenario == 'fast':
                # Fast train, already at high speed, maintains it
                depart_speed = np.random.uniform(40, 48)
                accel = np.random.uniform(0.3, 0.8)  # Low accel (already fast)
                decel = np.random.uniform(0.3, 0.8)  # Low decel (maintains speed)
                
            elif scenario == 'moderate':
                # Regular freight train, steady moderate speed
                depart_speed = np.random.uniform(30, 40)
                accel = np.random.uniform(0.5, 1.2)
                decel = np.random.uniform(0.5, 1.2)
                
            elif scenario == 'slow':
                # Cautious/heavy train, stays slow
                depart_speed = np.random.uniform(20, 32)
                accel = np.random.uniform(0.3, 0.7)  # Low accel (stays slow)
                decel = np.random.uniform(0.8, 1.5)
                
            elif scenario == 'accelerating':
                # Train gaining speed rapidly
                depart_speed = np.random.uniform(25, 35)
                accel = np.random.uniform(1.5, 2.0)  # High accel (speeding up)
                decel = np.random.uniform(0.5, 1.0)
                
            else:  # decelerating
                # Train slowing down
                depart_speed = np.random.uniform(35, 45)
                accel = np.random.uniform(0.3, 0.8)
                decel = np.random.uniform(1.5, 2.0)  # High decel (slowing down)
            
            params.append({
                'depart_speed': depart_speed,
                'accel': accel,
                'decel': decel,
                'length': np.random.choice([100, 150, 200, 250]),
                'speed_factor': 1.0,  # All trains CAN go 50 m/s, but behavior varies
                'scenario': scenario
            })
        
        return params
    
    def run_simulation(self, train_params, run_id):
        """Run one SUMO simulation"""
        route_file = self.network_gen.generate_route_file(train_params, run_id)
        config_file = self.network_gen.generate_config_file(route_file, run_id)
        
        result = subprocess.run(
            ['sumo', '-c', config_file, '--no-step-log', '--no-warnings'],
            capture_output=True
        )
        
        Path(route_file).unlink(missing_ok=True)
        Path(config_file).unlink(missing_ok=True)
        
        if result.returncode != 0:
            return None
        
        fcd_file = f'temp_fcd_{run_id}.xml'
        if not Path(fcd_file).exists():
            return None
        
        data = self.parse_fcd(fcd_file, run_id, train_params['length'], train_params.get('scenario', 'unknown'))
        Path(fcd_file).unlink(missing_ok=True)
        
        return data
    
    def parse_fcd(self, fcd_file, run_id, train_length, scenario):
        """Parse SUMO FCD output"""
        try:
            tree = ET.parse(fcd_file)
            root = tree.getroot()
        except:
            return None
        
        data = []
        for timestep in root.findall('timestep'):
            time = float(timestep.get('time'))
            for vehicle in timestep.findall('vehicle'):
                if vehicle.get('id').startswith('train_'):
                    data.append({
                        'time': time,
                        'pos': float(vehicle.get('pos')),
                        'speed': float(vehicle.get('speed')),
                        'acceleration': float(vehicle.get('acceleration', 0)),
                        'length': train_length,
                        'run_id': run_id,
                        'scenario': scenario
                    })
        
        return pd.DataFrame(data) if data else None
    
    def generate_trajectories(self, n_samples):
        """Generate training data"""
        Logger.section(f"Generating {n_samples} training samples")
        
        net_file = self.network_gen.generate()
        if not net_file:
            Logger.log("Failed to generate network")
            return None
        
        train_params = self.generate_train_params(n_samples)
        all_data = []
        successful = 0
        scenario_counts = {}
        
        for i, params in enumerate(train_params):
            df = self.run_simulation(params, i)
            
            if df is not None and len(df) > 10:
                all_data.append(df)
                successful += 1
                scenario = params.get('scenario', 'unknown')
                scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
                
                if (i + 1) % 100 == 0:
                    Logger.log(f"Progress: {successful}/{i+1} ({successful/(i+1)*100:.1f}%)")
        
        if not all_data:
            Logger.log("No successful simulations")
            return None
        
        combined = pd.concat(all_data, ignore_index=True)
        output_path = self.output_dir / 'raw_trajectories.csv'
        combined.to_csv(output_path, index=False)
        
        Logger.log(f"Generated {successful} trajectories with {len(combined)} data points")
        Logger.log(f"Success rate: {successful}/{len(train_params)} ({successful/len(train_params)*100:.1f}%)")
        Logger.log("Scenario distribution:")
        for scenario, count in sorted(scenario_counts.items()):
            Logger.log(f"  {scenario}: {count} ({count/successful*100:.1f}%)")
        Logger.log(f"Saved to {output_path}")
        
        if successful < n_samples * 0.85:
            Logger.log(f"WARNING: Success rate below 85%. Consider increasing sim_duration in config.yaml")
        
        return combined
    
    def calculate_physics_prediction(self, speed, distance):
        """Simple physics baseline"""
        return distance / speed if speed > 0 else 0
    
    def extract_features_from_trajectory(self, run_df):
        """Extract features from one trajectory"""
        run_df = run_df.sort_values('time')
        train_length = run_df['length'].iloc[0]
        scenario = run_df['scenario'].iloc[0] if 'scenario' in run_df.columns else 'unknown'
        
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
        positions = [triggers[sid]['pos'] for sid in sensor_ids]
        
        crossing_time = triggers[crossing_id]['time']
        crossing_pos = triggers[crossing_id]['pos']
        
        rear_crossing_mask = run_df['pos'] >= (crossing_pos + train_length)
        if not rear_crossing_mask.any():
            return None
        
        rear_crossing_time = run_df.loc[rear_crossing_mask.idxmax(), 'time']
        
        last_sensor_time = times[-1]
        last_speed = speeds[-1]
        distance_remaining = crossing_pos - positions[-1]
        
        eta_actual = crossing_time - last_sensor_time
        etd_actual = rear_crossing_time - last_sensor_time
        
        eta_physics = self.calculate_physics_prediction(last_speed, distance_remaining)
        etd_physics = self.calculate_physics_prediction(last_speed, distance_remaining + train_length)
        
        time_01 = times[1] - times[0]
        time_12 = times[2] - times[1]
        
        avg_speed_01 = (positions[1] - positions[0]) / time_01 if time_01 > 0 else 0
        avg_speed_12 = (positions[2] - positions[1]) / time_12 if time_12 > 0 else 0
        
        # Calculate acceleration trend (is train speeding up or slowing down?)
        accel_01 = (speeds[1] - speeds[0]) / time_01 if time_01 > 0 else 0
        accel_12 = (speeds[2] - speeds[1]) / time_12 if time_12 > 0 else 0
        
        # Predicted speed at crossing (extrapolate from acceleration trend)
        time_to_crossing = distance_remaining / last_speed if last_speed > 0 else 0
        predicted_crossing_speed = last_speed + (accel_12 * time_to_crossing)
        predicted_crossing_speed = max(5.0, min(50.0, predicted_crossing_speed))  # Clamp to realistic range
        
        return {
            'distance_remaining': distance_remaining,
            'train_length': train_length,
            'last_speed': last_speed,
            'speed_change': speeds[-1] - speeds[0],
            'time_01': time_01,
            'time_12': time_12,
            'avg_speed_01': avg_speed_01,
            'avg_speed_12': avg_speed_12,
            'accel_trend': accel_12,  # NEW: Recent acceleration
            'predicted_speed_at_crossing': predicted_crossing_speed,  # NEW: Extrapolated speed
            'eta_actual': eta_actual,
            'etd_actual': etd_actual,
            'eta_physics': eta_physics,
            'etd_physics': etd_physics,
            'scenario': scenario
        }
    
    def extract_features(self, trajectory_df):
        """Extract features from all trajectories"""
        Logger.section("Extracting features from trajectories")
        
        features_list = []
        for run_id in trajectory_df['run_id'].unique():
            run_df = trajectory_df[trajectory_df['run_id'] == run_id]
            features = self.extract_features_from_trajectory(run_df)
            
            if features is not None:
                features['run_id'] = run_id
                features_list.append(features)
        
        if not features_list:
            Logger.log("No features extracted")
            return None
        
        features_df = pd.DataFrame(features_list)
        
        output_path = self.output_dir / 'features.csv'
        features_df.to_csv(output_path, index=False)
        
        eta_physics_error = np.mean(np.abs(features_df['eta_actual'] - features_df['eta_physics']))
        etd_physics_error = np.mean(np.abs(features_df['etd_actual'] - features_df['etd_physics']))
        
        Logger.log(f"Extracted {len(features_df)} feature sets")
        Logger.log(f"Speed at last sensor - Mean: {features_df['last_speed'].mean():.2f} m/s, Std: {features_df['last_speed'].std():.2f} m/s")
        Logger.log(f"ETA actual - Mean: {features_df['eta_actual'].mean():.2f}s, Std: {features_df['eta_actual'].std():.2f}s")
        Logger.log(f"ETA physics baseline error: {eta_physics_error:.3f}s")
        Logger.log(f"ETD physics baseline error: {etd_physics_error:.3f}s")
        Logger.log(f"Saved to {output_path}")
        
        return features_df
    
    def plot_trajectories(self, trajectory_df):
        """Plot sample train trajectories"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        sample_runs = np.random.choice(trajectory_df['run_id'].unique(), 6, replace=False)
        colors = plt.cm.tab10(np.linspace(0, 1, 6))
        
        ax = axes[0, 0]
        for i, run_id in enumerate(sample_runs):
            run_df = trajectory_df[trajectory_df['run_id'] == run_id]
            scenario = run_df['scenario'].iloc[0] if 'scenario' in run_df.columns else ''
            ax.plot(run_df['time'], run_df['pos'], 
                   label=f'Train {run_id} ({scenario})', 
                   color=colors[i], linewidth=2, alpha=0.8)
        
        for name, pos in self.sensors.items():
            if name != 'crossing':
                ax.axhline(pos, color='gray', linestyle='--', alpha=0.5)
                ax.text(5, pos + 50, f'Sensor {name}', fontsize=9, color='gray')
            else:
                ax.axhline(pos, color='red', linestyle='-', linewidth=2, alpha=0.7)
                ax.text(5, pos + 50, 'CROSSING', fontsize=10, color='red', fontweight='bold')
        
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Position (meters)', fontsize=12)
        ax.set_title('Sample Train Trajectories (Variable Speed Profiles)', fontsize=14, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        ax = axes[0, 1]
        for i, run_id in enumerate(sample_runs):
            run_df = trajectory_df[trajectory_df['run_id'] == run_id]
            scenario = run_df['scenario'].iloc[0] if 'scenario' in run_df.columns else ''
            ax.plot(run_df['time'], run_df['speed'], 
                   label=f'Train {run_id} ({scenario})',
                   color=colors[i], linewidth=2, alpha=0.8)
        
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Speed (m/s)', fontsize=12)
        ax.set_title('Train Speed Profiles (Now with Variance!)', fontsize=14, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        ax = axes[1, 0]
        for i, run_id in enumerate(sample_runs):
            run_df = trajectory_df[trajectory_df['run_id'] == run_id]
            scenario = run_df['scenario'].iloc[0] if 'scenario' in run_df.columns else ''
            ax.plot(run_df['time'], run_df['acceleration'], 
                   label=f'Train {run_id} ({scenario})',
                   color=colors[i], linewidth=2, alpha=0.8)
        
        ax.axhline(0, color='black', linestyle='-', linewidth=1)
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Acceleration (m/s²)', fontsize=12)
        ax.set_title('Train Acceleration Profiles', fontsize=14, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        ax = axes[1, 1]
        for i, run_id in enumerate(sample_runs):
            run_df = trajectory_df[trajectory_df['run_id'] == run_id]
            scenario = run_df['scenario'].iloc[0] if 'scenario' in run_df.columns else ''
            ax.plot(run_df['pos'], run_df['speed'], 
                   label=f'Train {run_id} ({scenario})',
                   color=colors[i], linewidth=2, alpha=0.8)
        
        for name, pos in self.sensors.items():
            if name != 'crossing':
                ax.axvline(pos, color='gray', linestyle='--', alpha=0.5)
            else:
                ax.axvline(pos, color='red', linestyle='-', linewidth=2, alpha=0.7)
        
        ax.set_xlabel('Position (meters)', fontsize=12)
        ax.set_ylabel('Speed (m/s)', fontsize=12)
        ax.set_title('Speed vs Position', fontsize=14, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = self.plots_dir / 'train_trajectories.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved: {plot_path}")
        plt.close()
    
    def plot_features(self, features_df):
        """Plot feature distributions and correlations"""
        fig, axes = plt.subplots(3, 3, figsize=(16, 14))
        axes = axes.flatten()
        
        features_to_plot = [
            ('last_speed', 'Last Sensor Speed (m/s)', '#3498db'),
            ('train_length', 'Train Length (m)', '#e74c3c'),
            ('distance_remaining', 'Distance Remaining (m)', '#2ecc71'),
            ('speed_change', 'Speed Change (m/s)', '#f39c12'),
            ('time_01', 'Time Between Sensors 0-1 (s)', '#9b59b6'),
            ('time_12', 'Time Between Sensors 1-2 (s)', '#1abc9c'),
            ('avg_speed_01', 'Avg Speed 0-1 (m/s)', '#34495e'),
            ('avg_speed_12', 'Avg Speed 1-2 (m/s)', '#e67e22'),
        ]
        
        for i, (feature, title, color) in enumerate(features_to_plot):
            ax = axes[i]
            ax.hist(features_df[feature], bins=30, color=color, alpha=0.7, edgecolor='black')
            ax.set_xlabel(title, fontsize=11)
            ax.set_ylabel('Frequency', fontsize=11)
            ax.set_title(f'{title}\nMean: {features_df[feature].mean():.2f}, Std: {features_df[feature].std():.2f}',
                        fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
        
        ax = axes[8]
        ax.hist(features_df['eta_actual'], bins=30, alpha=0.6, label='ETA', color='blue', edgecolor='black')
        ax.hist(features_df['etd_actual'], bins=30, alpha=0.6, label='ETD', color='red', edgecolor='black')
        ax.set_xlabel('Time (seconds)', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title('Target Variables: ETA and ETD', fontsize=11, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plot_path = self.plots_dir / 'feature_distributions.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved: {plot_path}")
        plt.close()
        
        fig, axes = plt.subplots(2, 4, figsize=(18, 10))
        axes = axes.flatten()
        
        features = ['last_speed', 'train_length', 'distance_remaining', 'speed_change',
                   'time_01', 'time_12', 'avg_speed_01', 'avg_speed_12']
        
        for i, feature in enumerate(features):
            ax = axes[i]
            ax.scatter(features_df[feature], features_df['eta_actual'], 
                      alpha=0.4, s=10, color='blue')
            
            z = np.polyfit(features_df[feature], features_df['eta_actual'], 1)
            p = np.poly1d(z)
            x_line = np.linspace(features_df[feature].min(), features_df[feature].max(), 100)
            ax.plot(x_line, p(x_line), "b-", linewidth=2, alpha=0.8)
            
            corr = features_df[feature].corr(features_df['eta_actual'])
            
            ax.set_xlabel(feature.replace('_', ' ').title(), fontsize=10)
            ax.set_ylabel('ETA (seconds)', fontsize=10)
            ax.set_title(f'{feature.replace("_", " ").title()}\nCorrelation: {corr:.3f}', 
                        fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = self.plots_dir / 'feature_correlations.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved: {plot_path}")
        plt.close()
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        ax = axes[0]
        ax.scatter(features_df['eta_actual'], features_df['eta_physics'], 
                  alpha=0.5, s=20, color='blue')
        
        min_val = min(features_df['eta_actual'].min(), features_df['eta_physics'].min())
        max_val = max(features_df['eta_actual'].max(), features_df['eta_physics'].max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect prediction')
        
        physics_error = np.mean(np.abs(features_df['eta_actual'] - features_df['eta_physics']))
        ax.set_xlabel('Actual ETA (seconds)', fontsize=12)
        ax.set_ylabel('Physics Prediction (seconds)', fontsize=12)
        ax.set_title(f'ETA: Physics Baseline\nMAE = {physics_error:.3f}s', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        ax = axes[1]
        ax.scatter(features_df['etd_actual'], features_df['etd_physics'], 
                  alpha=0.5, s=20, color='red')
        
        min_val = min(features_df['etd_actual'].min(), features_df['etd_physics'].min())
        max_val = max(features_df['etd_actual'].max(), features_df['etd_physics'].max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect prediction')
        
        physics_error = np.mean(np.abs(features_df['etd_actual'] - features_df['etd_physics']))
        ax.set_xlabel('Actual ETD (seconds)', fontsize=12)
        ax.set_ylabel('Physics Prediction (seconds)', fontsize=12)
        ax.set_title(f'ETD: Physics Baseline\nMAE = {physics_error:.3f}s', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = self.plots_dir / 'physics_comparison.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved: {plot_path}")
        plt.close()
    
    def visualize(self, trajectory_df, features_df):
        """Create all visualizations"""
        Logger.section("Creating visualizations")
        self.plot_trajectories(trajectory_df)
        self.plot_features(features_df)
    
    def prepare(self, n_samples=None):
        """Run complete data preparation pipeline"""
        if n_samples is None:
            n_samples = self.config['training']['n_samples']
        
        trajectory_df = self.generate_trajectories(n_samples)
        if trajectory_df is None:
            return None
        
        features_df = self.extract_features(trajectory_df)
        if features_df is None:
            return None
        
        self.visualize(trajectory_df, features_df)
        
        return features_df


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare ML training data')
    parser.add_argument('--samples', type=int, help='Number of samples to generate')
    parser.add_argument('--config', default='ml/config.yaml', help='Config file path')
    args = parser.parse_args()
    
    prep = Data(args.config)
    prep.prepare(args.samples)