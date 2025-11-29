"""Train and compare regression models for train ETA prediction."""

import numpy as np
import pandas as pd
import json
import sys
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config


FEATURE_COLS = ['time_0_to_1', 'time_1_to_2', 'speed_0_to_1', 'speed_1_to_2']
REQUIRED_COLS = FEATURE_COLS + ['ETA']
R2_THRESHOLD = 0.95


def load_train_data(filepath):
    """Load and validate training data."""
    df = pd.read_csv(filepath)
    
    for col in REQUIRED_COLS:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    print(f"Loaded {len(df)} data points")
    print(f"Features: {df.columns.tolist()}")
    print("\nData statistics:")
    print(df[REQUIRED_COLS].describe())
    
    print("\nCorrelations with ETA:")
    for col in FEATURE_COLS:
        corr = df[col].corr(df['ETA'])
        print(f"  {col}: {corr:.4f}")
    
    return df


def prepare_features(df):
    """Extract feature matrix and target vector."""
    for col in FEATURE_COLS:
        if col not in df.columns:
            raise ValueError(f"Missing required feature column: {col}")
    
    X = df[FEATURE_COLS].values
    y = df['ETA'].values
    
    print(f"\nFeature matrix shape: {X.shape}")
    print(f"Target vector shape: {y.shape}")
    print(f"Features used: {FEATURE_COLS}")
    
    return X, y


def calculate_metrics(y_true, y_pred):
    """Calculate regression metrics."""
    return {
        'r2': float(r2_score(y_true, y_pred)),
        'mae': float(mean_absolute_error(y_true, y_pred)),
        'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred)))
    }


def train_linear_model(X_train, y_train, X_test, y_test):
    """Train linear regression model."""
    print("\nTraining Linear Regression Model")
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_metrics = calculate_metrics(y_train, y_pred_train)
    test_metrics = calculate_metrics(y_test, y_pred_test)
    
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    
    print(f"  Train R2: {train_metrics['r2']:.4f}")
    print(f"  Test R2: {test_metrics['r2']:.4f}")
    print(f"  Train MAE: {train_metrics['mae']:.4f}s")
    print(f"  Test MAE: {test_metrics['mae']:.4f}s")
    print(f"  Train RMSE: {train_metrics['rmse']:.4f}s")
    print(f"  Test RMSE: {test_metrics['rmse']:.4f}s")
    print(f"  Cross-validation R2: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    coefs = model.coef_
    formula_parts = [f"{model.intercept_:.4f}"]
    formula_parts.extend([f"{coefs[i]:.4f}*{FEATURE_COLS[i][:3]}" 
                         for i in range(len(FEATURE_COLS))])
    
    weights = {
        'intercept': float(model.intercept_),
        'coefficients': coefs.tolist(),
        'feature_names': FEATURE_COLS,
        'formula': f"ETA = {' + '.join(formula_parts)}"
    }
    
    metrics = {
        'train_r2': train_metrics['r2'],
        'test_r2': test_metrics['r2'],
        'train_mae': train_metrics['mae'],
        'test_mae': test_metrics['mae'],
        'train_rmse': train_metrics['rmse'],
        'test_rmse': test_metrics['rmse'],
        'cv_r2_mean': float(cv_scores.mean()),
        'cv_r2_std': float(cv_scores.std())
    }
    
    return model, weights, metrics, y_pred_test


def train_polynomial_model(X_train, y_train, X_test, y_test, degree=2):
    """Train polynomial regression model."""
    print(f"\nTraining Polynomial Regression Model (degree={degree})")
    
    poly = PolynomialFeatures(degree=degree)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)
    
    model = LinearRegression()
    model.fit(X_train_poly, y_train)
    
    y_pred_train = model.predict(X_train_poly)
    y_pred_test = model.predict(X_test_poly)
    
    train_metrics = calculate_metrics(y_train, y_pred_train)
    test_metrics = calculate_metrics(y_test, y_pred_test)
    
    print(f"  Train R2: {train_metrics['r2']:.4f}")
    print(f"  Test R2: {test_metrics['r2']:.4f}")
    print(f"  Train MAE: {train_metrics['mae']:.4f}s")
    print(f"  Test MAE: {test_metrics['mae']:.4f}s")
    print(f"  Train RMSE: {train_metrics['rmse']:.4f}s")
    print(f"  Test RMSE: {test_metrics['rmse']:.4f}s")
    
    feature_names = poly.get_feature_names_out(FEATURE_COLS)
    
    weights = {
        'degree': degree,
        'intercept': float(model.intercept_),
        'coefficients': model.coef_.tolist(),
        'feature_names': feature_names.tolist()
    }
    
    metrics = {
        'train_r2': train_metrics['r2'],
        'test_r2': test_metrics['r2'],
        'train_mae': train_metrics['mae'],
        'test_mae': test_metrics['mae'],
        'train_rmse': train_metrics['rmse'],
        'test_rmse': test_metrics['rmse']
    }
    
    return model, poly, weights, metrics, y_pred_test


