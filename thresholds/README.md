# Thresholds Module: Railroad Crossing Safety Parameters

This module calculates safe timing thresholds for railroad crossing control by measuring real traffic behavior. It determines when gates should close, when they can safely open, and where sensors should be placed.

## Overview

The thresholds pipeline simulates traffic flow, measures vehicle behavior, and uses statistical methods (95th percentile) to calculate conservative safety parameters. These values are used by all other modules.

## Files

### Core Files

**network.py** - Network generation

- Creates simple road network with railroad crossing
- Two intersections with traffic lights (300m from crossing)
- Bidirectional traffic with 400 vehicles/hour per direction
- Three train types (slow, medium, fast) with varied speeds
- Output: `thresholds.net.xml`, `thresholds.rou.xml`, `thresholds.sumocfg`
- Run: `python -m thresholds.network`

**collector.py** - Data collection

- Runs SUMO simulation and tracks vehicle movements
- Measures clearance times (how long to cross tracks)
- Measures travel times (intersection to crossing)
- Filters outliers and validates data
- Outputs: `outputs/data/clearances.csv`, `outputs/data/travels.csv`
- Run: `python -m thresholds.collector`

**analyzer.py** - Threshold calculation

- Loads collected data and calculates safety thresholds
- Uses 95th percentile for conservative estimates
- Adds safety margins for unexpected delays
- Calculates sensor positions based on train speeds
- Enforces sensor ordering constraint (S0 >= S1 >= S2)
- Outputs: `outputs/results/thresholds.yaml`, `outputs/results/thresholds.json`, `outputs/plots/thresholds_analysis.png`
- Run: `python -m thresholds.analyzer`

**config.yaml** - Configuration

- Collection duration: 3600s (1 hour) default
- Safety margins: close (2.0s), open (3.0s), driver reaction (2.5s)
- Configurable for different safety requirements

****init**.py** - Module initialization

- Exports NetworkGenerator, DataCollector, ThresholdAnalyzer classes

### Hardware Export

**hardware/exporters/threshold.py** - Arduino export

- Converts thresholds to C header file
- Validates sensor ordering before export
- Automatically corrects invalid sensor positions
- Generates `hardware/thresholds.h` with #define constants
- Run: `python -m hardware.exporters.threshold`

## Methodology

### Problem

Crossings need safe timing parameters:

- When to close gates before train arrives
- When to open gates after train leaves
- How much advance warning for traffic lights
- Where to place train detection sensors

Fixed values don't account for:

- Local traffic patterns
- Road geometry
- Vehicle mix (cars, trucks, buses)
- Driver behavior variations

### Solution

Measure actual traffic behavior and use statistical methods:

1. Simulate realistic traffic for 1 hour
2. Record every vehicle crossing event
3. Calculate 95th percentile (conservative)
4. Add safety margins
5. Derive sensor positions from train speeds
6. Validate and enforce sensor ordering

### Data Collection

**Network Layout**:

```
West Far <-- 500m --> West Int <-- 300m --> Crossing <-- 300m --> East Int <-- 500m --> East Far
                       (traffic            (x=0)                    (traffic
                        light)                                        light)
```

**Traffic Flows**:

- Cars: 400 vehicles/hour each direction
- Road speed: 16.67 m/s (60 km/h)
- Train types: Slow (25 m/s), Medium (33 m/s), Fast (39 m/s)
- Train frequency: One every 180 seconds (staggered)

**Measurements**:

1. **Clearance Time**: How long a vehicle occupies the crossing area

   - Trigger: Vehicle enters within 150m of crossing
   - End: Vehicle exits beyond 150m
   - Filters: 0.5s < clearance < 30s (removes invalid data)

2. **Travel Time**: How long from traffic light to crossing
   - Trigger: Vehicle passes within 50m of intersection
   - End: Vehicle reaches within 50m of crossing
   - Filters: 1s < travel < 60s (removes invalid data)

### Threshold Calculations

**Gate Closure Threshold**:

```
closure_before_eta = clearance_95th_percentile + margin_close
```

Example:

