# Sensors Module

IR sensor positioning and train detection logic.

## Structure

```
02_sensors/
├── __init__.py        # Module marker
├── sensor_array.py    # Detection logic, timing
├── positioning.py     # Position calculation + validation
└── README.md
```

## Purpose

1. Calculate optimal sensor placement based on traffic clearance requirements
2. Detect train presence at multiple points
3. Record timing for speed/ETA calculation

## Usage

### Calculate Positions

```bash
make sensors-calculate
# or
python -m 02_sensors.positioning calculate
```

### Apply to Config

```bash
make sensors-apply
# or
python -m 02_sensors.positioning apply
```

### Validate

```bash
make sensors-validate
# or
python -m 02_sensors.positioning validate
```

## Positioning Algorithm

```
Required warning time = max_clearance + safety_buffer + gate_offset
Detection distance = fastest_train_speed × warning_time

Sensor 0 (furthest) = 100% of detection distance
Sensor 1 (middle)   = 60% of detection distance
Sensor 2 (nearest)  = 30% of detection distance
```

## Detection Logic

Binary detection:

- Sensor triggers when train passes over it
- Records entry time (train front reaches sensor)
- Records exit time (train rear leaves sensor)

Speed calculation:

```
speed = distance_between_sensors / time_between_detections
```

## Python API

```python
from 02_sensors.sensor_array import SensorArray

# Initialize with positions from config
sensors = SensorArray()

# Update during simulation
events = sensors.update(
    train_distance=1500,  # meters from crossing
    current_time=10.5,    # seconds
    train_length=150      # meters
)

# Get detection times
times = sensors.get_detection_times()
print(times['sensor_0']['entry_time'])

# Calculate speed
speed = sensors.calculate_speed(sensor1_id=0, sensor2_id=1)
print(f"Speed: {speed * 3.6:.1f} km/h")
```

## Integration

### With Traffic Module

Traffic clearance times determine sensor distance:

```python
from 01_traffic import generate_traffic_parameters
from 02_sensors.positioning import calculate_sensor_positions

# Step 1: Generate traffic data
generate_traffic_parameters()

# Step 2: Calculate sensor positions based on clearance
positions = calculate_sensor_positions()
```

### With Train Module (Coming Next)

Sensors detect train and record timings for ETA:

```python
from 02_sensors.sensor_array import SensorArray
from 03_train import TrainSimulator

sensors = SensorArray()
train = TrainSimulator(train_type='express')

for t in range(simulation_time):
    position = train.get_position(t)
    events = sensors.update(position, t, train.length)

    if len(events) > 0:
        print(f"Sensor {events[0]['sensor_id']} detected at t={t}s")
```

---

**Module Version**: 1.0.0  
**Files**: 3 files (~300 lines)  
**Dependencies**: config module
