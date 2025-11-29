"""Generate diverse training scenarios with IR sensor detection events."""

import numpy as np
import pandas as pd
import sys
import os

try:
    from .train_simulator import TrainSimulator
    from .ir_sensors import IRSensorArray
except ImportError:
    from train_simulator import TrainSimulator
    from ir_sensors import IRSensorArray

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config


def generate_dataset(num_scenarios: int = 100, 
                     output_file: str = 'train_data.csv') -> None:
    """
    Generate diverse training scenarios with IR sensor detection events.
    
    Args:
        num_scenarios: Number of unique scenarios to generate
        output_file: CSV filename for output
    """
    config = get_scale_config()
    train_config = config['train']
    scale_mode = config['scale_mode']
    unit = 'cm' if scale_mode == 'demo' else 'm'
    
    crossing_distance = train_config['crossing_distance']
    sensor_positions = train_config['sensor_positions']
    train_length = train_config['train_length']
    train_speeds = config['train_speeds']
    
    print(f"Generating {num_scenarios} scenarios")
    print(f"Scale: {scale_mode} ({unit})")
    print(f"Crossing distance: {crossing_distance} {unit}")
    print(f"Sensor positions: {sensor_positions} {unit}")
    
    all_data = []
    failed_scenarios = 0
    
    for i in range(num_scenarios):
        ir_array = IRSensorArray(sensor_positions=sensor_positions)
        
        train_type = np.random.choice(['passenger', 'freight', 'express'])
        speeds = train_speeds[train_type]
        
        initial_speed = np.random.uniform(speeds['min'], speeds['max'])
        target_speed = initial_speed + np.random.uniform(-5, 5)
        grade = np.random.uniform(-2, 2)
        weather = np.random.choice(['clear', 'rain', 'fog'], p=[0.7, 0.2, 0.1])
        
        sim = TrainSimulator(train_type, crossing_distance)
        trajectory = sim.simulate_approach(initial_speed, grade, weather, target_speed)
        
        if len(trajectory) == 0 or trajectory[-1]['distance_to_crossing'] > 10:
            failed_scenarios += 1
            continue
        
        for point in trajectory:
            train_distance = point['distance_to_crossing']
            current_time = point['time']
            ir_array.update_sensors(train_distance, current_time, train_length)
        
        detection_times = ir_array.get_detection_times()
        
        sensor_0_entry = detection_times['sensor_0']['entry_time']
        sensor_1_entry = detection_times['sensor_1']['entry_time']
        sensor_2_entry = detection_times['sensor_2']['entry_time']
        
        if sensor_0_entry is None or sensor_1_entry is None or sensor_2_entry is None:
            if i < 5:
                print(f"  Scenario {i} failed: sensor_0={sensor_0_entry}, "
                      f"sensor_1={sensor_1_entry}, sensor_2={sensor_2_entry}")
                print(f"    Train started at {crossing_distance}, "
                      f"sensors at {sensor_positions}")
            failed_scenarios += 1
            continue
        
        time_0_to_1 = sensor_1_entry - sensor_0_entry
        time_1_to_2 = sensor_2_entry - sensor_1_entry
        time_0_to_2 = sensor_2_entry - sensor_0_entry
        
        dist_0_to_1 = sensor_positions[0] - sensor_positions[1]
        dist_1_to_2 = sensor_positions[1] - sensor_positions[2]
        
        speed_0_to_1 = dist_0_to_1 / time_0_to_1 if time_0_to_1 > 0 else 0
        speed_1_to_2 = dist_1_to_2 / time_1_to_2 if time_1_to_2 > 0 else 0
        
        eta_at_sensor_2 = (trajectory[-1]['distance_to_crossing'] / 
                          (speed_1_to_2 if speed_1_to_2 > 0 else 1))
        
        for point in trajectory:
            if point['time'] >= sensor_2_entry:
                eta_at_sensor_2 = point['ETA']
                break
        
        all_data.append({
            'scenario_id': i,
            'train_type': train_type,
            'initial_speed': initial_speed,
            'grade': grade,
            'weather': weather,
            'sensor_0_entry': sensor_0_entry,
            'sensor_1_entry': sensor_1_entry,
            'sensor_2_entry': sensor_2_entry,
            'time_0_to_1': time_0_to_1,
            'time_1_to_2': time_1_to_2,
            'time_0_to_2': time_0_to_2,
            'speed_0_to_1': speed_0_to_1 * 3.6,
            'speed_1_to_2': speed_1_to_2 * 3.6,
            'ETA': eta_at_sensor_2,
            'sensor_0_pos': sensor_positions[0],
            'sensor_1_pos': sensor_positions[1],
            'sensor_2_pos': sensor_positions[2]
        })
        
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_scenarios}")
    
    if len(all_data) == 0:
        print("Error: No valid scenarios generated")
        return
    
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    
    print(f"Dataset saved: {output_file}")
    print(f"Total scenarios: {len(df)}")
    print(f"Valid scenarios: {num_scenarios - failed_scenarios}/{num_scenarios}")
    if failed_scenarios > 0:
        print(f"Failed scenarios: {failed_scenarios}")
    
    print("\nSample data:")
    print(df[['time_0_to_1', 'time_1_to_2', 'speed_0_to_1', 
              'speed_1_to_2', 'ETA']].head(10))


if __name__ == "__main__":
    module_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(module_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    presets = {
        'demo': (10, os.path.join(data_dir, 'train_data_demo.csv')),
        'small': (50, os.path.join(data_dir, 'train_data_small.csv')),
        'full': (100, os.path.join(data_dir, 'train_data.csv'))
    }
    
    if len(sys.argv) > 1:
        preset = sys.argv[1].lower()
        if preset in presets:
            num, filename = presets[preset]
            generate_dataset(num_scenarios=num, output_file=filename)
        else:
            print(f"Unknown preset: {preset}")
            print(f"Usage: python -m 02_train.generate_dataset "
                  f"[{'/'.join(presets.keys())}]")
            sys.exit(1)
    else:
        generate_dataset(
            num_scenarios=100, 
            output_file=os.path.join(data_dir, 'train_data.csv')
        )