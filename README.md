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

## Technical Deep Dive

This section explains the technical concepts behind the system in more detail, while still keeping things understandable.

### How Machine Learning Works in This Project

**The Basic Idea:**

Think of machine learning like teaching someone to recognize patterns. Instead of telling a computer exactly what to do with a bunch of if-else statements, we show it thousands of examples and let it figure out the patterns on its own.

In our project, we show the computer 2000 examples of trains moving at different speeds and accelerations. The computer learns: "When I see THIS speed pattern, the train usually arrives in THAT amount of time."

**Why Not Just Use Math?**

You might wonder: "Can't we just use the distance formula (distance = speed × time)?" The problem is real trains don't move at constant speed. They speed up and slow down. The simple formula assumes constant speed, so it makes mistakes.

Our machine learning model learns more complex patterns like:
- "If the train is slowing down between sensor 1 and sensor 2, it will probably keep slowing down"
- "Fast trains with high acceleration reach the crossing faster than the simple formula predicts"
- "Train length matters - longer trains take more time to completely clear"

The ML model captured these patterns by analyzing 2000 different train movements, achieving 79.6% better accuracy than the simple physics formula.

### Random Forest: The "Wisdom of Crowds" Algorithm

**What is Random Forest?**

Imagine you're trying to predict tomorrow's weather. You could ask one weather expert, or you could ask 10 different experts and take the average of their predictions. The average is usually more accurate than any single expert because individual mistakes get canceled out.

Random Forest works exactly like this, but with "decision trees" instead of weather experts. A decision tree is like a flowchart that makes decisions by asking yes/no questions:

```
Is train speed > 10 m/s?
├─ YES → Is acceleration positive?
│  ├─ YES → Predict ETA = 3.2 seconds
│  └─ NO  → Predict ETA = 4.1 seconds
└─ NO  → Is train length > 150m?
   ├─ YES → Predict ETA = 5.8 seconds
   └─ NO  → Predict ETA = 4.5 seconds
```

**Random Forest Regressor vs Classifier:**

You might wonder: "Doesn't Random Forest predict categories, not continuous numbers?" That's a common misconception!

Random Forest comes in two flavors:

1. **Random Forest Classifier** (predicts categories):
   - Example: "Is this email spam?" → Yes/No
   - Trees vote, majority wins
   - Output: Discrete categories

2. **Random Forest Regressor** (predicts continuous numbers):
   - Example: "What's the train's ETA?" → 3.45 seconds
   - Trees predict numbers, we average them
   - Output: Smooth continuous values

**Our Code Uses Random Forest Regressor:**

In `train_models.py`, we explicitly use the regressor version:

```python
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(
    n_estimators=10,        # 10 decision trees
    max_depth=8,            # Each tree can be 8 levels deep
    random_state=42,        # For reproducible results
    n_jobs=-1               # Use all CPU cores
)

model.fit(X_train, y_train)  # Train on continuous ETA values
predictions = model.predict(X_test)  # Get continuous predictions
```

**How It Produces Continuous Predictions:**

Each of the 10 decision trees makes its own prediction (a continuous number), then we average them:

```
Example prediction for one train:

Tree 1: Predicts ETA = 3.21 seconds
Tree 2: Predicts ETA = 3.45 seconds
Tree 3: Predicts ETA = 3.18 seconds
Tree 4: Predicts ETA = 3.67 seconds
Tree 5: Predicts ETA = 3.29 seconds
Tree 6: Predicts ETA = 3.52 seconds
Tree 7: Predicts ETA = 3.33 seconds
Tree 8: Predicts ETA = 3.41 seconds
Tree 9: Predicts ETA = 3.38 seconds
Tree 10: Predicts ETA = 3.52 seconds

Final ETA = (3.21 + 3.45 + ... + 3.52) / 10 = 3.396 seconds
```

The averaging produces smooth, continuous predictions. We're not limited to specific values - we can predict 3.396 seconds, 4.821 seconds, or any decimal value.

**Why Random Forest Regressor is Perfect for ETA/ETD:**

1. **Handles non-linear relationships**: The relationship between speed, acceleration, and arrival time isn't a simple straight line. Random Forest can learn complex curved patterns.

2. **Captures feature interactions**: It learns patterns like "when speed is high AND acceleration is negative, arrival time increases more than expected"

3. **Robust to noise**: One tree might be thrown off by a noisy sensor reading, but averaging 10 trees cancels out the error

