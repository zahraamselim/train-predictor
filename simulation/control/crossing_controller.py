"""
Crossing Controller
Main control logic for level crossing system
"""
import traci
import yaml
from datetime import datetime
from pathlib import Path


class CrossingController:
    def __init__(self, config_file="config/thresholds.yaml"):
        with open(config_file) as f:
            self.config = yaml.safe_load(f)
        
        self.sensors = self.config['sensor_positions']
        self.closure_threshold = self.config['closure_before_eta']
        self.opening_threshold = self.config['opening_after_etd']
        self.notification_threshold = max(self.config['notification_times'].values())
        self.engine_off_threshold = self.config['engine_off_threshold']
        
        self.crossing_w = -200.0
        self.crossing_e = 200.0
        
        self.trains = {}
        self.gates_closed = False
        self.intersections_notified = False
        
        self.vehicles_engines_off = set()
    
    def step(self, t):
        """Execute one control step"""
        self._track_trains(t)
        self._control_gates(t)
        self._control_intersections(t)
        self._control_vehicle_engines(t)
    
    def _track_trains(self, t):
        """Track train positions and calculate ETA"""
        for tid in traci.vehicle.getIDList():
            if 'train' not in tid.lower():
                continue
            
            pos = traci.vehicle.getPosition(tid)[0]
            speed = traci.vehicle.getSpeed(tid)
            
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
            
            # Check sensor triggers
            for i, sensor_pos in enumerate(self.sensors):
                if i not in train['sensor_triggers'] and pos >= sensor_pos:
                    train['sensor_triggers'][i] = t
                    train['sensor_speeds'][i] = speed
                    
                    if i == 0:
                        print(f"[{self._timestamp()}] Train {tid} detected at sensor 0")
            
            # Calculate ETA when all sensors triggered
            if len(train['sensor_triggers']) == 3 and train['eta'] is None:
                train['eta'] = self._calculate_eta(train)
                train['eta_calculated_at'] = t
                print(f"[{self._timestamp()}] Train {tid} ETA: {train['eta']:.1f}s")
            
            # Track crossing passage
            if pos >= self.crossing_w and not train['passed_w']:
                train['passed_w'] = True
                train['arrival_w'] = t
                print(f"[{self._timestamp()}] Train {tid} reached west crossing")
            
            if pos >= self.crossing_e and not train['passed_e']:
                train['passed_e'] = True
                train['arrival_e'] = t
    
    def _calculate_eta(self, train):
        """Calculate train ETA using kinematics"""
        triggers = train['sensor_triggers']
        speeds = train['sensor_speeds']
        
        t01 = triggers[1] - triggers[0]
        t12 = triggers[2] - triggers[1]
        
        d01 = self.sensors[0] - self.sensors[1]
        d12 = self.sensors[1] - self.sensors[2]
        
        v01 = d01 / t01 if t01 > 0 else speeds[1]
        v12 = d12 / t12 if t12 > 0 else speeds[2]
        
        # Use most recent speed for ETA
        distance = self.sensors[2]
        eta = distance / v12 if v12 > 0 else distance / 30.0
        
        return eta
    
    def _control_gates(self, t):
        """Control gate closure and opening"""
        for tid, train in self.trains.items():
            if train['eta'] is None:
                continue
            
            elapsed = t - train['eta_calculated_at']
            remaining = train['eta'] - elapsed
            
            # Close gates
            if remaining <= self.closure_threshold and not self.gates_closed:
                self._close_gates(t)
            
            # Open gates after train passes
            if train['passed_e'] and self.gates_closed:
                departure_time = t - train['arrival_e']
                if departure_time >= self.opening_threshold:
                    self._open_gates(t)
    
    def _close_gates(self, t):
        """Close crossing gates"""
        self.gates_closed = True
        print(f"[{self._timestamp()}] Gates closed")
    
    def _open_gates(self, t):
        """Open crossing gates"""
        self.gates_closed = False
        self.intersections_notified = False
        self.vehicles_engines_off.clear()
        print(f"[{self._timestamp()}] Gates opened")
    
    def _control_intersections(self, t):
        """Control intersection notifications"""
        for tid, train in self.trains.items():
            if train['eta'] is None:
                continue
            
            elapsed = t - train['eta_calculated_at']
            remaining = train['eta'] - elapsed
            
            if remaining <= self.notification_threshold and not self.intersections_notified:
                self.intersections_notified = True
                print(f"[{self._timestamp()}] Intersections notified")
                print(f"  Buzzer activated, warning lights on")
    
    def _control_vehicle_engines(self, t):
        """Control vehicle engine off/on"""
        if not self.gates_closed:
            return
        
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            pos = traci.vehicle.getPosition(vid)[0]
            speed = traci.vehicle.getSpeed(vid)
            
            # Check if vehicle is waiting at crossing
            in_queue_w = abs(pos - self.crossing_w) < 50 and speed < 0.5
            in_queue_e = abs(pos - self.crossing_e) < 50 and speed < 0.5
            
            if (in_queue_w or in_queue_e) and vid not in self.vehicles_engines_off:
                # Calculate wait time
                wait_time = self._get_expected_wait_time(t)
                
                if wait_time >= self.engine_off_threshold:
                    self.vehicles_engines_off.add(vid)
                    print(f"[{self._timestamp()}] Vehicle {vid} engine off (wait: {wait_time:.0f}s)")
    
    def _get_expected_wait_time(self, t):
        """Get expected wait time for vehicles"""
        for train in self.trains.values():
            if train['eta'] is not None and not train['passed_e']:
                elapsed = t - train['eta_calculated_at']
                remaining = train['eta'] - elapsed
                return remaining + self.opening_threshold
        
        return 0
    
    def get_state(self):
        """Get current system state"""
        return {
            'gates_closed': self.gates_closed,
            'intersections_notified': self.intersections_notified,
            'active_trains': len([t for t in self.trains.values() if not t['passed_e']]),
            'engines_off': len(self.vehicles_engines_off)
        }
    
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")