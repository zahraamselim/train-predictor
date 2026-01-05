# Thresholds Module

Calculates safe timing parameters for railway crossing control by measuring real traffic behavior.

## What It Does

Determines three critical values:

1. **Gate Closure**: When to close gates before train arrives
2. **Gate Opening**: When to open gates after train leaves
3. **Sensor Positions**: Where to place train detection sensors

## Why Measure?

Different locations need different timings:

- Urban crossings: More traffic, longer clearance times
- Rural crossings: Less traffic, faster clearance
- School zones: Extra caution needed

Fixed values don't account for local conditions. Measuring actual behavior ensures safety.

## How It Works

### 1. Simulate Traffic (1 hour)

Creates realistic traffic scenario:

- 800 cars per hour (400 each direction)
- Road speed: 60 km/h
- Three train types: Slow (25 m/s), Medium (33 m/s), Fast (39 m/s)
- Traffic lights 300m from crossing

### 2. Measure Behavior

**Clearance Time**: How long vehicles take to cross tracks

- Measures from entering crossing to fully clearing
- Typical: 3-5 seconds for cars

**Travel Time**: How long from traffic light to crossing

- Measures from passing intersection to reaching crossing
- Typical: 16-18 seconds

### 3. Calculate Thresholds

Uses **95th percentile** - the value that 95% of measurements fall below.

**Why 95th percentile?**
Like a fire drill: you don't use average evacuation time, you plan for the slowest 95% of people. This ensures safety for almost everyone.

**Gate Closure**:

```
closure = 95th percentile clearance + 2 second safety margin
```

Example: 4.8s (95th) + 2.0s = 6.8 seconds before train

**Gate Opening**:

```
opening = 3 second safety margin
```

Simple: wait 3 seconds after train rear clears

**Notification** (traffic light warning):

```
notification = 95th percentile travel + reaction time + closure
```

Example: 18.2s + 2.5s + 6.8s = 27.5 seconds warning

**Sensor Positions**:

```
detection distance = notification × max train speed × 1.3
sensor 0 = detection distance × 3.0 (max 1500m)
sensor 1 = detection distance × 1.8 (max 1000m)
sensor 2 = detection distance × 0.9 (min 300m)
```

Ensures sensors are properly spaced: S0 > S1 > S2

## Usage

### Full Pipeline

```bash
make th-pipeline
```

Runs complete workflow (takes ~1 hour):

1. Generate network
2. Simulate traffic for 1 hour
3. Calculate thresholds
4. Export to Arduino

### Quick Test

```bash
make th-quick
```

5-minute simulation for testing (less accurate).

### Manual Steps

```bash
python -m thresholds.network              # Create network
python -m thresholds.collector            # Collect data (1 hour)
python -m thresholds.analyzer             # Calculate thresholds
python -m hardware.exporters.threshold    # Export for Arduino
```

### Custom Duration

```bash
python -m thresholds.collector --duration 1800    # 30 minutes
```

## Configuration

Edit `thresholds/config.yaml`:

```yaml
data_collection:
  duration: 3600 # Collection time in seconds

safety:
  margin_close: 2.0 # Extra time before closing gates
  margin_open: 3.0 # Wait time after opening gates
  driver_reaction: 2.5 # Driver reaction time
```

**Common Changes**:

| Goal              | Parameter       | Change     |
| ----------------- | --------------- | ---------- |
| More conservative | margin_close    | 2.0 → 4.0  |
| Faster testing    | duration        | 3600 → 600 |
| Quicker reactions | driver_reaction | 2.5 → 2.0  |

## Outputs

```
outputs/
├── data/
│   ├── clearances.csv     # Vehicle crossing times
│   └── travels.csv        # Traffic light to crossing times
├── plots/
│   └── thresholds_analysis.png    # 6-panel visualization
└── results/
    ├── thresholds.yaml    # Results (human-readable)
    └── thresholds.json    # Results (machine-readable)

hardware/
└── thresholds.h           # Arduino C header
```

### Results File

**thresholds.yaml**:

