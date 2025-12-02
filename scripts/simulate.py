import sys
import traci
from simulation.utils.logger import Logger
from simulation.control.controller import CrossingController
from simulation.control.rerouter import VehicleRerouter
from simulation.control.metrics import MetricsTracker

class Simulator:
    """Run level crossing simulation"""
    
    def __init__(self, use_gui=False, duration=3600):
        self.use_gui = use_gui
        self.duration = duration
        
        self.controller = CrossingController()
        self.rerouter = VehicleRerouter()
        self.metrics = MetricsTracker()
        
        self.step_count = 0
    
    def run(self):
        Logger.section(f"Starting simulation ({self.duration}s)")
        
        self._start_sumo()
        
        try:
            while traci.simulation.getMinExpectedNumber() > 0 and self.step_count < self.duration * 10:
                t = traci.simulation.getTime()
                
                traci.simulationStep()
                
                self.controller.step(t)
                self.rerouter.step(t, self.controller)
                
                self._track_metrics(t)
                
                if self.step_count % 1000 == 0:
                    self._log_progress(t)
                
                self.step_count += 1
            
            Logger.section("Simulation completed")
        
        except KeyboardInterrupt:
            Logger.log("Interrupted")
        
        finally:
            traci.close()
            self._finalize()
    
    def _start_sumo(self):
        sumo_binary = "sumo-gui" if self.use_gui else "sumo"
        traci.start([sumo_binary, "-c", "sumo/complete/simulation.sumocfg", "--start", "--quit-on-end"])
    
    def _track_metrics(self, t):
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            speed = traci.vehicle.getSpeed(vid)
            waiting = speed < 0.5
            engine_off = vid in self.controller.vehicles_engines_off
            
            self.metrics.track_vehicle(vid, t, speed, waiting, engine_off)
        
        if self.step_count % 100 == 0:
            queue_length = sum(1 for vid in traci.vehicle.getIDList() 
                             if traci.vehicle.getSpeed(vid) < 0.5)
            avg_wait = sum(v['total_wait'] for v in self.metrics.vehicle_data.values()) / max(len(self.metrics.vehicle_data), 1)
            
            self.metrics.calculate_comfort(queue_length, avg_wait)
    
    def _log_progress(self, t):
        state = self.controller.get_state()
        
        total_vehicles = len([v for v in traci.vehicle.getIDList() if 'train' not in v.lower()])
        waiting = sum(1 for v in traci.vehicle.getIDList() 
                     if 'train' not in v.lower() and traci.vehicle.getSpeed(v) < 0.5)
        
        Logger.log(f"t={t:.0f}s | Vehicles: {total_vehicles} | Waiting: {waiting} | "
                  f"Engines off: {state['engines_off']} | Gates: {'CLOSED' if state['gates_closed'] else 'OPEN'}")
    
    def _finalize(self):
        metrics = self.metrics.finalize()
        
        reroute_stats = self.rerouter.get_stats()
        if reroute_stats:
            Logger.section("Rerouting Statistics")
            print(f"  Total decisions: {reroute_stats['total_decisions']}")
            print(f"  Rerouted: {reroute_stats['rerouted']}")
            print(f"  Time saved: {reroute_stats['total_time_saved']:.0f}s")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--duration', type=int, default=3600)
    
    args = parser.parse_args()
    
    simulator = Simulator(use_gui=args.gui, duration=args.duration)
    simulator.run()