### The 14 Features

From three sensor timestamps, we calculate 14 measurements that describe the train's motion:

| # | Feature | Formula | Purpose |
|---|---------|---------|---------|
| 1 | time_01 | t₁ - t₀ | Time between sensors 0 and 1 |
| 2 | time_12 | t₂ - t₁ | Time between sensors 1 and 2 |
| 3 | dist_01 | 0.1m | Distance between sensors 0 and 1 |
| 4 | dist_12 | 0.1m | Distance between sensors 1 and 2 |
| 5 | dist_2c# Railway Crossing Control System

An intelligent railway crossing that predicts train arrivals using machine learning to reduce traffic congestion, save fuel, and lower emissions.

**Project by:** Somaya Selim & Lana Bassem  
**School:** Dakahlia STEM School, Grade 12  
**Project ID:** 13330

---

## The Problem

In Egypt and many cities worldwide, trains operate without fixed schedules. When a train approaches, the crossing gate closes early "just to be safe," forcing vehicles to wait without knowing how long. This causes:

- Traffic congestion and long queues
- Wasted fuel from idling engines
- Air pollution from vehicle emissions
- Driver frustration and time loss

**Our solution:** A smart system that predicts exactly when the train will arrive and depart, closing the gate only when necessary and displaying the exact wait time to drivers.

---

## How It Works

### Hardware Setup

The system uses an Arduino Uno with:

- **3 IR Sensors**: Detect the train at three points along the track (50cm, 40cm, 30cm from crossing)
- **Servo Motor**: Controls the crossing gate (opens/closes)
- **TM1637 Display**: Shows countdown time in MM:SS format
- **4 LEDs**: 
  - Crossing: Green (safe) / Red (train coming)
  - Intersection: Green (clear) / Red (reroute recommended)
- **Buzzer**: Warning sound with pattern alerts

### The Process

1. **Detection Phase**: Train passes three sensors spaced 10cm apart
   - Sensor 0 triggers at t₀ (furthest from crossing)
   - Sensor 1 triggers at t₁ (middle position)
   - Sensor 2 triggers at t₂ (nearest to crossing)

2. **Calculation Phase**: System extracts 14 features from timestamps:
   ```
   time_01 = t₁ - t₀
   time_12 = t₂ - t₁
   speed_01 = 0.1m / time_01
   speed_12 = 0.1m / time_12
   acceleration = (speed_12 - speed_01) / time_12
   ```

3. **Prediction Phase**: Machine learning model predicts:
   - **ETA** (Estimated Time of Arrival): When train front reaches crossing
   - **ETD** (Estimated Time of Departure): When train rear clears crossing

4. **Action Phase**:
   - At 2.5 seconds: Intersection alert (red LED) + buzzer starts
   - At 1.0 seconds: Gate closes, crossing red LED flashes
   - Display shows live countdown
   - At ETD = 0: Gate opens, all alerts clear

---

## The Machine Learning Model

### Training Data Generation

We used SUMO (traffic simulation software) to create 2000 realistic train scenarios:

- **Speed variations**: 20-48 m/s (simulated as 5-15 cm/s for physical demo)
- **Acceleration patterns**: 0.3-2.0 m/s² (accelerating, decelerating, steady)
- **Train lengths**: 100-250 m (simulated as 10-25 cm)

Each simulation recorded the complete train trajectory, from which we extracted sensor trigger times and calculated features.

### The 14 Features

From three sensor timestamps and known geometry, we calculate 14 features that describe the train's motion:

