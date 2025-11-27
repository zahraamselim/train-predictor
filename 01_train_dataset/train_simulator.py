from typing import List

try:
    from .train_types import TRAIN_TYPES
    from .train_physics import TrainPhysics
except ImportError:
    from train_types import TRAIN_TYPES
    from train_physics import TrainPhysics

class TrainSimulator:
    """
    Runs train simulation scenarios and generates approach data.
    """
    
    def __init__(self, train_type: str, crossing_distance: float = 2000):
        """
        Args:
            train_type: 'passenger', 'freight', or 'express'
            crossing_distance: Distance from start to level crossing (meters)
        """
        self.physics = TrainPhysics(TRAIN_TYPES[train_type])
        self.train_type = train_type
        self.crossing_distance = crossing_distance
    
    def simulate_approach(self, 
                         initial_speed: float,
                         grade: float,
                         weather: str = 'clear',
                         dt: float = 0.1) -> List[dict]:
        """
        Simulate train approaching level crossing.
        
        Scenario logic:
        1. Train starts at initial_speed, some distance before crossing
        2. Train maintains speed or adjusts based on grade
        3. At appropriate distance, train begins braking
        4. Simulation ends when train reaches crossing (distance = 0)
        
        Args:
            initial_speed: Starting speed (km/h)
            grade: Average track grade (percentage, -5 to +5 typical)
            weather: 'clear', 'rain', or 'fog' (affects braking)
            dt: Simulation timestep (seconds)
        
        Returns:
            List of state dictionaries with keys:
                time, distance_to_crossing, speed, acceleration, ETA
        """
        # Convert initial speed to m/s
        speed = initial_speed / 3.6
        distance = self.crossing_distance
        time = 0.0
        
        # Weather affects braking effectiveness
        weather_factor = {'clear': 1.0, 'rain': 0.85, 'fog': 0.90}
        brake_effectiveness = weather_factor.get(weather, 1.0)
        
        # Modify brake force for weather
        original_brake = self.physics.train.brake_force_service
        self.physics.train.brake_force_service *= brake_effectiveness
        
        trajectory = []
        
        # Determine braking point based on current speed and braking capability
        # Using v² = u² + 2as => braking_distance = v² / (2 * brake_decel)
        brake_decel = self.physics.train.brake_force_service
        braking_distance = (speed ** 2) / (2 * brake_decel) * 1.3  # 30% safety margin
        
        # Track if train is making progress (to detect stuck scenarios)
        last_distance = distance
        stall_counter = 0
        
        while distance > 0:
            # Decide control action
            if distance <= braking_distance:
                braking = 'service'
            else:
                braking = None  # Maintain speed or coast
            
            # Calculate physics
            accel = self.physics.calculate_acceleration(speed, grade, braking)
            
            # Check if train can overcome resistance (not stuck)
            if not braking and accel <= 0 and speed < 5:
                # Train is stalled (can't overcome resistance at low speed)
                # Apply some throttle to keep moving
                accel = max(accel, 0.05)  # Minimum forward acceleration
            
            # Update state using kinematics
            speed_new = max(0, speed + accel * dt)
            distance_new = distance - (speed * dt + 0.5 * accel * dt**2)
            
            # Detect stalling (not making progress)
            if abs(distance - last_distance) < 0.01:
                stall_counter += 1
                if stall_counter > 100:  # Stalled for 10 seconds
                    # Force some progress to avoid infinite loop
                    distance_new = distance - 0.1
            else:
                stall_counter = 0
            
            last_distance = distance
            
            # Calculate ETA (simple: current_distance / current_speed)
            eta = distance / speed if speed > 0.1 else 0
            
            trajectory.append({
                'time': round(time, 2),
                'distance_to_crossing': round(distance, 2),
                'speed': round(speed * 3.6, 2),  # Convert back to km/h
                'acceleration': round(accel, 3),
                'ETA': round(eta, 2),
                'grade': grade,
                'weather': weather,
                'train_type': self.train_type
            })
            
            # Advance simulation
            speed = speed_new
            distance = distance_new
            time += dt
            
            # Safety check - more lenient now
            if time > 300:  # 5 minutes max (reduced from 10)
                # If we're close enough, consider it done
                if distance < 50:
                    break
                # Otherwise this scenario failed
                break
        
        # Restore original brake force
        self.physics.train.brake_force_service = original_brake
        
        return trajectory
