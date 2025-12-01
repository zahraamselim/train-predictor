"""
Main Simulation Runner
Orchestrates the complete level crossing simulation
"""
import sys
import os
import traci
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.control.crossing_controller import CrossingController
from simulation.control.rerouter import VehicleRerouter
from simulation.control.metrics import MetricsTracker


class SimulationRunner:
    def __init__(self, use_gui=False, duration=3600):
        self.use_gui = use_gui
        self.duration = duration
        
        self.controller = CrossingController()
        self.rerouter = VehicleRerouter()
        self.metrics = MetricsTracker()
        
        self.step_count = 0
    
    def run(self):
        """Run complete simulation"""
        print(f"[{self._timestamp()}] Starting simulation")
        print(f"Duration: {self.duration}s")
        print(f"GUI: {self.use_gui}")
        
        self._start_sumo()
        
        try:
            while traci.simulation.getMinExpectedNumber() > 0 and self.step_count < self.duration * 10:
                t = traci.simulation.getTime()
                
                traci.simulationStep()
                
                # Execute control logic
                self.controller.step(t)
                self.rerouter.step(t, self.controller)
                
                # Track metrics
                self._track_metrics(t)
                
                # Log progress
                if self.step_count % 1000 == 0:
                    self._log_progress(t)
                
                self.step_count += 1
            
            print(f"\n[{self._timestamp()}] Simulation completed")
            
        except KeyboardInterrupt:
            print(f"\n[{self._timestamp()}] Interrupted")
        
        finally:
            traci.close()
            self._finalize()
    
    def _start_sumo(self):
        """Start SUMO simulation"""
        sumo_binary = "sumo-gui" if self.use_gui else "sumo"
        
        traci.start([
            sumo_binary,
            "-c", "sumo/simulation.sumocfg",
            "--start",
            "--quit-on-end"
        ])
    
    def _track_metrics(self, t):
        """Track all metrics for current step"""
        state = self.controller.get_state()
        
        # Track each vehicle
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            speed = traci.vehicle.getSpeed(vid)
            waiting = speed < 0.5
            engine_off = vid in self.controller.vehicles_engines_off
            
            self.metrics.track_vehicle(vid, t, speed, waiting, engine_off)
        
        # Calculate comfort periodically
        if self.step_count % 100 == 0:
            queue_length = sum(1 for vid in traci.vehicle.getIDList() 
                             if traci.vehicle.getSpeed(vid) < 0.5)
            avg_wait = sum(v['total_wait'] for v in self.metrics.vehicle_data.values()) / max(len(self.metrics.vehicle_data), 1)
            
            self.metrics.calculate_comfort(queue_length, avg_wait)
    
    def _log_progress(self, t):
        """Log simulation progress"""
        state = self.controller.get_state()
        
        total_vehicles = len([v for v in traci.vehicle.getIDList() if 'train' not in v.lower()])
        waiting = sum(1 for v in traci.vehicle.getIDList() 
                     if 'train' not in v.lower() and traci.vehicle.getSpeed(v) < 0.5)
        
        print(f"[{self._timestamp()}] t={t:.0f}s | "
              f"Vehicles: {total_vehicles} | "
              f"Waiting: {waiting} | "
              f"Engines off: {state['engines_off']} | "
              f"Gates: {'CLOSED' if state['gates_closed'] else 'OPEN'}")
    
    def _finalize(self):
        """Finalize simulation and generate reports"""
        print(f"\n[{self._timestamp()}] Generating reports")
        
        # Get final metrics
        metrics = self.metrics.finalize()
        
        # Get rerouting stats
        reroute_stats = self.rerouter.get_stats()
        
        if reroute_stats:
            print(f"\nRerouting Statistics:")
            print(f"  Total decisions: {reroute_stats['total_decisions']}")
            print(f"  Vehicles rerouted: {reroute_stats['rerouted']}")
            print(f"  Time saved: {reroute_stats['total_time_saved']:.0f}s")
        
        print(f"\n[{self._timestamp()}] Reports saved to outputs/metrics/")
    
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', action='store_true', help='Use SUMO GUI')
    parser.add_argument('--duration', type=int, default=3600, help='Simulation duration (seconds)')
    
    args = parser.parse_args()
    
    runner = SimulationRunner(use_gui=args.gui, duration=args.duration)
    runner.run()