| # | Feature | Formula | Purpose |
|---|---------|---------|---------|
| 1 | time_01 | t₁ - t₀ | Time interval sensor 0→1 |
| 2 | time_12 | t₂ - t₁ | Time interval sensor 1→2 |
| 3 | total_time | t₂ - t₀ | Total time across both sensors |
| 4 | dist_01 | 0.1m | Distance between sensors 0 and 1 |
| 5 | dist_12 | 0.1m | Distance between sensors 1 and 2 |
| 6 | dist_to_crossing | 0.3m | Distance from sensor 2 to crossing |
| 7 | speed_01 | dist_01 / time_01 | Speed in first section |
| 8 | speed_12 | dist_12 / time_12 | Speed in second section |
| 9 | acceleration | (speed_12 - speed_01) / time_12 | Rate of speed change |
| 10 | speed_change | speed_12 - speed_01 | Velocity difference |
| 11 | train_length | 0.15m | Length of train |
| 12 | total_distance | dist_to_crossing + train_length | Total distance for ETD (0.45m) |
| 13 | eta_baseline | dist_to_crossing / speed_12 | Simple physics ETA estimate |
| 14 | etd_baseline | total_distance / speed_12 | Simple physics ETD estimate |

**Feature Categories:**

- **Temporal Features (1-3)**: Direct timing measurements from sensors
- **Geometric Features (4-6)**: Distances defining the system layout
- **Kinematic Features (7-10)**: Velocity and acceleration calculations
- **Physical Constants (11-12)**: Train geometry
- **Baseline Predictions (13-14)**: Simple physics estimates that the ML model learns to correct

**Why Include Baseline Predictions as Features?**

Features 13 and 14 give the model a "starting point" - the simple constant-speed prediction. The Random Forest then learns patterns like:
- "When eta_baseline = 3.0s but acceleration is negative, actual ETA is usually 3.4s"
- "When train is decelerating at -0.05 m/s², add 13% to baseline estimate"

This is called "residual learning" - the model learns to correct a simple estimate rather than predicting from scratch, which often gives better results.

### Random Forest Algorithm

We use **Random Forest Regressor** - a machine learning algorithm that:

1. Creates multiple decision trees (10 for ETA, 5 for ETD)
2. Each tree makes its own prediction
3. Final prediction = average of all trees

**Example prediction:**
```
Tree 1: ETA = 3.21s
Tree 2: ETA = 3.45s
Tree 3: ETA = 3.18s
...
Tree 10: ETA = 3.52s

Final ETA = (3.21 + 3.45 + ... + 3.52) / 10 = 3.35s
```

The averaging produces smooth, continuous predictions and is more accurate than any single tree.

### Model Performance

**ETA Model (10 trees):**
- Mean Absolute Error: **0.031 seconds**
- R² Score: **0.986** (98.6% accuracy)
- Improvement over physics: **44.9%**

**ETD Model (5 trees):**
- Mean Absolute Error: **0.058 seconds**
- R² Score: **0.990** (99.0% accuracy)
- Improvement over physics: **28.1%**

**Why better than simple physics?**

Physics formula assumes constant speed: `time = distance / speed`

But trains accelerate and decelerate! The ML model learned from 2000 examples to account for:
- Speed changes during approach
- Deceleration patterns when braking
- Acceleration variations across different trains

---

## Traffic Impact Simulation

We simulated 30 minutes of traffic (1200 vehicles/hour) with trains passing every 4 minutes:

### Three Scenarios Tested

**Baseline (Current System):**
- All vehicles use route through railway crossing
- Gate closes early "just to be safe"
- Vehicles wait without knowing duration

**Alternative Route:**
- All vehicles use detour (no railway crossing)
- Slightly longer distance but no train delays

