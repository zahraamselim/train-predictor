"""Generate decision scenarios for ML training: wait vs reroute."""

import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config, get_scale_config
from physics.vehicle import VehiclePhysics, VEHICLE_SPECS


def simulate_wait_scenario(train_eta, queue_length, traffic_density):
    """
    Simulate waiting at crossing for train to pass.
    
    Returns:
        Wait time in seconds
    """
    config = load_config()
    gate_closure_offset = config['gates']['closure_before_eta']
    
    time_until_gate_closes = train_eta - gate_closure_offset
    time_gate_closed = gate_closure_offset + 5
    time_to_reopen = 10
    
    avg_vehicle_delay = 3
    queue_delay = queue_length * avg_vehicle_delay
    
    total_wait = max(0, -time_until_gate_closes) + time_gate_closed + time_to_reopen + queue_delay
    
    return total_wait


def simulate_reroute_scenario(alternative_route_distance, traffic_density, vehicle_type='car'):
    """
    Simulate taking alternative route.
    
    Returns:
        Reroute time in seconds
    """
    density_speeds = {
        'light': 50,
        'medium': 40,
        'heavy': 30
    }
    
    avg_speed_kmh = density_speeds.get(traffic_density, 40)
    avg_speed_ms = avg_speed_kmh / 3.6
    
    reroute_time = alternative_route_distance / avg_speed_ms
    
    decision_delay = 5
    
    return reroute_time + decision_delay


def generate_decision_scenario():
    """
    Generate one decision scenario with optimal action.
    
    Returns:
        Dict with scenario features and optimal action
    """
    train_eta = np.random.uniform(20, 120)
    queue_length = np.random.randint(0, 15)
    traffic_density = np.random.choice(['light', 'medium', 'heavy'], p=[0.4, 0.4, 0.2])
    
    config = get_scale_config()
    intersection_distances = config['traffic']['intersection_distances']
    base_distance = np.random.choice(intersection_distances)
    
    reroute_factor = np.random.uniform(1.2, 2.5)
    alternative_route_distance = base_distance * reroute_factor
    
    wait_time = simulate_wait_scenario(train_eta, queue_length, traffic_density)
    reroute_time = simulate_reroute_scenario(alternative_route_distance, traffic_density)
    
    if wait_time < reroute_time:
        optimal_action = 'wait'
        time_saved = reroute_time - wait_time
    else:
        optimal_action = 'reroute'
        time_saved = wait_time - reroute_time
    
    return {
        'train_eta': train_eta,
        'queue_length': queue_length,
        'traffic_density': traffic_density,
        'intersection_distance': base_distance,
        'alternative_route_distance': alternative_route_distance,
        'wait_time': wait_time,
        'reroute_time': reroute_time,
        'optimal_action': optimal_action,
        'time_saved': time_saved
    }


def generate_decision_dataset(num_scenarios=500, output_file=None):
    """Generate complete decision dataset for ML training."""
    if output_file is None:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, 'decisions.csv')
    
    print(f"\nGenerating {num_scenarios} decision scenarios for ML training")
    
    all_data = []
    for i in range(num_scenarios):
        scenario = generate_decision_scenario()
        scenario['scenario_id'] = i
        all_data.append(scenario)
        
        if (i + 1) % 100 == 0:
            print(f"Progress: {i + 1}/{num_scenarios}")
    
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    
    print(f"\nDataset saved: {output_file}")
    print(f"Total scenarios: {len(df)}")
    
    wait_count = (df['optimal_action'] == 'wait').sum()
    reroute_count = (df['optimal_action'] == 'reroute').sum()
    
    print(f"\nAction distribution:")
    print(f"  Wait: {wait_count} ({wait_count/len(df)*100:.1f}%)")
    print(f"  Reroute: {reroute_count} ({reroute_count/len(df)*100:.1f}%)")
    
    print(f"\nSample:")
    print(df[['train_eta', 'queue_length', 'traffic_density', 'optimal_action', 'time_saved']].head(3))
    
    print(f"\nStatistics:")
    print(f"  Average time saved: {df['time_saved'].mean():.1f}s")
    print(f"  Max time saved: {df['time_saved'].max():.1f}s")
    
    return output_file


def validate_decision_data(data_file=None):
    """Validate decision dataset."""
    if data_file is None:
        data_file = os.path.join(os.path.dirname(__file__), 'data', 'decisions.csv')
    
    print("\nVALIDATING DECISION DATA")
    
    if not os.path.exists(data_file):
        print(f"ERROR: File not found: {data_file}")
        return False
    
    df = pd.read_csv(data_file)
    
    required_cols = ['train_eta', 'queue_length', 'traffic_density', 
                    'wait_time', 'reroute_time', 'optimal_action', 'time_saved']
    
    tests = []
    
    test1 = all(col in df.columns for col in required_cols)
    print(f"Required columns present: {'PASS' if test1 else 'FAIL'}")
    tests.append(test1)
    
    test2 = not df.isnull().any().any()
    print(f"No NULL values: {'PASS' if test2 else 'FAIL'}")
    tests.append(test2)
    
    test3 = df['optimal_action'].isin(['wait', 'reroute']).all()
    print(f"Valid actions: {'PASS' if test3 else 'FAIL'}")
    tests.append(test3)
    
    test4 = (df['time_saved'] >= 0).all()
    print(f"Non-negative time saved: {'PASS' if test4 else 'FAIL'}")
    tests.append(test4)
    
    print(f"\nValidation: {'PASSED' if all(tests) else 'FAILED'} ({sum(tests)}/{len(tests)} tests)")
    return all(tests)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        validate_decision_data()
    else:
        num = 500
        if len(sys.argv) > 1:
            num = int(sys.argv[1])
        generate_decision_dataset(num_scenarios=num)