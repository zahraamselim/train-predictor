import pandas as pd
import json
import numpy as np
from pathlib import Path
from utils.logger import Logger


class MetricsTracker:
    def __init__(self, config):
        self.config = config
        
        self.output_dir = Path('outputs/metrics')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_dir = Path('outputs/results')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        fuel = config['fuel']
        self.fuel_driving = fuel['driving']
        self.fuel_idling = fuel['idling']
        self.fuel_off = fuel['engine_off']
        self.co2_factor = fuel['co2_per_liter']
        self.engine_off_factor = fuel.get('engine_off_factor', 0.7)
        self.min_wait_to_shutoff = fuel['min_wait_to_shutoff']
        
        # Track vehicle fuel consumption
        self.vehicles = {}
        
        # Event tracking
        self.wait_events = []
        self.reroute_events = []
        
        # Totals
        self.total_wait_time = 0
        self.total_engine_off_time = 0
        self.total_fuel_saved = 0
        self.total_co2_saved = 0
        self.total_time_saved_from_rerouting = 0
    
    def track_fuel(self, vid, t, dt, waiting):
        """Track fuel consumption for each vehicle"""
        if vid not in self.vehicles:
            self.vehicles[vid] = {
                'first_seen': t,
                'total_fuel': 0,
                'total_co2': 0,
            }
        
        v = self.vehicles[vid]
        
        # Calculate fuel consumption for this timestep
        if waiting:
            fuel = self.fuel_idling * dt
        else:
            fuel = self.fuel_driving * dt
        
        v['total_fuel'] += fuel
        v['total_co2'] += fuel * self.co2_factor
    
    def record_wait_event(self, vid, crossing, wait_duration, engine_off_duration, t):
        """Record a wait event with engine-off time"""
        # Calculate fuel and CO2 saved from engine shutoff
        # Apply the engine_off_factor (e.g., 0.7 = 70% of drivers actually turn off engine)
        actual_engine_off_time = engine_off_duration * self.engine_off_factor
        
        # Fuel saved = time with engine off × (idling rate - off rate)
        fuel_saved = actual_engine_off_time * (self.fuel_idling - self.fuel_off)
        co2_saved = fuel_saved * self.co2_factor
        
        # Store the event
        self.wait_events.append({
            'vehicle': vid,
            'crossing': crossing,
            'wait_duration': wait_duration,
            'engine_off_duration': actual_engine_off_time,
            'fuel_saved': fuel_saved,
            'co2_saved': co2_saved,
            'time': t
        })
        
        # Update totals
        self.total_wait_time += wait_duration
        self.total_engine_off_time += actual_engine_off_time
        self.total_fuel_saved += fuel_saved
        self.total_co2_saved += co2_saved
        
        if actual_engine_off_time > 0:
            Logger.log(f"Vehicle {vid} waited {wait_duration:.1f}s at {crossing}, "
                      f"engine off for {actual_engine_off_time:.1f}s, "
                      f"saved {fuel_saved:.3f}L fuel")
    
    def record_reroute(self, vid, from_crossing, time_saved, t):
        """Record a rerouting decision"""
        to_crossing = 'east' if from_crossing == 'west' else 'west'
        
        # Calculate fuel saved from time saved
        # Time saved × driving fuel rate
        fuel_saved_from_time = time_saved * self.fuel_driving
        co2_saved_from_time = fuel_saved_from_time * self.co2_factor
        
        self.reroute_events.append({
            'vehicle': vid,
            'from': from_crossing,
            'to': to_crossing,
            'time_saved': time_saved,
            'fuel_saved': fuel_saved_from_time,
            'co2_saved': co2_saved_from_time,
            'time': t
        })
        
        # Update totals
        self.total_time_saved_from_rerouting += time_saved
        self.total_fuel_saved += fuel_saved_from_time
        self.total_co2_saved += co2_saved_from_time
    
    def finalize_and_save(self):
        """Finalize calculations and save all results"""
        Logger.section("Saving metrics")
        
        # Save wait events
        if self.wait_events:
            df = pd.DataFrame(self.wait_events)
            df.to_csv(self.output_dir / 'wait_times.csv', index=False)
            Logger.log(f"Wait events: {len(df)}")
        
        # Save reroute events
        if self.reroute_events:
            df = pd.DataFrame(self.reroute_events)
            df.to_csv(self.output_dir / 'reroutes.csv', index=False)
            Logger.log(f"Reroute events: {len(df)}")
        
        # Calculate summary
        summary = self._calculate_summary()
        
        # Save summary as JSON
        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Write human-readable report
        self._write_report(summary)
    
    def _calculate_summary(self):
        """Calculate comprehensive summary statistics"""
        summary = {
            'vehicles_tracked': len(self.vehicles),
            'wait_events': len(self.wait_events),
            'reroute_events': len(self.reroute_events)
        }
        
        # Wait time statistics
        if self.wait_events:
            wait_durations = [w['wait_duration'] for w in self.wait_events]
            summary['wait_times'] = {
                'total_events': len(self.wait_events),
                'total_time_seconds': float(self.total_wait_time),
                'mean_seconds': float(np.mean(wait_durations)),
                'median_seconds': float(np.median(wait_durations)),
                'max_seconds': float(np.max(wait_durations)),
                'p95_seconds': float(np.percentile(wait_durations, 95))
            }
        
        # Engine management statistics
        engine_off_events = [w for w in self.wait_events if w['engine_off_duration'] > 0]
        if engine_off_events:
            summary['engine_management'] = {
                'events_with_engine_off': len(engine_off_events),
                'percentage_of_waits': float(len(engine_off_events) / len(self.wait_events) * 100),
                'total_engine_off_time_seconds': float(self.total_engine_off_time),
                'average_engine_off_time_seconds': float(np.mean([e['engine_off_duration'] for e in engine_off_events])),
                'total_fuel_saved_liters': float(sum(e['fuel_saved'] for e in engine_off_events)),
                'total_co2_saved_kg': float(sum(e['co2_saved'] for e in engine_off_events))
            }
        
        # Rerouting statistics
        if self.reroute_events:
            time_saved_list = [r['time_saved'] for r in self.reroute_events]
            fuel_saved_list = [r['fuel_saved'] for r in self.reroute_events]
            co2_saved_list = [r['co2_saved'] for r in self.reroute_events]
            
            summary['rerouting'] = {
                'total_reroutes': len(self.reroute_events),
                'total_time_saved_seconds': float(sum(time_saved_list)),
                'average_time_saved_seconds': float(np.mean(time_saved_list)),
                'total_fuel_saved_liters': float(sum(fuel_saved_list)),
                'total_co2_saved_kg': float(sum(co2_saved_list))
            }
        
        # Overall fuel and emissions savings
        summary['total_savings'] = {
            'total_fuel_saved_liters': float(self.total_fuel_saved),
            'total_co2_saved_kg': float(self.total_co2_saved),
            'fuel_saved_from_engine_off_liters': float(sum(e['fuel_saved'] for e in engine_off_events)) if engine_off_events else 0,
            'fuel_saved_from_rerouting_liters': float(sum(r['fuel_saved'] for r in self.reroute_events)) if self.reroute_events else 0
        }
        
        return summary
    
    def _write_report(self, summary):
        """Generate human-readable report"""
        lines = []
        lines.append("=" * 60)
        lines.append("RAILROAD CROSSING SIMULATION RESULTS")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Vehicles tracked: {summary['vehicles_tracked']}")
        lines.append("")
        
        # Wait times
        if 'wait_times' in summary:
            lines.append("-" * 60)
            lines.append("WAIT TIMES AT CROSSINGS")
            lines.append("-" * 60)
            w = summary['wait_times']
            lines.append(f"  Total wait events: {w['total_events']}")
            lines.append(f"  Total wait time: {w['total_time_seconds']:.1f} seconds ({w['total_time_seconds']/60:.1f} minutes)")
            lines.append(f"  Average wait: {w['mean_seconds']:.1f} seconds")
            lines.append(f"  Median wait: {w['median_seconds']:.1f} seconds")
            lines.append(f"  Maximum wait: {w['max_seconds']:.1f} seconds")
            lines.append(f"  95th percentile: {w['p95_seconds']:.1f} seconds")
            lines.append("")
        
        # Engine management
        if 'engine_management' in summary:
            lines.append("-" * 60)
            lines.append("ENGINE MANAGEMENT & FUEL SAVINGS")
            lines.append("-" * 60)
            e = summary['engine_management']
            lines.append(f"  Events with engine shutoff: {e['events_with_engine_off']}")
            lines.append(f"  Percentage of waits: {e['percentage_of_waits']:.1f}%")
            lines.append(f"  Total engine-off time: {e['total_engine_off_time_seconds']:.1f} seconds ({e['total_engine_off_time_seconds']/60:.1f} minutes)")
            lines.append(f"  Average engine-off time: {e['average_engine_off_time_seconds']:.1f} seconds")
            lines.append(f"  Fuel saved from engine shutoff: {e['total_fuel_saved_liters']:.2f} liters")
            lines.append(f"  CO₂ reduced from engine shutoff: {e['total_co2_saved_kg']:.2f} kg")
            lines.append("")
        
        # Rerouting
        if 'rerouting' in summary:
            lines.append("-" * 60)
            lines.append("SMART REROUTING")
            lines.append("-" * 60)
            r = summary['rerouting']
            lines.append(f"  Total reroute events: {r['total_reroutes']}")
            lines.append(f"  Total time saved: {r['total_time_saved_seconds']:.1f} seconds ({r['total_time_saved_seconds']/60:.1f} minutes)")
            lines.append(f"  Average time saved per reroute: {r['average_time_saved_seconds']:.1f} seconds")
            lines.append(f"  Fuel saved from rerouting: {r['total_fuel_saved_liters']:.2f} liters")
            lines.append(f"  CO₂ reduced from rerouting: {r['total_co2_saved_kg']:.2f} kg")
            lines.append("")
        
        # Total savings
        if 'total_savings' in summary:
            lines.append("=" * 60)
            lines.append("TOTAL ENVIRONMENTAL IMPACT")
            lines.append("=" * 60)
            t = summary['total_savings']
            lines.append(f"  Total fuel saved: {t['total_fuel_saved_liters']:.2f} liters")
            lines.append(f"    - From engine shutoff: {t['fuel_saved_from_engine_off_liters']:.2f} liters")
            lines.append(f"    - From smart rerouting: {t['fuel_saved_from_rerouting_liters']:.2f} liters")
            lines.append(f"  Total CO₂ emissions reduced: {t['total_co2_saved_kg']:.2f} kg")
            lines.append("")
            
            # Add some context
            lines.append("  Environmental Context:")
            lines.append(f"    - Equivalent to {t['total_fuel_saved_liters']/50:.1f} typical car refuelings saved")
            lines.append(f"    - Equivalent to {t['total_co2_saved_kg']/0.404:.0f} km of car driving emissions avoided")
            lines.append("")
        
        lines.append("=" * 60)
        
        report = "\n".join(lines)
        
        # Save to file
        report_path = self.results_dir / 'simulation_report.txt'
        report_path.write_text(report)
        
        # Print to console
        Logger.section("Results")
        print(report)