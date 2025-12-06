# Hardware Implementation: Arduino Railroad Crossing

Physical demonstration of the intelligent crossing control system using Arduino Uno.

## Overview

This hardware implementation demonstrates real-time train detection, ML-based prediction, and automated crossing control. The system uses compressed decision tree models that fit within Arduino Uno's 32KB flash memory.

## Components

**Required Hardware**:

- Arduino Uno (or compatible)
- 3x PIR motion sensors (train detection)
- 1x Servo motor SG90 (gate control)
- 4x LEDs (2 red, 2 green)
- 1x Active buzzer (5V)
- 1x TM1637 4-digit 7-segment display
- 5x 220Ω resistors (LED current limiting)
- 1x 100Ω resistor (buzzer current limiting)
- Breadboard and jumper wires

**Pin Connections**:

```
Sensors:
  Sensor 0 (farthest) → Pin 2
  Sensor 1 (middle)   → Pin 3
  Sensor 2 (closest)  → Pin 4

Gate Control:
  Servo PWM           → Pin 5

Crossing Signals:
  Green LED           → Pin 6
  Red LED             → Pin 7

Intersection Signals:
  Green LED           → Pin 8
  Red LED             → Pin 9

Alerts:
  Buzzer              → Pin 10
  TM1637 CLK          → Pin 11
  TM1637 DIO          → Pin 12
```

## System Operation

**State Machine**:

1. IDLE: System ready, gates open, all green
2. TRAIN_DETECTED: Sensor triggered, collecting data
3. INTERSECTION_NOTIFIED: Upstream signal red, buzzer on
4. GATES_CLOSED: Crossing closed, countdown active
5. GATES_OPENING: Train cleared, reopening

**Detection Sequence**:

1. Train passes Sensor 0 (20cm from crossing)
2. Train passes Sensor 1 (15cm from crossing)
3. Train passes Sensor 2 (10cm from crossing)
4. System calculates speed and acceleration
5. ML models predict ETA and ETD

**Control Timeline**:

```
T-3.0s: Intersection notified (red light, buzzer)
T-2.0s: Gates close
T+0.0s: Train arrives at crossing
T+X.Xs: Train rear clears crossing
T+1.0s: Gates open, system reset
```

## Machine Learning Models

**Compressed Decision Trees**:

- 50 trees maximum (Arduino flash constraint)
- Integer-only arithmetic (no floating-point)
- Fixed-point scaling (multiply by 1000)
- Depth limited to 5 levels

**Features Used** (8 for ETA, 10 for ETD):

```
distance_remaining    - Distance from last sensor
train_length          - Train length (fixed 10cm)
last_speed            - Speed at sensor 2
speed_change          - Acceleration trend
time_01, time_12      - Transit times
avg_speed_01/12       - Average speeds
accel_trend           - Recent acceleration (ETD only)
predicted_speed       - Extrapolated speed (ETD only)
```

**Performance**:

- ETA accuracy: 0.3-0.4 seconds
- ETD accuracy: 0.4-0.5 seconds
- Prediction time: <50ms on Arduino

## Configuration

**Physical Scale**:

- Sensor spacing: 5cm between sensors
- Crossing distance: 20cm from sensor 0
- Train length: 10cm (adjustable)
- Speed range: 5-30 cm/s

**Timing Thresholds**:

```c
#define CLOSURE_THRESHOLD 2.0f       // Close gates 2s before arrival
#define OPENING_THRESHOLD 1.0f       // Open gates 1s after departure
#define NOTIFICATION_THRESHOLD 3.0f  // Alert intersection 3s before
```

**Sensor Positions**:

```c
#define SENSOR_0_POS 20.0f  // 20cm from crossing (farthest)
#define SENSOR_1_POS 15.0f  // 15cm from crossing (middle)
#define SENSOR_2_POS 10.0f  // 10cm from crossing (closest)
```

## Code Structure

**Main Files**:

- `sketch.ino` - Main control logic
- `train_models.h` - Compressed ML models
- `thresholds_config.h` - Timing parameters
- `scale_config.h` - Physical dimensions

**Key Functions**:

```c
checkSensors()          - Monitor PIR sensors
calculatePredictions()  - Run ML models
notifyIntersections()   - Alert upstream traffic
closeGates()           - Lower crossing gates
openGates()            - Raise crossing gates
updateCountdown()      - Display time remaining
updateBuzzer()         - Control warning sound
```

