"""Physics-based ETA calculator from sensor timings."""

import math
from typing import Dict, List, Optional


class ETACalculator:
    """
    Calculate train ETA using sensor detection timings.
    
    Uses kinematic equations with measured speed and acceleration
    between sensors to predict arrival time.
    """
    
    def __init__(self, sensor_positions: List[float]):
        """
        Initialize calculator with sensor positions.
        
        Args:
            sensor_positions: List of [furthest, middle, nearest] distances
                from crossing in meters
        """
        self.sensor_positions = sensor_positions
        
        if len(sensor_positions) != 3:
            raise ValueError("Requires exactly 3 sensor positions")
        
        # Verify ordering (furthest to nearest)
        if not (sensor_positions[0] > sensor_positions[1] > sensor_positions[2]):
            raise ValueError("Sensors must be ordered: furthest to nearest")
    
    def calculate_eta_simple(
        self,
        sensor_timings: Dict[str, float]
    ) -> float:
        """
        Simple ETA: Constant speed assumption.
        
        Uses most recent speed (between sensors 1-2) to predict ETA.
        
        Args:
            sensor_timings: Dict with 'sensor_0_entry', 'sensor_1_entry', 
                           'sensor_2_entry' in seconds
        
        Returns:
            ETA in seconds from sensor 2 detection
        """
        # Extract timing
        t0 = sensor_timings['sensor_0_entry']
        t1 = sensor_timings['sensor_1_entry']
        t2 = sensor_timings['sensor_2_entry']
        
        # Calculate speed between sensors 1 and 2 (most recent)
        distance_1_to_2 = self.sensor_positions[1] - self.sensor_positions[2]
        time_1_to_2 = t2 - t1
        
        if time_1_to_2 <= 0:
            return float('inf')
        
        speed = distance_1_to_2 / time_1_to_2  # m/s
        
        # Distance remaining from sensor 2 to crossing
        remaining_distance = self.sensor_positions[2]
        
        # ETA = distance / speed
        eta = remaining_distance / speed if speed > 0 else float('inf')
        
        return round(eta, 2)
    
    def calculate_eta_with_acceleration(
        self,
        sensor_timings: Dict[str, float]
    ) -> float:
        """
        Advanced ETA: Accounts for acceleration/deceleration.
        
        Calculates acceleration between sensors and uses kinematic
        equation to predict ETA.
        
        Args:
            sensor_timings: Dict with sensor entry times
        
        Returns:
            ETA in seconds from sensor 2 detection
        """
        # Extract timings
        t0 = sensor_timings['sensor_0_entry']
        t1 = sensor_timings['sensor_1_entry']
        t2 = sensor_timings['sensor_2_entry']
        
        # Calculate speeds
        dist_0_to_1 = self.sensor_positions[0] - self.sensor_positions[1]
        dist_1_to_2 = self.sensor_positions[1] - self.sensor_positions[2]
        
        time_0_to_1 = t1 - t0
        time_1_to_2 = t2 - t1
        
        if time_0_to_1 <= 0 or time_1_to_2 <= 0:
            return float('inf')
        
        speed_0_to_1 = dist_0_to_1 / time_0_to_1  # m/s
        speed_1_to_2 = dist_1_to_2 / time_1_to_2  # m/s
        
        # Calculate acceleration
        acceleration = (speed_1_to_2 - speed_0_to_1) / time_1_to_2
        
        # Distance remaining from sensor 2 to crossing
        remaining_distance = self.sensor_positions[2]
        current_speed = speed_1_to_2
        
        # If acceleration is negligible, use constant speed
        if abs(acceleration) < 0.05:  # Less than 0.05 m/s²
            eta = remaining_distance / current_speed
        else:
            # Use kinematic equation: d = v*t + 0.5*a*t²
            # Rearranged: 0.5*a*t² + v*t - d = 0
            # Solve for t using quadratic formula
            
            a = 0.5 * acceleration
            b = current_speed
            c = -remaining_distance
            
            discriminant = b**2 - 4*a*c
            
            if discriminant < 0:
                # No real solution, fallback to constant speed
                eta = remaining_distance / current_speed
            else:
                # Use positive root (future time)
                t1 = (-b + math.sqrt(discriminant)) / (2*a)
                t2 = (-b - math.sqrt(discriminant)) / (2*a)
                
                # Choose positive time
                if t1 > 0:
                    eta = t1
                elif t2 > 0:
                    eta = t2
                else:
                    # Fallback
                    eta = remaining_distance / current_speed
        
        return round(max(0, eta), 2)
    
    def calculate_eta_robust(
        self,
        sensor_timings: Dict[str, float],
        use_acceleration: bool = True
    ) -> Dict[str, float]:
        """
        Robust ETA calculation with multiple estimates.
        
        Args:
            sensor_timings: Dict with sensor entry times
            use_acceleration: Whether to account for acceleration
        
        Returns:
            Dict with multiple ETA estimates and diagnostics
        """
        # Simple estimate (constant speed)
        eta_simple = self.calculate_eta_simple(sensor_timings)
        
        # Advanced estimate (with acceleration)
        if use_acceleration:
            eta_advanced = self.calculate_eta_with_acceleration(sensor_timings)
        else:
            eta_advanced = eta_simple
        
        # Calculate speeds for diagnostics
        t0 = sensor_timings['sensor_0_entry']
        t1 = sensor_timings['sensor_1_entry']
        t2 = sensor_timings['sensor_2_entry']
        
        dist_0_to_1 = self.sensor_positions[0] - self.sensor_positions[1]
        dist_1_to_2 = self.sensor_positions[1] - self.sensor_positions[2]
        
        speed_0_to_1 = dist_0_to_1 / (t1 - t0)  # m/s
        speed_1_to_2 = dist_1_to_2 / (t2 - t1)  # m/s
        
        acceleration = (speed_1_to_2 - speed_0_to_1) / (t2 - t1)
        
        return {
            'eta_simple': eta_simple,
            'eta_advanced': eta_advanced,
            'eta_final': eta_advanced,  # Use advanced as final
            'speed_0_to_1_ms': round(speed_0_to_1, 2),
            'speed_1_to_2_ms': round(speed_1_to_2, 2),
            'speed_0_to_1_kmh': round(speed_0_to_1 * 3.6, 2),
            'speed_1_to_2_kmh': round(speed_1_to_2 * 3.6, 2),
            'acceleration': round(acceleration, 3),
            'is_accelerating': acceleration > 0.05,
            'is_decelerating': acceleration < -0.05
        }
    
    def validate_timings(self, sensor_timings: Dict[str, float]) -> bool:
        """
        Validate sensor timings are reasonable.
        
        Args:
            sensor_timings: Dict with sensor entry times
        
        Returns:
            True if timings are valid
        """
        required_keys = ['sensor_0_entry', 'sensor_1_entry', 'sensor_2_entry']
        
        # Check all keys present
        if not all(key in sensor_timings for key in required_keys):
            return False
        
        t0 = sensor_timings['sensor_0_entry']
        t1 = sensor_timings['sensor_1_entry']
        t2 = sensor_timings['sensor_2_entry']
        
        # Check None values
        if t0 is None or t1 is None or t2 is None:
            return False
        
        # Check proper ordering (train moves forward)
        if not (t0 < t1 < t2):
            return False
        
        # Check reasonable time deltas (not too fast or too slow)
        time_0_to_1 = t1 - t0
        time_1_to_2 = t2 - t1
        
        # Speeds should be between 10 m/s (36 km/h) and 50 m/s (180 km/h)
        dist_0_to_1 = self.sensor_positions[0] - self.sensor_positions[1]
        dist_1_to_2 = self.sensor_positions[1] - self.sensor_positions[2]
        
        speed_0_to_1 = dist_0_to_1 / time_0_to_1
        speed_1_to_2 = dist_1_to_2 / time_1_to_2
        
        if speed_0_to_1 < 10 or speed_0_to_1 > 50:
            return False
        if speed_1_to_2 < 10 or speed_1_to_2 > 50:
            return False
        
        return True