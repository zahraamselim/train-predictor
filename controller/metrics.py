"""Calculate design requirement metrics for capstone project."""

from typing import Dict, List
import numpy as np


class PerformanceMetrics:
    """
    Calculate design requirements:
    1. Travel time improvement
    2. Fuel consumption reduction
    3. Comfort improvement
    4. Emission reduction
    """
    
    def __init__(self):
        self.fuel_rates = {
            'driving': 0.08,      # L/min while driving
            'idling': 0.01,       # L/min while idling
            'off': 0.0            # L/min when engine off
        }
        
        self.emission_factor = 2.31  # kg CO2 per liter of gasoline
        
        self.comfort_factors = {
            'driving': 1.0,       # Baseline comfort
            'waiting_uncertain': 3.0,  # 3x worse when don't know wait time
            'waiting_known': 1.5,      # 1.5x worse when know wait time
            'rerouting': 1.2      # Slightly worse due to deviation
        }
        
        self.vehicle_journey_data = []
    
    def reset(self):
        """Reset all collected data."""
        self.vehicle_journey_data = []
    
    def log_vehicle_journey(self, journey: Dict):
        """
        Log a vehicle's complete journey for analysis.
        
        Args:
            journey: Dict with keys:
                - vehicle_id: Unique ID
                - system_active: Whether notification system was active
                - action_taken: 'wait', 'reroute', or 'unaffected'
                - total_travel_time: Total journey time (s)
                - driving_time: Time spent driving (s)
                - waiting_time: Time spent waiting (s)
                - knew_wait_time: Whether driver knew wait time in advance
                - reroute_distance: Extra distance if rerouted (m)
                - engine_off_time: Time with engine off while waiting (s)
        """
        self.vehicle_journey_data.append(journey)
    
    def calculate_travel_time_metrics(self) -> Dict:
        """
        Calculate travel time improvements.
        
        Returns:
            Dict with baseline_avg, system_avg, improvement_seconds, improvement_percent
        """
        baseline_times = [j['total_travel_time'] for j in self.vehicle_journey_data 
                         if not j['system_active']]
        system_times = [j['total_travel_time'] for j in self.vehicle_journey_data 
                       if j['system_active']]
        
        if not baseline_times or not system_times:
            return {'error': 'Insufficient data'}
        
        baseline_avg = np.mean(baseline_times)
        system_avg = np.mean(system_times)
        improvement = baseline_avg - system_avg
        improvement_percent = (improvement / baseline_avg) * 100
        
        return {
            'baseline_avg_seconds': round(baseline_avg, 2),
            'system_avg_seconds': round(system_avg, 2),
            'improvement_seconds': round(improvement, 2),
            'improvement_percent': round(improvement_percent, 2),
            'baseline_samples': len(baseline_times),
            'system_samples': len(system_times)
        }
    
    def calculate_fuel_consumption(self) -> Dict:
        """
        Calculate fuel consumption and savings.
        
        Returns:
            Dict with baseline_fuel, system_fuel, savings_liters, savings_percent
        """
        baseline_fuel = 0
        system_fuel = 0
        
        for journey in self.vehicle_journey_data:
            driving_time_min = journey['driving_time'] / 60
            waiting_time_min = journey['waiting_time'] / 60
            engine_off_time_min = journey.get('engine_off_time', 0) / 60
            
            fuel_driving = driving_time_min * self.fuel_rates['driving']
            
            if journey['system_active'] and journey.get('knew_wait_time', False):
                fuel_waiting_on = max(0, waiting_time_min - engine_off_time_min) * self.fuel_rates['idling']
                fuel_waiting_off = engine_off_time_min * self.fuel_rates['off']
                fuel_waiting = fuel_waiting_on + fuel_waiting_off
            else:
                fuel_waiting = waiting_time_min * self.fuel_rates['idling']
            
            total_fuel = fuel_driving + fuel_waiting
            
            if journey['system_active']:
                system_fuel += total_fuel
            else:
                baseline_fuel += total_fuel
        
        baseline_count = sum(1 for j in self.vehicle_journey_data if not j['system_active'])
        system_count = sum(1 for j in self.vehicle_journey_data if j['system_active'])
        
        baseline_avg = baseline_fuel / baseline_count if baseline_count > 0 else 0
        system_avg = system_fuel / system_count if system_count > 0 else 0
        
        savings = baseline_avg - system_avg
        savings_percent = (savings / baseline_avg * 100) if baseline_avg > 0 else 0
        
        return {
            'baseline_fuel_liters': round(baseline_avg, 3),
            'system_fuel_liters': round(system_avg, 3),
            'savings_liters': round(savings, 3),
            'savings_percent': round(savings_percent, 2)
        }
    
    def calculate_emissions(self) -> Dict:
        """
        Calculate CO2 emissions.
        
        Returns:
            Dict with baseline_co2, system_co2, reduction_kg, reduction_percent
        """
        fuel_metrics = self.calculate_fuel_consumption()
        
        baseline_co2 = fuel_metrics['baseline_fuel_liters'] * self.emission_factor
        system_co2 = fuel_metrics['system_fuel_liters'] * self.emission_factor
        reduction = baseline_co2 - system_co2
        reduction_percent = (reduction / baseline_co2 * 100) if baseline_co2 > 0 else 0
        
        return {
            'baseline_co2_kg': round(baseline_co2, 3),
            'system_co2_kg': round(system_co2, 3),
            'reduction_kg': round(reduction, 3),
            'reduction_percent': round(reduction_percent, 2)
        }
    
    def calculate_comfort_score(self) -> Dict:
        """
        Calculate comfort/convenience score.
        Lower is better (less discomfort).
        
        Returns:
            Dict with baseline_score, system_score, improvement_percent
        """
        baseline_scores = []
        system_scores = []
        
        for journey in self.vehicle_journey_data:
            driving_time = journey['driving_time']
            waiting_time = journey['waiting_time']
            
            driving_discomfort = driving_time * self.comfort_factors['driving']
            
            if journey['system_active']:
                if journey.get('knew_wait_time', False):
                    waiting_discomfort = waiting_time * self.comfort_factors['waiting_known']
                else:
                    waiting_discomfort = waiting_time * self.comfort_factors['waiting_uncertain']
                
                if journey['action_taken'] == 'reroute':
                    reroute_time = journey.get('reroute_distance', 0) / 15  # Assume 15 m/s
                    driving_discomfort += reroute_time * self.comfort_factors['rerouting']
            else:
                waiting_discomfort = waiting_time * self.comfort_factors['waiting_uncertain']
            
            total_discomfort = driving_discomfort + waiting_discomfort
            
            if journey['system_active']:
                system_scores.append(total_discomfort)
            else:
                baseline_scores.append(total_discomfort)
        
        if not baseline_scores or not system_scores:
            return {'error': 'Insufficient data'}
        
        baseline_avg = np.mean(baseline_scores)
        system_avg = np.mean(system_scores)
        improvement = baseline_avg - system_avg
        improvement_percent = (improvement / baseline_avg * 100) if baseline_avg > 0 else 0
        
        return {
            'baseline_discomfort': round(baseline_avg, 2),
            'system_discomfort': round(system_avg, 2),
            'improvement': round(improvement, 2),
            'improvement_percent': round(improvement_percent, 2)
        }
    
    def generate_full_report(self) -> Dict:
        """Generate complete metrics report."""
        return {
            'travel_time': self.calculate_travel_time_metrics(),
            'fuel_consumption': self.calculate_fuel_consumption(),
            'emissions': self.calculate_emissions(),
            'comfort': self.calculate_comfort_score(),
            'total_vehicles': len(self.vehicle_journey_data),
            'baseline_vehicles': sum(1 for j in self.vehicle_journey_data if not j['system_active']),
            'system_vehicles': sum(1 for j in self.vehicle_journey_data if j['system_active'])
        }
    
    def print_report(self):
        """Print formatted metrics report."""
        report = self.generate_full_report()
        
        print("\nPERFORMANCE METRICS REPORT")
        print(f"Total vehicles analyzed: {report['total_vehicles']}")
        print(f"  Baseline (no system): {report['baseline_vehicles']}")
        print(f"  With system: {report['system_vehicles']}")
        
        if 'error' not in report['travel_time']:
            tt = report['travel_time']
            print("\n1. TRAVEL TIME")
            print(f"  Baseline average: {tt['baseline_avg_seconds']:.1f}s")
            print(f"  System average: {tt['system_avg_seconds']:.1f}s")
            print(f"  Improvement: {tt['improvement_seconds']:.1f}s ({tt['improvement_percent']:.1f}%)")
        
        fc = report['fuel_consumption']
        print("\n2. FUEL CONSUMPTION")
        print(f"  Baseline: {fc['baseline_fuel_liters']:.3f}L per vehicle")
        print(f"  With system: {fc['system_fuel_liters']:.3f}L per vehicle")
        print(f"  Savings: {fc['savings_liters']:.3f}L ({fc['savings_percent']:.1f}%)")
        
        em = report['emissions']
        print("\n3. CO2 EMISSIONS")
        print(f"  Baseline: {em['baseline_co2_kg']:.3f}kg per vehicle")
        print(f"  With system: {em['system_co2_kg']:.3f}kg per vehicle")
        print(f"  Reduction: {em['reduction_kg']:.3f}kg ({em['reduction_percent']:.1f}%)")
        
        if 'error' not in report['comfort']:
            cf = report['comfort']
            print("\n4. COMFORT/CONVENIENCE")
            print(f"  Baseline discomfort: {cf['baseline_discomfort']:.1f}")
            print(f"  With system: {cf['system_discomfort']:.1f}")
            print(f"  Improvement: {cf['improvement_percent']:.1f}%")