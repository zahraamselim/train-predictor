"""
Run complete simulation with control system
Run: python -m simulation.runner
"""
import traci
import yaml
from pathlib import Path
from utils.logger import Logger
from simulation.crossing_controller import CrossingController
from simulation.vehicle_rerouter import VehicleRerouter
from simulation.metrics_tracker import MetricsTracker

class SimulationRunner:
    def __init__(self, config_path='config/simulation.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.controller = CrossingController()
        self.rerouter = VehicleRerouter()
        self.metrics = MetricsTracker()
    
    def run(self, duration=None, gui=False):
        """Run simulation"""
        if duration is None:
            duration = self.config['simulation']['duration']
        
        Logger.section(f"Running simulation for {duration}s")
        
        sumo_cmd = ['sumo-gui' if gui else 'sumo']
        sumo_cmd.extend([
            '-c', 'sumo/complete/simulation.sumocfg',
            '--start',
            '--quit-on-end'
        ])
        
        traci.start(sumo_cmd)
        
        try:
            step = 0
            max_steps = int(duration / self.config['simulation']['step_length'])
            
            while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
                traci.simulationStep()
                t = traci.simulation.getTime()
                
                self.controller.step(t)
                self.rerouter.step(t, self.controller)
                
                self._track_metrics(t)
                
                # FIXED: Track queue and comfort every 10 seconds
                if step % 100 == 0:  # Every 10 seconds (100 * 0.1s)
                    self._track_queue_comfort(t)
                
                step += 1
                if step % 600 == 0:
                    state = self.controller.get_state()
                    Logger.log(f"Step {t:.0f}s - Gates: {state['gates_closed']}, Trains: {state['active_trains']}, Engines off: {state['engines_off']}")
        
        except KeyboardInterrupt:
            Logger.log("Interrupted by user")
        
        finally:
            traci.close()
            self._finalize()
    
    def _track_metrics(self, t):
        """Track metrics for all vehicles"""
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            try:
                speed = traci.vehicle.getSpeed(vid)
                waiting = speed < 0.5
                engine_off = vid in self.controller.vehicles_engines_off
                
                self.metrics.track_vehicle(vid, t, speed, waiting, engine_off)
            except:
                continue
    
    def _track_queue_comfort(self, t):
        """FIXED: Track queue sizes and comfort scores"""
        # Count vehicles waiting at crossings
        queue_w = 0
        queue_e = 0
        
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            try:
                pos = traci.vehicle.getPosition(vid)[0]
                speed = traci.vehicle.getSpeed(vid)
                
                # Check if waiting near west crossing
                if abs(pos - self.controller.crossing_w) < 100 and speed < 0.5:
                    queue_w += 1
                
                # Check if waiting near east crossing
                elif abs(pos - self.controller.crossing_e) < 100 and speed < 0.5:
                    queue_e += 1
            except:
                continue
        
        total_queue = queue_w + queue_e
        
        # Calculate average wait time from recent waits
        if self.metrics.wait_times:
            recent_waits = [w['wait_duration'] for w in self.metrics.wait_times[-50:]]
            avg_wait = sum(recent_waits) / len(recent_waits) if recent_waits else 0
        else:
            avg_wait = 0
        
        # Track queue and comfort
        self.metrics.track_queue(total_queue, avg_wait)
    
    def _finalize(self):
        """Finalize and save results"""
        metrics = self.metrics.finalize()
        
        reroute_stats = self.rerouter.get_stats()
        if reroute_stats:
            Logger.section("Rerouting Statistics")
            Logger.log(f"Total decisions: {reroute_stats['total_decisions']}")
            Logger.log(f"Rerouted: {reroute_stats['rerouted']}")
            Logger.log(f"Time saved: {reroute_stats['total_time_saved']:.0f}s")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run level crossing simulation')
    parser.add_argument('--duration', type=int, help='Simulation duration in seconds')
    parser.add_argument('--gui', action='store_true', help='Use SUMO GUI')
    parser.add_argument('--config', default='config/simulation.yaml', help='Config file path')
    args = parser.parse_args()
    
    runner = SimulationRunner(args.config)
    runner.run(args.duration, args.gui)