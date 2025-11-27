from .train_types import TrainType

class TrainPhysics:
    """
    Simulates train motion using fundamental physics principles.
    
    Key Physics Modeled:
    
    1. TRACTIVE EFFORT: F_traction = min(Power/velocity, F_max)
       - At low speeds, limited by wheel adhesion
       - At high speeds, limited by engine power
       - Power decreases transmission efficiency at high speeds
    
    2. ROLLING RESISTANCE: F_roll = C_rr * mass * g
       - Friction in bearings, wheel-rail contact
       - Approximately 0.0015-0.002 of weight
       - Constant with speed (simplification)
    
    3. AIR RESISTANCE: F_air = 0.5 * ρ * Cd * A * v²
       - Dominant at high speeds
       - Quadratic relationship with velocity
       - ρ = air density (1.225 kg/m³ at sea level)
    
    4. GRADE RESISTANCE: F_grade = mass * g * sin(θ)
       - Component of weight parallel to track
       - Positive for uphill (opposes motion)
       - Negative for downhill (assists motion)
    
    5. BRAKING FORCE: Applied as negative acceleration
       - Service brake: Controlled, comfortable deceleration
       - Emergency brake: Maximum safe deceleration
       - Reduced effectiveness on wet rails (coefficient of friction)
    """
    
    def __init__(self, train_type: TrainType):
        self.train = train_type
        self.g = 9.81  # gravity (m/s²)
        self.air_density = 1.225  # kg/m³
        self.rolling_resistance_coef = 0.0018  # typical for steel wheels on steel rails
        
    def calculate_tractive_force(self, velocity: float) -> float:
        """
        Calculate available engine force at given velocity.
        
        Real trains have power curves where:
        - At low speeds: Force limited by adhesion (wheels slipping)
        - At mid speeds: Constant power region (F = P/v)
        - At high speeds: Power drops due to electrical/mechanical limits
        
        Args:
            velocity: Current speed (m/s)
        
        Returns:
            Tractive force (N)
        """
        if velocity < 0.1:
            velocity = 0.1  # Avoid division by zero
        
        # Convert power to force: P = F * v => F = P / v
        power_watts = self.train.max_power * 1000
        force_from_power = power_watts / velocity
        
        # Maximum adhesion force (wheels don't slip)
        # Adhesion coefficient typically 0.25-0.35 for steel on steel
        adhesion_limit = 0.30 * self.train.mass * 1000 * self.g
        
        # Real force is minimum of these limits
        return min(force_from_power, adhesion_limit)
    
    def calculate_resistance(self, velocity: float, grade: float) -> float:
        """
        Calculate total resistance forces opposing motion.
        
        Args:
            velocity: Current speed (m/s)
            grade: Track slope (percentage: +2 = 2% uphill, -2 = 2% downhill)
        
        Returns:
            Total resistance force (N)
        """
        mass_kg = self.train.mass * 1000
        
        # Rolling resistance (bearing friction, wheel deformation)
        rolling_force = self.rolling_resistance_coef * mass_kg * self.g
        
        # Air resistance (aerodynamic drag)
        air_force = 0.5 * self.air_density * self.train.drag_coefficient * \
                    self.train.frontal_area * velocity**2
        
        # Grade resistance (gravity component)
        # Convert grade percentage to radians: sin(θ) ≈ grade/100 for small angles
        grade_force = mass_kg * self.g * (grade / 100)
        
        return rolling_force + air_force + grade_force
    
    def calculate_acceleration(self, velocity: float, grade: float, 
                              braking: str = None) -> float:
        """
        Calculate net acceleration using Newton's second law: F = ma
        
        Args:
            velocity: Current speed (m/s)
            grade: Track slope (percentage)
            braking: None, 'service', or 'emergency'
        
        Returns:
            Acceleration (m/s²) - positive speeds up, negative slows down
        """
        mass_kg = self.train.mass * 1000
        
        if braking:
            # Braking: apply negative force
            if braking == 'emergency':
                brake_force = -self.train.brake_force_emergency * mass_kg
            else:
                brake_force = -self.train.brake_force_service * mass_kg
            
            # Resistance still applies (helps braking)
            resistance = self.calculate_resistance(velocity, grade)
            net_force = brake_force - resistance
        else:
            # Accelerating/coasting: engine force vs resistance
            traction = self.calculate_tractive_force(velocity)
            resistance = self.calculate_resistance(velocity, grade)
            net_force = traction - resistance
        
        # F = ma => a = F/m
        return net_force / mass_kg
