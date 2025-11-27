import numpy as np
import sys

try:
    from .train_simulator import TrainSimulator
except ImportError:
    from train_simulator import TrainSimulator

def generate_dataset(num_scenarios: int = 100, 
                     crossing_distance: float = 2000,
                     output_file: str = 'train_data.csv') -> None:
    """
    Generate diverse training scenarios.
    
    Variations include:
    - Train types (passenger, freight, express)
    - Initial speeds (40-120 km/h range, type-dependent)
    - Grades (-2% to +2%, realistic for mainline railways)
    - Weather conditions (clear, rain, fog)
    
    Args:
        num_scenarios: Number of unique scenarios to generate
        crossing_distance: Distance from start to crossing (meters)
        output_file: CSV filename for output
    """
    import pandas as pd
    
    all_data = []
    failed_scenarios = 0
    
    for i in range(num_scenarios):
        # Random scenario parameters
        train_type = np.random.choice(['passenger', 'freight', 'express'])
        
        # Speed range depends on train type (higher minimum for freight on grades)
        if train_type == 'freight':
            speed = np.random.uniform(50, 80)  # Increased minimum from 40
        elif train_type == 'express':
            speed = np.random.uniform(90, 140)  # Increased minimum from 80
        else:
            speed = np.random.uniform(60, 120)  # Increased minimum from 50
        
        # Reduced grade range to avoid physics edge cases
        grade = np.random.uniform(-2, 2)  # Was -3 to 3
        weather = np.random.choice(['clear', 'rain', 'fog'], p=[0.7, 0.2, 0.1])
        
        # Run simulation
        sim = TrainSimulator(train_type, crossing_distance)
        trajectory = sim.simulate_approach(speed, grade, weather)
        
        # Validate scenario completed successfully
        if len(trajectory) == 0 or trajectory[-1]['distance_to_crossing'] > 10:
            # Scenario failed to complete
            failed_scenarios += 1
            print(f"Warning: Scenario {i} failed to complete (train didn't reach crossing)")
            continue
        
        # Add scenario ID
        for point in trajectory:
            point['scenario_id'] = i
        
        all_data.extend(trajectory)
        
        if (i + 1) % 10 == 0:
            print(f"Generated {i + 1}/{num_scenarios} scenarios")
    
    # Save to CSV
    if len(all_data) == 0:
        print("ERROR: No valid scenarios generated!")
        return
    
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    print(f"\nDataset saved to {output_file}")
    print(f"Total data points: {len(df)}")
    print(f"Valid scenarios: {num_scenarios - failed_scenarios}/{num_scenarios}")
    if failed_scenarios > 0:
        print(f"Failed scenarios: {failed_scenarios}")
    print(f"\nColumns: {list(df.columns)}")


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        preset = sys.argv[1].lower()
        
        if preset == 'demo':
            generate_dataset(num_scenarios=10, output_file='train_data_demo.csv')
        elif preset == 'small':
            generate_dataset(num_scenarios=50, output_file='train_data_small.csv')
        elif preset == 'full':
            generate_dataset(num_scenarios=100, output_file='train_data.csv')
        else:
            print(f"Unknown preset: {preset}")
            print("Usage: python generate_dataset.py [demo|small|full]")
            sys.exit(1)
    else:
        # Default
        generate_dataset(num_scenarios=100, output_file='train_data.csv')
