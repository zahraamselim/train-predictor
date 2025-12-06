import traci
import yaml
from pathlib import Path
from simulation.data import DataCollector
from simulation.metrics import MetricsCalculator


class TrafficController:
    def __init__(self, config_path='simulation/config.yaml'):
        self.config_path = config_path
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.collector = DataCollector(config_path)
        self.calculator = MetricsCalculator(config_path)
    
    def run_phase1(self, gui=False):
        print("\nPhase 1: West route with trains (1800s)")
        
        self.collector.generate_routes('west')
        
        cmd = ['sumo-gui' if gui else 'sumo', '-c', 'simulation.sumocfg', 
               '--start', '--quit-on-end', '--delay', '0', '--no-warnings']
        traci.start(cmd)
        
        self.collector.west.setup_visuals()
        self.collector.east.setup_visuals()
        
        train_interval = 240
        train_duration = 90
        next_train_time = 90
        
        try:
            step = 0
            dt = self.config['simulation']['step_size']
            max_steps = int(1800 / dt)
            
            while step < max_steps:
                try:
                    traci.simulationStep()
                except traci.exceptions.FatalTraCIError:
                    break
                
                t = traci.simulation.getTime()
                
                if traci.simulation.getMinExpectedNumber() == 0:
                    break
                
                if t >= next_train_time and not self.collector.west.gate_closed:
                    self.collector.west.close_gate(t)
                
                if self.collector.west.gate_closed:
                    if t >= self.collector.west.gate_close_time + train_duration:
                        self.collector.west.release_vehicles()
                        self.collector.west.open_gate(t)
                        next_train_time = t + train_interval
                    else:
                        self.collector.west.control_vehicles()
                
                self.collector.west.update_visuals()
                self.collector.east.update_visuals()
                
                self.collector.track_vehicles(t, self.calculator.tracker)
                
                if step % 100 == 0:
                    self.calculator.tracker.sample_queue_length(t)
                
                step += 1
                
                if step % 6000 == 0:
                    west_count = len([v for v in self.calculator.tracker.vehicles.values() 
                                     if v['route_choice'] == 'west'])
                    queue_size = len(self.collector.west.waiting_vehicles)
                    print(f"T={t:.0f}s | Active: {len(traci.vehicle.getIDList())} | "
                          f"West: {west_count} | Queue: {queue_size}")
        
        except KeyboardInterrupt:
            print("Stopped by user")
        
        finally:
            try:
                traci.close()
            except:
                pass
            
            stats = self.calculator.tracker.save_results('phase1')
            if stats:
                self.calculator.print_summary(stats)
            
            return stats
    
    def run_phase2(self, gui=False):
        print("\nPhase 2: East route without trains (1800s)")
        
        self.collector.generate_routes('east')
        
        cmd = ['sumo-gui' if gui else 'sumo', '-c', 'simulation.sumocfg', 
               '--start', '--quit-on-end', '--delay', '0', '--no-warnings']
        traci.start(cmd)
        
        self.collector.west.setup_visuals()
        self.collector.east.setup_visuals()
        
        try:
            step = 0
            dt = self.config['simulation']['step_size']
            max_steps = int(1800 / dt)
            
            while step < max_steps:
                try:
                    traci.simulationStep()
                except traci.exceptions.FatalTraCIError:
                    break
                
                t = traci.simulation.getTime()
                
                if traci.simulation.getMinExpectedNumber() == 0:
                    break
                
                self.collector.west.update_visuals()
                self.collector.east.update_visuals()
                
                self.collector.track_vehicles(t, self.calculator.tracker)
                
                if step % 100 == 0:
                    self.calculator.tracker.sample_queue_length(t)
                
                step += 1
                
                if step % 6000 == 0:
                    east_count = len([v for v in self.calculator.tracker.vehicles.values() 
                                     if v['route_choice'] == 'east'])
                    print(f"T={t:.0f}s | Active: {len(traci.vehicle.getIDList())} | East: {east_count}")
        
        except KeyboardInterrupt:
            print("Stopped by user")
        
        finally:
            try:
                traci.close()
            except:
                pass
            
            stats = self.calculator.tracker.save_results('phase2')
            if stats:
                self.calculator.print_summary(stats)
            
            return stats
    
    def run_comparison(self):
        print("\nRunning two-phase simulation")
        
        phase1_stats = self.run_phase1()
        
        # Create a new calculator for phase 2 with fresh tracker
        self.calculator = MetricsCalculator(self.config_path)
        phase2_stats = self.run_phase2()
        
        self.calculator.create_optimized_scenario(phase1_stats, phase2_stats)
        self.calculator.compare_scenarios(phase1_stats, phase2_stats)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--phase', choices=['1', '2', 'both'], default='both')
    args = parser.parse_args()
    
    controller = TrafficController()
    
    if args.phase == '1':
        controller.run_phase1(gui=args.gui)
    elif args.phase == '2':
        controller.run_phase2(gui=args.gui)
    else:
        controller.run_comparison()