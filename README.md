# Railroad Crossing Control System

A complete intelligent railroad crossing safety system that combines traffic simulation, machine learning prediction, and hardware implementation.

## Overview

This project demonstrates how real-time train detection and ML-based prediction can improve railroad crossing safety and traffic flow. The system uses three sensors to detect approaching trains, predicts arrival/departure times with sub-second accuracy, and controls crossing gates and traffic signals optimally.

## System Components

### 1. Thresholds Module

Calculates safe timing parameters by simulating real traffic:

- Gate closure time: When to close gates before train arrives
- Gate opening time: When to open gates after train departs
- Traffic notification time: When to alert upstream intersections
- Sensor positions: Where to place train detection sensors

Uses 95th percentile statistics and safety margins to ensure conservative, location-appropriate values.

### 2. Machine Learning Module

Trains Gradient Boosting models to predict train timing:

- ETA Model: Predicts when train front reaches crossing (0.3-0.4s accuracy)
- ETD Model: Predicts when train rear clears crossing (0.4-0.5s accuracy)
- 25-35% improvement over simple physics calculations
- Achieves sub-second precision using 8-10 features from 3 sensors

### 3. Simulation Module

Validates system performance with two-phase traffic simulation:

- Phase 1: Baseline traffic with train blockages
- Phase 2: Alternative route without trains
- Optimized: Calculated scenario with 70% smart rerouting

Measures trip time, wait time, fuel consumption, CO2 emissions, and comfort scores with 95% confidence intervals.

### 4. Hardware Implementation

Arduino-based physical demonstration:

- 3 PIR motion sensors for train detection
- Servo motor for gate control
- LED indicators for crossing and intersection status
- TM1637 display for countdown timer
- Buzzer for audible warnings

## Key Results

**Thresholds** (typical values):

- Close gates: 6-8 seconds before train
- Open gates: 3 seconds after train
- Notify traffic: 25-30 seconds before train
- Sensor positions: 1500m, 1000m, 800m

**ML Performance**:

- ETA accuracy: 0.35 ± 0.02 seconds (95% CI)
- ETD accuracy: 0.45 ± 0.03 seconds (95% CI)
- Cross-validation: Stable across 5 folds
- R² scores: 0.92-0.96 (ETA), 0.88-0.93 (ETD)

**Traffic Simulation** (with 70% adoption):

- Trip time: 11.6% ± 1.3% improvement
- Wait time: 64.7% ± 4.2% reduction
- Fuel consumption: 9.0% ± 0.9% savings
- CO2 emissions: 9.0% ± 0.9% reduction
- Comfort score: 3.3% ± 0.4% improvement

All improvements are statistically significant at 95% confidence level.

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install pandas numpy scikit-learn matplotlib scipy pyyaml

# Install SUMO traffic simulator
# Ubuntu: sudo apt-get install sumo sumo-tools
# macOS: brew install sumo
# Windows: https://www.eclipse.org/sumo/

# Verify installation
sumo --version
python3 --version
```

### Run Complete Pipeline

```bash
# Build Docker environment (optional)
make build

# Generate thresholds from traffic data
make th-pipeline

# Train ML models
make ml-pipeline

# Run traffic simulation
make sim-pipeline
```

### Quick Testing

```bash
# Fast thresholds (5 min simulation)
make th-quick

# Fast ML (50 samples)
make ml-quick

