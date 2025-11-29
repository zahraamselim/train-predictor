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
    Generate diverse training scenarios with IR sensor readings.
    
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
    
    print(f"Generating {num_scenarios} scenarios")
    print(f"Scale: {scale_mode} ({unit})")
    print(f"Crossing distance: {crossing_distance} {unit}")
    print(f"Sensor positions: {sensor_positions} {unit}")
    
    ir_array = IRSensorArray(sensor_positions=sensor_positions)
    train_speeds = config['train_speeds']
    all_data = []
    failed_scenarios = 0
    
    for i in range(num_scenarios):
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
            ir_readings = ir_array.get_readings(train_distance, point['weather'])
            
            point['IR1'] = ir_readings[0]
            point['IR2'] = ir_readings[1]
            point['IR3'] = ir_readings[2]
            point['scenario_id'] = i
        
        all_data.extend(trajectory)
        
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_scenarios}")
    
    if len(all_data) == 0:
        print("Error: No valid scenarios generated")
        return
    
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    
    print(f"Dataset saved: {output_file}")
    print(f"Total points: {len(df)}")
    print(f"Valid scenarios: {num_scenarios - failed_scenarios}/{num_scenarios}")
    if failed_scenarios > 0:
        print(f"Failed scenarios: {failed_scenarios}")
    
    print(f"Sample data:")
    print(df[['distance_to_crossing', 'speed', 'ETA', 'IR1', 'IR2', 'IR3']].head(10))


if __name__ == "__main__":
    presets = {
        'demo': (10, '01_train_dataset/data/train_data_demo.csv'),
        'small': (50, '01_train_dataset/data/train_data_small.csv'),
        'full': (100, '01_train_dataset/data/train_data.csv')
    }
    
    if len(sys.argv) > 1:
        preset = sys.argv[1].lower()
        if preset in presets:
            num, filename = presets[preset]
            generate_dataset(num_scenarios=num, output_file=filename)
        else:
            print(f"Unknown preset: {preset}")
            print(f"Usage: python -m 01_train_dataset.generate_dataset [{'/'.join(presets.keys())}]")
            sys.exit(1)
    else:
        generate_dataset(num_scenarios=100, output_file='01_train_dataset/data/train_data.csv')