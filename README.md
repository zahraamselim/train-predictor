# Smart Railway Crossing Control System

An intelligent railway crossing management system using machine learning to predict train arrival times and optimize traffic flow.

## Overview

This project combines traffic simulation, machine learning, and embedded systems to create a complete railway crossing control solution that:

- Predicts train arrival/departure times with sub-second accuracy
- Reduces traffic delays by 65%
- Saves 9% fuel consumption and CO2 emissions
- Runs on Arduino for physical deployment

## System Architecture

```
SUMO Simulation → Data Collection → ML Training → Threshold Calculation
                                          ↓
                                   Physical Hardware
                                    (Arduino Demo)
```

### Modules

1. **Thresholds** - Calculate safe gate timing from traffic measurements
2. **ML** - Train models to predict train ETA/ETD
3. **Simulation** - Test system performance with realistic traffic
4. **Hardware** - Deploy to Arduino for physical demonstration

## Quick Start

### Prerequisites

**Software**:

- Docker & Docker Compose
- Python 3.8+
- SUMO traffic simulator

**Hardware** (optional):

- Arduino Uno
- 3x PIR sensors
- Servo motor, LEDs, buzzer, 7-segment display

### Installation

```bash
# Clone repository
git clone <repository-url>
cd somaya

# Build Docker environment
make build

# Run complete pipeline
make all
```

This will:

1. Generate traffic thresholds (1 hour)
2. Train ML models (10 minutes)
3. Run simulation comparison (30 minutes)
4. Export to Arduino headers

### Quick Test

```bash
make test
```

Runs reduced versions of all modules (~5 minutes).

## Usage

### Complete Pipeline

```bash
make all
```

Runs entire system: thresholds → ML → simulation

### Individual Modules

**Thresholds** (calculate safe gate timing):

```bash
make th-pipeline    # Full: 1 hour simulation
make th-quick       # Quick: 5 minutes
```

**ML** (train prediction models):

```bash
make ml-pipeline    # Full: 1000 samples
make ml-quick       # Quick: 50 samples
```

**Simulation** (test system performance):

```bash
make sim-pipeline   # Headless simulation
make sim-gui        # With visualization
```

**Hardware** (export to Arduino):

```bash
make hw-export      # Generate Arduino headers
```

## Results

### Machine Learning Performance

**ETA Model** (8 features):

- Accuracy: 0.30-0.40s mean error
- R² Score: 0.92-0.96
- Improvement: 25-35% over physics

**ETD Model** (10 features):

- Accuracy: 0.40-0.50s mean error
- R² Score: 0.88-0.93
- Improvement: 20-30% over physics

### Traffic Simulation Results

Comparing baseline (no smart routing) vs optimized (70% adoption):

| Metric    | Baseline | Optimized | Improvement |
| --------- | -------- | --------- | ----------- |
| Trip time | 5.9 min  | 5.2 min   | 12% faster  |
| Wait time | 15 sec   | 5 sec     | 65% less    |
| Fuel      | 27.1 L   | 24.7 L    | 9% saved    |
| CO2       | 62.6 kg  | 57.0 kg   | 9% saved    |

**System-wide savings** (485 vehicles):

- 1,188 liters fuel saved
- 2,745 kg CO2 reduced
- 334 vehicle-minutes saved

## Project Structure

```
.
├── docker/              # Docker configuration
├── hardware/            # Arduino code and exporters
│   ├── exporters/       # Python → C converters
│   ├── sketch.ino       # Main Arduino program
│   └── diagram.json     # Circuit layout
├── ml/                  # Machine learning module
│   ├── data.py          # Training data generation
│   ├── model.py         # Model training
│   └── network.py       # SUMO network generator
├── simulation/          # Traffic simulation module
│   ├── controller.py    # Simulation controller
│   ├── metrics.py       # Performance metrics
│   └── network.py       # Network generator
├── thresholds/          # Safety threshold calculation
│   ├── collector.py     # Data collection
│   ├── analyzer.py      # Threshold calculation
│   └── network.py       # Network generator
├── utils/               # Shared utilities
│   └── logger.py        # Clean logging
├── outputs/             # Generated data and results
│   ├── data/            # CSV data files
│   ├── models/          # Trained ML models
│   ├── plots/           # Visualizations
│   └── results/         # JSON metrics
├── Makefile             # Build automation
└── README.md            # This file
```

## Module Details

### 1. Thresholds Module

**Purpose**: Calculate safe gate timing from real traffic measurements

**Process**:

1. Simulate realistic traffic (1 hour)
2. Measure vehicle clearance times
3. Calculate 95th percentile + safety margins
4. Determine sensor positions

**Output**: `outputs/results/thresholds.yaml`

**Documentation**: `thresholds/README.md`

### 2. ML Module

**Purpose**: Train models to predict train arrival/departure times

**Process**:

1. Generate 1000 train trajectories in SUMO
2. Extract features from 3 sensor readings
3. Train Gradient Boosting models (200 trees)
4. Evaluate with 95% confidence intervals

**Output**:

- `outputs/models/eta_model.pkl`
- `outputs/models/etd_model.pkl`

**Documentation**: `ml/README.md`

### 3. Simulation Module

**Purpose**: Validate system benefits with realistic traffic

**Process**:

1. Phase 1: All traffic uses west crossing (with trains)
2. Phase 2: All traffic uses east crossing (no trains)
3. Calculate optimized scenario (70% smart routing)
4. Compare metrics

**Output**: `outputs/results/comparison.json`

**Documentation**: `simulation/README.md`

### 4. Hardware Module

