# Railroad Crossing Simulation Project

A realistic simulation of railroad crossings that helps vehicles save fuel and reduce emissions through smart gate control and rerouting.

## What This Project Does

Imagine you're driving and approaching a railroad crossing. A train is coming - should you wait here or take a different route? How long will the gates be closed? Should you turn off your engine while waiting?

This project simulates these real-world decisions and measures their environmental impact.

## The Big Picture

```
        West Crossing          East Crossing
              |                      |
══════════════════════════════════════════ North Road (cars going east-west)
              |                      |
             [X]                    [X]     Gates & Sensors
------------- TRAIN TRACKS ------------------
             [X]                    [X]     Gates & Sensors
              |                      |
══════════════════════════════════════════ South Road (cars going east-west)
              |                      |
        <------ 300m apart ------>
```

The simulation has:

- Two railroad crossings 300 meters apart
- Cars driving on roads that cross the train tracks
- Trains passing through at various speeds
- Smart sensors that detect trains early
- Gates that close before trains arrive
- Vehicles that can choose to wait or reroute

## Four Main Components

### 1. Threshold Calculation

Measures real traffic behavior to calculate safe timing parameters.

**What it calculates:**

- When gates should close before train arrives
- When gates can open after train leaves
- When to warn traffic lights
- Where to place train sensors

**How it works:**

- Runs traffic simulation
- Measures how long vehicles take to cross
- Measures travel time from intersection to crossing
- Calculates 95th percentile values with safety margins
- Outputs recommended thresholds

**Results:**

- Closure threshold: 6-8 seconds before train
- Opening threshold: 3 seconds after train leaves
- Notification time: 25-30 seconds advance warning
- Sensor positions: 300m, 600-1000m, 1000-1500m

**Run it:**

```bash
# Full pipeline
make th-pipeline

# Or step by step
python -m thresholds.network
python -m thresholds.collector
python -m thresholds.analyzer
```

### 2. Main Simulation

Runs a realistic traffic simulation where:

- Cars drive on roads
- Trains pass through crossings
- Gates close when trains approach
- Vehicles wait at closed crossings
- Some vehicles reroute to avoid long waits
- System tracks fuel consumption and emissions

**What you'll see:**

- 500 vehicles tracked over 20 minutes
- 261 wait events (times vehicles stopped at crossings)
- Average wait time: 25.5 seconds
- 92.7% of waiting drivers turn off engines
- 37.82 liters of fuel saved
- 87.36 kg of CO2 reduced

**Run it:**

```bash
# Generate the road network
make sim-network

# Run simulation with visual interface
make sim-gui

# Or run without visuals (faster)
make sim-run
```

### 3. Machine Learning

Trains a computer model to predict:

- How long until a train arrives (ETA)
- How long until a train fully clears the crossing (ETD)

**Why this matters:**

- Better predictions mean shorter gate closure times
- Shorter closure times mean less waiting
- Less waiting means less fuel wasted

**The AI learns from data:**

- Simulates 1000 different trains
- Each train has different speed, length, and acceleration
- Extracts patterns from sensor readings
- Builds a prediction model

**Results:**

- ETA predictions accurate to 0.3-0.4 seconds
- 25-35% better than simple physics formulas
- Fast enough to run on an Arduino

**Run it:**

```bash
# Generate training data (takes 10-15 minutes)
make ml-data

# Train the prediction models
make ml-train
```

### 4. Hardware Integration

Arduino-based crossing controller that runs on real embedded hardware.

**Features:**

- Implements trained ML models in C++
- Uses calculated thresholds for safe operation
- Reads sensor data from train detectors
- Controls gate motors and warning lights
- Runs on Arduino Mega (or Uno with compression)

**Exports:**

- ETA/ETD model coefficients
- Threshold parameters
- Sensor configurations
- Train speed profiles

**Run exporters:**

```bash
# Export all data for Arduino
python -m hardware.exporters.model
python -m hardware.exporters.threshold
python -m hardware.exporters.train
```

## Quick Start Guide

### Installation

You need:

1. Python 3.8 or newer
2. SUMO (traffic simulator)
3. Python packages

**Install on Linux/Mac:**

