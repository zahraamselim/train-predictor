"""Vehicle type definitions loaded from config."""

from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config


@dataclass
class VehicleType:
    """Vehicle characteristics for physics simulation."""
    name: str
    mass: float
    max_speed: float
    max_accel: float
    max_decel: float
    length: float
    reaction_time: float


def _load_vehicle_types():
    """Load vehicle types from system config."""
    config = load_config()
    types = {}
    
    for name, specs in config['vehicle_types'].items():
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


VEHICLE_TYPES = _load_vehicle_types()