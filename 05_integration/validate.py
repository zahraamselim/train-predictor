"""Validation for integration module."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config

package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from decision_logic import CrossingController, SafetyValidator
from notification_optimizer import NotificationOptimizer


def validate_integration():
    """Validate integration module."""
    
    print("\nINTEGRATION MODULE VALIDATION\n")
    
    results = []
    
    # Test 1: Controller initialization
    print("Testing crossing controller...")
    try:
        controller = CrossingController()
        test1 = True
        print("  Controller initialized: PASS")
    except Exception as e:
        print(f"  FAIL: {e}")
        test1 = False
    results.append(test1)
    
    # Test 2: Decision logic
    print("\nTesting decision logic...")
    test_timings = {
        'sensor_0_entry': 0.0,
        'sensor_1_entry': 24.0,
        'sensor_2_entry': 42.0
    }
    
    try:
        decisions = controller.process_sensor_detection(test_timings, eta=25.0)
        
        test2a = 'close_gates' in decisions
        test2b = 'notify_intersections' in decisions
        test2c = decisions['close_gates'] == True  # ETA=25, offset=10, so 25 < 10 → close
        
        test2 = test2a and test2b and test2c
        print(f"  Close gates decision: {decisions['close_gates']} {'PASS' if test2 else 'FAIL'}")
    except Exception as e:
        print(f"  FAIL: {e}")
        test2 = False
    results.append(test2)
    
    # Test 3: Safety validator
    print("\nTesting safety validator...")
    try:
        validator = SafetyValidator()
        
        validation = validator.validate_notification_timing(
            train_eta=60.0,
            notification_time=20.0,
            traffic_density='heavy',
            intersection_distance=500
        )
        
        test3 = 'is_safe' in validation and 'safety_margin' in validation
        print(f"  Safety validation: {validation['is_safe']}")
        print(f"  Safety margin: {validation['safety_margin']:.1f}s")
        print(f"  {'PASS' if test3 else 'FAIL'}")
    except Exception as e:
        print(f"  FAIL: {e}")
        test3 = False
    results.append(test3)
    
    # Test 4: System constraints check
    print("\nTesting system constraints...")
    try:
        config = get_scale_config()
        sensor_positions = config['train']['sensor_positions']
        crossing_distance = config['train']['crossing_distance']
        
        constraints = validator.check_system_constraints(
            sensor_positions,
            crossing_distance,
            max_train_speed=160  # km/h
        )
        
        test4 = 'meets_requirements' in constraints
        print(f"  Warning time available: {constraints['warning_time_available']:.1f}s")
        print(f"  Warning time required: {constraints['warning_time_required']:.1f}s")
        print(f"  Meets requirements: {constraints['meets_requirements']}")
        print(f"  {'PASS' if test4 else 'FAIL'}")
    except Exception as e:
        print(f"  FAIL: {e}")
        test4 = False
    results.append(test4)
    
    # Test 5: ML optimizer (optional)
    print("\nTesting ML notification optimizer...")
    try:
        optimizer = NotificationOptimizer()
        
        # Generate small training set
        X, y = optimizer.generate_training_data(num_scenarios=100)
        
        test5a = len(X) == 100
        test5b = len(y) == 100
        
        print(f"  Training data generated: {len(X)} scenarios")
        
        # Train model
        metrics = optimizer.train(X, y)
        
        test5c = metrics['test_r2'] > 0.8  # Should have decent fit
        
        print(f"  Model R²: {metrics['test_r2']:.4f} {'PASS' if test5c else 'FAIL'}")
        
        # Test prediction
        notification_time = optimizer.predict(
            train_eta=60.0,
            traffic_density='heavy',
            intersection_distance=500
        )
        
        test5d = 0 < notification_time < 60
        print(f"  Predicted notification: {notification_time:.1f}s {'PASS' if test5d else 'FAIL'}")
        
        test5 = test5a and test5b and test5c and test5d
        
    except Exception as e:
        print(f"  FAIL: {e}")
        test5 = False
    results.append(test5)
    
    # Summary
    print(f"\nValidation result: {'ALL TESTS PASSED' if all(results) else 'SOME TESTS FAILED'}")
    print(f"Passed: {sum(results)}/{len(results)}\n")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(validate_integration())