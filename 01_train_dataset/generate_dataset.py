import numpy as np
import pandas as pd
import sys

try:
    from .train_simulator import TrainSimulator
    from .config import get_config, get_unit
except ImportError:
    from train_simulator import TrainSimulator
    from config import get_config, get_unit


def simulate_IR_sensor(distance: float, weather: str, sensor_constant: float = 10000) -> float:
    """
    Simulate IR sensor reading with realistic noise.
    Uses inverse square law: IR intensity = K / distance²
    
    Args:
        distance: Distance from sensor to train (meters or cm depending on scale)
        weather: 'clear', 'rain', or 'fog'
        sensor_constant: Calibration constant K for inverse square law
    
    Returns:
        IR sensor reading in arbitrary units
    """
    if distance <= 0.1:
        return sensor_constant
    
    base_reading = sensor_constant / (distance ** 2)
    
    noise_factors = {'clear': 0.05, 'rain': 0.15, 'fog': 0.25}
    noise_std = base_reading * noise_factors.get(weather, 0.05)
    noise = np.random.normal(0, noise_std)
    
    return max(0, base_reading + noise)


def generate_dataset(num_scenarios: int = 100, 
                     output_file: str = 'train_data.csv') -> None:
    """
    Generate diverse training scenarios with IR sensor readings.
    Trains are already in motion at initial_speed (not starting from rest).
    
    Args:
        num_scenarios: Number of unique scenarios to generate
        output_file: CSV filename for output
    """
    config = get_config()
    unit = get_unit()
    
    crossing_distance = config['crossing_distance']
    sensor_positions = config['sensor_positions']
    
    print(f"Generating {num_scenarios} scenarios")
    print(f"Scale: {unit}")
    print(f"Crossing distance: {crossing_distance} {unit}")
    print(f"Sensor positions: {sensor_positions} {unit}")
    
    all_data = []
    failed_scenarios = 0
    
    for i in range(num_scenarios):
        train_type = np.random.choice(['passenger', 'freight', 'express'])
        
        if train_type == 'freight':
            initial_speed = np.random.uniform(50, 80)
            target_speed = initial_speed + np.random.uniform(-5, 5)
        elif train_type == 'express':
            initial_speed = np.random.uniform(90, 140)
            target_speed = initial_speed + np.random.uniform(-10, 10)
        else:
            initial_speed = np.random.uniform(60, 120)
            target_speed = initial_speed + np.random.uniform(-8, 8)
        
        grade = np.random.uniform(-2, 2)
        weather = np.random.choice(['clear', 'rain', 'fog'], p=[0.7, 0.2, 0.1])
        
        sim = TrainSimulator(train_type, crossing_distance)
        trajectory = sim.simulate_approach(initial_speed, grade, weather, target_speed)
        
        if len(trajectory) == 0 or trajectory[-1]['distance_to_crossing'] > 10:
            failed_scenarios += 1
            continue
        
        for point in trajectory:
            train_distance = point['distance_to_crossing']
            
            ir_readings = []
            for sensor_pos in sensor_positions:
                sensor_distance = abs(train_distance - sensor_pos)
                sensor_distance = max(sensor_distance, 0.1)
                ir_reading = simulate_IR_sensor(sensor_distance, point['weather'])
                ir_readings.append(round(ir_reading, 4))
            
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
    
    print(f"\nDataset saved: {output_file}")
    print(f"Total points: {len(df)}")
    print(f"Valid scenarios: {num_scenarios - failed_scenarios}/{num_scenarios}")
    if failed_scenarios > 0:
        print(f"Failed scenarios: {failed_scenarios}")
    
    print(f"\nSample data:")
    print(df[['distance_to_crossing', 'speed', 'ETA', 'IR1', 'IR2', 'IR3']].head(10))


if __name__ == "__main__":
    presets = {
        'demo': (10, 'train_data_demo.csv'),
        'small': (50, 'train_data_small.csv'),
        'full': (100, 'train_data.csv')
    }
    
    if len(sys.argv) > 1:
        preset = sys.argv[1].lower()
        if preset in presets:
            num, filename = presets[preset]
            generate_dataset(num_scenarios=num, output_file=filename)
        else:
            print(f"Unknown preset: {preset}")
            print(f"Usage: python generate_dataset.py [{'/'.join(presets.keys())}]")
            sys.exit(1)
    else:
        generate_dataset(num_scenarios=100, output_file='train_data.csv')