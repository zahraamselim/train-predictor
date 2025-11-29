"""Validate traffic parameters module output and physics."""

import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config, get_scale_config


def validate_traffic_dataset(filepath):
    """Validate traffic parameters CSV file."""
    print("Validating Traffic Dataset")
    print(f"File: {filepath}\n")
    
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        return False
    
    df = pd.read_csv(filepath)
    errors = []
    warnings = []
    
    required_columns = [
        'intersection_distance', 'traffic_density', 'vehicle_type',
        'vehicle_id', 'initial_speed', 'time_to_crossing',
        'stopping_distance', 'clearance_time', 'can_stop'
    ]
    
    print("Checking column presence...")
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")
    
    if errors:
        for err in errors:
            print(f"  ERROR: {err}")
        return False
    
    print("  All required columns present")
    
    print("\nChecking data integrity...")
    
    if df.isnull().any().any():
        null_cols = df.columns[df.isnull().any()].tolist()
        errors.append(f"NULL values found in columns: {null_cols}")
    else:
        print("  No NULL values")
    
    if (df['clearance_time'] <= 0).any():
        errors.append("Found non-positive clearance times")
    else:
        print("  All clearance times positive")
    
    if (df['initial_speed'] < 0).any() or (df['initial_speed'] > 120).any():
        warnings.append("Initial speeds outside expected range (0-120 km/h)")
    else:
        print("  Initial speeds in valid range")
    
    if (df['stopping_distance'] < 0).any():
        errors.append("Found negative stopping distances")
    else:
        print("  All stopping distances non-negative")
    
    valid_densities = ['light', 'medium', 'heavy']
    if not df['traffic_density'].isin(valid_densities).all():
        errors.append(f"Invalid traffic densities (must be {valid_densities})")
    else:
        print("  All traffic densities valid")
    
    valid_vehicles = ['car', 'suv', 'truck', 'motorcycle']
    if not df['vehicle_type'].isin(valid_vehicles).all():
        errors.append(f"Invalid vehicle types (must be {valid_vehicles})")
    else:
        print("  All vehicle types valid")
    
    print("\nChecking physics consistency...")
    
    config = get_scale_config()
    vehicle_types = config['vehicle_types']
    
    for _, row in df.iterrows():
        v_type = row['vehicle_type']
        if v_type not in vehicle_types:
            continue
        
        max_speed = vehicle_types[v_type]['max_speed']
        if row['initial_speed'] > max_speed:
            warnings.append(f"Vehicle {v_type} exceeds max speed: "
                          f"{row['initial_speed']} > {max_speed}")
    
    if not warnings:
        print("  No speed violations")
    
    print("\nDataset statistics:")
    print(f"  Total records: {len(df)}")
    print(f"  Unique vehicles: {df['vehicle_id'].nunique()}")
    print(f"  Traffic densities: {df['traffic_density'].value_counts().to_dict()}")
    print(f"  Vehicle types: {df['vehicle_type'].value_counts().to_dict()}")
    print(f"\n  Clearance time range: {df['clearance_time'].min():.2f}s - "
          f"{df['clearance_time'].max():.2f}s")
    print(f"  Average clearance time: {df['clearance_time'].mean():.2f}s")
    
    print("\nValidation Summary:")
    if errors:
        print(f"  ERRORS: {len(errors)}")
        for err in errors:
            print(f"    - {err}")
    else:
        print("  ERRORS: 0")
    
    if warnings:
        print(f"  WARNINGS: {len(warnings)}")
        for warn in warnings:
            print(f"    - {warn}")
    else:
        print("  WARNINGS: 0")
    
    return len(errors) == 0


def validate_vehicle_clearance_times():
    """Validate vehicle clearance times in config match dataset."""
    print("\nValidating Vehicle Clearance Times in Config")
    
    config = load_config()
    vehicle_clearance = config.get('vehicle_clearance', {})
    
    if not vehicle_clearance:
        print("  WARNING: No vehicle clearance times in config")
        return False
    
    print("\nConfigured clearance times:")
    for density in ['light', 'medium', 'heavy']:
        if density in vehicle_clearance:
            times = vehicle_clearance[density]
            print(f"  {density}:")
            print(f"    min: {times['min_time']}s")
            print(f"    max: {times['max_time']}s")
            print(f"    avg: {times['avg_time']}s")
            
            if times['min_time'] >= times['max_time']:
                print(f"    ERROR: min_time >= max_time")
                return False
            
            if not (times['min_time'] <= times['avg_time'] <= times['max_time']):
                print(f"    WARNING: avg_time outside [min, max] range")
    
    return True


def validate_sensor_positions():
    """Validate sensor positions are properly calculated."""
    print("\nValidating Sensor Positions")
    
    config = load_config()
    scale_mode = config['system']['scale_mode']
    
    train_config = config['train'][f'{scale_mode}_scale']
    sensor_positions = train_config.get('sensor_positions', [])
    
    if len(sensor_positions) != 3:
        print(f"  ERROR: Expected 3 sensors, found {len(sensor_positions)}")
        return False
    
    print(f"  Scale mode: {scale_mode}")
    print(f"  Sensor positions: {sensor_positions}")
    
    if sensor_positions[0] <= sensor_positions[1] or sensor_positions[1] <= sensor_positions[2]:
        print("  ERROR: Sensors not in decreasing order (furthest to nearest)")
        return False
    
    print("  Sensors properly ordered (decreasing distance from crossing)")
    
    if sensor_positions[2] <= 0:
        print("  ERROR: Nearest sensor at or behind crossing")
        return False
    
    print("  All sensors positioned before crossing")
    
    vehicle_clearance = config['vehicle_clearance']
    max_clearance = max(
        vehicle_clearance['light']['max_time'],
        vehicle_clearance['medium']['max_time'],
        vehicle_clearance['heavy']['max_time']
    )
    
    train_types = config['train_types']
    max_train_speed_kmh = max(t['max_speed'] for t in train_types.values())
    max_train_speed_ms = max_train_speed_kmh / 3.6
    
    gate_closure_offset = config['gates']['closure_before_eta']
    safety_buffer = config['traffic'][f'{scale_mode}_scale']['safety_buffer']
    
    total_warning_time = max_clearance + safety_buffer + gate_closure_offset
    min_detection_distance = max_train_speed_ms * total_warning_time
    
    if scale_mode == 'demo':
        scale_factor = config['system']['scale_factor']
        min_detection_distance = min_detection_distance / scale_factor
    
    print(f"\n  Required detection distance: {min_detection_distance:.1f}m")
    print(f"  Furthest sensor at: {sensor_positions[0]}m")
    
    if sensor_positions[0] < min_detection_distance * 0.95:
        print(f"  WARNING: Furthest sensor may be too close")
        print(f"           (expected ~{min_detection_distance:.1f}m)")
    else:
        print("  Furthest sensor position adequate")
    
    return True


def main():
    """Run all traffic validations."""
    module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    traffic_data = os.path.join(module_dir, '01_traffic', 'data', 'traffic_parameters.csv')
    
    print("TRAFFIC MODULE VALIDATION")
    print("=" * 60)
    
    results = []
    
    if os.path.exists(traffic_data):
        results.append(("Dataset", validate_traffic_dataset(traffic_data)))
    else:
        print(f"\nSkipping dataset validation (file not found)")
        results.append(("Dataset", False))
    
    results.append(("Clearance Times", validate_vehicle_clearance_times()))
    results.append(("Sensor Positions", validate_sensor_positions()))
    
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