- 95% of vehicles clear in 4.8 seconds
- Safety margin: 2.0 seconds
- Result: Close gates 6.8s before train arrives

Rationale: Ensures 95% of vehicles can safely clear. Margin handles slower drivers, hesitation, or unexpected delays.

**Gate Opening Threshold**:

```
opening_after_etd = margin_open
```

Example:

- Train rear clears crossing
- Wait 3.0 seconds
- Open gates

Rationale: Simple and conservative. Accounts for sensor measurement delays and provides buffer for any residual hazards.

**Traffic Notification Threshold**:

```
notification_time = travel_95th_percentile + driver_reaction + closure_before_eta
```

Example:

- Travel time (95th percentile): 18.2s
- Driver reaction time: 2.5s
- Gate closure time: 6.8s
- Total: 27.5s warning needed

Rationale: Traffic lights must stop vehicles before they enter the approach zone. Includes time for driver to see signal, react, and brake safely.

**Sensor Positions**:

```
detection_distance = notification_time × max_train_speed × 1.3
sensor_0 = min(detection_distance × 3.0, 1500)
sensor_1 = min(detection_distance × 1.8, 1000)
sensor_2_raw = detection_distance × 0.9
sensor_2 = max(sensor_2_raw, 300)

# Enforce ordering constraint
if sensor_2 >= sensor_1:
    sensor_2 = sensor_1 × 0.8
    sensor_2 = max(sensor_2, 300)
```

Example:

- Notification: 27.5s
- Max speed: 39 m/s (fastest train type)
- Detection distance: 27.5 × 39 × 1.3 = 1394m
- Sensor 0: min(1394 × 3.0, 1500) = 1500m (capped)
- Sensor 1: min(1394 × 1.8, 1000) = 1000m (capped)
- Sensor 2 raw: 1394 × 0.9 = 1255m
- Sensor 2: 1255m (valid, less than sensor 1)

Rationale:

- Three sensors improve ETA/ETD prediction accuracy
- Logarithmically spaced to capture speed changes
- Factor 1.3 provides additional safety margin
- Caps prevent impractically long distances
- Max train speed from fastest train type in network
- Ordering constraint ensures sensors are properly sequenced

### Sensor Ordering Validation

The analyzer enforces that sensors must be in descending order of distance from crossing:

```
sensor_0 >= sensor_1 >= sensor_2
```

If sensor_2 calculates to a value greater than sensor_1 (which can happen with very high notification times), the analyzer automatically corrects it:

```python
if sensor_2 >= sensor_1:
    sensor_2 = sensor_1 * 0.8
    sensor_2 = max(sensor_2, 300)  # Maintain minimum distance
```

This ensures the ML models and hardware receive properly ordered sensor positions.

## Usage

### Full Pipeline

```bash
# Complete workflow (1 hour simulation)
make th-pipeline

# Or step by step
make th-network   # Generate network
make th-collect   # Collect data (1 hour)
make th-analyze   # Calculate thresholds
make th-export    # Export for Arduino
```

### Quick Test

```bash
# 5 minute simulation for testing
make th-quick

# Or manually
python -m thresholds.network
python -m thresholds.collector --duration 300
python -m thresholds.analyzer
```

Note: Short simulations produce fewer samples and less accurate results.

### Custom Configuration

Edit `thresholds/config.yaml`:

```yaml
data_collection:
  duration: 3600 # 1 hour

safety:
  margin_close: 2.0 # Closure safety margin
  margin_open: 3.0 # Opening safety margin
  driver_reaction: 2.5 # Driver reaction time
```

Common adjustments:

| Goal              | Parameter    | Change       |
| ----------------- | ------------ | ------------ |
| More conservative | margin_close | 2.0 to 4.0   |
| More aggressive   | margin_close | 2.0 to 1.0   |
| Longer collection | duration     | 3600 to 7200 |
| Faster testing    | duration     | 3600 to 600  |

### Direct Python

```bash
# Generate network
python -m thresholds.network --config thresholds/config.yaml

# Collect data (custom duration)
python -m thresholds.collector --duration 1800

# Analyze data
python -m thresholds.analyzer --config thresholds/config.yaml

# Export for Arduino
python -m hardware.exporters.threshold
```

