"""
Metrics data collector with integrated control system
Run: python -m metrics.data_collector
"""
import traci
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from utils.logger import Logger


class MetricsDataCollector:
    def __init__(self, config_path='config/simulation.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.output_dir = Path('outputs/metrics')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        thresholds_path = Path('outputs/results/thresholds.yaml')
        if thresholds_path.exists():
            with open(thresholds_path) as f:
                self.thresholds = yaml.safe_load(f)
        else:
            Logger.log("WARNING: No calculated thresholds found, using defaults")
            self.thresholds = {
                'closure_before_eta': 10.0,
                'opening_after_etd': 3.0,
                'notification_time': 30.0,
                'sensor_positions': [1500.0, 900.0, 450.0],
                'engine_off_threshold': 5.0,
                'max_train_speed': 50.0
            }
        
        metrics_cfg = self.config.get('metrics', {})
        self.fuel_rate_driving = metrics_cfg.get('fuel_rate_driving', 0.08)
        self.fuel_rate_idling = metrics_cfg.get('fuel_rate_idling', 0.01)
        self.fuel_rate_off = metrics_cfg.get('fuel_rate_off', 0.0)
        self.co2_per_liter = metrics_cfg.get('co2_per_liter', 2.31)
        
        net_cfg = self.config.get('network', {})
        self.crossing_w = net_cfg.get('crossing_w', -200.0)
        self.crossing_e = net_cfg.get('crossing_e', 200.0)
        self.intersections = net_cfg.get('intersections', {'west': -200.0, 'east': 200.0})
        
        self.sensor_positions = [self.crossing_w - s for s in self.thresholds['sensor_positions']]
        
        self.trains = {}
        self.gates_closed = False
        self.intersections_notified = False
        self.vehicles_engines_off = set()
        
        self.vehicle_data = {}
        self.vehicle_wait_start = {}
        self.wait_events = []
        self.queue_snapshots = []
        self.comfort_scores = []
        self.engine_off_count = 0
        self.step_count = 0
    
    def run(self, duration=None, gui=False):
        """Execute metrics collection with control system"""
        if duration is None:
            duration = self.config.get('simulation', {}).get('duration', 3600)
        
        Logger.section(f"Collecting metrics data ({duration}s simulation)")
        Logger.log(f"Closure threshold: {self.thresholds['closure_before_eta']:.2f}s")
        Logger.log(f"Opening threshold: {self.thresholds['opening_after_etd']:.2f}s")
        Logger.log(f"Engine off threshold: {self.thresholds['engine_off_threshold']:.2f}s")
        
        sumo_cmd = ['sumo-gui' if gui else 'sumo']
        sumo_cmd.extend([
            '-c', 'sumo/metrics/metrics.sumocfg',
            '--start',
            '--quit-on-end',
            '--no-step-log',
            '--no-warnings'
        ])
        
        traci.start(sumo_cmd)
        
        try:
            step = 0
            step_length = self.config.get('simulation', {}).get('step_length', 0.1)
            max_steps = int(duration / step_length)
            
            while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
                traci.simulationStep()
                t = traci.simulation.getTime()
                
                self._track_trains(t)
                self._control_gates(t)
                self._control_intersections(t)
                self._control_vehicle_engines(t)
                self._track_vehicles(t, step_length)
                
                if step % 100 == 0:
                    self._track_queue_comfort(t)
                
                step += 1
                self.step_count = step
                
                if step % 600 == 0:
                    Logger.log(f"Progress: {t:.0f}s ({step/max_steps*100:.0f}%) - "
                             f"Gates: {'closed' if self.gates_closed else 'open'}, "
                             f"Vehicles: {len(self.vehicle_data)}, "
                             f"Engines off: {len(self.vehicles_engines_off)}")
        
        except KeyboardInterrupt:
            Logger.log("Interrupted by user")
        
        finally:
            traci.close()
            self._save_data()
    
    def _track_trains(self, t):
        """Track train positions and calculate ETAs"""
        for tid in traci.vehicle.getIDList():
            if 'train' not in tid.lower():
                continue
            
            try:
                pos = traci.vehicle.getPosition(tid)[0]
                speed = traci.vehicle.getSpeed(tid)
            except:
                continue
            
            if tid not in self.trains:
                self.trains[tid] = {
                    'sensor_triggers': {},
                    'sensor_speeds': {},
                    'eta': None,
                    'eta_calculated_at': None,
                    'passed_w': False,
                    'passed_e': False
                }
            
            train = self.trains[tid]
            
            for i, sensor_x in enumerate(self.sensor_positions):
                if i not in train['sensor_triggers'] and pos >= sensor_x:
                    train['sensor_triggers'][i] = t
                    train['sensor_speeds'][i] = speed
                    
                    if i == 0:
                        Logger.log(f"Train {tid} detected at sensor 0")
            
            if len(train['sensor_triggers']) == 3 and train['eta'] is None:
                train['eta'] = self._calculate_eta(train)
                train['eta_calculated_at'] = t
                Logger.log(f"Train {tid} ETA: {train['eta']:.1f}s")
            
            if pos >= self.crossing_w and not train['passed_w']:
                train['passed_w'] = True
                train['arrival_w'] = t
                Logger.log(f"Train {tid} reached west crossing")
            
            if pos >= self.crossing_e and not train['passed_e']:
                train['passed_e'] = True
                train['arrival_e'] = t
    
    def _calculate_eta(self, train):
        """Calculate ETA from sensor data"""
        triggers = train['sensor_triggers']
        speeds = train['sensor_speeds']
        
        t01 = triggers[1] - triggers[0]
        t12 = triggers[2] - triggers[1]
        
        d01 = abs(self.sensor_positions[1] - self.sensor_positions[0])
        d12 = abs(self.sensor_positions[2] - self.sensor_positions[1])
        
        v01 = d01 / t01 if t01 > 0 else speeds[1]
        v12 = d12 / t12 if t12 > 0 else speeds[2]
        
        distance = abs(self.crossing_w - self.sensor_positions[2])
        eta = distance / v12 if v12 > 0 else distance / 30.0
        
        return eta
    
    def _control_gates(self, t):
        """Control gate opening/closing"""
        for tid, train in self.trains.items():
            if train['eta'] is None:
                continue
            
            elapsed = t - train['eta_calculated_at']
            remaining = train['eta'] - elapsed
            
            if remaining <= self.thresholds['closure_before_eta'] and not self.gates_closed:
                self._close_gates()
            
            if train['passed_e'] and self.gates_closed:
                departure_time = t - train['arrival_e']
                if departure_time >= self.thresholds['opening_after_etd']:
                    self._open_gates()
    
    def _close_gates(self):
        """Close crossing gates"""
        self.gates_closed = True
        Logger.log("GATES CLOSED")
    
    def _open_gates(self):
        """Open crossing gates"""
        self.gates_closed = False
        self.intersections_notified = False
        self.vehicles_engines_off.clear()
        self.vehicle_wait_start.clear()
        Logger.log("GATES OPENED")
        if self.engine_off_count > 0:
            Logger.log(f"Vehicles with engine off during closure: {self.engine_off_count}")
            self.engine_off_count = 0
    
    def _control_intersections(self, t):
        """Control intersection notifications"""
        for tid, train in self.trains.items():
            if train['eta'] is None:
                continue
            
            elapsed = t - train['eta_calculated_at']
            remaining = train['eta'] - elapsed
            
            if remaining <= self.thresholds['notification_time'] and not self.intersections_notified:
                self.intersections_notified = True
                Logger.log("Intersections notified")
    
    def _control_vehicle_engines(self, t):
        """Control vehicle engine shutdown"""
        if not self.gates_closed:
            self.vehicle_wait_start.clear()
            return
        
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            try:
                pos = traci.vehicle.getPosition(vid)[0]
                speed = traci.vehicle.getSpeed(vid)
            except:
                continue
            
            in_queue_w = abs(pos - self.crossing_w) < 50 and speed < 0.5
            in_queue_e = abs(pos - self.crossing_e) < 50 and speed < 0.5
            is_waiting = in_queue_w or in_queue_e
            
            if is_waiting:
                if vid not in self.vehicle_wait_start:
                    self.vehicle_wait_start[vid] = t
                
                wait_time = t - self.vehicle_wait_start[vid]
                expected_remaining = self._get_expected_wait_time(t)
                
                if (wait_time >= 5.0 and 
                    expected_remaining >= self.thresholds['engine_off_threshold'] and 
                    vid not in self.vehicles_engines_off):
                    
                    self.vehicles_engines_off.add(vid)
                    self.engine_off_count += 1
                    Logger.log(f"Vehicle {vid} engine off (waited: {wait_time:.1f}s, remaining: {expected_remaining:.1f}s)")
            else:
                if vid in self.vehicle_wait_start:
                    del self.vehicle_wait_start[vid]
                if vid in self.vehicles_engines_off:
                    self.vehicles_engines_off.remove(vid)
    
    def _get_expected_wait_time(self, t):
        """Calculate expected wait time for vehicles"""
        for train in self.trains.values():
            if train['eta'] is not None and not train['passed_e']:
                elapsed = t - train['eta_calculated_at']
                remaining = train['eta'] - elapsed
                return max(0, remaining + self.thresholds['opening_after_etd'])
        return 0
    
    def _track_vehicles(self, t, dt):
        """Track individual vehicle metrics"""
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            try:
                speed = traci.vehicle.getSpeed(vid)
                pos = traci.vehicle.getPosition(vid)
                waiting = speed < 0.5
                engine_off = vid in self.vehicles_engines_off
            except:
                continue
            
            if vid not in self.vehicle_data:
                self.vehicle_data[vid] = {
                    'first_seen': t,
                    'last_seen': t,
                    'total_wait': 0,
                    'wait_start': None,
                    'total_fuel': 0,
                    'total_emissions': 0,
                    'stops': 0,
                    'engine_off_time': 0,
                    'engine_off_start': None,
                    'distance_traveled': 0,
                    'last_pos': pos,
                    'max_speed': speed,
                    'speed_sum': 0,
                    'speed_count': 0
                }
            
            veh = self.vehicle_data[vid]
            veh['last_seen'] = t
            
            if waiting and veh['wait_start'] is None:
                veh['wait_start'] = t
                veh['stops'] += 1
            elif not waiting and veh['wait_start'] is not None:
                wait_duration = t - veh['wait_start']
                veh['total_wait'] += wait_duration
                veh['wait_start'] = None
                
                self.wait_events.append({
                    'vehicle_id': vid,
                    'wait_duration': wait_duration,
                    'time': t,
                    'engine_off': engine_off
                })
            
            if engine_off and veh['engine_off_start'] is None:
                veh['engine_off_start'] = t
            elif not engine_off and veh['engine_off_start'] is not None:
                engine_off_duration = t - veh['engine_off_start']
                veh['engine_off_time'] += engine_off_duration
                veh['engine_off_start'] = None
            
            if engine_off:
                fuel_used = self.fuel_rate_off * dt
            elif speed < 0.5:
                fuel_used = self.fuel_rate_idling * dt
            else:
                fuel_used = self.fuel_rate_driving * dt
            
            emissions = fuel_used * self.co2_per_liter
            
            veh['total_fuel'] += fuel_used
            veh['total_emissions'] += emissions
            
            if veh['last_pos'] is not None:
                dx = pos[0] - veh['last_pos'][0]
                dy = pos[1] - veh['last_pos'][1]
                veh['distance_traveled'] += np.sqrt(dx**2 + dy**2)
            
            veh['last_pos'] = pos
            veh['max_speed'] = max(veh['max_speed'], speed)
            veh['speed_sum'] += speed
            veh['speed_count'] += 1
    
    def _track_queue_comfort(self, t):
        """Track queue sizes and calculate comfort score"""
        queue_w = 0
        queue_e = 0
        
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            try:
                pos = traci.vehicle.getPosition(vid)[0]
                speed = traci.vehicle.getSpeed(vid)
                
                if abs(pos - self.crossing_w) < 100 and speed < 0.5:
                    queue_w += 1
                elif abs(pos - self.crossing_e) < 100 and speed < 0.5:
                    queue_e += 1
            except:
                continue
        
        total_queue = queue_w + queue_e
        
        if self.wait_events:
            recent_waits = [w['wait_duration'] for w in self.wait_events[-50:]]
            avg_wait = np.mean(recent_waits) if recent_waits else 0
        else:
            avg_wait = 0
        
        comfort = self._calculate_comfort(total_queue, avg_wait)
        
        self.queue_snapshots.append({
            'time': t,
            'queue_west': queue_w,
            'queue_east': queue_e,
            'total_queue': total_queue,
            'avg_wait': avg_wait,
            'comfort': comfort
        })
        
        self.comfort_scores.append(comfort)
    
    def _calculate_comfort(self, queue_length, avg_wait):
        """Calculate driver comfort score (0-1, higher is better)"""
        queue_penalty = min(queue_length / 20.0, 1.0)
        wait_penalty = min(avg_wait / 60.0, 1.0)
        comfort = 1.0 - (0.6 * queue_penalty + 0.4 * wait_penalty)
        return max(0.0, comfort)
    
    def _save_data(self):
        """Save collected metrics data"""
        Logger.section("Saving metrics data")
        
        if self.wait_events:
            df = pd.DataFrame(self.wait_events)
            output_path = self.output_dir / 'wait_events.csv'
            df.to_csv(output_path, index=False)
            Logger.log(f"Wait events: {len(df)} records")
            Logger.log(f"  Mean wait: {df['wait_duration'].mean():.2f}s")
            Logger.log(f"  95th percentile: {df['wait_duration'].quantile(0.95):.2f}s")
        
        if self.queue_snapshots:
            df = pd.DataFrame(self.queue_snapshots)
            output_path = self.output_dir / 'queue_snapshots.csv'
            df.to_csv(output_path, index=False)
            Logger.log(f"Queue snapshots: {len(df)} records")
            Logger.log(f"  Mean queue: {df['total_queue'].mean():.1f} vehicles")
            Logger.log(f"  Mean comfort: {df['comfort'].mean():.2f}")
        
        if self.vehicle_data:
            vehicle_records = []
            for vid, data in self.vehicle_data.items():
                travel_time = data['last_seen'] - data['first_seen']
                avg_speed = data['speed_sum'] / data['speed_count'] if data['speed_count'] > 0 else 0
                
                vehicle_records.append({
                    'vehicle_id': vid,
                    'travel_time': travel_time,
                    'total_wait': data['total_wait'],
                    'stops': data['stops'],
                    'distance_traveled': data['distance_traveled'],
                    'total_fuel': data['total_fuel'],
                    'total_emissions': data['total_emissions'],
                    'engine_off_time': data['engine_off_time'],
                    'avg_speed': avg_speed,
                    'max_speed': data['max_speed']
                })
            
            df = pd.DataFrame(vehicle_records)
            output_path = self.output_dir / 'vehicle_metrics.csv'
            df.to_csv(output_path, index=False)
            Logger.log(f"Vehicle metrics: {len(df)} vehicles")
        
        summary = self._calculate_summary()
        df = pd.DataFrame([summary])
        output_path = self.output_dir / 'summary.csv'
        df.to_csv(output_path, index=False)
        
        self._print_summary(summary)
    
    def _calculate_summary(self):
        """Calculate summary statistics"""
        summary = {
            'vehicles_tracked': len(self.vehicle_data),
            'total_wait_events': len(self.wait_events),
            'steps_simulated': self.step_count,
            'total_engine_off_time': sum(v['engine_off_time'] for v in self.vehicle_data.values())
        }
        
        if self.wait_events:
            waits = [w['wait_duration'] for w in self.wait_events]
            summary.update({
                'total_wait_time': sum(waits),
                'avg_wait_time': np.mean(waits),
                'max_wait_time': max(waits),
                'median_wait_time': np.median(waits),
                'p95_wait_time': np.percentile(waits, 95)
            })
        
        if self.queue_snapshots:
            queues = [q['total_queue'] for q in self.queue_snapshots]
            summary.update({
                'avg_queue_length': np.mean(queues),
                'max_queue_length': max(queues),
                'avg_comfort_score': np.mean(self.comfort_scores)
            })
        
        if self.vehicle_data:
            total_fuel = sum(v['total_fuel'] for v in self.vehicle_data.values())
            total_emissions = sum(v['total_emissions'] for v in self.vehicle_data.values())
            total_stops = sum(v['stops'] for v in self.vehicle_data.values())
            total_engine_off = sum(v['engine_off_time'] for v in self.vehicle_data.values())
            
            fuel_saved = total_engine_off * (self.fuel_rate_idling - self.fuel_rate_off)
            emissions_saved = fuel_saved * self.co2_per_liter
            
            summary.update({
                'total_fuel': total_fuel,
                'fuel_saved': fuel_saved,
                'total_emissions': total_emissions,
                'emissions_saved': emissions_saved,
                'total_stops': total_stops
            })
        
        return summary
    
    def _print_summary(self, metrics):
        """Print metrics summary"""
        Logger.section("Metrics Summary")
        
        print(f"\nWait Time:")
        print(f"  Total: {metrics.get('total_wait_time', 0):.1f}s")
        print(f"  Average: {metrics.get('avg_wait_time', 0):.1f}s")
        print(f"  Maximum: {metrics.get('max_wait_time', 0):.1f}s")
        
        print(f"\nQueue:")
        print(f"  Average length: {metrics.get('avg_queue_length', 0):.1f} vehicles")
        
        print(f"\nComfort:")
        print(f"  Score: {metrics.get('avg_comfort_score', 0):.2f}")
        
        print(f"\nEngine Management:")
        print(f"  Total engine-off time: {metrics.get('total_engine_off_time', 0):.1f}s")
        
        print(f"\nFuel:")
        print(f"  Total: {metrics.get('total_fuel', 0):.2f}L")
        print(f"  Saved: {metrics.get('fuel_saved', 0):.2f}L")
        
        print(f"\nEmissions:")
        print(f"  Total: {metrics.get('total_emissions', 0):.2f}kg CO2")
        print(f"  Saved: {metrics.get('emissions_saved', 0):.2f}kg CO2")
        
        print(f"\nVehicles:")
        print(f"  Tracked: {metrics['vehicles_tracked']}")
        print(f"  Total stops: {metrics.get('total_stops', 0)}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect metrics data')
    parser.add_argument('--duration', type=int, help='Simulation duration in seconds')
    parser.add_argument('--gui', action='store_true', help='Use SUMO GUI')
    parser.add_argument('--config', default='config/simulation.yaml', help='Config file path')
    args = parser.parse_args()
    
    collector = MetricsDataCollector(args.config)
    collector.run(args.duration, args.gui)