def compare_models(linear_metrics, poly2_metrics, poly3_metrics):
    """Compare model performance and identify best model."""
    print("\nMODEL COMPARISON")
    
    models = {
        'Linear': linear_metrics,
        'Polynomial (deg=2)': poly2_metrics,
        'Polynomial (deg=3)': poly3_metrics
    }
    
    print(f"\n{'Model':<20} {'Test R2':<12} {'Test MAE':<12} {'Test RMSE':<12}")
    print("-" * 60)
    
    best_model = None
    best_score = -float('inf')
    
    for name, metrics in models.items():
        test_r2 = metrics['test_r2']
        test_mae = metrics['test_mae']
        test_rmse = metrics['test_rmse']
        
        print(f"{name:<20} {test_r2:<12.4f} {test_mae:<12.4f} {test_rmse:<12.4f}")
        
        if test_r2 > best_score:
            best_score = test_r2
            best_model = name
    
    print("-" * 60)
    print(f"\nBest Model: {best_model} (R2 = {best_score:.4f})")
    
    if best_score < R2_THRESHOLD:
        print(f"WARNING: Best model R2 ({best_score:.4f}) is below target threshold ({R2_THRESHOLD})")
    else:
        print(f"SUCCESS: Best model meets R2 threshold (>= {R2_THRESHOLD})")
    
    return best_model


def plot_predictions(y_test, y_pred_linear, y_pred_poly2, y_pred_poly3, output_dir=None):
    """Generate comparison plots for all models."""
    if output_dir is None:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(module_dir, 'plots')
    
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    models = [
        ('Linear', y_pred_linear),
        ('Polynomial (deg=2)', y_pred_poly2),
        ('Polynomial (deg=3)', y_pred_poly3)
    ]
    
    for ax, (name, y_pred) in zip(axes, models):
        ax.scatter(y_test, y_pred, alpha=0.5, s=20)
        ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
                'r--', lw=2)
        ax.set_xlabel('Actual ETA (s)')
        ax.set_ylabel('Predicted ETA (s)')
        ax.set_title(f'{name}\nR2 = {r2_score(y_test, y_pred):.4f}')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'model_comparison.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved comparison plot to {output_path}")
    plt.close()


def save_model_weights(linear_weights, poly2_weights, poly3_weights, output_dir=None):
    """Save model weights to JSON files."""
    if output_dir is None:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(module_dir, 'models')
    
    os.makedirs(output_dir, exist_ok=True)
    
    weights_map = {
        'linear_weights.json': linear_weights,
        'poly2_weights.json': poly2_weights,
        'poly3_weights.json': poly3_weights
    }
    
    for filename, weights in weights_map.items():
        with open(os.path.join(output_dir, filename), 'w') as f:
            json.dump(weights, f, indent=2)
    
    print(f"\nSaved model weights to {output_dir}/")


def generate_arduino_code(weights, model_type, output_dir=None):
    """Generate Arduino-compatible C++ header file for model."""
    if output_dir is None:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(module_dir, 'models')
    
    os.makedirs(output_dir, exist_ok=True)
    
    if model_type == 'linear':
        code = _generate_linear_code(weights)
    else:
        code = _generate_polynomial_code(weights)
    
    output_path = os.path.join(output_dir, 'eta_model.h')
    with open(output_path, 'w') as f:
        f.write(code)
    
    print(f"Generated Arduino code: {output_path}")


def _generate_linear_code(weights):
    """Generate linear model Arduino code."""
    return f"""// Linear Regression Model for ETA Prediction
// Formula: ETA = intercept + c1*time_0_to_1 + c2*time_1_to_2 + c3*speed_0_to_1 + c4*speed_1_to_2

const float INTERCEPT = {weights['intercept']:.6f};
const float COEF_TIME_0_TO_1 = {weights['coefficients'][0]:.6f};
const float COEF_TIME_1_TO_2 = {weights['coefficients'][1]:.6f};
const float COEF_SPEED_0_TO_1 = {weights['coefficients'][2]:.6f};
const float COEF_SPEED_1_TO_2 = {weights['coefficients'][3]:.6f};

float predictETA(float time_0_to_1, float time_1_to_2, float speed_0_to_1, float speed_1_to_2) {{
    return INTERCEPT 
        + COEF_TIME_0_TO_1 * time_0_to_1 
        + COEF_TIME_1_TO_2 * time_1_to_2 
        + COEF_SPEED_0_TO_1 * speed_0_to_1 
        + COEF_SPEED_1_TO_2 * speed_1_to_2;
}}
"""


