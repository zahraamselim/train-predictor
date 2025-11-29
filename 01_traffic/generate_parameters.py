"""Generate traffic parameters for different road intersection distances."""

import numpy as np
import pandas as pd
import sys
import os
from typing import Dict

try:
    from .traffic_simulator import TrafficSimulator
except ImportError:
    from traffic_simulator import TrafficSimulator

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config, update_vehicle_clearance


def generate_traffic_parameters(output_file: str = None) -> None:
    """
    Generate traffic parameters for different road intersection distances.
    Reads intersection distances from system config and writes clearance times back.
    
    Args:
        output_file: CSV filename for output (uses default module path if None)
    """
    if output_file is None:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(module_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, 'traffic_parameters.csv')
    
    config = get_scale_config()
    traffic_config = config['traffic']
    scale_mode = config['scale_mode']
    unit = 'cm' if scale_mode == 'demo' else 'm'
    
    intersection_distances = traffic_config['intersection_distances']
    print(f"Generating traffic parameters")
    print(f"Scale: {scale_mode} ({unit})")
    print(f"Intersection distances: {intersection_distances} {unit}")
    
    all_data = []
    clearance_by_density = {}
    
    for distance in intersection_distances:
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
    
    print(f"Dataset saved: {output_file}")
    print(f"Total data points: {len(df)}")
    
    for density in ['light', 'medium', 'heavy']:
        times = clearance_by_density[density]['times']
        min_time = round(min(times), 2)
        max_time = round(max(times), 2)
        avg_time = round(np.mean(times), 2)
        
        print(f"{density}: min={min_time}s, avg={avg_time}s, max={max_time}s")
        update_vehicle_clearance(density, min_time, max_time, avg_time)
    
    print("Updated system_config.yaml with clearance times")


def calculate_gate_timing(train_eta: float, 
                          intersection_distance: float) -> Dict:
    """
    Calculate optimal gate closure and notification timings.
    
    Args:
        train_eta: Estimated time to arrival at train crossing (seconds)
        intersection_distance: Distance from road intersection to train crossing
    
    Returns:
        Dictionary with timing recommendations
    """
    config = get_scale_config()
    gate_closure_offset = config['gates']['closure_before_eta']
    safety_buffer = config['traffic']['safety_buffer']
    
    gate_closure_time = train_eta - gate_closure_offset
    
    sim = TrafficSimulator(intersection_distance)
    notification = sim.calculate_notification_time(gate_closure_time, safety_buffer)
    
    return {
        'train_eta': train_eta,
        'gate_closure_time': max(0, gate_closure_time),
        'notification_time': notification['notification_time'],
        'gate_closure_offset': gate_closure_offset,
        'time_to_reach_crossing': notification['avg_clearance_time'],
        'safety_buffer': safety_buffer,
        'intersection_distance': intersection_distance,
    }


def analyze_intersection_scenarios() -> None:
    """Analyze and print timing scenarios for different road intersections."""
    config = get_scale_config()
    intersection_distances = config['traffic']['intersection_distances']
    scale_mode = config['scale_mode']
    unit = 'cm' if scale_mode == 'demo' else 'm'
    
    print("Gate Closure and Notification Timing Analysis")
    print(f"Scale: {scale_mode} ({unit})")
    
    example_etas = [30, 60, 90]
    
    for eta in example_etas:
        print(f"\nTrain ETA: {eta} seconds")
        
        for distance in intersection_distances:
            timing = calculate_gate_timing(eta, distance)
            
            print(f"  {distance}{unit}: "
                  f"gate={timing['gate_closure_time']:.1f}s, "
                  f"notify={timing['notification_time']:.1f}s")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'generate':
            generate_traffic_parameters()
        elif command == 'analyze':
            analyze_intersection_scenarios()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python -m 01_traffic.generate_parameters [generate|analyze]")
            sys.exit(1)
    else:
        print("Generating traffic parameters...")
        generate_traffic_parameters()
        print("\nAnalyzing scenarios...")
        analyze_intersection_scenarios()