# Machine Learning Pipeline Documentation

## Overview

The ML pipeline trains an artificial intelligence model to predict when a train will arrive at a railroad crossing. This prediction allows the crossing gates to close at exactly the right time, minimizing wait times for cars while maintaining safety.

## Pipeline Components

The ML pipeline consists of five main modules that work together in sequence:

1. **Data Generator** - Creates training data
2. **Feature Extractor** - Processes raw data into useful features
3. **Model Trainer** - Trains the prediction model
4. **Model Exporter** - Converts model for embedded hardware
5. **Model Evaluator** - Measures model performance

---

## 1. Data Generator (data_generator.py)

### Purpose

Generates synthetic train trajectory data using SUMO traffic simulator. This creates hundreds of different train scenarios with varying speeds, accelerations, and lengths to train the model on diverse situations.

### How It Works

**Step 1: Network Creation**

- Creates a simple straight railroad track in SUMO
- Track runs from -2000m to +2000m (4km total)
- Maximum allowed speed: 50 m/s (180 km/h)

**Step 2: Parameter Generation**

- Creates 500 different train configurations
- Each train has random but realistic parameters:
  - **Speed**: Fast (35-45 m/s), Medium (25-35 m/s), or Slow (15-25 m/s)
  - **Acceleration**: 0.3-2.5 m/s²
  - **Deceleration**: 0.3-2.5 m/s²
  - **Length**: 100m, 150m, 200m, or 250m
  - **Speed factor**: 0.9-1.1 (variation in maintaining speed)

**Step 3: Simulation Execution**

- Runs each train configuration through SUMO
- Records train position, speed, and acceleration every 0.1 seconds
- Duration: 300 seconds per simulation
- Generates temporary XML files for SUMO configuration
- Cleans up temporary files after each run

**Step 4: Data Parsing**

- Extracts vehicle data from SUMO's XML output
- Creates structured dataset with columns:
  - `time`: Timestamp in seconds
  - `pos`: Position along track in meters
  - `speed`: Current speed in m/s
  - `acceleration`: Current acceleration in m/s²
  - `run_id`: Unique identifier for this simulation

### Output

- File: `outputs/data/raw_trajectories.csv`
- Contains approximately 430,000 data points
- Each row represents one time step for one train

### Configuration

Controlled by `config/ml.yaml`:

```yaml
training:
  n_samples: 500 # Number of train scenarios
  sim_duration: 300 # Seconds per simulation
  random_seed: 42 # For reproducibility
```

---

## 2. Feature Extractor (feature_extractor.py)

### Purpose

Transforms raw trajectory data into meaningful features that the machine learning model can learn from. Each train's journey is converted into a single row of calculated features.

### Sensor System

The system uses 3 sensors before the crossing plus the crossing itself:

- **Sensor 0 (s0)**: 1870m before crossing
- **Sensor 1 (s1)**: 2355m before crossing
- **Sensor 2 (s2)**: 2678m before crossing
- **Crossing**: 3000m mark

### Feature Calculation Process

**Step 1: Sensor Trigger Detection**
For each train trajectory:

- Identifies the exact moment each sensor is triggered
- Records time, speed, and acceleration at each trigger point

**Step 2: Time-Based Features**

- `dt_interval_0`: Time between sensor 0 and sensor 1
- `dt_interval_1`: Time between sensor 1 and sensor 2
- `time_variance`: How consistent the train's timing is

**Step 3: Speed-Based Features**

- `last_speed`: Speed at the last sensor before crossing
- `last_accel`: Acceleration at the last sensor
- `avg_speed_0`: Average speed between sensors 0 and 1
- `avg_speed_1`: Average speed between sensors 1 and 2
- `avg_speed_overall`: Average of all segment speeds
- `speed_trend`: Whether train is speeding up or slowing down
- `speed_variance`: How much speed varies

**Step 4: Distance Feature**

- `distance_remaining`: Meters from last sensor to crossing

**Step 5: Target Variables**

- `eta_actual`: True time from last sensor to crossing (what we want to predict)
- `eta_physics`: Simple physics calculation for comparison (distance/speed)

### Physics Baseline Calculation