**Purpose**: Deploy to Arduino for physical demonstration

**Physical Setup**:

- Tabletop model (~60cm)
- 3 sensors (10cm spacing)
- Servo gate, LEDs, buzzer, display
- Hand-moved toy train

**Process**:

1. Export thresholds → `hardware/thresholds.h`
2. Export ML models → `hardware/eta_model.h`
3. Generate config → `hardware/crossing_config.h`
4. Upload `sketch.ino` to Arduino

**Documentation**: `hardware/README.md`

## Key Features

### Statistical Rigor

- 95% confidence intervals on all metrics
- 5-fold cross-validation
- Error propagation in calculations
- Non-overlapping intervals prove significance

### Real-World Applicability

- Handles varied train speeds (25-39 m/s)
- Accounts for acceleration/deceleration
- Conservative safety margins
- Location-specific optimization

### Complete Pipeline

- Simulation → Training → Testing → Deployment
- Reproducible with random seeds
- Documented assumptions and limitations
- Validation at each stage

## Configuration

### Thresholds Configuration

Edit `thresholds/config.yaml`:

```yaml
data_collection:
  duration: 3600 # Simulation time (seconds)

safety:
  margin_close: 2.0 # Extra time before closing
  margin_open: 3.0 # Wait time after train
  driver_reaction: 2.5 # Driver reaction time
```

### ML Configuration

Edit `ml/config.yaml`:

```yaml
training:
  n_samples: 1000 # Number of trains
  random_seed: 42 # Reproducibility

sensors:
  s0: 1500 # Sensor positions (meters)
  s1: 1000
  s2: 800
```

### Simulation Configuration

Edit `simulation/config.yaml`:

```yaml
traffic:
  cars_per_hour: 1200 # Traffic density

routing:
  adoption_rate: 0.70 # Smart routing adoption
```

## Outputs

### Data Files

```
outputs/data/
├── clearances.csv           # Vehicle crossing times
├── travels.csv              # Traffic light to crossing
├── raw_trajectories.csv     # Train simulation data
├── features.csv             # ML training features
├── phase1_vehicles.csv      # Baseline vehicle data
└── phase2_vehicles.csv      # Alternative route data
```

### Models

```
outputs/models/
├── eta_model.pkl            # ETA prediction model
└── etd_model.pkl            # ETD prediction model
```

### Visualizations

```
outputs/plots/
├── thresholds_analysis.png      # 6-panel threshold plots
├── train_trajectories.png       # Sample train paths
├── feature_distributions.png    # ML input data
├── eta_comprehensive.png        # 9-panel ETA evaluation
├── etd_comprehensive.png        # 9-panel ETD evaluation
└── physics_comparison.png       # Baseline comparison
```

### Results

```
outputs/results/
├── thresholds.yaml              # Calculated thresholds
├── evaluation_results.json      # ML performance
└── comparison.json              # Simulation comparison
```

### Hardware

```
hardware/
├── thresholds.h                 # Generated sensor config
├── eta_model.h                  # Generated prediction code
└── crossing_config.h            # Generated helpers
```

## Docker Environment

### Build and Run

```bash
make build      # Build Docker image
make up         # Start container
make down       # Stop container
make shell      # Open shell in container
```

### Manual Commands

```bash
# Inside container
python -m thresholds.collector --duration 300
python -m ml.data --samples 100
python -m simulation.controller --gui
```

## Troubleshooting

### SUMO Not Found

**Problem**: "sumo: command not found"

**Fix**:

```bash
# Ubuntu/Debian
sudo apt-get install sumo sumo-tools

# macOS
brew install sumo

# Or use Docker
make build
```

### Memory Issues

**Problem**: "MemoryError" during ML training

**Fix**: Reduce sample count

```bash
make ml-quick  # Uses 50 samples instead of 1000
```

### Network Generation Fails

**Problem**: "Network generation failed"

**Fix**: Check netconvert installation

```bash
netconvert --version  # Should show SUMO version
```

### Arduino Upload Fails

**Problem**: Headers not found

**Fix**: Generate headers first

```bash
make hw-export
```

## Development

### Running Tests

```bash
make test           # Quick test all modules
make th-quick       # Test thresholds
make ml-quick       # Test ML
make sim-network    # Test simulation
```

### Cleaning

```bash
make clean          # Clean all generated files
make th-clean       # Clean thresholds only
make ml-clean       # Clean ML only
make sim-clean      # Clean simulation only
```

## Limitations

**Assumptions**:

- Perfect train detection (no missed sensors)
- Known train schedule
- Uniform vehicle behavior
- No weather effects
- Single origin-destination pair

**Physical Demo Constraints**:

- Hand movement variability
- Very short timing (~0.2-2 seconds)
- No physics (momentum, inertia)
- Scaled distances (1:10,000)

## Future Work

**Enhanced Models**:

- Deep learning for better accuracy
- Multi-crossing networks
- Emergency vehicle priority
- Pedestrian integration

**Real Deployment**:

- Field testing with real sensors
- Integration with existing systems
- Multi-train coordination
- Weather-adaptive thresholds

## Citation

If you use this project in your research or education, please cite:

```
Smart Railway Crossing Control System
Authors: [Your Names]
Institution: [Your School]
Year: 2024
```

## License

[Your License Here]

## Contact

For questions or support:

- [Your Email]
- [Your GitHub]

## Acknowledgments

- SUMO traffic simulator
- scikit-learn ML library
- Arduino community
- [Your School/Advisors]

---

**Project Status**: Complete and tested

**Last Updated**: 2024

**Version**: 1.0
