# Intelligent Level Crossing Control System

High school capstone project implementing ML-based railway crossing control with comprehensive performance metrics.

## Project Overview

This system uses SUMO traffic simulation to design and test an intelligent railway level crossing control system. The system:

- Predicts train arrival time using machine learning
- Controls gates with optimal timing
- Notifies intersections for vehicle rerouting decisions
- Recommends engine-off periods to save fuel and reduce emissions
- Tracks comprehensive performance metrics
- Deploys to Arduino hardware for physical implementation

## System Architecture

```
simulation/
├── network/          SUMO network generation
├── data/            Data collection and analysis
├── ml/              ML model training and export
└── control/         Control logic and metrics

hardware/
└── arduino/         Arduino implementation

config/              Configuration files
outputs/             Generated data and reports
scripts/             Main execution scripts
```

## Key Features

### 1. ML-Based ETA Prediction

- Decision tree model optimized for Arduino deployment
- Advanced feature engineering (speed variance, deceleration rate)
- Trained on 250+ simulation samples
- Sub-second prediction accuracy

### 2. Intelligent Control

- Optimal gate timing based on predicted ETA
- Intersection notification with buzzer and lights
- Vehicle rerouting recommendations
- Engine-off suggestions for long waits

### 3. Comprehensive Metrics

- Travel time savings from rerouting
- Wait time reduction
- Traffic comfort scoring
- Fuel consumption and savings
- CO2 emissions reduction

### 4. Hardware Deployment

- Arduino Uno R3 compatible
- 3 IR sensors for train detection
- Servo-controlled gates
- LED indicators and countdown display
- Buzzer for audio alerts

## Quick Start

### Prerequisites

- Docker and Docker Compose
- SUMO 1.14+ (included in container)
- Python 3.8+ (included in container)
- Arduino IDE (for hardware deployment)

### Setup

1. Build the Docker environment:

```bash
make build
```

2. Run the complete pipeline:

```bash
make pipeline
```

This will:

- Generate SUMO network
- Collect training data (1 hour simulation)
- Calculate control thresholds
- Collect ETA training data
- Train ML model
- Export to Arduino

### Running Simulation

Without GUI:

```bash
make simulate
```

With GUI:

```bash
make gui
```

### View Metrics

```bash
make metrics
```

Detailed reports are saved in `outputs/metrics/`.

## Performance Metrics

The system tracks and optimizes:

### 1. Travel Time

- Total time saved through rerouting
- Average time per rerouted vehicle
- Comparison: wait vs alternative route

### 2. Wait Time

- Total wait time at crossings
- Average wait per vehicle
- Queue length distribution

### 3. Traffic Comfort

- Composite score (0-1)
- Based on queue length and wait duration
- Measured throughout simulation

### 4. Fuel Consumption

- Total fuel used
- Fuel saved through engine-off
- Reduction percentage

### 5. Emissions

- Total CO2 emissions
- Emissions saved through engine-off
- Environmental impact

## ML Model Details

### Features

- Time between sensor triggers (2 features)
- Speeds at sensor locations (2 features)
- Acceleration rate
- Distance to crossing
- Average speed
- Speed variance
- Deceleration rate

### Model Type

Decision tree regressor optimized for:

- Low complexity (Arduino deployment)
- High accuracy (MAE < 0.5s)
- Fast inference (<1ms)

### Training Process

1. Simulate 250+ train passes with varying speeds
2. Collect sensor trigger times and actual ETAs
3. Engineer advanced features
4. Train decision tree with depth optimization
5. Export to C header file

## Hardware Components

### Arduino Uno R3

- Microcontroller: ATmega328P
- Operating Voltage: 5V
- Digital I/O Pins: 14

### Sensors

- 3x PIR Motion Sensors (train detection)
- Positions: 54cm, 32.4cm, 16.2cm from crossing

### Actuators

- 1x Servo Motor (gate control)
- 4x LEDs (status indicators)
- 1x Buzzer (audio alert)
- 1x TM1637 (countdown display)

## Configuration

### Simulation Parameters

Edit `config/simulation.yaml`:

- Simulation duration
- Train spawn frequency
- Vehicle densities
- Safety margins

### Thresholds

Generated automatically in `config/thresholds.yaml`:

- Gate closure timing
- Gate opening timing
- Intersection notification
- Engine-off recommendation

## Project Structure Details

### Data Collection

`simulation/data/collector.py`: Collects training data

- Vehicle clearance times
- Train passage times
- Intersection travel times

### Threshold Analysis

`simulation/data/analyzer.py`: Calculates control thresholds

- 95th percentile vehicle clearance
- Maximum train passage time
- Intersection travel times
- Sensor placement

### ML Training

`simulation/ml/train_eta.py`: Trains ETA prediction model

- Collects ETA samples
- Engineers features
- Trains decision tree
- Validates accuracy

### Control System

`simulation/control/crossing_controller.py`: Main control logic

- Track trains and calculate ETA
- Control gates based on thresholds
- Notify intersections
- Manage vehicle engines

`simulation/control/rerouter.py`: Vehicle rerouting

- Calculate route alternatives
- Make rerouting decisions
- Track time savings

`simulation/control/metrics.py`: Performance tracking

- Track all metrics in real-time
- Generate comprehensive reports
- Save detailed CSV files

## Capstone Requirements

This project addresses the following requirements:

### Design Requirements

1. Three measurable parameters: ETA accuracy, gate timing, emissions reduction
2. Improves traffic quality: Reduced wait time, fuel savings, better comfort
3. Uses ICT: ML for prediction, sensors for detection, automated control
4. Contains hardware: Arduino with sensors, actuators, display

### Constraints

1. Testable system: Comprehensive simulation and metrics
2. Observable inputs/outputs: Real-time logging and visualization
3. Cost-effective: Uses standard Arduino components
4. Documented: Complete logbook in outputs/

### Grand Challenges Addressed

- Urban congestion reduction through rerouting
- Pollution reduction through engine-off strategy
- Public safety through optimal gate timing

## Development

### Adding Features

1. Modify control logic in `simulation/control/`
2. Update metrics in `simulation/control/metrics.py`
3. Test in simulation
4. Export to Arduino if needed

### Debugging

View logs in real-time:

```bash
make simulate
```

Check specific metrics:

```bash
cat outputs/metrics/vehicle_metrics.csv
```

### Testing

Run specific pipeline steps:

```bash
make network    # Test network generation
make data       # Test data collection
make train      # Test ML training
```

## Results

Expected performance improvements:

- Travel time: 5-10% reduction
- Wait time: 20-30% reduction
- Fuel consumption: 15-20% reduction
- CO2 emissions: 15-20% reduction
- Traffic comfort: 30-40% improvement

## License

Educational project for high school capstone.

## Authors

Zahraa Selim

## Acknowledgments

- SUMO Traffic Simulation Suite
- Arduino Community
- Wokwi Online Simulator