```bash
# Install SUMO
sudo apt-get install sumo sumo-tools  # Ubuntu/Debian
brew install sumo                      # Mac

# Install Python packages
pip install pandas numpy matplotlib pyyaml scikit-learn
```

**Install on Windows:**

1. Download SUMO from https://www.eclipse.org/sumo/
2. Add SUMO to your PATH
3. Install Python packages: `pip install pandas numpy matplotlib pyyaml scikit-learn`

### Run Your First Simulation

```bash
# 1. Generate the road network
python simulation/network.py

# 2. Run the simulation (no visuals)
python simulation/controller.py

# 3. Check the results
cat outputs/results/simulation_report.txt
```

### See It in Action (With Visuals)

```bash
# Run with GUI
python simulation/controller.py --gui
```

In the GUI you'll see:

- Cars moving on roads (blue)
- Trains passing through (red)
- Gates (green when open, red when closed)
- Sensors (orange boxes along the tracks)
- Buildings and trees (for scenery)
- Countdown timers showing gate status

## Understanding the Results

After running a simulation, check `outputs/results/simulation_report.txt`:

### Wait Times

```
Average wait: 25.5 seconds
Median wait: 27.6 seconds
Maximum wait: 46.5 seconds
```

This tells you how long vehicles typically wait. Most wait about 25-27 seconds.

### Engine Management

```
Events with engine shutoff: 242 (92.7%)
Total engine off time: 63.0 minutes
Fuel saved: 37.82 liters
```

242 out of 261 waiting vehicles (92.7%) turned off their engines after 5 seconds. This saved 37.82 liters of fuel.

### Environmental Impact

```
CO₂ reduced: 87.36 kg
Equivalent to 216 km of driving emissions avoided
Trees needed to offset: 4.2
```

The fuel savings prevented 87.36 kg of CO2 emissions - about the same as driving 216 km.

### Per-Crossing Statistics

```
West Crossing: 142 events, 25.9 seconds average
East Crossing: 119 events, 25.1 seconds average
```

Both crossings have similar wait times, showing the system is balanced.

## Project Structure

```
railroad-crossing/
├── simulation/              Main simulation code
│   ├── controller.py       Runs the simulation, controls crossings
│   ├── network.py          Generates road network
│   ├── metrics.py          Tracks and calculates results
│   ├── config.yaml         Settings (timing, traffic, fuel rates)
│   └── README.md           Simulation documentation
│
├── thresholds/             Calculate safe timing parameters
│   ├── network.py          Simple network for data collection
│   ├── collector.py        Collects vehicle timing data
│   ├── analyzer.py         Calculates thresholds from data
│   ├── config.yaml         Collection settings
│   └── README.md           Threshold calculation guide
│
├── ml/                     Machine learning for predictions
│   ├── data.py            Generates training data
│   ├── model.py           Trains prediction models
│   ├── network.py         Simple network for ML training
│   ├── config.yaml        ML settings
│   └── README.md          ML documentation
│
├── hardware/               Arduino integration
│   ├── sketch.ino         Arduino firmware
│   ├── exporters/         Python scripts to export data
│   │   ├── model.py       Export ML model
│   │   ├── threshold.py   Export thresholds
│   │   └── train.py       Export train profiles
│   ├── diagram.json       Circuit diagram
│   └── README.md          Hardware documentation
│
├── utils/                  Helper code
│   └── logger.py          Logging utility
│
├── outputs/               Results and data
│   ├── data/              Raw CSV data files
│   ├── metrics/           Simulation metrics
│   ├── models/            Trained ML models
│   ├── plots/             Visualizations
│   ├── results/           Human-readable reports
│   └── logs/              Simulation logs
│
├── docker/                Docker containerization
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── Makefile               Easy commands
├── requirements.txt       Python dependencies
└── README.md              This file
```

## Configuration Files Explained

### simulation/config.yaml

Controls the main simulation:

