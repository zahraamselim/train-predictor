# Railroad Crossing Simulation

A realistic simulation of railroad crossings with smart vehicle behavior.

## What This Does

Simulates a road network with two railroad crossings where:

- Vehicles wait for trains
- Vehicles turn off engines to save fuel
- Vehicles can reroute to avoid long waits
- Each crossing works independently with its own sensors and timing

## The Setup

```
        West Crossing          East Crossing
              |                      |
═══════════════════════════════════════════ North Road
              |                      |
             [X]                    [X]     Gates & Sensors
------------- RAILWAY -------------------
             [X]                    [X]     Gates & Sensors
              |                      |
═══════════════════════════════════════════ South Road
              |                      |

        <------ 300m apart ------>
        (roads 200m apart)
```

## How It Works

### Railroad Crossings

Each crossing has:

1. **Three sensors** that detect trains at different distances
2. **Gates** that close before trains arrive
3. **Warning lights** that alert drivers early
4. **Countdown timer** showing when gates will close/open

### Train Detection

When a train passes the three sensors:

```
Sensor 1 (Far)  →  Sensor 2 (Mid)  →  Sensor 3 (Near)  →  Crossing
```

The system:

1. Records when train passes each sensor
2. Calculates train speed from sensor data
3. Predicts when train will arrive (ETA)
4. Closes gates before arrival
5. Opens gates after train departs

### Smart Features

**Engine Management (Automatic)**

- System tracks how long vehicles wait in queue
- After 5 seconds of waiting, assumes engine is turned off
- Calculates fuel saved: `wait_time × 0.7 × (idling_rate - off_rate)`
- The 0.7 factor accounts for realistic driver behavior (70% compliance)
- Tracks total fuel and CO2 savings

**Smart Rerouting**

- Warning light turns yellow when train is coming
- Vehicles near the crossing can choose:
  - Wait for train to pass
  - Go to the other crossing (if faster)
- System calculates which is faster
- Tracks time saved from rerouting

## Files

```
simulation/
├── config.yaml          Configuration (timing, speeds, etc)
├── network.py           Generate road network
├── controller.py        Run simulation and control crossings
├── metrics.py           Track and save results
└── README.md            This file
```

## Configuration

Edit `config.yaml` to change:

```yaml
network:
  road_separation: 200 # Distance between north/south roads
  crossing_distance: 300 # Distance between west/east crossings
  road_length: 2000 # How long the roads are

traffic:
  cars_per_hour: 300 # Number of cars per hour
  train_interval: 360 # Train every 6 minutes

crossings:
  west: # West crossing settings
    sensors: [1200, 800, 400] # Sensor distances from crossing
    close_before_arrival: 8.0 # Close gates 8s before train
    open_after_departure: 5.0 # Open gates 5s after train leaves
    warning_time: 25.0 # Warn drivers 25s before arrival

  east: # East crossing (different timing!)
    sensors: [1500, 900, 450]
    close_before_arrival: 10.0
    open_after_departure: 3.0
    warning_time: 30.0

fuel:
  driving: 0.08 # Fuel when driving (liters/second)
  idling: 0.01 # Fuel when idling (liters/second)
  engine_off: 0.0 # Fuel when off (liters/second)
  co2_per_liter: 2.31 # CO2 per liter of fuel
  min_wait_to_shutoff: 5.0 # Assume engine off after 5s wait
  engine_off_factor: 0.7 # 70% of wait time engines actually off

rerouting:
  min_time_saved: 8.0 # Only reroute if saves > 8 seconds
  decision_point: 180 # Make decision 180m before crossing
```

## Running the Simulation

### Generate Network

```bash
make sim-network
```

### Run Simulation (Text Only)

```bash
make sim-run
```

### Run with Visual Interface

```bash
make sim-gui
```

### Quick Test (5 minutes)

```bash
make sim-quick
```

## What You'll See

### In the GUI

**Colors:**

- **Realistic vehicles**: Cars look like actual cars (not triangles!)
- **Realistic trains**: Trains look like actual trains
- **Green gates**: Open, safe to cross
- **Red gates**: Closed, train coming/passing
- **Orange sensors**: Waiting for train
- **Red sensors**: Train detected
- **Yellow warning lights**: Train approaching, decide now!
- **Red warning lights**: Gates closed
- **Buildings**: Gray/brown structures with roofs
- **Trees**: Green foliage with brown trunks
- **Green background**: Grass/landscape

**Countdown Timer:**

- Before gate closes: "Closing in X seconds"
- While closed: "Opening in X seconds"

### In the Console

```
[12:00:00] Starting simulation (3600s)
[12:00:15] West: Train detected
[12:00:17] West: ETA = 12.3s
[12:00:25] West: Warning activated
[12:00:27] West: GATE CLOSED
[12:00:32] Vehicle car_45 engine OFF (wait=5.2s, remaining=7.1s)
[12:00:35] Vehicle car_67 rerouted (saves 11.3s)
[12:00:39] West: Train arrived
[12:00:42] West: Train departed
[12:00:47] West: GATE OPENED
```

## Understanding the Results

After simulation, check `outputs/results/simulation_report.txt`:

