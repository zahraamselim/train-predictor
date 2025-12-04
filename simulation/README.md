# Railroad Crossing Simulation

Simulates cars waiting at railroad crossings when trains pass through. Measures fuel savings from turning off engines and smart rerouting decisions.

## What It Does

```
        West Crossing          East Crossing
              |                      |
══════════════════════════════════════════ North Road
              |                      |
             [X]                    [X]     Gates & Sensors
------------- TRAIN TRACKS ------------------
             [X]                    [X]     Gates & Sensors
              |                      |
══════════════════════════════════════════ South Road
              |                      |
```

- Cars drive on roads
- Trains pass through crossings
- Sensors detect trains early
- Gates close before trains arrive
- Vehicles wait (and save fuel by turning off engines)
- Some vehicles reroute to avoid long waits

## How It Works

### Train Detection

Three sensors detect approaching trains:

```
Sensor 1 (Far)  →  Sensor 2 (Mid)  →  Sensor 3 (Near)  →  Crossing
```

When a train passes all three sensors:

1. System calculates train speed
2. Predicts when train will arrive (ETA)
3. Closes gates 8 seconds before arrival
4. Opens gates 5 seconds after train leaves

### Engine Management

When vehicles wait at crossings:

- First 5 seconds: engine idles (0.01 L/s)
- After 5 seconds: engine turns off (0 L/s)
- Reality factor: only 70% of drivers actually turn off

**Fuel saved per vehicle:**

```
if wait_time > 5 seconds:
    engine_off_time = (wait_time - 5) × 0.7
    fuel_saved = engine_off_time × 0.01 L/s
```

### Smart Rerouting

When a train approaches:

1. Warning light turns yellow
2. Nearby vehicles calculate fastest route
3. If rerouting saves 8+ seconds, they switch crossings
4. System tracks time and fuel saved

## Running the Simulation

### Setup

```bash
# Generate road network
python simulation/network.py
```

### Run Without Visuals (Faster)

```bash
python simulation/controller.py
```

### Run With Visual Interface

```bash
python simulation/controller.py --gui
```

### Quick Test (10 minutes)

Edit `config.yaml`:

```yaml
simulation:
  duration: 600 # 10 minutes instead of 20
```

## Understanding Results

After running, check `outputs/results/simulation_report.txt`:

### Example Results

```
SIMULATION OVERVIEW
  Vehicles tracked: 500
  Wait events: 261
  Reroute events: 0

WAIT TIMES
  Average: 25.5 seconds
  Median: 27.6 seconds
  Maximum: 46.5 seconds

ENGINE MANAGEMENT
  Events with engine shutoff: 242 (92.7%)
  Total engine off time: 63.0 minutes
  Fuel saved: 37.82 liters
  CO₂ reduced: 87.36 kg

ENVIRONMENTAL IMPACT
  Equivalent to 0.8 car refuelings saved
  Equivalent to 216 km of emissions avoided
  Trees needed to offset: 4.2
```

### What This Means

**92.7% of vehicles turned off engines** - 242 out of 261 waiting vehicles waited longer than 5 seconds

**37.82 liters saved** - From vehicles turning off engines while waiting

**87.36 kg CO₂ reduced** - Environmental benefit (1 liter fuel = 2.31 kg CO₂)

**No rerouting** - Both crossings had similar wait times, so vehicles stayed put

## Configuration

Edit `simulation/config.yaml` to change behavior:

### Traffic Settings

```yaml
traffic:
  cars_per_hour: 300 # More cars = more wait events
  train_interval: 180 # Train every 3 minutes
```

Try:

- Heavy traffic: `cars_per_hour: 600`
- Frequent trains: `train_interval: 120` (every 2 minutes)

### Gate Timing

```yaml
crossings:
  west:
    close_before_arrival: 8.0 # Close gate 8s before train
    open_after_departure: 5.0 # Open gate 5s after train
    warning_time: 25.0 # Warn drivers 25s ahead
```

Try:

- Aggressive: `close_before_arrival: 5.0` (shorter waits, less safe)
- Conservative: `close_before_arrival: 12.0` (longer waits, safer)

### Engine Shutoff

```yaml
fuel:
  min_wait_to_shutoff: 5.0 # Turn off after 5s
  engine_off_factor: 0.7 # 70% of drivers comply
```

Try:

- Earlier shutoff: `min_wait_to_shutoff: 3.0`
- Higher compliance: `engine_off_factor: 0.9` (90%)

### Rerouting

```yaml
rerouting:
  min_time_saved: 8.0 # Only reroute if saves 8+ seconds
  decision_point: 180 # Decide 180m before crossing
```

Try:

- More rerouting: `min_time_saved: 5.0`
- Earlier decision: `decision_point: 250`

## Output Files

### outputs/metrics/

**wait_events.csv** - Every vehicle wait:

```csv
vehicle,crossing,wait_duration,engine_off_duration,fuel_saved,co2_saved,time
car_0,west,15.2,7.1,0.071,0.164,145.3
```

