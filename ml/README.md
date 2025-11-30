# Machine Learning Module

ETA prediction model for railway level crossing system.

## Files

```
ml/
├── eta_predictor.py              # ML model training and prediction
├── models/
│   └── eta_predictor.pkl         # Trained model (generated)
└── README.md                     # This file
```

## Purpose

The ML model predicts accurate train ETA by learning from sensor timing patterns. It's more accurate than simple physics calculations because it accounts for:

- Train acceleration/deceleration patterns
- Different train types and behaviors
- Real-world measurement variations
- Non-linear dynamics

## Model Architecture

**Type:** Random Forest Regressor (not classification!)

**Features (6):**

1. `time_0_to_1` - Time between sensors 0→1 (seconds)
2. `time_1_to_2` - Time between sensors 1→2 (seconds)
3. `speed_0_to_1` - Calculated speed at first segment (m/s)
4. `speed_1_to_2` - Calculated speed at second segment (m/s)
5. `acceleration` - Train acceleration (m/s²)
6. `distance_remaining` - Distance from sensor 2 to crossing (m)

**Output:** Continuous ETA value (seconds)

**Hyperparameters:**

- n_estimators: 100 trees
- max_depth: 15
- min_samples_split: 5

## Training

### Generate Training Data

```bash
make data-train
```

This creates `data_generation/data/train_approaches.csv` with ~100 scenarios.

### Train Model

```bash
make ml-train
```

Expected output:

```
Training ETA Predictor on: data_generation/data/train_approaches.csv
Training samples: 80
Test samples: 20

Training Performance:
  MAE: 0.156s
  RMSE: 0.234s
  R²: 0.9876

Test Performance:
  MAE: 1.234s
  RMSE: 1.567s
  R²: 0.9234

✓ Model meets accuracy requirements
  - MAE < 2.0s
  - R² > 0.90

Model saved: ml/models/eta_predictor.pkl
```

### Test Model

```bash
make ml-test
```

## Usage in Python

### Load and Predict

```python
from ml.eta_predictor import ETAPredictor

# Load trained model
predictor = ETAPredictor('ml/models/eta_predictor.pkl')

# Make prediction
result = predictor.predict(
    time_0_to_1=8.5,      # seconds
    time_1_to_2=6.2,      # seconds
    speed_0_to_1=25.5,    # m/s
    speed_1_to_2=28.3,    # m/s
    acceleration=0.45,    # m/s²
    distance_remaining=81 # meters
)

print(result)
# {
#     'eta_predicted': 12.5,
#     'confidence': 0.923,
#     'std_dev': 0.084
# }
```

### Compare with Physics

```python
physics_eta = 15.2  # seconds from physics calculation

comparison = predictor.compare_with_physics(
    sensor_data={
        'time_0_to_1': 8.5,
        'time_1_to_2': 6.2,
        'speed_0_to_1': 25.5,
        'speed_1_to_2': 28.3,
        'acceleration': 0.45,
        'distance_remaining': 81
    },
    physics_eta=physics_eta
)

print(comparison)
# {
#     'physics_eta': 15.2,
#     'ml_eta': 12.5,
#     'difference': 2.7,
#     'ml_confidence': 0.923,
#     'better_accuracy': 'ML'
# }
```

## Export to Arduino

### Full Process

```bash
# 1. Train model
make ml-train

# 2. Export to Arduino
make ml-export

# 3. Choose option
# Option 1: Simplified Decision Tree (recommended)
# Option 2: Linear Regression (smallest)

# 4. Copy arduino/eta_model.h to sketch
```

### What Gets Exported

The export script converts the Random Forest to a simplified version that fits on Arduino:

**Decision Tree (recommended):**

- Accuracy: Good (~1-2s error)
- Memory: 1-3KB
- Speed: Fast

**Linear Regression (smallest):**

- Accuracy: Acceptable (~2-3s error)
- Memory: ~100 bytes
- Speed: Very fast

## Model Performance

### Target Metrics

- **MAE < 2.0s**: Mean Absolute Error
- **RMSE < 3.0s**: Root Mean Square Error
- **R² > 0.90**: Coefficient of determination
- **Confidence > 0.85**: Prediction confidence

