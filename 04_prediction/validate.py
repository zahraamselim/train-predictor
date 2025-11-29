"""Validation for prediction module."""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config

package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from eta_calculator import ETACalculator


def validate_prediction():
    """Validate ETA prediction module."""
    
    print("\nPREDICTION MODULE VALIDATION\n")
    
    config = get_scale_config()
    sensor_positions = config['train']['sensor_positions']
    
    results = []
    
    # Test 1: Calculator initialization
    print("Testing ETA calculator initialization...")
    try:
        calc = ETACalculator(sensor_positions)
        test1 = True
        print(f"  Initialized with sensors: {sensor_positions}")
    except Exception as e:
        print(f"  FAIL: {e}")
        test1 = False
    results.append(test1)
    
    # Test 2: Simple ETA calculation
    print("\nTesting simple ETA calculation...")
    test_timings = {
        'sensor_0_entry': 0.0,
        'sensor_1_entry': 24.0,   # 1080m in 24s = 45 m/s = 162 km/h
        'sensor_2_entry': 42.0    # 810m in 18s = 45 m/s
    }
    
    try:
        eta = calc.calculate_eta_simple(test_timings)
        # At 45 m/s, 810m should take 18s
        expected = 810 / 45  # = 18s
        test2 = abs(eta - expected) < 1.0  # Within 1 second
        print(f"  ETA: {eta:.2f}s (expected ~{expected:.2f}s)")
        print(f"  {'PASS' if test2 else 'FAIL'}")
    except Exception as e:
        print(f"  FAIL: {e}")
        test2 = False
    results.append(test2)
    
    # Test 3: ETA with acceleration
    print("\nTesting ETA with acceleration...")
    accel_timings = {
        'sensor_0_entry': 0.0,
        'sensor_1_entry': 27.0,   # Slower initially
        'sensor_2_entry': 45.0    # Speeding up
    }
    
    try:
        eta = calc.calculate_eta_with_acceleration(accel_timings)
        test3 = eta > 0 and eta < 100  # Reasonable range
        print(f"  ETA with acceleration: {eta:.2f}s")
        print(f"  {'PASS' if test3 else 'FAIL'}")
    except Exception as e:
        print(f"  FAIL: {e}")
        test3 = False
    results.append(test3)
    
    # Test 4: Robust calculation
    print("\nTesting robust ETA calculation...")
    try:
        result = calc.calculate_eta_robust(test_timings)
        
        test4a = 'eta_final' in result
        test4b = 'speed_1_to_2_kmh' in result
        test4c = 'acceleration' in result
        test4 = test4a and test4b and test4c
        
        print(f"  Final ETA: {result['eta_final']:.2f}s")
        print(f"  Speed: {result['speed_1_to_2_kmh']:.1f} km/h")
        print(f"  Acceleration: {result['acceleration']:.3f} m/s²")
        print(f"  {'PASS' if test4 else 'FAIL'}")
    except Exception as e:
        print(f"  FAIL: {e}")
        test4 = False
    results.append(test4)
    
    # Test 5: Timing validation
    print("\nTesting timing validation...")
    
    valid_timings = {
        'sensor_0_entry': 0.0,
        'sensor_1_entry': 24.0,
        'sensor_2_entry': 42.0
    }
    
    invalid_timings = {
        'sensor_0_entry': 0.0,
        'sensor_1_entry': 42.0,  # Wrong order
        'sensor_2_entry': 24.0
    }
    
    test5a = calc.validate_timings(valid_timings)
    test5b = not calc.validate_timings(invalid_timings)
    test5 = test5a and test5b
    
    print(f"  Valid timings accepted: {'PASS' if test5a else 'FAIL'}")
    print(f"  Invalid timings rejected: {'PASS' if test5b else 'FAIL'}")
    results.append(test5)
    
    # Test 6: Real dataset validation
    train_data = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        '03_train', 'data', 'train_data.csv'
    )
    
    if os.path.exists(train_data):
        print("\nTesting on real dataset...")
        df = pd.read_csv(train_data)
        
        errors = []
        for idx, row in df.head(10).iterrows():
            timings = {
                'sensor_0_entry': row['sensor_0_entry'],
                'sensor_1_entry': row['sensor_1_entry'],
                'sensor_2_entry': row['sensor_2_entry']
            }
            
            predicted_eta = calc.calculate_eta_simple(timings)
            actual_eta = row['ETA']
            error = abs(predicted_eta - actual_eta)
            errors.append(error)
        
        avg_error = sum(errors) / len(errors)
        max_error = max(errors)
        
        test6 = avg_error < 5.0  # Average error less than 5 seconds
        
        print(f"  Tested on {len(errors)} scenarios")
        print(f"  Average error: {avg_error:.2f}s")
        print(f"  Max error: {max_error:.2f}s")
        print(f"  {'PASS' if test6 else 'FAIL'}")
        results.append(test6)
    else:
        print(f"\nTrain dataset not found: {train_data}")
        print("Run 'make train-generate' first")
        results.append(False)
    
    # Summary
    print(f"\nValidation result: {'ALL TESTS PASSED' if all(results) else 'SOME TESTS FAILED'}")
    print(f"Passed: {sum(results)}/{len(results)}\n")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(validate_prediction())