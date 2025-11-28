# Train Dataset Generation Module

Generates realistic train approach data for level crossing prediction using physics-based simulation.

## Overview

This module simulates trains approaching and clearing level crossings with realistic physics, generating training data for machine learning models. The simulation accounts for train type, speed, grade, weather conditions, and includes IR sensor readings.

## Module Structure

```
01_train_dataset/
├── config.py              # Scale configuration (real/demo)
├── train_types.py         # Train type definitions
├── train_physics.py       # Physics calculations
├── train_simulator.py     # Simulation engine
├── generate_dataset.py    # Dataset generation
└── __init__.py           # Module exports
```

## Files Description

### config.py

Manages two operational scales:

**Real Scale (meters)**

- Crossing distance: 2000m
- Sensor positions: 400m, 250m, 100m from crossing
- Train length: 150m
- Use case: ML training, realistic simulations

**Demo Scale (centimeters)**

- Board size: 75cm × 75cm
- Scale factor: 1cm = 33.33m
- Crossing distance: 60cm
- Sensor positions: 12cm, 7.5cm, 3cm
- Use case: Physical board demonstrations

Switch scales:

```python
from config import set_scale
set_scale('real')  # or 'demo'
```

### train_types.py

Defines three train types with realistic parameters:

**Passenger Train**

- Mass: 450 tonnes (6-8 coaches)
- Power: 3200 kW
- Max speed: 140 km/h
- Braking: 0.6 m/s² (service), 1.1 m/s² (emergency)

**Freight Train**

- Mass: 3500 tonnes (heavy cargo)
- Power: 4500 kW
- Max speed: 80 km/h
- Braking: 0.4 m/s² (service), 0.9 m/s² (emergency)

**Express Train**

- Mass: 380 tonnes (streamlined)
- Power: 4200 kW
- Max speed: 160 km/h
- Braking: 0.7 m/s² (service), 1.2 m/s² (emergency)

### train_physics.py

Implements realistic train physics using fundamental principles:

**Forces Calculated:**

1. **Tractive Effort** (Engine Force)

   - Power-limited at high speeds: F = Power / velocity
   - Adhesion-limited at low speeds: F = 0.30 × mass × g
   - Uses minimum of both constraints

2. **Rolling Resistance**

   - F = 0.0018 × mass × g
   - Steel-on-steel friction
   - Weather adjustment: +15% rain, +10% fog

3. **Air Resistance** (Aerodynamic Drag)

   - F = 0.5 × ρ × Cd × A × v²
   - Quadratic with speed
   - Dominant at high speeds

4. **Grade Resistance**

   - F = mass × g × (grade/100)
   - Positive grade: uphill (opposes motion)
   - Negative grade: downhill (assists motion)

5. **Braking Force**
   - Service brake: comfortable deceleration
   - Emergency brake: maximum safe deceleration
   - Weather-adjusted: -15% rain, -10% fog

**Key Methods:**

- `calculate_tractive_force(velocity)` → Engine force available
- `calculate_resistance(velocity, grade, weather)` → Total opposing forces
- `calculate_acceleration(velocity, grade, target_speed, weather, braking)` → Net acceleration

### train_simulator.py

Runs simulation scenarios with realistic dynamics.

**Key Features:**

- Train starts at operational speed (not from rest)
- Cruise control maintains target speed
- Simulates complete crossing including clearing phase
- Timestep: 0.1 seconds (adjustable)

**Crossing Status:**

- `approaching`: Train far from crossing (distance > train_length)
- `entering`: Front entering crossing (0 < distance < train_length)
- `occupying`: Train over crossing (-train_length < distance < 0)
- `clearing`: Exiting buffer zone
- `cleared`: Completely past crossing

**Usage:**

```python
from train_simulator import TrainSimulator

sim = TrainSimulator('passenger', crossing_distance=2000)
trajectory = sim.simulate_approach(
    initial_speed=100,      # km/h
    grade=0.5,              # %
    weather='clear',        # 'clear', 'rain', 'fog'
    target_speed=100        # km/h
)
```

### generate_dataset.py

Generates training datasets with diverse scenarios.

**Scenario Diversity:**

- Train types: passenger, freight, express
- Speed ranges by type (50-140 km/h)
- Grade variations: -2% to +2%
- Weather conditions: 70% clear, 20% rain, 10% fog

**IR Sensor Simulation:**

- Inverse square law: IR = K / distance²
- Realistic noise based on weather
- Three sensors at different positions

**Output Format (CSV):**

```
time, distance_to_crossing, speed, acceleration, ETA,
grade, weather, train_type, crossing_status,
IR1, IR2, IR3, scenario_id
```

**Usage:**

```python
from generate_dataset import generate_dataset

generate_dataset(
    num_scenarios=100,
    output_file='train_data.csv'
)
```

## Physics Implementation Details

### Why These Physics Matter

**For ETA Prediction:**

- Grade affects approach speed (±20% speed change on 2% grade)
- Train type determines baseline behavior
- Weather affects braking distance (+10-20%)

