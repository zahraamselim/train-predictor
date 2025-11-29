"""Train trajectory simulation and dataset generation."""

import numpy as np
import pandas as pd
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config

package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from train import TRAIN_TYPES, TrainPhysics


class TrainSimulator:
    """Train approach simulation."""
    
    def __init__(self, train_type: str, crossing_distance: float = None):
        self.physics = TrainPhysics(TRAIN_TYPES[train_type])
        self.train_type = train_type
        
        config = get_scale_config()
        train_config = config['train']
        self.crossing_distance = crossing_distance or train_config['crossing_distance']
        self.train_length = train_config['train_length']
        self.buffer_distance = train_config['buffer_distance']
    
    def simulate_approach(
        self, 
        initial_speed: float,
        grade: float,
        weather: str = 'clear',
        target_speed: float = None,
        dt: float = None
    ) -> List[dict]:
        """Simulate train approaching crossing."""
        speed = initial_speed / 3.6
        if target_speed is None:
            target_speed = initial_speed
        target_speed_ms = target_speed / 3.6
        
        if dt is None:
            if self.crossing_distance > 5000:
                dt = 1.0
            elif self.crossing_distance > 1000:
                dt = 0.5
            else:
                dt = 0.1
        
        distance = self.crossing_distance
        time = 0.0
        max_time = self.crossing_distance / (initial_speed / 3.6) * 3.0
        
        trajectory = []
        last_distance = distance
        stall_counter = 0
        max_speed_ms = self.physics.train.max_speed / 3.6
        
        while distance > -(self.train_length + self.buffer_distance):
            crossing_status = self._get_crossing_status(distance)
            
            accel = self.physics.calculate_acceleration(
                speed, grade, target_speed_ms, weather, braking=None
            )
            
            if speed > max_speed_ms:
                speed = max_speed_ms
                accel = min(accel, 0)
            
            speed_new = max(0, speed + accel * dt)
            distance_new = distance - (speed * dt + 0.5 * accel * dt**2)
            
            if abs(distance - last_distance) < 0.001 and distance > 0:
                stall_counter += 1
                if stall_counter > 50:
                    break
            else:
                stall_counter = 0
            
            last_distance = distance
            eta = distance / speed if speed > 0.1 and distance > 0 else 0
            
            trajectory.append({
                'time': round(time, 2),
                'distance_to_crossing': round(distance, 2),
                'speed': round(speed * 3.6, 2),
                'acceleration': round(accel, 3),
                'ETA': round(eta, 2),
                'grade': grade,
                'weather': weather,
                'train_type': self.train_type,
                'crossing_status': crossing_status
            })
            
            speed = speed_new
            distance = distance_new
            time += dt
            
            if time > max_time:
                break
        
        return trajectory
    
    def _get_crossing_status(self, distance: float) -> str:
        """Determine crossing status based on train position."""
        if distance > self.train_length:
            return 'approaching'
        elif distance > 0:
            return 'entering'
        elif distance > -self.train_length:
            return 'occupying'
        else:
            return 'cleared'


def generate_dataset(num_scenarios: int = 100, output_file: str = None):
    """Generate train approach dataset with sensor detections."""
    
    # Import sensor array here to avoid circular dependency
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), '02_sensors'))
    from sensor_array import SensorArray
    
    if output_file is None:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, 'train_data.csv')
    
    config = get_scale_config()
    train_config = config['train']
    scale_mode = config['scale_mode']
    unit = 'cm' if scale_mode == 'demo' else 'm'
    
    crossing_distance = train_config['crossing_distance']
    sensor_positions = train_config['sensor_positions']
    train_length = train_config['train_length']
    train_speeds = config['train_speeds']
    
    print(f"\nGenerating {num_scenarios} train scenarios ({scale_mode} scale)")
    print(f"Crossing distance: {crossing_distance} {unit}")
    print(f"Sensor positions: {sensor_positions} {unit}\n")
    
    all_data = []
    failed_scenarios = 0
    
    for i in range(num_scenarios):
        sensors = SensorArray(sensor_positions=sensor_positions)
        
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
            sensors.update(train_distance, current_time, train_length)
        
        detection_times = sensors.get_detection_times()
        
        sensor_0_entry = detection_times['sensor_0']['entry_time']
        sensor_1_entry = detection_times['sensor_1']['entry_time']
        sensor_2_entry = detection_times['sensor_2']['entry_time']
        
        if sensor_0_entry is None or sensor_1_entry is None or sensor_2_entry is None:
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
        
        if (i + 1) % 20 == 0:
            print(f"Progress: {i + 1}/{num_scenarios}")
    
    if len(all_data) == 0:
        print("Error: No valid scenarios generated")
        return
    
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    
    print(f"\nDataset saved: {output_file}")
    print(f"Valid scenarios: {len(df)}/{num_scenarios}")
    if failed_scenarios > 0:
        print(f"Failed scenarios: {failed_scenarios}")
    
    print(f"\nSample data:")
    print(df[['train_type', 'speed_0_to_1', 'speed_1_to_2', 'ETA']].head(3).to_string(index=False))
    
    print(f"\nSpeed statistics:")
    print(f"  Speed 0->1: {df['speed_0_to_1'].min():.1f} - {df['speed_0_to_1'].max():.1f} km/h")
    print(f"  Speed 1->2: {df['speed_1_to_2'].min():.1f} - {df['speed_1_to_2'].max():.1f} km/h")
    print(f"  ETA range: {df['ETA'].min():.1f} - {df['ETA'].max():.1f}s")


