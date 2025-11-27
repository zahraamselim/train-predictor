# Level Crossing Notification System

## Project Overview

This project builds an intelligent system that predicts train arrival at level crossings and notifies vehicles at nearby intersections to prevent congestion and safety hazards. The system uses IR sensor readings, machine learning, and traffic simulation to make real-time decisions.

**Core Goal**: Predict train ETA using IR sensors → Notify intersection vehicles at optimal timing → Validate with realistic simulations.

---

## System Architecture

### Phase 1: Data Generation (Simulation)

#### 1.1 Train Data Collection (Open Rails)

- **Purpose**: Generate realistic train approach data
- **Scenarios to simulate**:
  - Different train types (passenger, freight, express)
  - Different speeds (40-120 km/h)
  - Different grades (flat, uphill, downhill)
  - Weather conditions (affects braking)
- **Data collected per scenario**:
  - Train speed at each time step
  - Distance to level crossing
  - Train acceleration/deceleration
  - Time to arrival (ETA)
- **Output format**: CSV with columns `[time, speed, distance_to_crossing, ETA, train_type, grade]`
- **Target**: 100+ diverse scenarios

#### 1.2 IR Sensor Simulation

- **Purpose**: Convert train distance data into realistic IR readings
- **Sensor placement**: 400m, 250m, 100m before crossing
- **Physics model**: IR intensity follows inverse square law
  - `IR_intensity = K / distance²`
  - Add realistic noise (weather, ambient light, sensor drift)
- **Output**: Augment training data with `[IR1_reading, IR2_reading, IR3_reading]` columns

#### 1.3 Traffic Data Collection (SUMO)

- **Purpose**: Model vehicle behavior at intersection
- **Scenarios to simulate**:
  - Different intersection distances (300m, 500m, 1000m from crossing)
  - Different traffic densities (light, medium, heavy)
  - Different vehicle types and reaction times
- **Data collected**:
  - Time for vehicles to traverse from intersection to crossing
  - Queue formation patterns
  - Vehicle clearance times
  - Driver reaction times (typically 2 seconds)
- **Output format**: CSV with columns `[intersection_distance, traffic_density, traversal_time, queue_length]`

---

### Phase 2: Model Development

#### 2.1 Training Data Preparation

- **Combine datasets**: Merge Open Rails + simulated IR + SUMO data
- **Training set**: 80% of scenarios
- **Test set**: 20% held out for validation
- **Target format**: CSV with columns `[IR1, IR2, IR3, ETA, intersection_distance, traffic_density, ...]`

#### 2.2 Model Selection & Training

Train two regression models:

1. **Linear Regression**: `ETA = w0 + w1*IR1 + w2*IR2 + w3*IR3`
2. **Polynomial Regression (degree 2-3)**: Includes squared terms for nonlinearity

#### 2.3 Model Comparison

Compare using:

- **R² score**: How well model fits data (target: >0.95)
- **MAE (Mean Absolute Error)**: Average prediction error in seconds
- **RMSE (Root Mean Square Error)**: Penalizes larger errors
- **Cross-validation**: k-fold (5 or 10 folds) to detect overfitting

Select the winner based on lowest test error.

#### 2.4 Model Export

- Extract weights and save to JSON/text file
- Format for Arduino: simple arrays of numbers
- Example: `weights = [w0, w1, w2, w3]` for linear model

---

### Phase 3: Decision Logic

#### 3.1 Gate Closure Timing

- **Rule**: Gates close 10 seconds before train ETA (based on safety standards)
- **Formula**: `gate_closure_time = ETA - 10`

#### 3.2 Vehicle Notification Timing

- **Rule**: Notify vehicles early enough so they can clear before gates close
- **Formula**:
  ```
  notification_time = gate_closure_time - (intersection_distance / avg_vehicle_speed) - reaction_buffer
  notification_time = (ETA - 10) - (intersection_distance / 15 m/s) - 2
  ```
- **Components**:
  - `ETA - 10`: Gate closure time
  - `intersection_distance / 15`: Time for vehicle to reach crossing (assuming 54 km/h average)
  - `2 seconds`: Safety reaction buffer

#### 3.3 Decision Rules

- If `current_time >= notification_time`: Send alert to intersection
- If `current_time >= gate_closure_time`: Close gates
- If `current_time >= ETA`: Train is at crossing (emergency stop if needed)

---

### Phase 4: System Deployment

#### 4.1 Arduino Uno R3 Hardware

- **Inputs**: 3 IR analog sensors (A0, A1, A2)
- **Outputs**: Gate control signal, notification signal
- **Model**: Polynomial regression (weights stored in EEPROM)
- **Operation**:
  1. Read 3 IR sensors
  2. Apply trained model: `ETA = model(IR1, IR2, IR3)`
  3. Compare with decision rules
  4. Output gate/notification signals
  5. No WiFi needed (local computation only)

#### 4.2 Communication

- Serial communication (USB) for testing/logging
- CAN bus (optional upgrade) for real-world deployment

---

### Phase 5: Validation & Visualization

#### 5.1 Log Replay System

- Run Open Rails + SUMO independently to generate complete logs
- Save logs to CSV files with timestamps
- Python bridge replays logs and simulates your system's decisions

#### 5.2 Pygame Visualization

