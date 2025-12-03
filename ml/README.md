# Machine Learning Pipeline

## Overview

This pipeline trains AI models to predict train arrival (ETA) and departure (ETD) times at railroad crossings. The system learns from thousands of simulated train examples to make predictions more accurate than simple physics formulas.

## Why Machine Learning

Simple physics predicts: `time = distance / speed`

But real trains:

- Accelerate and decelerate
- Have varying lengths
- Behave unpredictably

Machine learning learns these patterns from data.

## Pipeline Components

### 1. Data Preparation (`data.py`)

Handles data generation, feature extraction, and visualization in one module.

**Data Generation:**

- Simulates 1000 trains using SUMO
- Random speeds: 15-45 m/s
- Random accelerations: 0.5-2.0 m/s²
- Random lengths: 100, 150, 200, 250 meters
- Records position, speed, acceleration every 0.1 seconds

**Feature Extraction:**

- 3 sensors before crossing (1500m, 2100m, 2550m)
- Crossing at 3000m
- Extracts 8 features per train:
  - distance_remaining: Meters from last sensor to crossing
  - train_length: Length in meters
  - last_speed: Speed at last sensor
  - speed_change: Speed difference between first and last sensor
  - time_01: Time between sensors 0 and 1
  - time_12: Time between sensors 1 and 2
  - avg_speed_01: Average speed between sensors 0-1
  - avg_speed_12: Average speed between sensors 1-2

**Visualization:**
Creates 4 plot files:

- train_trajectories.png: Sample train movements
- feature_distributions.png: Feature histograms
- feature_correlations.png: Feature-ETA relationships
- physics_comparison.png: ML vs simple physics

**Outputs:**

- `outputs/data/raw_trajectories.csv`: Raw simulation data
- `outputs/data/features.csv`: Extracted features
- `outputs/plots/`: Visualization images

### 2. Model Training (`model.py`)

Trains and evaluates Linear Regression models for ETA and ETD.

**Linear Regression:**
Finds the best formula:

```
ETA = a × distance + b × speed + c × length + ... + constant
```

**Training Process:**

1. Split data: 80% training, 20% testing
2. Train model (learns coefficients)
3. Evaluate on test data
4. Generate performance plots
5. Save model and metrics

**Performance Metrics:**

- MAE (Mean Absolute Error): Average prediction error in seconds
- R² Score: How well model explains data (0-1, higher better)
- Improvement: Percentage better than physics baseline

**Outputs:**

- `outputs/models/eta_model.pkl`: ETA model
- `outputs/models/etd_model.pkl`: ETD model
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
python -m ml.data --config custom_config.yaml --samples 500
python -m ml.model --config custom_config.yaml
```

## Expected Results

**ETA Model:**

- Test error: 0.4-0.5 seconds
- R² score: 0.85-0.90
- Improvement over physics: 10-15%

**ETD Model:**

- Test error: 0.5-0.6 seconds
- R² score: 0.82-0.88
- Improvement over physics: 8-12%

## Understanding the Outputs

### Trajectory Plots

Shows 6 sample trains moving through sensors. Each subplot shows:

- Position over time
- Speed over time
- Acceleration over time
- Speed vs position

Use these to verify trains behave realistically.

### Feature Distribution Plots

Histograms of all 8 features plus targets. Look for:

- Wide spread (good variety)
- Bell-shaped curves (normal distribution)
- No unusual spikes or gaps

### Feature Correlation Plots

Shows how each feature relates to ETA. Correlation values:

- +1.0: Perfect positive correlation
- 0.0: No relationship
- -1.0: Perfect negative correlation

Examples:

- last_speed: negative correlation (higher speed = shorter time)
- distance_remaining: positive correlation (more distance = more time)

### Physics Comparison Plots

Compares simple physics to actual times. Spread from diagonal line shows physics error (~0.5s).

### Training Performance Plots

6 subplots per model:

1. Training predictions vs actual
2. Test predictions vs actual (most important)
3. Error distribution (should be bell-shaped)
4. Feature importance (coefficient sizes)
5. Performance comparison (ML vs physics)
6. Residuals (should be random scatter)

Good signs:

- Points near diagonal in prediction plots
- Bell-shaped error distribution
- Test performance close to training
- Random residuals

Bad signs:

- Points far from diagonal
- Test much worse than training (overfitting)
- Patterns in residuals (missing information)

## Configuration

Edit `config/ml.yaml`:

```yaml
network:
  start_x: -2000
  end_x: 2000
  max_speed: 50.0
  track_length: 4000

