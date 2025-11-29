"""Traffic scenario simulation for clearance time analysis."""

import numpy as np
from typing import List, Dict, Optional, Tuple
import sys
import os

# Add parent directory to path for config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config

# Import from same package - add package directory to path
package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from vehicle import VEHICLE_TYPES, VehiclePhysics


class TrafficSimulator:
    """Simulates traffic scenarios at intersections."""
    
    def __init__(self, intersection_distance: float):
        self.intersection_distance = intersection_distance
        
        self._vehicle_mix = {
            'car': 0.60,
            'suv': 0.25,
            'truck': 0.10,
            'motorcycle': 0.05
        }
        
        self._density_configs = {
            'light': {'num_vehicles': 3, 'speed_range': (45, 60)},
            'medium': {'num_vehicles': 8, 'speed_range': (35, 55)},
            'heavy': {'num_vehicles': 15, 'speed_range': (20, 40)}
        }
    
    def simulate_single_vehicle(
        self, 
        vehicle_type: str, 
        initial_speed: float,
        at_intersection: bool = True
    ) -> Dict:
        """Simulate single vehicle clearance."""
        physics = VehiclePhysics(VEHICLE_TYPES[vehicle_type])
        
        time_to_crossing = physics.calculate_time_to_traverse(
            self.intersection_distance, initial_speed, at_intersection
        )
        
        stopping = physics.calculate_stopping_distance(initial_speed)
        can_stop = stopping['total_distance'] < self.intersection_distance
        
        clearance_time = physics.calculate_clearance_time(
            self.intersection_distance, initial_speed, True
        )
        
        return {
            'vehicle_type': vehicle_type,
            'initial_speed': initial_speed,
            'time_to_crossing': time_to_crossing,
            'stopping_distance': stopping['total_distance'],
            'can_stop': can_stop,
            'clearance_time': clearance_time
        }
    
    def simulate_vehicle_queue(
        self,
        num_vehicles: int,
        vehicle_mix: Optional[Dict[str, float]] = None,
        speed_range: Tuple[float, float] = (30, 60)
    ) -> List[Dict]:
        """Simulate queue of vehicles."""
        if vehicle_mix is None:
            vehicle_mix = self._vehicle_mix
        
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
    
    def analyze_traffic_density(self, density: str = 'medium') -> Dict:
        """Analyze traffic clearance for density scenario."""
        config = self._density_configs.get(density, self._density_configs['medium'])
        
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