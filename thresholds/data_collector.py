"""
Threshold data collector
Run: python -m thresholds.data_collector
"""
import traci
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from utils.logger import Logger


class ThresholdDataCollector:
    def __init__(self, config_path='config/thresholds.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.data_dir = Path('outputs/data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.crossing_pos = 0.0
        self.intersection_west = -300.0
        self.intersection_east = 300.0
        
        self.clearance_data = []
        self.train_data = []
        self.travel_data = []
        
        self.vehicles_at_crossing = {}
        self.trains = {}
        self.travel_start = {}
    
    def run(self, duration=None):
        """Execute data collection simulation"""
        if duration is None:
            duration = self.config['data_collection']['duration']
        
        Logger.section(f"Collecting threshold data ({duration}s simulation)")
        
        traci.start([
            'sumo',
            '-c', 'thresholds.sumocfg',
            '--start',
            '--quit-on-end',
            '--no-step-log',
            '--no-warnings'
        ])
        
        try:
            step = 0
            step_length = self.config['data_collection']['step_length']
            max_steps = int(duration / step_length)
            
            while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
                traci.simulationStep()
                t = traci.simulation.getTime()
                
                self._track_vehicles(t)
                self._track_trains(t)
                
                step += 1
                if step % 600 == 0:
                    Logger.log(f"Progress: {t:.0f}s ({step/max_steps*100:.0f}%) - "
                             f"Clearances: {len(self.clearance_data)}, "
                             f"Trains: {len(self.train_data)}, "
                             f"Travels: {len(self.travel_data)}")
        
        except KeyboardInterrupt:
            Logger.log("Interrupted by user")
        
        finally:
            traci.close()
            self._save_data()
    
    def _track_vehicles(self, t):
        """Track vehicle clearance and travel times"""
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            try:
                x, y = traci.vehicle.getPosition(vid)
                speed = traci.vehicle.getSpeed(vid)
            except:
                continue
            
            is_at_crossing = abs(y - self.crossing_pos) < 150
            
            if is_at_crossing:
                if vid not in self.vehicles_at_crossing:
                    self.vehicles_at_crossing[vid] = {
                        'enter_time': t,
                        'enter_speed': speed,
                        'enter_pos': y
                    }
            elif vid in self.vehicles_at_crossing:
                entry = self.vehicles_at_crossing.pop(vid)
                clearance_time = t - entry['enter_time']
                
                if 0.5 < clearance_time < 30:
                    distance = abs(y - entry['enter_pos'])
                    self.clearance_data.append({
                        'vehicle_id': vid,
                        'clearance_time': clearance_time,
                        'enter_speed': entry['enter_speed'],
                        'exit_speed': speed,
                        'distance': distance
                    })
            
            for int_name, int_pos in [('west', self.intersection_west), ('east', self.intersection_east)]:
                key = f"{vid}_{int_name}"
                
                if abs(x - int_pos) < 50 and key not in self.travel_start:
                    self.travel_start[key] = {
                        'start_time': t,
                        'start_x': x,
                        'intersection': int_name
                    }
                
                elif key in self.travel_start:
                    travel_info = self.travel_start[key]
                    
                    if abs(y - self.crossing_pos) < 50:
                        travel_time = t - travel_info['start_time']
                        
                        if 1.0 < travel_time < 60:
                            distance = abs(x - travel_info['start_x'])
                            
                            self.travel_data.append({
                                'vehicle_id': vid,
                                'intersection': int_name,
                                'travel_time': travel_time,
                                'distance': distance,
                                'avg_speed': distance / travel_time if travel_time > 0 else 0
                            })
                        
                        del self.travel_start[key]
    
    def _track_trains(self, t):
        """Track train passage times and speeds"""
        for tid in traci.vehicle.getIDList():
            if 'train' not in tid.lower():
                continue
            
            try:
                x, y = traci.vehicle.getPosition(tid)
                speed = traci.vehicle.getSpeed(tid)
                length = traci.vehicle.getLength(tid)
            except:
                continue
            
            if tid not in self.trains:
                self.trains[tid] = {
                    'speeds': [],
                    'positions': [],
                    'times': [],
                    'length': length
                }
            
            train = self.trains[tid]
            train['speeds'].append(speed)
            train['positions'].append(y)
            train['times'].append(t)
            
            front_y = y
            rear_y = y - length
            
            if front_y >= self.crossing_pos and 'arrival' not in train:
                train['arrival'] = t
            
            if rear_y >= self.crossing_pos and 'departure' not in train and 'arrival' in train:
                train['departure'] = t
                
                self.train_data.append({
                    'train_id': tid,
                    'passage_time': train['departure'] - train['arrival'],
                    'avg_speed': float(np.mean(train['speeds'])),
                    'min_speed': float(np.min(train['speeds'])),
                    'max_speed': float(np.max(train['speeds'])),
                    'speed_variance': float(np.var(train['speeds'])),
                    'length': length,
                    'arrival_time': train['arrival']
                })
    
    def _save_data(self):
        """Save collected data to CSV files"""
        Logger.section("Saving collected data")
        
        if self.clearance_data:
            df = pd.DataFrame(self.clearance_data)
            output_path = self.data_dir / 'gate_clearance.csv'
            df.to_csv(output_path, index=False)
            Logger.log(f"Gate clearance samples: {len(df)}")
            Logger.log(f"  Mean: {df['clearance_time'].mean():.2f}s")
            Logger.log(f"  95th percentile: {df['clearance_time'].quantile(0.95):.2f}s")
            Logger.log(f"  Max: {df['clearance_time'].max():.2f}s")
        else:
            Logger.log("No clearance data collected")
            pd.DataFrame(columns=['vehicle_id', 'clearance_time', 'enter_speed', 
                                'exit_speed', 'distance']).to_csv(
                self.data_dir / 'gate_clearance.csv', index=False)
        
        if self.train_data:
            df = pd.DataFrame(self.train_data)
            output_path = self.data_dir / 'train_passages.csv'
            df.to_csv(output_path, index=False)
            Logger.log(f"Train passages: {len(df)}")
            Logger.log(f"  Passage time mean: {df['passage_time'].mean():.2f}s")
            Logger.log(f"  Speed range: {df['min_speed'].min():.1f} - {df['max_speed'].max():.1f} m/s")
        else:
            Logger.log("No train data collected")
            pd.DataFrame(columns=['train_id', 'passage_time', 'avg_speed', 'min_speed', 
                                'max_speed', 'speed_variance', 'length', 'arrival_time']).to_csv(
                self.data_dir / 'train_passages.csv', index=False)
        
        if self.travel_data:
            df = pd.DataFrame(self.travel_data)
            output_path = self.data_dir / 'vehicle_travels.csv'
            df.to_csv(output_path, index=False)
            Logger.log(f"Travel time samples: {len(df)}")
            Logger.log(f"  Mean: {df['travel_time'].mean():.2f}s")
            Logger.log(f"  95th percentile: {df['travel_time'].quantile(0.95):.2f}s")
        else:
            Logger.log("No travel data collected")
            pd.DataFrame(columns=['vehicle_id', 'intersection', 'travel_time', 
                                'distance', 'avg_speed']).to_csv(
                self.data_dir / 'vehicle_travels.csv', index=False)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect threshold data')
    parser.add_argument('--duration', type=int, help='Simulation duration in seconds')
    parser.add_argument('--config', default='config/thresholds.yaml', help='Config file path')
    args = parser.parse_args()
    
    collector = ThresholdDataCollector(args.config)
    collector.run(args.duration)