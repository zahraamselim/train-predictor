"""
Traffic Parameters Module

Simulates vehicle behavior to determine optimal gate closure and notification timings.
"""

from .vehicle_types import VehicleType, VEHICLE_TYPES
from .vehicle_physics import VehiclePhysics
from .traffic_simulator import TrafficSimulator
from .generate_parameters import (
    generate_traffic_parameters,
    calculate_gate_timing,
    analyze_intersection_scenarios
)

__all__ = [
    'VehicleType',
    'VEHICLE_TYPES',
    'VehiclePhysics',
    'TrafficSimulator',
    'generate_traffic_parameters',
    'calculate_gate_timing',
    'analyze_intersection_scenarios'
]