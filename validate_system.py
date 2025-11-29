"""Complete system validation script."""

import sys
import os


def validate_structure():
    """Validate directory structure exists."""
    print("VALIDATING PROJECT STRUCTURE\n")
    
    required_dirs = [
        'physics',
        'data_generation',
        'ml',
        'controller',
        'simulation',
        'arduino',
        'config'
    ]
    
    required_files = [
        'physics/vehicle.py',
        'physics/train.py',
        'physics/sensors.py',
        'data_generation/generate_traffic.py',
        'data_generation/generate_train.py',
        'data_generation/generate_decisions.py',
        'ml/route_optimizer.py',
        'ml/train.py',
        'controller/eta_calculator.py',
        'controller/decision_maker.py',
        'controller/metrics.py',
        'simulation/main.py',
        'simulation/map.py',
        'simulation/crossing.py',
        'simulation/vehicles.py',
        'simulation/visualizer.py',
        'arduino/sketch.ino',
        'arduino/README.md',
        'config/system.yaml',
        'config/utils.py',
        'Makefile',
        'requirements.txt'
    ]
    
    all_pass = True
    
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ (MISSING)")
            all_pass = False
    
    print()
    
    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (MISSING)")
            all_pass = False
    
    if all_pass:
        print("\nStructure validation: PASSED")
    else:
        print("\nStructure validation: FAILED")
        print("Some files are missing. Check MIGRATION_GUIDE.md")
    
    return all_pass


def validate_imports():
    """Validate all modules can be imported."""
    print("\n\nVALIDATING MODULE IMPORTS\n")
    
    modules = [
        ('physics.vehicle', 'VehiclePhysics, VEHICLE_SPECS'),
        ('physics.train', 'TrainPhysics, TRAIN_SPECS'),
        ('physics.sensors', 'SensorArray, calculate_sensor_positions'),
        ('controller.eta_calculator', 'ETACalculator'),
        ('controller.decision_maker', 'CrossingController, SafetyValidator'),
        ('controller.metrics', 'PerformanceMetrics'),
        ('config.utils', 'load_config, get_scale_config'),
    ]
    
    all_pass = True
    
    for module_path, items in modules:
        try:
            exec(f"from {module_path} import {items}")
            print(f"✓ {module_path}")
        except Exception as e:
            print(f"✗ {module_path}: {e}")
            all_pass = False
    
    if all_pass:
        print("\nImport validation: PASSED")
    else:
        print("\nImport validation: FAILED")
        print("Check for syntax errors or missing dependencies")
    
    return all_pass


def validate_config():
    """Validate configuration file."""
    print("\n\nVALIDATING CONFIGURATION\n")
    
    try:
        from config.utils import load_config, get_scale_config
        
        config = load_config()
        scale_config = get_scale_config()
        
        required_keys = [
            'system', 'train', 'traffic', 'train_types', 
            'vehicle_types', 'gates', 'vehicle_clearance'
        ]
        
        all_pass = True
        
        for key in required_keys:
            if key in config:
                print(f"✓ {key}")
            else:
                print(f"✗ {key} (MISSING)")
                all_pass = False
        
        scale_mode = config['system']['scale_mode']
        print(f"\nCurrent scale mode: {scale_mode}")
        
        if all_pass:
            print("\nConfig validation: PASSED")
        else:
            print("\nConfig validation: FAILED")
        
        return all_pass
        
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False


def validate_data_generation():
    """Validate data generation capability."""
    print("\n\nVALIDATING DATA GENERATION\n")
    
    try:
        from data_generation.generate_traffic import validate_traffic_data
        from data_generation.generate_train import validate_train_data
        from data_generation.generate_decisions import validate_decision_data
        
        print("Traffic data:")
        result1 = validate_traffic_data()
        
        print("\nTrain data:")
        result2 = validate_train_data()
        
        print("\nDecision data:")
        result3 = validate_decision_data()
        
        if result1 and result2 and result3:
            print("\nData validation: PASSED")
            return True
        else:
            print("\nData validation: FAILED")
            print("Run: make data-all")
            return False
            
    except Exception as e:
        print(f"✗ Data validation error: {e}")
        print("Ensure data has been generated: make data-all")
        return False


def validate_ml_model():
    """Validate ML model exists and works."""
    print("\n\nVALIDATING ML MODEL\n")
    
    model_path = 'ml/models/route_optimizer.pkl'
    
    if not os.path.exists(model_path):
        print(f"✗ Model not found: {model_path}")
        print("Run: make ml-train")
        return False
    
    try:
        from ml.route_optimizer import RouteOptimizer
        
        optimizer = RouteOptimizer(model_path)
        
        result = optimizer.predict(
            train_eta=45,
            queue_length=5,
            traffic_density='medium',
            intersection_distance=500,
            alternative_route_distance=1200
        )
        
        if 'action' in result and 'confidence' in result:
            print(f"✓ Model loaded and working")
            print(f"  Test prediction: {result['action']} (confidence: {result['confidence']:.1%})")
            print("\nML model validation: PASSED")
            return True
        else:
            print("✗ Model output format incorrect")
            return False
            
    except Exception as e:
        print(f"✗ ML model error: {e}")
        return False


def main():
    """Run complete system validation."""
    print("="*60)
    print("LEVEL CROSSING SYSTEM - COMPLETE VALIDATION")
    print("="*60)
    
    results = []
    
    results.append(('Structure', validate_structure()))
    results.append(('Imports', validate_imports()))
    results.append(('Config', validate_config()))
    results.append(('Data', validate_data_generation()))
    results.append(('ML Model', validate_ml_model()))
    
    print("\n\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name:20s}: {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if all(passed for _, passed in results):
        print("\n✓ ALL VALIDATIONS PASSED")
        print("\nSystem ready! Run: make simulate")
        return 0
    else:
        print("\n✗ SOME VALIDATIONS FAILED")
        print("\nFix issues above before running simulation")
        return 1


if __name__ == "__main__":
    sys.exit(main())