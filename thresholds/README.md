# Threshold Analysis Pipeline

## Overview

The threshold analysis pipeline determines optimal timing parameters for the level crossing control system. It collects empirical data from SUMO traffic simulations and calculates when to close gates, open gates, notify intersections, and where to place sensors.

## Pipeline Components

The threshold pipeline consists of four main modules:

1. **Network Generator** - Creates SUMO network for data collection
2. **Data Collector** - Runs simulation and collects timing measurements
3. **Analyzer** - Calculates control thresholds from collected data
4. **Exporter** - Converts thresholds to Arduino C header file

## 1. Network Generator (network_generator.py)

### Purpose

Creates a simplified SUMO network optimized for collecting representative timing data. The network is simpler than the full simulation network because we only need to measure vehicle and train behaviors, not test complex scenarios.

### Network Structure

**Intersections and Roads**:

- Main road with two traffic light intersections at -300m and +300m
- Rail crossing at position 0m (center)
- North-south side roads connecting to crossing
- All edges use realistic speeds (50-60 km/h for roads)

**Traffic Flows**:

- Main road: 400 vehicles/hour in each direction
- Side roads: 150 vehicles/hour
- Trucks: 80 vehicles/hour (mixed with cars)
- Three train types: slow (25 m/s), medium (33 m/s), fast (39 m/s)
- Trains every 3 minutes alternating between types

### Output

Network files for SUMO:

- `thresholds.nod.xml` - Node definitions
- `thresholds.edg.xml` - Edge definitions
- `thresholds.net.xml` - Compiled network
- `thresholds.rou.xml` - Traffic flows
- `thresholds.sumocfg` - SUMO configuration

### Configuration

Controlled by `config/thresholds.yaml`:

```yaml
data_collection:
  duration: 3600
  train_period: 180
  vehicle_flow:
    main_road: 400
    side_roads: 150
    trucks: 80
```

## 2. Data Collector (data_collector.py)

### Purpose

Runs SUMO simulation with TraCI and collects three types of timing measurements needed to calculate safe control thresholds.

### Data Collection Process

**Step 1: Vehicle Clearance Times**

Measures how long vehicles take to clear the crossing area:

- Tracks when vehicle enters crossing zone (within 150m)
- Records entry speed and position
- Tracks when vehicle exits crossing zone
- Records exit speed and distance traveled
- Filters invalid samples (< 0.5s or > 30s)

**Step 2: Train Passage Times**

Measures how long trains occupy the crossing:

- Tracks train front position reaching crossing (y = 0)
- Records arrival time and speed
- Tracks train rear position clearing crossing (y = train_length)
- Records departure time
- Calculates passage time = departure - arrival
- Stores speed statistics (avg, min, max, variance)

**Step 3: Vehicle Travel Times**

Measures how long vehicles take from intersection to crossing:

- Detects vehicles passing intersection positions (-300m and +300m)
- Records start time and position for each intersection
- Tracks vehicle until it reaches crossing (within 50m)
- Calculates travel time and average speed
- Filters invalid samples (< 1.0s or > 60s)

### Output Files

Three CSV files saved to `outputs/data/`:

**gate_clearance.csv**:

```
vehicle_id,clearance_time,enter_speed,exit_speed,distance
car_0,3.2,15.8,16.2,52.3
truck_5,4.8,12.1,13.5,63.7
```

**train_passages.csv**:

```
train_id,passage_time,avg_speed,min_speed,max_speed,speed_variance,length,arrival_time
train_slow_0,6.0,25.1,24.8,25.3,0.02,150.0,180.0
train_fast_1,3.9,38.5,38.2,38.7,0.03,150.0,540.0
```

**vehicle_travels.csv**:

```
vehicle_id,intersection,travel_time,distance,avg_speed
car_12,west,18.2,285.3,15.7
car_23,east,19.5,295.1,15.1
```

### Simulation Duration

Default: 3600 seconds (1 hour)

- Yields 100+ clearance samples
- Yields 10+ train passages (20 trains expected at 180s period)
- Yields 50+ travel time samples

Quick mode: 300 seconds (5 minutes)

- For testing only, insufficient data for production use

