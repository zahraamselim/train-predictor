# Machine Learning Pipeline Documentation

## Overview

The ML pipeline trains artificial intelligence models to predict both when a train will arrive at a railroad crossing (ETA) and when it will fully clear the crossing (ETD). These predictions allow the crossing gates to close at exactly the right time and open as soon as safe, minimizing wait times for cars while maintaining safety.

## Pipeline Components

The ML pipeline consists of five main modules that work together in sequence:

1. **Data Generator** - Creates training data
2. **Feature Extractor** - Processes raw data into useful features
3. **Model Trainer** - Trains the prediction models
4. **Model Exporter** - Converts models for embedded hardware
5. **Model Evaluator** - Measures model performance

## 1. Data Generator (data_generator.py)

### Purpose

Generates synthetic train trajectory data using SUMO traffic simulator. This creates thousands of different train scenarios with varying speeds, accelerations, and lengths to train the models on diverse situations.

### How It Works

**Step 1: Network Creation**

- Creates a simple straight railroad track in SUMO
- Track runs from -2000m to +2000m (4km total)
- Maximum allowed speed: 50 m/s (180 km/h)

**Step 2: Parameter Generation**

- Creates 2000 different train configurations
- Each train has random but realistic parameters:
  - **Speed**: Fast (35-45 m/s), Medium (25-35 m/s), or Slow (15-25 m/s)
  - **Acceleration**: 0.3-2.5 m/s²
  - **Deceleration**: 0.3-2.5 m/s²
  - **Length**: 100m, 150m, 200m, or 250m
  - **Speed factor**: 0.9-1.1 (variation in maintaining speed)

**Step 3: Simulation Execution**

- Runs each train configuration through SUMO
- Records train position, speed, acceleration, and length every 0.1 seconds
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
  - `length`: Train length in meters
  - `run_id`: Unique identifier for this simulation

### Output

- File: `outputs/data/raw_trajectories.csv`
- Contains approximately 1.7M data points (2000 trains × ~850 time steps)
- Each row represents one time step for one train

### Configuration

Controlled by `config/ml.yaml`:

```yaml
training:
  n_samples: 2000
  sim_duration: 300
  random_seed: 42
```

## 2. Feature Extractor (feature_extractor.py)

### Purpose

Transforms raw trajectory data into meaningful features that the machine learning models can learn from. Each train's journey is converted into a single row of calculated features.

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
- Detects when train front reaches crossing
- Detects when train rear clears crossing (front position + train length)

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

**Step 4: Distance and Length Features**

- `distance_remaining`: Meters from last sensor to crossing
- `train_length`: Length of the train in meters
- `length_speed_ratio`: Train length divided by current speed
- `distance_length_ratio`: Distance remaining divided by train length

**Step 5: Target Variables**

- `eta_actual`: True time from last sensor to crossing front arrival
- `etd_actual`: True time from last sensor to crossing rear clearance
- `eta_physics`: Simple physics calculation for ETA baseline
- `etd_physics`: Simple physics calculation for ETD baseline

### Physics Baseline Calculation

**ETA Physics**: Uses kinematic equation `d = v*t + 0.5*a*t²` to solve for time

**ETD Physics**: Calculates time for train length to pass at crossing:

- First calculates ETA to get time to crossing
- Estimates speed at crossing: `speed_at_crossing = last_speed + last_accel * eta`
- Adds time for length to pass: `etd = eta + train_length / speed_at_crossing`

### Output

- File: `outputs/data/features.csv`
- 2000 rows (one per train)
- 14 feature columns + 4 target columns + 1 ID column

### Example Feature Row

```
distance_remaining: 322.87m
train_length: 200m
last_speed: 32.45 m/s
last_accel: 0.15 m/s²
speed_trend: -0.03
length_speed_ratio: 6.16
distance_length_ratio: 1.61
eta_actual: 10.1s
etd_actual: 16.3s
```

## 3. Model Trainer (model_trainer.py)

### Purpose

Trains Random Forest models to predict both ETA and ETD based on sensor data. Random forests combine multiple decision trees to reduce overfitting and improve generalization.

