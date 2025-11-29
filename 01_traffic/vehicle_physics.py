"""Vehicle motion and stopping distance calculations."""

try:
    from .vehicle_types import VehicleType
except ImportError:
    from vehicle_types import VehicleType


class VehiclePhysics:
    """Simulates vehicle motion using fundamental physics."""
    
    def __init__(self, vehicle_type: VehicleType):
        self.vehicle = vehicle_type
    
    def calculate_stopping_distance(self, initial_speed: float, 
                                    reaction_time: float = None) -> dict:
        """
        Calculate total stopping distance including reaction time.
        
        Args:
            initial_speed: Current speed in km/h
            reaction_time: Driver reaction time in seconds (uses vehicle default if None)
        
        Returns:
            Dictionary with distance components (m)
        """
        if reaction_time is None:
            reaction_time = self.vehicle.reaction_time
        
        speed_ms = initial_speed / 3.6
        reaction_distance = speed_ms * reaction_time
        
        if speed_ms > 0:
            braking_distance = (speed_ms ** 2) / (2 * self.vehicle.max_decel)
        else:
            braking_distance = 0
        
        return {
            'reaction_distance': round(reaction_distance, 2),
            'braking_distance': round(braking_distance, 2),
            'total_distance': round(reaction_distance + braking_distance, 2),
            'reaction_time': reaction_time
        }
    
    def calculate_time_to_traverse(self, distance: float, 
                                   initial_speed: float,
                                   accelerate: bool = False) -> float:
        """
        Calculate time to traverse a distance.
        
        Args:
            distance: Distance to cover in meters
            initial_speed: Starting speed in km/h
            accelerate: Whether vehicle accelerates from stop
        
        Returns:
            Time in seconds
        """
        speed_ms = initial_speed / 3.6
        
        if not accelerate or speed_ms >= self.vehicle.max_speed / 3.6:
            time = distance / speed_ms if speed_ms > 0 else float('inf')
            return round(time, 2)
        
        max_speed_ms = self.vehicle.max_speed / 3.6
        accel = self.vehicle.max_accel
        
        time_to_max = (max_speed_ms - speed_ms) / accel
        dist_to_max = speed_ms * time_to_max + 0.5 * accel * time_to_max**2
        
        if distance <= dist_to_max:
            time = (-speed_ms + (speed_ms**2 + 2 * accel * distance)**0.5) / accel
        else:
            remaining_dist = distance - dist_to_max
            time_at_max = remaining_dist / max_speed_ms
            time = time_to_max + time_at_max
        
        return round(time, 2)
    
    def calculate_clearance_time(self, distance_to_crossing: float,
                                initial_speed: float,
                                include_vehicle_length: bool = True) -> float:
        """
        Calculate time for vehicle to completely clear the crossing.
        
        Args:
            distance_to_crossing: Distance from vehicle front to crossing (m)
            initial_speed: Current speed in km/h
            include_vehicle_length: Add vehicle length to distance
        
        Returns:
            Time to clear in seconds
        """
        total_distance = distance_to_crossing
        if include_vehicle_length:
            total_distance += self.vehicle.length
        
        return self.calculate_time_to_traverse(
            total_distance, 
            initial_speed, 
            accelerate=False
        )