**For Safety:**

- Heavy freight: 644m braking distance at 100 km/h
- Weather conditions extend stopping distance
- Grade + weather = compound effect

**For Realism:**

- Heavy train + uphill = significant speed loss
- Express train + downhill = extended braking distance
- All forces interact realistically

### Force Balance

At any moment:

```
Net Force = Traction - Rolling - Air - Grade - Braking
Acceleration = Net Force / Mass
```

### Speed Control

Cruise control prevents unrealistic constant acceleration:

- If speed < target: apply engine power
- If speed ≥ target: coast (zero traction)
- Natural deceleration from resistance forces

### Weather Effects

**Rolling Resistance:**

- Clear: 0.0018 coefficient
- Rain: 0.0018 × 1.15
- Fog: 0.0018 × 1.10

**Braking:**

- Clear: 100% effectiveness
- Rain: 85% effectiveness
- Fog: 90% effectiveness

## Usage Examples

### Generate Training Data

```python
from generate_dataset import generate_dataset
from config import set_scale

# Real scale for ML training
set_scale('real')
generate_dataset(num_scenarios=100, output_file='train_data.csv')

# Demo scale for physical board
set_scale('demo')
generate_dataset(num_scenarios=10, output_file='train_data_demo.csv')
```

### Simulate Single Scenario

```python
from train_simulator import TrainSimulator

sim = TrainSimulator('freight', crossing_distance=2000)
trajectory = sim.simulate_approach(
    initial_speed=60,
    grade=1.5,
    weather='rain',
    target_speed=65
)

for point in trajectory:
    print(f"Time: {point['time']}s, Distance: {point['distance_to_crossing']}m, "
          f"Speed: {point['speed']} km/h, Status: {point['crossing_status']}")
```

### Custom Physics Analysis

```python
from train_physics import TrainPhysics
from train_types import TRAIN_TYPES

physics = TrainPhysics(TRAIN_TYPES['passenger'])

velocity = 100 / 3.6  # 100 km/h to m/s
traction = physics.calculate_tractive_force(velocity)
resistance = physics.calculate_resistance(velocity, grade=0, weather='clear')
accel = physics.calculate_acceleration(velocity, grade=0, target_speed=None)

print(f"Traction: {traction/1000:.1f} kN")
print(f"Resistance: {resistance/1000:.1f} kN")
print(f"Acceleration: {accel:.3f} m/s²")
```

## Data Quality Validation

Generated data should exhibit:

1. **Realistic speed ranges by train type**

   - Freight: 50-80 km/h
   - Passenger: 60-120 km/h
   - Express: 90-140 km/h

2. **Grade effects visible**

   - Uphill: speed decreases over time
   - Downhill: speed increases or steady

3. **Weather effects in IR readings**

   - Higher noise in rain/fog
   - Clear conditions: minimal noise

4. **Complete crossing cycles**

   - All scenarios reach "cleared" status
   - Simulation continues past crossing

5. **IR sensor response**
   - Peak when train at sensor position
   - Inverse square law behavior

## Scale Considerations

**Physics stays the same regardless of scale:**

- Speed in km/h
- Acceleration in m/s²
- Forces calculated normally

**Only distances scale:**

- Real: 2000m crossing distance
- Demo: 60cm crossing distance
- Time to cross: identical at same speed

**IR sensors scale naturally:**

- Inverse square law works at any scale
- Sensor constant K adjusts automatically

## Integration with Other Modules

This module produces CSV data consumed by:

1. **02_model_training**: Trains ML models on generated data
2. **06_validation**: Validates physics and data quality
3. **05_visualization**: Visual inspection of trajectories

Expected data format for downstream modules:

- Clean CSV with no missing values
- All scenarios complete crossing
- IR readings positive and realistic
- ETA calculated correctly

## Performance Notes

**Generation speed:**

- ~10 scenarios: 1-2 seconds
- ~100 scenarios: 5-10 seconds
- ~1000 scenarios: 1-2 minutes

**Memory usage:**

- Minimal (< 100MB for 1000 scenarios)
- Data points: ~100-300 per scenario depending on speed

**Timestep considerations:**

- Default 0.1s: good balance
- Smaller dt: more accurate, slower generation
- Larger dt: faster, may miss sensor peaks

## Troubleshooting

**Scenarios fail to complete:**

- Check speed ranges (must be > 0)
- Verify crossing distance > 0
- Ensure grade not too steep (< ±5%)

**Unrealistic speeds:**

- Verify train type parameters
- Check max_speed limits
- Review grade + weather combination

**IR readings all zero:**

- Check sensor positions
- Verify sensor_constant value
- Ensure distance calculations correct

**Simulation too slow:**

- Increase timestep (dt)
- Reduce number of scenarios
- Use real scale (fewer data points)

## Future Enhancements

Potential additions:

- Variable grade along track (currently constant)
- Wind resistance effects
- Track curvature effects
- Train length variations
- Multiple train configurations
- Tunnel/bridge environmental effects