## Generating Model Headers

**Export from trained models**:

```bash
# Train ML models first
make ml-pipeline

# Export compressed models for Arduino
python -m hardware.exporters.model
```

**Output files**:

- `hardware/eta_model.h` - ETA prediction model
- `hardware/etd_model.h` - ETD prediction model
- `hardware/thresholds.h` - Timing configuration

**Model format**:

```c
// Example tree structure
const int8_t eta_tree_0_features[] = {2, 7, -1, -1};
const int16_t eta_tree_0_thresholds[] = {15000, 12000, 0, 0};
const int8_t eta_tree_0_children_left[] = {1, 2, -1, -1};
const int8_t eta_tree_0_children_right[] = {3, 4, -1, -1};
const int16_t eta_tree_0_values[] = {0, 0, 2500, 1800};
```

## Testing

**Wokwi Simulator**:

1. Open `diagram.json` in Wokwi
2. Upload `sketch.ino`
3. Run simulation
4. Trigger sensors sequentially to simulate train

**Physical Setup**:

1. Wire components per diagram
2. Upload sketch to Arduino
3. Open Serial Monitor (9600 baud)
4. Pass object past sensors to test

**Expected Output**:

```
[00:00] Demonstration Level Crossing System
[00:00] Scale: 5cm between sensors, 20cm to crossing
[00:00] Ready - waiting for train detection
[00:05] Sensor 0 triggered (20cm from crossing)
[00:06] Sensor 1 triggered (15cm from crossing)
[00:07] Sensor 2 triggered (10cm from crossing)
[00:07] Train parameters calculated:
[00:07]   Speed: 10.00 cm/s
[00:07]   Acceleration: 0.00 cm/s²
[00:07]   ETA: 2.1s
[00:07]   ETD: 3.2s
[00:10] INTERSECTION NOTIFIED - Buzzer activated
[00:10]   Time to gate closure: 0.1s
[00:10] GATES CLOSED
[00:10]   Wait time: 4.2s
[00:14] GATES OPEN - System ready
[00:14] System reset - Ready for next train
```

## Limitations

**Hardware Constraints**:

- Arduino Uno: 32KB flash, 2KB RAM
- No floating-point hardware
- Model compression required
- Integer math only

**Timing Accuracy**:

- PIR sensor latency: ~100ms
- Servo response time: ~200ms
- Prediction overhead: ~50ms
- Total system latency: ~350ms

**Physical Constraints**:

- PIR detection range: 3-7 meters
- Requires moving heat source (person, warm object)
- Indoor use only (PIR affected by sunlight)
- Small scale demonstration only

## Scaling to Real System

**Full-Scale Implementation**:

- Replace PIR with magnetic/inductive sensors
- Use industrial servo or barrier motor
- Add redundant sensors for safety
- Implement fail-safe mechanisms
- Scale distances proportionally (50:1 ratio)

**Example Scaling**:

```
Demo:    Real System:
10cm  →  5m train length
20cm  →  10m to crossing
5cm   →  2.5m between sensors
10cm/s → 5m/s (18 km/h)
```

## Safety Notes

**Important**:

- This is a demonstration system only
- Not certified for actual railroad use
- No safety guarantees provided
- PIR sensors not suitable for critical applications
- Always include fail-safe mechanisms in real systems

## Troubleshooting

**Sensors not triggering**:

- Check PIR sensor power (5V)
- Verify sensor sensitivity adjustment
- Test with warm object (hand)
- Check sensor orientation

**Incorrect predictions**:

- Verify sensor spacing (exactly 5cm)
- Check timing calculation (millis() overflow)
- Ensure train moves at constant speed
- Regenerate models if scale changed

**Servo not moving**:

- Check servo power (5V)
- Verify PWM connection (pin 5)
- Test servo separately
- Check for physical obstruction

**Display not working**:

- Verify TM1637 connections
- Check CLK/DIO pins (11, 12)
- Test display brightness setting
- Ensure common ground

## References

**Libraries Used**:

- Servo.h (built-in Arduino library)
- TM1637Display.h (open source)

**Model Training**:

- scikit-learn GradientBoostingRegressor
- Custom compression for embedded systems
- See `ml/` directory for training code

## License

MIT License - Educational and research use
