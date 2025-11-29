"""Train type definitions loaded from config."""

from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config


@dataclass
class TrainType:
    """Train characteristics for physics simulation."""
    name: str
    mass: float
    max_power: float
    max_speed: float
    brake_force_service: float
    brake_force_emergency: float
    frontal_area: float
    drag_coefficient: float


def _load_train_types():
    """Load train types from system config."""
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


TRAIN_TYPES = _load_train_types()