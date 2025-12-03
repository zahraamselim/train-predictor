# Metrics Collection and Analysis

## Overview

The metrics module collects comprehensive performance data from the level crossing control system, including wait times, queue lengths, fuel consumption, emissions, and driver comfort scores.

## Pipeline Components

The metrics pipeline consists of three main modules:

1. **Network Generator** - Creates SUMO network for metrics collection
2. **Data Collector** - Runs simulation with full control system and tracks metrics
3. **Analyzer** - Processes collected data and generates performance reports

## 1. Network Generator (network_generators/metrics.py)

### Purpose

Creates a SUMO network that includes the complete level crossing infrastructure for realistic metrics collection.

### Network Structure

**Crossings and Roads**:

- Two rail crossings: west (-200m) and east (200m)
- Main roads running parallel north and south
- Traffic light intersections at crossing points
- Vertical connector roads crossing the rail

**Traffic Configuration**:

- Main road: 200 vehicles/hour per direction
- Side roads: 80 vehicles/hour
- Trucks: 50 vehicles/hour
- Trains: Configurable period (default 300 seconds)

### Output

Network files in `sumo/metrics/`:

- `metrics.nod.xml` - Node definitions
- `metrics.edg.xml` - Edge definitions
- `metrics.net.xml` - Compiled network
- `metrics.rou.xml` - Traffic flows
- `metrics.sumocfg` - SUMO configuration

### Configuration

Controlled by `config/simulation.yaml`:

```yaml
network:
  crossing_w: -200.0
  crossing_e: 200.0
  intersections:
    west: -200.0
    east: 200.0

traffic:
  main_flow: 200
  side_flow: 80
  truck_flow: 50

trains:
  period: 300
```

## 2. Data Collector (metrics/data_collector.py)

### Purpose

Runs a complete simulation with the crossing control system active, tracking both control decisions and their performance impacts.

### Control System Components

**Train Detection**:

- Three sensors positioned before crossing
- Calculates ETA/ETD when train triggers sensors
- Uses physics-based calculations or ML models

**Gate Control**:

- Closes gates at calculated threshold before ETA
- Opens gates at threshold after ETD clears
- Logs all gate operations

**Intersection Notification**:

- Notifies upstream intersections at calculated threshold
- Allows traffic signal coordination

**Engine Management**:

- Identifies vehicles waiting at closed gates
- Recommends engine shutdown when:
  - Vehicle waited ≥ 5 seconds
  - Expected remaining wait ≥ engine_off_threshold
- Tracks fuel and emissions savings

**Vehicle Rerouting** (planned):

- Evaluates alternative routes when gates close
- Makes rerouting decisions based on time savings

### Metrics Tracked

**Per-Vehicle Metrics**:

- Travel time (first seen to last seen)
- Total wait time (stationary with speed < 0.5 m/s)
- Number of stops
- Distance traveled
- Fuel consumed (driving, idling, engine off)
- CO2 emissions
- Engine-off time
- Average and maximum speed

**Wait Events**:

- Vehicle ID
- Wait duration
- Time of occurrence
- Whether engine was off

**Queue Snapshots** (every 10 seconds):

- Queue length at west crossing
- Queue length at east crossing
- Total queue length
- Average wait time
- Comfort score (0-1)

**System State**:

- Gate status (open/closed)
- Number of trains being tracked
- Number of vehicles with engines off

### Fuel and Emissions Model

Fuel consumption rates (L/s):

- Driving: 0.08 L/s
- Idling: 0.01 L/s
- Engine off: 0.0 L/s

Emissions:

- 2.31 kg CO2 per liter of fuel

**Fuel Savings Calculation**:

```
fuel_saved = engine_off_time × (idling_rate - off_rate)
emissions_saved = fuel_saved × co2_per_liter
```

### Comfort Score Calculation

Comfort score combines queue length and wait time:

```python
queue_penalty = min(queue_length / 20.0, 1.0)
wait_penalty = min(avg_wait / 60.0, 1.0)
comfort = 1.0 - (0.6 × queue_penalty + 0.4 × wait_penalty)
```

Score interpretation:

- 1.0 = Perfect (no queues, no waits)
- 0.8-1.0 = Good (short waits, small queues)
- 0.6-0.8 = Moderate (moderate waits)
- 0.4-0.6 = Poor (long waits, large queues)
- 0.0-0.4 = Very poor (excessive delays)

### Output Files

All saved to `outputs/metrics/`:

**wait_events.csv**:

```csv
vehicle_id,wait_duration,time,engine_off
car_0,12.5,180.0,true
car_5,8.2,195.0,false
```

**queue_snapshots.csv**:

```csv
time,queue_west,queue_east,total_queue,avg_wait,comfort
100.0,3,2,5,8.5,0.85
110.0,4,3,7,9.2,0.82
```

**vehicle_metrics.csv**:

```csv
vehicle_id,travel_time,total_wait,stops,distance_traveled,total_fuel,total_emissions,engine_off_time,avg_speed,max_speed
car_0,125.5,12.5,2,1850.3,10.04,23.19,8.0,14.8,19.5
```

**summary.csv**:
Single-row summary of all metrics

### Simulation Duration

Default: 3600 seconds (1 hour)

- Produces 100+ wait events
- 50+ queue snapshots
- 200+ vehicles tracked

Quick mode: 300 seconds (5 minutes)

- For testing only

## 3. Analyzer (metrics/analyzer.py)

### Purpose

Processes collected metrics and generates comprehensive performance analysis.

### Analysis Components

**Wait Time Analysis**:

- Mean, median, standard deviation
- Min, max values
- Percentiles (25th, 75th, 95th, 99th)
- Percentage of waits with engine off

**Queue Analysis**:

- Mean and max queue lengths
- Mean and min comfort scores
- Queue length percentiles
- Time-series patterns

**Vehicle Analysis**:

- Mean travel and wait times per vehicle
- Mean stops per vehicle
- Total distance traveled
- Mean speed
- Fuel and emissions per vehicle
- Engine-off time per vehicle

**Efficiency Metrics**:

- Fuel reduction percentage
- Emissions reduction percentage
- Average wait per vehicle
- Average stops per vehicle
- System comfort score

### Output

Saves to `outputs/results/metrics_analysis.json`:

```json
{
  "summary": {
    "vehicles_tracked": 250,
    "total_wait_events": 145,
    "total_engine_off_time": 387.5
  },
  "wait_analysis": {
    "total_waits": 145,
    "mean": 10.5,
    "median": 9.2,
    "std": 3.8,
    "p95": 16.2,
    "engine_off_percentage": 65.5
  },
  "queue_analysis": {
    "mean_queue": 4.2,
    "max_queue": 12,
    "mean_comfort": 0.82
  },
  "vehicle_analysis": {
    "total_vehicles": 250,
    "mean_wait_time": 10.5,
    "fuel_per_vehicle": 9.8,
    "emissions_per_vehicle": 22.6
  },
  "efficiency": {
    "fuel_reduction_percent": 3.5,
    "emissions_reduction_percent": 3.5,
    "fuel_saved_liters": 85.2,
    "emissions_saved_kg": 196.8,
    "comfort_score": 0.82
  }
}
```

## Running the Pipeline

### Full Pipeline (1 hour)

```bash
# Generate network
python -m network_generators.metrics

# Collect metrics (with control system)
python -m metrics.data_collector --duration 3600

# Analyze results
python -m metrics.analyzer
```

### Quick Pipeline (5 minutes)

```bash
python -m network_generators.metrics
python -m metrics.data_collector --duration 300
python -m metrics.analyzer
```

### With GUI

```bash
python -m metrics.data_collector --duration 3600 --gui
```

## Makefile Targets