## 3. Analyzer (analyzer.py)

### Purpose

Processes collected data and calculates all control system thresholds using statistical analysis and safety margins.

### Calculation Methods

**Gate Closure Threshold**

Determines when gates must close before train arrives:

```python
if samples >= 100:
    threshold = clearance_95th_percentile + margin_close
else:
    threshold = clearance_max + margin_close
```

- Uses 95th percentile with sufficient data (ensures 95% of vehicles clear)
- Falls back to maximum observed time if insufficient samples
- Adds safety margin (default 2.0 seconds)
- Example: 95th percentile = 4.8s, margin = 2.0s → threshold = 6.8s

**Gate Opening Threshold**

Determines when gates can open after train clears:

```python
threshold = margin_open
```

- Simple safety margin after train rear clears crossing
- Default 3.0 seconds
- Conservative approach since train passage time is deterministic

**Intersection Notification Time**

Determines when to notify upstream intersections:

```python
if samples >= 50:
    travel_time = travel_95th_percentile
else:
    travel_time = travel_max

notification = travel_time + driver_reaction + closure_threshold
```

- Uses 95th percentile travel time with sufficient data
- Accounts for driver reaction time (default 2.5s)
- Includes gate closure time
- Example: travel = 18.2s, reaction = 2.5s, closure = 6.8s → notify = 27.5s

**Sensor Positions**

Calculates optimal sensor placement before crossing:

```python
max_speed = max(observed_max, ml_max_speed)
safety_factor = 1.3
detection_distance = notification_time * max_speed * safety_factor

sensor_0 = detection_distance * 3.0
sensor_1 = detection_distance * 1.8
sensor_2 = detection_distance * 0.9
```

- Uses maximum speed from observations or ML training data
- Applies 1.3x safety factor for speed variations
- Three sensors for ETA/ETD calculation accuracy
- Scales to practical limits (300m - 1500m per sensor)

### Data Quality Checks

Minimum recommended samples:

- Clearance: 100 samples (statistical reliability of 95th percentile)
- Trains: 10 passages (covers all train types multiple times)
- Travel: 50 samples (accounts for traffic variations)

Warnings issued if insufficient data collected.

### Output

Saves to `config/thresholds_calculated.yaml`:

```yaml
closure_before_eta: 6.8
opening_after_etd: 3.0
notification_time: 27.5
sensor_positions: [1245.0, 747.0, 373.5]
max_train_speed: 38.89
engine_off_threshold: 5.0

statistics:
  clearance_samples: 156
  train_samples: 18
  travel_samples: 89
  clearance_mean: 3.42
  clearance_95th: 4.82
  clearance_max: 6.15
  passage_mean: 4.15
  passage_max: 6.02
  travel_mean: 18.31
  travel_95th: 21.45
  observed_max_speed: 38.67
  ml_max_speed: 38.89
  used_max_speed: 38.89
```

## 4. Exporter (exporter.py)

### Purpose

Converts calculated thresholds into a C header file for Arduino deployment.

### Generated Header

Creates `outputs/arduino/thresholds_config.h`:

```c
#ifndef THRESHOLDS_CONFIG_H
#define THRESHOLDS_CONFIG_H

#define SENSOR_0_POS 1245.00f
#define SENSOR_1_POS 747.00f
#define SENSOR_2_POS 373.50f

#define CLOSURE_THRESHOLD 6.80f
#define OPENING_THRESHOLD 3.00f
#define NOTIFICATION_THRESHOLD 27.50f

#define ENGINE_OFF_THRESHOLD 5.00f
#define MAX_TRAIN_SPEED 38.89f

#endif
```

### Usage in Arduino

```cpp
#include "thresholds_config.h"

if (time_until_eta <= CLOSURE_THRESHOLD) {
    closeGates();
}

if (time_since_etd >= OPENING_THRESHOLD) {
    openGates();
}
```

## Running the Pipeline

### Full Pipeline (1 hour)

```bash
make th-pipeline
```

Executes all steps:

1. Network generation (1 second)
2. Data collection (3600 seconds)
3. Threshold analysis (1 second)
4. Arduino export (1 second)