```
SIMULATION RESULTS

Vehicles tracked: 487

WAIT TIMES
  Total events: 234
  Average: 12.5 seconds
  Median: 11.8 seconds
  Maximum: 28.3 seconds
  95th percentile: 22.1 seconds

ENGINE MANAGEMENT
  Events: 156
  Percentage: 66.7%
  Total time engines off: 1,247 seconds
  Fuel saved: 12.47 liters
  CO2 saved: 28.81 kg

REROUTING
  Events: 34
  Total time saved: 523 seconds
  Average per reroute: 15.4 seconds
```

## Data Files

All in `outputs/metrics/`:

**wait_times.csv**: When vehicles waited

```csv
vehicle,crossing,duration,time
car_0,west,12.5,180.0
car_5,east,8.2,195.0
```

**engine_savings.csv**: Engine shutoff events

```csv
vehicle,duration,fuel_saved,co2_saved,time
car_0,8.0,0.08,0.185,188.0
```

**reroutes.csv**: Rerouting decisions

```csv
vehicle,from,to,time_saved,time
car_25,west,east,15.3,245.0
```

## How the Math Works

### ETA Calculation

When train passes 3 sensors:

```
Distance between sensors: d₁, d₂
Time between sensors: t₁, t₂

Recent speed: v = d₂ / t₂
Distance to crossing: d
ETA = d / v
```

### Rerouting Decision

```
Option 1 (Wait):
  Time = wait_for_train

Option 2 (Reroute):
  Time = drive_to_other_crossing + wait_at_other_crossing

If (Option 1 - Option 2) > 8 seconds:
  Reroute!
```

### Fuel Savings

```
For each vehicle waiting:
  if wait_time > 5 seconds:
    effective_engine_off_time = (wait_time - 5) × 0.7
    fuel_saved = effective_engine_off_time × (idling_rate - off_rate)
    fuel_saved = effective_engine_off_time × 0.01 liters/second

CO₂ saved = fuel_saved × 2.31 kg/liter
```

The 0.7 factor represents that 70% of drivers actually turn off engines, 30% keep idling.

## Experiments to Try

### 1. Different Crossing Timings

Try making crossings very different:

```yaml
west:
  close_before_arrival: 5.0 # Aggressive
east:
  close_before_arrival: 15.0 # Conservative
```

**Question**: Which gets fewer complaints? Which is safer?

### 2. Traffic Density

```yaml
traffic:
  cars_per_hour: 500 # Heavy traffic
```

**Question**: How does this affect wait times? Rerouting?

### 3. Train Frequency

```yaml
traffic:
  train_interval: 180 # Train every 3 minutes
```

**Question**: At what point does rerouting stop working?

### 4. Sensor Placement

```yaml
sensors: [2000, 1000, 500] # Farther away
```

**Question**: Does earlier detection improve wait times?

### 5. Engine Shutoff Factor

```yaml
fuel:
  engine_off_factor: 0.5 # Only 50% compliance
```

**Question**: How does driver compliance affect total savings?

## Real-World Connection

This simulation models real engineering problems:

**Questions Engineers Face:**

- How far should sensors be from crossings?
- When should gates close? (Too early = long waits, too late = danger)
- Should warning systems be integrated?
- What's the optimal timing?

**What You're Learning:**

- System optimization
- Trade-offs (safety vs. convenience)
- Data collection and analysis
- Real-time decision making
- Environmental impact assessment

**Careers Using This:**

- Traffic Engineer
- Transportation Planner
- Safety Engineer
- Software Developer
- Data Analyst
- Environmental Consultant

## Tips for Success

1. **Start with defaults**: Run once to see normal behavior
2. **Change one thing**: Modify one parameter at a time
3. **Compare results**: Run multiple times, compare reports
4. **Think about trade-offs**: Faster isn't always better
5. **Real data**: These numbers come from real systems!

## Common Questions

**Q: Why do crossings have different timing?**
A: In reality, crossings are independent. Train speeds vary, sensor placements differ, and each crossing optimizes for its local conditions.

**Q: Why turn off engines?**
A: Modern cars have auto-start-stop systems that save fuel and emissions. This simulates that technology.

**Q: Why is rerouting optional?**
A: In real life, drivers make their own decisions. Warning lights inform them, but they choose whether to reroute.

**Q: Why do some vehicles not reroute even when it's faster?**
A: Some vehicles are past the decision point when the warning activates. Realistic behavior!

**Q: Can trains slow down?**
A: Trains can't easily slow down or stop. That's why cars must wait, not trains.

## Troubleshooting

**No vehicles appear:**

- Run `make sim-network` first
- Check that SUMO is installed

**Gates never close:**

- Check sensor distances in config
- Ensure trains are spawning (`train_interval`)

**No rerouting happens:**

- Lower `min_time_saved` threshold
- Increase train frequency

**Simulation crashes:**

- Delete `.xml` files and regenerate network
- Check config syntax

## Next Steps

After understanding this simulation:

1. Try the optimization module to find best timings
2. Try the machine learning module to predict train arrivals
3. Combine all three for a complete system

## Summary

This simulation shows:

- How railroad crossings work
- How smart systems can save time and fuel
- How to balance safety, efficiency, and convenience
- Real engineering trade-offs

Perfect for learning about:

- Traffic engineering
- System optimization
- Environmental impact
- Data-driven decision making
