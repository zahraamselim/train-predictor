from typing import List
import sys
import os

try:
    from .train_types import TRAIN_TYPES
    from .train_physics import TrainPhysics
except ImportError:
    from train_types import TRAIN_TYPES
    from train_physics import TrainPhysics

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config


class TrainSimulator:
    """Runs train simulation scenarios and generates approach data."""
    
    def __init__(self, train_type: str, crossing_distance: float = None):
        """
        Args:
            train_type: 'passenger', 'freight', or 'express'
            crossing_distance: Distance from start to level crossing (uses config if None)
        """
        self.physics = TrainPhysics(TRAIN_TYPES[train_type])
        self.train_type = train_type
        
        config = get_scale_config()
        train_config = config['train']
        self.crossing_distance = crossing_distance if crossing_distance else train_config['crossing_distance']
        self.train_length = train_config['train_length']
        self.buffer_distance = train_config['buffer_distance']
    
    def simulate_approach(self, 
                         initial_speed: float,
                         grade: float,
                         weather: str = 'clear',
                         target_speed: float = None,
                         dt: float = 0.1) -> List[dict]:
        """
        Simulate train approaching and clearing level crossing.
        
        Args:
            initial_speed: Starting speed (km/h)
            grade: Average track grade (percentage)
            weather: 'clear', 'rain', or 'fog'
            target_speed: Cruising speed to maintain (km/h). If None, uses initial_speed
            dt: Simulation timestep (seconds)
        
        Returns:
            List of state dictionaries
        """
        speed = initial_speed / 3.6
        if target_speed is None:
            target_speed = initial_speed
        target_speed_ms = target_speed / 3.6
        
        distance = self.crossing_distance
        time = 0.0
        
        trajectory = []
        last_distance = distance
        stall_counter = 0
        
        while distance > -(self.train_length + self.buffer_distance):
            if distance > self.train_length:
                crossing_status = 'approaching'
            elif distance > 0:
                crossing_status = 'entering'
            elif distance > -self.train_length:
                crossing_status = 'occupying'
            else:
                crossing_status = 'cleared'
            
            accel = self.physics.calculate_acceleration(speed, grade, target_speed_ms, weather, braking=None)
            
            max_speed_ms = self.physics.train.max_speed / 3.6
            if speed > max_speed_ms:
                speed = max_speed_ms
                accel = min(accel, 0)
            
            speed_new = max(0, speed + accel * dt)
            distance_new = distance - (speed * dt + 0.5 * accel * dt**2)
            
            if abs(distance - last_distance) < 0.001 and distance > 0:
                stall_counter += 1
                if stall_counter > 50:
                    print(f"Warning: Train stalled at {distance:.2f}m - insufficient power for grade {grade}%")
                    break
            else:
                stall_counter = 0
            
            last_distance = distance
            
            if distance > 0:
                eta = distance / speed if speed > 0.1 else 0
            else:
                eta = 0
            
            trajectory.append({
                'time': round(time, 2),
                'distance_to_crossing': round(distance, 2),
                'speed': round(speed * 3.6, 2),
                'acceleration': round(accel, 3),
                'ETA': round(eta, 2),
                'grade': grade,
                'weather': weather,
                'train_type': self.train_type,
                'crossing_status': crossing_status
            })
            
            speed = speed_new
            distance = distance_new
            time += dt
            
            if time > 300:
                print(f"Warning: Simulation timeout at {time}s")
                break
        
        return trajectory