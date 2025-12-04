# Threshold Calculation Module

Calculates safe timing thresholds for railroad crossing control by measuring real traffic behavior.

## What This Calculates

- When gates should close before a train arrives
- When gates can open after a train leaves
- When to warn traffic lights
- Where to place train sensors

## How It Works

### Step 1: Generate Network

Creates a simple road network with one railroad crossing and traffic lights.

### Step 2: Collect Data

Runs traffic simulation and measures:

- **Vehicle clearance time**: How long cars take to cross the tracks
- **Vehicle travel time**: How long cars take from intersection to crossing

### Step 3: Analyze Data

Calculates safe thresholds using 95th percentile values with safety margins.

## Running

### Full Pipeline (1 hour simulation)

```bash
python -m thresholds.network
python -m thresholds.collector
python -m thresholds.analyzer
```

Or using make:

```bash
make th-pipeline
```

### Quick Test (5 minutes)

```bash
python -m thresholds.network
python -m thresholds.collector --duration 300
python -m thresholds.analyzer
```

Note: Short simulations give less accurate results (fewer samples).

## What Gets Measured

### Vehicle Clearance Time

How long does a car take to cross the railroad tracks?

```
Car enters crossing area (within 150m) → Car exits → Calculate time
```

Purpose: Determines how long gates must stay closed to let cars clear.

Typical values: 2-5 seconds for most vehicles

### Vehicle Travel Time

How long does a car take from traffic light to crossing?

```
Car passes intersection (300m away) → Car reaches crossing → Calculate time
```

Purpose: Determines how much advance warning traffic lights need.

Typical values: 15-20 seconds at normal speeds

## Output Files

### Data (outputs/data/)

**clearances.csv** - Crossing times for each vehicle:

```csv
vehicle_id,clearance_time,speed
car_0,3.2,15.8
car_1,4.1,14.2
```

**travels.csv** - Travel times for each vehicle:

```csv
vehicle_id,travel_time
car_5,18.2
car_8,19.5
```

### Results (outputs/results/thresholds.yaml)

```yaml
closure_before_eta: 6.8 # Close gate 6.8s before train
opening_after_etd: 3.0 # Open gate 3.0s after train
notification_time: 27.5 # Warn traffic 27.5s ahead
sensor_0: 1245.0 # First sensor position
sensor_1: 747.0 # Second sensor position
sensor_2: 373.0 # Third sensor position
max_train_speed: 39.0 # Maximum train speed (m/s)
```

### Plots (outputs/plots/)

**thresholds_analysis.png** - Six panels showing:

- Vehicle clearance time histogram
- Travel time histogram
- Clearance time vs vehicle speed
- Sensor positions bar chart
- Clearance time cumulative distribution
- Summary statistics table

## Understanding the Calculations

### Gate Closure Threshold

**Formula:**

```
95th percentile clearance time + safety margin
```

**Example:**

- 95% of cars clear in 4.8 seconds
- Safety margin: 2.0 seconds
- Result: Close gates 6.8s before train

**Why:** Ensures 95% of cars can safely clear. Safety margin handles slower drivers.

### Gate Opening Threshold

**Formula:**

```
safety margin (3.0 seconds)
```

**Example:**

- Train rear leaves crossing
- Wait 3.0 seconds
- Open gates

**Why:** Simple and conservative. Accounts for sensor delays and measurement errors.

### Notification Threshold

**Formula:**

```
95th percentile travel time + driver reaction + closure time
```

**Example:**

- Travel from intersection: 18.2s (95th percentile)
- Driver sees signal, reacts: 2.5s
- Gates close before train: 6.8s
- Total: 27.5s warning needed

**Why:** Traffic lights need enough time to stop cars before they reach the crossing approach.

### Sensor Positions

**Formula:**

```
detection_distance = notification_time × max_speed × 1.3
sensor_0 = detection_distance × 3.0 (capped at 1500m)
sensor_1 = detection_distance × 1.8 (capped at 1000m)
sensor_2 = detection_distance × 0.9 (min 300m)
```

**Example:**

- Notification: 27.5s
- Max speed: 39 m/s
- Detection distance: 27.5 × 39 × 1.3 = 1394m
- Sensor 0: 1394 × 3.0 = 4182m → capped at 1500m
- Sensor 1: 1394 × 1.8 = 2509m → capped at 1000m
- Sensor 2: 1394 × 0.9 = 1255m (no cap needed)

**Why:**

- Three sensors improve ETA/ETD prediction accuracy
- Spaced logarithmically to capture speed changes
- Capped at practical installation limits
- Max train speed from network configuration (train_fast maxSpeed)

## Configuration

Edit `thresholds/config.yaml`:

```yaml
data_collection:
  duration: 3600 # Collect for 1 hour

safety:
  margin_close: 2.0 # Safety margin for closing (seconds)
  margin_open: 3.0 # Safety margin for opening (seconds)
  driver_reaction: 2.5 # Driver reaction time (seconds)
```

