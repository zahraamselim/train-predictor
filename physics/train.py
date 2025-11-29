"""Train physics and motion simulation."""

from dataclasses import dataclass
from typing import Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config


@dataclass
class TrainSpec:
    """Train specifications for physics simulation."""
    name: str
    mass: float              # tons
    max_power: float         # kW
    max_speed: float         # km/h
    brake_force_service: float    # g (as fraction of gravity)
    brake_force_emergency: float  # g
    frontal_area: float      # m²
    drag_coefficient: float


def load_train_specs() -> Dict[str, TrainSpec]:
    """Load train specifications from config."""
    config = load_config()
    specs = {}
    
    for name, data in config['train_types'].items():
        specs[name] = TrainSpec(
            name=name.capitalize(),
            mass=data['mass'],
            max_power=data['max_power'],
            max_speed=data['max_speed'],
            brake_force_service=data['brake_force_service'],
            brake_force_emergency=data['brake_force_emergency'],
            frontal_area=data['frontal_area'],
            drag_coefficient=data['drag_coefficient']
        )
    
    return specs


TRAIN_SPECS = load_train_specs()


class TrainPhysics:
    """Train motion physics using Newton's laws."""
    
    def __init__(self, spec: TrainSpec):
        self.spec = spec
        self.g = 9.81
        self.air_density = 1.225
        self.rolling_resistance_coef = 0.0018
    
    def calculate_tractive_force(self, velocity_ms: float) -> float:
        """Calculate available engine force at velocity."""
        if velocity_ms < 0.1:
            velocity_ms = 0.1
        
        power_watts = self.spec.max_power * 1000
        force_from_power = power_watts / velocity_ms
        adhesion_limit = 0.30 * self.spec.mass * 1000 * self.g
        
        return min(force_from_power, adhesion_limit)
    
    def calculate_resistance(self, velocity_ms: float, grade: float, weather: str = 'clear') -> float:
        """Calculate total resistance forces."""
        mass_kg = self.spec.mass * 1000
        
        rolling_coef = self.rolling_resistance_coef
        if weather == 'rain':
            rolling_coef *= 1.15
        elif weather == 'fog':
            rolling_coef *= 1.10
        
        rolling_force = rolling_coef * mass_kg * self.g
        air_force = (0.5 * self.air_density * self.spec.drag_coefficient * 
                    self.spec.frontal_area * velocity_ms**2)
        grade_force = mass_kg * self.g * (grade / 100)
        
        return rolling_force + air_force + grade_force
    
    def calculate_acceleration(self, velocity_ms: float, grade: float, 
                              target_speed_ms: float = None, weather: str = 'clear',
                              braking: str = None) -> float:
        """
        Calculate net acceleration using Newton's second law.
        
        Args:
            velocity_ms: Current velocity in m/s
            grade: Grade in percent (positive = uphill)
            target_speed_ms: Target speed for cruising control
            weather: Weather condition
            braking: 'service' or 'emergency' for braking
            
        Returns:
            Acceleration in m/s²
        """
        mass_kg = self.spec.mass * 1000
        
        if braking:
            brake_coef = (self.spec.brake_force_emergency if braking == 'emergency' 
                         else self.spec.brake_force_service)
            
            if weather == 'rain':
                brake_coef *= 0.85
            elif weather == 'fog':
                brake_coef *= 0.90
            
            brake_force = -brake_coef * mass_kg
            resistance = self.calculate_resistance(velocity_ms, grade, weather)
            net_force = brake_force - resistance
        else:
            resistance = self.calculate_resistance(velocity_ms, grade, weather)
            
            if target_speed_ms is not None:
                speed_error = target_speed_ms - velocity_ms
                if speed_error < 0:
                    traction = 0
                elif abs(speed_error) < 0.5:
                    traction = self.calculate_tractive_force(velocity_ms) * (speed_error / 0.5)
                else:
                    traction = self.calculate_tractive_force(velocity_ms)
            else:
                traction = self.calculate_tractive_force(velocity_ms)
            
            net_force = traction - resistance
        
        return net_force / mass_kg