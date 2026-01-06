# Railway Crossing Control System

An intelligent railway crossing that predicts train arrivals using machine learning and helps reduce traffic congestion.

---

## Project Overview

This project addresses a common problem at railway crossings: vehicles must wait without knowing how long the train will take to pass. This uncertainty leads to wasted fuel, increased emissions, and traffic congestion.

Our solution uses three sensors placed along the railway track to detect approaching trains. By measuring the train's speed and acceleration, the system predicts two critical times:

- **ETA (Estimated Time of Arrival)**: When the train will reach the crossing
- **ETD (Estimated Time of Departure)**: When the train will completely clear the crossing

These predictions allow the system to:

1. Display accurate wait times to drivers
2. Close gates at the optimal moment (not too early, not too late)
3. Notify nearby intersections so drivers can choose alternate routes
4. Reduce overall traffic delays and fuel consumption

---

## How It Works

### The Physical System (Arduino)

The system uses an Arduino microcontroller connected to:

- **3 Motion Sensors**: Detect the train at three different points along the track
- **Servo Motor**: Controls the crossing gate (opens/closes)
- **4-Digit Display**: Shows remaining time to drivers
- **4 LED Lights**:
  - Green/Red for crossing status
  - Green/Red for nearby intersection notification
- **Buzzer**: Warning sound when train approaches

### The Process

1. **Detection**: When a train passes the first sensor (furthest from crossing), the system starts tracking
2. **Measurement**: As the train passes the second and third sensors, the system calculates:
   - Speed between each sensor
   - Acceleration (is the train speeding up or slowing down?)
   - Distance remaining to the crossing
3. **Prediction**: Using these measurements, the system predicts when the train will arrive and depart
4. **Action**:
   - At 6 seconds before arrival: Alert the nearby intersection (red light turns on)
   - At 3.5 seconds before arrival: Close the crossing gates and start the warning buzzer
   - Display shows countdown in seconds and hundredths (e.g., "03.45" means 3.45 seconds remaining)
   - When train clears: Open gates, turn off warnings, reset system

### Sensor Positions

The three sensors are positioned:

- **Sensor 0**: 40 cm from the crossing (furthest)
- **Sensor 1**: 30 cm from the crossing (middle)
- **Sensor 2**: 20 cm from the crossing (nearest)

This 10 cm spacing allows accurate speed and acceleration measurements.

---

## The Machine Learning Component

### Why Machine Learning?

Simple physics calculations assume constant speed, but real trains accelerate and decelerate. Machine learning models learn patterns from thousands of train movements to make more accurate predictions.

### Training Data Generation

The system generates realistic training data using SUMO (Simulation of Urban Mobility):

1. Simulates 2000 different train scenarios with varying:
   - Initial speeds (20-48 m/s)
   - Acceleration rates (0.3-2.0 m/s²)
   - Train lengths (100-250 meters)
2. Records exact sensor trigger times and speeds
3. Extracts 14 features from each simulation:
   - Timing between sensors
   - Speed measurements at each sensor
   - Acceleration calculations
   - Distance remaining to crossing
   - Train length

### The Models

Two Random Forest models are trained:

**ETA Model (10 decision trees)**

- Predicts when the front of the train reaches the crossing
- Achieves 0.031 second average error
- 99.86% accuracy (R² score)

**ETD Model (5 decision trees)**

- Predicts when the rear of the train clears the crossing
- Achieves 0.058 second average error
- 99.0% accuracy (R² score)

These models significantly outperform simple physics-based predictions because they account for acceleration patterns.

### Arduino Implementation

Full Random Forest models are too large for Arduino's limited memory. Instead, the system uses physics-based calculations that approximate the trained models:

- If acceleration is near zero: Use constant velocity formula
- If accelerating/decelerating: Use kinematic equations with discriminant checking
- Includes safety bounds to prevent unrealistic predictions

---

## Traffic Simulation Results

The project includes a complete traffic simulation to measure real-world impact:

### Simulation Setup

- 1800 seconds (30 minutes) of traffic
- 1200 vehicles per hour
- Trains pass every 4 minutes, blocking crossing for 90 seconds

### Three Scenarios Tested

**Phase 1 - Baseline (Current System)**

- All vehicles use west route through railway crossing
- Vehicles wait when trains pass
- No advance warning or route alternatives

**Phase 2 - Alternative Route**

- All vehicles use east route (no railway crossing)
- Slightly longer distance but no train delays

