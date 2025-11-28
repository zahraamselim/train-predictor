"""
Train ML models to predict ETA from IR sensor readings.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import json
import matplotlib.pyplot as plt


def load_data(csv_file: str):
    """Load and prepare training data."""
    df = pd.read_csv(csv_file)
    
    # Features: IR sensor readings
    X = df[['IR1_400m', 'IR2_250m', 'IR3_100m']].values
    
    # Target: ETA
    y = df['ETA'].values
    
    # Only use data where train is approaching (ETA > 0)
    mask = y > 0
    X = X[mask]
    y = y[mask]
    
    return X, y, df


def train_linear_model(X_train, y_train):
    """Train linear regression model."""
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model


def train_polynomial_model(X_train, y_train, degree=2):
    """Train polynomial regression model."""
    model = Pipeline([
        ('poly', PolynomialFeatures(degree=degree)),
        ('linear', LinearRegression())
    ])
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate model performance."""
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n{model_name} Performance:")
    print(f"  R² Score: {r2:.4f}")
    print(f"  MAE: {mae:.2f} seconds")
    print(f"  RMSE: {rmse:.2f} seconds")
    
    return {'mae': mae, 'rmse': rmse, 'r2': r2, 'predictions': y_pred}


def plot_predictions(y_test, predictions, model_names, output_file='model_comparison.png'):
    """Plot predicted vs actual ETA."""
    fig, axes = plt.subplots(1, len(predictions), figsize=(15, 5))
    
    if len(predictions) == 1:
        axes = [axes]
    
    for idx, (name, y_pred) in enumerate(predictions.items()):
        ax = axes[idx]
        ax.scatter(y_test, y_pred, alpha=0.5, s=10)
        ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
                'r--', lw=2, label='Perfect prediction')
        ax.set_xlabel('Actual ETA (s)')
        ax.set_ylabel('Predicted ETA (s)')
        ax.set_title(name)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    print(f"\nPrediction plot saved to: {output_file}")


def save_model_weights(model, model_name, output_file):
    """Save model weights for Arduino deployment."""
    if model_name == 'Linear':
        weights = {
            'model_type': 'linear',
            'intercept': float(model.intercept_),
            'coefficients': model.coef_.tolist()
        }
    else:
        linear_model = model.named_steps['linear']
        weights = {
            'model_type': 'polynomial',
            'degree': model.named_steps['poly'].degree,
            'intercept': float(linear_model.intercept_),
            'coefficients': linear_model.coef_.tolist()
        }
    
    with open(output_file, 'w') as f:
        json.dump(weights, f, indent=2)
    
    print(f"Model weights saved to: {output_file}")


def cross_validate_model(model, X, y, cv=5):
    """Perform cross-validation."""
    scores = cross_val_score(model, X, y, cv=cv, 
                            scoring='neg_mean_absolute_error')
    return -scores.mean(), scores.std()


def main(csv_file='train_data.csv'):
    """Main training pipeline."""
    print("Loading data...")
    X, y, df = load_data(csv_file)
    
    print(f"Dataset: {len(X)} samples")
    print(f"ETA range: {y.min():.1f}s to {y.max():.1f}s")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train models
    print("\nTraining Linear Regression...")
    linear_model = train_linear_model(X_train, y_train)
    
    print("Training Polynomial Regression (degree 2)...")
    poly2_model = train_polynomial_model(X_train, y_train, degree=2)
    
    print("Training Polynomial Regression (degree 3)...")
    poly3_model = train_polynomial_model(X_train, y_train, degree=3)
    
    # Evaluate models
    results = {}
    predictions = {}
    
    result = evaluate_model(linear_model, X_test, y_test, "Linear Regression")
    results['Linear'] = result
    predictions['Linear'] = result['predictions']
    
    result = evaluate_model(poly2_model, X_test, y_test, "Polynomial (degree 2)")
    results['Poly2'] = result
    predictions['Poly2'] = result['predictions']
    
    result = evaluate_model(poly3_model, X_test, y_test, "Polynomial (degree 3)")
    results['Poly3'] = result
    predictions['Poly3'] = result['predictions']
    
    # Cross-validation
    print("\nCross-Validation (5-fold):")
    for name, model in [('Linear', linear_model), 
                        ('Poly2', poly2_model), 
                        ('Poly3', poly3_model)]:
        cv_mae, cv_std = cross_validate_model(model, X_train, y_train)
        print(f"  {name}: MAE = {cv_mae:.2f} ± {cv_std:.2f}s")
    
    # Select best model
    best_model_name = min(results, key=lambda k: results[k]['mae'])
    best_model = {
        'Linear': linear_model,
        'Poly2': poly2_model,
        'Poly3': poly3_model
    }[best_model_name]
    
    print(f"\nBest model: {best_model_name}")
    print(f"  R² = {results[best_model_name]['r2']:.4f}")
    print(f"  MAE = {results[best_model_name]['mae']:.2f}s")
    
    # Save best model
    save_model_weights(best_model, best_model_name, 'best_model_weights.json')
    
    # Plot results
    plot_predictions(y_test, predictions, list(predictions.keys()))
    
    return best_model, results


if __name__ == "__main__":
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'train_data.csv'
    main(csv_file)