Uses kinematic equation: `d = v*t + 0.5*a*t²`

Where:

- `d` = distance remaining
- `v` = current speed
- `a` = current acceleration
- `t` = time (what we solve for)

This provides a baseline that the ML model should beat.

### Output

- File: `outputs/data/features.csv`
- 500 rows (one per train)
- 11 feature columns + 2 target columns + 1 ID column

### Example Feature Row

```
distance_remaining: 322.87m
last_speed: 32.45 m/s
last_accel: 0.15 m/s²
speed_trend: -0.03 (slightly slowing)
dt_interval_0: 15.2s
dt_interval_1: 9.8s
eta_actual: 10.1s (true value)
eta_physics: 9.9s (simple calculation)
```

---

## 3. Model Trainer (model_trainer.py)

### Purpose

Trains a decision tree model to predict train arrival time (ETA) based on sensor data. The model learns patterns from the 500 training examples.

### Algorithm: Decision Tree Regressor

A decision tree makes predictions by asking a series of yes/no questions:

```
Is speed > 30 m/s?
├─ Yes: Is acceleration > 0.5?
│  ├─ Yes: Predict ETA = 9.2s
│  └─ No: Is distance > 300m?
│     ├─ Yes: Predict ETA = 10.5s
│     └─ No: Predict ETA = 9.8s
└─ No: Predict ETA = 11.3s
```

### Training Process

**Step 1: Data Splitting**

- **Training set (70%)**: 350 samples - Used to build the model
- **Validation set (15%)**: 75 samples - Used to choose best model
- **Test set (15%)**: 75 samples - Used to evaluate final performance

**Step 2: Hyperparameter Search**
Tries different tree depths (3 to 15) to find the best model:

- Shallow trees (depth 3-5): Simple but may miss patterns
- Medium trees (depth 6-9): Balance of simplicity and accuracy
- Deep trees (depth 10-15): Very accurate but may overfit

The model selects depth based on validation set performance.

**Step 3: Model Training**

- Fits decision tree on training data
- Each split in the tree minimizes prediction error
- Continues splitting until reaching maximum depth or minimum samples

**Step 4: Evaluation**
Calculates performance metrics:

- **MAE (Mean Absolute Error)**: Average prediction error in seconds
- **RMSE (Root Mean Square Error)**: Emphasizes large errors
- **R² Score**: How well model explains variance (0 to 1, higher is better)

### Output

- File: `outputs/models/eta_model.pkl`
- Contains:
  - Trained decision tree model
  - List of feature names
  - Performance metrics
  - Training configuration

### Typical Performance

```
Training MAE: 0.013s
Test MAE: 0.053s
Test RMSE: 0.084s
Test R²: 0.969 (96.9% of variance explained)
Physics baseline MAE: 0.057s
Improvement over physics: 7.0%
```

### Why This Performance?

**High R² (96.9%)**:

- Model captures nearly all variation in arrival times
- Means predictions are very reliable

**Small MAE (0.053s)**:

- Average error is only 53 milliseconds
- Much smaller than typical human reaction time

**Improvement over Physics (7%)**:

- ML model accounts for factors physics equation ignores
- Examples: wind resistance, track conditions, driver behavior

---

## 4. Model Exporter (model_exporter.py)

### Purpose

Converts the trained Python model into C code that can run on an Arduino or other embedded system. This allows the crossing control system to make predictions without needing a full computer.

### Conversion Process

**Step 1: Load Model**

- Reads the trained decision tree from the pickle file
- Extracts tree structure (nodes, splits, thresholds)

**Step 2: Generate C Code**
Converts each node in the tree to an if-else statement:

Python model:

```python
if features[2] <= 30.5:
    if features[0] <= 300.0:
        return 9.8
    else:
        return 10.5
else:
    return 9.2
```

Becomes C code:

```c
float predictETA(float features[11]) {
    if (features[2] <= 30.5000f) {
        if (features[0] <= 300.0000f) {
            return 9.8000f;
        } else {
            return 10.5000f;
        }
    } else {
        return 9.2000f;
    }
}
```

**Step 3: Add Documentation**
Includes header comments explaining:

- What each feature index represents
- How to call the function
- Expected input format

### Output