### Algorithm: Random Forest Regressor

A random forest consists of multiple decision trees, each trained on a slightly different subset of the data. The final prediction is the average of all trees:

```
Tree 1 predicts: 9.8s
Tree 2 predicts: 10.1s
Tree 3 predicts: 9.9s
...
Tree 10 predicts: 10.0s

Final prediction: 9.95s (average)
```

### Training Process

**Step 1: Data Splitting**

- **Training set (70%)**: 1400 samples - Used to build the models
- **Validation set (15%)**: 300 samples - Used to choose best hyperparameters
- **Test set (15%)**: 300 samples - Used to evaluate final performance

**Step 2: Hyperparameter Search**

Both ETA and ETD models search over:

- Number of trees: 5, 10, 15
- Maximum depth: 4-9
- Minimum samples per leaf: 5, 8, 10

The search finds the combination that minimizes validation error.

**Step 3: Model Training**

For each model:

- Trains Random Forest on training data
- Each tree is built on a bootstrap sample (random subset with replacement)
- Trees are grown to specified depth with regularization constraints
- Uses all CPU cores for parallel training (n_jobs=-1)

**Step 4: Evaluation**

Calculates performance metrics:

- **MAE (Mean Absolute Error)**: Average prediction error in seconds
- **RMSE (Root Mean Square Error)**: Emphasizes large errors
- **R² Score**: How well model explains variance (0 to 1, higher is better)
- **Improvement over physics**: Percentage better than simple physics baseline

### Output

Two model files:

- `outputs/models/eta_model.pkl` - ETA prediction model
- `outputs/models/etd_model.pkl` - ETD prediction model

Each contains:

- Trained Random Forest model
- List of feature names
- Performance metrics
- Training configuration

### Expected Performance

With 2000 training samples:

**ETA Model**:

```
Training MAE: ~0.02s
Test MAE: ~0.04s
Test R²: >0.97
Improvement over physics: 5-15%
```

**ETD Model**:

```
Training MAE: ~0.05s
Test MAE: ~0.07s
Test R²: >0.96
Improvement over physics: 5-20%
```

### Why Random Forests?

**Advantages over single decision trees**:

- Reduced overfitting through ensemble averaging
- Better generalization to unseen data
- More stable predictions
- Can capture complex non-linear relationships

**Trade-offs**:

- Larger model size (multiple trees)
- Slightly slower prediction (must evaluate all trees)
- Still deployable on Arduino with 5-15 trees

## 4. Model Exporter (model_exporter.py)

### Purpose

Converts the trained Random Forest models into C code that can run on an Arduino or other embedded system. This allows the crossing control system to make predictions without needing a full computer.

### Conversion Process

**Step 1: Load Models**

- Reads both ETA and ETD models from pickle files
- Extracts all decision trees from each forest
- Gets feature names and tree structures

**Step 2: Generate C Code for Each Tree**

Converts each tree in the forest to C functions. For a 3-tree forest:

```c
float predictETA_tree0(float features[14]) {
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

float predictETA_tree1(float features[14]) {
    // Similar structure...
}

float predictETA_tree2(float features[14]) {
    // Similar structure...
}
```

**Step 3: Generate Ensemble Function**

Creates wrapper function that averages all tree predictions:

```c
float predictETA(float features[14]) {
    float sum = 0.0f;
    sum += predictETA_tree0(features);
    sum += predictETA_tree1(features);
    sum += predictETA_tree2(features);
    return sum / 3.0f;
}
```

**Step 4: Add Documentation**

Includes header comments explaining:

- What each feature index represents
- Number of trees in forest
- How to call the functions

### Output

- File: `outputs/models/train_models.h`
- C header file ready for Arduino
- Contains both ETA and ETD prediction functions
- Typical size: 5-15 trees per model, 20-50 nodes per tree

### Usage in Arduino