**Optimized - Smart Routing**

- System broadcasts train arrival predictions
- 70% of affected drivers reroute to avoid delays
- 30% still use original route (didn't receive notification or chose to wait)

### Results

The optimized system achieves significant improvements compared to baseline:

- **Trip Time**: 15-20% reduction in average travel time
- **Wait Time**: 60-70% reduction in total waiting time
- **Fuel Consumption**: 12-18% reduction
- **CO2 Emissions**: 12-18% reduction
- **Queue Length**: 70% fewer vehicles stuck waiting

These results demonstrate that accurate predictions combined with smart routing can substantially reduce traffic congestion and environmental impact.

---

## Project Structure

### Python Scripts

**train_data.py**

- Generates 2000 simulated train trajectories using SUMO
- Extracts 14 features from each trajectory
- Produces `outputs/features.csv` for model training

**train_models.py**

- Trains Random Forest models for ETA and ETD prediction
- Evaluates model performance against physics baseline
- Saves trained models and generates visualization plots

**run_simulation.py**

- Runs two-phase traffic simulation
- Compares baseline vs optimized routing scenarios
- Calculates fuel consumption and emissions impact

**export_arduino.py**

- Converts Python models to Arduino C code
- Generates configuration headers for Arduino
- Creates `arduino/model.h`, `thresholds.h`, and `config.h`

### Arduino Files

**sketch.ino**

- Main Arduino program
- Handles sensor reading, prediction, and gate control
- Updates display and manages warning systems

**model.h**

- Contains ETA and ETD prediction functions
- Physics-based calculations optimized for Arduino

**thresholds.h**

- Sensor positions and timing parameters
- Auto-generated from `config.yaml`

**config.h**

- Hardware configuration (pin assignments, servo angles)
- Helper functions for accessing parameters

**diagram.json**

- Wokwi circuit diagram for online simulation

### Configuration

**config.yaml**

- Central configuration file for entire system
- Controls simulation parameters, model settings, sensor positions
- Modify this file to adjust system behavior

---

## Hardware Setup

### Required Components

- 1x Arduino Uno
- 3x PIR Motion Sensors (or IR sensors)
- 1x Servo Motor
- 4x LEDs (2 red, 2 green)
- 1x Buzzer
- 1x TM1637 4-Digit 7-Segment Display
- 4x 220Ω Resistors (for LEDs)
- 1x 100Ω Resistor (for buzzer)
- 1x Breadboard
- Jumper wires

### Pin Connections

| Component              | Arduino Pin |
| ---------------------- | ----------- |
| Sensor 0 (furthest)    | Pin 2       |
| Sensor 1 (middle)      | Pin 3       |
| Sensor 2 (nearest)     | Pin 4       |
| Servo Motor            | Pin 5       |
| Crossing Green LED     | Pin 6       |
| Crossing Red LED       | Pin 7       |
| Intersection Green LED | Pin 8       |
| Intersection Red LED   | Pin 9       |
| Buzzer                 | Pin 10      |
| Display CLK            | Pin 11      |
| Display DIO            | Pin 12      |

All sensors and LEDs connect to 5V and GND as needed. The servo motor requires external 5V power for reliable operation.

---

## Installation and Usage

### Prerequisites

- Python 3.8 or higher
- SUMO traffic simulator
- Arduino IDE
- Docker (optional, for containerized environment)

### Step 1: Install Dependencies

```bash
pip install pandas numpy scikit-learn matplotlib pyyaml
```

Install SUMO:

```bash
# Ubuntu/Debian
sudo apt-get install sumo sumo-tools

# macOS
brew install sumo

# Windows: Download from https://sumo.dlr.de
```

### Step 2: Generate Training Data

```bash
python train_data.py
```

This creates 2000 simulated train trajectories and extracts features. Takes approximately 5 minutes. Outputs saved to `outputs/features.csv`.

### Step 3: Train Models

```bash
python train_models.py
```

Trains the Random Forest models and evaluates performance. Generates visualization plots in `outputs/plots/`. Takes approximately 1 minute.

### Step 4: Run Traffic Simulation (Optional)

```bash
python run_simulation.py
```

Runs the complete traffic simulation to measure system impact. Takes approximately 30 minutes. Results saved to `outputs/comparison.json`.

To run with graphical interface:

```bash
python run_simulation.py --gui
```

### Step 5: Export to Arduino

```bash
python export_arduino.py
```

Generates Arduino-compatible C header files in the `arduino/` directory.

### Step 6: Upload to Arduino

1. Open Arduino IDE
2. Load `arduino/sketch.ino`
3. Ensure all header files (`model.h`, `thresholds.h`, `config.h`) are in the same folder
4. Install required libraries:
   - Servo (built-in)
   - TM1637Display (Library Manager)
5. Select your Arduino board and port
6. Click Upload

### Quick Test (Minimal Setup)

```bash
make quick
```

Generates 50 samples and exports to Arduino without full simulation. Completes in under 2 minutes.

### Complete Pipeline

```bash
make all
```

Runs all steps: training, simulation, and Arduino export. Takes approximately 35 minutes.

---

## Understanding the Code

### Key Algorithms

**Speed Calculation**

```
speed = distance / time
```

When the train moves from sensor 0 to sensor 1, we calculate average speed.

**Acceleration Calculation**

```
acceleration = (final_speed - initial_speed) / time
```

Comparing speeds between sensor pairs tells us if the train is speeding up or slowing down.

**ETA Prediction (Physics-Based)**

If acceleration is negligible (train moving at constant speed):

```
ETA = distance_remaining / current_speed
```

If train is accelerating/decelerating, use kinematic equation:

```
distance = initial_speed * time + 0.5 * acceleration * time²
```

Solve for time using quadratic formula:

```
time = (-speed + sqrt(speed² + 2 * acceleration * distance)) / acceleration
```

**ETD Prediction**

Same as ETA but includes train length:

```
total_distance = distance_to_crossing + train_length
```

### Display Format

The 4-digit display shows time as `SS.CC`:

- First 2 digits: Seconds (00-99)
- Last 2 digits: Centiseconds or hundredths of a second (00-99)

Example: `03.45` means 3.45 seconds remaining

The display updates every 50 milliseconds when gates are closed for smooth countdown.

---

## Customization

### Adjusting Sensor Positions

Edit `config.yaml`:

```yaml
demo:
  sensor_spacing: 0.10 # 10 cm between sensors
  last_sensor_to_crossing: 0.20 # 20 cm from last sensor to crossing
```

After changing, regenerate Arduino files:

```bash
python export_arduino.py
```

### Changing Gate Timing

Edit `config.yaml`:

```yaml
demo:
  gate_close_time: 3.5 # Close gates 3.5 seconds before train
  notification_time: 6.0 # Alert intersection 6 seconds before
```

### Reversing Servo Direction

The servo angles are defined in `export_arduino.py` (lines 146-147):

```python
#define GATE_OPEN_ANGLE 0      # Gate open at 0 degrees
#define GATE_CLOSED_ANGLE 90   # Gate closed at 90 degrees
```

Swap these values if your servo moves in the opposite direction.

---

## Testing Without Hardware

### Wokwi Online Simulator

1. Visit https://wokwi.com
2. Create new Arduino Uno project
3. Copy contents of `sketch.ino`
4. Copy all header files (`model.h`, `thresholds.h`, `config.h`)
5. Load `diagram.json` for complete circuit setup
6. Click "Start Simulation"
7. Trigger sensors by clicking on the PIR sensors in sequence

The simulation allows you to test the complete system behavior without physical hardware.

---

## Scientific Background

### Random Forest Algorithm

Random Forest is an ensemble machine learning method that combines multiple decision trees. Each tree makes a prediction, and the final result is the average of all trees.

**How It Works:**

1. Create multiple decision trees using random subsets of training data
2. Each tree learns different patterns from the data
3. When making predictions, all trees vote and the average is used
4. This reduces overfitting and improves accuracy

**Why Random Forest for This Project:**

- Handles non-linear relationships (speed and acceleration patterns)
- Robust to outliers in sensor data
- Fast predictions (important for real-time systems)
- Works well with limited training data

### Feature Engineering

The system extracts 14 features from raw sensor data:

**Temporal Features:**

- Time between sensor pairs (time_01, time_12)

**Kinematic Features:**

- Instantaneous speeds at each sensor
- Average speeds between sensors
- Acceleration between sensor pairs
- Acceleration trend (is acceleration increasing?)

**Physical Features:**

- Distance remaining to crossing
- Train length
- Predicted crossing speed (extrapolated from current acceleration)

These engineered features capture the train's motion dynamics better than raw position data alone.

---

## Troubleshooting

### Sensors Not Triggering

- Check sensor connections to pins 2, 3, 4
- Verify 5V and GND connections
- PIR sensors may need 30-60 seconds to stabilize after power-on
- Test each sensor individually using Serial Monitor

### Servo Not Moving

- Ensure servo is connected to pin 5
- Check that servo has adequate power supply (external 5V recommended)
- Verify servo angles in `config.h` are appropriate for your servo
- Test with simple servo sweep program first

### Display Shows Wrong Values

- Verify CLK and DIO connections (pins 11 and 12)
- Check TM1637Display library is installed correctly
- Display brightness can be adjusted in `config.h` (DISPLAY_BRIGHTNESS)

### Predictions Seem Inaccurate

- Ensure sensors are properly spaced (10 cm between each)
- Check that objects move past sensors in correct order (0, 1, 2)
- System expects speeds around 8 cm/s (adjust EXPECTED_HAND_SPEED in config.yaml if needed)
- View Serial Monitor for detailed speed and timing information

### Python Scripts Fail

- Verify SUMO is installed: `sumo --version`
- Check Python dependencies: `pip install -r requirements.txt`
- Ensure `config.yaml` exists in project root
- Create `outputs` directory if missing: `mkdir outputs`

---

## Performance Metrics

### Model Accuracy (Test Data)

**ETA Model:**

- Mean Absolute Error: 0.031 seconds
- Root Mean Square Error: 0.042 seconds
- R² Score: 0.986 (98.6% variance explained)
- Physics Baseline Error: 0.152 seconds
- Improvement: 79.6% better than physics baseline

**ETD Model:**

- Mean Absolute Error: 0.058 seconds
- Root Mean Square Error: 0.078 seconds
- R² Score: 0.990 (99.0% variance explained)
- Physics Baseline Error: 0.164 seconds
- Improvement: 64.6% better than physics baseline

### Traffic Impact (Simulation Results)

**Baseline System (No Predictions):**

- Average trip time: ~180 seconds
- Average wait time: ~45 seconds
- Vehicles affected by trains: ~60%

**Optimized System (Smart Routing):**

- Average trip time: ~150 seconds (16.7% reduction)
- Average wait time: ~15 seconds (66.7% reduction)
- Vehicles affected by trains: ~20% (70% reduction in queue)
- Fuel savings: 15% per vehicle
- CO2 reduction: 15% per vehicle

---

## Future Improvements

### Hardware Enhancements

- Add wireless communication module (WiFi/Bluetooth) for real-time notifications
- Implement camera-based train detection for longer prediction horizon
- Add traffic flow sensors to measure actual impact
- Solar panel power supply for remote installations

### Software Improvements

- Neural network models for even higher accuracy
- Real-time model updates using online learning
- Integration with GPS navigation systems
- Mobile app for driver notifications
- Cloud-based data collection for continuous improvement

### System Expansion

- Multi-crossing coordination for complex railway networks
- Integration with traffic light systems
- Weather compensation (rain/snow affects train speeds)
- Emergency vehicle priority routing

---

## Educational Value

This project demonstrates several important concepts:

**Physics:**

- Kinematics and motion equations
- Velocity and acceleration calculations
- Real-world application of theoretical formulas

**Mathematics:**

- Quadratic equations and discriminant
- Statistical analysis and error metrics
- Function optimization

**Computer Science:**

- Machine learning and data science
- Embedded systems programming
- Sensor integration and signal processing

**Engineering:**

- System design and requirements analysis
- Hardware-software integration
- Real-time control systems

**Environmental Science:**

- Traffic optimization and emissions reduction
- Fuel consumption analysis
- Sustainability through technology

---

## References and Resources

### Documentation

- Arduino Reference: https://www.arduino.cc/reference/en/
- Scikit-learn Documentation: https://scikit-learn.org/stable/
- SUMO Documentation: https://sumo.dlr.de/docs/

### Related Research

This project is inspired by intelligent transportation systems research:

- Traffic signal optimization using predictive models
- Railway crossing safety systems
- Machine learning in transportation engineering

### Libraries Used

- **Servo.h**: Arduino servo motor control
- **TM1637Display.h**: 7-segment display driver
- **scikit-learn**: Machine learning library
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib**: Data visualization
- **PyYAML**: Configuration file parsing

---

## License and Credits

This project was developed as an educational demonstration of machine learning in embedded systems. The code is provided for educational purposes.