**Optimized (Our System):**
- System broadcasts train arrival predictions at 2.5 seconds
- 70% of affected drivers reroute to avoid delay
- 30% still wait (didn't receive alert or chose to wait)

### Results

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| Travel Time | 180s | 91.5s | **49.2%** |
| Wait Time | 45s | ~0s | **100%** for rerouters |
| Fuel Used | 0.5L | 0.497L | **0.5%** |
| CO₂ Emissions | 1.155kg | 1.149kg | **0.5%** |
| Queue Length | 60 vehicles | 33 vehicles | **45.2%** |

The optimized system significantly reduced travel time and queue size by enabling smart routing based on accurate predictions.

---

## Project Structure

### Python Scripts

**train_data.py**
- Generates 2000 train trajectories using SUMO
- Extracts 14 features from each run
- Outputs: `outputs/features.csv`

**train_models.py**
- Trains Random Forest models for ETA and ETD
- Evaluates performance vs physics baseline
- Outputs: `outputs/eta_model.pkl`, `outputs/etd_model.pkl`, `outputs/model_results.json`

**run_simulation.py**
- Runs traffic simulation (baseline, alternative, optimized)
- Calculates fuel consumption and emissions
- Outputs: `outputs/comparison.json`

**export_arduino.py**
- Converts Python models to Arduino C code
- Generates configuration headers
- Outputs: `arduino/model.h`, `arduino/thresholds.h`, `arduino/config.h`

### Arduino Files

**sketch.ino**
- Main program
- Reads sensors, makes predictions, controls gate
- Updates display and manages alerts

**model.h**
- ETA and ETD prediction functions
- Physics-based calculations (optimized for Arduino memory)

**thresholds.h**
- Sensor positions: 0.5m, 0.4m, 0.3m from crossing
- Timing thresholds: gate close at 1.0s, notify at 2.5s

**config.h**
- Hardware configuration (pin assignments, servo angles)
- Gate angles: OPEN=90°, CLOSED=0°

### Configuration

**config.yaml**
- Central configuration for entire system
- Controls simulation parameters, model settings, sensor positions

---

## Hardware Components

### Required Parts

- 1× Arduino Uno
- 3× IR Motion Sensors (or PIR sensors)
- 1× Servo Motor
- 4× LEDs (2 red, 2 green)
- 1× Buzzer
- 1× TM1637 4-Digit Display
- 4× 220Ω Resistors (for LEDs)
- 1× 100Ω Resistor (for buzzer)
- 1× Breadboard
- Jumper wires
- 4× AA Batteries (for servo external power)

### Pin Connections

| Component | Arduino Pin |
|-----------|-------------|
| Sensor 0 (50cm) | Pin 2 |
| Sensor 1 (40cm) | Pin 3 |
| Sensor 2 (30cm) | Pin 4 |
| Servo Motor | Pin 5 |
| Crossing Green LED | Pin 6 |
| Crossing Red LED | Pin 7 |
| Intersection Green LED | Pin 8 |
| Intersection Red LED | Pin 9 |
| Buzzer | Pin 10 |
| Display CLK | Pin 11 |
| Display DIO | Pin 12 |
| 5V and GND | As needed |

**Power Note:** Servo motor requires external 5V (4× AA batteries) for reliable operation. Connect servo GND to Arduino GND for common ground.

---

## Installation

### Prerequisites

- Python 3.8+
- SUMO traffic simulator
- Arduino IDE
- Docker (optional)

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

Generates 2000 train trajectories (~5 minutes). Output: `outputs/features.csv`

### Step 3: Train ML Models

```bash
python train_models.py
```

Trains Random Forest models (~1 minute). Outputs: `outputs/eta_model.pkl`, `outputs/etd_model.pkl`

### Step 4: Run Traffic Simulation (Optional)

```bash
python run_simulation.py
```

Full simulation (~30 minutes). Output: `outputs/comparison.json`

For GUI mode:
```bash
python run_simulation.py --gui
```

### Step 5: Export to Arduino

```bash
python export_arduino.py
```

Generates Arduino headers in `arduino/` directory.

### Step 6: Upload to Arduino

1. Open Arduino IDE
2. Load `arduino/sketch.ino`
3. Install TM1637Display library (Sketch → Include Library → Manage Libraries)
4. Select Arduino Uno and correct port
5. Click Upload

### Quick Test (2 minutes)

```bash
make quick
```

Generates 50 samples and exports to Arduino without full simulation.

### Complete Pipeline (35 minutes)

```bash
make all
```

Runs training → simulation → Arduino export.

---

## Usage

### Testing the System

1. Power on Arduino
2. Slowly move your hand across the three sensors in order (0 → 1 → 2)
3. Expected speed: ~8 cm/s (similar to train demo scale)

**System Response:**
- At sensor 2 trigger: Predictions calculated
- At 2.5s remaining: Intersection red LED on, buzzer starts
- At 1.0s remaining: Gate closes, crossing red LED flashes
- Display shows countdown in MM:SS format
- At 0s: Gate opens, all alerts clear

### Adjusting Parameters

Edit `config.yaml` then run `python export_arduino.py`:

```yaml
demo:
  sensor_spacing: 0.10          # 10cm between sensors
  last_sensor_to_crossing: 0.30 # 30cm from sensor 2 to crossing
  gate_close_time: 1.0          # Close gate at 1.0s
  notification_time: 2.5        # Alert at 2.5s
  train_length: 0.15            # 15cm train length
```

---

## Understanding the Results

### What is R² Score?

R² (coefficient of determination) measures prediction accuracy on a scale of 0 to 1:
- **R² = 1.0**: Perfect predictions
- **R² = 0.5**: Model explains 50% of variation
- **R² = 0.0**: Model no better than guessing average

**Our ETA Model: R² = 0.986**

This means the model explains 98.6% of variation in train arrival times. Only 1.4% is unexplained (due to sensor noise or random factors).

### Mean Absolute Error (MAE)

Average error across all predictions:

```
MAE = (|actual₁ - predicted₁| + |actual₂ - predicted₂| + ... + |actualₙ - predictedₙ|) / n
```

**Our ETA MAE: 0.031 seconds**

On average, predictions are off by only 0.031 seconds (31 milliseconds) - barely noticeable!

### Why Our Model Outperforms Physics

**Physics baseline** (constant speed):
```
ETA = distance / speed = 0.3m / 0.1m/s = 3.0s
```

**Reality**: Train decelerating at 0.05 m/s²
```
Actual ETA = 3.4s  (physics was wrong by 0.4s!)
```

**Our ML Model**: Learned from 2000 examples that trains with this deceleration pattern typically take 13% longer than the simple formula predicts.
```
ML Prediction = 3.38s  (error only 0.02s!)
```

---

## Power Consumption

Total system power: **6.65 Watts**

Calculated using P = V × I:

| Component | Voltage | Current | Power |
|-----------|---------|---------|-------|
| Arduino Uno | 5V | 50mA | 0.25W |
| 3× IR Sensors | 5V | 20mA each | 0.30W |
| 4× LEDs | 5V | 20mA each | 0.40W |
| Buzzer | 5V | 30mA | 0.15W |
| Servo Motor | 5V | 500mA | 2.50W |
| TM1637 Display | 5V | 80mA | 0.40W |
| **Total** | | | **6.65W** |

Can be powered by USB (Arduino) + 4× AA batteries (servo).

---

## Technical Details

### Edge Detection for Sensors

IR sensors output HIGH (no object) or LOW (object detected). To prevent multiple triggers as the train passes over a sensor, we use **edge detection**:

```cpp
bool sensor_prev_state = HIGH;

void loop() {
    int current_state = digitalRead(SENSOR_PIN);
    
    // Trigger only on HIGH→LOW transition (falling edge)
    if (current_state == LOW && sensor_prev_state == HIGH) {
        recordSensorTrigger();  // Only triggers once!
    }
    
    sensor_prev_state = current_state;  // Save for next loop
}
```

This ensures each sensor triggers exactly once per train pass.

### Physics Equations Used

**For constant speed:**
```
time = distance / speed
```

**For changing speed (acceleration ≠ 0):**

Using kinematic equation: d = v₀t + ½at²

Rearranged with quadratic formula:
```
t = (-v + √(v² + 2ad)) / a
```

Where:
- v = current speed (m/s)
- a = acceleration (m/s²)
- d = distance remaining (m)

The model uses these as a fallback when ML predictions are unavailable.

---

## Troubleshooting

**Sensors not triggering:**
- Check connections to pins 2, 3, 4
- Verify 5V and GND connections
- PIR sensors need 30-60 seconds to stabilize after power-on
- Test each sensor individually

**Servo not moving:**
- Ensure external 5V power (4× AA batteries)
- Check signal wire to pin 5
- Verify servo angles in config.h

**Display shows wrong values:**
- Check CLK → pin 11, DIO → pin 12
- Verify TM1637Display library installed
- Display format is MM:SS (minutes:seconds)

**Predictions seem wrong:**
- Ensure sensors are properly spaced (10cm apart)
- Move hand/object at ~8 cm/s (expected demo speed)
- Check Serial Monitor for detailed timing info

---

## Project Results Summary

### ML Model Performance

- **ETA Prediction**: 0.031s MAE, 98.6% R², 44.9% better than physics
- **ETD Prediction**: 0.058s MAE, 99.0% R², 28.1% better than physics
- **Training Dataset**: 2000 samples, mean ETA 6.7s, mean ETD 10.3s

### Traffic Simulation Impact

- **Travel Time**: 49.2% reduction (180s → 91.5s)
- **Queue Length**: 45.2% reduction (60 → 33 vehicles)
- **Fuel Consumption**: 0.5% reduction
- **CO₂ Emissions**: 0.5% reduction

### Design Requirements Met

✅ Reduced air pollution  
✅ Improved response time and accuracy  
✅ Used AI and IoT technologies  
✅ Decreased fuel consumption  
✅ Reduced waiting time  
✅ Enabled smart routing

---

## Future Improvements

1. **Use LiDAR or Radar** instead of IR sensors for longer detection range
2. **Solar-powered operation** for remote installations
3. **Vibration/pressure sensors** on tracks for earlier detection
4. **GPS modules** for precise train tracking
5. **Backup power system** for continuous operation during outages
6. **Mobile app integration** for real-time driver notifications
7. **Cloud-based data collection** for continuous model improvement

---

## Educational Value

This project demonstrates:

**Physics**: Kinematics, velocity, acceleration, motion equations

**Mathematics**: Statistics, regression, error metrics, optimization

**Computer Science**: Machine learning, embedded systems, sensor integration

**Engineering**: System design, hardware-software integration, real-time control

**Environmental Science**: Traffic optimization, emissions reduction, sustainability

---

## References

1. Faheem, H. B., Shorbagy, A. M. E., & Gabr, M. E. (2024). Impact of traffic congestion on transportation system. *Mansoura Engineering Journal*, 49(2), 18.

2. Farooq, B., & Manocha, A. (2025). Core Technologies in AI-based Traffic Systems. In *AI-Based Statistical Modeling for Road Traffic Surveillance*.

3. Ghanem, S., Ferrini, S., & Di Maria, C. (2023). Air pollution and willingness to pay for health risk reductions in Egypt. *World Development*, 172, 106373.

4. Neufville, R., Abdalla, H., & Abbas, A. (2022). Potential of connected fully autonomous vehicles in reducing congestion. *Sustainability*, 14(11), 6910.

5. Park, J., et al. (2025). Connected Traffic Signal Coordination Optimization Framework. *Journal of Transportation Engineering*, 151(2), 04024113.

---

## Acknowledgements

We thank Allah, Mr. Ibrahim Ismail (Capstone supervisor), Mr. Osama Abdo (Capstone teacher), and Eng. Zahraa Selim for their guidance and support.

---

## Contact

**Lana Bassem**: Lana.1323526@stemdakahlia.moe.edu.eg  
**Somaya Selim**: Somaya.1323523@stemdakahlia.moe.edu.eg

**Dakahlia STEM School**  
Grade 12, Semester 1  
Project ID: 13330  
Academic Year: 2025/2026
