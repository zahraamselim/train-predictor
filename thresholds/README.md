# Threshold Calculation Module

## What This Does

Calculates safe timing thresholds for railroad crossing control by measuring real traffic behavior.

Questions answered:

- When should gates close before a train arrives?
- When can gates open after a train leaves?
- When should traffic lights be warned?
- Where should train sensors be placed?

## How It Works

1. Generate a simple road network with a railroad crossing
2. Run traffic simulation and measure vehicle timing
3. Calculate safe thresholds with safety margins

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
Car enters crossing area (within 150m) -> Car exits -> Calculate time
```

Purpose: Determines how long gates must stay closed to let cars clear.

### Vehicle Travel Time

How long does a car take from traffic light to crossing?

```
Car passes intersection (-300m or +300m) -> Car reaches crossing -> Calculate time
```

Purpose: Determines how much advance warning traffic lights need.

## Output Files

### Data (outputs/data/)

**clearances.csv**

```
vehicle_id,clearance_time,speed
car_0,3.2,15.8
car_1,4.1,14.2
```

**travels.csv**

```
vehicle_id,travel_time
car_5,18.2
car_8,19.5
```

### Results (outputs/results/thresholds.yaml)

```yaml
closure_before_eta: 6.8
opening_after_etd: 3.0
notification_time: 27.5
sensor_0: 1245.0
sensor_1: 747.0
sensor_2: 373.0
max_train_speed: 39.0
```

### Plots (outputs/plots/)

**thresholds_analysis.png** - Main analysis with 6 panels:

- Vehicle clearance time histogram
- Travel time histogram
- Clearance time vs vehicle speed
- Sensor positions bar chart
- Clearance time cumulative distribution
- Summary statistics

## Understanding the Calculations

### Gate Closure Threshold

Formula:

```
95th percentile clearance time + safety margin
```

Example:

- 95% of cars clear in 4.8 seconds
- Safety margin: 2.0 seconds
- Result: Close gates 6.8s before train

Why: Ensures 95% of cars can safely clear. Safety margin handles slower drivers.

### Gate Opening Threshold

Formula:

```
safety margin (3.0 seconds)
```

Example:

- Train leaves
- Wait 3.0 seconds
- Open gates

Why: Simple and conservative. Accounts for sensor delays.

### Notification Threshold

Formula:

```
95th percentile travel time + driver reaction + closure time
```

Example:

- Travel from intersection: 18.2s
- Driver sees signal, reacts: 2.5s
- Gates close: 6.8s
- Total: 27.5s warning needed

Why: Traffic lights need time to stop cars before they reach the crossing approach.

### Sensor Positions

Formula:

```
detection_distance = notification_time × max_speed × 1.3
sensor_0 = detection_distance × 3.0 (capped at 1500m)
sensor_1 = detection_distance × 1.8 (capped at 1000m)
sensor_2 = detection_distance × 0.9 (min 300m)
```

Example:

- Notification: 27.5s
- Max speed: 39 m/s
- Detection distance: 27.5 × 39 × 1.3 = 1394m
- Sensor 0: 1394 × 3.0 = 4182m (capped at 1500m)
- Sensor 1: 1394 × 1.8 = 2509m (capped at 1000m)
- Sensor 2: 1394 × 0.9 = 1255m (min 300m)

Why: Three sensors improve ETA/ETD prediction accuracy. Spaced logarithmically.

Note: Max train speed (39 m/s) is taken from the network configuration (train_fast maxSpeed).

## Configuration

Edit `thresholds/config.yaml`:

```yaml
data_collection:
  duration: 3600

safety:
  margin_close: 2.0
  margin_open: 3.0
  driver_reaction: 2.5
```

## Expected Results

### Good Data Quality

- Clearances: 100+ samples
- Travels: 50+ samples

### Typical Values

- Closure threshold: 6-8 seconds
- Opening threshold: 3 seconds
- Notification: 25-30 seconds
- Sensor 0: 1000-1500m
- Sensor 1: 600-1000m
- Sensor 2: 300-500m

## Experiments

### Experiment 1: Effect of Safety Margins

Question: How do safety margins affect gate closure time?

Method:

1. Run baseline: `margin_close: 2.0`
2. Run conservative: `margin_close: 4.0`
3. Run aggressive: `margin_close: 1.0`
4. Compare closure thresholds

Expected: Higher margins = earlier closure = safer but more traffic delay

### Experiment 2: Traffic Volume Impact

Question: Does heavy traffic change clearance times?

Method:

1. Baseline: 400 vehicles/hour
2. Light traffic: Edit routes, 200 vehicles/hour
3. Heavy traffic: 800 vehicles/hour
4. Compare 95th percentile clearance times

Expected: Heavy traffic = longer clearance (cars queued at crossing)

### Experiment 3: Short vs Long Simulation

Question: How much data is needed for accurate results?

Method:

1. Run 5 minutes (300s)
2. Run 30 minutes (1800s)
3. Run 1 hour (3600s)
4. Compare sample counts and threshold stability

Expected: Longer runs = more samples = more accurate 95th percentiles

## Troubleshooting

**No data collected**

- Check SUMO installation: `sumo --version`
- Verify network files exist: `ls thresholds.net.xml`

**Low sample counts**

- Increase simulation duration to 3600s
- Check traffic is flowing (not gridlocked)

**Very high clearance times**

- Normal if traffic is congested
- Thresholds will adjust automatically

**Sensors exceed 1500m**

- Automatically capped at practical limits
- Consider slower train speeds in config

## File Structure

```
thresholds/
├── __init__.py
├── config.yaml
├── network.py
├── collector.py
└── analyzer.py

outputs/
├── data/
│   ├── clearances.csv
│   └── travels.csv
├── results/
│   └── thresholds.yaml
└── plots/
    └── thresholds_analysis.png
```

## Integration

These thresholds are used by:

- Arduino firmware for gate control
- Traffic light coordination logic
- ETA/ETD prediction models

The analyzer uses the maximum configured train speed (39 m/s from train_fast) for sensor placement calculations.