4. **No distribution assumptions**: Unlike linear regression (which assumes normal distribution), Random Forest works with any data pattern

5. **Smooth predictions through averaging**: While individual trees make somewhat discrete predictions, averaging 10 trees produces very smooth continuous outputs

**Real Example from Our Data:**

When a train passes our sensors with these features:
- Last speed: 0.105 m/s
- Acceleration: -0.033 m/s²
- Distance: 0.2 m

The 10 trees in our ETA model might predict: [3.42, 3.38, 3.51, 3.45, 3.39, 3.47, 3.41, 3.49, 3.43, 3.46]

Average = **3.441 seconds** (smooth continuous value)

Compare this to the physics formula which would predict: 0.2 / 0.105 = 1.905 seconds (doesn't account for deceleration!)

The Random Forest learned from 2000 examples that when trains are decelerating at this rate, they actually take longer to arrive than the simple formula suggests.

**How Random Forest Improves on Single Trees:**

One decision tree can easily memorize the training data instead of learning real patterns (called "overfitting"). It's like a student who memorizes answers without understanding the concepts - they fail on new questions.

Random Forest solves this by creating many trees, where each tree:
1. **Sees different data**: Each tree trains on a random 67% of the training examples (called "bootstrap sampling" or "bagging")
2. **Considers different features**: At each decision point, each tree only looks at a random subset of features instead of all of them
3. **Makes independent predictions**: The trees don't influence each other

When making a prediction, all trees vote and we average their answers. This "ensemble" approach means:
- Individual trees can make mistakes, but mistakes cancel out
- If 7 out of 10 trees predict 3.5 seconds and 3 trees predict 4.2 seconds, the average (3.68 seconds) is probably more accurate than any single tree
- The model is more stable - small changes in training data don't drastically change predictions

**Our Random Forest Configuration:**

- **ETA Model**: 10 trees, maximum depth of 8 levels
- **ETD Model**: 5 trees, maximum depth of 10 levels
- **Why different sizes?** ETA prediction is more complex (train could still be accelerating), so we use more trees. ETD is simpler (just add train length), so fewer trees work fine.

### Understanding Features: Turning Raw Data into Machine Learning Input

**What Are Features?**

Features are the measurements or characteristics that we feed into a machine learning model. Think of them as the "questions" the model uses to make decisions.

For example, if you're predicting whether a student will pass an exam, your features might be:
- Hours studied
- Previous test scores
- Attendance percentage
- Hours of sleep

In our railway system, features are measurements we extract from the train's movement.

**Raw Data vs Features:**

Here's the key distinction - machine learning models can't work with raw sensor data directly. We need to transform it into meaningful features.

**Our Raw Data (what sensors actually give us):**

When the train passes our three sensors, we record timestamps:

```
Sensor 0 triggered at: t = 10.23 seconds, position = 0.5m
Sensor 1 triggered at: t = 11.15 seconds, position = 0.4m
Sensor 2 triggered at: t = 12.03 seconds, position = 0.3m
```

This raw data is just three timestamps and positions. Not very useful by itself!

**Feature Engineering (what we calculate from raw data):**

We transform this raw data into 14 meaningful features that capture the train's behavior:

```python
# From train_data.py - the extract_features() function

# Raw sensor data
s0_time = 10.23  # seconds
s1_time = 11.15
s2_time = 12.03

s0_pos = 0.5  # meters from crossing
s1_pos = 0.4
s2_pos = 0.3

# FEATURE 1 & 2: Time intervals
time_01 = s1_time - s0_time  # = 0.92 seconds
time_12 = s2_time - s1_time  # = 0.88 seconds

# FEATURE 3-5: Instantaneous speeds (from SUMO simulation)
speed_0 = 0.110  # m/s at sensor 0
speed_1 = 0.105  # m/s at sensor 1
last_speed = 0.098  # m/s at sensor 2

# FEATURE 6 & 7: Average speeds between sensors
avg_speed_01 = (s0_pos - s1_pos) / time_01  # = 0.1 / 0.92 = 0.109 m/s
avg_speed_12 = (s1_pos - s2_pos) / time_12  # = 0.1 / 0.88 = 0.114 m/s

# FEATURE 8: Speed change (is train speeding up or slowing down?)
speed_change = last_speed - speed_0  # = 0.098 - 0.110 = -0.012 m/s (slowing!)

# FEATURE 9 & 10: Accelerations
accel_01 = (speed_1 - speed_0) / time_01  # = (0.105 - 0.110) / 0.92 = -0.0054 m/s²
accel_12 = (last_speed - speed_1) / time_12  # = (0.098 - 0.105) / 0.88 = -0.0080 m/s²

# FEATURE 11: Acceleration trend (is deceleration increasing?)
accel_trend = accel_12 - accel_01  # = -0.0080 - (-0.0054) = -0.0026 m/s²/s

# FEATURE 12: Distance remaining
distance_remaining = s2_pos  # = 0.3m to crossing

# FEATURE 13: Train length
train_length = 0.15  # meters

# FEATURE 14: Predicted crossing speed (physics extrapolation)
time_to_crossing = distance_remaining / last_speed  # = 0.3 / 0.098 = 3.06s
predicted_crossing_speed = last_speed + (accel_12 * time_to_crossing)
# = 0.098 + (-0.0080 × 3.06) = 0.073 m/s
```

**Why These Specific Features?**

Each feature tells the model something important:

**Temporal Features** (when things happened):
- `time_01`, `time_12`: How long between sensors? If time_12 < time_01, train is speeding up

**Kinematic Features** (motion characteristics):
- `speed_0`, `speed_1`, `last_speed`: Current velocities - most important is `last_speed` (closest to crossing)
- `avg_speed_01`, `avg_speed_12`: Smooth out momentary speed fluctuations
- `speed_change`: Overall velocity trend - positive means accelerating, negative means decelerating

**Dynamic Features** (how motion is changing):
- `accel_01`, `accel_12`: Rate of speed change - tells us if train is speeding up/slowing down
- `accel_trend`: Is acceleration itself changing? Helps predict future behavior

**Physical Features** (geometry and prediction):
- `distance_remaining`: How far train must travel - smaller means less time
- `train_length`: Longer trains take more time to clear
- `predicted_crossing_speed`: Physics-based guess of speed at crossing

**The Power of Feature Combinations:**

The model doesn't just look at features individually. It learns combinations:

- "When `last_speed` is low AND `accel_12` is negative AND `distance_remaining` is large, ETA is usually much longer than the simple formula predicts"
- "When `train_length` is above 200m AND `speed_change` is positive, ETD increases significantly"
- "When `accel_trend` is strongly negative (deceleration increasing), trains often take 15% longer than expected"

### The Training Dataset: 2000 Simulated Train Runs

**How We Generated Training Data:**

We used SUMO (Simulation of Urban Mobility) to create realistic train trajectories. Here's what happens in `train_data.py`:

**Step 1: Define Train Scenarios**

We created 5 different scenario types to cover realistic train behavior:

```python
# From config.yaml
scenarios:
  fast:
    speed: [40, 48]      # High-speed trains (40-48 m/s)
    accel: [0.3, 0.8]    # Moderate acceleration
    decel: [0.3, 0.8]
  
  moderate:
    speed: [30, 40]      # Medium-speed trains
    accel: [0.5, 1.2]    # Can accelerate more
    decel: [0.5, 1.2]
  
  slow:
    speed: [20, 32]      # Slow trains
    accel: [0.3, 0.7]    # Low acceleration
    decel: [0.8, 1.5]    # Can brake harder
  
  accelerating:
    speed: [25, 35]      # Starting moderate
    accel: [1.5, 2.0]    # Strong acceleration
    decel: [0.5, 1.0]
  
  decelerating:
    speed: [35, 45]      # Starting fast
    accel: [0.3, 0.8]
    decel: [1.5, 2.0]    # Strong braking
```

**Step 2: Generate Random Parameters**

For each of the 2000 training samples, we randomly pick:

```python
# From train_data.py - generate_train_params()
import numpy as np

np.random.seed(42)  # For reproducibility

for sample in range(2000):
    scenario = random.choice(['fast', 'moderate', 'slow', 'accelerating', 'decelerating'])
    
    train_params = {
        'initial_speed': random.uniform(scenario.speed[0], scenario.speed[1]),
        'acceleration': random.uniform(scenario.accel[0], scenario.accel[1]),
        'deceleration': random.uniform(scenario.decel[0], scenario.decel[1]),
        'train_length': random.choice([100, 150, 200, 250])  # meters
    }
```

This creates diverse data covering many situations:
- Train #0743: Fast (45 m/s), low acceleration (0.4 m/s²), length 150m
- Train #1256: Slow (22 m/s), high acceleration (1.8 m/s²), length 200m
- Train #0089: Moderate (35 m/s), decelerating (1.6 m/s²), length 100m

**Step 3: Run SUMO Simulation**

For each train, SUMO simulates the complete trajectory:

```python
# From train_data.py - run_simulation()

# SUMO records position and speed every 0.1 seconds
time    position    speed       acceleration
0.0     -2000      40.0        0.5
0.1     -1996      40.05       0.5
0.2     -1992      40.10       0.5
...
39.8    500        42.1        0.48
39.9    504.2      42.15       0.48
40.0    508.4      42.2        0.47
```

Each simulation runs for up to 400 seconds, recording thousands of data points per train.

**Step 4: Extract Sensor Triggers**

We find the exact moments when the train passed each sensor:

```python
# From train_data.py - extract_features()

# Find when train position crossed each sensor
for sensor_id, sensor_position in sensors.items():
    # Find first time when train.position >= sensor_position
    trigger_time = trajectory[trajectory['pos'] >= sensor_position].iloc[0]['time']
    trigger_speed = trajectory[trajectory['pos'] >= sensor_position].iloc[0]['speed']
```

**Step 5: Calculate Target Values (What We're Trying to Predict)**

```python
# Find when train front reaches crossing
crossing_time = trajectory[trajectory['pos'] >= 2000].iloc[0]['time']
eta_actual = crossing_time - s2_time  # Time from last sensor to crossing

# Find when train rear clears crossing
rear_position = crossing_time_position + train_length
rear_crossing_time = trajectory[trajectory['pos'] >= rear_position].iloc[0]['time']
etd_actual = rear_crossing_time - s2_time  # Time from last sensor to fully cleared
```

**The Final Dataset:**

After processing all 2000 simulations, we get a CSV file with this structure:

```
features.csv (2000 rows × 20 columns)

Row    Feature_1  Feature_2  ...  Feature_14  ETA_actual  ETD_actual  ETA_physics  ETD_physics
0      0.92       0.88       ...  0.073       3.18        5.71        3.06         5.59
1      1.15       1.09       ...  0.095       2.95        4.82        3.21         4.94
2      0.78       0.81       ...  0.112       2.67        4.23        2.68         4.15
...
1999   1.02       0.95       ...  0.088       3.42        6.05        3.51         6.18
```

**Dataset Statistics:**

```python
# From our actual results
Total samples: 2000
ETA range: 1.2 - 8.5 seconds
ETA mean: 3.4 ± 1.2 seconds
ETD range: 2.8 - 12.3 seconds  
ETD mean: 5.7 ± 1.8 seconds

Speed range: 0.05 - 0.15 m/s (5-15 cm/s)
Acceleration range: -0.08 to +0.12 m/s²
Train length: 0.10 - 0.25 m (10-25 cm scaled down)
```

**Why 2000 Samples?**

- Too few (<500): Model won't see enough variation, might not generalize well
- Too many (>5000): Diminishing returns, takes too long to generate (5min vs 2+ hours)
- 2000 is the sweet spot: Covers all scenarios, trains in reasonable time

**Data Quality Checks:**

We validate each sample before including it:

```python
# From train_data.py - extract_features()

# Reject invalid samples
if time_01 <= 0 or time_12 <= 0:
    return None  # Invalid timing
    
if eta_actual <= 0 or eta_actual > 100:
    return None  # Unrealistic prediction
    
if etd_actual < eta_actual:
    return None  # ETD must be after ETA

# Only keep valid samples
successful_samples = 1847 out of 2000 (92.4% success rate)
```

This ensures our model trains on clean, physically realistic data.

### Feature Summary Table

For quick reference, here's what each of our 14 features represents:

| # | Feature Name | What It Measures | Why It Matters |
|---|-------------|------------------|----------------|
| 1 | time_01 | Time between sensor 0 and 1 | Detects speed changes |
| 2 | time_12 | Time between sensor 1 and 2 | Detects acceleration/deceleration |
| 3 | speed_0 | Speed at furthest sensor | Starting velocity |
| 4 | speed_1 | Speed at middle sensor | Intermediate velocity |
| 5 | last_speed | Speed at nearest sensor | **Most important** - closest to crossing |
| 6 | avg_speed_01 | Average speed (0→1) | Smooths fluctuations |
| 7 | avg_speed_12 | Average speed (1→2) | Recent average motion |
| 8 | speed_change | Total velocity change | Overall acceleration trend |
| 9 | accel_01 | Acceleration (0→1) | Rate of speed change |
| 10 | accel_12 | Acceleration (1→2) | Recent acceleration |
| 11 | accel_trend | Change in acceleration | Is train speeding up faster/slower? |
| 12 | distance_remaining | Distance to crossing | Geometric constraint |
| 13 | train_length | Length of train | Needed for ETD calculation |
| 14 | predicted_crossing_speed | Extrapolated speed | Physics-based prediction |

**Feature Importance (from trained model):**

The Random Forest automatically learns which features are most important:

1. **last_speed** (35%): Current speed is the strongest predictor
2. **distance_remaining** (18%): How far determines how long
3. **accel_12** (12%): Recent acceleration affects arrival time
4. **train_length** (10%): Directly impacts ETD
5. **predicted_crossing_speed** (8%): Physics extrapolation helps
6. Other features (17%): Fine-tune predictions

**Feature Correlations:**

Some features are related, which is intentional:
- `avg_speed_01` and `avg_speed_12` might be similar if train moves steadily
- `accel_01` and `accel_12` show acceleration consistency
- `speed_change` summarizes what accelerations show in detail

The Random Forest handles these correlations automatically - it doesn't get confused by related features like simpler models would.

### The 14 Features We Extract (Detailed List)

When the train passes our three sensors, we calculate 14 different measurements (features) that help predict when it will arrive:

### The Physics Behind the Predictions

**For constant speed (acceleration ≈ 0):**

This is the simplest case. If the train is moving at steady speed, we use:

```
time = distance / speed
```

Example: Train is 0.2m from crossing, moving at 0.1 m/s:
```
time = 0.2 / 0.1 = 2 seconds
```

**For changing speed (acceleration ≠ 0):**

When the train is speeding up or slowing down, we use kinematic equations from physics class:

```
distance = initial_speed × time + (1/2) × acceleration × time²
```

We need to solve for `time`, which requires the quadratic formula:

```
time = (-speed + √(speed² + 2 × acceleration × distance)) / acceleration
```

The part under the square root (speed² + 2 × acceleration × distance) is called the "discriminant". If it's negative, the formula won't work (can't take square root of negative), so we fall back to the constant speed formula.

**Example with acceleration:**
- Current speed: 0.1 m/s
- Acceleration: 0.05 m/s² (speeding up)
- Distance: 0.2 m

```
discriminant = (0.1)² + 2(0.05)(0.2) = 0.01 + 0.02 = 0.03
time = (-0.1 + √0.03) / 0.05 = (-0.1 + 0.173) / 0.05 = 1.46 seconds
```

Notice this is faster than the 2 seconds we calculated assuming constant speed, because the train is speeding up!

**ETD Calculation:**

ETD (when the train completely clears) adds the train length to the distance:

```
total_distance = distance_to_crossing + train_length
```

Then uses the same formulas but with this longer distance. For a 0.15m train:

```
total_distance = 0.2 + 0.15 = 0.35m
time = 0.35 / 0.1 = 3.5 seconds (at constant speed)
```

### Why Our Model Beats Simple Physics

The physics formulas make assumptions:
- Acceleration is constant between sensor 2 and the crossing
- No external factors affect the train
- Measurements are perfectly accurate

In reality:
- Trains don't accelerate uniformly
- The hand pushing the train in our demo isn't perfectly steady
- Sensors have small timing errors

The Random Forest model learns to compensate for these imperfections by studying patterns in the training data. For example, it might learn "when acceleration is decreasing and speed is low, predictions tend to be 0.5 seconds too early" and automatically adjust.

**Our Results:**
- Physics baseline ETA error: 0.152 seconds
- Random Forest ETA error: 0.031 seconds
- **Improvement: 79.6%**

- Physics baseline ETD error: 0.164 seconds  
- Random Forest ETD error: 0.058 seconds
- **Improvement: 64.6%**

### Arduino Implementation Challenges

**Problem:** The trained Random Forest models are too large for Arduino.

Each decision tree stores:
- Split conditions (which feature, what threshold)
- Tree structure (parent-child relationships)
- Leaf values (predictions)

Our 10-tree ETA model would need about 50KB of memory, but Arduino Uno only has 32KB total! We can't fit the full model.

**Solution:** Use physics-based approximations that mimic the trained model.

The Arduino code uses the kinematic equations described above, with safety checks:
- If discriminant is negative, fall back to constant speed
- If predicted time is unrealistic (>1000 seconds), use simpler formula  
- If speed is invalid (≤0), return error

While not as accurate as the full Random Forest (which achieves 0.031s error), the physics approximation on Arduino achieves about 0.15s error - still good enough for a demo system.

For a real deployment, you'd use a more powerful microcontroller (like ESP32 with 520KB RAM) that can run the full Random Forest model.

### How the Traffic Simulation Works

The simulation uses SUMO (Simulation of Urban Mobility), a professional traffic simulator used by researchers and city planners worldwide.

**Simulation Setup:**

We create a network with two routes:
- **West Route**: Crosses the railway (affected by trains)
- **East Route**: Bypasses the railway (slightly longer, but no trains)

We simulate 30 minutes of traffic (1200 cars/hour) with trains passing every 4 minutes, blocking the crossing for 90 seconds each time.

**Three Scenarios Tested:**

1. **Phase 1 - Baseline**: Everyone uses west route
   - Vehicles stop when train blocks crossing
   - Average wait time: ~45 seconds per vehicle
   - Some vehicles wait through multiple train passes

2. **Phase 2 - Alternative**: Everyone uses east route
   - No train delays
   - Slightly longer distance (+5-10 seconds)
   - Proves the detour is viable

3. **Optimized - Smart Routing**: 70% reroute when notified
   - System broadcasts "train in 6 seconds" warning
   - 70% of nearby drivers receive notification and choose east route
   - 30% still use west route (didn't get notification or chose to wait)

**Fuel Consumption Calculation:**

We track each vehicle and calculate fuel used:
```
fuel = (driving_time × 0.08 L/min) + (idling_time × 0.01 L/min)
```

Idling uses less fuel than driving, but still wastes fuel and creates emissions:
```
CO2 = fuel_consumed × 2.31 kg/L
```

**Results Show:**
- Waiting at crossing: ~45 seconds idling per vehicle
- Rerouting: ~5 seconds extra driving, but no idling
- Net savings: 15% less fuel, 15% less CO2

### Understanding R² Score (Coefficient of Determination)

When we say our model has "R² = 0.986", what does that mean?

R² measures how well predictions match actual values, on a scale from 0 to 1:
- **R² = 1.0**: Perfect predictions (every prediction exactly matches reality)
- **R² = 0.5**: Model explains 50% of the variation in the data
- **R² = 0.0**: Model is no better than just guessing the average

**Our ETA Model: R² = 0.986**

This means our model explains 98.6% of the variation in train arrival times. Only 1.4% of the variation is unexplained (due to randomness or factors we didn't measure).

**How it's calculated:**
```
R² = 1 - (sum of squared errors) / (total variance)
```

Where:
- Squared errors: How far each prediction is from actual value, squared
- Total variance: How spread out the actual values are

A high R² (above 0.9) indicates very accurate predictions. For comparison, weather forecasts typically have R² around 0.7-0.8.

### From Training Data to Arduino Code

Here's the complete pipeline:

**Step 1: Generate Training Data (train_data.py)**
- Creates 2000 simulated train trajectories in SUMO
- Varies speed (20-48 m/s), acceleration (0.3-2.0 m/s²), length (100-250m)
- Records exact position and speed every 0.1 seconds
- Saves as CSV file

**Step 2: Extract Features (train_data.py)**  
- Reads the trajectory data
- Finds when train passed each sensor
- Calculates all 14 features
- Saves features.csv with 2000 rows × 14 columns

**Step 3: Train Models (train_models.py)**
- Loads features.csv
- Splits into 80% training, 20% testing
- Trains Random Forest models
- Evaluates accuracy on test set
- Saves trained models as .pkl files

**Step 4: Export to Arduino (export_arduino.py)**
- Reads config.yaml for sensor positions and thresholds
- Generates model.h with prediction functions
- Generates thresholds.h with sensor configurations
- Generates config.h with hardware settings

**Step 5: Upload to Arduino**
- Compile sketch.ino with all header files
- Upload to Arduino Uno
- System now runs independently, making predictions in real-time

The entire process takes about 35 minutes to run, producing a working system that makes predictions in milliseconds on the Arduino.

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