```yaml
network:
  crossing_distance: 300 # Distance between crossings (meters)
  road_separation: 200 # Distance between north/south roads

traffic:
  cars_per_hour: 300 # Traffic density
  train_interval: 180 # Train every 3 minutes

crossings:
  west:
    sensors: [1200, 800, 400] # Sensor distances (meters)
    close_before_arrival: 8.0 # Close gate 8s before train
    open_after_departure: 5.0 # Open gate 5s after train leaves
    warning_time: 25.0 # Warn drivers 25s ahead

fuel:
  driving: 0.08 # Fuel rate when driving (L/s)
  idling: 0.01 # Fuel rate when idling (L/s)
  engine_off: 0.0 # Fuel rate when engine off (L/s)
  min_wait_to_shutoff: 5.0 # Turn off engine after 5s
  engine_off_factor: 0.7 # 70% of drivers actually turn off

rerouting:
  min_time_saved: 8.0 # Only reroute if saves 8+ seconds
  decision_point: 180 # Decide 180m before crossing

simulation:
  duration: 1200 # Run for 20 minutes
  step_size: 0.1 # Update every 0.1 seconds
```

### thresholds/config.yaml

Controls threshold calculation:

```yaml
data_collection:
  duration: 3600 # Collect data for 1 hour

safety:
  margin_close: 2.0 # Safety margin for gate closure
  margin_open: 3.0 # Safety margin for gate opening
  driver_reaction: 2.5 # Driver reaction time (seconds)
```

### ml/config.yaml

Controls machine learning:

```yaml
training:
  n_samples: 1000 # Generate 1000 train examples
  sim_duration: 400 # Run each for 400 seconds
  random_seed: 42 # For reproducibility

model:
  test_size: 0.2 # Use 20% of data for testing
```

## Output Files Guide

### outputs/data/

**clearances.csv** - Vehicle crossing times (from thresholds):

```csv
vehicle_id,clearance_time,speed
car_0,3.2,15.8
```

**travels.csv** - Intersection to crossing times (from thresholds):

```csv
vehicle_id,travel_time
car_5,18.2
```

**raw_trajectories.csv** - Train movement data (from ML):

```csv
time,pos,speed,acceleration,length,run_id,scenario
0.0,0.0,35.2,0.8,150,0,fast
```

**features.csv** - Extracted ML features:

```csv
distance_remaining,train_length,last_speed,eta_actual,etd_actual,...
450.0,150,35.2,12.8,17.3,...
```

### outputs/metrics/

**wait_events.csv** - Every time a vehicle waited:

```csv
vehicle,crossing,wait_duration,engine_off_duration,fuel_saved,co2_saved,time
car_0,west,15.2,7.1,0.071,0.164,145.3
```

**reroute_events.csv** - Every time a vehicle rerouted:

```csv
vehicle,from,to,time_saved,fuel_saved,co2_saved,time
car_5,west,east,12.3,0.984,2.273,234.5
```

**vehicle_fuel.csv** - Fuel consumption per vehicle:

```csv
vehicle_id,first_seen,total_fuel_liters,total_co2_kg,total_wait_time_seconds
car_0,10.5,2.45,5.66,15.2
```

**summary.json** - All statistics in machine-readable format

### outputs/results/

**simulation_report.txt** - Human-readable summary of simulation

**thresholds.yaml** - Calculated timing parameters:

```yaml
closure_before_eta: 6.8
opening_after_etd: 3.0
notification_time: 27.5
sensor_0: 1245.0
sensor_1: 747.0
sensor_2: 373.0
```

**evaluation_results.json** - ML model performance metrics

### outputs/models/

**eta_model.pkl** - Trained ETA prediction model
**etd_model.pkl** - Trained ETD prediction model

### outputs/plots/

- **thresholds_analysis.png** - Threshold calculation visualizations
- **train_trajectories.png** - Sample train movement plots
- **feature_distributions.png** - ML feature histograms
- **feature_correlations.png** - Feature-target relationships
- **eta_training.png** - ETA model performance
- **etd_training.png** - ETD model performance

## Workflow: From Data to Hardware

The typical workflow through all components:

### Step 1: Calculate Thresholds

```bash
make th-pipeline
```

Outputs: `thresholds.yaml` with safe timing parameters

### Step 2: Generate ML Training Data

```bash
make ml-data
```

Outputs: `features.csv` with 1000 train examples

### Step 3: Train Prediction Models

```bash
make ml-train
```

Outputs: `eta_model.pkl` and `etd_model.pkl`

