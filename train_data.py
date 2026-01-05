"""
Generate ML training data from SUMO simulations
Matches poster: 2000 train runs, 14 features
Usage: python train_data.py [--samples N]
"""

import subprocess
import pandas as pd
import numpy as np
import yaml
import matplotlib.pyplot as plt
from pathlib import Path
import xml.etree.ElementTree as ET
from utils.logger import Logger


class TrainingDataGenerator:
    def __init__(self, config_path='config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.output_dir = Path('outputs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.plots_dir = self.output_dir / 'plots'
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        
        self.sensors = self.config['sensors']
        self.check_sumo()
    
    def check_sumo(self):
        """Verify SUMO is installed"""
        try:
            subprocess.run(['sumo', '--version'], capture_output=True, timeout=5)
        except:
            Logger.log("ERROR: SUMO not found. Install: sudo apt-get install sumo sumo-tools")
            raise
    
    def generate_network(self):
        """Create linear track for training"""
        Logger.section("Generating SUMO network")
        
        nodes = f"""<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="start" x="{self.config['network']['start_x']}" y="0"/>
    <node id="end" x="{self.config['network']['end_x']}" y="0"/>
</nodes>"""
        
        edges = f"""<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <edge id="track" from="start" to="end" priority="1" numLanes="1" 
          speed="{self.config['network']['max_speed']}"/>
</edges>"""
        
        Path('training.nod.xml').write_text(nodes)
        Path('training.edg.xml').write_text(edges)
        
        result = subprocess.run([
            'netconvert',
            '--node-files=training.nod.xml',
            '--edge-files=training.edg.xml',
            '--output-file=training.net.xml',
            '--no-turnarounds',
            '--no-warnings'
        ], capture_output=True)
        
        if result.returncode != 0:
            Logger.log("Network generation failed")
            return False
        
        Logger.log("Network created: training.net.xml")
        return True
    
    def generate_train_params(self, n_samples):
        """Generate realistic train parameters"""
        np.random.seed(self.config['training']['random_seed'])
        scenarios = self.config['training']['scenarios']
        
        params = []
        for _ in range(n_samples):
            scenario_name = np.random.choice(list(scenarios.keys()))
            s = scenarios[scenario_name]
            
            params.append({
                'depart_speed': np.random.uniform(*s['speed']),
                'accel': np.random.uniform(*s['accel']),
                'decel': np.random.uniform(*s['decel']),
                'length': np.random.choice(self.config['training']['train_lengths']),
                'speed_factor': 1.0,
                'scenario': scenario_name
            })
        
        return params
    
    def create_route_file(self, train_params, run_id):
        """Create SUMO route file for one train"""
        p = train_params
        
        routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="train_{run_id}" length="{p['length']}" 
           maxSpeed="{self.config['network']['max_speed']}" 
           accel="{p['accel']}" decel="{p['decel']}" 
           speedFactor="{p['speed_factor']}" speedDev="0" color="1,0,0"/>
    <route id="route_{run_id}" edges="track"/>
    <vehicle id="train_{run_id}" type="train_{run_id}" route="route_{run_id}" 
             depart="0" departSpeed="{p['depart_speed']}"/>
</routes>"""
        
        route_file = f'temp_route_{run_id}.rou.xml'
        Path(route_file).write_text(routes)
        return route_file
    
    def create_config_file(self, route_file, run_id):
        """Create SUMO configuration file"""
        config = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="training.net.xml"/>
        <route-files value="{route_file}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{self.config['training']['sim_duration']}"/>
        <step-length value="0.1"/>
    </time>
    <output>
        <fcd-output value="temp_fcd_{run_id}.xml"/>
    </output>
    <processing>
        <time-to-teleport value="-1"/>
    </processing>
</configuration>"""
        
        config_file = f'temp_config_{run_id}.sumocfg'
        Path(config_file).write_text(config)
        return config_file
    
    def run_simulation(self, train_params, run_id):
        """Run SUMO simulation for one train"""
        route_file = self.create_route_file(train_params, run_id)
        config_file = self.create_config_file(route_file, run_id)
        
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
        
        data = self.parse_fcd(fcd_file, run_id, train_params)
        Path(fcd_file).unlink(missing_ok=True)
        
        return data
    
    def parse_fcd(self, fcd_file, run_id, train_params):
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
                        'length': train_params['length'],
                        'run_id': run_id,
                        'scenario': train_params['scenario']
                    })
        
        return pd.DataFrame(data) if data else None
    
    def extract_features(self, run_df):
        """Extract 14 features from trajectory (poster version)"""
        run_df = run_df.sort_values('time')
        train_length = run_df['length'].iloc[0]
        scenario = run_df['scenario'].iloc[0]
        
        # Find sensor trigger times
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
        
        # Get sensor values
        s0_time = triggers['s0']['time']
        s1_time = triggers['s1']['time']
        s2_time = triggers['s2']['time']
        
        s0_speed = triggers['s0']['speed']
        s1_speed = triggers['s1']['speed']
        s2_speed = triggers['s2']['speed']
        
        s0_pos = triggers['s0']['pos']
        s1_pos = triggers['s1']['pos']
        s2_pos = triggers['s2']['pos']
        
        crossing_time = triggers['crossing']['time']
        crossing_pos = triggers['crossing']['pos']
        
        # Find rear crossing time
        rear_crossing_mask = run_df['pos'] >= (crossing_pos + train_length)
        if not rear_crossing_mask.any():
            return None
        rear_crossing_time = run_df.loc[rear_crossing_mask.idxmax(), 'time']
        
        # Calculate timing features
        time_01 = s1_time - s0_time
        time_12 = s2_time - s1_time
        
        if time_01 <= 0 or time_12 <= 0:
            return None
        
        # Calculate speed features
        avg_speed_01 = (s1_pos - s0_pos) / time_01
        avg_speed_12 = (s2_pos - s1_pos) / time_12
        speed_change = s2_speed - s0_speed
        
        # Calculate acceleration features
        accel_01 = (s1_speed - s0_speed) / time_01
        accel_12 = (s2_speed - s1_speed) / time_12
        accel_trend = accel_12 - accel_01
        
        # Predict crossing speed
        distance_remaining = crossing_pos - s2_pos
        time_to_crossing = distance_remaining / s2_speed if s2_speed > 0 else 0
        predicted_crossing_speed = s2_speed + (accel_12 * time_to_crossing)
        predicted_crossing_speed = max(5.0, min(50.0, predicted_crossing_speed))
        
        # Calculate actual ETA and ETD
        eta_actual = crossing_time - s2_time
        etd_actual = rear_crossing_time - s2_time
        
        # Calculate physics baseline
        eta_physics = distance_remaining / s2_speed if s2_speed > 0 else 0
        etd_physics = (distance_remaining + train_length) / s2_speed if s2_speed > 0 else 0
        
        # Return 14 features (poster version)
        return {
            'distance_remaining': distance_remaining,
            'train_length': train_length,
            'last_speed': s2_speed,
            'speed_change': speed_change,
            'time_01': time_01,
            'time_12': time_12,
            'avg_speed_01': avg_speed_01,
            'avg_speed_12': avg_speed_12,
            'speed_0': s0_speed,
            'speed_1': s1_speed,
            'accel_01': accel_01,
            'accel_12': accel_12,
            'accel_trend': accel_trend,
            'predicted_crossing_speed': predicted_crossing_speed,
            'eta_actual': eta_actual,
            'etd_actual': etd_actual,
            'eta_physics': eta_physics,
            'etd_physics': etd_physics,
            'scenario': scenario,
            'run_id': run_df['run_id'].iloc[0]
        }
    
    def plot_results(self, trajectories, features):
        """Create visualization (poster Fig 5, 9-12)"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Sample trajectories
        sample_runs = np.random.choice(trajectories['run_id'].unique(), min(5, len(trajectories['run_id'].unique())), replace=False)
        
        ax = axes[0, 0]
        for run_id in sample_runs:
            run_df = trajectories[trajectories['run_id'] == run_id]
            ax.plot(run_df['time'], run_df['pos'], linewidth=2, alpha=0.7)
        
        for name, pos in self.sensors.items():
            style = '-' if name == 'crossing' else '--'
            color = 'red' if name == 'crossing' else 'gray'
            ax.axhline(pos, color=color, linestyle=style, linewidth=2 if name == 'crossing' else 1)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Position (m)')
        ax.set_title('Sample Train Trajectories')
        ax.grid(True, alpha=0.3)
        
        # Feature distributions
        ax = axes[0, 1]
        ax.hist(features['last_speed'], bins=30, edgecolor='black', alpha=0.7, color='blue')
        ax.set_xlabel('Last Sensor Speed (m/s)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Speed Distribution (mean={features["last_speed"].mean():.1f})')
        ax.grid(True, alpha=0.3, axis='y')
        
        # ETA vs prediction
        ax = axes[1, 0]
        ax.scatter(features['eta_actual'], features['eta_physics'], alpha=0.5, s=20, color='red')
        min_val = min(features['eta_actual'].min(), features['eta_physics'].min())
        max_val = max(features['eta_actual'].max(), features['eta_physics'].max())
        ax.plot([min_val, max_val], [min_val, max_val], 'k--', lw=2)
        
        physics_error = np.mean(np.abs(features['eta_actual'] - features['eta_physics']))
        ax.set_xlabel('Actual ETA (s)')
        ax.set_ylabel('Physics Prediction (s)')
        ax.set_title(f'Physics Baseline (MAE={physics_error:.3f}s)')
        ax.grid(True, alpha=0.3)
        
        # Target distribution
        ax = axes[1, 1]
        ax.hist(features['eta_actual'], bins=30, alpha=0.6, label='ETA', color='blue', edgecolor='black')
        ax.hist(features['etd_actual'], bins=30, alpha=0.6, label='ETD', color='red', edgecolor='black')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency')
        ax.set_title('Target Variables')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plot_path = self.plots_dir / 'training_data.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved: {plot_path}")
        plt.close()
    
    def generate(self, n_samples=None):
        """Run complete data generation pipeline"""
        if n_samples is None:
            n_samples = self.config['training']['n_samples']
        
        Logger.section(f"Generating {n_samples} training samples")
        
        if not self.generate_network():
            return False
        
        train_params = self.generate_train_params(n_samples)
        all_trajectories = []
        all_features = []
        successful = 0
        
        for i, params in enumerate(train_params):
            trajectory_df = self.run_simulation(params, i)
            
            if trajectory_df is not None and len(trajectory_df) > 10:
                all_trajectories.append(trajectory_df)
                
                features = self.extract_features(trajectory_df)
                if features is not None:
                    all_features.append(features)
                    successful += 1
            
            if (i + 1) % 100 == 0:
                Logger.log(f"Progress: {successful}/{i+1} ({successful/(i+1)*100:.1f}%)")
        
        if not all_trajectories or not all_features:
            Logger.log("No successful simulations")
            return False
        
        # Save results
        trajectories = pd.concat(all_trajectories, ignore_index=True)
        trajectories.to_csv(self.output_dir / 'trajectories.csv', index=False)
        
        features = pd.DataFrame(all_features)
        features.to_csv(self.output_dir / 'features.csv', index=False)
        
        Logger.log(f"\nGenerated {successful} samples")
        Logger.log(f"ETA mean: {features['eta_actual'].mean():.2f}s")
        Logger.log(f"ETD mean: {features['etd_actual'].mean():.2f}s")
        Logger.log(f"Physics baseline ETA error: {np.mean(np.abs(features['eta_actual'] - features['eta_physics'])):.3f}s")
        Logger.log(f"Physics baseline ETD error: {np.mean(np.abs(features['etd_actual'] - features['etd_physics'])):.3f}s")
        Logger.log(f"\nSaved:")
        Logger.log(f"  {self.output_dir / 'trajectories.csv'}")
        Logger.log(f"  {self.output_dir / 'features.csv'}")
        
        self.plot_results(trajectories, features)
        
        return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ML training data')
    parser.add_argument('--samples', type=int, help='Number of samples to generate')
    parser.add_argument('--config', default='config.yaml', help='Config file path')
    args = parser.parse_args()
    
    generator = TrainingDataGenerator(args.config)
    generator.generate(args.samples)