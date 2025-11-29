# Traffic Module

Vehicle physics and clearance time simulation for level crossing notification system.

## Structure

```
01_traffic/
├── __init__.py       # Module marker
├── vehicle.py        # Vehicle types + physics engine
├── simulator.py      # Traffic scenario simulation
├── generate.py       # Dataset generation + validation
└── data/
    └── traffic_parameters.csv
```

## Purpose

Calculate worst-case vehicle clearance times to determine when to notify intersections before train arrival.

## Usage

### Generate Dataset

```bash
make traffic-generate
# or
python -m 01_traffic.generate
```

Output: `01_traffic/data/traffic_parameters.csv`

### Validate

```bash
make validate-traffic
# or
python -m 01_traffic.generate validate
```

## Physics Models

### Stopping Distance

```
d_total = v × t_reaction + v² / (2 × a_max)
```

### Clearance Time

```
t_clearance = (distance + vehicle_length) / speed
```

Critical: Always includes vehicle length for safety.

## Vehicle Types

| Type       | Mass   | Max Speed | Accel    | Decel    | Length | Reaction |
| ---------- | ------ | --------- | -------- | -------- | ------ | -------- |
| Car        | 1500kg | 60 km/h   | 2.5 m/s² | 4.5 m/s² | 4.5m   | 1.5s     |
| SUV        | 2200kg | 60 km/h   | 2.0 m/s² | 4.0 m/s² | 5.0m   | 1.5s     |
| Truck      | 8000kg | 50 km/h   | 1.0 m/s² | 3.0 m/s² | 10.0m  | 2.0s     |
| Motorcycle | 250kg  | 70 km/h   | 4.0 m/s² | 6.0 m/s² | 2.0m   | 1.2s     |

## Traffic Densities

- **Light**: 3 vehicles, 45-60 km/h
- **Medium**: 8 vehicles, 35-55 km/h
- **Heavy**: 15 vehicles, 20-40 km/h

## Python API

```python
from 01_traffic.vehicle import VehiclePhysics, VEHICLE_TYPES
from 01_traffic.simulator import TrafficSimulator

# Physics calculations
physics = VehiclePhysics(VEHICLE_TYPES['car'])
stopping = physics.calculate_stopping_distance(60)  # km/h
print(f"Stopping distance: {stopping['total_distance']}m")

# Traffic simulation
sim = TrafficSimulator(intersection_distance=500)  # meters
result = sim.analyze_traffic_density('heavy')
print(f"Worst-case clearance: {result['max_clearance_time']}s")
```

## Integration

### With Pygame Simulation

```python
from 01_traffic.vehicle import VehiclePhysics, VEHICLE_TYPES

class Vehicle:
    def __init__(self, vehicle_type):
        self.physics = VehiclePhysics(VEHICLE_TYPES[vehicle_type])
        self.speed = 50  # km/h

    def update(self, dt, distance_ahead):
        stopping = self.physics.calculate_stopping_distance(self.speed)

        if distance_ahead < stopping['total_distance']:
            # Brake
            self.speed -= self.physics.vehicle.max_decel * dt * 3.6
        else:
            # Accelerate
            self.speed += self.physics.vehicle.max_accel * dt * 3.6
```

## Output Format

CSV columns:

- intersection_distance, traffic_density, vehicle_type
- initial_speed, time_to_crossing, stopping_distance
- clearance_time, can_stop

## Validation Tests

1. Physics equations (stopping distance, traverse time)
2. Dataset integrity (no NULLs, valid ranges)
3. Config synchronization (clearance times)

## References

- AASHTO (2018) - Stopping sight distance formulas
- Gillespie (1992) - Vehicle dynamics
- Treiber & Kesting (2013) - Traffic flow

---

**Module Version**: 1.0.0  
**Files**: 4 core files (300 lines total)  
**Dependencies**: numpy, pandas, config module
