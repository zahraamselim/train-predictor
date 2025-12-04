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
        
        Logger.log("MetricsTracker initialized")
    
    def track_fuel(self, vid, t, dt, waiting):
        """Track fuel consumption for each vehicle"""
        if vid not in self.vehicles:
            self.vehicles[vid] = {
                'first_seen': t,
                'total_fuel': 0,
                'total_co2': 0,
                'total_distance': 0,
                'total_wait_time': 0
            }
        
        v = self.vehicles[vid]
        
        # Calculate fuel consumption for this timestep
        if waiting:
            fuel = self.fuel_idling * dt
            v['total_wait_time'] += dt
        else:
            fuel = self.fuel_driving * dt
        
        v['total_fuel'] += fuel
        v['total_co2'] += fuel * self.co2_factor
    
    def record_wait_event(self, vid, crossing, wait_duration, engine_off_duration, t):
        """Record a wait event with engine-off time"""
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
    
    def record_reroute(self, vid, from_crossing, time_saved, wait_original, wait_new, t):
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
            'wait_original': wait_original,
            'wait_new': wait_new,
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
            df.to_csv(self.output_dir / 'wait_events.csv', index=False)
            Logger.log(f"Saved {len(df)} wait events")
        else:
            Logger.log("No wait events recorded")
        
        # Save reroute events
        if self.reroute_events:
            df = pd.DataFrame(self.reroute_events)
            df.to_csv(self.output_dir / 'reroute_events.csv', index=False)
            Logger.log(f"Saved {len(df)} reroute events")
        else:
            Logger.log("No reroute events recorded")
        
        # Save vehicle fuel data
        if self.vehicles:
            vehicle_data = []
            for vid, data in self.vehicles.items():
                vehicle_data.append({
                    'vehicle_id': vid,
                    'first_seen': data['first_seen'],
                    'total_fuel_liters': data['total_fuel'],
                    'total_co2_kg': data['total_co2'],
                    'total_wait_time_seconds': data['total_wait_time']
                })
            df = pd.DataFrame(vehicle_data)
            df.to_csv(self.output_dir / 'vehicle_fuel.csv', index=False)
            Logger.log(f"Saved fuel data for {len(df)} vehicles")
        
        # Calculate summary
        summary = self._calculate_summary()
        
        # Save summary as JSON
        with open(self.output_dir / 'summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        Logger.log(f"Saved summary to {self.output_dir / 'summary.json'}")
        
        # Write human-readable report
        self._write_report(summary)
    
    def _calculate_summary(self):
        """Calculate comprehensive summary statistics"""
        summary = {
            'simulation': {
                'vehicles_tracked': len(self.vehicles),
                'wait_events': len(self.wait_events),
                'reroute_events': len(self.reroute_events)
            }
        }
        
        # Wait time statistics
        if self.wait_events:
            wait_durations = [w['wait_duration'] for w in self.wait_events]
            summary['wait_times'] = {
                'total_events': len(self.wait_events),
                'total_time_seconds': float(self.total_wait_time),
                'total_time_minutes': float(self.total_wait_time / 60),
                'mean_seconds': float(np.mean(wait_durations)),
                'median_seconds': float(np.median(wait_durations)),
                'max_seconds': float(np.max(wait_durations)),
                'min_seconds': float(np.min(wait_durations)),
                'std_dev_seconds': float(np.std(wait_durations)),
                'p95_seconds': float(np.percentile(wait_durations, 95))
            }
        
        # Engine management statistics
        engine_off_events = [w for w in self.wait_events if w['engine_off_duration'] > 0]
        if engine_off_events:
            engine_off_times = [e['engine_off_duration'] for e in engine_off_events]
            summary['engine_management'] = {
                'events_with_engine_off': len(engine_off_events),
                'percentage_of_waits': float(len(engine_off_events) / len(self.wait_events) * 100),
                'total_engine_off_time_seconds': float(self.total_engine_off_time),
                'total_engine_off_time_minutes': float(self.total_engine_off_time / 60),
                'average_engine_off_time_seconds': float(np.mean(engine_off_times)),
                'median_engine_off_time_seconds': float(np.median(engine_off_times)),
                'total_fuel_saved_liters': float(sum(e['fuel_saved'] for e in engine_off_events)),
                'total_co2_saved_kg': float(sum(e['co2_saved'] for e in engine_off_events))
            }
        
        # Rerouting statistics
        if self.reroute_events:
            time_saved_list = [r['time_saved'] for r in self.reroute_events]
            fuel_saved_list = [r['fuel_saved'] for r in self.reroute_events]
            co2_saved_list = [r['co2_saved'] for r in self.reroute_events]
            wait_original_list = [r['wait_original'] for r in self.reroute_events]
            wait_new_list = [r['wait_new'] for r in self.reroute_events]
            
            summary['rerouting'] = {
                'total_reroutes': len(self.reroute_events),
                'total_wait_before_seconds': float(sum(wait_original_list)),
                'total_wait_after_seconds': float(sum(wait_new_list)),
                'total_time_saved_seconds': float(sum(time_saved_list)),
                'total_time_saved_minutes': float(sum(time_saved_list) / 60),
                'average_wait_before_seconds': float(np.mean(wait_original_list)),
                'average_wait_after_seconds': float(np.mean(wait_new_list)),
                'average_time_saved_seconds': float(np.mean(time_saved_list)),
                'median_time_saved_seconds': float(np.median(time_saved_list)),
                'max_time_saved_seconds': float(np.max(time_saved_list)),
                'total_fuel_saved_liters': float(sum(fuel_saved_list)),
                'total_co2_saved_kg': float(sum(co2_saved_list))
            }
        
        # Overall fuel and emissions savings
        fuel_from_engine = sum(e['fuel_saved'] for e in engine_off_events) if engine_off_events else 0
        fuel_from_rerouting = sum(r['fuel_saved'] for r in self.reroute_events) if self.reroute_events else 0
        
        # Calculate what would have been consumed without optimizations
        total_fuel_consumed = sum(v['total_fuel'] for v in self.vehicles.values())
        fuel_without_optimization = total_fuel_consumed + self.total_fuel_saved
        
        summary['total_savings'] = {
            'fuel_without_optimization_liters': float(fuel_without_optimization),
            'fuel_with_optimization_liters': float(total_fuel_consumed),
            'total_fuel_saved_liters': float(self.total_fuel_saved),
            'total_co2_saved_kg': float(self.total_co2_saved),
            'fuel_saved_from_engine_off_liters': float(fuel_from_engine),
            'fuel_saved_from_rerouting_liters': float(fuel_from_rerouting),
            'co2_saved_from_engine_off_kg': float(fuel_from_engine * self.co2_factor),
            'co2_saved_from_rerouting_kg': float(fuel_from_rerouting * self.co2_factor),
            'co2_without_optimization_kg': float((fuel_without_optimization) * self.co2_factor),
            'co2_with_optimization_kg': float(total_fuel_consumed * self.co2_factor)
        }
        
        # Per-crossing breakdown
        if self.wait_events:
            west_events = [w for w in self.wait_events if w['crossing'] == 'west']
            east_events = [w for w in self.wait_events if w['crossing'] == 'east']
            
            summary['by_crossing'] = {}
            
            if west_events:
                summary['by_crossing']['west'] = {
                    'total_events': len(west_events),
                    'total_wait_time_seconds': float(sum(w['wait_duration'] for w in west_events)),
                    'average_wait_seconds': float(np.mean([w['wait_duration'] for w in west_events]))
                }
            
            if east_events:
                summary['by_crossing']['east'] = {
                    'total_events': len(east_events),
                    'total_wait_time_seconds': float(sum(w['wait_duration'] for w in east_events)),
                    'average_wait_seconds': float(np.mean([w['wait_duration'] for w in east_events]))
                }
        
        return summary
    
    def _write_report(self, summary):
        """Generate human-readable report"""
        lines = []
        lines.append("=" * 70)
        lines.append("RAILROAD CROSSING SIMULATION - RESULTS REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        # Overview
        lines.append("SIMULATION OVERVIEW")
        lines.append("-" * 70)
        sim = summary['simulation']
        lines.append(f"  Vehicles tracked: {sim['vehicles_tracked']}")
        lines.append(f"  Wait events recorded: {sim['wait_events']}")
        lines.append(f"  Reroute events: {sim['reroute_events']}")
        lines.append("")
        
        # Wait times
        if 'wait_times' in summary:
            lines.append("=" * 70)
            lines.append("WAIT TIMES AT CROSSINGS")
            lines.append("=" * 70)
            w = summary['wait_times']
            lines.append(f"  Total wait events: {w['total_events']}")
            lines.append(f"  Total wait time: {w['total_time_seconds']:.1f} seconds ({w['total_time_minutes']:.1f} minutes)")
            lines.append(f"")
            lines.append(f"  Statistics:")
            lines.append(f"    Average wait: {w['mean_seconds']:.1f} seconds")
            lines.append(f"    Median wait: {w['median_seconds']:.1f} seconds")
            lines.append(f"    Minimum wait: {w['min_seconds']:.1f} seconds")
            lines.append(f"    Maximum wait: {w['max_seconds']:.1f} seconds")
            lines.append(f"    Standard deviation: {w['std_dev_seconds']:.1f} seconds")
            lines.append(f"    95th percentile: {w['p95_seconds']:.1f} seconds")
            lines.append("")
        
        # By crossing breakdown
        if 'by_crossing' in summary:
            lines.append("-" * 70)
            lines.append("BREAKDOWN BY CROSSING")
            lines.append("-" * 70)
            
            if 'west' in summary['by_crossing']:
                w = summary['by_crossing']['west']
                lines.append(f"  West Crossing:")
                lines.append(f"    Events: {w['total_events']}")
                lines.append(f"    Total wait time: {w['total_wait_time_seconds']:.1f} seconds")
                lines.append(f"    Average wait: {w['average_wait_seconds']:.1f} seconds")
                lines.append("")
            
            if 'east' in summary['by_crossing']:
                e = summary['by_crossing']['east']
                lines.append(f"  East Crossing:")
                lines.append(f"    Events: {e['total_events']}")
                lines.append(f"    Total wait time: {e['total_wait_time_seconds']:.1f} seconds")
                lines.append(f"    Average wait: {e['average_wait_seconds']:.1f} seconds")
                lines.append("")
        
        # Engine management
        if 'engine_management' in summary:
            lines.append("=" * 70)
            lines.append("ENGINE MANAGEMENT & FUEL SAVINGS")
            lines.append("=" * 70)
            e = summary['engine_management']
            lines.append(f"  Events with engine shutoff: {e['events_with_engine_off']}")
            lines.append(f"  Percentage of waits: {e['percentage_of_waits']:.1f}%")
            lines.append(f"")
            lines.append(f"  Engine Off Time:")
            lines.append(f"    Total: {e['total_engine_off_time_seconds']:.1f} seconds ({e['total_engine_off_time_minutes']:.1f} minutes)")
            lines.append(f"    Average per event: {e['average_engine_off_time_seconds']:.1f} seconds")
            lines.append(f"    Median per event: {e['median_engine_off_time_seconds']:.1f} seconds")
            lines.append(f"")
            lines.append(f"  Environmental Impact:")
            lines.append(f"    Fuel saved: {e['total_fuel_saved_liters']:.2f} liters")
            lines.append(f"    CO₂ reduced: {e['total_co2_saved_kg']:.2f} kg")
            lines.append("")
        
        # Rerouting
        if 'rerouting' in summary:
            lines.append("=" * 70)
            lines.append("SMART REROUTING")
            lines.append("=" * 70)
            r = summary['rerouting']
            lines.append(f"  Total reroute events: {r['total_reroutes']}")
            lines.append(f"")
            lines.append(f"  Wait Time Comparison:")
            lines.append(f"    Before rerouting: {r['total_wait_before_seconds']:.1f} seconds ({r['average_wait_before_seconds']:.1f}s avg)")
            lines.append(f"    After rerouting: {r['total_wait_after_seconds']:.1f} seconds ({r['average_wait_after_seconds']:.1f}s avg)")
            lines.append(f"    Time saved: {r['total_time_saved_seconds']:.1f} seconds ({r['total_time_saved_minutes']:.1f} minutes)")
            lines.append(f"")
            lines.append(f"  Statistics:")
            lines.append(f"    Average saved per reroute: {r['average_time_saved_seconds']:.1f} seconds")
            lines.append(f"    Median saved per reroute: {r['median_time_saved_seconds']:.1f} seconds")
            lines.append(f"    Maximum saved: {r['max_time_saved_seconds']:.1f} seconds")
            lines.append(f"")
            lines.append(f"  Environmental Impact:")
            lines.append(f"    Fuel saved: {r['total_fuel_saved_liters']:.2f} liters")
            lines.append(f"    CO₂ reduced: {r['total_co2_saved_kg']:.2f} kg")
            lines.append("")
        
        # Total savings
        if 'total_savings' in summary:
            lines.append("=" * 70)
            lines.append("TOTAL ENVIRONMENTAL IMPACT")
            lines.append("=" * 70)
            t = summary['total_savings']
            lines.append(f"  Total fuel saved: {t['total_fuel_saved_liters']:.2f} liters")
            lines.append(f"    - From engine shutoff: {t['fuel_saved_from_engine_off_liters']:.2f} liters ({t['fuel_saved_from_engine_off_liters']/t['total_fuel_saved_liters']*100:.1f}%)")
            lines.append(f"    - From smart rerouting: {t['fuel_saved_from_rerouting_liters']:.2f} liters ({t['fuel_saved_from_rerouting_liters']/t['total_fuel_saved_liters']*100:.1f}%)")
            lines.append(f"")
            lines.append(f"  Total CO₂ emissions reduced: {t['total_co2_saved_kg']:.2f} kg")
            lines.append(f"    - From engine shutoff: {t['co2_saved_from_engine_off_kg']:.2f} kg")
            lines.append(f"    - From smart rerouting: {t['co2_saved_from_rerouting_kg']:.2f} kg")
            lines.append("")
            
            # Add some context
            lines.append("-" * 70)
            lines.append("  Environmental Context:")
            lines.append(f"    • Equivalent to {t['total_fuel_saved_liters']/50:.1f} typical car refuelings saved")
            lines.append(f"    • Equivalent to {t['total_co2_saved_kg']/0.404:.0f} km of car driving emissions avoided")
            lines.append(f"    • Trees needed to offset CO₂: {t['total_co2_saved_kg']/21:.1f} (1 tree absorbs ~21kg CO₂/year)")
            lines.append("")
        
        lines.append("=" * 70)
        lines.append("END OF REPORT")
        lines.append("=" * 70)
        
        report = "\n".join(lines)
        
        # Save to file
        report_path = self.results_dir / 'simulation_report.txt'
        report_path.write_text(report)
        Logger.log(f"Report saved to {report_path}")
        
        # Print to console
        Logger.section("Simulation Results")
        print(report)