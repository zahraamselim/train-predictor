from dataclasses import dataclass

@dataclass
class TrainType:
    """
    Defines characteristics for different train types.
    
    Parameters are based on typical railway engineering values:
    - mass: Total train weight (tonnes)
    - max_power: Engine power (kW) - determines acceleration capability
    - max_speed: Maximum operational speed (km/h)
    - brake_force_service: Normal braking deceleration (m/s²)
    - brake_force_emergency: Emergency braking deceleration (m/s²)
    - frontal_area: Cross-sectional area (m²) - affects air resistance
    - drag_coefficient: Aerodynamic efficiency (dimensionless)
    """
    name: str
    mass: float  # tonnes
    max_power: float  # kW
    max_speed: float  # km/h
    brake_force_service: float  # m/s²
    brake_force_emergency: float  # m/s²
    frontal_area: float  # m²
    drag_coefficient: float


# Realistic train type definitions
TRAIN_TYPES = {
    'passenger': TrainType(
        name='Passenger',
        mass=450,  # 6-8 coaches
        max_power=3200,  # Modern EMU
        max_speed=140,
        brake_force_service=0.6,
        brake_force_emergency=1.1,
        frontal_area=10.5,
        drag_coefficient=0.7
    ),
    'freight': TrainType(
        name='Freight',
        mass=3500,  # Heavy cargo
        max_power=4500,  # Diesel locomotive
        max_speed=80,
        brake_force_service=0.4,
        brake_force_emergency=0.9,
        frontal_area=11.0,
        drag_coefficient=0.9
    ),
    'express': TrainType(
        name='Express',
        mass=380,  # Lighter, streamlined
        max_power=4200,
        max_speed=160,
        brake_force_service=0.7,
        brake_force_emergency=1.2,
        frontal_area=9.5,
        drag_coefficient=0.5
    )
}