def validate_train():
    """Validate train module."""
    data_file = os.path.join(os.path.dirname(__file__), 'data', 'train_data.csv')
    
    print("\nTRAIN MODULE VALIDATION\n")
    
    results = []
    
    # Test 1: Train physics
    print("Testing train physics...")
    physics = TrainPhysics(TRAIN_TYPES['passenger'])
    
    force = physics.calculate_tractive_force(20)  # 20 m/s
    test1 = force > 0
    print(f"  Tractive force positive: {'PASS' if test1 else 'FAIL'}")
    results.append(test1)
    
    resistance = physics.calculate_resistance(20, 0, 'clear')
    test2 = resistance > 0
    print(f"  Resistance positive: {'PASS' if test2 else 'FAIL'}")
    results.append(test2)
    
    accel = physics.calculate_acceleration(20, 0, 25, 'clear')
    test3 = accel != 0
    print(f"  Acceleration calculated: {'PASS' if test3 else 'FAIL'}\n")
    results.append(test3)
    
    # Test 2: Dataset validation
    if os.path.exists(data_file):
        print("Validating dataset...")
        df = pd.read_csv(data_file)
        
        required_cols = ['train_type', 'sensor_0_entry', 'sensor_1_entry', 
                        'sensor_2_entry', 'speed_0_to_1', 'speed_1_to_2', 'ETA']
        
        test4 = all(col in df.columns for col in required_cols)
        print(f"  Required columns: {'PASS' if test4 else 'FAIL'}")
        results.append(test4)
        
        test5 = not df.isnull().any().any()
        print(f"  No NULL values: {'PASS' if test5 else 'FAIL'}")
        results.append(test5)
        
        test6 = (df['ETA'] > 0).all()
        print(f"  Positive ETA values: {'PASS' if test6 else 'FAIL'}")
        results.append(test6)
        
        # Test sensor timing order
        test7 = ((df['sensor_0_entry'] < df['sensor_1_entry']) & 
                 (df['sensor_1_entry'] < df['sensor_2_entry'])).all()
        print(f"  Sensor timing ordered: {'PASS' if test7 else 'FAIL'}")
        results.append(test7)
        
        print(f"\n  Dataset info:")
        print(f"  - Total scenarios: {len(df)}")
        print(f"  - Train types: {df['train_type'].value_counts().to_dict()}")
        print(f"  - Speed range: {df['speed_1_to_2'].min():.1f} - {df['speed_1_to_2'].max():.1f} km/h")
        print(f"  - ETA range: {df['ETA'].min():.1f} - {df['ETA'].max():.1f}s")
    else:
        print(f"Dataset not found: {data_file}")
        print("Run: python -m 03_train.simulator\n")
        results.append(False)
    
    print(f"\nValidation result: {'ALL TESTS PASSED' if all(results) else 'SOME TESTS FAILED'}")
    print(f"Passed: {sum(results)}/{len(results)}\n")
    
    return 0 if all(results) else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        sys.exit(validate_train())
    else:
        # Default dataset size
        num = 100
        if len(sys.argv) > 1:
            presets = {'demo': 10, 'small': 50, 'full': 100}
            num = presets.get(sys.argv[1], 100)
        
        generate_dataset(num_scenarios=num)
        print("\nRun validation with: python -m 03_train.simulator validate")