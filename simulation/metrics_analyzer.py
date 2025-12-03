"""
Analyze collected metrics data
Run: python -m metrics.analyzer
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path
from utils.logger import Logger


class MetricsAnalyzer:
    def __init__(self):
        self.metrics_dir = Path('outputs/metrics')
        self.results_dir = Path('outputs/results')
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze(self):
        """Analyze collected metrics"""
        Logger.section("Analyzing metrics data")
        
        summary = self._load_summary()
        wait_events = self._load_wait_events()
        queue_snapshots = self._load_queue_snapshots()
        vehicle_metrics = self._load_vehicle_metrics()
        
        if summary is None:
            Logger.log("ERROR: No summary data found")
            return None
        
        analysis = {
            'summary': summary,
            'wait_analysis': self._analyze_waits(wait_events) if wait_events is not None else {},
            'queue_analysis': self._analyze_queues(queue_snapshots) if queue_snapshots is not None else {},
            'vehicle_analysis': self._analyze_vehicles(vehicle_metrics) if vehicle_metrics is not None else {},
            'efficiency': self._calculate_efficiency(summary, vehicle_metrics)
        }
        
        output_path = self.results_dir / 'metrics_analysis.json'
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        Logger.log(f"Analysis saved to {output_path}")
        self._print_report(analysis)
        
        return analysis
    
    def _load_summary(self):
        """Load summary CSV"""
        path = self.metrics_dir / 'summary.csv'
        if not path.exists():
            return None
        df = pd.read_csv(path)
        return df.iloc[0].to_dict()
    
    def _load_wait_events(self):
        """Load wait events CSV"""
        path = self.metrics_dir / 'wait_events.csv'
        if not path.exists():
            return None
        return pd.read_csv(path)
    
    def _load_queue_snapshots(self):
        """Load queue snapshots CSV"""
        path = self.metrics_dir / 'queue_snapshots.csv'
        if not path.exists():
            return None
        return pd.read_csv(path)
    
    def _load_vehicle_metrics(self):
        """Load vehicle metrics CSV"""
        path = self.metrics_dir / 'vehicle_metrics.csv'
        if not path.exists():
            return None
        return pd.read_csv(path)
    
    def _analyze_waits(self, df):
        """Analyze wait time patterns"""
        if df is None or len(df) == 0:
            return {}
        
        return {
            'total_waits': len(df),
            'mean': float(df['wait_duration'].mean()),
            'median': float(df['wait_duration'].median()),
            'std': float(df['wait_duration'].std()),
            'min': float(df['wait_duration'].min()),
            'max': float(df['wait_duration'].max()),
            'p25': float(df['wait_duration'].quantile(0.25)),
            'p75': float(df['wait_duration'].quantile(0.75)),
            'p95': float(df['wait_duration'].quantile(0.95)),
            'p99': float(df['wait_duration'].quantile(0.99)),
            'engine_off_percentage': float((df['engine_off'].sum() / len(df)) * 100) if 'engine_off' in df.columns else 0.0
        }
    
    def _analyze_queues(self, df):
        """Analyze queue patterns"""
        if df is None or len(df) == 0:
            return {}
        
        return {
            'total_snapshots': len(df),
            'mean_queue': float(df['total_queue'].mean()),
            'max_queue': int(df['total_queue'].max()),
            'mean_comfort': float(df['comfort'].mean()),
            'min_comfort': float(df['comfort'].min()),
            'queue_percentiles': {
                'p25': float(df['total_queue'].quantile(0.25)),
                'p50': float(df['total_queue'].quantile(0.50)),
                'p75': float(df['total_queue'].quantile(0.75)),
                'p95': float(df['total_queue'].quantile(0.95))
            }
        }
    
    def _analyze_vehicles(self, df):
        """Analyze vehicle-level metrics"""
        if df is None or len(df) == 0:
            return {}
        
        return {
            'total_vehicles': len(df),
            'mean_travel_time': float(df['travel_time'].mean()),
            'mean_wait_time': float(df['total_wait'].mean()),
            'mean_stops': float(df['stops'].mean()),
            'total_distance': float(df['distance_traveled'].sum()),
            'mean_speed': float(df['avg_speed'].mean()),
            'fuel_per_vehicle': float(df['total_fuel'].mean()),
            'emissions_per_vehicle': float(df['total_emissions'].mean()),
            'engine_off_per_vehicle': float(df['engine_off_time'].mean())
        }
    
    def _calculate_efficiency(self, summary, vehicle_df):
        """Calculate system efficiency metrics"""
        if summary is None:
            return {}
        
        efficiency = {}
        
        if 'total_fuel' in summary and 'fuel_saved' in summary:
            total_fuel = summary['total_fuel']
            fuel_saved = summary['fuel_saved']
            
            if total_fuel > 0:
                efficiency['fuel_reduction_percent'] = float((fuel_saved / total_fuel) * 100)
            else:
                efficiency['fuel_reduction_percent'] = 0.0
            
            efficiency['total_fuel_liters'] = float(total_fuel)
            efficiency['fuel_saved_liters'] = float(fuel_saved)
        
        if 'total_emissions' in summary and 'emissions_saved' in summary:
            total_emissions = summary['total_emissions']
            emissions_saved = summary['emissions_saved']
            
            if total_emissions > 0:
                efficiency['emissions_reduction_percent'] = float((emissions_saved / total_emissions) * 100)
            else:
                efficiency['emissions_reduction_percent'] = 0.0
            
            efficiency['total_emissions_kg'] = float(total_emissions)
            efficiency['emissions_saved_kg'] = float(emissions_saved)
        
        if vehicle_df is not None and len(vehicle_df) > 0:
            efficiency['avg_wait_per_vehicle'] = float(vehicle_df['total_wait'].mean())
            efficiency['avg_stops_per_vehicle'] = float(vehicle_df['stops'].mean())
        
        if 'avg_comfort_score' in summary:
            efficiency['comfort_score'] = float(summary['avg_comfort_score'])
        
        return efficiency
    
    def _print_report(self, analysis):
        """Print analysis report"""
        Logger.section("Metrics Analysis Report")
        
        if analysis['wait_analysis']:
            wait = analysis['wait_analysis']
            print(f"\nWait Time Analysis:")
            print(f"  Total waits: {wait['total_waits']}")
            print(f"  Mean: {wait['mean']:.2f}s")
            print(f"  Median: {wait['median']:.2f}s")
            print(f"  Std Dev: {wait['std']:.2f}s")
            print(f"  Range: [{wait['min']:.2f}s, {wait['max']:.2f}s]")
            print(f"  95th percentile: {wait['p95']:.2f}s")
            print(f"  99th percentile: {wait['p99']:.2f}s")
            if 'engine_off_percentage' in wait:
                print(f"  Engine-off waits: {wait['engine_off_percentage']:.1f}%")
        
        if analysis['queue_analysis']:
            queue = analysis['queue_analysis']
            print(f"\nQueue Analysis:")
            print(f"  Mean queue length: {queue['mean_queue']:.1f} vehicles")
            print(f"  Max queue length: {queue['max_queue']} vehicles")
            print(f"  Mean comfort score: {queue['mean_comfort']:.2f}")
            print(f"  Min comfort score: {queue['min_comfort']:.2f}")
            
            perc = queue['queue_percentiles']
            print(f"  Queue percentiles:")
            print(f"    25th: {perc['p25']:.1f}")
            print(f"    50th: {perc['p50']:.1f}")
            print(f"    75th: {perc['p75']:.1f}")
            print(f"    95th: {perc['p95']:.1f}")
        
        if analysis['vehicle_analysis']:
            veh = analysis['vehicle_analysis']
            print(f"\nVehicle Analysis:")
            print(f"  Total vehicles: {veh['total_vehicles']}")
            print(f"  Mean travel time: {veh['mean_travel_time']:.1f}s")
            print(f"  Mean wait time: {veh['mean_wait_time']:.1f}s")
            print(f"  Mean stops: {veh['mean_stops']:.1f}")
            print(f"  Mean speed: {veh['mean_speed']:.1f} m/s")
            print(f"  Fuel per vehicle: {veh['fuel_per_vehicle']:.3f}L")
            print(f"  Emissions per vehicle: {veh['emissions_per_vehicle']:.3f}kg CO2")
            print(f"  Engine-off time per vehicle: {veh['engine_off_per_vehicle']:.1f}s")
        
        if analysis['efficiency']:
            eff = analysis['efficiency']
            print(f"\nSystem Efficiency:")
            
            if 'fuel_reduction_percent' in eff:
                print(f"  Fuel saved: {eff['fuel_saved_liters']:.2f}L ({eff['fuel_reduction_percent']:.1f}%)")
            
            if 'emissions_reduction_percent' in eff:
                print(f"  Emissions saved: {eff['emissions_saved_kg']:.2f}kg CO2 ({eff['emissions_reduction_percent']:.1f}%)")
            
            if 'comfort_score' in eff:
                print(f"  Comfort score: {eff['comfort_score']:.2f}/1.00")
            
            if 'avg_wait_per_vehicle' in eff:
                print(f"  Avg wait per vehicle: {eff['avg_wait_per_vehicle']:.1f}s")


if __name__ == '__main__':
    analyzer = MetricsAnalyzer()
    analyzer.analyze()