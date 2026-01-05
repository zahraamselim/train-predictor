"""
Collect timing data from SUMO simulation
Run: python -m thresholds.collector
"""
import traci
import pandas as pd
import yaml
from pathlib import Path
from utils.logger import Logger


class DataCollector:
    def __init__(self, config_path='thresholds/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.data_dir = Path('outputs/data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.clearance_data = []
        self.travel_data = []
        
        self.vehicles_at_crossing = {}
        self.travel_start = {}
        
        self.check_network_files()
    
    def check_network_files(self):
        """Check if required network files exist"""
        required = ['thresholds.sumocfg', 'thresholds.net.xml', 'thresholds.rou.xml']
        missing = [f for f in required if not Path(f).exists()]
        
        if missing:
            Logger.log(f"ERROR: Missing network files: {', '.join(missing)}")
            Logger.log("Run: make th-network or python -m thresholds.network")
            raise FileNotFoundError(f"Missing files: {missing}")
    
    def run(self, duration=None):
        """Collect timing data"""
        if duration is None:
            duration = self.config['data_collection']['duration']
        
        Logger.section(f"Collecting data for {duration}s")
        
        traci.start(['sumo', '-c', 'thresholds.sumocfg', '--no-step-log', '--no-warnings'])
        
        try:
            step = 0
            max_steps = int(duration / 0.1)
            
            while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
                traci.simulationStep()
                t = traci.simulation.getTime()
                
                for vid in traci.vehicle.getIDList():
                    if 'train' in vid.lower():
                        continue
                    
                    try:
                        x, y = traci.vehicle.getPosition(vid)
                        speed = traci.vehicle.getSpeed(vid)
                    except:
                        continue
                    
                    self._track_vehicle(vid, x, y, speed, t)
                
                step += 1
                if step % 600 == 0:
                    Logger.log(f"Step {step}/{max_steps}: {len(self.clearance_data)} clearances, "
                             f"{len(self.travel_data)} travels")
        
        finally:
            traci.close()
            self._save_data()
    
    def _track_vehicle(self, vid, x, y, speed, t):
        """Track vehicle clearance and travel times"""
        at_crossing = abs(x) < 150
        
        if at_crossing and vid not in self.vehicles_at_crossing:
            self.vehicles_at_crossing[vid] = {'time': t, 'speed': speed}
        
        elif not at_crossing and vid in self.vehicles_at_crossing:
            entry = self.vehicles_at_crossing.pop(vid)
            clearance = t - entry['time']
            
            if 0.5 < clearance < 30:
                self.clearance_data.append({
                    'vehicle_id': vid,
                    'clearance_time': clearance,
                    'speed': entry['speed']
                })
        
        for int_name, int_x in [('west', -300), ('east', 300)]:
            key = f"{vid}_{int_name}"
            
            if abs(x - int_x) < 50 and key not in self.travel_start:
                self.travel_start[key] = t
            
            elif key in self.travel_start and abs(x) < 50:
                travel = t - self.travel_start.pop(key)
                
                if 1 < travel < 60:
                    self.travel_data.append({
                        'vehicle_id': vid,
                        'travel_time': travel
                    })
    
    def _save_data(self):
        """Save collected data"""
        Logger.log("Saving data")
        
        pd.DataFrame(self.clearance_data).to_csv(
            self.data_dir / 'clearances.csv', index=False)
        Logger.log(f"{len(self.clearance_data)} clearance samples")
        
        pd.DataFrame(self.travel_data).to_csv(
            self.data_dir / 'travels.csv', index=False)
        Logger.log(f"{len(self.travel_data)} travel samples")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect threshold data')
    parser.add_argument('--duration', type=int, help='Simulation duration')
    parser.add_argument('--config', default='thresholds/config.yaml', help='Config file')
    args = parser.parse_args()
    
    collector = DataCollector(args.config)
    collector.run(args.duration)