- File: `outputs/models/eta_model.h`
- C header file ready for Arduino
- Typical size: 111 nodes (decision points)
- No external dependencies needed

### Usage in Arduino

```cpp
#include "eta_model.h"

float features[11] = {
    322.87,  // distance_remaining
    32.45,   // last_speed
    0.15,    // last_accel
    -0.03,   // speed_trend
    0.02,    // speed_variance
    0.15,    // time_variance
    32.1,    // avg_speed_overall
    15.2,    // dt_interval_0
    9.8,     // dt_interval_1
    32.0,    // avg_speed_0
    32.5     // avg_speed_1
};

float eta = predictETA(features);  // Returns predicted ETA in seconds
```

### Why This Matters

**Advantages**:

- Arduino has limited memory (32 KB on typical boards)
- No need for Python or ML libraries on hardware
- Predictions run in microseconds
- No network connection required

**Limitations**:

- Model cannot be retrained on Arduino
- New model requires regenerating the C code
- Tree size limited by Arduino memory

---

## 5. Model Evaluator (evaluator.py)

### Purpose

Provides comprehensive analysis of the trained model's performance and saves detailed metrics for documentation and comparison.

### Evaluation Metrics

**Dataset Statistics**:

- Number of training samples
- Average, standard deviation, min, and max ETA values
- Shows the range of scenarios the model learned from

**Performance Metrics**:

- **Test MAE**: Error on unseen data
- **Test RMSE**: Emphasizes large prediction errors
- **Test R²**: Goodness of fit (closer to 1.0 is better)

**Baseline Comparison**:

- Physics-based prediction error
- Percentage improvement of ML over physics

**Model Architecture**:

- Number of input features
- Number of tree nodes
- Maximum tree depth

### Output Files

**1. JSON Results** (`outputs/results/evaluation_results.json`)

```json
{
  "metrics": {
    "test_mae": 0.053,
    "test_rmse": 0.084,
    "test_r2": 0.969,
    "physics_baseline_mae": 0.057,
    "improvement_over_physics": 7.0
  },
  "dataset_stats": {
    "n_samples": 500,
    "eta_mean": 6.71,
    "eta_std": 0.38,
    "eta_min": 6.4,
    "eta_max": 9.1
  },
  "model_info": {
    "type": "DecisionTreeRegressor",
    "n_features": 11,
    "n_nodes": 111,
    "max_depth": 7
  }
}
```

**2. Console Summary**
Prints human-readable summary to terminal for quick review.

### Interpreting Results

**Good Model Indicators**:

- Test MAE < 0.1s (predictions within 100ms)
- Test R² > 0.95 (explains 95%+ of variance)
- Improvement over physics > 0% (beats simple calculation)
- Test MAE close to Train MAE (not overfitting)

**Warning Signs**:

- Large gap between train and test MAE (overfitting)
- Low R² < 0.90 (model not learning patterns)
- Negative improvement (worse than physics)

---

## Configuration Files

### ml.yaml

Complete configuration for the entire ML pipeline:

```yaml
network:
  start_x: -2000 # Track start position (meters)
  end_x: 2000 # Track end position (meters)
  max_speed: 50.0 # Maximum train speed (m/s)
  track_length: 4000 # Total track length (meters)

sensors:
  s0: 1870 # First sensor position (meters)
  s1: 2355 # Second sensor position (meters)
  s2: 2678 # Third sensor position (meters)
  crossing: 3000 # Crossing position (meters)

training:
  n_samples: 500 # Number of train scenarios
  sim_duration: 300 # Simulation time per train (seconds)
  random_seed: 42 # For reproducible results

  speed_distribution: # Train speed categories
    fast:
      min: 35 # m/s (126 km/h)
      max: 45 # m/s (162 km/h)
    medium:
      min: 25 # m/s (90 km/h)
      max: 35 # m/s (126 km/h)
    slow:
      min: 15 # m/s (54 km/h)
      max: 25 # m/s (90 km/h)

  train_params:
    lengths: [100, 150, 200, 250] # Train lengths (meters)
    accel_range: [0.3, 2.5] # Acceleration range (m/s²)
    decel_range: [0.3, 2.5] # Deceleration range (m/s²)
    speed_factor_range: [0.9, 1.1] # Speed variation factor

model:
  type: decision_tree # Model algorithm
  max_depth_range: [3, 15] # Tree depth search range
  min_samples_split: 5 # Minimum samples to split node
  test_size: 0.15 # 15% for testing
  val_size: 0.15 # 15% for validation

output:
  data_dir: data # Raw data directory
  model_dir: models # Trained models directory
  results_dir: results # Evaluation results directory
  sumo_dir: sumo # SUMO files directory
  arduino_header: eta_model.h # Arduino output filename
  python_model: eta_model.pkl # Python model filename
```

