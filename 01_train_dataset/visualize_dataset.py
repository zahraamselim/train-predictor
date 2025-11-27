"""
Visualize generated train dataset to verify realism.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def visualize_dataset(csv_file: str = 'train_data.csv'):
    """
    Create comprehensive visualizations of the generated dataset.
    
    Args:
        csv_file: Path to the CSV file
    """
    df = pd.read_csv(csv_file)
    
    print(f"Dataset loaded: {len(df)} data points across {df['scenario_id'].nunique()} scenarios")
    print(f"\nTrain type distribution:")
    print(df.groupby('scenario_id')['train_type'].first().value_counts())
    print(f"\nWeather distribution:")
    print(df.groupby('scenario_id')['weather'].first().value_counts())
    
    fig, axes = plt.subplots(3, 3, figsize=(16, 12))
    fig.suptitle('Train Dataset Analysis', fontsize=16, fontweight='bold')
    
    # 1. Speed vs Distance profiles by train type
    ax = axes[0, 0]
    for train_type in df['train_type'].unique():
        subset = df[df['train_type'] == train_type]
        for scenario_id in subset['scenario_id'].unique()[:5]:  # Show first 5 scenarios per type
            scenario = subset[subset['scenario_id'] == scenario_id]
            ax.plot(scenario['distance_to_crossing'], scenario['speed'], 
                   alpha=0.6, linewidth=1.5, label=train_type if scenario_id == subset['scenario_id'].unique()[0] else "")
    ax.set_xlabel('Distance to Crossing (m)')
    ax.set_ylabel('Speed (km/h)')
    ax.set_title('Speed vs Distance (Sample Scenarios)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. ETA vs Distance
    ax = axes[0, 1]
    for train_type in df['train_type'].unique():
        subset = df[df['train_type'] == train_type]
        scenario = subset[subset['scenario_id'] == subset['scenario_id'].unique()[0]]
        ax.plot(scenario['distance_to_crossing'], scenario['ETA'], 
               label=train_type, linewidth=2)
    ax.set_xlabel('Distance to Crossing (m)')
    ax.set_ylabel('ETA (seconds)')
    ax.set_title('ETA vs Distance by Train Type')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Acceleration profiles
    ax = axes[0, 2]
    for train_type in df['train_type'].unique():
        subset = df[df['train_type'] == train_type]
        scenario = subset[subset['scenario_id'] == subset['scenario_id'].unique()[0]]
        ax.plot(scenario['time'], scenario['acceleration'], 
               label=train_type, linewidth=2)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Acceleration (m/s²)')
    ax.set_title('Acceleration Profiles')
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. Speed distribution by train type
    ax = axes[1, 0]
    for train_type in df['train_type'].unique():
        subset = df[df['train_type'] == train_type]
        initial_speeds = subset.groupby('scenario_id')['speed'].first()
        ax.hist(initial_speeds, bins=20, alpha=0.6, label=train_type)
    ax.set_xlabel('Initial Speed (km/h)')
    ax.set_ylabel('Frequency')
    ax.set_title('Initial Speed Distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 5. Grade distribution
    ax = axes[1, 1]
    grades = df.groupby('scenario_id')['grade'].first()
    ax.hist(grades, bins=30, color='green', alpha=0.7, edgecolor='black')
    ax.set_xlabel('Grade (%)')
    ax.set_ylabel('Frequency')
    ax.set_title('Track Grade Distribution')
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Flat')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 6. Braking behavior (speed reduction over last 500m)
    ax = axes[1, 2]
    for train_type in df['train_type'].unique():
        subset = df[df['train_type'] == train_type]
        for scenario_id in subset['scenario_id'].unique()[:3]:
            scenario = subset[subset['scenario_id'] == scenario_id]
            braking_zone = scenario[scenario['distance_to_crossing'] <= 500]
            if len(braking_zone) > 0:
                ax.plot(braking_zone['distance_to_crossing'], braking_zone['speed'], 
                       alpha=0.7, linewidth=2, label=f"{train_type}" if scenario_id == subset['scenario_id'].unique()[0] else "")
    ax.set_xlabel('Distance to Crossing (m)')
    ax.set_ylabel('Speed (km/h)')
    ax.set_title('Braking Zone (Last 500m)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.invert_xaxis()
    
    # 7. Time to crossing vs initial distance
    ax = axes[2, 0]
    for train_type in df['train_type'].unique():
        subset = df[df['train_type'] == train_type]
        total_times = subset.groupby('scenario_id')['time'].max()
        ax.scatter(range(len(total_times)), total_times, alpha=0.6, label=train_type, s=50)
    ax.set_xlabel('Scenario Index')
    ax.set_ylabel('Total Time to Crossing (s)')
    ax.set_title('Journey Duration by Train Type')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 8. Weather effect on braking
    ax = axes[2, 1]
    weather_colors = {'clear': 'blue', 'rain': 'gray', 'fog': 'lightgray'}
    for weather in df['weather'].unique():
        subset = df[df['weather'] == weather]
        for scenario_id in subset['scenario_id'].unique()[:2]:
            scenario = subset[subset['scenario_id'] == scenario_id]
            braking = scenario[scenario['acceleration'] < -0.1]
            if len(braking) > 0:
                ax.plot(braking['time'], braking['speed'], 
                       color=weather_colors.get(weather, 'black'),
                       alpha=0.7, linewidth=2,
                       label=weather if scenario_id == subset['scenario_id'].unique()[0] else "")
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Speed (km/h)')
    ax.set_title('Braking Under Different Weather')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 9. Grade effect on speed
    ax = axes[2, 2]
    scenario_stats = df.groupby('scenario_id').agg({
        'grade': 'first',
        'speed': 'mean',
        'train_type': 'first'
    })
    for train_type in scenario_stats['train_type'].unique():
        subset = scenario_stats[scenario_stats['train_type'] == train_type]
        ax.scatter(subset['grade'], subset['speed'], 
                  alpha=0.6, s=50, label=train_type)
    ax.set_xlabel('Grade (%)')
    ax.set_ylabel('Average Speed (km/h)')
    ax.set_title('Grade Effect on Average Speed')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_file = csv_file.replace('.csv', '_visualization.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to: {output_file}")
    plt.show()


def print_sample_scenarios(csv_file: str = 'train_data.csv', n: int = 3):
    """
    Print detailed information about sample scenarios.
    
    Args:
        csv_file: Path to the CSV file
        n: Number of scenarios to display
    """
    df = pd.read_csv(csv_file)
    
    print(f"\n{'='*80}")
    print(f"SAMPLE SCENARIOS (showing {n} examples)")
    print(f"{'='*80}\n")
    
    for i, scenario_id in enumerate(df['scenario_id'].unique()[:n]):
        scenario = df[df['scenario_id'] == scenario_id]
        
        print(f"Scenario {scenario_id}:")
        print(f"  Train Type: {scenario['train_type'].iloc[0]}")
        print(f"  Weather: {scenario['weather'].iloc[0]}")
        print(f"  Grade: {scenario['grade'].iloc[0]:.2f}%")
        print(f"  Initial Speed: {scenario['speed'].iloc[0]:.1f} km/h")
        print(f"  Final Speed: {scenario['speed'].iloc[-1]:.1f} km/h")
        print(f"  Total Time: {scenario['time'].iloc[-1]:.1f} seconds")
        print(f"  Distance Traveled: {scenario['distance_to_crossing'].iloc[0]:.0f} meters")
        print(f"  Data Points: {len(scenario)}")
        
        braking_points = scenario[scenario['acceleration'] < -0.1]
        if len(braking_points) > 0:
            print(f"  Braking Started: {braking_points['distance_to_crossing'].iloc[0]:.0f}m before crossing")
        print()


if __name__ == "__main__":
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'train_data.csv'
    
    print_sample_scenarios(csv_file)
    visualize_dataset(csv_file)