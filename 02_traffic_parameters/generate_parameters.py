import numpy as np
import pandas as pd
import sys
from typing import Dict

try:
    from .traffic_simulator import TrafficSimulator
except ImportError:
    from traffic_simulator import TrafficSimulator


def generate_traffic_parameters(intersection_distances: list = None,
                                output_file: str = 'traffic_parameters.csv') -> None:
    """
    Generate traffic parameters for different road intersection distances.
    
    Args:
        intersection_distances: List of distances from road intersection to train crossing (meters)
        output_file: CSV filename for output
    """
    if intersection_distances is None:
        intersection_distances = [300, 500, 1000]
    
    print(f"Generating traffic parameters")
    print(f"Road intersection distances: {intersection_distances} m")
    
    all_data = []
    
    for distance in intersection_distances:
        sim = TrafficSimulator(distance)
        
        for density in ['light', 'medium', 'heavy']:
            analysis = sim.analyze_traffic_density(density)
            
            for vehicle in analysis['vehicles']:
                data_point = {
                    'intersection_distance': distance,
                    'traffic_density': density,
                    'vehicle_type': vehicle['vehicle_type'],
                    'vehicle_id': vehicle['vehicle_id'],
                    'initial_speed': vehicle['initial_speed'],
                    'time_to_crossing': vehicle['time_to_crossing'],
                    'stopping_distance': vehicle['stopping_distance'],
                    'can_stop': vehicle['can_stop']
                }
                all_data.append(data_point)
    
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    
    print(f"\nDataset saved: {output_file}")
    print(f"Total data points: {len(df)}")
    print(f"\nSummary by road intersection distance:")
    
    for distance in intersection_distances:
        subset = df[df['intersection_distance'] == distance]
        avg_time = subset['time_to_crossing'].mean()
        max_time = subset['time_to_crossing'].max()
        print(f"  {distance}m: avg={avg_time:.2f}s, max={max_time:.2f}s")
    
    print(f"\nSample data:")
    print(df[['intersection_distance', 'traffic_density', 'vehicle_type', 
              'time_to_crossing', 'can_stop']].head(10))


def calculate_gate_timing(train_eta: float, 
                          intersection_distance: float,
                          safety_buffer: float = 2.0) -> Dict:
    """
    Calculate optimal gate closure and notification timings.
    
    Args:
        train_eta: Estimated time to arrival at train crossing (seconds)
        intersection_distance: Distance from road intersection to train crossing (meters)
        safety_buffer: Additional safety margin (seconds)
    
    Returns:
        Dictionary with timing recommendations
    """
    gate_closure_before_eta = 10.0
    gate_closure_time = train_eta - gate_closure_before_eta
    
    sim = TrafficSimulator(intersection_distance)
    notification = sim.calculate_notification_time(
        gate_closure_time,
        safety_buffer
    )
    
    return {
        'train_eta': train_eta,
        'gate_closure_time': max(0, gate_closure_time),
        'notification_time': notification['notification_time'],
        'gate_closure_before_eta': gate_closure_before_eta,
        'time_to_reach_crossing': notification['time_to_reach_crossing'],
        'safety_buffer': safety_buffer,
        'intersection_distance': intersection_distance,
        'note': 'Notify vehicles at road intersection to NOT proceed toward train crossing'
    }


def analyze_intersection_scenarios(intersection_distances: list = None) -> None:
    """
    Analyze and print timing scenarios for different road intersections.
    
    Args:
        intersection_distances: List of distances from road intersection to train crossing (meters)
    """
    if intersection_distances is None:
        intersection_distances = [300, 500, 1000]
    
    print("Gate Closure and Notification Timing Analysis")
    print("=" * 60)
    print("Road intersections are BEFORE the train crossing")
    print("Vehicles at intersection should NOT proceed after notification")
    print("=" * 60)
    
    example_etas = [30, 60, 90]
    
    for eta in example_etas:
        print(f"\nTrain ETA: {eta} seconds")
        print("-" * 60)
        
        for distance in intersection_distances:
            timing = calculate_gate_timing(eta, distance)
            
            print(f"\nRoad intersection at {distance}m from train crossing:")
            print(f"  Gate closes at train crossing: {timing['gate_closure_time']:.1f}s")
            print(f"  Notify road intersection: {timing['notification_time']:.1f}s")
            print(f"  Time to reach crossing: {timing['time_to_reach_crossing']:.1f}s")
            print(f"  Safety buffer: {timing['safety_buffer']:.1f}s")
            
            if timing['notification_time'] <= 0:
                print(f"  WARNING: Insufficient time for notification!")
                print(f"  Vehicles already at intersection may not have time to be warned")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'generate':
            generate_traffic_parameters()
        elif command == 'analyze':
            analyze_intersection_scenarios()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python generate_parameters.py [generate|analyze]")
            sys.exit(1)
    else:
        print("Generating traffic parameters...")
        generate_traffic_parameters()
        print("\nAnalyzing scenarios...")
        analyze_intersection_scenarios()