### Adjusting Safety Margins

**More conservative (safer, longer waits):**

```yaml
margin_close: 4.0
margin_open: 5.0
```

**More aggressive (shorter waits, less margin):**

```yaml
margin_close: 1.0
margin_open: 2.0
```

### Adjusting Collection Duration

**Longer collection (more accurate):**

```yaml
duration: 7200 # 2 hours
```

**Shorter collection (faster testing):**

```yaml
duration: 600 # 10 minutes
```

## Expected Results

### Good Data Quality

- Clearances: 100+ samples
- Travels: 50+ samples
- Sample rate: 10+ vehicles per minute

### Typical Threshold Values

- Closure threshold: 6-8 seconds
- Opening threshold: 3 seconds
- Notification: 25-30 seconds
- Sensor 0: 1000-1500m
- Sensor 1: 600-1000m
- Sensor 2: 300-500m

## Experiments

### Experiment 1: Effect of Safety Margins

**Question:** How do safety margins affect gate closure time?

**Method:**

1. Run baseline: `margin_close: 2.0`
2. Run conservative: `margin_close: 4.0`
3. Run aggressive: `margin_close: 1.0`
4. Compare closure thresholds

**Expected:** Higher margins = earlier closure = safer but more traffic delay

### Experiment 2: Traffic Volume Impact

**Question:** Does heavy traffic change clearance times?

**Method:**

1. Edit network.py to change vehicle flow rates
2. Run with low traffic (200 veh/hr)
3. Run with high traffic (800 veh/hr)
4. Compare 95th percentile clearance times

**Expected:** Heavy traffic = longer clearance (cars queued at crossing)

### Experiment 3: Short vs Long Simulation

**Question:** How much data is needed for accurate results?

**Method:**

1. Run 5 minutes: `--duration 300`
2. Run 30 minutes: `--duration 1800`
3. Run 1 hour: `--duration 3600`
4. Compare sample counts and threshold stability

**Expected:** Longer runs = more samples = more accurate 95th percentiles

### Experiment 4: Different Train Speeds

**Question:** How does train speed affect sensor placement?

**Method:**

1. Edit network.py to change train_fast maxSpeed
2. Run with slow trains (25 m/s)
3. Run with fast trains (50 m/s)
4. Compare sensor positions

**Expected:** Faster trains = farther sensors (more detection distance needed)

## File Structure

```
thresholds/
├── __init__.py
├── config.yaml          Configuration settings
├── network.py           Generates simple network
├── collector.py         Collects vehicle timing data
├── analyzer.py          Calculates thresholds
└── README.md            This file
```

## Integration with Other Modules

These thresholds are used by:

### Main Simulation

Uses threshold values in `simulation/config.yaml`:

```yaml
crossings:
  west:
    close_before_arrival: 6.8 # From closure_before_eta
    open_after_departure: 3.0 # From opening_after_etd
    warning_time: 27.5 # From notification_time
```

### Machine Learning

Uses sensor positions for feature extraction:

```yaml
sensors:
  s0: 1245.0 # From sensor_0
  s1: 747.0 # From sensor_1
  s2: 373.0 # From sensor_2
```

### Hardware (Arduino)

Exports thresholds to C header files:

```cpp
#define CLOSURE_THRESHOLD 6.8
#define OPENING_THRESHOLD 3.0
#define NOTIFICATION_TIME 27.5
#define SENSOR_0_POS 1245.0
#define SENSOR_1_POS 747.0
#define SENSOR_2_POS 373.0
```

## Why Measure Instead of Calculate?

**Why not just use fixed values?**

Different locations have different characteristics:

- Road speeds vary (urban vs rural)
- Traffic density affects clearance times
- Road geometry changes behavior
- Local regulations differ

Measuring actual behavior ensures thresholds are appropriate for the specific location.

**Real-world example:**

- Urban crossing: 4.5s clearance, tight timing
- Rural crossing: 3.0s clearance, relaxed timing
- School zone: 6.0s clearance, extra safety

## Data Quality Indicators

### Good Quality Data

**Clearance times:**

- Mean: 3-4 seconds
- 95th percentile: 4-6 seconds
- Minimum: 1-2 seconds
- Maximum: 8-10 seconds

**Travel times:**

- Mean: 15-18 seconds
- 95th percentile: 18-22 seconds
- Minimum: 12-14 seconds
- Maximum: 25-30 seconds

### Poor Quality Data

**Warning signs:**

- Very few samples (< 50 clearances)
- Extreme outliers (> 30 second clearance)
- No variation (all times identical)
- Missing data files

**Solutions:**

- Run longer simulations
- Check network connectivity
- Verify traffic is flowing
- Increase vehicle generation rates

## Summary

The threshold calculation module:

- Measures real vehicle behavior
- Calculates safe timing parameters
- Uses statistical methods (95th percentile)
- Includes safety margins
- Outputs values for other modules
- Ensures location-specific optimization

Results are conservative by design - prioritizing safety over efficiency.
