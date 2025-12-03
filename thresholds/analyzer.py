"""
Calculate control thresholds from collected data
Run: python -m thresholds.analyzer
"""
import pandas as pd
import yaml
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from utils.logger import Logger


class ThresholdAnalyzer:
    def __init__(self, config_path='thresholds/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.data_dir = Path('outputs/data')
        self.results_dir = Path('outputs/results')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.plots_dir = Path('outputs/plots')
        self.plots_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze(self):
        """Calculate all thresholds"""
        Logger.section("Calculating thresholds")
        
        clearance_file = self.data_dir / 'clearances.csv'
        travel_file = self.data_dir / 'travels.csv'
        
        if not clearance_file.exists() or not travel_file.exists():
            Logger.log("Error: Data files not found. Run collector first:")
            Logger.log("  python -m thresholds.network")
            Logger.log("  python -m thresholds.collector")
            return None
        
        clearances = pd.read_csv(clearance_file)
        travels = pd.read_csv(travel_file)
        
        if len(clearances) == 0 or len(travels) == 0:
            Logger.log("Error: Data files are empty. Run collector first:")
            Logger.log("  python -m thresholds.collector")
            return None
        
        Logger.log(f"Loaded: {len(clearances)} clearances, {len(travels)} travels")
        
        if len(clearances) < 100 or len(travels) < 50:
            Logger.log("Warning: Low sample count, results may be inaccurate")
        
        safety = self.config['safety']
        
        if len(clearances) >= 100:
            closure = clearances['clearance_time'].quantile(0.95) + safety['margin_close']
        else:
            closure = clearances['clearance_time'].max() + safety['margin_close']
        
        opening = safety['margin_open']
        
        if len(travels) >= 50:
            travel = travels['travel_time'].quantile(0.95)
        else:
            travel = travels['travel_time'].max()
        
        notification = travel + safety['driver_reaction'] + closure
        
        max_speed = 39.0
        detect_dist = notification * max_speed * 1.3
        
        sensor_0 = min(detect_dist * 3.0, 1500)
        sensor_1 = min(detect_dist * 1.8, 1000)
        sensor_2 = max(detect_dist * 0.9, 300)
        
        thresholds = {
            'closure_before_eta': float(closure),
            'opening_after_etd': float(opening),
            'notification_time': float(notification),
            'sensor_0': float(sensor_0),
            'sensor_1': float(sensor_1),
            'sensor_2': float(sensor_2),
            'max_train_speed': float(max_speed),
            'samples': {
                'clearances': len(clearances),
                'travels': len(travels)
            }
        }
        
        output = self.results_dir / 'thresholds.yaml'
        with open(output, 'w') as f:
            yaml.dump(thresholds, f, default_flow_style=False)
        
        Logger.log(f"Saved to {output}")
        self._print_summary(thresholds)
        self._plot_results(clearances, travels, thresholds)
        
        return thresholds
    
    def _print_summary(self, t):
        """Print results"""
        print("\nThreshold Results")
        print(f"Close gates: {t['closure_before_eta']:.2f}s before train")
        print(f"Open gates: {t['opening_after_etd']:.2f}s after train")
        print(f"Notify intersection: {t['notification_time']:.2f}s before train")
        print(f"Sensor 0: {t['sensor_0']:.0f}m")
        print(f"Sensor 1: {t['sensor_1']:.0f}m")
        print(f"Sensor 2: {t['sensor_2']:.0f}m")
        print(f"Max speed: {t['max_train_speed']:.1f} m/s ({t['max_train_speed']*3.6:.1f} km/h)")
        print()
    
    def _plot_results(self, clearances, travels, thresholds):
        """Generate visualization plots"""
        Logger.section("Generating plots")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        ax = axes[0, 0]
        ax.hist(clearances['clearance_time'], bins=30, edgecolor='black', alpha=0.7, color='blue')
        ax.axvline(clearances['clearance_time'].quantile(0.95), 
                   color='red', linestyle='--', linewidth=2, label='95th percentile')
        ax.axvline(thresholds['closure_before_eta'], 
                   color='green', linestyle='-', linewidth=2, label='Closure threshold')
        ax.set_xlabel('Clearance Time (seconds)')
        ax.set_ylabel('Frequency')
        ax.set_title('Vehicle Clearance Times')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        ax = axes[0, 1]
        ax.hist(travels['travel_time'], bins=30, edgecolor='black', alpha=0.7, color='green')
        ax.axvline(travels['travel_time'].quantile(0.95), 
                   color='red', linestyle='--', linewidth=2, label='95th percentile')
        ax.set_xlabel('Travel Time (seconds)')
        ax.set_ylabel('Frequency')
        ax.set_title('Intersection to Crossing Travel Times')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        ax = axes[0, 2]
        if clearances['speed'].std() > 0.01:
            ax.scatter(clearances['speed'], clearances['clearance_time'], alpha=0.5, s=20)
            ax.set_xlabel('Vehicle Speed (m/s)')
            ax.set_ylabel('Clearance Time (seconds)')
            ax.set_title('Clearance Time vs Vehicle Speed')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No speed variation', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Clearance Time vs Vehicle Speed')
        
        ax = axes[1, 0]
        sensors = [thresholds['sensor_0'], thresholds['sensor_1'], thresholds['sensor_2']]
        colors = ['red', 'orange', 'green']
        bars = ax.barh(['Sensor 0', 'Sensor 1', 'Sensor 2'], sensors, color=colors, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Distance Before Crossing (meters)')
        ax.set_title('Sensor Positions')
        ax.grid(True, alpha=0.3, axis='x')
        for i, (bar, sensor) in enumerate(zip(bars, sensors)):
            ax.text(sensor, i, f' {sensor:.0f}m', va='center', fontweight='bold')
        
        ax = axes[1, 1]
        sorted_clear = np.sort(clearances['clearance_time'])
        cumulative = np.arange(1, len(sorted_clear) + 1) / len(sorted_clear) * 100
        ax.plot(sorted_clear, cumulative, linewidth=2)
        ax.axhline(95, color='red', linestyle='--', linewidth=2, label='95th percentile')
        ax.axvline(clearances['clearance_time'].quantile(0.95), 
                   color='red', linestyle='--', linewidth=2)
        ax.set_xlabel('Clearance Time (seconds)')
        ax.set_ylabel('Cumulative Percentage')
        ax.set_title('Clearance Time CDF')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        ax = axes[1, 2]
        ax.axis('off')
        summary = f"""Threshold Summary

Gate Control:
  Close: {thresholds['closure_before_eta']:.2f}s before train
  Open: {thresholds['opening_after_etd']:.2f}s after train

Notification:
  Warn: {thresholds['notification_time']:.2f}s before train

Max Train Speed:
  {thresholds['max_train_speed']:.1f} m/s ({thresholds['max_train_speed']*3.6:.1f} km/h)

Data Samples:
  Clearances: {thresholds['samples']['clearances']}
  Travels: {thresholds['samples']['travels']}
"""
        ax.text(0.1, 0.5, summary, fontsize=10, family='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plot_path = self.plots_dir / 'thresholds_analysis.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved plot: {plot_path}")
        plt.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze threshold data')
    parser.add_argument('--config', default='thresholds/config.yaml', help='Config file')
    args = parser.parse_args()
    
    analyzer = ThresholdAnalyzer(args.config)
    analyzer.analyze()