### Feature Importance

Typical importance ranking:

1. `speed_1_to_2` (35%) - Most recent speed
2. `distance_remaining` (25%) - How far to go
3. `acceleration` (20%) - Is train speeding up/down
4. `time_1_to_2` (10%) - Recent timing
5. `speed_0_to_1` (7%) - Earlier speed
6. `time_0_to_1` (3%) - Earlier timing

## Why Regression?

**Question:** Why Random Forest Regressor instead of classifier?

**Answer:** ETA is a **continuous value** (5.3s, 12.7s, 18.2s), not categories.

| Task           | Model Type      | Output                   |
| -------------- | --------------- | ------------------------ |
| ETA Prediction | **Regressor** ✓ | 12.5 seconds             |
| Train Type     | Classifier      | "passenger" or "freight" |
| Risk Level     | Classifier      | "low", "medium", "high"  |

**Our choice:**

- `RandomForestRegressor` - predicts numbers
- NOT `RandomForestClassifier` - predicts categories

## Improving Accuracy

### 1. More Training Data

```bash
# Generate 500 scenarios instead of 100
python -m data_generation.generate_train 500
make ml-train
```

### 2. Better Features

Add more informative features:

- Weather conditions
- Train type (passenger/freight)
- Track grade
- Time of day

### 3. Tune Hyperparameters

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [10, 15, 20],
    'min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(
    RandomForestRegressor(),
    param_grid,
    cv=5,
    scoring='neg_mean_absolute_error'
)

grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
```

## Troubleshooting

### Model Not Found

```
ERROR: Model not found at ml/models/eta_predictor.pkl
```

**Solution:** Train the model first

```bash
make ml-train
```

### Low Accuracy

```
WARNING: Model accuracy too low
  MAE: 3.5s (target < 2.0s)
```

**Solutions:**

1. Generate more training data
2. Check sensor positions match config
3. Verify training data quality
4. Try different hyperparameters

### Import Errors

```
ModuleNotFoundError: No module named 'sklearn'
```

**Solution:** Install dependencies

```bash
pip install -r requirements.txt
```

### Overfitting

```
Train MAE: 0.1s
Test MAE: 5.0s  (much worse!)
```

**Solutions:**

1. Reduce `max_depth` (try 10 instead of 15)
2. Increase `min_samples_split` (try 10)
3. Add more diverse training data

## Integration Points

### 1. Hardware (Arduino)

```cpp
// In sketch.ino after export
float features[6] = {t01, t12, s01, s12, acc, dist};
float eta = predictETA(features);
```

### 2. Simulation (Python)

```python
# In simulation/main.py
from ml.eta_predictor import ETAPredictor

predictor = ETAPredictor('ml/models/eta_predictor.pkl')
result = predictor.predict(...)
```

### 3. Arduino Bridge (Serial)

```python
# In arduino/arduino_bridge.py
from ml.eta_predictor import ETAPredictor

bridge = ArduinoBridge(port)
# Automatically uses ML predictor if available
bridge.run()
```

## File Structure

```
ml/
├── eta_predictor.py
│   ├── ETAPredictor class
│   │   ├── train()          # Train on CSV data
│   │   ├── predict()        # Make single prediction
│   │   ├── save_model()     # Save to .pkl
│   │   └── load_model()     # Load from .pkl
│   └── train_eta_model()    # CLI function
│
├── models/
│   └── eta_predictor.pkl    # Trained model (binary)
│
└── README.md                # This file
```

## Next Steps

1. ✅ Generate training data: `make data-train`
2. ✅ Train model: `make ml-train`
3. ✅ Test accuracy: `make ml-test`
4. ✅ Export to Arduino: `make ml-export`
5. ✅ Deploy to hardware

## References

- Scikit-learn Random Forest: https://scikit-learn.org/stable/modules/ensemble.html#forest
- Regression vs Classification: https://scikit-learn.org/stable/supervised_learning.html
- Model Export: See `arduino/export_model_to_arduino.py`