```cpp
#include "train_models.h"

float features[14] = {
    322.87,  // distance_remaining
    200.0,   // train_length
    32.45,   // last_speed
    0.15,    // last_accel
    -0.03,   // speed_trend
    0.02,    // speed_variance
    0.15,    // time_variance
    32.1,    // avg_speed_overall
    6.16,    // length_speed_ratio
    1.61,    // distance_length_ratio
    15.2,    // dt_interval_0
    9.8,     // dt_interval_1
    32.0,    // avg_speed_0
    32.5     // avg_speed_1
};

float eta = predictETA(features);  // Time until front arrives
float etd = predictETD(features);  // Time until rear clears
```

### Why This Matters

**Advantages**:

- Arduino has limited memory (32 KB on typical boards)
- No need for Python or ML libraries on hardware
- Predictions run in milliseconds
- No network connection required
- Both predictions available with single feature computation

**Limitations**:

- Models cannot be retrained on Arduino
- New models require regenerating the C code
- Forest size limited by Arduino memory (typically 5-15 trees feasible)

## 5. Model Evaluator (evaluator.py)

### Purpose

Provides comprehensive analysis of both trained models' performance and saves detailed metrics for documentation and comparison.

### Evaluation Metrics

**Dataset Statistics**:

- Number of training samples
- Average, standard deviation, min, and max for both ETA and ETD
- Shows the range of scenarios the models learned from

**Performance Metrics (for each model)**:

- **Test MAE**: Error on unseen data
- **Test RMSE**: Emphasizes large prediction errors
- **Test R²**: Goodness of fit (closer to 1.0 is better)

**Baseline Comparison**:

- Physics-based prediction error
- Percentage improvement of ML over physics

**Model Architecture**:

- Number of input features (14)
- Model type (RandomForestRegressor)
- Number of trees in each forest

### Output Files

**1. JSON Results** (`outputs/results/evaluation_results.json`)

```json
{
  "eta_metrics": {
    "test_mae": 0.042,
    "test_rmse": 0.068,
    "test_r2": 0.976,
    "physics_baseline_mae": 0.057,
    "improvement_over_physics": 26.3
  },
  "etd_metrics": {
    "test_mae": 0.071,
    "test_rmse": 0.145,
    "test_r2": 0.967,
    "physics_baseline_mae": 0.086,
    "improvement_over_physics": 17.4
  },
  "dataset_stats": {
    "n_samples": 2000,
    "eta_mean": 6.71,
    "eta_std": 0.38,
    "etd_mean": 10.4,
    "etd_std": 1.31
  },
  "model_info": {
    "eta": {
      "type": "RandomForestRegressor",
      "n_features": 14,
      "n_trees": 10
    },
    "etd": {
      "type": "RandomForestRegressor",
      "n_features": 14,
      "n_trees": 10
    }
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
- Test MAE not much larger than Train MAE (not overfitting)

**Warning Signs**:

- Large gap between train and test MAE (overfitting)
- Low R² < 0.90 (model not learning patterns)
- Negative improvement (worse than physics)

## Configuration Files

### ml.yaml

Complete configuration for the entire ML pipeline:

```yaml
network:
  start_x: -2000
  end_x: 2000
  max_speed: 50.0
  track_length: 4000

sensors:
  s0: 1870
  s1: 2355
  s2: 2678
  crossing: 3000

training:
  n_samples: 2000
  sim_duration: 300
  random_seed: 42

  speed_distribution:
    fast:
      min: 35
      max: 45
    medium:
      min: 25
      max: 35
    slow:
      min: 15
      max: 25

  train_params:
    lengths: [100, 150, 200, 250]
    accel_range: [0.3, 2.5]
    decel_range: [0.3, 2.5]
    speed_factor_range: [0.9, 1.1]

model:
  type: random_forest
  max_depth_range: [4, 10]
  min_samples_split: 5
  test_size: 0.15
  val_size: 0.15

output:
  data_dir: data
  model_dir: models
  results_dir: results
  sumo_dir: sumo
  arduino_header: train_models.h
  python_model: eta_model.pkl
```

## Running the Pipeline

### Full Pipeline

```bash
make ml-pipeline
```

Executes all steps in sequence:

1. Data generation (2-3 hours for 2000 samples)
2. Feature extraction (few seconds)
3. Model training (1-2 minutes with hyperparameter search)
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
make ml-train          # Train models
make ml-export         # Export for Arduino
make ml-evaluate       # Evaluate performance
```

