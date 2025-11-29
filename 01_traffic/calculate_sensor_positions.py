"""
Calculate optimal IR sensor positions based on traffic clearance requirements.
Sensors must be positioned to give enough warning time for the FASTEST train.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config, save_config


def calculate_sensor_positions():
    """
    Calculate sensor positions based on:
    1. Traffic clearance times (worst case)
    2. Fastest train speed (worst case)
    3. Safety buffers
    4. Available crossing distance
    
    Returns positions as distances from crossing.
    """
    config = load_config()
    scale_mode = config['system']['scale_mode']
    
    # Get maximum clearance time across all traffic densities
    vehicle_clearance = config['vehicle_clearance']
    max_clearance = max(
        vehicle_clearance['light']['max_time'],
        vehicle_clearance['medium']['max_time'],
        vehicle_clearance['heavy']['max_time']
    )
    
    gate_closure_offset = config['gates']['closure_before_eta']
    safety_buffer = config['traffic'][f'{scale_mode}_scale']['safety_buffer']
    
    # Get fastest train speed
    train_types = config['train_types']
    max_train_speed_kmh = max(t['max_speed'] for t in train_types.values())
    max_train_speed_ms = max_train_speed_kmh / 3.6
    
    # Calculate total warning time needed
    total_warning_time = max_clearance + safety_buffer + gate_closure_offset
    
    # Calculate ideal detection distance
    ideal_detection_distance = max_train_speed_ms * total_warning_time
    
    # Get available crossing distance (where train starts)
    train_config = config['train'][f'{scale_mode}_scale']
    crossing_distance = train_config['crossing_distance']
    
    # Sensors must be within crossing distance
    # Use 90% of crossing distance as maximum to leave buffer
    max_sensor_distance = crossing_distance * 0.9
    
    # If ideal distance exceeds available distance, use maximum available
    if ideal_detection_distance > max_sensor_distance:
        print(f"WARNING: Ideal detection distance ({ideal_detection_distance:.1f}m) exceeds")
        print(f"         available crossing distance ({crossing_distance}m)")
        print(f"         Using maximum available distance ({max_sensor_distance:.1f}m)")
        min_detection_distance = max_sensor_distance
    else:
        min_detection_distance = ideal_detection_distance
    
    # Place sensors at 30%, 60%, and 100% of detection distance
    sensor_3_pos = round(min_detection_distance * 0.3, 1)
    sensor_2_pos = round(min_detection_distance * 0.6, 1)
    sensor_1_pos = round(min_detection_distance * 1.0, 1)
    
    positions = [sensor_1_pos, sensor_2_pos, sensor_3_pos]
    
    print("Sensor Position Calculation")
    print(f"Scale mode: {scale_mode}")
    print()
    print("Traffic Requirements:")
    print(f"  Max clearance time: {max_clearance:.2f}s")
    print(f"  Safety buffer: {safety_buffer:.2f}s")
    print(f"  Gate closure offset: {gate_closure_offset:.2f}s")
    print(f"  Total warning time needed: {total_warning_time:.2f}s")
    print()
    print("Train Constraints:")
    print(f"  Fastest train speed: {max_train_speed_kmh:.1f} km/h ({max_train_speed_ms:.2f} m/s)")
    print(f"  Crossing distance: {crossing_distance}m")
    print()
    print("Calculated Positions:")
    print(f"  Ideal detection distance: {ideal_detection_distance:.1f}m")
    print(f"  Actual detection distance: {min_detection_distance:.1f}m")
    print(f"  Sensor 1 (furthest): {sensor_1_pos}m from crossing")
    print(f"  Sensor 2 (middle):   {sensor_2_pos}m from crossing")
    print(f"  Sensor 3 (nearest):  {sensor_3_pos}m from crossing")
    
    # Warning if sensors won't provide enough warning time
    actual_warning_time = min_detection_distance / max_train_speed_ms
    if actual_warning_time < total_warning_time:
        print()
        print(f"WARNING: Actual warning time ({actual_warning_time:.1f}s) is less than")
        print(f"         required warning time ({total_warning_time:.1f}s)")
        print(f"         System may not have enough time to clear traffic!")
        print()
        print("Recommendations:")
        print(f"  1. Increase crossing_distance to at least {ideal_detection_distance:.1f}m")
        print(f"  2. Reduce maximum vehicle clearance times")
        print(f"  3. Increase gate closure offset time")
    
    return positions


def update_sensor_positions_in_config(positions):
    """Update config with calculated sensor positions."""
    config = load_config()
    scale_mode = config['system']['scale_mode']
    
    config['train'][f'{scale_mode}_scale']['sensor_positions'] = positions
    
    save_config(config)
    print("\nUpdated sensor positions in config")


if __name__ == "__main__":
    positions = calculate_sensor_positions()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--apply':
        update_sensor_positions_in_config(positions)
    else:
        print("\nRun with --apply to update config file")