---

## Running the Pipeline

### Full Pipeline

```bash
make ml-pipeline
```

Executes all steps in sequence:

1. Data generation (20-30 minutes for 500 samples)
2. Feature extraction (few seconds)
3. Model training (few seconds)
4. Model export (instant)
5. Evaluation (instant)

### Quick Testing

```bash
make ml-pipeline-quick
```

Uses only 50 samples for rapid testing (~2 minutes total).

### Individual Steps

```bash
make ml-data           # Generate training data
make ml-features       # Extract features
make ml-train          # Train model
make ml-export         # Export for Arduino
make ml-evaluate       # Evaluate performance
```

---

## File Dependencies

```
ml.yaml
    │
    ├─> data_generator.py
    │       │
    │       └─> raw_trajectories.csv
    │               │
    │               └─> feature_extractor.py
    │                       │
    │                       └─> features.csv
    │                               │
    │                               └─> model_trainer.py
    │                                       │
    │                                       ├─> eta_model.pkl
    │                                       │       │
    │                                       │       ├─> model_exporter.py
    │                                       │       │       │
    │                                       │       │       └─> eta_model.h
    │                                       │       │
    │                                       │       └─> evaluator.py
    │                                       │               │
    │                                       │               └─> evaluation_results.json
    │                                       │
    │                                       └─> (training metrics displayed)
```

---

## Troubleshooting

### No Successful Simulations

**Problem**: `No successful simulations` message  
**Cause**: SUMO network or configuration error  
**Solution**: Check that SUMO is installed and network files exist

### Low Model Performance

**Problem**: Test R² < 0.90 or high MAE  
**Cause**: Insufficient training data or poor feature engineering  
**Solution**:

- Increase `n_samples` in config
- Check sensor positions are reasonable
- Verify speed distributions cover expected range

### Overfitting

**Problem**: Training MAE much lower than test MAE  
**Cause**: Model too complex for amount of data  
**Solution**:

- Reduce `max_depth_range` upper limit
- Increase `min_samples_split`
- Generate more training samples

### Memory Issues on Arduino

**Problem**: Arduino runs out of memory  
**Cause**: Decision tree too large  
**Solution**:

- Reduce `max_depth_range`
- Decrease number of features
- Use simpler model architecture

---

## Technical Terms Glossary

**Decision Tree**: Machine learning algorithm that makes predictions by following a series of if-then rules, similar to a flowchart.

**Feature**: A measurable property used as input to the model (e.g., speed, distance, acceleration).

**ETA (Estimated Time of Arrival)**: Predicted time until train reaches crossing.

**MAE (Mean Absolute Error)**: Average size of prediction errors, ignoring whether they're over or under estimates.

**RMSE (Root Mean Square Error)**: Similar to MAE but penalizes large errors more heavily.

**R² Score**: Percentage of variance in the target variable that the model explains. 1.0 is perfect, 0.0 means model is no better than guessing the average.

**Overfitting**: When a model learns the training data too well and performs poorly on new data.

**Hyperparameter**: A setting that controls how the model learns (e.g., tree depth), as opposed to parameters the model learns from data.

**Validation Set**: Data used to choose the best hyperparameters, separate from test set used for final evaluation.

---

## Summary

The ML pipeline creates an intelligent system that predicts train arrival times more accurately than simple physics calculations. By learning from hundreds of realistic train scenarios, the model accounts for subtle factors that improve prediction accuracy by 7%. The exported C code allows these predictions to run on inexpensive embedded hardware, making the system practical for real-world deployment at railroad crossings.
