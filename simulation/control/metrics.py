"""
Metrics Tracker
Comprehensive tracking of all performance metrics
"""
import pandas as pd
from pathlib import Path
from datetime import datetime


class MetricsTracker:
    def __init__(self, output_dir="outputs/metrics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Emission and fuel constants
        self.fuel_rate_driving = 0.08  # L/s
        self.fuel_rate_idling = 0.01   # L/s
        self.fuel_rate_off = 0.0       # L/s
        self.co2_per_liter = 2.31      # kg CO2 per liter fuel
        
        # Data storage
        self.vehicle_data = {}
        self.wait_times = []
        self.travel_times = []
        self.comfort_scores = []
        self.fuel_data = []
        self.emission_data = []
    
    def track_vehicle(self, vid, t, speed, waiting, engine_off):
        """Track individual vehicle metrics"""
        if vid not in self.vehicle_data:
            self.vehicle_data[vid] = {
                'first_seen': t,
                'total_wait': 0,
                'wait_start': None,
                'total_fuel': 0,
                'total_emissions': 0,
                'stops': 0,
                'engine_off_time': 0,
                'engine_off_start': None
            }
        
        veh = self.vehicle_data[vid]
        
        # Track waiting
        if waiting and veh['wait_start'] is None:
            veh['wait_start'] = t
            veh['stops'] += 1
        elif not waiting and veh['wait_start'] is not None:
            wait_duration = t - veh['wait_start']
            veh['total_wait'] += wait_duration
            veh['wait_start'] = None
            self.wait_times.append({
                'vehicle_id': vid,
                'wait_duration': wait_duration,
                'time': t
            })
        
        # Track engine off time
        if engine_off and veh['engine_off_start'] is None:
            veh['engine_off_start'] = t
        elif not engine_off and veh['engine_off_start'] is not None:
            engine_off_duration = t - veh['engine_off_start']
            veh['engine_off_time'] += engine_off_duration
            veh['engine_off_start'] = None
        
        # Track fuel and emissions
        dt = 0.1  # simulation step
        
        if engine_off:
            fuel_used = self.fuel_rate_off * dt
        elif speed < 0.5:
            fuel_used = self.fuel_rate_idling * dt
        else:
            fuel_used = self.fuel_rate_driving * dt
        
        emissions = fuel_used * self.co2_per_liter
        
        veh['total_fuel'] += fuel_used
        veh['total_emissions'] += emissions
    
    def calculate_comfort(self, queue_length, avg_wait):
        """Calculate comfort score based on queue and wait time"""
        # Comfort decreases with queue length and wait time
        queue_penalty = min(queue_length / 20.0, 1.0)
        wait_penalty = min(avg_wait / 60.0, 1.0)
        
        comfort = 1.0 - (0.6 * queue_penalty + 0.4 * wait_penalty)
        
        self.comfort_scores.append(comfort)
        
        return comfort
    
    def finalize(self):
        """Calculate final metrics and save reports"""
        print(f"[{self._timestamp()}] Calculating final metrics")
        
        # Travel time savings (from rerouting)
        total_travel_time_saved = 0
        
        # Wait time metrics
        if self.wait_times:
            df_wait = pd.DataFrame(self.wait_times)
            total_wait = df_wait['wait_duration'].sum()
            avg_wait = df_wait['wait_duration'].mean()
            max_wait = df_wait['wait_duration'].max()
        else:
            total_wait = avg_wait = max_wait = 0
        
        # Fuel and emissions
        total_fuel = sum(v['total_fuel'] for v in self.vehicle_data.values())
        total_emissions = sum(v['total_emissions'] for v in self.vehicle_data.values())
        total_engine_off_time = sum(v['engine_off_time'] for v in self.vehicle_data.values())
        
        # Fuel saved by engine-off
        fuel_saved = total_engine_off_time * (self.fuel_rate_idling - self.fuel_rate_off)
        emissions_saved = fuel_saved * self.co2_per_liter
        
        # Comfort
        avg_comfort = sum(self.comfort_scores) / len(self.comfort_scores) if self.comfort_scores else 0
        
        # Compile metrics
        metrics = {
            'travel_time_saved': total_travel_time_saved,
            'total_wait_time': total_wait,
            'avg_wait_time': avg_wait,
            'max_wait_time': max_wait,
            'comfort_score': avg_comfort,
            'total_fuel': total_fuel,
            'fuel_saved': fuel_saved,
            'total_emissions': total_emissions,
            'emissions_saved': emissions_saved,
            'vehicles_tracked': len(self.vehicle_data),
            'total_stops': sum(v['stops'] for v in self.vehicle_data.values())
        }
        
        # Save detailed reports
        self._save_reports(metrics)
        
        # Print summary
        self._print_summary(metrics)
        
        return metrics
    
    def _save_reports(self, metrics):
        """Save detailed metric reports"""
        # Save wait times
        if self.wait_times:
            df = pd.DataFrame(self.wait_times)
            df.to_csv(self.output_dir / 'wait_times.csv', index=False)
        
        # Save vehicle data
        vehicle_records = []
        for vid, data in self.vehicle_data.items():
            vehicle_records.append({
                'vehicle_id': vid,
                'total_wait': data['total_wait'],
                'total_fuel': data['total_fuel'],
                'total_emissions': data['total_emissions'],
                'engine_off_time': data['engine_off_time'],
                'stops': data['stops']
            })
        
        if vehicle_records:
            df = pd.DataFrame(vehicle_records)
            df.to_csv(self.output_dir / 'vehicle_metrics.csv', index=False)
        
        # Save summary
        df = pd.DataFrame([metrics])
        df.to_csv(self.output_dir / 'summary.csv', index=False)
    
    def _print_summary(self, metrics):
        """Print metrics summary"""
        print(f"\n[{self._timestamp()}] Metrics Summary")
        print(f"\nTravel Time:")
        print(f"  Total time saved: {metrics['travel_time_saved']:.1f}s")
        
        print(f"\nWait Time:")
        print(f"  Total: {metrics['total_wait_time']:.1f}s")
        print(f"  Average: {metrics['avg_wait_time']:.1f}s")
        print(f"  Maximum: {metrics['max_wait_time']:.1f}s")
        
        print(f"\nComfort:")
        print(f"  Score: {metrics['comfort_score']:.2f}")
        
        print(f"\nFuel Consumption:")
        print(f"  Total: {metrics['total_fuel']:.2f}L")
        print(f"  Saved: {metrics['fuel_saved']:.2f}L")
        print(f"  Reduction: {metrics['fuel_saved']/metrics['total_fuel']*100:.1f}%")
        
        print(f"\nEmissions:")
        print(f"  Total: {metrics['total_emissions']:.2f}kg CO2")
        print(f"  Saved: {metrics['emissions_saved']:.2f}kg CO2")
        print(f"  Reduction: {metrics['emissions_saved']/metrics['total_emissions']*100:.1f}%")
        
        print(f"\nVehicles:")
        print(f"  Tracked: {metrics['vehicles_tracked']}")
        print(f"  Total stops: {metrics['total_stops']}")
    
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")