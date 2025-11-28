"""
Data validation module for train and traffic datasets.
"""

import pandas as pd
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config


def validate_train_data():
    """Validate train datasets for completeness and consistency."""
    config = get_scale_config()
    scale_mode = config['scale_mode']
    unit = 'cm' if scale_mode == 'demo' else 'm'
    
    data_dir = Path('01_train_dataset/data')
    if not data_dir.exists():
        print("Error: No train data directory found")
        return False
    
    csv_files = list(data_dir.glob('*.csv'))
    if not csv_files:
        print("Error: No CSV files found in train data directory")
        return False
    
    print("Validating train datasets")
    all_valid = True
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            
            required_cols = ['distance_to_crossing', 'speed', 'ETA', 'IR1', 'IR2', 'IR3']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"  {csv_file.name}: FAIL - Missing columns: {missing_cols}")
                all_valid = False
                continue
            
            if df.empty:
                print(f"  {csv_file.name}: FAIL - Empty dataset")
                all_valid = False
                continue
            
            if (df[required_cols] < 0).any().any():
                print(f"  {csv_file.name}: FAIL - Negative values found")
                all_valid = False
                continue
            
            scenarios = df['scenario_id'].nunique() if 'scenario_id' in df.columns else 0
            points = len(df)
            
            print(f"  {csv_file.name}: OK - {scenarios} scenarios, {points} datapoints")
            
        except Exception as e:
            print(f"  {csv_file.name}: FAIL - {str(e)}")
            all_valid = False
    
    return all_valid


def validate_traffic_data():
    """Validate traffic datasets for completeness and consistency."""
    config = get_scale_config()
    scale_mode = config['scale_mode']
    unit = 'cm' if scale_mode == 'demo' else 'm'
    
    data_dir = Path('02_traffic_parameters/data')
    if not data_dir.exists():
        print("Error: No traffic data directory found")
        return False
    
    csv_file = data_dir / 'traffic_parameters.csv'
    if not csv_file.exists():
        print("Error: traffic_parameters.csv not found")
        return False
    
    print("Validating traffic dataset")
    
    try:
        df = pd.read_csv(csv_file)
        
        required_cols = ['intersection_distance', 'traffic_density', 'vehicle_type',
                        'time_to_crossing', 'clearance_time', 'can_stop']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"  FAIL - Missing columns: {missing_cols}")
            return False
        
        if df.empty:
            print(f"  FAIL - Empty dataset")
            return False
        
        if (df[['time_to_crossing', 'clearance_time']] < 0).any().any():
            print(f"  FAIL - Negative time values found")
            return False
        
        valid_densities = {'light', 'medium', 'heavy'}
        invalid_densities = set(df['traffic_density'].unique()) - valid_densities
        if invalid_densities:
            print(f"  FAIL - Invalid density values: {invalid_densities}")
            return False
        
        distances = df['intersection_distance'].unique()
        densities = df['traffic_density'].unique()
        vehicles = len(df)
        
        print(f"  OK - {len(distances)} distances, {len(densities)} densities, {vehicles} vehicle records")
        print(f"  Intersections ({unit}): {sorted(distances)}")
        print(f"  Avg clearance times: light={df[df['traffic_density']=='light']['clearance_time'].mean():.2f}s, "
              f"medium={df[df['traffic_density']=='medium']['clearance_time'].mean():.2f}s, "
              f"heavy={df[df['traffic_density']=='heavy']['clearance_time'].mean():.2f}s")
        
        return True
        
    except Exception as e:
        print(f"  FAIL - {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'train':
            valid = validate_train_data()
        elif command == 'traffic':
            valid = validate_traffic_data()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python validate_data.py [train|traffic]")
            sys.exit(1)
    else:
        train_valid = validate_train_data()
        print()
        traffic_valid = validate_traffic_data()
        valid = train_valid and traffic_valid
    
    sys.exit(0 if valid else 1)