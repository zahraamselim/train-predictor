try:
    from .train_types import TrainType
except ImportError:
    from train_types import TrainType


class TrainPhysics:
    """Simulates train motion using fundamental physics principles."""
    
    def __init__(self, train_type: TrainType):
        self.train = train_type
        self.g = 9.81
        self.air_density = 1.225
        self.rolling_resistance_coef = 0.0018
    
    def calculate_tractive_force(self, velocity: float) -> float:
        """
        Calculate available engine force at given velocity.
        
        Args:
            velocity: Current speed in m/s
        
        Returns:
            Tractive force in N
        """
        if velocity < 0.1:
            velocity = 0.1
        
        power_watts = self.train.max_power * 1000
        force_from_power = power_watts / velocity
        adhesion_limit = 0.30 * self.train.mass * 1000 * self.g
        
        return min(force_from_power, adhesion_limit)
    
    def calculate_resistance(self, velocity: float, grade: float, weather: str = 'clear') -> float:
        """
        Calculate total resistance forces opposing motion.
        
        Args:
            velocity: Current speed in m/s
            grade: Track slope in percentage
            weather: 'clear', 'rain', or 'fog'
        
        Returns:
            Total resistance force in N
        """
        mass_kg = self.train.mass * 1000
        
        rolling_coef = self.rolling_resistance_coef
        if weather == 'rain':
            rolling_coef *= 1.15
        elif weather == 'fog':
            rolling_coef *= 1.10
        
        rolling_force = rolling_coef * mass_kg * self.g
        air_force = 0.5 * self.air_density * self.train.drag_coefficient * \
                    self.train.frontal_area * velocity**2
        grade_force = mass_kg * self.g * (grade / 100)
        
        total_resistance = rolling_force + air_force + grade_force
        
        return total_resistance
    
    def calculate_acceleration(self, velocity: float, grade: float, 
                              target_speed: float = None,
                              weather: str = 'clear',
                              braking: str = None) -> float:
        """
        Calculate net acceleration using Newton's second law with speed control.
        
        Args:
            velocity: Current speed in m/s
            grade: Track slope in percentage
            target_speed: Target cruising speed in m/s (None for no limit)
            weather: 'clear', 'rain', or 'fog'
            braking: None, 'service', or 'emergency'
        
        Returns:
            Acceleration in m/s²
        """
        mass_kg = self.train.mass * 1000
        
        if braking:
            brake_coef = (self.train.brake_force_emergency if braking == 'emergency' 
                         else self.train.brake_force_service)
            
            if weather == 'rain':
                brake_coef *= 0.85
            elif weather == 'fog':
                brake_coef *= 0.90
            
            brake_force = -brake_coef * mass_kg
            resistance = self.calculate_resistance(velocity, grade, weather)
            net_force = brake_force - resistance
        else:
            resistance = self.calculate_resistance(velocity, grade, weather)
            
            if target_speed is not None and velocity >= target_speed - 0.5:
                traction = 0
            else:
                traction = self.calculate_tractive_force(velocity)
            
            net_force = traction - resistance
        
        return net_force / mass_kg