Expected data quality: 100+ clearances, 15+ trains, 80+ travels

### Quick Pipeline (5 minutes)

```bash
make th-pipeline-quick
```

Uses 300 second simulation for testing.
Warning: Insufficient data for production use.

### Individual Steps

```bash
make th-network    # Generate network
make th-collect    # Collect data (1 hour)
make th-analyze    # Analyze existing data
make th-export     # Export to Arduino header
```

## Configuration

Edit `config/thresholds.yaml`:

```yaml
data_collection:
  duration: 3600 # Simulation length (increase for more data)
  step_length: 0.1 # Simulation time step
  train_period: 180 # Train frequency (seconds)

  train:
    length: 150.0 # Train length (meters)
    min_speed: 25.0 # Slowest trains (m/s)
    typical_speed: 33.33 # Average speed (m/s)
    max_speed: 38.89 # Fastest trains (m/s)

  vehicle:
    max_speed: 20.0 # Vehicle speed limit (m/s)
    accel: 2.6 # Acceleration (m/s²)
    decel: 4.5 # Deceleration (m/s²)

  vehicle_flow:
    main_road: 400 # Main road traffic (veh/hour)
    side_roads: 150 # Side road traffic (veh/hour)
    trucks: 80 # Truck traffic (veh/hour)

safety:
  margin_close: 2.0 # Extra time before closing (seconds)
  margin_open: 3.0 # Extra time before opening (seconds)
  driver_reaction: 2.5 # Driver reaction time (seconds)
  engine_off_threshold: 5.0 # Min wait for engine shutoff (seconds)
```

## Integration with ML Pipeline

The analyzer automatically loads train parameters from ML training if available:

```python
train_params_file = Path('config/train_params.yaml')
if train_params_file.exists():
    # Use ML-derived max speed and acceleration
    params = yaml.safe_load(train_params_file)
else:
    # Use config defaults
    params = config['data_collection']['train']
```

This ensures sensor positions account for the fastest trains seen during ML training.

## Troubleshooting

### No data collected

**Problem**: CSV files are empty
**Cause**: Network error or simulation crash
**Solution**: Check `thresholds.net.xml` exists, verify SUMO installation

### Insufficient samples

**Problem**: < 100 clearances, < 10 trains, or < 50 travels
**Cause**: Simulation too short or low traffic flow
**Solution**:

- Increase `duration` to 7200 (2 hours)
- Increase `vehicle_flow` rates
- Decrease `train_period` to 120 (more frequent trains)

### Very high clearance times

**Problem**: 95th percentile > 10 seconds
**Cause**: Traffic congestion or very slow vehicles
**Solution**: Expected behavior, thresholds will adjust appropriately

### Sensors exceed practical limits

**Problem**: Sensor positions > 1500m
**Cause**: Very fast trains or long notification times
**Solution**: Automatically scaled to 1500m maximum

### Low data quality warnings

**Problem**: Analyzer reports insufficient samples
**Cause**: Short simulation or low traffic
**Solution**: Run full 1-hour simulation with default traffic flows

## File Dependencies

```
thresholds.yaml
    │
    ├─> network_generator.py
    │       │
    │       └─> thresholds.net.xml, thresholds.rou.xml
    │               │
    │               └─> data_collector.py
    │                       │
    │                       ├─> gate_clearance.csv
    │                       ├─> train_passages.csv
    │                       └─> vehicle_travels.csv
    │                               │
    │                               └─> analyzer.py
    │                                       │
    │                                       └─> thresholds_calculated.yaml
    │                                               │
    │                                               └─> exporter.py
    │                                                       │
    │                                                       └─> thresholds_config.h
```

## Summary

The threshold analysis pipeline provides data-driven control parameters:

1. Collects 100+ vehicle clearance measurements to determine safe gate closure timing
2. Measures 10+ train passages to validate gate opening timing
3. Records 50+ travel times to calculate intersection notification timing
4. Calculates sensor positions based on maximum observed train speeds
5. Exports all parameters as Arduino-compatible C header file

These empirically-derived thresholds ensure the crossing control system operates safely and efficiently for the specific train speeds and traffic patterns in your deployment scenario.
