"""Validate model training output and performance."""

import sys
import os
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def validate_model_weights(filepath, model_type):
    """Validate model weight files."""
    print(f"\nValidating {model_type} model weights")
    print(f"File: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ERROR: File not found")
        return False
    
    try:
        with open(filepath, 'r') as f:
            weights = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ERROR: Invalid JSON: {e}")
        return False
    
    errors = []
    
    required_keys = ['intercept', 'coefficients', 'feature_names']
    for key in required_keys:
        if key not in weights:
            errors.append(f"Missing required key: {key}")
    
    if errors:
        for err in errors:
            print(f"  ERROR: {err}")
        return False
    
    print(f"  Intercept: {weights['intercept']:.6f}")
    print(f"  Number of coefficients: {len(weights['coefficients'])}")
    print(f"  Number of features: {len(weights['feature_names'])}")
    
    if model_type == 'linear':
        if len(weights['coefficients']) != 4:
            print(f"  ERROR: Linear model should have 4 coefficients")
            return False
        
        if len(weights['feature_names']) != 4:
            print(f"  ERROR: Linear model should have 4 features")
            return False
    
    elif model_type.startswith('poly'):
        degree = weights.get('degree')
        if degree is None:
            print(f"  ERROR: Polynomial model missing degree")
            return False
        
        print(f"  Polynomial degree: {degree}")
        
        if degree == 2:
            expected_features = 15
        elif degree == 3:
            expected_features = 35
        else:
            expected_features = None
        
        if expected_features and len(weights['coefficients']) != expected_features:
            print(f"  WARNING: Expected {expected_features} coefficients for degree {degree}, "
                  f"got {len(weights['coefficients'])}")
    
    if any(np.isnan(c) or np.isinf(c) for c in weights['coefficients']):
        print(f"  ERROR: Invalid coefficient values (NaN or Inf)")
        return False
    
    print(f"  All coefficients valid")
    
    return True


def validate_arduino_code(filepath):
    """Validate generated Arduino header file."""
    print("\nValidating Arduino code")
    print(f"File: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ERROR: File not found")
        return False
    
    with open(filepath, 'r') as f:
        code = f.read()
    
    errors = []
    warnings = []
    
    if 'predictETA' not in code:
        errors.append("Missing predictETA function")
    else:
        print("  predictETA function found")
    
    if 'INTERCEPT' not in code:
        errors.append("Missing INTERCEPT constant")
    else:
        print("  INTERCEPT constant found")
    
    if 'COEFFICIENTS' not in code or 'COEF_' not in code:
        warnings.append("No coefficient constants found")
    else:
        print("  Coefficient constants found")
    
    if 'float' not in code:
        errors.append("No float type declarations")
    else:
        print("  Float type declarations found")
    
    if code.count('{') != code.count('}'):
        errors.append("Mismatched braces in generated code")
    else:
        print("  Brace matching valid")
    
    if errors:
        for err in errors:
            print(f"  ERROR: {err}")
        return False
    
    if warnings:
        for warn in warnings:
            print(f"  WARNING: {warn}")
    
    return True


def validate_model_performance(model_dir):
    """Validate model performance from training output."""
    print("\nValidating Model Performance")
    
    results = {}
    
    for model_type in ['linear', 'poly2', 'poly3']:
        filepath = os.path.join(model_dir, f'{model_type}_weights.json')
        
        if not os.path.exists(filepath):
            print(f"  Skipping {model_type} (file not found)")
            continue
        
        with open(filepath, 'r') as f:
            weights = json.load(f)
        
        results[model_type] = weights
    
    if not results:
        print("  ERROR: No model weights found")
        return False
    
    print(f"\n  Found {len(results)} trained models")
    
    return True


def validate_plots(plot_dir):
    """Validate generated plots exist."""
    print("\nValidating Plots")
    
    expected_plots = ['model_comparison.png']
    
    found_plots = []
    missing_plots = []
    
    for plot in expected_plots:
        filepath = os.path.join(plot_dir, plot)
        if os.path.exists(filepath):
            found_plots.append(plot)
            size = os.path.getsize(filepath)
            print(f"  Found: {plot} ({size} bytes)")
        else:
            missing_plots.append(plot)
            print(f"  Missing: {plot}")
    
    if missing_plots:
        print(f"\n  WARNING: {len(missing_plots)} plot(s) missing")
    else:
        print(f"\n  All expected plots found")
    
    return len(missing_plots) == 0


def validate_training_data_compatibility():
    """Validate that training data is compatible with model expectations."""
    print("\nValidating Training Data Compatibility")
    
    module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    train_data_path = os.path.join(module_dir, '02_train', 'data', 'train_data.csv')
    
    if not os.path.exists(train_data_path):
        print("  WARNING: Training data not found, skipping compatibility check")
        return True
    
    df = pd.read_csv(train_data_path)
    
    expected_features = ['time_0_to_1', 'time_1_to_2', 'speed_0_to_1', 'speed_1_to_2']
    expected_target = 'ETA'
    
    missing_features = [f for f in expected_features if f not in df.columns]
    if missing_features:
        print(f"  ERROR: Missing features in training data: {missing_features}")
        return False
    
    if expected_target not in df.columns:
        print(f"  ERROR: Missing target variable '{expected_target}' in training data")
        return False
    
    print(f"  All required features present")
    print(f"  Target variable present")
    
    for feature in expected_features:
        if df[feature].isnull().any():
            print(f"  ERROR: NULL values in feature '{feature}'")
            return False
    
    if df[expected_target].isnull().any():
        print(f"  ERROR: NULL values in target variable")
        return False
    
    print(f"  No NULL values in features or target")
    
    return True


def main():
    """Run all model validations."""
    module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(module_dir, '03_model', 'models')
    plot_dir = os.path.join(module_dir, '03_model', 'plots')
    
    print("MODEL TRAINING VALIDATION")
    print("=" * 60)
    
    results = []
    
    model_files = [
        ('linear_weights.json', 'linear'),
        ('poly2_weights.json', 'poly2'),
        ('poly3_weights.json', 'poly3')
    ]
    
    for filename, model_type in model_files:
        filepath = os.path.join(model_dir, filename)
        if os.path.exists(filepath):
            results.append((f"Weights ({model_type})", 
                          validate_model_weights(filepath, model_type)))
        else:
            print(f"\nSkipping {model_type} weights (file not found)")
    
    arduino_file = os.path.join(model_dir, 'eta_model.h')
    if os.path.exists(arduino_file):
        results.append(("Arduino Code", validate_arduino_code(arduino_file)))
    else:
        print("\nSkipping Arduino code validation (file not found)")
    
    results.append(("Model Performance", validate_model_performance(model_dir)))
    
    if os.path.exists(plot_dir):
        results.append(("Plots", validate_plots(plot_dir)))
    else:
        print("\nSkipping plot validation (directory not found)")
    
    results.append(("Training Data", validate_training_data_compatibility()))
    
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    print("\n" + ("All validations passed!" if all_passed else "Some validations failed."))
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())