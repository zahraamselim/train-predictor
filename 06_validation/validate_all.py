"""Run all validation checks across all modules."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .validate_traffic import main as validate_traffic_main
from .validate_train import main as validate_train_main
from .validate_model import main as validate_model_main


def main():
    """Run all validations."""
    print("\nRunning validation for all modules...\n")
    
    results = {}
    
    print("1. TRAFFIC MODULE")
    try:
        results['traffic'] = validate_traffic_main()
    except Exception as e:
        print(f"ERROR: Traffic validation failed with exception: {e}")
        results['traffic'] = 1
    
    print("2. TRAIN DATASET MODULE")
    try:
        results['train'] = validate_train_main()
    except Exception as e:
        print(f"ERROR: Train validation failed with exception: {e}")
        results['train'] = 1
    
    print("3. MODEL TRAINING MODULE")
    try:
        results['model'] = validate_model_main()
    except Exception as e:
        print(f"ERROR: Model validation failed with exception: {e}")
        results['model'] = 1
    
    print("FINAL SUMMARY")
    
    for module, exit_code in results.items():
        status = "PASS" if exit_code == 0 else "FAIL"
        print(f"  {module.upper()}: {status}")
    
    all_passed = all(code == 0 for code in results.values())
    
    if all_passed:
        print("SUCCESS: All modules passed validation!")
    else:
        failed_modules = [m for m, c in results.items() if c != 0]
        print(f"FAILURE: The following modules failed validation: {', '.join(failed_modules)}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())