# Machine Learning Pipeline

## Overview

This pipeline trains AI models to predict train arrival (ETA) and departure (ETD) times at railroad crossings. The system learns from thousands of simulated train examples to make predictions more accurate than simple physics formulas.

## Why Machine Learning

Simple physics predicts: `time = distance / speed`

But real trains:

- Accelerate and decelerate
- Have varying lengths
- Behave unpredictably
- Change speed during approach

Machine learning learns these patterns from data.

## Pipeline Components

### 1. Data Preparation (`data.py`)

Handles data generation, feature extraction, and visualization in one module.

**Data Generation:**

- Simulates 1000 trains using SUMO
- Five realistic operating scenarios:
  - Fast trains: 40-48 m/s, low accel/decel (express trains)
  - Moderate trains: 30-40 m/s, medium accel/decel (regular freight)
  - Slow trains: 20-32 m/s, low accel/high decel (heavy/cautious)
  - Accelerating trains: 25-35 m/s starting, high acceleration
  - Decelerating trains: 35-45 m/s starting, high deceleration
- Variable lengths: 100, 150, 200, 250 meters
- Records position, speed, acceleration every 0.1 seconds

**Feature Extraction:**

- 3 sensors before crossing (1500m, 2100m, 2550m)
- Crossing at 3000m
- Extracts 10 features per train:
  - distance_remaining: Meters from last sensor to crossing
  - train_length: Length in meters
  - last_speed: Speed at last sensor
  - speed_change: Speed difference between first and last sensor
  - time_01: Time between sensors 0 and 1
  - time_12: Time between sensors 1 and 2
  - avg_speed_01: Average speed between sensors 0-1
  - avg_speed_12: Average speed between sensors 1-2
  - accel_trend: Recent acceleration (for ETD model)
  - predicted_speed_at_crossing: Extrapolated speed (for ETD model)

Note: ETA model uses first 8 features, ETD model uses all 10 features. The extra features help predict how quickly the train will clear the crossing.

**Visualization:**
Creates 4 plot files:

- train_trajectories.png: Sample train movements with scenario labels
- feature_distributions.png: Feature histograms
- feature_correlations.png: Feature-ETA relationships
- physics_comparison.png: ML vs simple physics

**Outputs:**

- `outputs/data/raw_trajectories.csv`: Raw simulation data with scenarios
- `outputs/data/features.csv`: Extracted features with scenario labels
- `outputs/plots/`: Visualization images

### 2. Model Training (`model.py`)

Trains and evaluates Gradient Boosting models for ETA and ETD.

**Gradient Boosting:**
An ensemble method that builds multiple decision trees sequentially. Each tree learns to correct the errors of previous trees. More powerful than linear regression but still efficient enough for embedded systems.

**Model Configuration:**

```python
GradientBoostingRegressor(
    n_estimators=200,        # 200 decision trees
    learning_rate=0.05,      # Conservative learning
    max_depth=5,             # Shallow trees prevent overfitting
    min_samples_split=3,     # Minimum samples to split a node
    min_samples_leaf=2,      # Minimum samples per leaf
    subsample=0.9,           # Use 90% of data per tree
    max_features='sqrt',     # Feature sampling
    validation_fraction=0.15,
    n_iter_no_change=15,     # Early stopping
    tol=0.00001
)
```

**Training Process:**

1. Split data: 64% training, 16% validation, 20% testing
2. Standardize features (zero mean, unit variance)
3. Train model with early stopping
4. Track training curves (loss and R² score)
5. Evaluate on test data
6. Generate performance plots
7. Save model with scaler

**Performance Metrics:**

- MAE (Mean Absolute Error): Average prediction error in seconds
- RMSE (Root Mean Squared Error): Penalizes larger errors more
- R² Score: How well model explains data (0-1, higher better)
- Improvement: Percentage better than physics baseline

**Outputs:**

- `outputs/models/eta_model.pkl`: ETA model (8 features)
- `outputs/models/etd_model.pkl`: ETD model (10 features)
- `outputs/plots/eta_history.png`: ETA training curves
- `outputs/plots/etd_history.png`: ETD training curves
- `outputs/plots/eta_training.png`: ETA performance plots
- `outputs/plots/etd_training.png`: ETD performance plots
- `outputs/results/evaluation_results.json`: Metrics summary

## Running the Pipeline

### Full pipeline (1000 samples):

```bash
python -m ml.data
python -m ml.model
```

Or using make:

```bash
make ml-data
make ml-train
```

### Quick test (50 samples):

```bash
python -m ml.data --samples 50
python -m ml.model
```

### Custom configuration:

```bash
python -m ml.data --config ml/config.yaml --samples 500
python -m ml.model --config ml/config.yaml
```

## Expected Results

**ETA Model (8 features):**

- Test error: 0.3-0.4 seconds
- R² score: 0.92-0.96
- RMSE: 0.4-0.5 seconds
- Improvement over physics: 25-35%

**ETD Model (10 features):**

