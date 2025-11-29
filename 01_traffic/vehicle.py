"""Vehicle specifications and physics calculations."""

from dataclasses import dataclass
from typing import Dict, Optional
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config


@dataclass
class VehicleType:
    """Vehicle specifications for physics."""
    name: str
    mass: float
    max_speed: float
    max_accel: float
    max_decel: float
    length: float
    reaction_time: float


def load_vehicle_types() -> Dict[str, VehicleType]:
    """Load vehicle types from config."""
    config = load_config()
    types = {}
    
    for name, specs in config['vehicle_types'].items():
        if specs['max_decel'] > 10.0:
            raise ValueError(f"{name}: max_decel too high")
        if specs['max_accel'] > 5.0:
            raise ValueError(f"{name}: max_accel too high")
        
        types[name] = VehicleType(
            name=name.capitalize(),
            mass=specs['mass'],
            max_speed=specs['max_speed'],
            max_accel=specs['max_accel'],
            max_decel=specs['max_decel'],
            length=specs['length'],
            reaction_time=specs['reaction_time']
        )
    
    return types


VEHICLE_TYPES = load_vehicle_types()


class VehiclePhysics:
    """Physics engine for vehicle motion calculations."""
    
    def __init__(self, vehicle_type: VehicleType):
        self.vehicle = vehicle_type
    
    def calculate_stopping_distance(
        self, 
        initial_speed: float, 
        reaction_time: Optional[float] = None
    ) -> Dict[str, float]:
        """Calculate total stopping distance."""
        if reaction_time is None:
            reaction_time = self.vehicle.reaction_time
        
        speed_ms = initial_speed / 3.6
        reaction_distance = speed_ms * reaction_time
        
        if speed_ms > 0:
            braking_distance = (speed_ms ** 2) / (2 * self.vehicle.max_decel)
        else:
            braking_distance = 0.0
        
        return {
            'reaction_distance': round(reaction_distance, 2),
            'braking_distance': round(braking_distance, 2),
            'total_distance': round(reaction_distance + braking_distance, 2),
            'reaction_time': reaction_time
        }
    
    def calculate_time_to_traverse(
        self, 
        distance: float, 
        initial_speed: float,
        accelerate: bool = False
    ) -> float:
        """Calculate time to traverse distance."""
        speed_ms = initial_speed / 3.6
        
        if not accelerate or speed_ms >= self.vehicle.max_speed / 3.6:
            time = distance / speed_ms if speed_ms > 0 else float('inf')
            return round(time, 2)
        
        max_speed_ms = self.vehicle.max_speed / 3.6
        accel = self.vehicle.max_accel
        
        time_to_max = (max_speed_ms - speed_ms) / accel
        dist_to_max = speed_ms * time_to_max + 0.5 * accel * time_to_max**2
        
        if distance <= dist_to_max:
            discriminant = speed_ms**2 + 2 * accel * distance
            time = (-speed_ms + math.sqrt(discriminant)) / accel
        else:
            remaining_dist = distance - dist_to_max
            time_at_max = remaining_dist / max_speed_ms
            time = time_to_max + time_at_max
        
        return round(time, 2)
    
    def calculate_clearance_time(
        self, 
        distance_to_crossing: float,
        initial_speed: float,
        include_vehicle_length: bool = True
    ) -> float:
        """Calculate time for vehicle to completely clear crossing."""
        total_distance = distance_to_crossing
        if include_vehicle_length:
            total_distance += self.vehicle.length
        
        return self.calculate_time_to_traverse(total_distance, initial_speed, False)
    
    def calculate_safe_following_distance(self, speed: float, time_headway: float = 2.0) -> float:
        """Calculate safe following distance (2-second rule)."""
        speed_ms = speed / 3.6
        return round(speed_ms * time_headway, 2)