sensors:
  s0: 1500
  s1: 2100
  s2: 2550
  crossing: 3000

training:
  n_samples: 1000
  sim_duration: 300
  random_seed: 42
  train_params:
    lengths: [100, 150, 200, 250]

model:
  type: linear_regression
  test_size: 0.2
```

Adjustments:

- More accuracy: Increase n_samples to 2000
- Faster testing: Decrease n_samples to 100
- Different sensors: Change sensor positions

## Failed Experiments

### Experiment 1: 100 Training Samples

**Result:** Poor accuracy

- ETA error: 0.8s
- R² score: 0.65

**Lesson:** Need 500-1000 samples minimum.

### Experiment 2: Only 2 Features

**Result:** Only 8% improvement over physics

- Missing information about train behavior

**Lesson:** Need multiple sensor measurements.

### Experiment 3: Polynomial Features

**Result:** Overfitting

- Training error: 0.1s (great)
- Test error: 0.9s (terrible)
- Model memorized instead of learned

**Lesson:** Keep it simple, linear works fine.

### Experiment 4: ETD from ETA

**Result:** ETD error 0.9s

- Speed changes between arrival and clearance

**Lesson:** Train separate models for ETA and ETD.

## Arduino Deployment

Linear regression converts to simple C code:

```cpp
float predictETA(float features[8]) {
    float eta = 5.234;  // Intercept
    eta += features[0] * 0.0287;   // distance_remaining
    eta += features[1] * 0.0123;   // train_length
    eta += features[2] * -0.1456;  // last_speed
    eta += features[3] * -0.0678;  // speed_change
    eta += features[4] * 0.0891;   // time_01
    eta += features[5] * 0.0734;   // time_12
    eta += features[6] * -0.1234;  // avg_speed_01
    eta += features[7] * -0.1156;  // avg_speed_12
    return eta;
}
```

Only 8 multiplications and 8 additions. Runs in microseconds on Arduino.

## Troubleshooting

**Problem:** No successful simulations
**Solution:** Check SUMO installation: `sumo --version`

**Problem:** Test error > 0.8s
**Solution:** Increase n_samples to 1500-2000

**Problem:** R² score < 0.75
**Solution:** Check sensor positions, verify data quality

**Problem:** Plots show patterns in residuals
**Solution:** May need additional features or non-linear model

**Problem:** Matplotlib errors
**Solution:** Install: `pip install matplotlib`

## File Structure

```
ml/
├── __init__.py
├── data.py             # Data generation, features, plots
├── model.py            # Training and evaluation
└── README.md

outputs/
├── data/
│   ├── raw_trajectories.csv
│   └── features.csv
├── models/
│   ├── eta_model.pkl
│   └── etd_model.pkl
├── plots/
│   ├── train_trajectories.png
│   ├── feature_distributions.png
│   ├── feature_correlations.png
│   ├── physics_comparison.png
│   ├── eta_training.png
│   └── etd_training.png
└── results/
    └── evaluation_results.json
```

## Summary

The ML pipeline:

1. Generates 1000 diverse train scenarios
2. Extracts 8 features from sensor data
3. Creates visualizations for data understanding
4. Trains simple linear regression models
5. Achieves 0.4-0.5s prediction accuracy
6. Deploys as lightweight Arduino code

Linear regression provides the simplest possible ML model while achieving significant improvements over physics baselines.
