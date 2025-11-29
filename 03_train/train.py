"""Train specifications and physics engine."""

from dataclasses import dataclass
from typing import Dict
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config


@dataclass
class TrainType:
    """Train specifications for physics simulation."""
    name: str
    mass: float
    max_power: float
    max_speed: float
    brake_force_service: float
    brake_force_emergency: float
    frontal_area: float
    drag_coefficient: float


def load_train_types() -> Dict[str, TrainType]:
    """Load train types from config."""
    config = load_config()
    types = {}
    
    for name, specs in config['train_types'].items():
        types[name] = TrainType(
            name=name.capitalize(),
            mass=specs['mass'],
            max_power=specs['max_power'],
            max_speed=specs['max_speed'],
            brake_force_service=specs['brake_force_service'],
            brake_force_emergency=specs['brake_force_emergency'],
            frontal_area=specs['frontal_area'],
            drag_coefficient=specs['drag_coefficient']
        )
    
    return types


TRAIN_TYPES = load_train_types()


class TrainPhysics:
    """Train motion physics using Newton's laws."""
    
    def __init__(self, train_type: TrainType):
        self.train = train_type
        self.g = 9.81
        self.air_density = 1.225
        self.rolling_resistance_coef = 0.0018
    
    def calculate_tractive_force(self, velocity: float) -> float:
        """Calculate available engine force at given velocity."""
        if velocity < 0.1:
            velocity = 0.1
        
        power_watts = self.train.max_power * 1000
        force_from_power = power_watts / velocity
        adhesion_limit = 0.30 * self.train.mass * 1000 * self.g
        
        return min(force_from_power, adhesion_limit)
    
    def calculate_resistance(self, velocity: float, grade: float, weather: str = 'clear') -> float:
        """Calculate total resistance forces."""
        mass_kg = self.train.mass * 1000
        
        rolling_coef = self.rolling_resistance_coef
        if weather == 'rain':
            rolling_coef *= 1.15
        elif weather == 'fog':
            rolling_coef *= 1.10
        
        rolling_force = rolling_coef * mass_kg * self.g
        air_force = (0.5 * self.air_density * self.train.drag_coefficient * 
                    self.train.frontal_area * velocity**2)
        grade_force = mass_kg * self.g * (grade / 100)
        
        return rolling_force + air_force + grade_force
    
    def calculate_acceleration(
        self, 
        velocity: float, 
        grade: float, 
        target_speed: float = None,
        weather: str = 'clear',
        braking: str = None
    ) -> float:
        """Calculate net acceleration using Newton's second law."""
        mass_kg = self.train.mass * 1000
        
        if braking:
            brake_coef = (self.train.brake_force_emergency if braking == 'emergency' 
                         else self.train.brake_force_service)
            
            if weather == 'rain':
                brake_coef *= 0.85
            elif weather == 'fog':
                brake_coef *= 0.90
            
            brake_force = -brake_coef * mass_kg
            resistance = self.calculate_resistance(velocity, grade, weather)
            net_force = brake_force - resistance
        else:
            resistance = self.calculate_resistance(velocity, grade, weather)
            
            if target_speed is not None:
                speed_error = target_speed - velocity
                if speed_error < 0:
                    traction = 0
                elif abs(speed_error) < 0.5:
                    traction = self.calculate_tractive_force(velocity) * (speed_error / 0.5)
                else:
                    traction = self.calculate_tractive_force(velocity)
            else:
                traction = self.calculate_tractive_force(velocity)
            
            net_force = traction - resistance
        
        return net_force / mass_kg