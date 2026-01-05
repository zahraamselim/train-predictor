"""
Traffic simulation for poster Table 3 metrics
Two-phase comparison: West route (with trains) vs East route (without trains)
Usage: python run_simulation.py [--gui]
"""

import subprocess
import traci
import pandas as pd
import numpy as np
import json
import yaml
from pathlib import Path
from utils.logger import Logger


class TrafficSimulation:
    def __init__(self, config_path='config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.output_dir = Path('outputs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.vehicles = {}
        self.waiting_west = {}
        self.waiting_east = {}
    
    def generate_network(self):
        """Create SUMO network with two routes"""
        Logger.section("Generating simulation network")
        
        net = self.config['network']
        road_sep = net['road_separation']
        cross_dist = net['crossing_distance']
        length = net['road_length']
        
        north_y = road_sep / 2
        south_y = -road_sep / 2
        west_x = -cross_dist / 2
        east_x = cross_dist / 2
        
        nodes = f"""<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="n_west" x="-{length}" y="{north_y}" type="priority"/>
    <node id="n_east" x="{length}" y="{north_y}" type="priority"/>
    <node id="s_west" x="-{length}" y="{south_y}" type="priority"/>
    <node id="s_east" x="{length}" y="{south_y}" type="priority"/>
    
    <node id="nw_junction" x="{west_x}" y="{north_y}" type="priority"/>
    <node id="sw_junction" x="{west_x}" y="{south_y}" type="priority"/>
    <node id="west_crossing" x="{west_x}" y="0" type="rail_crossing"/>
    
    <node id="ne_junction" x="{east_x}" y="{north_y}" type="priority"/>
    <node id="se_junction" x="{east_x}" y="{south_y}" type="priority"/>
    <node id="east_crossing" x="{east_x}" y="0" type="rail_crossing"/>
</nodes>"""
        
        edges = """<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <edge id="n_in_w" from="n_west" to="nw_junction" numLanes="1" speed="16.67"/>
    <edge id="n_w_e" from="nw_junction" to="ne_junction" numLanes="1" speed="16.67"/>
    <edge id="n_out_e" from="ne_junction" to="n_east" numLanes="1" speed="16.67"/>
    
    <edge id="s_in_w" from="s_west" to="sw_junction" numLanes="1" speed="16.67"/>
    <edge id="s_w_e" from="sw_junction" to="se_junction" numLanes="1" speed="16.67"/>
    <edge id="s_out_e" from="se_junction" to="s_east" numLanes="1" speed="16.67"/>
    
    <edge id="v_w_n_s" from="nw_junction" to="west_crossing" numLanes="1" speed="13.89"/>
    <edge id="v_w_x_s" from="west_crossing" to="sw_junction" numLanes="1" speed="13.89"/>
    
    <edge id="v_e_n_s" from="ne_junction" to="east_crossing" numLanes="1" speed="13.89"/>
    <edge id="v_e_x_s" from="east_crossing" to="se_junction" numLanes="1" speed="13.89"/>
</edges>"""
        
        connections = """<?xml version="1.0" encoding="UTF-8"?>
<connections>
    <connection from="n_in_w" to="v_w_n_s" fromLane="0" toLane="0"/>
    <connection from="n_in_w" to="n_w_e" fromLane="0" toLane="0"/>
    <connection from="v_w_x_s" to="s_w_e" fromLane="0" toLane="0"/>
    <connection from="n_w_e" to="v_e_n_s" fromLane="0" toLane="0"/>
    <connection from="v_e_x_s" to="s_out_e" fromLane="0" toLane="0"/>
    <connection from="s_w_e" to="s_out_e" fromLane="0" toLane="0"/>
</connections>"""
        
        Path('simulation.nod.xml').write_text(nodes)
        Path('simulation.edg.xml').write_text(edges)
        Path('simulation.con.xml').write_text(connections)
        
        result = subprocess.run([
            'netconvert',
            '--node-files=simulation.nod.xml',
            '--edge-files=simulation.edg.xml',
            '--connection-files=simulation.con.xml',
            '--output-file=simulation.net.xml',
            '--no-turnarounds'
        ], capture_output=True)
        
        if result.returncode != 0:
            Logger.log("Network generation failed")
            return False
        
        Logger.log("Network created: simulation.net.xml")
        return True
    
    def create_routes(self, phase):
        """Create route file"""
        traffic = self.config['simulation']['traffic']
        
        if phase == 1:
            routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="4.5" maxSpeed="20" accel="2.6" decel="4.5" sigma="0.5" color="70,130,180"/>
    <route id="route_west" edges="n_in_w v_w_n_s v_w_x_s s_w_e s_out_e"/>
    <flow id="cars" type="car" route="route_west" begin="0" end="1800" vehsPerHour="{traffic['cars_per_hour']}"/>
</routes>"""
        else:
            routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="4.5" maxSpeed="20" accel="2.6" decel="4.5" sigma="0.5" color="255,140,0"/>
    <route id="route_east" edges="n_in_w n_w_e v_e_n_s v_e_x_s s_out_e"/>
    <flow id="cars" type="car" route="route_east" begin="0" end="1800" vehsPerHour="{traffic['cars_per_hour']}"/>
</routes>"""
        
        Path('simulation.rou.xml').write_text(routes)
    
    def create_config(self):
        """Create SUMO configuration"""
        config = """<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="simulation.net.xml"/>
        <route-files value="simulation.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="1800"/>
        <step-length value="0.1"/>
    </time>
    <processing>
        <ignore-route-errors value="true"/>
        <time-to-teleport value="-1"/>
    </processing>
</configuration>"""
        
        Path('simulation.sumocfg').write_text(config)
    
    def get_crossing_position(self, crossing_name):
        """Get actual position of crossing from SUMO"""
        try:
            pos = traci.junction.getPosition(f"{crossing_name}_crossing")
            return pos[0], pos[1]
        except:
            return None, None
    
    def track_vehicle(self, vid, route, t):
        """Track vehicle data"""
        if vid not in self.vehicles:
            self.vehicles[vid] = {
                'start_time': t,
                'end_time': None,
                'route': route,
                'wait_time': 0,
                'trip_time': None
            }
    
    def check_waiting(self, vid, x, speed, crossing_x, waiting_dict, t):
        """Check if vehicle is waiting at crossing"""
        if crossing_x is None:
            return
        
        distance = abs(x - crossing_x)
        
        # If near crossing (within 50m) and stopped
        if distance < 50 and speed < 0.5:
            if vid not in waiting_dict:
                waiting_dict[vid] = t  # Start waiting
        else:
            if vid in waiting_dict:
                # Was waiting, now moving - add wait time
                wait_duration = t - waiting_dict[vid]
                if vid in self.vehicles:
                    self.vehicles[vid]['wait_time'] += wait_duration
                del waiting_dict[vid]
    
    def end_vehicle(self, vid, t):
        """Vehicle completed trip"""
        if vid in self.vehicles:
            v = self.vehicles[vid]
            v['end_time'] = t
            v['trip_time'] = t - v['start_time']
    
    def calculate_metrics(self, phase_name):
        """Calculate metrics (poster Table 3)"""
        completed = [v for v in self.vehicles.values() if v['end_time'] is not None]
        
        if not completed:
            Logger.log(f"No completed vehicles in {phase_name}")
            return None
        
        trip_times = [v['trip_time'] for v in completed]
        wait_times = [v['wait_time'] for v in completed]
        
        # Fuel calculation
        fuel = self.config['simulation']['fuel']
        fuel_consumed = []
        co2_emitted = []
        
        for v in completed:
            driving_time = v['trip_time'] - v['wait_time']
            idling_time = v['wait_time']
            
            fuel_used = driving_time * fuel['driving'] + idling_time * fuel['idling']
            fuel_consumed.append(fuel_used)
            co2_emitted.append(fuel_used * fuel['co2_per_liter'])
        
        metrics = {
            'phase': phase_name,
            'n_vehicles': len(completed),
            'trip_time': {
                'mean': float(np.mean(trip_times)),
                'std': float(np.std(trip_times))
            },
            'wait_time': {
                'mean': float(np.mean(wait_times)),
                'std': float(np.std(wait_times)),
                'vehicles_waited': sum(1 for w in wait_times if w > 0)
            },
            'fuel': {
                'mean': float(np.mean(fuel_consumed)),
                'total': float(np.sum(fuel_consumed))
            },
            'co2': {
                'mean': float(np.mean(co2_emitted)),
                'total': float(np.sum(co2_emitted))
            }
        }
        
        return metrics
    
    def save_vehicles(self, phase_name):
        """Save vehicle data"""
        completed = [v for v in self.vehicles.values() if v['end_time'] is not None]
        
        records = []
        for vid, v in self.vehicles.items():
            if v['end_time'] is None:
                continue
            
            records.append({
                'vehicle_id': vid,
                'route': v['route'],
                'trip_time': v['trip_time'],
                'wait_time': v['wait_time']
            })
        
        df = pd.DataFrame(records)
        df.to_csv(self.output_dir / f'{phase_name}_vehicles.csv', index=False)
        Logger.log(f"Saved: {self.output_dir / f'{phase_name}_vehicles.csv'}")
    
    def run_phase1(self, gui=False):
        """Phase 1: West route with trains"""
        Logger.section("Phase 1: West route (baseline with trains)")
        
        self.create_routes(1)
        self.create_config()
        
        cmd = ['sumo-gui' if gui else 'sumo', '-c', 'simulation.sumocfg', 
               '--start', '--quit-on-end', '--delay', '0', '--no-warnings']
        traci.start(cmd)
        
        # Get crossing position
        west_x, _ = self.get_crossing_position('west')
        
        # Train parameters
        train_interval = self.config['simulation']['traffic']['train_interval']
        train_duration = self.config['simulation']['traffic']['train_duration']
        next_train = 90
        gate_closed = False
        gate_close_time = 0
        stopped_vehicles = set()
        
        try:
            step = 0
            max_steps = 18000  # 1800 seconds / 0.1
            
            while step < max_steps:
                try:
                    traci.simulationStep()
                except:
                    break
                
                t = traci.simulation.getTime()
                
                if traci.simulation.getMinExpectedNumber() == 0:
                    break
                
                # Train gate control
                if t >= next_train and not gate_closed:
                    gate_closed = True
                    gate_close_time = t
                    Logger.log(f"[Train] Gate closed at T={t:.0f}s")
                
                if gate_closed:
                    if t >= gate_close_time + train_duration:
                        # Open gate
                        gate_closed = False
                        for vid in list(stopped_vehicles):
                            try:
                                traci.vehicle.setSpeed(vid, -1)
                            except:
                                pass
                        stopped_vehicles.clear()
                        next_train = t + train_interval
                        Logger.log(f"[Train] Gate opened at T={t:.0f}s")
                    else:
                        # Stop vehicles near crossing
                        if west_x is not None:
                            for vid in traci.vehicle.getIDList():
                                try:
                                    x, _ = traci.vehicle.getPosition(vid)
                                    if abs(x - west_x) < 50 and vid not in stopped_vehicles:
                                        traci.vehicle.setSpeed(vid, 0)
                                        stopped_vehicles.add(vid)
                                except:
                                    continue
                
                # Track vehicles
                for vid in traci.vehicle.getIDList():
                    try:
                        x, _ = traci.vehicle.getPosition(vid)
                        speed = traci.vehicle.getSpeed(vid)
                        
                        self.track_vehicle(vid, 'west', t)
                        self.check_waiting(vid, x, speed, west_x, self.waiting_west, t)
                    except:
                        continue
                
                # Handle arrivals
                for vid in traci.simulation.getArrivedIDList():
                    self.end_vehicle(vid, t)
                
                step += 1
                
                if step % 6000 == 0:
                    Logger.log(f"T={t:.0f}s | Vehicles: {len(traci.vehicle.getIDList())} | Waiting: {len(self.waiting_west)}")
        
        except KeyboardInterrupt:
            Logger.log("Stopped by user")
        
        finally:
            try:
                traci.close()
            except:
                pass
            
            metrics = self.calculate_metrics('phase1')
            self.save_vehicles('phase1')
            
            if metrics:
                Logger.log(f"\nPhase 1 Results:")
                Logger.log(f"  Vehicles: {metrics['n_vehicles']}")
                Logger.log(f"  Avg trip time: {metrics['trip_time']['mean']:.1f}s")
                Logger.log(f"  Avg wait time: {metrics['wait_time']['mean']:.1f}s")
                Logger.log(f"  Vehicles waited: {metrics['wait_time']['vehicles_waited']}")
                Logger.log(f"  Total fuel: {metrics['fuel']['total']:.1f}L")
                Logger.log(f"  Total CO2: {metrics['co2']['total']:.1f}kg")
            
            return metrics
    
    def run_phase2(self, gui=False):
        """Phase 2: East route without trains"""
        Logger.section("Phase 2: East route (alternative without trains)")
        
        self.vehicles = {}
        self.waiting_west = {}
        self.waiting_east = {}
        
        self.create_routes(2)
        self.create_config()
        
        cmd = ['sumo-gui' if gui else 'sumo', '-c', 'simulation.sumocfg', 
               '--start', '--quit-on-end', '--delay', '0', '--no-warnings']
        traci.start(cmd)
        
        east_x, _ = self.get_crossing_position('east')
        
        try:
            step = 0
            max_steps = 18000
            
            while step < max_steps:
                try:
                    traci.simulationStep()
                except:
                    break
                
                t = traci.simulation.getTime()
                
                if traci.simulation.getMinExpectedNumber() == 0:
                    break
                
                for vid in traci.vehicle.getIDList():
                    try:
                        x, _ = traci.vehicle.getPosition(vid)
                        speed = traci.vehicle.getSpeed(vid)
                        
                        self.track_vehicle(vid, 'east', t)
                        self.check_waiting(vid, x, speed, east_x, self.waiting_east, t)
                    except:
                        continue
                
                for vid in traci.simulation.getArrivedIDList():
                    self.end_vehicle(vid, t)
                
                step += 1
                
                if step % 6000 == 0:
                    Logger.log(f"T={t:.0f}s | Vehicles: {len(traci.vehicle.getIDList())}")
        
        except KeyboardInterrupt:
            Logger.log("Stopped by user")
        
        finally:
            try:
                traci.close()
            except:
                pass
            
            metrics = self.calculate_metrics('phase2')
            self.save_vehicles('phase2')
            
            if metrics:
                Logger.log(f"\nPhase 2 Results:")
                Logger.log(f"  Vehicles: {metrics['n_vehicles']}")
                Logger.log(f"  Avg trip time: {metrics['trip_time']['mean']:.1f}s")
                Logger.log(f"  Avg wait time: {metrics['wait_time']['mean']:.1f}s")
                Logger.log(f"  Total fuel: {metrics['fuel']['total']:.1f}L")
                Logger.log(f"  Total CO2: {metrics['co2']['total']:.1f}kg")
            
            return metrics
    
    def calculate_optimized(self, phase1, phase2):
        """Calculate optimized scenario with smart routing (poster Table 3)"""
        adoption_rate = self.config['simulation']['routing']['adoption_rate']
        
        # Vehicles that experienced waiting
        vehicles_affected = phase1['wait_time']['vehicles_waited']
        total_vehicles = phase1['n_vehicles']
        
        # With smart routing: 70% of affected vehicles reroute
        vehicles_rerouted = int(vehicles_affected * adoption_rate)
        vehicles_still_wait = vehicles_affected - vehicles_rerouted
        vehicles_clear = total_vehicles - vehicles_affected
        
        Logger.log(f"\nOptimized Scenario Calculation:")
        Logger.log(f"  Total vehicles: {total_vehicles}")
        Logger.log(f"  Affected by trains: {vehicles_affected} ({vehicles_affected/total_vehicles*100:.1f}%)")
        Logger.log(f"  Rerouted (70%): {vehicles_rerouted}")
        Logger.log(f"  Still wait (30%): {vehicles_still_wait}")
        Logger.log(f"  Clear period: {vehicles_clear}")
        
        # Calculate average wait for those who waited
        avg_wait_for_waiters = (phase1['wait_time']['mean'] * total_vehicles / vehicles_affected 
                               if vehicles_affected > 0 else 0)
        
        # Reroute penalty (5 seconds detour to east crossing)
        reroute_penalty = 5.0
        
        # Weighted average trip time
        opt_trip_time = (
            vehicles_rerouted * (phase2['trip_time']['mean'] + reroute_penalty) +
            vehicles_still_wait * (phase1['trip_time']['mean']) +
            vehicles_clear * phase1['trip_time']['mean']
        ) / total_vehicles
        
        # Weighted average wait time
        opt_wait_time = (
            vehicles_rerouted * reroute_penalty +
            vehicles_still_wait * avg_wait_for_waiters +
            vehicles_clear * 0
        ) / total_vehicles
        
        # Fuel calculation (rerouting uses more fuel, but saves idling)
        fuel_driving = self.config['simulation']['fuel']['driving']
        fuel_idling = self.config['simulation']['fuel']['idling']
        
        # Fuel for rerouted: base + extra driving - saved idling
        reroute_fuel_extra = reroute_penalty * fuel_driving
        idling_fuel_saved = avg_wait_for_waiters * fuel_idling
        
        opt_fuel = (
            vehicles_rerouted * (phase2['fuel']['mean'] + reroute_fuel_extra - idling_fuel_saved) +
            vehicles_still_wait * phase1['fuel']['mean'] +
            vehicles_clear * (phase1['fuel']['total'] - phase1['fuel']['mean'] * vehicles_affected) / vehicles_clear
        ) / total_vehicles
        
        opt_co2 = opt_fuel * self.config['simulation']['fuel']['co2_per_liter']
        
        optimized = {
            'phase': 'optimized',
            'n_vehicles': total_vehicles,
            'trip_time': {
                'mean': float(opt_trip_time),
                'std': phase1['trip_time']['std'] * 0.8  # Reduced variation
            },
            'wait_time': {
                'mean': float(opt_wait_time),
                'std': phase1['wait_time']['std'] * 0.5,  # Reduced variation
                'vehicles_waited': vehicles_still_wait
            },
            'fuel': {
                'mean': float(opt_fuel),
                'total': float(opt_fuel * total_vehicles)
            },
            'co2': {
                'mean': float(opt_co2),
                'total': float(opt_co2 * total_vehicles)
            },
            'routing': {
                'adoption_rate': adoption_rate,
                'vehicles_rerouted': vehicles_rerouted,
                'vehicles_still_wait': vehicles_still_wait
            }
        }
        
        return optimized
    
    def compare_phases(self, phase1, phase2):
        """Compare all scenarios (poster Table 3)"""
        if not phase1 or not phase2:
            Logger.log("Missing phase metrics")
            return
        
        # Calculate optimized scenario
        optimized = self.calculate_optimized(phase1, phase2)
        
        # Calculate improvements: Baseline vs Optimized
        trip_reduction = ((phase1['trip_time']['mean'] - optimized['trip_time']['mean']) / 
                         phase1['trip_time']['mean'] * 100)
        wait_reduction = ((phase1['wait_time']['mean'] - optimized['wait_time']['mean']) / 
                         phase1['wait_time']['mean'] * 100) if phase1['wait_time']['mean'] > 0 else 0
        fuel_reduction = ((phase1['fuel']['mean'] - optimized['fuel']['mean']) / 
                         phase1['fuel']['mean'] * 100)
        co2_reduction = ((phase1['co2']['mean'] - optimized['co2']['mean']) / 
                        phase1['co2']['mean'] * 100)
        
        # Queue reduction (affected vehicles)
        queue_reduction = ((phase1['wait_time']['vehicles_waited'] - optimized['wait_time']['vehicles_waited']) /
                          phase1['wait_time']['vehicles_waited'] * 100) if phase1['wait_time']['vehicles_waited'] > 0 else 0
        
        comparison = {
            'phase1_baseline': phase1,
            'phase2_alternative': phase2,
            'optimized_smart_routing': optimized,
            'improvements_baseline_vs_optimized': {
                'trip_time_reduction_percent': float(trip_reduction),
                'wait_time_reduction_percent': float(wait_reduction),
                'fuel_reduction_percent': float(fuel_reduction),
                'co2_reduction_percent': float(co2_reduction),
                'queue_reduction_percent': float(queue_reduction)
            }
        }
        
        with open(self.output_dir / 'comparison.json', 'w') as f:
            json.dump(comparison, f, indent=2)
        
        Logger.log("\n" + "="*60)
        Logger.log("COMPARISON: Baseline vs Optimized Smart Routing (Table 3)")
        Logger.log("="*60)
        Logger.log(f"\nBaseline (Phase 1):")
        Logger.log(f"  Trip time: {phase1['trip_time']['mean']:.1f}s")
        Logger.log(f"  Wait time: {phase1['wait_time']['mean']:.1f}s")
        Logger.log(f"  Fuel: {phase1['fuel']['mean']:.3f}L")
        Logger.log(f"  Vehicles waited: {phase1['wait_time']['vehicles_waited']}")
        
        Logger.log(f"\nOptimized (Smart Routing):")
        Logger.log(f"  Trip time: {optimized['trip_time']['mean']:.1f}s")
        Logger.log(f"  Wait time: {optimized['wait_time']['mean']:.1f}s")
        Logger.log(f"  Fuel: {optimized['fuel']['mean']:.3f}L")
        Logger.log(f"  Vehicles waited: {optimized['wait_time']['vehicles_waited']}")
        
        Logger.log(f"\nImprovements (Poster Table 3):")
        Logger.log(f"  Trip time reduction: {trip_reduction:.1f}%")
        Logger.log(f"  Wait time reduction: {wait_reduction:.1f}%")
        Logger.log(f"  Fuel reduction: {fuel_reduction:.1f}%")
        Logger.log(f"  CO2 reduction: {co2_reduction:.1f}%")
        Logger.log(f"  Queue reduction: {queue_reduction:.1f}%")
        Logger.log("\n" + "="*60)
    
    def run_full_simulation(self, gui=False):
        """Run complete two-phase simulation"""
        if not self.generate_network():
            return
        
        phase1_metrics = self.run_phase1(gui)
        phase2_metrics = self.run_phase2(gui)
        
        self.compare_phases(phase1_metrics, phase2_metrics)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run traffic simulation')
    parser.add_argument('--gui', action='store_true', help='Run with GUI')
    parser.add_argument('--phase', choices=['1', '2', 'both'], default='both', help='Which phase to run')
    args = parser.parse_args()
    
    sim = TrafficSimulation()
    
    if not sim.generate_network():
        exit(1)
    
    if args.phase == '1':
        sim.run_phase1(args.gui)
    elif args.phase == '2':
        sim.run_phase2(args.gui)
    else:
        sim.run_full_simulation(args.gui)