- Test error: 0.4-0.5 seconds
- R² score: 0.88-0.93
- RMSE: 0.5-0.6 seconds
- Improvement over physics: 20-30%

The ETD model is slightly less accurate because it must predict future train behavior (speed at crossing and clearance rate), which is inherently more uncertain than predicting arrival time.

## Understanding the Outputs

### Trajectory Plots

Shows 6 sample trains moving through sensors. Each subplot shows:

- Position over time (with scenario labels)
- Speed over time (now shows variation!)
- Acceleration over time (positive/negative patterns)
- Speed vs position

Look for variety in speed profiles. You should see trains that speed up, slow down, maintain constant speed, etc. This validates that the training data captures realistic train behavior.

### Feature Distribution Plots

Histograms of all 8 base features plus targets. Look for:

- Wide spread (good variety)
- Reasonable distributions (may not be perfectly normal)
- No unusual spikes or gaps
- Realistic ranges (speeds 20-50 m/s, etc.)

### Feature Correlation Plots

Shows how each feature relates to ETA. Correlation values:

- +1.0: Perfect positive correlation
- 0.0: No relationship
- -1.0: Perfect negative correlation

Examples:

- last_speed: strong negative correlation (higher speed = shorter time)
- distance_remaining: strong positive correlation (more distance = more time)
- avg_speed_12: stronger correlation than avg_speed_01 (recent data more important)

### Physics Comparison Plots

Compares simple physics to actual times. Spread from diagonal line shows physics error (~0.5-0.6s). Points should scatter around the perfect prediction line, showing that simple physics is reasonable but imperfect.

### Training History Plots

Shows loss and accuracy (R² score) over 200 training epochs:

Good signs:

- Both training and validation curves decrease smoothly
- Curves converge (don't diverge)
- Validation performance stays close to training
- No wild fluctuations

Bad signs:

- Validation loss increases while training decreases (overfitting)
- Large gap between training and validation (overfitting)
- Erratic curves (learning rate too high)

### Training Performance Plots

6 subplots per model:

1. Training predictions vs actual (should cluster on diagonal)
2. Test predictions vs actual (most important - should cluster on diagonal)
3. Error distribution (should be bell-shaped, centered near zero)
4. Feature importance (which features matter most)
5. Performance comparison (ML vs physics baseline)
6. Residual plot (should be random scatter around zero)

Good signs:

- Points near diagonal in prediction plots
- Bell-shaped error distribution centered at zero
- Test R² > 0.90 for ETA, > 0.85 for ETD
- Random residuals with no patterns
- Feature importances make sense (speed and distance important)

Bad signs:

- Points far from diagonal
- Test much worse than training (overfitting)
- Patterns in residuals (missing information)
- Skewed error distribution (systematic bias)

## Configuration

Edit `ml/config.yaml`:

```yaml
network:
  start_x: -2000
  end_x: 2000
  max_speed: 50.0
  track_length: 4000

sensors:
  s0: 1500 # First sensor
  s1: 2100 # Second sensor
  s2: 2550 # Third sensor (last before crossing)
  crossing: 3000 # Crossing position

training:
  n_samples: 1000
  sim_duration: 400 # Increased for slower trains
  random_seed: 42
  train_params:
    lengths: [100, 150, 200, 250]

model:
  type: linear_regression # Legacy config value (not used)
  test_size: 0.2
```

Adjustments:

- More accuracy: Increase n_samples to 2000
- Faster testing: Decrease n_samples to 100
- Different sensors: Change sensor positions (maintain increasing order)
- Longer trains: Add values to lengths array (e.g., [100, 150, 200, 250, 300])

## What Changed from Linear Regression

### Previous Approach (Linear Regression)

```
ETA = w1*distance + w2*speed + w3*length + ... + bias
```

Problems:

- Assumes linear relationships
- Can't capture acceleration/deceleration patterns
- No way to model train behavior changes
- Limited accuracy (10-15% improvement over physics)

### New Approach (Gradient Boosting)

```
ETA = tree1(features) + tree2(residuals) + tree3(residuals) + ...
```

Advantages:

- Learns non-linear patterns automatically
- Captures acceleration and deceleration
- Handles complex feature interactions
- Better accuracy (25-35% improvement over physics)
- Still efficient enough for embedded systems

### Why Not Neural Networks?

Neural networks would be too large and slow for Arduino deployment. Gradient Boosting provides a sweet spot:

- Better accuracy than linear regression
- Still deployable on embedded systems
- Interpretable (can see feature importances)
- Fast prediction (just tree traversals)

## Failed Experiments

### Experiment 1: All Trains Same Speed

**Result:** Poor model performance

- R² score: 0.70
- Test error: 0.7s
- Model had nothing to learn from

**Lesson:** Need variety in training data. Implemented 5 different scenarios.

### Experiment 2: Only 100 Training Samples

**Result:** High variance, inconsistent results

- ETA error: 0.6-0.9s depending on random split
- R² score: 0.75-0.85

**Lesson:** Need 500-1000 samples minimum for stable results.

### Experiment 3: Too Many Trees (500+)

**Result:** Overfitting

- Training error: 0.05s (too good to be true)
- Test error: 0.6s (worse than 200 trees)
- Training took much longer

**Lesson:** 200 trees with early stopping is optimal.

### Experiment 4: Deep Trees (max_depth=10)

**Result:** Overfitting and instability

- Model memorized training data
- Poor generalization to test set
- Sensitive to small changes in features

**Lesson:** Shallow trees (depth 5) generalize better.

### Experiment 5: ETD Without Extra Features

**Result:** ETD error 0.8s (worse than with features)

- Model couldn't predict speed changes during crossing clearance

**Lesson:** Need accel_trend and predicted_speed_at_crossing for good ETD predictions.

## Arduino Deployment

Gradient Boosting models can be deployed on Arduino, though it's more complex than linear regression:

```cpp
// Simplified example - actual implementation needs tree structures
struct TreeNode {
    int feature_idx;
    float threshold;
    float value;
    TreeNode* left;
    TreeNode* right;
};

float predictETA(float features[8]) {
    float prediction = 0.0;

    // Traverse each of the 200 trees
    for (int tree = 0; tree < 200; tree++) {
        prediction += traverseTree(trees[tree], features);
    }

    return prediction;
}

float traverseTree(TreeNode* node, float features[8]) {
    if (node->left == nullptr) {
        return node->value;  // Leaf node
    }

    if (features[node->feature_idx] <= node->threshold) {
        return traverseTree(node->left, features);
    } else {
        return traverseTree(node->right, features);
    }
}
```

Memory requirements:

- 200 trees × 31 max nodes/tree = 6200 nodes maximum
- Each node: 16 bytes (feature, threshold, value, pointers)
- Total: ~100KB (fits on Arduino Mega, not Uno)

For Arduino Uno (limited memory), consider:

- Reduce to 50-100 trees
- Use model compression techniques
- Or fall back to linear regression

## Troubleshooting

**Problem:** No successful simulations
**Solution:** Check SUMO installation: `sumo --version`

**Problem:** Success rate below 85%
**Solution:** Increase sim_duration in config.yaml to 500

**Problem:** All trains have same speed in plots
**Solution:** Verify generate_train_params() creates different scenarios

**Problem:** Test error > 0.6s for ETA
**Solution:** Increase n_samples to 1500-2000

**Problem:** R² score < 0.85 for ETA
**Solution:** Check that sensor positions are correct and increasing

**Problem:** Training curves diverge (validation gets worse)
**Solution:** Model is overfitting. Reduce max_depth or n_estimators

**Problem:** Matplotlib errors
**Solution:** Install: `pip install matplotlib scikit-learn pandas numpy`

**Problem:** Model file too large for Arduino
**Solution:** Reduce n_estimators to 50-100 or switch to linear regression

## File Structure

```
ml/
├── __init__.py
├── data.py             # Data generation, features, plots
├── model.py            # Training and evaluation
├── network.py          # SUMO network generator
├── config.yaml         # Configuration
└── README.md

outputs/
├── data/
│   ├── raw_trajectories.csv  # Has 'scenario' column
│   └── features.csv           # Has 'scenario' column + 10 features
├── models/
│   ├── eta_model.pkl          # GradientBoosting + scaler + metrics
│   └── etd_model.pkl          # GradientBoosting + scaler + metrics
├── plots/
│   ├── train_trajectories.png     # Shows scenario variety
│   ├── feature_distributions.png
│   ├── feature_correlations.png
│   ├── physics_comparison.png
│   ├── eta_history.png            # Training curves
│   ├── etd_history.png            # Training curves
│   ├── eta_training.png           # Performance plots
│   └── etd_training.png           # Performance plots
└── results/
    └── evaluation_results.json
```

## Model Details

### ETA Model (8 features)

Predicts time until train front reaches crossing.

Input features:

- distance_remaining
- train_length
- last_speed
- speed_change
- time_01
- time_12
- avg_speed_01
- avg_speed_12

Output: Seconds until train arrives

### ETD Model (10 features)

Predicts time until train rear clears crossing.

Input features: All 8 ETA features plus:

- accel_trend: Recent acceleration (m/s²)
- predicted_speed_at_crossing: Extrapolated speed

Output: Seconds until train fully clears

The extra features help ETD model predict how train speed will change between sensor detection and crossing clearance.

## Summary

The ML pipeline:

1. Generates 1000 diverse train scenarios (5 behavior types)
2. Extracts 10 features from sensor data (8 base + 2 for ETD)
3. Creates visualizations showing variety in train behavior
4. Trains Gradient Boosting models (200 trees, depth 5)
5. Achieves 0.3-0.5s prediction accuracy
6. 25-35% improvement over physics baseline
7. Can deploy to Arduino Mega (or compressed to Uno)

Gradient Boosting provides significant improvements over linear regression (0.3s vs 0.5s error) while remaining efficient enough for embedded systems. The key innovation is using ensemble learning to capture non-linear train behavior patterns.
