# Machine Learning Module

Trains AI models to predict when trains will arrive at and leave railway crossings.

## What It Does

Uses 1000 simulated trains to teach two models:

- **ETA Model**: Predicts when train front reaches crossing (8 features)
- **ETD Model**: Predicts when train rear clears crossing (10 features)

**Performance**: 0.3-0.5 second accuracy, 25-35% better than simple physics calculations.

## How It Works

### 1. Generate Training Data

Simulates 1000 trains with realistic behavior:

| Type         | Speed (m/s) | Behavior        |
| ------------ | ----------- | --------------- |
| Fast         | 40-48       | Express trains  |
| Moderate     | 30-40       | Regular freight |
| Slow         | 20-32       | Heavy loads     |
| Accelerating | 25-35       | Speeding up     |
| Decelerating | 35-45       | Slowing down    |

**Track Layout**:

```
Sensor 0 (1500m) -> Sensor 1 (1000m) -> Sensor 2 (800m) -> Crossing (3000m)
```

Sensors must be in descending order: s0 >= s1 >= s2

### 2. Extract Features

From 3 sensor readings, calculates:

**Base Features (both models)**:

1. distance_remaining: Meters to crossing
2. train_length: 100, 150, 200, or 250m
3. last_speed: Speed at sensor 2
4. speed_change: Speed difference s0 to s2
5. time_01: Transit time s0 to s1
6. time_12: Transit time s1 to s2
7. avg_speed_01: Average speed s0 to s1
8. avg_speed_12: Average speed s1 to s2

**Extended Features (ETD only)**: 9. accel_trend: Recent acceleration 10. predicted_speed_at_crossing: Estimated future speed

### 3. Train Models

Uses Gradient Boosting:

- 200 decision trees working together
- Each tree corrects previous tree's mistakes
- Learns patterns simple physics can't capture

**Why Gradient Boosting?**

- Handles non-linear patterns (trains don't move at constant speed)
- Captures interactions (speed x distance effects)
- More accurate than linear regression
- Can run on Arduino after compression

### 4. Evaluate Performance

**Metrics**:

- MAE (Mean Absolute Error): Average prediction error
- RMSE: Penalizes large errors more
- R2 Score: How well model explains variance (0-1, higher better)
- Confidence Intervals: Error range with 95% certainty

**Expected Results**:

ETA Model: 0.30-0.40s error, R2 = 0.92-0.96
ETD Model: 0.40-0.50s error, R2 = 0.88-0.93

## Usage

### Full Pipeline

```bash
make ml-pipeline
```

Runs complete workflow (10 minutes):

1. Generate 1000 train simulations
2. Extract features
3. Train both models
4. Create visualizations

### Quick Test

```bash
make ml-quick
```

50 samples in 30 seconds for testing.

### Manual Steps

```bash
python -m ml.data              # Generate data
python -m ml.model             # Train models

python -m ml.data --samples 500    # Custom sample count
```

## Configuration

Edit `ml/config.yaml`:

```yaml
network:
  track_length: 4000
  max_speed: 50.0

sensors:
  s0: 1500 # Must be descending order
  s1: 1000
  s2: 800
  crossing: 3000

training:
  n_samples: 1000
  sim_duration: 400
  random_seed: 42

model:
  test_size: 0.2
  hyperparameters:
    n_estimators: 200
    learning_rate: 0.05
    max_depth: 4 # Shallow trees prevent overfitting
```

**Common Changes**:

| Goal              | Parameter | Change           |
| ----------------- | --------- | ---------------- |
| More accuracy     | n_samples | 1000 -> 2000     |
| Faster testing    | n_samples | 1000 -> 100      |
| Different sensors | sensors   | Change positions |

**Important**: Always maintain s0 >= s1 >= s2

## Outputs

```
outputs/
├── data/
│   ├── raw_trajectories.csv      # Simulation data
│   └── features.csv               # Extracted features
├── models/
│   ├── eta_model.pkl              # Trained ETA model
│   └── etd_model.pkl              # Trained ETD model
├── plots/
│   ├── train_trajectories.png     # Sample train paths
│   ├── feature_distributions.png  # Feature histograms
│   ├── feature_correlations.png   # Feature vs ETA plots
│   ├── physics_comparison.png     # Physics baseline
│   ├── eta_history.png            # Training curves
│   ├── etd_history.png            # Training curves
│   ├── eta_comprehensive.png      # 9-panel evaluation
│   └── etd_comprehensive.png      # 9-panel evaluation
└── results/
    └── evaluation_results.json    # All metrics
```

### Key Plots

**train_trajectories.png**: Shows how different trains move differently

**feature_distributions.png**: Shows range and spread of input data

**eta_comprehensive.png**: 9 panels showing:

1. Training predictions vs actual
2. Test predictions vs actual (main result)
3. Error distribution (should be bell-shaped)
4. Feature importance (which sensors matter most)
5. ML vs Physics comparison
6. Residuals (checks for missed patterns)
7. Cross-validation stability
8. Q-Q plot (checks error distribution)
9. Metrics summary table

## Troubleshooting

### Sensor Order Error

```
ValueError: Sensor positions must be in descending order
```

**Fix**: Edit `ml/config.yaml` so s0 >= s1 >= s2

### Integration with Thresholds

1. Run thresholds first: `make th-pipeline`
2. Copy sensor positions from `outputs/results/thresholds.yaml`
3. Update `ml/config.yaml` sensors section
4. Run ML pipeline: `make ml-pipeline`

### Poor Accuracy

If test MAE > 0.6s:

- Check n_samples (should be 500-1000+)
- Verify sensor positions are reasonable (100-2000m spacing)
- Ensure varied train speeds in simulation

## Technical Details

**Algorithm**: Gradient Boosting Regressor

Builds 200 trees sequentially where each corrects previous errors:

```
Prediction = tree1 + tree2 + ... + tree200
```

**Hyperparameters**:

- n_estimators: 200 (number of trees)
- learning_rate: 0.05 (step size)
- max_depth: 4 (tree depth, prevents overfitting)
- subsample: 0.9 (use 90% of data per tree)

**Data Split**: 64% train, 16% validation, 20% test

**Why This Works**:

- Simple physics assumes constant speed: time = distance / speed
- Real trains accelerate and decelerate
- ML learns these patterns from 1000 examples
- Results in 30% better predictions

## Feature Importance

**ETA Model** (most important first):

1. last_speed (35%)
2. avg_speed_12 (22%)
3. distance_remaining (15%)

**ETD Model**:

1. last_speed (30%)
2. predicted_speed_at_crossing (20%)
3. train_length (15%)

Current speed is most predictive for both models.

## Files

- `data.py`: Generate simulations and extract features
- `model.py`: Train and evaluate models
- `network.py`: Create SUMO track network
- `config.yaml`: All settings
- `__init__.py`: Module exports