## Outputs

### File Structure

```
outputs/
├── data/
│   ├── clearances.csv             # Vehicle clearance times
│   └── travels.csv                # Intersection to crossing times
├── plots/
│   └── thresholds_analysis.png    # 6-subplot comprehensive visualization
└── results/
    ├── thresholds.yaml            # Results in YAML format
    └── thresholds.json            # Results in JSON format

hardware/
└── thresholds.h                   # Arduino C header file
```

### Data Files

**clearances.csv**:

```csv
vehicle_id,clearance_time,speed
car_0,3.2,15.8
car_1,4.1,14.2
car_5,3.8,16.1
```

**travels.csv**:

```csv
vehicle_id,travel_time
car_5,18.2
car_8,19.5
car_12,17.8
```

### Results Files

**thresholds.yaml**:

```yaml
closure_before_eta: 6.8
opening_after_etd: 3.0
notification_time: 27.5
sensor_positions:
  - 1500.0
  - 1000.0
  - 800.0
max_train_speed: 39.0
statistics:
  clearance_mean: 3.8
  clearance_p95: 4.8
  clearance_max: 8.2
  travel_mean: 16.5
  travel_p95: 18.2
  travel_max: 24.3
  n_clearances: 450
  n_travels: 180
config:
  margin_close: 2.0
  margin_open: 3.0
  driver_reaction: 2.5
```

**thresholds.json**: Same data in JSON format for programmatic access

**thresholds.h**:

```cpp
#ifndef THRESHOLDS_H
#define THRESHOLDS_H

#define SENSOR_0_POS 1500.00f
#define SENSOR_1_POS 1000.00f
#define SENSOR_2_POS 800.00f

#define CLOSURE_THRESHOLD 6.80f
#define OPENING_THRESHOLD 3.00f
#define NOTIFICATION_THRESHOLD 27.50f

#define MAX_TRAIN_SPEED 39.00f

#endif
```

### Plots

**thresholds_analysis.png** (6 subplots):

1. **Clearance Time Histogram**: Distribution of crossing times with 95th percentile and threshold lines
2. **Travel Time Histogram**: Distribution of intersection-to-crossing times with 95th percentile
3. **Clearance vs Speed**: Scatter plot showing relationship between vehicle speed and clearance time
4. **Sensor Positions**: Horizontal bar chart showing calculated sensor distances
5. **Clearance CDF**: Cumulative distribution showing percentage of vehicles clearing by time
6. **Summary Table**: Key metrics and threshold values

## Expected Results

### Data Quality Indicators

**Good Quality** (1 hour simulation):

- Clearances: 400-500 samples
- Travels: 150-200 samples
- Sample rate: 7-10 vehicles/minute
- Clearance mean: 3-4 seconds
- Travel mean: 15-18 seconds

**Poor Quality** (warning signs):

- Clearances: < 100 samples
- Travels: < 50 samples
- Extreme outliers (clearance > 30s)
- Missing data files

Solutions:

- Run longer simulations
- Increase vehicle flow rates in network.py
- Check network connectivity
- Verify traffic is flowing

### Typical Threshold Values

**Conservative Configuration** (margin_close: 4.0):

- Closure: 7-9 seconds
- Opening: 3 seconds
- Notification: 28-32 seconds

**Standard Configuration** (margin_close: 2.0):

- Closure: 6-8 seconds
- Opening: 3 seconds
- Notification: 25-30 seconds

**Aggressive Configuration** (margin_close: 1.0):

- Closure: 5-6 seconds
- Opening: 3 seconds
- Notification: 22-26 seconds

**Sensor Positions** (typical):

- Sensor 0: 1200-1500m (capped at 1500m)
- Sensor 1: 800-1000m (capped at 1000m)
- Sensor 2: 400-800m (minimum 300m, enforced < S1)

## Troubleshooting

### Sensor Ordering Issues

**Problem**: Your results show sensor_2 > sensor_1

**Symptoms**:

