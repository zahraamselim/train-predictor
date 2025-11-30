"""Vehicle physics and routing logic."""

from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config


@dataclass
class VehicleSpec:
    name: str
    mass: float
    max_speed: float
    max_accel: float
    max_decel: float
    length: float
    reaction_time: float


def load_vehicle_specs() -> Dict[str, VehicleSpec]:
    config = load_config()
    specs = {}
    
    for name, data in config['vehicle_types'].items():
        if data['max_decel'] > 10.0:
            raise ValueError(f"{name}: max_decel too high")
        if data['max_accel'] > 5.0:
            raise ValueError(f"{name}: max_accel too high")
        
        specs[name] = VehicleSpec(
            name=name.capitalize(),
            mass=data['mass'],
            max_speed=data['max_speed'],
            max_accel=data['max_accel'],
            max_decel=data['max_decel'],
            length=data['length'],
            reaction_time=data['reaction_time']
        )
    
    return specs


VEHICLE_SPECS = load_vehicle_specs()


class VehiclePhysics:
    def __init__(self, spec: VehicleSpec):
        self.spec = spec
    
    def calculate_stopping_distance(self, speed_kmh: float) -> Dict[str, float]:
        speed_ms = speed_kmh / 3.6
        reaction_distance = speed_ms * self.spec.reaction_time
        
        if speed_ms > 0:
            braking_distance = (speed_ms ** 2) / (2 * self.spec.max_decel)
        else:
            braking_distance = 0.0
        
        return {
            'reaction_distance': round(reaction_distance, 2),
            'braking_distance': round(braking_distance, 2),
            'total_distance': round(reaction_distance + braking_distance, 2),
            'reaction_time': self.spec.reaction_time
        }
    
    def calculate_clearance_time(self, distance: float, speed_kmh: float) -> float:
        speed_ms = speed_kmh / 3.6
        total_distance = distance + self.spec.length
        
        if speed_ms > 0:
            return round(total_distance / speed_ms, 2)
        return float('inf')
    
    def calculate_safe_following_distance(self, speed_kmh: float, time_headway: float = 2.0) -> float:
        speed_ms = speed_kmh / 3.6
        return round(speed_ms * time_headway, 2)


class RouteDecision:
    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                 crossing_pos: Tuple[int, int], alternative_distance: float):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.crossing_pos = crossing_pos
        self.alternative_distance = alternative_distance
        self.direct_distance = self._calculate_direct_distance()
    
    def _calculate_direct_distance(self) -> float:
        return abs(self.start_pos[0] - self.end_pos[0]) + abs(self.start_pos[1] - self.end_pos[1])
    
    def calculate_wait_time(self, train_eta: float, queue_length: int, gate_closure_offset: float) -> float:
        time_until_gate_closes = max(0, train_eta - gate_closure_offset)
        time_gate_closed = gate_closure_offset + 5
        time_to_reopen = 10
        avg_vehicle_delay = 3
        queue_delay = queue_length * avg_vehicle_delay
        
        total_wait = time_until_gate_closes + time_gate_closed + time_to_reopen + queue_delay
        return total_wait
    
    def calculate_reroute_time(self, traffic_density: str, speed_ms: float) -> float:
        density_factor = {
            'light': 1.0,
            'medium': 0.8,
            'heavy': 0.6
        }
        
        factor = density_factor.get(traffic_density, 0.8)
        effective_speed = speed_ms * factor
        decision_delay = 5
        
        if effective_speed > 0:
            reroute_time = self.alternative_distance / effective_speed + decision_delay
        else:
            reroute_time = float('inf')
        
        return reroute_time
    
    def should_wait_or_reroute(self, train_eta: float, queue_length: int, 
                               traffic_density: str, speed_ms: float, 
                               gate_closure_offset: float) -> Tuple[str, float]:
        wait_time = self.calculate_wait_time(train_eta, queue_length, gate_closure_offset)
        reroute_time = self.calculate_reroute_time(traffic_density, speed_ms)
        
        if wait_time < reroute_time:
            return 'wait', reroute_time - wait_time
        else:
            return 'reroute', wait_time - reroute_time


class VehicleQueue:
    def __init__(self, crossing_position: Tuple[int, int], direction: str):
        self.crossing_position = crossing_position
        self.direction = direction
        self.vehicles = []
    
    def add_vehicle(self, vehicle_id: int, position: Tuple[float, float]):
        self.vehicles.append({
            'id': vehicle_id,
            'position': position,
            'stopped': False
        })
    
    def remove_vehicle(self, vehicle_id: int):
        self.vehicles = [v for v in self.vehicles if v['id'] != vehicle_id]
    
    def get_queue_length(self) -> int:
        return len(self.vehicles)
    
    def get_position_in_queue(self, vehicle_id: int) -> Optional[int]:
        for idx, v in enumerate(self.vehicles):
            if v['id'] == vehicle_id:
                return idx
        return None
    
    def clear(self):
        self.vehicles = []