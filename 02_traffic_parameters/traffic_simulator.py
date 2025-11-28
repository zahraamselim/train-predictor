import numpy as np
from typing import List, Dict
import sys
import os

try:
    from .vehicle_types import VEHICLE_TYPES
    from .vehicle_physics import VehiclePhysics
except ImportError:
    from vehicle_types import VEHICLE_TYPES
    from vehicle_physics import VehiclePhysics

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config


class TrafficSimulator:
    """Simulates traffic scenarios at road intersection before level crossing."""
    
    def __init__(self, intersection_distance: float):
        """
        Args:
            intersection_distance: Distance from road intersection to train crossing
        """
        self.intersection_distance = intersection_distance
    
    def simulate_single_vehicle(self, vehicle_type: str, 
                                initial_speed: float,
                                at_intersection: bool = True) -> Dict:
        """
        Simulate single vehicle at road intersection.
        
        Args:
            vehicle_type: 'car', 'suv', 'truck', or 'motorcycle'
            initial_speed: Speed vehicle would travel at (km/h)
            at_intersection: True if stopped at intersection, False if already moving
        
        Returns:
            Dictionary with timing parameters
        """
        physics = VehiclePhysics(VEHICLE_TYPES[vehicle_type])
        
        if at_intersection:
            time_to_crossing = physics.calculate_time_to_traverse(
                self.intersection_distance,
                initial_speed,
                accelerate=True
            )
        else:
            time_to_crossing = physics.calculate_time_to_traverse(
                self.intersection_distance,
                initial_speed,
                accelerate=False
            )
        
        stopping = physics.calculate_stopping_distance(initial_speed)
        can_stop_before_crossing = stopping['total_distance'] < self.intersection_distance
        
        clearance_time = physics.calculate_clearance_time(
            self.intersection_distance,
            initial_speed,
            include_vehicle_length=True
        )
        
        return {
            'vehicle_type': vehicle_type,
            'initial_speed': initial_speed,
            'time_to_crossing': time_to_crossing,
            'stopping_distance': stopping['total_distance'],
            'reaction_distance': stopping['reaction_distance'],
            'braking_distance': stopping['braking_distance'],
            'can_stop': can_stop_before_crossing,
            'clearance_time': clearance_time,
            'at_intersection': at_intersection,
            'intersection_distance': self.intersection_distance
        }
    
    def simulate_vehicle_queue(self, num_vehicles: int,
                              vehicle_mix: Dict[str, float] = None,
                              speed_range: tuple = (30, 60)) -> List[Dict]:
        """
        Simulate queue of vehicles at intersection.
        
        Args:
            num_vehicles: Number of vehicles in queue
            vehicle_mix: Distribution of vehicle types (default: realistic mix)
            speed_range: Min/max speeds in km/h
        
        Returns:
            List of vehicle simulation results
        """
        if vehicle_mix is None:
            vehicle_mix = {'car': 0.60, 'suv': 0.25, 'truck': 0.10, 'motorcycle': 0.05}
        
        vehicle_types = list(vehicle_mix.keys())
        probabilities = list(vehicle_mix.values())
        results = []
        
        for i in range(num_vehicles):
            v_type = np.random.choice(vehicle_types, p=probabilities)
            speed = np.random.uniform(*speed_range)
            
            result = self.simulate_single_vehicle(v_type, speed)
            result['vehicle_id'] = i
            results.append(result)
        
        return results
    
    def calculate_notification_time(self, gate_closure_time: float,
                                   safety_buffer: float = 2.0) -> Dict:
        """
        Calculate when to notify vehicles at intersection.
        
        Args:
            gate_closure_time: Time until gates close (seconds)
            safety_buffer: Additional safety margin (seconds)
        
        Returns:
            Dictionary with notification timing
        """
        avg_speed = 50
        physics = VehiclePhysics(VEHICLE_TYPES['car'])
        
        avg_clearance_time = physics.calculate_clearance_time(
            self.intersection_distance,
            avg_speed,
            include_vehicle_length=True
        )
        
        notification_time = gate_closure_time - avg_clearance_time - safety_buffer
        
        return {
            'notification_time': max(0, round(notification_time, 2)),
            'gate_closure_time': gate_closure_time,
            'avg_clearance_time': avg_clearance_time,
            'safety_buffer': safety_buffer,
            'intersection_distance': self.intersection_distance
        }
    
    def analyze_traffic_density(self, density: str = 'medium') -> Dict:
        """
        Analyze traffic for different density scenarios.
        
        Args:
            density: 'light', 'medium', or 'heavy'
        
        Returns:
            Dictionary with density analysis
        """
        density_configs = {
            'light': {'num_vehicles': 3, 'speed_range': (45, 60)},
            'medium': {'num_vehicles': 8, 'speed_range': (35, 55)},
            'heavy': {'num_vehicles': 15, 'speed_range': (20, 40)}
        }
        
        config = density_configs.get(density, density_configs['medium'])
        
        vehicles = self.simulate_vehicle_queue(
            num_vehicles=config['num_vehicles'],
            speed_range=config['speed_range']
        )
        
        clearance_times = [v['clearance_time'] for v in vehicles]
        
        return {
            'density': density,
            'num_vehicles': len(vehicles),
            'avg_clearance_time': round(np.mean(clearance_times), 2),
            'max_clearance_time': round(np.max(clearance_times), 2),
            'min_clearance_time': round(np.min(clearance_times), 2),
            'vehicles': vehicles
        }