- **Display elements**:
  - Top-down level crossing view
  - Train approaching on tracks (position, speed, direction)
  - Vehicles at intersection (positions, queue status)
  - IR sensor zones (visual circles at 400m, 250m, 100m)
  - Gate status (open/closed animation)
  - Notification events (visual alerts when triggered)
  - ETA counter (real-time countdown)
  - Sensor readings (display IR1, IR2, IR3 values)
  - Model prediction (show predicted vs actual ETA)
  - Timeline/metrics panel (show decision events)

#### 5.3 Validation Metrics

- **Safety**: Did gates close before train arrived?
- **Efficiency**: Did vehicles actually clear before gates closed?
- **Accuracy**: What was model prediction error on test scenarios?
- **Edge cases**: What happens with sudden speed changes, malfunctions?

---

## Project Workflow

```
1. GENERATE DATA
   ├─ Run Open Rails (100+ scenarios)
   ├─ Simulate IR sensors on train data
   ├─ Run SUMO (traffic scenarios)
   └─ Output: training_data.csv

2. TRAIN MODEL
   ├─ Load training_data.csv
   ├─ Train linear regression
   ├─ Train polynomial regression
   ├─ Compare models
   └─ Output: best_model_weights.json

3. IMPLEMENT DECISION LOGIC
   ├─ Gate closure timing rule
   ├─ Vehicle notification rule
   └─ Output: decision_logic.py

4. DEPLOY TO ARDUINO
   ├─ Convert model weights to C code
   ├─ Implement inference + decision logic
   ├─ Upload sketch
   └─ Output: sketch.ino

5. VALIDATE & VISUALIZE
   ├─ Replay simulation logs
   ├─ Run system decisions on logs
   ├─ Render in Pygame
   └─ Output: validation metrics + visualization
```

---

## Key Parameters (Tunable)

| Parameter                  | Default Value    | Notes                       |
| -------------------------- | ---------------- | --------------------------- |
| Gate closure before ETA    | 10 seconds       | Check local regulations     |
| Sensor distance 1          | 400m             | Furthest detection          |
| Sensor distance 2          | 250m             | Medium detection            |
| Sensor distance 3          | 100m             | Close detection             |
| Average vehicle speed      | 15 m/s (54 km/h) | Adjust per region           |
| Reaction buffer            | 2 seconds        | Safety margin               |
| IR inverse square constant | TBD              | Calibrate from real sensors |
| Polynomial degree          | 2 or 3           | Test both                   |
| Model R² threshold         | 0.95             | Minimum acceptable accuracy |

---

## Success Criteria

1. ✓ Training data from realistic simulations (100+ scenarios)
2. ✓ Model achieves R² > 0.95 on test set
3. ✓ Model weights fit in Arduino (< 100 bytes)
4. ✓ Arduino inference runs in < 10ms
5. ✓ Visualization shows all key system states
6. ✓ No vehicles cross during gate closure period
7. ✓ ETA predictions accurate within ±2 seconds

---

## Technologies Used

- **Open Rails**: Train physics simulation
- **SUMO**: Traffic flow simulation
- **Python**: Data processing, model training (scikit-learn)
- **Pygame**: Visualization
- **Arduino IDE**: Embedded system code
- **scikit-learn**: Linear/polynomial regression

---

## Next Steps

1. Set up Open Rails and generate train scenarios
2. Implement IR sensor simulation
3. Set up SUMO and generate traffic scenarios
4. Merge datasets and train models
5. Compare models and select best
6. Export weights and create Arduino sketch
7. Build Python bridge for log replay
8. Implement Pygame visualization
9. Run full validation on test scenarios

Good question. Let me think through time factors systematically:

**Time factors that DON'T affect train physics:**

1. **Time of day**: Train physics (mass, engine power, air resistance) don't change between morning and night
2. **Day of week**: Same - the train behaves identically on Monday vs Sunday

**However, time factors that COULD matter for your system:**

1. **Traffic patterns at intersection** (affects your SUMO simulation, not train data):

   - Rush hour: More vehicles queuing at intersection
   - Weekend: Different traffic density
   - This impacts "how long vehicles need to clear" but not "when train arrives"

2. **Visibility for IR sensors**:

   - Daytime: Strong ambient IR from sunlight
   - Nighttime: Less IR noise
   - This affects sensor readings, not train motion

3. **Operational scheduling** (indirectly):
   - Freight trains often run at night (less passenger traffic)
   - Express trains during day (commuter schedules)
   - But this just biases which train types appear when, not how they move

**My recommendation:**

For the **train physics data** we're generating now: **No, don't add time factors.**

Reasons:

- Physics is time-invariant (F=ma works the same at 3 AM and 3 PM)
- Adds unnecessary complexity
- Your ML model predicts ETA from IR sensors, not from time of day

**Where time DOES matter:**

1. **IR sensor simulation** (next step): Add time-of-day effects

   - Solar IR interference during day
   - Temperature affects sensor baseline

2. **Traffic simulation** (SUMO): Add temporal patterns

   - Rush hour density
   - Weekend patterns
   - This determines notification urgency

3. **Operational context** (optional metadata):
   - Track "train_type + time_of_day" correlation
   - Example: freight trains more likely at night
   - Use this to make scenario generation more realistic

Should we keep train physics time-independent and add temporal effects later in the IR/traffic stages? Or do you see a specific reason time would affect train dynamics?