```bash
make metrics-network   # Generate network
make metrics-collect   # Collect data (1 hour)
make metrics-quick     # Quick collection (5 min)
make metrics-analyze   # Analyze existing data
make metrics-pipeline  # Full pipeline
```

## Configuration

Edit `config/simulation.yaml`:

```yaml
simulation:
  duration: 3600
  step_length: 0.1

network:
  crossing_w: -200.0
  crossing_e: 200.0
  intersections:
    west: -200.0
    east: 200.0

metrics:
  fuel_rate_driving: 0.08 # L/s
  fuel_rate_idling: 0.01 # L/s
  fuel_rate_off: 0.0 # L/s
  co2_per_liter: 2.31 # kg CO2/L

traffic:
  main_flow: 200
  side_flow: 80
  truck_flow: 50

trains:
  period: 300
```

## Integration with Other Modules

The metrics module uses outputs from:

**ML Module**:

- Can use trained models for ETA/ETD prediction (optional)
- Falls back to physics-based calculations if models unavailable

**Thresholds Module**:

- Loads `config/thresholds_calculated.yaml` for control parameters
- Uses calculated sensor positions, gate timings, and engine-off thresholds

## Interpreting Results

### Good Performance Indicators

**Wait Times**:

- Mean < 15 seconds
- 95th percentile < 25 seconds
- Engine-off usage > 50% of waits

**Queue Lengths**:

- Mean < 5 vehicles
- Max < 15 vehicles

**Comfort Score**:

- Mean > 0.75
- Rarely drops below 0.60

**Efficiency**:

- Fuel reduction > 2%
- Emissions reduction > 2%

### Warning Signs

**Poor Wait Times**:

- Mean > 30 seconds
- 95th percentile > 60 seconds
- Indicates gates closing too early or opening too late

**Large Queues**:

- Mean > 10 vehicles
- Max > 30 vehicles
- Indicates insufficient road capacity or excessive train frequency

**Low Comfort**:

- Mean < 0.60
- Indicates poor user experience

**Low Efficiency**:

- Fuel reduction < 1%
- Indicates engine-off threshold too high or insufficient wait times

## Troubleshooting

### No data collected

**Problem**: Empty CSV files
**Cause**: Simulation error or network missing
**Solution**: Check `sumo/metrics/` exists, verify SUMO installation

### Very high wait times

**Problem**: Mean wait > 30 seconds
**Cause**: Gate closure threshold too conservative
**Solution**: Re-run threshold analysis with more data

### Low engine-off usage

**Problem**: < 20% of waits have engine off
**Cause**: Engine-off threshold too high
**Solution**: Reduce `engine_off_threshold` in thresholds config

### Low comfort scores

**Problem**: Mean comfort < 0.70
**Cause**: Long waits or large queues
**Solution**:

- Reduce train frequency
- Increase road capacity
- Optimize gate timing thresholds

### Fuel savings below expectations

**Problem**: < 1% fuel reduction
**Cause**: Short wait times or low engine-off usage
**Solution**: Expected behavior if traffic is light

## File Dependencies

```
simulation.yaml + thresholds_calculated.yaml
    │
    ├─> network_generators/metrics.py
    │       │
    │       └─> metrics.net.xml, metrics.rou.xml
    │               │
    │               └─> metrics/data_collector.py
    │                       │
    │                       ├─> wait_events.csv
    │                       ├─> queue_snapshots.csv
    │                       ├─> vehicle_metrics.csv
    │                       └─> summary.csv
    │                               │
    │                               └─> metrics/analyzer.py
    │                                       │
    │                                       └─> metrics_analysis.json
```

## Summary

The metrics module provides comprehensive performance evaluation of the level crossing control system:

1. Simulates realistic traffic with active control system
2. Tracks wait times, queues, fuel, emissions, and comfort
3. Measures effectiveness of engine management and gate timing
4. Generates detailed performance analysis and efficiency metrics

These metrics validate that the control system improves safety while minimizing delays and environmental impact.