def _generate_polynomial_code(weights):
    """Generate polynomial model Arduino code."""
    degree = weights['degree']
    coefs = weights['coefficients']
    intercept = weights['intercept']
    
    code = f"""// Polynomial Regression Model (degree={degree}) for ETA Prediction

const float INTERCEPT = {intercept:.6f};
const float COEFFICIENTS[] = {{
"""
    for i, c in enumerate(coefs):
        code += f"    {c:.6f}{',' if i < len(coefs)-1 else ''}\n"
    
    code += f"""}};
const int NUM_COEFFICIENTS = {len(coefs)};

float predictETA(float time_0_to_1, float time_1_to_2, float speed_0_to_1, float speed_1_to_2) {{
    float features[NUM_COEFFICIENTS];
    int idx = 0;
    
    features[idx++] = 1.0;
"""
    
    if degree >= 1:
        code += """    features[idx++] = time_0_to_1;
    features[idx++] = time_1_to_2;
    features[idx++] = speed_0_to_1;
    features[idx++] = speed_1_to_2;
"""
    
    if degree >= 2:
        code += """    features[idx++] = time_0_to_1 * time_0_to_1;
    features[idx++] = time_0_to_1 * time_1_to_2;
    features[idx++] = time_0_to_1 * speed_0_to_1;
    features[idx++] = time_0_to_1 * speed_1_to_2;
    features[idx++] = time_1_to_2 * time_1_to_2;
    features[idx++] = time_1_to_2 * speed_0_to_1;
    features[idx++] = time_1_to_2 * speed_1_to_2;
    features[idx++] = speed_0_to_1 * speed_0_to_1;
    features[idx++] = speed_0_to_1 * speed_1_to_2;
    features[idx++] = speed_1_to_2 * speed_1_to_2;
"""
    
    if degree >= 3:
        code += """    // Third degree polynomial features
    features[idx++] = time_0_to_1 * time_0_to_1 * time_0_to_1;
    features[idx++] = time_0_to_1 * time_0_to_1 * time_1_to_2;
    features[idx++] = time_0_to_1 * time_0_to_1 * speed_0_to_1;
    features[idx++] = time_0_to_1 * time_0_to_1 * speed_1_to_2;
    features[idx++] = time_0_to_1 * time_1_to_2 * time_1_to_2;
    features[idx++] = time_0_to_1 * time_1_to_2 * speed_0_to_1;
    features[idx++] = time_0_to_1 * time_1_to_2 * speed_1_to_2;
    features[idx++] = time_0_to_1 * speed_0_to_1 * speed_0_to_1;
    features[idx++] = time_0_to_1 * speed_0_to_1 * speed_1_to_2;
    features[idx++] = time_0_to_1 * speed_1_to_2 * speed_1_to_2;
    features[idx++] = time_1_to_2 * time_1_to_2 * time_1_to_2;
    features[idx++] = time_1_to_2 * time_1_to_2 * speed_0_to_1;
    features[idx++] = time_1_to_2 * time_1_to_2 * speed_1_to_2;
    features[idx++] = time_1_to_2 * speed_0_to_1 * speed_0_to_1;
    features[idx++] = time_1_to_2 * speed_0_to_1 * speed_1_to_2;
    features[idx++] = time_1_to_2 * speed_1_to_2 * speed_1_to_2;
    features[idx++] = speed_0_to_1 * speed_0_to_1 * speed_0_to_1;
    features[idx++] = speed_0_to_1 * speed_0_to_1 * speed_1_to_2;
    features[idx++] = speed_0_to_1 * speed_1_to_2 * speed_1_to_2;
    features[idx++] = speed_1_to_2 * speed_1_to_2 * speed_1_to_2;
"""
    
    code += """    
    float eta = INTERCEPT;
    for (int i = 0; i < idx; i++) {
        eta += COEFFICIENTS[i] * features[i];
    }
    
    return eta;
}
"""
    
    return code


def main():
    """Main training pipeline."""
    config = get_scale_config()
    scale_mode = config['scale_mode']
    
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    else:
        train_dataset_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            '02_train', 
            'data'
        )
        data_file = os.path.join(train_dataset_dir, 'train_data.csv')
    
    print(f"Scale mode: {scale_mode}")
    print(f"Loading data from: {data_file}\n")
    
    df = load_train_data(data_file)
    X, y = prepare_features(df)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    linear_model, linear_weights, linear_metrics, y_pred_linear = train_linear_model(
        X_train, y_train, X_test, y_test
    )
    
    poly2_model, poly2_features, poly2_weights, poly2_metrics, y_pred_poly2 = train_polynomial_model(
        X_train, y_train, X_test, y_test, degree=2
    )
    
    poly3_model, poly3_features, poly3_weights, poly3_metrics, y_pred_poly3 = train_polynomial_model(
        X_train, y_train, X_test, y_test, degree=3
    )
    
    best_model = compare_models(linear_metrics, poly2_metrics, poly3_metrics)
    
    save_model_weights(linear_weights, poly2_weights, poly3_weights)
    plot_predictions(y_test, y_pred_linear, y_pred_poly2, y_pred_poly3)
    
    if 'Linear' in best_model:
        generate_arduino_code(linear_weights, 'linear')
    elif 'deg=2' in best_model:
        generate_arduino_code(poly2_weights, 'poly2')
    else:
        generate_arduino_code(poly3_weights, 'poly3')
    
    print("\nTraining complete!")


if __name__ == "__main__":
    main()