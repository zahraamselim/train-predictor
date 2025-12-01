"""
Data Collector
Collects training data from SUMO simulation
"""
import traci
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


class DataCollector:
    def __init__(self, output_dir="outputs/data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.crossing_w = -200.0
        self.crossing_e = 200.0
        self.intersections = {
            'west': -200.0,
            'east': 200.0
        }
        
        self.clearance_data = []
        self.train_data = []
        self.travel_data = []
        
        self.vehicles_at_crossing = {}
        self.trains = {}
        self.vehicle_travel_start = {}
    
    def start_simulation(self):
        """Start SUMO simulation"""
        traci.start(['sumo', '-c', 'sumo/simulation.sumocfg', '--start', '--quit-on-end'])
    
    def run(self, duration=3600):
        """Run data collection"""
        self.start_simulation()
        
        step = 0
        print(f"[{self._timestamp()}] Starting data collection")
        print(f"Duration: {duration}s")
        
        try:
            while traci.simulation.getMinExpectedNumber() > 0 and step < duration:
                traci.simulationStep()
                t = traci.simulation.getTime()
                
                self._track_vehicles(t)
                self._track_trains(t)
                
                step += 1
                
                if step % 600 == 0:
                    print(f"[{self._timestamp()}] Step {step}s")
        
        except KeyboardInterrupt:
            print(f"[{self._timestamp()}] Interrupted")
        
        finally:
            traci.close()
            self._save_data()
    
    def _track_vehicles(self, t):
        """Track vehicle clearance times and travel times"""
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            pos = traci.vehicle.getPosition(vid)[0]
            speed = traci.vehicle.getSpeed(vid)
            
            # Track clearance time at west crossing
            if abs(pos - self.crossing_w) < 30:
                if vid not in self.vehicles_at_crossing:
                    self.vehicles_at_crossing[vid] = {
                        'enter_time': t,
                        'enter_speed': speed
                    }
            elif abs(pos - self.crossing_w) > 30 and vid in self.vehicles_at_crossing:
                entry = self.vehicles_at_crossing.pop(vid)
                self.clearance_data.append({
                    'vehicle_id': vid,
                    'clearance_time': t - entry['enter_time'],
                    'avg_speed': (entry['enter_speed'] + speed) / 2
                })
            
            # Track travel time from intersections to crossing
            for inter_name, inter_pos in self.intersections.items():
                key = f"{vid}_{inter_name}"
                
                if abs(pos - inter_pos) < 10 and key not in self.vehicle_travel_start:
                    self.vehicle_travel_start[key] = {
                        'vehicle_id': vid,
                        'intersection': inter_name,
                        'start_time': t,
                        'distance': abs(self.crossing_w - inter_pos)
                    }
                
                elif key in self.vehicle_travel_start and abs(pos - self.crossing_w) < 30:
                    travel = self.vehicle_travel_start.pop(key)
                    travel['travel_time'] = t - travel['start_time']
                    travel['avg_speed'] = travel['distance'] / travel['travel_time']
                    self.travel_data.append(travel)
    
    def _track_trains(self, t):
        """Track train passage through crossings"""
        for tid in traci.vehicle.getIDList():
            if 'train' not in tid.lower():
                continue
            
            pos = traci.vehicle.getPosition(tid)[0]
            speed = traci.vehicle.getSpeed(tid)
            length = traci.vehicle.getLength(tid)
            
            if tid not in self.trains:
                self.trains[tid] = {
                    'speeds': [],
                    'positions': [],
                    'times': [],
                    'length': length
                }
            
            train = self.trains[tid]
            train['speeds'].append(speed)
            train['positions'].append(pos)
            train['times'].append(t)
            
            # Train front reaches west crossing
            if pos >= self.crossing_w and 'arrival_w' not in train:
                train['arrival_w'] = t
            
            # Train rear clears west crossing
            rear_pos = pos - length
            if rear_pos > self.crossing_w and 'departure_w' not in train:
                train['departure_w'] = t
            
            # Train reaches east crossing
            if pos >= self.crossing_e and 'arrival_e' not in train:
                train['arrival_e'] = t
            
            # Train clears east crossing
            if rear_pos > self.crossing_e and 'departure_e' not in train:
                train['departure_e'] = t
                
                self.train_data.append({
                    'train_id': tid,
                    'passage_time_w': train['departure_w'] - train['arrival_w'],
                    'passage_time_e': train['departure_e'] - train['arrival_e'],
                    'avg_speed': np.mean(train['speeds']),
                    'min_speed': np.min(train['speeds']),
                    'max_speed': np.max(train['speeds']),
                    'length': length
                })
    
    def _save_data(self):
        """Save collected data to CSV files"""
        if self.clearance_data:
            df = pd.DataFrame(self.clearance_data)
            df.to_csv(self.output_dir / 'gate_clearance.csv', index=False)
            print(f"[{self._timestamp()}] Saved {len(df)} clearance samples")
            print(f"  Mean: {df['clearance_time'].mean():.2f}s")
            print(f"  95th percentile: {df['clearance_time'].quantile(0.95):.2f}s")
        
        if self.train_data:
            df = pd.DataFrame(self.train_data)
            df.to_csv(self.output_dir / 'train_passages.csv', index=False)
            print(f"[{self._timestamp()}] Saved {len(df)} train passages")
            print(f"  Mean passage time: {df['passage_time_w'].mean():.2f}s")
        
        if self.travel_data:
            df = pd.DataFrame(self.travel_data)
            df.to_csv(self.output_dir / 'vehicle_travels.csv', index=False)
            print(f"[{self._timestamp()}] Saved {len(df)} travel samples")
            for inter in self.intersections.keys():
                inter_df = df[df['intersection'] == inter]
                if len(inter_df) > 0:
                    print(f"  {inter}: mean={inter_df['travel_time'].mean():.2f}s")
    
    def _timestamp(self):
        """Get current timestamp"""
        return datetime.now().strftime("%H:%M:%S")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--duration', type=int, default=3600)
    args = parser.parse_args()
    
    collector = DataCollector()
    collector.run(args.duration)