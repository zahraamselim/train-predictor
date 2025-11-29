# Train Module

Train trajectory simulation and dataset generation for ETA prediction.

## Structure

```
03_train/
├── __init__.py      # Module marker
├── train.py         # Train types + physics engine
├── simulator.py     # Simulation + dataset generation + validation
└── data/
    └── train_data.csv
```

## Purpose

Generate realistic train approach trajectories with sensor detection events for ML training.

## Usage

### Generate Dataset

```bash
# Full dataset (100 scenarios)
make train-generate

# Smaller datasets
make train-generate-demo   # 10 scenarios
make train-generate-small  # 50 scenarios
```

### Validate

```bash
make train-validate
```

## Physics Model

### Train Motion

Newton's second law: `F_net = m × a`

Forces:

- **Tractive force**: `P / v` (power-limited) or adhesion-limited
- **Rolling resistance**: `μ × m × g`
- **Air resistance**: `0.5 × ρ × Cd × A × v²`
- **Grade resistance**: `m × g × (grade / 100)`

Net acceleration:

```
a = (F_traction - F_resistance) / m
```

### Speed Control

Trains maintain target cruising speed:

- If below target: apply traction
- If above target: coast (no traction)
- Smooth transition near target (proportional control)

## Train Types

| Type      | Mass (t) | Power (kW) | Max Speed (km/h) | Braking (g) |
| --------- | -------- | ---------- | ---------------- | ----------- |
| Passenger | 450      | 3200       | 140              | 0.6 / 1.1   |
| Freight   | 3500     | 4500       | 80               | 0.4 / 0.9   |
| Express   | 380      | 4200       | 160              | 0.7 / 1.2   |

## Dataset Format

CSV columns:

- `scenario_id`: Unique scenario identifier
- `train_type`: passenger/freight/express
- `initial_speed`, `grade`, `weather`: Scenario parameters
- `sensor_0/1/2_entry`: Detection times at each sensor (s)
- `time_0_to_1`, `time_1_to_2`: Transit times between sensors (s)
- `speed_0_to_1`, `speed_1_to_2`: Calculated speeds (km/h)
- `ETA`: Actual time to arrival at sensor 2 (s)
- `sensor_0/1/2_pos`: Sensor positions (m)

## Generation Parameters

Random variations for each scenario:

- Train type: Random (passenger/freight/express)
- Speed: Within type's min/max range
- Grade: -2% to +2% (uphill/downhill)
- Weather: 70% clear, 20% rain, 10% fog
- Target speed: ±5 km/h from initial

## Python API

```python
from 03_train.train import TrainPhysics, TRAIN_TYPES
from 03_train.simulator import TrainSimulator

# Physics calculations
physics = TrainPhysics(TRAIN_TYPES['express'])
force = physics.calculate_tractive_force(velocity=20)  # m/s
accel = physics.calculate_acceleration(20, grade=1.5)

# Trajectory simulation
sim = TrainSimulator('passenger', crossing_distance=3000)
trajectory = sim.simulate_approach(
    initial_speed=120,  # km/h
    grade=0.5,          # %
    weather='clear'
)

# Each point in trajectory:
for point in trajectory:
    print(f"t={point['time']}s: d={point['distance_to_crossing']}m, "
          f"v={point['speed']}km/h, ETA={point['ETA']}s")
```

## Integration

### With Sensors Module

Sensors detect train and record timing:

```python
from 02_sensors.sensor_array import SensorArray
from 03_train.simulator import TrainSimulator

sensors = SensorArray()
sim = TrainSimulator('express')

trajectory = sim.simulate_approach(140, 0, 'clear')

for point in trajectory:
    events = sensors.update(
        point['distance_to_crossing'],
        point['time'],
        train_length=150
    )

    for event in events:
        if event['event'] == 'entry':
            print(f"Sensor {event['sensor_id']} at t={event['time']:.2f}s")
```

### With Traffic Module (Next)

Train ETA determines when to notify intersections:

```python
from 03_train.simulator import TrainSimulator
from 01_traffic.simulator import TrafficSimulator

# Train approaching
train_eta = 45.0  # seconds

# Check if intersection can clear in time
traffic = TrafficSimulator(intersection_distance=500)
analysis = traffic.analyze_traffic_density('heavy')

if analysis['max_clearance_time'] < train_eta - 10:
    print("Sufficient time for traffic to clear")
else:
    print("WARNING: Insufficient clearance time!")
```

## Validation Tests

1. Physics correctness (forces positive, acceleration calculated)
2. Dataset integrity (no NULLs, required columns)
3. ETA values positive
4. Sensor timing ordered (0 < 1 < 2)
5. Speed ranges realistic

## Typical Results

From 100 scenarios:

- Valid scenarios: 100/100
- Speed range: 28-162 km/h
- ETA range: 18-108 seconds
- Train mix: ~33% each type

## Edge Cases Handled

- **Train stalling**: Detects insufficient power for grade
- **Timeout**: Stops if simulation takes too long
- **Sensor misses**: Discards scenarios where sensors don't all trigger
- **Speed limiting**: Enforces train max speed

## References

- Train motion: "Railway Vehicle Dynamics" by Iwnicki (2006)
- Traction physics: "The Fundamentals of Railway Traction" by Armstrong (1983)
- Resistance: Davis equation for railway resistance

---

**Module Version**: 1.0.0  
**Files**: 3 files (~400 lines)  
**Dependencies**: config, 02_sensors