# View simulation with GUI
make sim-gui
```

## Project Structure

```
level-crossing-project/
├── thresholds/          # Safety parameter calculation
│   ├── network.py       # SUMO network generator
│   ├── collector.py     # Traffic data collection
│   ├── analyzer.py      # Threshold calculation
│   └── config.yaml      # Safety margins, duration
├── ml/                  # Machine learning models
│   ├── data.py          # Training data generation
│   ├── model.py         # Model training/evaluation
│   ├── network.py       # SUMO network for ML
│   └── config.yaml      # Sensors, hyperparameters
├── simulation/          # Traffic simulation
│   ├── network.py       # Road network with crossings
│   ├── controller.py    # Simulation controller
│   ├── data.py          # Vehicle tracking
│   ├── metrics.py       # Performance metrics
│   └── config.yaml      # Traffic, fuel, routing
├── hardware/            # Arduino implementation
│   ├── sketch.ino       # Main Arduino code
│   ├── exporters/       # Model/threshold exporters
│   └── diagram.json     # Wokwi circuit diagram
├── outputs/             # Generated results
│   ├── data/            # Raw CSV data
│   ├── models/          # Trained ML models
│   ├── plots/           # Visualizations
│   └── results/         # JSON metrics
└── Makefile            # Build automation
```

## Module Details

### Thresholds Module

**Purpose**: Calculate safe, location-specific control parameters

**Process**:

1. Simulate 1 hour of realistic traffic (600 vehicles)
2. Measure vehicle clearance times (95th percentile: 4-5s)
3. Measure intersection-to-crossing travel times (95th percentile: 18s)
4. Add safety margins (2s for closure, 3s for opening)
5. Calculate sensor positions based on max train speed
6. Validate sensor ordering (S0 >= S1 >= S2)

**Output**: YAML/JSON files with thresholds, Arduino C header

### ML Module

**Purpose**: Train models to predict train arrival/departure

**Process**:

1. Generate 1000 synthetic train trajectories
2. Extract 8-10 features from 3 sensor readings
3. Train Gradient Boosting models (200 trees, depth 4)
4. Validate with 5-fold cross-validation
5. Export compressed models for Arduino

**Output**: Pickle models, comprehensive evaluation plots, JSON metrics

### Simulation Module

**Purpose**: Measure system-wide traffic benefits

**Process**:

1. Phase 1: All traffic uses west crossing (with trains)
2. Phase 2: All traffic uses east crossing (no trains)
3. Calculate optimized scenario (70% reroute when train detected)
4. Compare metrics with 95% confidence intervals

**Output**: Per-vehicle CSV data, scenario comparison JSON

### Hardware Module

**Purpose**: Physical demonstration of crossing control

**Features**:

- Real-time train detection with 3 PIR sensors
- ML-based ETA/ETD prediction (compressed models)
- Automated gate control with servo motor
- Visual/audio warnings (LEDs, buzzer)
- Countdown display (TM1637 7-segment)

**Platform**: Arduino Uno, Wokwi simulator compatible

## Scientific Rigor

**Statistical Methods**:

- 95% confidence intervals on all metrics
- 5-fold cross-validation for ML models
- Error propagation for calculated scenarios
- t-distribution for small samples
- Non-overlapping CIs prove significance

**Reproducibility**:

- All random seeds fixed (seed=42)
- Complete hyperparameter documentation
- Automated pipeline via Makefile
- Version-controlled configurations

**Validation**:

- ML models tested on held-out data (20%)
- Simulation runs for 30 minutes (1800s)
- Thresholds based on 400+ vehicle samples
- Multiple evaluation metrics per experiment

## Performance Benchmarks

**Computation Time**:

- Thresholds: 10-15 minutes (1 hour simulation)
- ML training: 8-12 minutes (1000 samples)
- Simulation: 5-8 minutes per phase

**Memory Usage**:

- Peak: ~2GB RAM during training
- Models: <100KB compressed for Arduino
- Data: ~50MB for complete pipeline

**Accuracy**:

- Thresholds: Conservative (95th percentile + margins)
- ML: Sub-second precision on test data
- Simulation: Error margins <5% on all metrics

## Real-World Applications

**Direct Implementation**:

- Smart traffic signal coordination
- Dynamic route guidance apps
- Railroad crossing safety systems
- Emergency vehicle preemption

**Research Extensions**:

- Multi-crossing networks
- Probabilistic arrival predictions
- Adaptive safety margins
- Integration with V2X communication

## Limitations

**Current System**:

- Simulated data (not real-world validated)
- Simplified traffic patterns
- Single train type in simulation
- No adverse weather conditions
- Assumes perfect sensor reliability

**Hardware Constraints**:

- Arduino Uno: 32KB flash, 2KB RAM
- Compressed models only (50 trees max)
- Integer-only calculations
- No floating-point on hardware

## Future Work

- Real-world data collection and validation
- Multi-train scenarios
- Weather-dependent adjustments
- Pedestrian and cyclist detection
- Integration with existing railroad systems
- Mobile app for driver notifications
- Cost-benefit analysis

## License

MIT License - see LICENSE file for details

## Authors

Zahraa Selim - Complete system design and implementation

## Acknowledgments

- SUMO Traffic Simulator (Eclipse Foundation)
- scikit-learn Machine Learning Library
- Arduino Platform and Community
- Wokwi Online Circuit Simulator