```yaml
closure_before_eta: 6.8 # Close gates 6.8s before train
opening_after_etd: 3.0 # Open gates 3.0s after train
notification_time: 27.5 # Warn traffic 27.5s before
sensor_positions:
  - 1500.0 # Sensor 0: 1500m from crossing
  - 1000.0 # Sensor 1: 1000m from crossing
  - 800.0 # Sensor 2: 800m from crossing
max_train_speed: 39.0 # Fastest train: 39 m/s
```

### Arduino Export

**thresholds.h**:

```cpp
#define SENSOR_0_POS 1500.00f
#define SENSOR_1_POS 1000.00f
#define SENSOR_2_POS 800.00f
#define CLOSURE_THRESHOLD 6.80f
#define OPENING_THRESHOLD 3.00f
```

### Visualization

**thresholds_analysis.png** shows 6 panels:

1. Clearance time histogram (how long to cross)
2. Travel time histogram (intersection to crossing)
3. Clearance vs speed scatter plot
4. Calculated sensor positions
5. Cumulative distribution (95th percentile line)
6. Summary table with all values

## Expected Results

### Good Quality (1 hour simulation)

Data collected:

- 400-500 clearance measurements
- 150-200 travel measurements

Typical values:

- Clearance: 3-5 seconds (95th: 4-5s)
- Travel: 16-18 seconds (95th: 18-20s)
- Closure threshold: 6-8 seconds
- Notification: 25-30 seconds
- Sensors: 1500m, 1000m, 800m

### Poor Quality (Warning Signs)

- Less than 100 clearances
- Less than 50 travels
- Clearance > 10 seconds (congestion)
- Travel > 25 seconds (lights too far)

**Fix**: Run longer simulation or check network configuration.

## Troubleshooting

### Not Enough Data

**Problem**: Only 50 clearances after 1 hour

**Solutions**:

- Increase simulation duration: `--duration 7200`
- Check traffic flow in network.py
- Verify SUMO is running correctly

### Sensors Out of Order

**Problem**: Warning about sensor_2 > sensor_1

**Cause**: Very high notification time causing calculation error

**Fix**: Analyzer automatically corrects this, but you can:

- Reduce safety margins in config.yaml
- Run longer simulation for better statistics
- Check for data quality issues

### Missing Network Files

**Problem**: "File not found: thresholds.net.xml"

**Fix**:

```bash
make th-network
# or
python -m thresholds.network
```

### SUMO Not Found

**Problem**: "sumo: command not found"

**Install**:

```bash
# Ubuntu/Debian
sudo apt-get install sumo sumo-tools

# macOS
brew install sumo
```

## Integration

### With ML Module

Copy sensor positions to `ml/config.yaml`:

```yaml
sensors:
  s0: 1500 # From sensor_positions[0]
  s1: 1000 # From sensor_positions[1]
  s2: 800 # From sensor_positions[2]
```

### With Simulation Module

Copy thresholds to `simulation/config.yaml`:

```yaml
crossings:
  west:
    close_before_arrival: 6.8
    open_after_departure: 3.0
```

### With Hardware

Arduino automatically includes thresholds.h:

```cpp
#include "thresholds.h"

float closure = CLOSURE_THRESHOLD;  // 6.8
```

## Key Concepts

### 95th Percentile

If you measured 100 cars crossing:

- Sort times from fastest to slowest
- 95th percentile is the 95th value
- This means 95 out of 100 cars finish within this time

**Why not average?**
Average = 4.0 seconds means half of cars need more than 4 seconds. Not safe!

### Safety Margins

Why add 2 seconds to clearance time?

- Sensor measurement delays
- Driver hesitation
- Unexpected events
- System processing time

Real-world systems need buffers beyond statistics.

### Multiple Sensors

Why 3 sensors instead of 1?

- Detect if train is speeding up or slowing down
- More accurate predictions
- Redundancy if one sensor fails
- Validates measurements

## Files

- **network.py**: Creates SUMO road network with crossing
- **collector.py**: Runs simulation and records measurements
- **analyzer.py**: Calculates thresholds using statistics
- **config.yaml**: All settings and safety parameters
- ****init**.py**: Module exports
