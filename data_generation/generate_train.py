"""Generate train approach dataset with sensor detections."""

import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config, get_scale_config
from physics.train import TRAIN_SPECS, TrainPhysics
from physics.sensors import SensorArray


def simulate_train_approach(train_type, initial_speed, grade, weather, 
                            crossing_distance, train_length, sensor_positions, dt=0.05):
    """Simulate train approaching crossing with sensor detections."""
    
    physics = TrainPhysics(TRAIN_SPECS[train_type])
    sensors = SensorArray(sensor_positions)
    
    speed_ms = initial_speed / 3.6
    speed_variation = np.random.uniform(-8, 8)
    target_speed_ms = max(12/3.6, (initial_speed + speed_variation) / 3.6)
    max_speed_ms = physics.spec.max_speed / 3.6
    
    distance = crossing_distance
    time = 0.0
    max_time = crossing_distance / speed_ms * 4.0
    
    stall_counter = 0
    last_distance = distance
    
    while distance > -(train_length + 50):
        accel = physics.calculate_acceleration(speed_ms, grade, target_speed_ms, weather)
        
        if speed_ms > max_speed_ms:
            speed_ms = max_speed_ms
            accel = min(accel, 0)
        
        new_speed = speed_ms + accel * dt
        speed_ms = max(10/3.6, new_speed)
        distance -= speed_ms * dt
        
        if abs(distance - last_distance) < 0.0001 and distance > 0:
            stall_counter += 1
            if stall_counter > 100:
                return None
        else:
            stall_counter = 0
        
        last_distance = distance
        sensors.update(distance, time, train_length)
        time += dt
        
        if time > max_time:
            return None
    
    detection_times = sensors.get_detection_times()
    
    s0_entry = detection_times['sensor_0']['entry_time']
    s1_entry = detection_times['sensor_1']['entry_time']
    s2_entry = detection_times['sensor_2']['entry_time']
    
    if None in [s0_entry, s1_entry, s2_entry]:
        return None
    
    time_0_to_1 = s1_entry - s0_entry
    time_1_to_2 = s2_entry - s1_entry
    
    if time_0_to_1 <= 0 or time_1_to_2 <= 0:
        return None
    
    dist_0_to_1 = sensor_positions[0] - sensor_positions[1]
    dist_1_to_2 = sensor_positions[1] - sensor_positions[2]
    
    speed_0_to_1_ms = dist_0_to_1 / time_0_to_1
    speed_1_to_2_ms = dist_1_to_2 / time_1_to_2
    
    crossing_time = None
    for t in np.arange(s2_entry, time, dt):
        est_distance = sensor_positions[2] - speed_1_to_2_ms * (t - s2_entry)
        if est_distance <= 0:
            crossing_time = t
            break
    
    eta = (crossing_time - s2_entry) if crossing_time else (sensor_positions[2] / speed_1_to_2_ms)
    
    return {
        'train_type': train_type,
        'initial_speed': initial_speed,
        'grade': grade,
        'weather': weather,
        'sensor_0_entry': s0_entry,
        'sensor_1_entry': s1_entry,
        'sensor_2_entry': s2_entry,
        'time_0_to_1': time_0_to_1,
        'time_1_to_2': time_1_to_2,
        'speed_0_to_1': speed_0_to_1_ms * 3.6,
        'speed_1_to_2': speed_1_to_2_ms * 3.6,
        'ETA': eta,
        'sensor_0_pos': sensor_positions[0],
        'sensor_1_pos': sensor_positions[1],
        'sensor_2_pos': sensor_positions[2]
    }


def generate_train_dataset(num_scenarios=500, output_file=None):
    """Generate train approach dataset with more samples."""
    
    if output_file is None:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, 'train_approaches.csv')
    
    config = get_scale_config()
    crossing_distance = config['train']['crossing_distance']
    sensor_positions = config['train']['sensor_positions']
    train_length = config['train']['train_length']
    train_speeds = config['train_speeds']
    scale_mode = config['scale_mode']
    unit = 'cm' if scale_mode == 'demo' else 'm'
    
    print(f"\nGenerating {num_scenarios} train scenarios ({scale_mode} scale)")
    print(f"Crossing distance: {crossing_distance}{unit}")
    print(f"Sensor positions: {sensor_positions}{unit}")
    
    all_data = []
    failed = 0
    
    for i in range(num_scenarios):
        train_type = np.random.choice(['passenger', 'freight', 'express'])
        speeds = train_speeds[train_type]
        
        initial_speed = np.random.uniform(speeds['min'], speeds['max'])
        grade = np.random.uniform(-2, 2)
        weather = np.random.choice(['clear', 'rain', 'fog'], p=[0.7, 0.2, 0.1])
        
        result = simulate_train_approach(
            train_type, initial_speed, grade, weather,
            crossing_distance, train_length, sensor_positions
        )
        
        if result is None:
            failed += 1
            continue
        
        result['scenario_id'] = i
        all_data.append(result)
        
        if (i + 1) % 50 == 0:
            print(f"Progress: {i + 1}/{num_scenarios} ({failed} failed)")
    
    if len(all_data) == 0:
        print("ERROR: No valid scenarios generated")
        return None
    
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    
    print(f"\nDataset saved: {output_file}")
    print(f"Valid scenarios: {len(df)}/{num_scenarios}")
    print(f"Failed scenarios: {failed}")
    
    print(f"\nSample:")
    print(df[['train_type', 'speed_0_to_1', 'speed_1_to_2', 'ETA']].head(3))
    
    print(f"\nStatistics:")
    print(f"  Speed range: {df['speed_1_to_2'].min():.1f} - {df['speed_1_to_2'].max():.1f} km/h")
    print(f"  ETA range: {df['ETA'].min():.1f} - {df['ETA'].max():.1f}s")
    
    return output_file


def validate_train_data(data_file=None):
    """Validate train dataset."""
    
    if data_file is None:
        data_file = os.path.join(os.path.dirname(__file__), 'data', 'train_approaches.csv')
    
    print("\nVALIDATING TRAIN DATA")
    
    if not os.path.exists(data_file):
        print(f"ERROR: File not found: {data_file}")
        return False
    
    df = pd.read_csv(data_file)
    
    required_cols = ['train_type', 'sensor_0_entry', 'sensor_1_entry', 
                    'sensor_2_entry', 'speed_0_to_1', 'speed_1_to_2', 'ETA']
    
    tests = []
    
    test1 = all(col in df.columns for col in required_cols)
    print(f"Required columns present: {'PASS' if test1 else 'FAIL'}")
    tests.append(test1)
    
    test2 = not df.isnull().any().any()
    print(f"No NULL values: {'PASS' if test2 else 'FAIL'}")
    tests.append(test2)
    
    test3 = (df['ETA'] > 0).all()
    print(f"Positive ETA values: {'PASS' if test3 else 'FAIL'}")
    tests.append(test3)
    
    test4 = ((df['sensor_0_entry'] < df['sensor_1_entry']) & 
             (df['sensor_1_entry'] < df['sensor_2_entry'])).all()
    print(f"Sensor timing ordered: {'PASS' if test4 else 'FAIL'}")
    tests.append(test4)
    
    print(f"\nValidation: {'PASSED' if all(tests) else 'FAILED'} ({sum(tests)}/{len(tests)} tests)")
    return all(tests)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        validate_train_data()
    else:
        num = 500
        if len(sys.argv) > 1:
            presets = {'demo': 50, 'small': 200, 'full': 500}
            num = presets.get(sys.argv[1], 500)
        generate_train_dataset(num_scenarios=num)