```
Sensor 0: 1500m
Sensor 1: 1000m
Sensor 2: 1850m  # Wrong!
```

**Root Causes**:

1. Unusually high travel times (22+ seconds vs typical 18s)
2. Very high clearance times (13+ seconds vs typical 5s)
3. Low sample counts causing statistical instability

**Solutions**:

The analyzer automatically fixes this, but to address the root cause:

1. Check your data collection:

   ```bash
   cat outputs/results/thresholds.yaml | grep "n_clearances\|n_travels"
   ```

   Should be > 400 clearances and > 150 travels

2. Check your network geometry:

   ```bash
   grep "west_int\|east_int" thresholds.nod.xml
   ```

   Should show x=-300 and x=300

3. Re-run with longer simulation:

   ```bash
   python -m thresholds.collector --duration 3600
   python -m thresholds.analyzer
   ```

4. Reduce safety margins if values are too conservative:
   ```yaml
   # In thresholds/config.yaml
   safety:
     margin_close: 1.5 # Reduced from 2.0
   ```

### High Clearance Times

**Problem**: clearance_p95 > 10 seconds (typical is 4-5s)

**Causes**:

- Network congestion
- Vehicles queuing at crossing
- Incorrect crossing zone definition

**Check**:

```bash
head -20 outputs/data/clearances.csv
python3 -c "import pandas as pd; df = pd.read_csv('outputs/data/clearances.csv'); print(df.describe())"
```

### High Travel Times

**Problem**: travel_p95 > 22 seconds (typical is 18s)

**Causes**:

- Intersections farther than 300m
- Traffic light timing issues
- Low vehicle speeds

**Check network distances**:

```bash
grep "node id" thresholds.nod.xml | grep "int\|crossing"
```

## Integration with Other Modules

### Machine Learning Module

Uses sensor positions for feature extraction:

```yaml
# ml/config.yaml
sensors:
  s0: 1500.0 # From sensor_positions[0]
  s1: 1000.0 # From sensor_positions[1]
  s2: 800.0 # From sensor_positions[2]
  crossing: 3000.0
```

The ML models train on data from sensors at these positions to predict ETA/ETD.

### Simulation Module

Uses threshold values for crossing control:

```yaml
# simulation/config.yaml
crossings:
  west:
    close_before_arrival: 6.8 # From closure_before_eta
    open_after_departure: 3.0 # From opening_after_etd
    warning_time: 27.5 # From notification_time
```

### Hardware (Arduino)

Includes thresholds header:

```cpp
#include "thresholds.h"

void setup() {
    // Use defined constants
    float closure_time = CLOSURE_THRESHOLD;
    float sensor_0 = SENSOR_0_POS;
}
```

## Why Measure Instead of Calculate?

**Different locations have different characteristics**:

Urban crossing:

- Higher traffic density
- Frequent stops and starts
- Longer clearance times (queuing)
- Result: 8-10s closure, 30-35s notification

Rural crossing:

- Lower traffic density
- Free-flowing traffic
- Shorter clearance times
- Result: 5-6s closure, 20-25s notification

School zone:

- Pedestrians and buses
- Variable speeds
- Extra caution needed
- Result: 10-12s closure, 35-40s notification

Measuring actual behavior ensures thresholds are location-appropriate and accounts for factors that are difficult to model analytically.

## Failed Experiments

### Experiment 1: Fixed 5-Second Closure

**Hypothesis**: Simple fixed 5-second closure should be sufficient

**Method**: Use `closure_before_eta = 5.0` regardless of measured data

**Results**:

- 15% of vehicles trapped between gates
- Insufficient time for slow or hesitant drivers
- No accounting for vehicle queue buildup

**Analysis**: Fixed values ignore actual vehicle behavior and traffic patterns

**Lesson**: Must measure real clearance times. 95th percentile provides appropriate safety margin.

### Experiment 2: Mean Instead of 95th Percentile

**Hypothesis**: Mean clearance time should be sufficient with safety margin

**Method**: `closure = mean(clearances) + margin_close`

**Results**:

