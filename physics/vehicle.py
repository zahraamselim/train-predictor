"""Vehicle physics and specifications."""

from dataclasses import dataclass
from typing import Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config


@dataclass
class VehicleSpec:
    """Vehicle specifications for physics calculations."""
    name: str
    mass: float          # kg
    max_speed: float     # km/h
    max_accel: float     # m/s²
    max_decel: float     # m/s²
    length: float        # m
    reaction_time: float # s


def load_vehicle_specs() -> Dict[str, VehicleSpec]:
    """Load vehicle specifications from config."""
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
    """Physics engine for vehicle motion."""
    
    def __init__(self, spec: VehicleSpec):
        self.spec = spec
    
    def calculate_stopping_distance(self, speed_kmh: float) -> Dict[str, float]:
        """
        Calculate total stopping distance.
        
        Args:
            speed_kmh: Speed in km/h
            
        Returns:
            Dict with reaction_distance, braking_distance, total_distance
        """
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
        """
        Calculate time to completely clear a distance.
        
        Args:
            distance: Distance to clear in meters
            speed_kmh: Speed in km/h
            
        Returns:
            Time in seconds
        """
        speed_ms = speed_kmh / 3.6
        total_distance = distance + self.spec.length
        
        if speed_ms > 0:
            return round(total_distance / speed_ms, 2)
        return float('inf')
    
    def calculate_safe_following_distance(self, speed_kmh: float, time_headway: float = 2.0) -> float:
        """
        Calculate safe following distance (2-second rule).
        
        Args:
            speed_kmh: Speed in km/h
            time_headway: Time gap in seconds
            
        Returns:
            Distance in meters
        """
        speed_ms = speed_kmh / 3.6
        return round(speed_ms * time_headway, 2)