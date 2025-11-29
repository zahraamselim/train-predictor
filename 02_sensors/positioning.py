"""Calculate optimal IR sensor positions based on traffic requirements."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config, save_config


def calculate_sensor_positions(verbose=True):
    """
    Calculate optimal sensor positions.
    
    Requirements:
    1. Furthest sensor must detect train early enough for traffic to clear
    2. Multiple sensors needed for speed/acceleration calculation
    3. Sensors spaced for accurate ETA prediction
    
    Returns:
        List of sensor positions (distances from crossing in meters)
    """
    config = load_config()
    scale_mode = config['system']['scale_mode']
    
    # Get worst-case traffic clearance time
    vehicle_clearance = config['vehicle_clearance']
    max_clearance = max(
        vehicle_clearance['light']['max_time'],
        vehicle_clearance['medium']['max_time'],
        vehicle_clearance['heavy']['max_time']
    )
    
    # Safety parameters
    gate_closure_offset = config['gates']['closure_before_eta']
    safety_buffer = config['traffic'][f'{scale_mode}_scale']['safety_buffer']
    
    # Get fastest train speed (worst case)
    train_types = config['train_types']
    max_train_speed_kmh = max(t['max_speed'] for t in train_types.values())
    max_train_speed_ms = max_train_speed_kmh / 3.6
    
    # Calculate total warning time needed
    total_warning_time = max_clearance + safety_buffer + gate_closure_offset
    
    # Calculate ideal detection distance
    ideal_detection_distance = max_train_speed_ms * total_warning_time
    
    # Get available crossing distance
    train_config = config['train'][f'{scale_mode}_scale']
    crossing_distance = train_config['crossing_distance']
    
    # Use 90% of crossing distance as maximum
    max_sensor_distance = crossing_distance * 0.9
    
    # Choose actual detection distance
    if ideal_detection_distance > max_sensor_distance:
        if verbose:
            print(f"WARNING: Ideal distance ({ideal_detection_distance:.1f}m) exceeds")
            print(f"         available distance ({crossing_distance}m)")
            print(f"         Using maximum available ({max_sensor_distance:.1f}m)")
        detection_distance = max_sensor_distance
    else:
        detection_distance = ideal_detection_distance
    
    # Place 3 sensors at 30%, 60%, 100% of detection distance
    sensor_positions = [
        round(detection_distance * 1.0, 1),  # Furthest (100%)
        round(detection_distance * 0.6, 1),  # Middle (60%)
        round(detection_distance * 0.3, 1)   # Nearest (30%)
    ]
    
    if verbose:
        unit = 'cm' if scale_mode == 'demo' else 'm'
        print(f"\nSensor Position Calculation ({scale_mode} scale)")
        print(f"\nTraffic requirements:")
        print(f"  Max clearance time: {max_clearance:.2f}s")
        print(f"  Safety buffer: {safety_buffer:.2f}s")
        print(f"  Gate closure offset: {gate_closure_offset:.2f}s")
        print(f"  Total warning time: {total_warning_time:.2f}s")
        print(f"\nTrain constraints:")
        print(f"  Fastest speed: {max_train_speed_kmh:.1f} km/h ({max_train_speed_ms:.2f} m/s)")
        print(f"  Crossing distance: {crossing_distance}{unit}")
        print(f"\nCalculated positions:")
        print(f"  Ideal detection: {ideal_detection_distance:.1f}{unit}")
        print(f"  Actual detection: {detection_distance:.1f}{unit}")
        print(f"  Sensor 0 (furthest): {sensor_positions[0]}{unit}")
        print(f"  Sensor 1 (middle):   {sensor_positions[1]}{unit}")
        print(f"  Sensor 2 (nearest):  {sensor_positions[2]}{unit}")
        
        # Check if adequate warning time
        actual_warning_time = detection_distance / max_train_speed_ms
        if actual_warning_time < total_warning_time:
            print(f"\nWARNING: Actual warning ({actual_warning_time:.1f}s) < Required ({total_warning_time:.1f}s)")
            print(f"Recommendations:")
            print(f"  1. Increase crossing_distance to {ideal_detection_distance:.1f}{unit}")
            print(f"  2. Reduce vehicle clearance times")
            print(f"  3. Increase gate closure offset")
        else:
            print(f"\nWarning time adequate: {actual_warning_time:.1f}s")
    
    return sensor_positions


def update_sensor_positions(positions=None):
    """Update config with calculated sensor positions."""
    if positions is None:
        positions = calculate_sensor_positions(verbose=False)
    
    config = load_config()
    scale_mode = config['system']['scale_mode']
    
    config['train'][f'{scale_mode}_scale']['sensor_positions'] = positions
    save_config(config)
    
    return positions


def validate_sensors():
    """Validate sensor configuration."""
    print("\nSENSOR CONFIGURATION VALIDATION\n")
    
    config = load_config()
    scale_mode = config['system']['scale_mode']
    train_config = config['train'][f'{scale_mode}_scale']
    
    sensor_positions = train_config.get('sensor_positions', [])
    crossing_distance = train_config.get('crossing_distance')
    
    results = []
    
    # Test 1: Correct number of sensors
    test1 = len(sensor_positions) == 3
    print(f"Correct sensor count (3): {'PASS' if test1 else 'FAIL'}")
    results.append(test1)
    
    # Test 2: Sensors in decreasing order
    test2 = sensor_positions == sorted(sensor_positions, reverse=True)
    print(f"Sensors ordered (far to near): {'PASS' if test2 else 'FAIL'}")
    results.append(test2)
    
    # Test 3: All sensors before crossing
    test3 = all(pos > 0 for pos in sensor_positions)
    print(f"All sensors before crossing: {'PASS' if test3 else 'FAIL'}")
    results.append(test3)
    
    # Test 4: Furthest sensor within crossing distance
    test4 = sensor_positions[0] <= crossing_distance
    print(f"Furthest within crossing distance: {'PASS' if test4 else 'FAIL'}")
    results.append(test4)
    
    # Test 5: Adequate spacing between sensors
    spacing_01 = sensor_positions[0] - sensor_positions[1]
    spacing_12 = sensor_positions[1] - sensor_positions[2]
    min_spacing = sensor_positions[2] * 0.5  # At least 50% of nearest
    test5 = spacing_01 > min_spacing and spacing_12 > min_spacing
    print(f"Adequate sensor spacing: {'PASS' if test5 else 'FAIL'}")
    results.append(test5)
    
    # Show configuration
    unit = 'cm' if scale_mode == 'demo' else 'm'
    print(f"\nCurrent configuration ({scale_mode} scale):")
    print(f"  Crossing distance: {crossing_distance}{unit}")
    print(f"  Sensor positions: {sensor_positions} {unit}")
    print(f"  Spacing: {spacing_01:.1f}{unit}, {spacing_12:.1f}{unit}")
    
    # Test 6: Calculate and compare
    print(f"\nRecalculating optimal positions...")
    calculated = calculate_sensor_positions(verbose=False)
    test6 = sensor_positions == calculated
    print(f"Matches calculated positions: {'PASS' if test6 else 'FAIL'}")
    if not test6:
        print(f"  Current:    {sensor_positions}")
        print(f"  Calculated: {calculated}")
        print(f"  Run 'make sensors-apply' to update")
    results.append(test6)
    
    print(f"\nValidation result: {'ALL TESTS PASSED' if all(results) else 'SOME TESTS FAILED'}")
    print(f"Passed: {sum(results)}/{len(results)}\n")
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'calculate':
            calculate_sensor_positions()
        elif sys.argv[1] == 'apply':
            positions = update_sensor_positions()
            print(f"\nUpdated config with positions: {positions}")
        elif sys.argv[1] == 'validate':
            sys.exit(validate_sensors())
        else:
            print("Usage: python -m 02_sensors.positioning [calculate|apply|validate]")
    else:
        calculate_sensor_positions()