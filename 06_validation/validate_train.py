"""Validate train dataset module output and physics."""

import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config, get_scale_config


def validate_train_dataset(filepath):
    """Validate train dataset CSV file."""
    print("Validating Train Dataset")
    print(f"File: {filepath}\n")
    
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        return False
    
    df = pd.read_csv(filepath)
    errors = []
    warnings = []
    
    required_columns = [
        'scenario_id', 'train_type', 'initial_speed', 'grade', 'weather',
        'sensor_0_entry', 'sensor_1_entry', 'sensor_2_entry',
        'time_0_to_1', 'time_1_to_2', 'time_0_to_2',
        'speed_0_to_1', 'speed_1_to_2', 'ETA',
        'sensor_0_pos', 'sensor_1_pos', 'sensor_2_pos'
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
    
    if (df['ETA'] <= 0).any():
        errors.append("Found non-positive ETA values")
    else:
        print("  All ETA values positive")
    
    if (df['time_0_to_1'] <= 0).any() or (df['time_1_to_2'] <= 0).any():
        errors.append("Found non-positive sensor transit times")
    else:
        print("  All sensor transit times positive")
    
    if (df['speed_0_to_1'] <= 0).any() or (df['speed_1_to_2'] <= 0).any():
        errors.append("Found non-positive train speeds")
    else:
        print("  All train speeds positive")
    
    valid_trains = ['passenger', 'freight', 'express']
    if not df['train_type'].isin(valid_trains).all():
        errors.append(f"Invalid train types (must be {valid_trains})")
    else:
        print("  All train types valid")
    
    valid_weather = ['clear', 'rain', 'fog']
    if not df['weather'].isin(valid_weather).all():
        errors.append(f"Invalid weather types (must be {valid_weather})")
    else:
        print("  All weather types valid")
    
    print("\nChecking sensor timing consistency...")
    
    time_sum_diff = abs(df['time_0_to_2'] - (df['time_0_to_1'] + df['time_1_to_2']))
    if (time_sum_diff > 0.1).any():
        warnings.append("Sensor timing inconsistency: time_0_to_2 != time_0_to_1 + time_1_to_2")
    else:
        print("  Sensor timing consistent")
    
    if (df['sensor_0_entry'] >= df['sensor_1_entry']).any():
        errors.append("Sensor 0 entry time >= Sensor 1 entry time")
    
    if (df['sensor_1_entry'] >= df['sensor_2_entry']).any():
        errors.append("Sensor 1 entry time >= Sensor 2 entry time")
    
    if not errors:
        print("  Sensor entry times properly ordered")
    
    print("\nChecking physics consistency...")
    
    config = get_scale_config()
    train_types = config['train_types']
    
    for _, row in df.iterrows():
        t_type = row['train_type']
        if t_type not in train_types:
            continue
        
        max_speed = train_types[t_type]['max_speed']
        if row['speed_0_to_1'] > max_speed * 1.1:
            warnings.append(f"Train {t_type} speed exceeds max by >10%: "
                          f"{row['speed_0_to_1']:.1f} > {max_speed}")
        
        if row['speed_1_to_2'] > max_speed * 1.1:
            warnings.append(f"Train {t_type} speed exceeds max by >10%: "
                          f"{row['speed_1_to_2']:.1f} > {max_speed}")
    
    if not warnings:
        print("  No significant speed violations")
    
    dist_0_to_1 = df['sensor_0_pos'] - df['sensor_1_pos']
    dist_1_to_2 = df['sensor_1_pos'] - df['sensor_2_pos']
    
    calc_speed_0_to_1 = (dist_0_to_1 / df['time_0_to_1']) * 3.6
    calc_speed_1_to_2 = (dist_1_to_2 / df['time_1_to_2']) * 3.6
    
    speed_diff_0_to_1 = abs(df['speed_0_to_1'] - calc_speed_0_to_1)
    speed_diff_1_to_2 = abs(df['speed_1_to_2'] - calc_speed_1_to_2)
    
    if (speed_diff_0_to_1 > 1.0).any() or (speed_diff_1_to_2 > 1.0).any():
        warnings.append("Speed calculation mismatch (speed != distance/time)")
    else:
        print("  Speed calculations consistent with distance/time")
    
    print("\nDataset statistics:")
    print(f"  Total scenarios: {len(df)}")
    print(f"  Train types: {df['train_type'].value_counts().to_dict()}")
    print(f"  Weather conditions: {df['weather'].value_counts().to_dict()}")
    print(f"\n  Speed range (sensor 0->1): {df['speed_0_to_1'].min():.1f} - "
          f"{df['speed_0_to_1'].max():.1f} km/h")
    print(f"  Speed range (sensor 1->2): {df['speed_1_to_2'].min():.1f} - "
          f"{df['speed_1_to_2'].max():.1f} km/h")
    print(f"  ETA range: {df['ETA'].min():.2f} - {df['ETA'].max():.2f}s")
    print(f"  Average ETA: {df['ETA'].mean():.2f}s")
    
    print("\nValidation Summary:")
    if errors:
        print(f"  ERRORS: {len(errors)}")
        for err in errors:
            print(f"    - {err}")
    else:
        print("  ERRORS: 0")
    
    if warnings:
        print(f"  WARNINGS: {len(warnings)}")
        for warn in warnings[:5]:
            print(f"    - {warn}")
        if len(warnings) > 5:
            print(f"    ... and {len(warnings) - 5} more warnings")
    else:
        print("  WARNINGS: 0")
    
    return len(errors) == 0


def validate_sensor_configuration():
    """Validate sensor configuration in config."""
    print("\nValidating Sensor Configuration")
    
    config = load_config()
    scale_mode = config['system']['scale_mode']
    
    train_config = config['train'][f'{scale_mode}_scale']
    sensor_positions = train_config.get('sensor_positions', [])
    crossing_distance = train_config.get('crossing_distance')
    
    print(f"  Scale mode: {scale_mode}")
    print(f"  Crossing distance: {crossing_distance}")
    print(f"  Sensor positions: {sensor_positions}")
    
    if len(sensor_positions) != 3:
        print(f"  ERROR: Expected 3 sensors, found {len(sensor_positions)}")
        return False
    
    if sensor_positions[0] > crossing_distance:
        print("  ERROR: Furthest sensor beyond crossing distance")
        return False
    
    print("  Sensors within crossing distance")
    
    if sensor_positions[0] <= sensor_positions[1] or sensor_positions[1] <= sensor_positions[2]:
        print("  ERROR: Sensors not in decreasing order")
        return False
    
    print("  Sensors properly ordered")
    
    return True


def validate_train_speeds():
    """Validate train speed configurations."""
    print("\nValidating Train Speed Configurations")
    
    config = load_config()
    train_speeds = config.get('train_speeds', {})
    train_types = config.get('train_types', {})
    
    for train_type in ['passenger', 'freight', 'express']:
        if train_type not in train_speeds:
            print(f"  ERROR: Missing speed config for {train_type}")
            return False
        
        if train_type not in train_types:
            print(f"  ERROR: Missing train type config for {train_type}")
            return False
        
        speeds = train_speeds[train_type]
        max_speed = train_types[train_type]['max_speed']
        
        print(f"  {train_type}:")
        print(f"    Speed range: {speeds['min']} - {speeds['max']} km/h")
        print(f"    Max speed: {max_speed} km/h")
        
        if speeds['min'] >= speeds['max']:
            print(f"    ERROR: min >= max")
            return False
        
        if speeds['max'] > max_speed:
            print(f"    WARNING: max speed range exceeds train max speed")
    
    print("\n  All train speed configurations valid")
    return True


def main():
    """Run all train dataset validations."""
    module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    datasets = [
        ('demo', os.path.join(module_dir, '02_train', 'data', 'train_data_demo.csv')),
        ('small', os.path.join(module_dir, '02_train', 'data', 'train_data_small.csv')),
        ('full', os.path.join(module_dir, '02_train', 'data', 'train_data.csv'))
    ]
    
    print("TRAIN DATASET VALIDATION")
    print("=" * 60)
    
    results = []
    
    for name, filepath in datasets:
        if os.path.exists(filepath):
            print(f"\nValidating {name} dataset...")
            results.append((f"Dataset ({name})", validate_train_dataset(filepath)))
        else:
            print(f"\nSkipping {name} dataset (file not found)")
    
    results.append(("Sensor Config", validate_sensor_configuration()))
    results.append(("Train Speeds", validate_train_speeds()))
    
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