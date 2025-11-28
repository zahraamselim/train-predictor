from dataclasses import dataclass

@dataclass
class VehicleType:
    """
    Defines characteristics for different vehicle types.
    
    Parameters based on typical urban traffic:
    - mass: Vehicle weight (kg)
    - max_speed: Typical operating speed (km/h)
    - max_accel: Maximum acceleration (m/s²)
    - max_decel: Maximum comfortable braking (m/s²)
    - length: Vehicle length (m)
    - reaction_time: Driver reaction time (s)
    """
    name: str
    mass: float
    max_speed: float
    max_accel: float
    max_decel: float
    length: float
    reaction_time: float


VEHICLE_TYPES = {
    'car': VehicleType(
        name='Car',
        mass=1500,
        max_speed=60,
        max_accel=2.5,
        max_decel=4.5,
        length=4.5,
        reaction_time=1.5
    ),
    'suv': VehicleType(
        name='SUV',
        mass=2200,
        max_speed=60,
        max_accel=2.0,
        max_decel=4.0,
        length=5.0,
        reaction_time=1.5
    ),
    'truck': VehicleType(
        name='Truck',
        mass=8000,
        max_speed=50,
        max_accel=1.0,
        max_decel=3.0,
        length=10.0,
        reaction_time=2.0
    ),
    'motorcycle': VehicleType(
        name='Motorcycle',
        mass=250,
        max_speed=70,
        max_accel=4.0,
        max_decel=6.0,
        length=2.0,
        reaction_time=1.2
    )
}