"""Generate and validate traffic parameters."""

import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config, update_vehicle_clearance, load_config

package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from simulator import TrafficSimulator
from vehicle import VehiclePhysics, VEHICLE_TYPES


def generate_traffic_parameters(output_file=None):
    """Generate traffic dataset for all intersection distances."""
    if output_file is None:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, 'traffic_parameters.csv')
    
    config = get_scale_config()
    traffic_config = config['traffic']
    scale_mode = config['scale_mode']
    unit = 'cm' if scale_mode == 'demo' else 'm'
    
    intersection_distances = traffic_config['intersection_distances']
    
    print(f"\nGenerating traffic parameters ({scale_mode} scale)")
    print(f"Intersection distances: {intersection_distances} {unit}\n")
    
    all_data = []
    clearance_by_density = {}
    
    for distance in intersection_distances:
        print(f"Simulating {distance}{unit} intersection...")
        sim = TrafficSimulator(distance)
        
        for density in ['light', 'medium', 'heavy']:
            analysis = sim.analyze_traffic_density(density)
            
            if density not in clearance_by_density:
                clearance_by_density[density] = {'times': []}
            
            clearance_by_density[density]['times'].extend(
                [v['clearance_time'] for v in analysis['vehicles']]
            )
            
            for vehicle in analysis['vehicles']:
                all_data.append({
                    'intersection_distance': distance,
                    'traffic_density': density,
                    'vehicle_type': vehicle['vehicle_type'],
                    'vehicle_id': vehicle['vehicle_id'],
                    'initial_speed': vehicle['initial_speed'],
                    'time_to_crossing': vehicle['time_to_crossing'],
                    'stopping_distance': vehicle['stopping_distance'],
                    'clearance_time': vehicle['clearance_time'],
                    'can_stop': vehicle['can_stop']
                })
    
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    
    print(f"\nDataset saved: {output_file}")
    print(f"Total records: {len(df)}")
    
    # Show sample of data
    print(f"\nSample data (first 3 rows):")
    print(df[['vehicle_type', 'traffic_density', 'initial_speed', 'clearance_time']].head(3).to_string(index=False))
    
    print(f"\nClearance time statistics:")
    for density in ['light', 'medium', 'heavy']:
        times = clearance_by_density[density]['times']
        min_time = round(min(times), 2)
        max_time = round(max(times), 2)
        avg_time = round(np.mean(times), 2)
        
        print(f"  {density:8} | min={min_time:6.2f}s | avg={avg_time:6.2f}s | max={max_time:6.2f}s")
        update_vehicle_clearance(density, min_time, max_time, avg_time)
    
    print(f"\nConfig updated with clearance times")


def validate_traffic(data_file=None):
    """Validate traffic module outputs."""
    if data_file is None:
        data_file = os.path.join(os.path.dirname(__file__), 'data', 'traffic_parameters.csv')
    
    print("\nTRAFFIC MODULE VALIDATION\n")
    
    results = []
    
    # Test 1: Physics equations
    print("Testing physics equations...")
    physics = VehiclePhysics(VEHICLE_TYPES['car'])
    
    result = physics.calculate_stopping_distance(60)
    test1 = 40 <= result['total_distance'] <= 60
    print(f"  Stopping distance: {result['total_distance']:.1f}m {'PASS' if test1 else 'FAIL'}")
    results.append(test1)
    
    time = physics.calculate_time_to_traverse(100, 50, False)
    test2 = abs(time - 7.2) < 0.5
    print(f"  Traverse time: {time:.1f}s {'PASS' if test2 else 'FAIL'}")
    results.append(test2)
    
    with_length = physics.calculate_clearance_time(100, 50, True)
    without_length = physics.calculate_clearance_time(100, 50, False)
    test3 = with_length > without_length
    print(f"  Clearance includes length: {'PASS' if test3 else 'FAIL'}\n")
    results.append(test3)
    
    # Test 2: Dataset validation
    if os.path.exists(data_file):
        print("Validating dataset...")
        df = pd.read_csv(data_file)
        
        required_cols = ['intersection_distance', 'traffic_density', 'vehicle_type',
                        'clearance_time', 'stopping_distance']
        
        test4 = all(col in df.columns for col in required_cols)
        print(f"  Required columns: {'PASS' if test4 else 'FAIL'}")
        results.append(test4)
        
        test5 = not df.isnull().any().any()
        print(f"  No NULL values: {'PASS' if test5 else 'FAIL'}")
        results.append(test5)
        
        test6 = (df['clearance_time'] > 0).all()
        print(f"  Positive clearance times: {'PASS' if test6 else 'FAIL'}")
        results.append(test6)
        
        # Check if data is actually readable
        print(f"\n  Dataset info:")
        print(f"  - Total records: {len(df)}")
        print(f"  - File size: {os.path.getsize(data_file)} bytes")
        print(f"  - Columns: {len(df.columns)}")
        print(f"  - Min clearance: {df['clearance_time'].min():.2f}s")
        print(f"  - Max clearance: {df['clearance_time'].max():.2f}s")
        
        # Show sample
        print(f"\n  Sample rows:")
        sample = df.head(2)[['vehicle_type', 'traffic_density', 'clearance_time']]
        for idx, row in sample.iterrows():
            print(f"    {row['vehicle_type']:10} | {row['traffic_density']:8} | {row['clearance_time']:.2f}s")
        
    else:
        print(f"Dataset not found: {data_file}")
        print("Run: python -m 01_traffic.generate\n")
        results.append(False)
    
    # Test 3: Config validation
    print("\nValidating config...")
    config = load_config()
    clearance = config.get('vehicle_clearance', {})
    
    test7 = all(d in clearance for d in ['light', 'medium', 'heavy'])
    print(f"  Clearance data in config: {'PASS' if test7 else 'FAIL'}")
    results.append(test7)
    
    if test7:
        valid_ranges = True
        for density in ['light', 'medium', 'heavy']:
            times = clearance[density]
            if not (times['min_time'] < times['avg_time'] < times['max_time']):
                valid_ranges = False
                break
        results.append(valid_ranges)
        print(f"  Clearance ranges valid: {'PASS' if valid_ranges else 'FAIL'}")
    
    # Summary
    print(f"\nValidation result: {'ALL TESTS PASSED' if all(results) else 'SOME TESTS FAILED'}")
    print(f"Passed: {sum(results)}/{len(results)}\n")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        sys.exit(validate_traffic())
    else:
        generate_traffic_parameters()
        print("\nRun validation with: python -m 01_traffic.generate validate")