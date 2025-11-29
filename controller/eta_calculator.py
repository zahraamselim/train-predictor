"""Physics-based ETA calculator from sensor timings."""

import math
from typing import Dict


class ETACalculator:
    """
    Calculate train ETA using sensor detection timings.
    Uses kinematic equations with measured speed and acceleration.
    """
    
    def __init__(self, sensor_positions):
        """
        Initialize calculator with sensor positions.
        
        Args:
            sensor_positions: List of [furthest, middle, nearest] distances from crossing (m)
        """
        if len(sensor_positions) != 3:
            raise ValueError("Requires exactly 3 sensor positions")
        
        if not (sensor_positions[0] > sensor_positions[1] > sensor_positions[2]):
            raise ValueError("Sensors must be ordered: furthest to nearest")
        
        self.sensor_positions = sensor_positions
    
    def calculate_eta_simple(self, sensor_timings: Dict[str, float]) -> float:
        """
        Simple ETA using constant speed assumption.
        Uses most recent speed (between sensors 1-2).
        
        Args:
            sensor_timings: Dict with 'sensor_0_entry', 'sensor_1_entry', 'sensor_2_entry' (s)
        
        Returns:
            ETA in seconds from sensor 2 detection
        """
        t0 = sensor_timings['sensor_0_entry']
        t1 = sensor_timings['sensor_1_entry']
        t2 = sensor_timings['sensor_2_entry']
        
        distance_1_to_2 = self.sensor_positions[1] - self.sensor_positions[2]
        time_1_to_2 = t2 - t1
        
        if time_1_to_2 <= 0:
            return float('inf')
        
        speed = distance_1_to_2 / time_1_to_2
        remaining_distance = self.sensor_positions[2]
        eta = remaining_distance / speed if speed > 0 else float('inf')
        
        return round(eta, 2)
    
    def calculate_eta_with_acceleration(self, sensor_timings: Dict[str, float]) -> float:
        """
        Advanced ETA accounting for acceleration/deceleration.
        
        Args:
            sensor_timings: Dict with sensor entry times
        
        Returns:
            ETA in seconds from sensor 2 detection
        """
        t0 = sensor_timings['sensor_0_entry']
        t1 = sensor_timings['sensor_1_entry']
        t2 = sensor_timings['sensor_2_entry']
        
        dist_0_to_1 = self.sensor_positions[0] - self.sensor_positions[1]
        dist_1_to_2 = self.sensor_positions[1] - self.sensor_positions[2]
        
        time_0_to_1 = t1 - t0
        time_1_to_2 = t2 - t1
        
        if time_0_to_1 <= 0 or time_1_to_2 <= 0:
            return float('inf')
        
        speed_0_to_1 = dist_0_to_1 / time_0_to_1
        speed_1_to_2 = dist_1_to_2 / time_1_to_2
        
        acceleration = (speed_1_to_2 - speed_0_to_1) / time_1_to_2
        
        remaining_distance = self.sensor_positions[2]
        current_speed = speed_1_to_2
        
        if abs(acceleration) < 0.05:
            eta = remaining_distance / current_speed
        else:
            a = 0.5 * acceleration
            b = current_speed
            c = -remaining_distance
            
            discriminant = b**2 - 4*a*c
            
            if discriminant < 0:
                eta = remaining_distance / current_speed
            else:
                t1_sol = (-b + math.sqrt(discriminant)) / (2*a)
                t2_sol = (-b - math.sqrt(discriminant)) / (2*a)
                
                if t1_sol > 0:
                    eta = t1_sol
                elif t2_sol > 0:
                    eta = t2_sol
                else:
                    eta = remaining_distance / current_speed
        
        return round(max(0, eta), 2)
    
    def calculate_eta_robust(self, sensor_timings: Dict[str, float]) -> Dict:
        """
        Robust ETA calculation with diagnostics.
        
        Returns:
            Dict with eta_final, speeds, acceleration, and flags
        """
        eta_simple = self.calculate_eta_simple(sensor_timings)
        eta_advanced = self.calculate_eta_with_acceleration(sensor_timings)
        
        t0 = sensor_timings['sensor_0_entry']
        t1 = sensor_timings['sensor_1_entry']
        t2 = sensor_timings['sensor_2_entry']
        
        dist_0_to_1 = self.sensor_positions[0] - self.sensor_positions[1]
        dist_1_to_2 = self.sensor_positions[1] - self.sensor_positions[2]
        
        speed_0_to_1 = dist_0_to_1 / (t1 - t0)
        speed_1_to_2 = dist_1_to_2 / (t2 - t1)
        acceleration = (speed_1_to_2 - speed_0_to_1) / (t2 - t1)
        
        return {
            'eta_simple': eta_simple,
            'eta_advanced': eta_advanced,
            'eta_final': eta_advanced,
            'speed_0_to_1_ms': round(speed_0_to_1, 2),
            'speed_1_to_2_ms': round(speed_1_to_2, 2),
            'speed_0_to_1_kmh': round(speed_0_to_1 * 3.6, 2),
            'speed_1_to_2_kmh': round(speed_1_to_2 * 3.6, 2),
            'acceleration': round(acceleration, 3),
            'is_accelerating': acceleration > 0.05,
            'is_decelerating': acceleration < -0.05
        }
    
    def validate_timings(self, sensor_timings: Dict[str, float]) -> bool:
        """Validate sensor timings are reasonable."""
        required_keys = ['sensor_0_entry', 'sensor_1_entry', 'sensor_2_entry']
        
        if not all(key in sensor_timings for key in required_keys):
            return False
        
        t0 = sensor_timings['sensor_0_entry']
        t1 = sensor_timings['sensor_1_entry']
        t2 = sensor_timings['sensor_2_entry']
        
        if t0 is None or t1 is None or t2 is None:
            return False
        
        if not (t0 < t1 < t2):
            return False
        
        time_0_to_1 = t1 - t0
        time_1_to_2 = t2 - t1
        
        dist_0_to_1 = self.sensor_positions[0] - self.sensor_positions[1]
        dist_1_to_2 = self.sensor_positions[1] - self.sensor_positions[2]
        
        speed_0_to_1 = dist_0_to_1 / time_0_to_1
        speed_1_to_2 = dist_1_to_2 / time_1_to_2
        
        if speed_0_to_1 < 10 or speed_0_to_1 > 50:
            return False
        if speed_1_to_2 < 10 or speed_1_to_2 > 50:
            return False
        
        return True