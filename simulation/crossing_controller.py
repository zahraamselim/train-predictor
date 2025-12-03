"""
Main control logic for level crossing system
"""
import traci
import yaml
from utils.logger import Logger


class CrossingController:
    def __init__(self, config_path='config/simulation.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        thresholds_path = 'outputs/results/thresholds.yaml'
        try:
            with open(thresholds_path) as f:
                thresholds = yaml.safe_load(f)
        except FileNotFoundError:
            Logger.log(f"WARNING: No thresholds found at {thresholds_path}, using defaults")
            thresholds = {
                'closure_before_eta': 10.0,
                'opening_after_etd': 3.0,
                'notification_time': 30.0,
                'sensor_positions': [1500.0, 900.0, 450.0],
                'engine_off_threshold': 5.0
            }
        
        self.closure_threshold = thresholds['closure_before_eta']
        self.opening_threshold = thresholds['opening_after_etd']
        self.notification_threshold = thresholds['notification_time']
        self.engine_off_threshold = thresholds['engine_off_threshold']
        
        net_cfg = self.config.get('network', {})
        self.crossing_w = net_cfg.get('crossing_w', -200.0)
        self.crossing_e = net_cfg.get('crossing_e', 200.0)
        
        self.sensor_positions = [self.crossing_w - s for s in thresholds['sensor_positions']]
        
        self.trains = {}
        self.gates_closed = False
        self.intersections_notified = False
        self.vehicles_engines_off = set()
        self.vehicle_wait_start = {}
        self.engine_off_count = 0
    
    def step(self, t):
        """Execute one control step"""
        self._track_trains(t)
        self._control_gates(t)
        self._control_intersections(t)
        self._control_vehicle_engines(t)
    
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
            
            if remaining <= self.closure_threshold and not self.gates_closed:
                self._close_gates()
            
            if train['passed_e'] and self.gates_closed:
                departure_time = t - train['arrival_e']
                if departure_time >= self.opening_threshold:
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
            
            if remaining <= self.notification_threshold and not self.intersections_notified:
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
                    expected_remaining >= self.engine_off_threshold and 
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
                return max(0, remaining + self.opening_threshold)
        return 0
    
    def get_state(self):
        """Get current controller state"""
        return {
            'gates_closed': self.gates_closed,
            'intersections_notified': self.intersections_notified,
            'active_trains': len([t for t in self.trains.values() if not t['passed_e']]),
            'engines_off': len(self.vehicles_engines_off)
        }