"""Generate traffic clearance time dataset."""

import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config, get_scale_config, update_vehicle_clearance
from physics.vehicle import VEHICLE_SPECS, VehiclePhysics


def simulate_traffic_scenario(intersection_distance, density, vehicle_mix=None):
    """
    Simulate vehicles clearing an intersection.
    
    Args:
        intersection_distance: Distance from intersection to crossing (m)
        density: 'light', 'medium', or 'heavy'
        vehicle_mix: Dict of vehicle type probabilities
        
    Returns:
        List of vehicle clearance records
    """
    if vehicle_mix is None:
        vehicle_mix = {'car': 0.60, 'suv': 0.25, 'truck': 0.10, 'motorcycle': 0.05}
    
    density_configs = {
        'light': {'num_vehicles': 3, 'speed_range': (45, 60)},
        'medium': {'num_vehicles': 8, 'speed_range': (35, 55)},
        'heavy': {'num_vehicles': 15, 'speed_range': (20, 40)}
    }
    
    config = density_configs[density]
    vehicle_types = list(vehicle_mix.keys())
    probabilities = list(vehicle_mix.values())
    
    results = []
    for i in range(config['num_vehicles']):
        v_type = np.random.choice(vehicle_types, p=probabilities)
        speed = np.random.uniform(*config['speed_range'])
        
        physics = VehiclePhysics(VEHICLE_SPECS[v_type])
        
        stopping = physics.calculate_stopping_distance(speed)
        can_stop = stopping['total_distance'] < intersection_distance
        
        clearance_time = physics.calculate_clearance_time(intersection_distance, speed)
        
        results.append({
            'intersection_distance': intersection_distance,
            'traffic_density': density,
            'vehicle_type': v_type,
            'vehicle_id': i,
            'initial_speed': speed,
            'stopping_distance': stopping['total_distance'],
            'clearance_time': clearance_time,
            'can_stop': can_stop
        })
    
    return results


def generate_traffic_dataset(output_file=None):
    """Generate complete traffic clearance dataset."""
    if output_file is None:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, 'traffic_clearance.csv')
    
    config = get_scale_config()
    intersection_distances = config['traffic']['intersection_distances']
    scale_mode = config['scale_mode']
    unit = 'cm' if scale_mode == 'demo' else 'm'
    
    print(f"\nGenerating traffic clearance data ({scale_mode} scale)")
    print(f"Intersection distances: {intersection_distances} {unit}")
    
    all_data = []
    clearance_by_density = {}
    
    for distance in intersection_distances:
        print(f"Simulating {distance}{unit} intersection...")
        
        for density in ['light', 'medium', 'heavy']:
            results = simulate_traffic_scenario(distance, density)
            
            if density not in clearance_by_density:
                clearance_by_density[density] = []
            
            clearance_by_density[density].extend([r['clearance_time'] for r in results])
            all_data.extend(results)
    
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    
    print(f"\nDataset saved: {output_file}")
    print(f"Total records: {len(df)}")
    print(f"\nSample:")
    print(df[['vehicle_type', 'traffic_density', 'initial_speed', 'clearance_time']].head(3))
    
    print(f"\nClearance time statistics:")
    for density in ['light', 'medium', 'heavy']:
        times = clearance_by_density[density]
        min_time = round(min(times), 2)
        max_time = round(max(times), 2)
        avg_time = round(np.mean(times), 2)
        
        print(f"  {density:8} | min={min_time:6.2f}s | avg={avg_time:6.2f}s | max={max_time:6.2f}s")
        update_vehicle_clearance(density, min_time, max_time, avg_time)
    
    print(f"\nConfig updated with clearance times")
    return output_file


def validate_traffic_data(data_file=None):
    """Validate traffic dataset."""
    if data_file is None:
        data_file = os.path.join(os.path.dirname(__file__), 'data', 'traffic_clearance.csv')
    
    print("\nVALIDATING TRAFFIC DATA")
    
    if not os.path.exists(data_file):
        print(f"ERROR: File not found: {data_file}")
        return False
    
    df = pd.read_csv(data_file)
    
    required_cols = ['intersection_distance', 'traffic_density', 'vehicle_type',
                    'clearance_time', 'stopping_distance']
    
    tests = []
    
    test1 = all(col in df.columns for col in required_cols)
    print(f"Required columns present: {'PASS' if test1 else 'FAIL'}")
    tests.append(test1)
    
    test2 = not df.isnull().any().any()
    print(f"No NULL values: {'PASS' if test2 else 'FAIL'}")
    tests.append(test2)
    
    test3 = (df['clearance_time'] > 0).all()
    print(f"Positive clearance times: {'PASS' if test3 else 'FAIL'}")
    tests.append(test3)
    
    test4 = len(df) > 0
    print(f"Data not empty: {'PASS' if test4 else 'FAIL'}")
    tests.append(test4)
    
    print(f"\nValidation: {'PASSED' if all(tests) else 'FAILED'} ({sum(tests)}/{len(tests)} tests)")
    return all(tests)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        validate_traffic_data()
    else:
        generate_traffic_dataset()