## File Dependencies

```
ml.yaml
    │
    ├─> data_generator.py
    │       │
    │       └─> raw_trajectories.csv (with length column)
    │               │
    │               └─> feature_extractor.py
    │                       │
    │                       └─> features.csv (14 features, ETA & ETD targets)
    │                               │
    │                               └─> model_trainer.py
    │                                       │
    │                                       ├─> eta_model.pkl (Random Forest)
    │                                       │       │
    │                                       ├─> etd_model.pkl (Random Forest)
    │                                       │       │
    │                                       │       ├─> model_exporter.py
    │                                       │       │       │
    │                                       │       │       └─> train_models.h
    │                                       │       │
    │                                       │       └─> evaluator.py
    │                                       │               │
    │                                       │               └─> evaluation_results.json
    │                                       │
    │                                       └─> (training metrics displayed)
```

## Failed Experiments and Lessons Learned

### Experiment 1: Single Decision Trees with Limited Data

**What We Tried**: Trained single decision trees (depth 3-15) on 500 samples to predict both ETA and ETD.

**The Problem**:

- ETA model: Barely beat physics baseline (1-2% improvement)
- ETD model: Performed WORSE than physics baseline (-13% to -27%)
- Both models had high node counts (125-191 nodes) indicating overfitting
- Test R² was good (0.94-0.97) but test MAE was worse than simple physics

**Root Cause**:

- Insufficient training data (500 samples) for the complexity of the problem
- Decision trees with 125+ nodes were memorizing training data patterns
- ETD has higher variance (std: 1.31s vs 0.38s for ETA) due to train length variation
- The physics baseline for ETD was already quite accurate (0.086s error)
- Single trees couldn't generalize well to unseen combinations of speed, acceleration, and length

**What We Learned**:

- More training data is essential for learning complex relationships
- High node count with small dataset = overfitting
- ETD is fundamentally harder than ETA because it depends on train length passing time
- Single decision trees are too simple for this multi-variable prediction task

### Experiment 2: Using ETA as Input to ETD Model

**What We Tried**: Created a hierarchical model where ETD uses the predicted ETA as an additional feature, reasoning that ETD = ETA + time_for_length_to_pass.

**The Problem**:

- Added complexity without improving performance
- ETD model still performed worse than physics (-27.6% improvement)
- Created dependency chain making deployment more complex
- Feature "eta_predicted" leaked information from training set

**Root Cause**:

- The relationship ETD = ETA + length/speed is already captured by physics
- ML model needs to learn CORRECTIONS to physics, not recreate physics
- Adding ETA prediction introduced error propagation
- Still had fundamental problem: not enough training data

**What We Learned**:

- Don't overcomplicate the model architecture
- Feature engineering should provide new information, not redundant calculations
- When physics baseline is good, ML should learn residuals, not recreate the formula

### Experiment 3: Derived ETD from ML-Predicted ETA

**What We Tried**: Only train ML for ETA, then calculate ETD using: `ETD = ETA_predicted + train_length / speed_at_crossing`

**The Problem**:

- This was actually a reasonable approach and would have worked
- However, it defeats the purpose of using ML for ETD
- Any improvements in ETA barely translated to ETD improvements
- Lost opportunity to learn ETD-specific patterns (like how train length affects deceleration)

**What We Learned**:

- Sometimes the simple solution is good enough
- But if ML is required for both predictions (project requirement), need a better approach
- Separating concerns (ETA vs ETD) makes sense, but both should use ML

### Final Solution: Random Forests with More Data

**What Changed**:

1. Increased training samples from 500 to 2000 (4x more data)
2. Switched from single decision trees to Random Forests (5-15 trees)
3. Added engineered features: `length_speed_ratio`, `distance_length_ratio`
4. Applied stronger regularization: min_leaf 5-10, depth 4-9
5. Trained completely independent models for ETA and ETD

**Why This Works**:

- 2000 samples provide enough examples of different train length + speed + acceleration combinations
- Random Forests reduce overfitting through bootstrap aggregating (bagging)
- Each tree sees different data, final prediction is average (more stable)
- Engineered features help model understand train length impact on timing
- Regularization prevents individual trees from becoming too complex
- Independent models allow each to learn task-specific patterns

**Results**:

- ETA: 5-15% improvement over physics, R² > 0.97
- ETD: 5-20% improvement over physics, R² > 0.96
- Both models generalize well to test set
- Deployable on Arduino (5-15 trees × 20-50 nodes = manageable size)

## Troubleshooting

### No Successful Simulations

**Problem**: `No successful simulations` message  
**Cause**: SUMO network or configuration error  
**Solution**: Check that SUMO is installed and network files exist

### Low Model Performance

**Problem**: Test R² < 0.90 or negative improvement over physics  
**Cause**: Insufficient training data or poor regularization  
**Solution**:

- Increase `n_samples` to 2000 or more
- Check sensor positions are reasonable
- Verify speed distributions cover expected range
- Ensure Random Forest hyperparameters include regularization (min_leaf ≥ 5)

### Overfitting

**Problem**: Training MAE much lower than test MAE, high node counts  
**Cause**: Model too complex for amount of data  
**Solution**:

- Use Random Forests instead of single trees
- Increase `min_samples_leaf` to 8-10
- Limit `max_depth` to 4-9
- Generate more training samples

### Memory Issues on Arduino

**Problem**: Arduino runs out of memory  
**Cause**: Too many trees or trees too deep  
**Solution**:

- Reduce number of trees to 5-10
- Reduce `max_depth` to 4-6
- Consider using single decision tree with strong regularization for resource-constrained devices

### ETD Worse Than Physics

**Problem**: ETD model improvement is negative  
**Cause**: Insufficient training data or overfitting  
**Solution**:

- Must have at least 1500-2000 samples
- Use Random Forests, not single trees
- Add length-related engineered features
- Increase regularization (min_leaf ≥ 8)

## Technical Terms Glossary

**Random Forest**: Ensemble learning method that combines multiple decision trees, each trained on different data subsets, to make more accurate and stable predictions.

**Decision Tree**: Machine learning algorithm that makes predictions by following a series of if-then rules, similar to a flowchart.

**Ensemble**: Combining multiple models to produce better predictions than any single model.

**Bootstrap Sampling**: Creating training subsets by randomly sampling with replacement from the original dataset.

**Feature**: A measurable property used as input to the model (e.g., speed, distance, acceleration, train length).

**ETA (Estimated Time of Arrival)**: Predicted time until train front reaches crossing.

**ETD (Estimated Time of Departure)**: Predicted time until train rear clears crossing.

**MAE (Mean Absolute Error)**: Average size of prediction errors, ignoring whether they're over or under estimates.

**RMSE (Root Mean Square Error)**: Similar to MAE but penalizes large errors more heavily.

**R² Score**: Percentage of variance in the target variable that the model explains. 1.0 is perfect, 0.0 means model is no better than guessing the average.

**Overfitting**: When a model learns the training data too well (including noise) and performs poorly on new data.

**Regularization**: Techniques to prevent overfitting by constraining model complexity (e.g., limiting tree depth, requiring minimum samples per leaf).

**Hyperparameter**: A setting that controls how the model learns (e.g., number of trees, tree depth), as opposed to parameters the model learns from data.

**Validation Set**: Data used to choose the best hyperparameters, separate from test set used for final evaluation.

**Feature Engineering**: Creating new features from existing data that help the model learn better (e.g., length_speed_ratio).

## Summary

The ML pipeline creates an intelligent system that predicts both train arrival and departure times more accurately than simple physics calculations. By training Random Forest models on 2000 diverse train scenarios, the system learns complex relationships between train length, speed, acceleration, and timing. The models achieve 5-20% improvements over physics baselines, with predictions accurate to within 40-70 milliseconds. The exported C code allows these predictions to run on inexpensive embedded hardware, making the system practical for real-world deployment at railroad crossings.