- Using mean (3.8s) + margin (2.0s) = 5.8s
- 50% of vehicles need more than mean time
- Safety margin insufficient for upper half of distribution
- 20-30% of vehicles at risk

**Analysis**: Mean provides no statistical guarantee. Half of vehicles exceed mean by definition.

**Lesson**: 95th percentile ensures safety for vast majority. Mean is inappropriate for safety-critical systems.

### Experiment 3: No Safety Margins

**Hypothesis**: 95th percentile alone should be safe enough

**Method**: `closure = clearance_95th_percentile` (no added margin)

**Results**:

- 5% of vehicles exceed threshold by definition
- No buffer for measurement errors
- No accommodation for driver hesitation
- Sensor delays unaccounted for

**Analysis**: Real-world systems have delays, errors, and uncertainties that statistical measures alone cannot handle.

**Lesson**: Safety margins are essential. They account for system imperfections and unexpected behavior beyond the measured distribution.

### Experiment 4: Too Short Simulation (60 seconds)

**Hypothesis**: 1 minute should be enough to understand traffic

**Method**: `--duration 60`

**Results**:

- Clearances: 8 samples
- Travels: 3 samples
- High variance between runs (40-60%)
- 95th percentile unreliable with small sample

**Analysis**: Insufficient samples lead to unstable statistics. 95th percentile requires adequate sample size.

**Lesson**: Need 100+ clearances and 50+ travels for stable results. 1 hour simulation provides 400+ clearances.

### Experiment 5: Ignoring Travel Times

**Hypothesis**: Only clearance time matters for notification

**Method**: `notification = closure_before_eta` (no travel time component)

**Results**:

- Traffic lights activate only 6.8s before train
- Vehicles already approaching crossing when lights change
- Cannot stop in time from intersection
- High collision risk

**Analysis**: Notification must account for time needed for vehicles to reach crossing from upstream traffic lights.

**Lesson**: Travel time is critical component. Vehicles need warning before they enter approach zone.

### Experiment 6: Single Sensor Position

**Hypothesis**: One sensor at notification distance is sufficient

**Method**: Calculate single sensor: `notification_time × max_speed`

**Results**:

- Single sensor: 1074m from crossing
- Cannot detect speed changes
- No redundancy if sensor fails
- ETA/ETD accuracy: ±2.5s

**Analysis**: Single sensor provides only one data point. Cannot compute acceleration or validate speed measurements.

**Lesson**: Multiple sensors dramatically improve prediction. Three sensors enable speed trend analysis and provide redundancy.

### Experiment 7: Same Margin for All Vehicles

**Hypothesis**: All vehicles need same safety margin

**Method**: Fixed 2.0s margin regardless of vehicle characteristics

**Results**:

- Works well for passenger cars
- Insufficient for trucks (longer, slower)
- Excessive for motorcycles (short, fast)
- One-size-fits-all suboptimal

**Analysis**: Different vehicle types have different clearance characteristics, but system must accommodate worst case.

**Lesson**: Use 95th percentile across all vehicle types. This automatically accounts for slowest/longest vehicles in the distribution.

### Experiment 8: No Sensor Ordering Validation

**Hypothesis**: Calculated sensor positions are always valid

**Method**: Use raw calculated values without validation

**Results**:

- High notification times caused sensor_2 > sensor_1
- ML models received invalid sensor configuration
- Prediction logic assumed S0 > S1 > S2
- System failures in edge cases

**Analysis**: Mathematical calculations can produce logically invalid results when parameters are extreme.

**Lesson**: Always validate constraints and enforce logical ordering. Automated correction ensures system reliability.

## Summary

The thresholds module:

- Simulates realistic traffic for data collection
- Measures vehicle clearance and travel times
- Uses 95th percentile for statistical safety
- Adds safety margins for uncertainties
- Calculates sensor positions from train speeds
- Validates and enforces sensor ordering
- Exports values for all other modules
- Ensures location-specific optimization

Results are conservative by design, prioritizing safety over efficiency. The 95th percentile plus margins approach ensures the system handles the vast majority of real-world scenarios safely.