**reroute_events.csv** - Every reroute decision:

```csv
vehicle,from,to,time_saved,fuel_saved,co2_saved,time
car_5,west,east,12.3,0.984,2.273,234.5
```

**vehicle_fuel.csv** - Per-vehicle consumption:

```csv
vehicle_id,total_fuel_liters,total_co2_kg,total_wait_time_seconds
car_0,2.45,5.66,15.2
```

### outputs/results/

**simulation_report.txt** - Human-readable summary

### outputs/logs/

**simulation_YYYYMMDD_HHMMSS.log** - Detailed event log

## Visual Elements

When running with `--gui`, you'll see:

**Colors:**

- Blue vehicles: cars
- Red vehicles: trains
- Green gates: open, safe to cross
- Red gates: closed, train coming
- Orange sensors: waiting for trains
- Red sensors: train detected
- Yellow warning lights: train approaching, decide now
- Red warning lights: gates closed
- Buildings with windows and roofs
- Trees with brown trunks and green leaves

**Countdown Timer:**

- Shows seconds until gate closes/opens
- Green numbers: gate will close soon
- Red numbers: gate closed, train passing

## Common Scenarios

### Scenario 1: Normal Operation

```
[12:00:15] West: Train detected
[12:00:17] West: ETA = 12.3s
[12:00:25] West: Warning activated (train 12s away)
[12:00:27] West: GATE CLOSED (train 10s away)
[12:00:35] Vehicle car_45 waited 8.2s, engine off 2.3s
[12:00:37] West: Train arrived
[12:00:40] West: Train departed
[12:00:45] West: GATE OPENED
```

### Scenario 2: Rerouting

```
[12:01:10] East: Warning activated
[12:01:12] Vehicle car_89 rerouted from east to west (saves 15.3s)
```

### Scenario 3: Both Crossings Busy

```
[12:02:00] West: GATE CLOSED (train approaching)
[12:02:05] East: GATE CLOSED (different train)
[12:02:10] Traffic backing up at both crossings
```

## Experiments to Try

### 1. Rush Hour

**Change:**

```yaml
cars_per_hour: 600
train_interval: 120
```

**Question:** How much more fuel is saved with heavy traffic?

### 2. Different Crossing Timings

**Change:**

```yaml
west:
  close_before_arrival: 5.0
east:
  close_before_arrival: 12.0
```

**Question:** Do vehicles start preferring one crossing?

### 3. Early Engine Shutoff

**Change:**

```yaml
min_wait_to_shutoff: 2.0
```

**Question:** How much extra fuel is saved?

### 4. High Compliance

**Change:**

```yaml
engine_off_factor: 0.95
```

**Question:** What if almost everyone turns off their engine?

### 5. Aggressive Rerouting

**Change:**

```yaml
min_time_saved: 3.0
decision_point: 300
```

**Question:** How often do vehicles reroute now?

## Interpreting Statistics

### Wait Time Statistics

**Average vs Median:**

- Average: 25.5s (sum of all waits / number of waits)
- Median: 27.6s (middle value when sorted)
- If median > average: Most waits are longer, with a few very short waits
- If average > median: Most waits are shorter, with a few very long waits

**Standard Deviation: 12.4s**

- Shows how spread out the wait times are
- 68% of waits are within 25.5 ± 12.4 seconds
- 95% of waits are within 25.5 ± 24.8 seconds

**95th Percentile: 43.3s**

- 95% of vehicles wait less than 43.3 seconds
- Only 5% experience longer waits
- Useful for worst-case planning

### Engine Shutoff Percentage

**92.7% of waits had engine shutoff**

- This means 92.7% of vehicles waited longer than 5 seconds
- Of those vehicles, 70% actually turned off their engines
- Effective shutoff rate: 92.7% × 70% = 64.9% of all vehicles

### Per-Crossing Comparison

**West: 142 events, 25.9s average**
**East: 119 events, 25.1s average**

- West crossing had more events (more traffic crosses there)
- Wait times similar (system is balanced)
- If one crossing had much longer waits, vehicles would reroute

## File Structure

```
simulation/
├── controller.py       Main simulation logic
├── network.py         Generates road network
├── metrics.py         Tracks and calculates results
├── config.yaml        All settings
└── README.md          This file
```

## What You're Learning

**Traffic Engineering:**

- How railroad crossings work
- Optimal gate timing
- Sensor placement

**Environmental Science:**

- Fuel consumption calculations
- Emission reduction strategies
- Real-world impact measurement

**System Design:**

- Safety vs efficiency tradeoffs
- Real-time decision making
- Performance optimization

**Data Analysis:**

- Statistical measures (mean, median, percentiles)
- Data collection and reporting
- Comparing different configurations

## Summary

The simulation shows:

- Typical vehicle waits: 25-28 seconds
- Most vehicles (92.7%) wait long enough to turn off engines
- Engine shutoff saves 37.82 liters of fuel per simulation
- This prevents 87.36 kg of CO₂ emissions
- Smart systems can reduce environmental impact without reducing safety
