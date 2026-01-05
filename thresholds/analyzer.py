"""
Calculate control thresholds from collected data
Run: python -m thresholds.analyzer
"""
import pandas as pd
import yaml
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET
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
    
    def _get_max_train_speed(self):
        """Extract maximum train speed from network routes"""
        try:
            tree = ET.parse('thresholds.rou.xml')
            root = tree.getroot()
            
            max_speed = 0.0
            for vtype in root.findall('vType'):
                vid = vtype.get('id', '')
                if 'train' in vid.lower():
                    speed = float(vtype.get('maxSpeed', 0))
                    max_speed = max(max_speed, speed)
                    Logger.log(f"Found train type '{vid}': {speed} m/s")
            
            if max_speed > 0:
                return max_speed
            else:
                Logger.log("WARNING: No train types found, using default 39.0 m/s")
                return 39.0
        except FileNotFoundError:
            Logger.log("WARNING: thresholds.rou.xml not found, using default 39.0 m/s")
            return 39.0
        except Exception as e:
            Logger.log(f"WARNING: Could not read train speeds ({e}), using default 39.0 m/s")
            return 39.0
    
    def analyze(self):
        """Calculate all thresholds"""
        Logger.section("Calculating thresholds")
        
        clearance_file = self.data_dir / 'clearances.csv'
        travel_file = self.data_dir / 'travels.csv'
        
        if not clearance_file.exists() or not travel_file.exists():
            Logger.log("Data files not found")
            Logger.log("Run: make th-network && make th-collect")
            return None
        
        clearances = pd.read_csv(clearance_file)
        travels = pd.read_csv(travel_file)
        
        if len(clearances) == 0 or len(travels) == 0:
            Logger.log("Data files are empty")
            Logger.log("Run: make th-collect")
            return None
        
        Logger.log(f"Loaded: {len(clearances)} clearances, {len(travels)} travels")
        
        if len(clearances) < 100 or len(travels) < 50:
            Logger.log("Warning: Low sample count, results may be inaccurate")
        
        safety = self.config['safety']
        
        if len(clearances) >= 100:
            clearance_p95 = clearances['clearance_time'].quantile(0.95)
        else:
            clearance_p95 = clearances['clearance_time'].max()
        
        closure = clearance_p95 + safety['margin_close']
        opening = safety['margin_open']
        
        if len(travels) >= 50:
            travel_p95 = travels['travel_time'].quantile(0.95)
        else:
            travel_p95 = travels['travel_time'].max()
        
        notification = travel_p95 + safety['driver_reaction'] + closure
        
        max_speed = self._get_max_train_speed()
        detect_dist = notification * max_speed * 1.3
        
        sensor_0 = min(detect_dist * 3.0, 1500)
        sensor_1 = min(detect_dist * 1.8, 1000)
        sensor_2_raw = detect_dist * 0.9
        sensor_2 = max(sensor_2_raw, 300)
        
        if sensor_2 >= sensor_1:
            Logger.log(f"WARNING: Sensor 2 ({sensor_2:.0f}m) >= Sensor 1 ({sensor_1:.0f}m)")
            sensor_2 = sensor_1 * 0.8
            sensor_2 = max(sensor_2, 300)
            Logger.log(f"Corrected Sensor 2 to {sensor_2:.0f}m")
        
        thresholds = {
            'closure_before_eta': float(closure),
            'opening_after_etd': float(opening),
            'notification_time': float(notification),
            'sensor_positions': [float(sensor_0), float(sensor_1), float(sensor_2)],
            'max_train_speed': float(max_speed),
            'statistics': {
                'clearance_mean': float(clearances['clearance_time'].mean()),
                'clearance_p95': float(clearance_p95),
                'clearance_max': float(clearances['clearance_time'].max()),
                'travel_mean': float(travels['travel_time'].mean()),
                'travel_p95': float(travel_p95),
                'travel_max': float(travels['travel_time'].max()),
                'n_clearances': len(clearances),
                'n_travels': len(travels)
            },
            'config': {
                'margin_close': safety['margin_close'],
                'margin_open': safety['margin_open'],
                'driver_reaction': safety['driver_reaction']
            }
        }
        
        yaml_path = self.results_dir / 'thresholds.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(thresholds, f, default_flow_style=False, sort_keys=False)
        Logger.log(f"Saved: {yaml_path}")
        
        json_path = self.results_dir / 'thresholds.json'
        with open(json_path, 'w') as f:
            json.dump(thresholds, f, indent=2)
        Logger.log(f"Saved: {json_path}")
        
        self._print_summary(thresholds)
        self._plot_results(clearances, travels, thresholds)
        
        return thresholds
    
    def _print_summary(self, t):
        """Print results"""
        Logger.log("\nThreshold Results")
        Logger.log(f"Close gates: {t['closure_before_eta']:.2f}s before train")
        Logger.log(f"Open gates: {t['opening_after_etd']:.2f}s after train")
        Logger.log(f"Notify traffic: {t['notification_time']:.2f}s before train")
        Logger.log(f"Sensor 0: {t['sensor_positions'][0]:.0f}m")
        Logger.log(f"Sensor 1: {t['sensor_positions'][1]:.0f}m")
        Logger.log(f"Sensor 2: {t['sensor_positions'][2]:.0f}m")
        Logger.log(f"Max speed: {t['max_train_speed']:.1f} m/s ({t['max_train_speed']*3.6:.1f} km/h)")
    
    def _plot_results(self, clearances, travels, thresholds):
        """Generate visualization plots"""
        Logger.section("Generating plots")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        ax = axes[0, 0]
        ax.hist(clearances['clearance_time'], bins=30, edgecolor='black', alpha=0.7, color='blue')
        ax.axvline(thresholds['statistics']['clearance_p95'], 
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
        ax.axvline(thresholds['statistics']['travel_p95'], 
                   color='red', linestyle='--', linewidth=2, label='95th percentile')
        ax.set_xlabel('Travel Time (seconds)')
        ax.set_ylabel('Frequency')
        ax.set_title('Intersection to Crossing Travel')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        ax = axes[0, 2]
        if clearances['speed'].std() > 0.01:
            ax.scatter(clearances['speed'], clearances['clearance_time'], alpha=0.5, s=20, color='blue')
            ax.set_xlabel('Vehicle Speed (m/s)')
            ax.set_ylabel('Clearance Time (seconds)')
            ax.set_title('Clearance vs Speed')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No speed variation', ha='center', va='center', 
                   transform=ax.transAxes)
            ax.set_title('Clearance vs Speed')
        
        ax = axes[1, 0]
        sensors = thresholds['sensor_positions']
        colors = ['red', 'orange', 'green']
        bars = ax.barh(['Sensor 0', 'Sensor 1', 'Sensor 2'], sensors, 
                      color=colors, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Distance Before Crossing (m)')
        ax.set_title('Sensor Positions')
        ax.grid(True, alpha=0.3, axis='x')
        for i, (bar, sensor) in enumerate(zip(bars, sensors)):
            ax.text(sensor, i, f' {sensor:.0f}m', va='center', fontweight='bold')
        
        ax = axes[1, 1]
        sorted_clear = np.sort(clearances['clearance_time'])
        cumulative = np.arange(1, len(sorted_clear) + 1) / len(sorted_clear) * 100
        ax.plot(sorted_clear, cumulative, linewidth=2, color='blue')
        ax.axhline(95, color='red', linestyle='--', linewidth=2, label='95th percentile')
        ax.axvline(thresholds['statistics']['clearance_p95'], 
                   color='red', linestyle='--', linewidth=2)
        ax.set_xlabel('Clearance Time (seconds)')
        ax.set_ylabel('Cumulative %')
        ax.set_title('Clearance CDF')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        ax = axes[1, 2]
        ax.axis('off')
        
        stats = thresholds['statistics']
        summary_text = f"""Threshold Summary

Gate Control:
  Close: {thresholds['closure_before_eta']:.2f}s before train
  Open: {thresholds['opening_after_etd']:.2f}s after train

Traffic Notification:
  Warn: {thresholds['notification_time']:.2f}s before train

Sensors:
  S0: {sensors[0]:.0f}m
  S1: {sensors[1]:.0f}m
  S2: {sensors[2]:.0f}m

Data Quality:
  Clearances: {stats['n_clearances']}
  Travels: {stats['n_travels']}
"""
        ax.text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
                verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.set_title('Summary', pad=20)
        
        plt.tight_layout()
        plot_path = self.plots_dir / 'thresholds_analysis.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved: {plot_path}")
        plt.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze threshold data')
    parser.add_argument('--config', default='thresholds/config.yaml', help='Config file')
    args = parser.parse_args()
    
    analyzer = ThresholdAnalyzer(args.config)
    analyzer.analyze()