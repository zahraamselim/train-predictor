# Level Crossing Notification System

Intelligent system for managing railway crossing safety using sensors, physics-based calculations, and machine learning.

## Project Structure

```
level-crossing-project/
├── config/                      # System configuration
│   ├── system.yaml             # All settings in one file
│   └── utils.py                # Config loader
│
├── physics/                     # Physics engines (consolidated)
│   ├── vehicle.py              # Vehicle motion physics
│   ├── train.py                # Train motion physics
│   └── sensors.py              # IR sensor detection logic
│
├── data_generation/            # Dataset generators
│   ├── generate_traffic.py    # Traffic clearance scenarios
│   ├── generate_train.py      # Train approach scenarios
│   ├── generate_decisions.py  # ML training data (wait vs reroute)
│   └── data/                   # Generated CSV files
│
├── ml/                         # Machine learning
│   ├── route_optimizer.py     # Wait vs reroute decision model
│   └── models/                 # Trained models (.pkl)
│
├── controller/                 # Core system logic
│   ├── eta_calculator.py      # Physics-based ETA prediction
│   ├── decision_maker.py      # Gate control + notifications
│   └── metrics.py             # Performance metrics calculator
│
├── simulation/                 # Pygame visualization
│   ├── main.py                # Main simulation loop
│   ├── map.py                 # Road network rendering
│   ├── vehicles.py            # Vehicle agents with physics
│   └── crossing.py            # Gates, lights, timers, buzzers
│
├── arduino/                    # Hardware deployment
│   ├── sketch.ino             # Arduino code
│   └── README.md              # Wiring guide
│
├── Makefile                    # Build commands
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Setup

```bash
make setup
source .venv/bin/activate
```

### 2. Generate Data

```bash
make data-all
```

This generates:

- Traffic clearance times for different densities
- Train approach scenarios with sensor timings
- Decision scenarios for ML training

### 3. Train ML Model

```bash
make ml-train
```

Trains Random Forest classifier to decide: should vehicles wait or reroute?

### 4. Run Simulation

```bash
make simulate
```

Controls:

- SPACE: Spawn train manually
- M: Show performance metrics
- ESC: Quit

## ML Component

**Problem**: Should vehicles at intersection wait for train or take alternative route?

**Features**:

- Train ETA (seconds)
- Queue length (vehicles)
- Traffic density (light/medium/heavy)
- Intersection distance (meters)
- Alternative route distance (meters)

**Output**: Action (wait/reroute) + confidence score

**Model**: Random Forest Classifier (100 trees, balanced classes)

## Design Requirements Metrics

The system calculates:

1. **Travel Time**: Average journey time with vs without system
2. **Fuel Consumption**: L/vehicle considering driving, idling, engine-off states
3. **Comfort**: Discomfort score factoring waiting uncertainty
4. **Emissions**: kg CO2 per vehicle based on fuel consumption

View metrics in real-time during simulation (press M).

## Workflow

### Complete Pipeline

```bash
make workflow
```

This runs:

1. Generate all datasets
2. Train ML model
3. Validate outputs

### Individual Steps

```bash
make data-traffic        # Traffic clearance data
make data-train          # Train approach data
make data-decisions      # ML training data
make ml-train           # Train model
make validate-all       # Check data quality
```

## Scale Modes

**Demo scale** (75x75cm board):

```bash
make scale-demo
```

**Real scale** (3km distances):

```bash
make scale-real
```

## Hardware Components

From Wokwi diagram:

1. **Railway sensors**: 3x IR obstacle avoidance sensors
2. **Crossing**: TM1637 display, servo gate, red/green LEDs
3. **Intersection**: Buzzer, red/green LEDs

See `arduino/README.md` for wiring details.

## Physics Models

### Vehicle

```
Stopping distance = v × t_reaction + v²/(2a_max)
Clearance time = (distance + vehicle_length) / speed
```

### Train

```
F_net = F_traction - F_resistance
a = F_net / mass
F_resistance = rolling + air_drag + grade
```

### Sensors

Binary detection: triggers when train passes over sensor.
Records entry/exit times for speed calculation.

## ETA Calculation

**Simple**: Constant speed assumption

```
speed = distance_1_to_2 / time_1_to_2
ETA = remaining_distance / speed
```

**Advanced**: Accounts for acceleration

```
Uses quadratic formula: d = v*t + 0.5*a*t²
```

## Design Parameters

Configurable in `config/system.yaml`:

- Vehicle types (mass, speed, accel, decel)
- Train types (power, braking, drag)
- Sensor positions
- Gate timing offsets
- Traffic densities
- Intersection distances

## Validation

```bash
make validate-all
```

Checks:

- Data integrity (no nulls, correct ranges)
- Physics correctness
- Sensor timing order
- ML model accuracy

## File Count Reduction

**Before**: 36 files across 11 directories
**After**: ~20 files across 7 directories

**Key consolidations**:

- 01_traffic + 03_train → physics/
- 04_prediction + 05_integration → controller/
- All data generation → data_generation/
- Single ML module instead of scattered

## Example Usage

### Testing ML Model

```python
from ml.route_optimizer import RouteOptimizer

optimizer = RouteOptimizer('ml/models/route_optimizer.pkl')
result = optimizer.predict(
    train_eta=45,           # seconds
    queue_length=5,         # vehicles
    traffic_density='medium',
    intersection_distance=500,    # meters
    alternative_route_distance=1200
)

print(result)
# {'action': 'reroute', 'confidence': 0.87, ...}
```

### Calculating Metrics

```python
from controller.metrics import PerformanceMetrics

metrics = PerformanceMetrics()

# Log vehicle journeys during simulation
for vehicle in completed_vehicles:
    metrics.log_vehicle_journey({
        'vehicle_id': vehicle.id,
        'system_active': True,
        'total_travel_time': vehicle.total_time,
        'waiting_time': vehicle.wait_time,
        'knew_wait_time': True,
        'action_taken': 'wait',
        ...
    })

# Generate report
report = metrics.generate_full_report()
metrics.print_report()
```

## Dependencies

```
numpy
pandas
scikit-learn
pygame
pyyaml
```

Install with: `make setup`

## License

Educational project for capstone requirements.