### Step 4: Run Full Simulation

```bash
make sim-network
make sim-run
```

Outputs: `simulation_report.txt` with performance metrics

### Step 5: Export to Hardware

```bash
python -m hardware.exporters.threshold
python -m hardware.exporters.model
python -m hardware.exporters.train
```

Outputs: Arduino-compatible header files

### Step 6: Deploy to Arduino

```bash
# Flash the firmware
arduino-cli compile --fqbn arduino:avr:mega hardware/sketch.ino
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:mega hardware/sketch.ino
```

## Real-World Applications

This simulation models real engineering problems:

### Traffic Engineering

- Optimal gate timing
- Sensor placement
- Warning system design

### Environmental Planning

- Emission reduction strategies
- Fuel consumption analysis
- Engine shutoff policies

### Smart Transportation

- Real-time rerouting
- Predictive gate control
- Multi-crossing coordination

### Safety Systems

- Early warning detection
- Fail-safe timing margins
- Worst-case scenario planning

### Embedded Systems

- Resource-constrained ML deployment
- Real-time prediction algorithms
- Sensor fusion and data processing

## Experiments to Try

### 1. Different Gate Timing

**Change in simulation/config.yaml:**

```yaml
close_before_arrival: 3.0   # Aggressive (risky)
close_before_arrival: 15.0  # Conservative (long waits)
```

**Measure:** Average wait time, safety margin

### 2. Engine Shutoff Policy

**Change in simulation/config.yaml:**

```yaml
engine_off_factor: 0.5   # Only 50% comply
engine_off_factor: 0.9   # 90% comply
min_wait_to_shutoff: 3.0 # Turn off sooner
```

**Measure:** Fuel savings, CO2 reduction

### 3. Heavy Traffic

**Change in simulation/config.yaml:**

```yaml
cars_per_hour: 600 # Double traffic
train_interval: 120 # Trains every 2 minutes
```

**Measure:** Wait times, congestion patterns

### 4. Sensor Placement

**Change sensor positions in simulation/config.yaml:**

```yaml
sensors: [2000, 1200, 600]  # Farther sensors
sensors: [800, 500, 250]    # Closer sensors
```

**Measure:** Prediction accuracy, gate timing

### 5. ML Model Complexity

**Change in ml/config.yaml:**

```yaml
n_samples: 2000  # More training data
n_samples: 100   # Less training data
```

**Measure:** Model accuracy, training time

## Docker Deployment

Run the entire system in a containerized environment:

```bash
# Build the container
docker-compose build

# Run threshold calculation
docker-compose run railroad make th-pipeline

# Run ML training
docker-compose run railroad make ml-data
docker-compose run railroad make ml-train

# Run simulation
docker-compose run railroad make sim-run
```

All outputs are saved to the `outputs/` directory which is mounted as a volume.

## Learning Resources

### Traffic Simulation

- SUMO Documentation: https://sumo.dlr.de/docs/
- Traffic Engineering Basics
- Transportation Planning

### Machine Learning

- scikit-learn tutorials
- Supervised Learning (Regression)
- Gradient Boosting explained

### Embedded Systems

- Arduino Programming Guide
- Resource-Constrained ML
- Sensor Integration

### Environmental Impact

- Vehicle Emissions Calculations
- Fuel Consumption Models
- Carbon Footprint Analysis

## Credits and Background

This project simulates real railroad crossing systems used worldwide. The concepts are based on:

- Actual train detection systems
- Real gate timing standards
- Environmental impact studies
- Traffic engineering research

The simulation uses SUMO (Simulation of Urban MObility), a professional traffic simulation tool used by researchers and transportation planners.

## Summary

This project shows how smart systems can:

- Reduce vehicle waiting times
- Save fuel through engine management
- Lower emissions
- Make better real-time decisions
- Balance safety with efficiency
- Deploy to embedded hardware

The complete system provides:

- Safe timing parameters from real traffic data
- Accurate train arrival predictions using ML
- Realistic simulation with environmental metrics
- Hardware-ready firmware for Arduino deployment

Perfect for learning about:

- Traffic engineering
- Environmental science
- Machine learning
- Embedded systems
- System optimization
- Real-world problem solving
