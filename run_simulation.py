"""
Traffic simulation for poster metrics
Replaces: simulation/network.py, simulation/controller.py, simulation/data.py, simulation/metrics.py
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
        self.waiting_vehicles_west = set()
        self.waiting_vehicles_east = set()
        self.queue_samples_west = []
        self.queue_samples_east = []
    
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
    
    <node id="rail_west" x="-{length}" y="0" type="priority"/>
    <node id="rail_east" x="{length}" y="0" type="priority"/>
    
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
    
    <edge id="rail_in" from="rail_west" to="west_crossing" numLanes="1" speed="33.33" allow="rail"/>
    <edge id="rail_mid" from="west_crossing" to="east_crossing" numLanes="1" speed="33.33" allow="rail"/>
    <edge id="rail_out" from="east_crossing" to="rail_east" numLanes="1" speed="33.33" allow="rail"/>
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
        
        self.create_view_settings()
        Logger.log("Network created: simulation.net.xml")
        return True
    
    def create_view_settings(self):
        """Create GUI view settings (same visual appearance)"""
        view = """<?xml version="1.0" encoding="UTF-8"?>
<viewsettings>
    <scheme name="realistic">
        <background backgroundColor="102,178,102" showGrid="0"/>
        <edges laneEdgeMode="0" scaleMode="0" laneShowBorders="1" 
            edgeColor="70,70,70" edgeColorSelected="255,255,0"
            edgeName.show="0" streetName.show="0"/>
        <vehicles vehicleQuality="3" vehicleSize="3.0" vehicleShape="3"
            showBlinker="1" drawMinGap="0" drawBrakeGap="0"
            vehicleName.show="0" vehicleColorMode="0"/>
        <junctions junctionMode="0" drawLinkTLIndex="0" drawLinkJunctionIndex="0"
            drawCrossingsAndWalkingareas="0" showLane2Lane="0"
            tlsPhaseIndex.show="0" junctionName.show="0"/>
    </scheme>
</viewsettings>"""
        Path('view.xml').write_text(view)
    
    def create_routes(self, phase):
        """Create route file for phase 1 (west) or phase 2 (east)"""
        traffic = self.config['simulation']['traffic']
        duration = self.config['simulation']['duration']
        
        if phase == 1:
            routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="4.5" maxSpeed="20" accel="2.6" decel="4.5" sigma="0.5" color="70,130,180"/>
    <route id="route_west" edges="n_in_w v_w_n_s v_w_x_s s_w_e s_out_e"/>
    <flow id="cars" type="car" route="route_west" begin="0" end="{duration}" vehsPerHour="{traffic['cars_per_hour']}"/>
</routes>"""
        else:
            routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="4.5" maxSpeed="20" accel="2.6" decel="4.5" sigma="0.5" color="255,140,0"/>
    <route id="route_east" edges="n_in_w n_w_e v_e_n_s v_e_x_s s_out_e"/>
    <flow id="cars" type="car" route="route_east" begin="0" end="{duration}" vehsPerHour="{traffic['cars_per_hour']}"/>
</routes>"""
        
        Path('simulation.rou.xml').write_text(routes)
    
    def create_config(self):
        """Create SUMO configuration file"""
        sim = self.config['simulation']
        
        config = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="simulation.net.xml"/>
        <route-files value="simulation.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{sim['duration']}"/>
        <step-length value="{sim['step_size']}"/>
    </time>
    <processing>
        <ignore-route-errors value="true"/>
        <time-to-teleport value="-1"/>
    </processing>
    <gui_only>
        <gui-settings-file value="view.xml"/>
    </gui_only>
</configuration>"""
        
        Path('simulation.sumocfg').write_text(config)
    
    def setup_crossing(self, crossing_name, x_pos):
        """Setup visual gate representation"""
        y = 0
        gate_w = 25
        gate_h = 3
        road_sep = self.config['network']['road_separation']
        
        north_y = y + road_sep / 2
        south_y = y - road_sep / 2
        
        gate_north = [
            (x_pos - gate_w/2, north_y + 2),
            (x_pos + gate_w/2, north_y + 2),
            (x_pos + gate_w/2, north_y + 2 + gate_h),
            (x_pos - gate_w/2, north_y + 2 + gate_h)
        ]
        traci.polygon.add(f"{crossing_name}_gate_n", gate_north, (0, 200, 0, 255), True, "gate", 10)
        
        gate_south = [
            (x_pos - gate_w/2, south_y - 2),
            (x_pos + gate_w/2, south_y - 2),
            (x_pos + gate_w/2, south_y - 2 - gate_h),
            (x_pos - gate_w/2, south_y - 2 - gate_h)
        ]
        traci.polygon.add(f"{crossing_name}_gate_s", gate_south, (0, 200, 0, 255), True, "gate", 10)
        
        return {'x': x_pos, 'gates': [f"{crossing_name}_gate_n", f"{crossing_name}_gate_s"], 'closed': False, 'stopped': set()}
    
    def close_gate(self, crossing):
        """Close gate (turn red, stop vehicles)"""
        if not crossing['closed']:
            crossing['closed'] = True
            for gate in crossing['gates']:
                traci.polygon.setColor(gate, (200, 0, 0, 255))
    
    def open_gate(self, crossing):
        """Open gate (turn green, release vehicles)"""
        if crossing['closed']:
            crossing['closed'] = False
            for gate in crossing['gates']:
                traci.polygon.setColor(gate, (0, 200, 0, 255))
            for vid in list(crossing['stopped']):
                try:
                    traci.vehicle.setSpeed(vid, -1)
                except:
                    pass
            crossing['stopped'].clear()
    
    def control_vehicles_at_crossing(self, crossing):
        """Stop vehicles near closed crossing"""
        if not crossing['closed']:
            return
        
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            try:
                x, _ = traci.vehicle.getPosition(vid)
                if abs(x - crossing['x']) < 50 and vid not in crossing['stopped']:
                    traci.vehicle.setSpeed(vid, 0)
                    crossing['stopped'].add(vid)
            except:
                continue
    
    def track_vehicle(self, vid, route_choice, t):
        """Track vehicle metrics"""
        if vid not in self.vehicles:
            self.vehicles[vid] = {
                'start_time': t,
                'end_time': None,
                'route': route_choice,
                'wait_start': None,
                'total_wait': 0,
                'trip_time': None
            }
    
    def track_waiting(self, vid, x, speed, t, crossing_x, is_west):
        """Track vehicle waiting at crossing"""
        if abs(x - crossing_x) > 100:
            return
        
        v = self.vehicles.get(vid)
        if not v:
            return
        
        is_stopped = speed < 0.5
        
        if is_stopped and v['wait_start'] is None:
            v['wait_start'] = t
            if is_west:
                self.waiting_vehicles_west.add(vid)
            else:
                self.waiting_vehicles_east.add(vid)
        
        elif not is_stopped and v['wait_start'] is not None:
            v['total_wait'] += (t - v['wait_start'])
            v['wait_start'] = None
            self.waiting_vehicles_west.discard(vid)
            self.waiting_vehicles_east.discard(vid)
    
    def end_vehicle(self, vid, t):
        """Mark vehicle as completed"""
        if vid in self.vehicles:
            v = self.vehicles[vid]
            if v['wait_start'] is not None:
                v['total_wait'] += (t - v['wait_start'])
            v['end_time'] = t
            v['trip_time'] = t - v['start_time']
    
    def calculate_metrics(self, phase_name):
        """Calculate performance metrics"""
        completed = [v for v in self.vehicles.values() if v['end_time'] is not None]
        
        if not completed:
            Logger.log(f"No completed vehicles in {phase_name}")
            return None
        
        trip_times = [v['trip_time'] for v in completed]
        wait_times = [v['total_wait'] for v in completed]
        
        fuel = self.config['simulation']['fuel']
        fuel_consumed = []
        co2_emitted = []
        
        for v in completed:
            driving_time = v['trip_time'] - v['total_wait']
            idling_time = v['total_wait']
            
            fuel_used = driving_time * fuel['driving'] + idling_time * fuel['idling']
            fuel_consumed.append(fuel_used)
            co2_emitted.append(fuel_used * fuel['co2_per_liter'])
        
        avg_west_queue = np.mean([s for s in self.queue_samples_west]) if self.queue_samples_west else 0
        max_west_queue = max(self.queue_samples_west) if self.queue_samples_west else 0
        avg_east_queue = np.mean([s for s in self.queue_samples_east]) if self.queue_samples_east else 0
        max_east_queue = max(self.queue_samples_east) if self.queue_samples_east else 0
        
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
            },
            'queue': {
                'west_avg': float(avg_west_queue),
                'west_max': int(max_west_queue),
                'east_avg': float(avg_east_queue),
                'east_max': int(max_east_queue)
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
                'wait_time': v['total_wait']
            })
        
        df = pd.DataFrame(records)
        df.to_csv(self.output_dir / f'{phase_name}_vehicles.csv', index=False)
        Logger.log(f"Saved: {self.output_dir / f'{phase_name}_vehicles.csv'}")
    
    def run_phase1(self, gui=False):
        """Phase 1: West route with trains blocking"""
        Logger.section("Phase 1: West route (baseline with trains)")
        
        self.create_routes(1)
        self.create_config()
        
        cmd = ['sumo-gui' if gui else 'sumo', '-c', 'simulation.sumocfg', 
               '--start', '--quit-on-end', '--delay', '0', '--no-warnings']
        traci.start(cmd)
        
        cross_dist = self.config['network']['crossing_distance']
        west_crossing = self.setup_crossing('west', -cross_dist / 2)
        east_crossing = self.setup_crossing('east', cross_dist / 2)
        
        traffic = self.config['simulation']['traffic']
        train_interval = traffic['train_interval']
        train_duration = traffic['train_duration']
        next_train = 90
        
        try:
            step = 0
            dt = self.config['simulation']['step_size']
            max_steps = int(self.config['simulation']['duration'] / dt)
            
            while step < max_steps:
                try:
                    traci.simulationStep()
                except:
                    break
                
                t = traci.simulation.getTime()
                
                if traci.simulation.getMinExpectedNumber() == 0:
                    break
                
                if t >= next_train and not west_crossing['closed']:
                    self.close_gate(west_crossing)
                    gate_close_time = t
                
                if west_crossing['closed']:
                    if t >= gate_close_time + train_duration:
                        self.open_gate(west_crossing)
                        next_train = t + train_interval
                    else:
                        self.control_vehicles_at_crossing(west_crossing)
                
                for vid in traci.vehicle.getIDList():
                    try:
                        x, _ = traci.vehicle.getPosition(vid)
                        speed = traci.vehicle.getSpeed(vid)
                        self.track_vehicle(vid, 'west', t)
                        self.track_waiting(vid, x, speed, t, west_crossing['x'], True)
                    except:
                        continue
                
                for vid in traci.simulation.getArrivedIDList():
                    self.end_vehicle(vid, t)
                
                if step % 100 == 0:
                    self.queue_samples_west.append(len(self.waiting_vehicles_west))
                    self.queue_samples_east.append(len(self.waiting_vehicles_east))
                
                step += 1
                
                if step % 6000 == 0:
                    Logger.log(f"T={t:.0f}s | Vehicles: {len(traci.vehicle.getIDList())} | Queue: {len(self.waiting_vehicles_west)}")
        
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
                with open(self.output_dir / 'phase1_metrics.json', 'w') as f:
                    json.dump(metrics, f, indent=2)
                
                Logger.log(f"\nPhase 1 Results:")
                Logger.log(f"  Vehicles: {metrics['n_vehicles']}")
                Logger.log(f"  Avg trip time: {metrics['trip_time']['mean']:.1f}s")
                Logger.log(f"  Avg wait time: {metrics['wait_time']['mean']:.1f}s")
                Logger.log(f"  Vehicles waited: {metrics['wait_time']['vehicles_waited']}")
                Logger.log(f"  Total fuel: {metrics['fuel']['total']:.1f}L")
                Logger.log(f"  Total CO2: {metrics['co2']['total']:.1f}kg")
                Logger.log(f"  Max queue: {metrics['queue']['west_max']}")
            
            return metrics
    
    def run_phase2(self, gui=False):
        """Phase 2: East route without trains"""
        Logger.section("Phase 2: East route (alternative without trains)")
        
        self.vehicles = {}
        self.waiting_vehicles_west = set()
        self.waiting_vehicles_east = set()
        self.queue_samples_west = []
        self.queue_samples_east = []
        
        self.create_routes(2)
        self.create_config()
        
        cmd = ['sumo-gui' if gui else 'sumo', '-c', 'simulation.sumocfg', 
               '--start', '--quit-on-end', '--delay', '0', '--no-warnings']
        traci.start(cmd)
        
        cross_dist = self.config['network']['crossing_distance']
        west_crossing = self.setup_crossing('west', -cross_dist / 2)
        east_crossing = self.setup_crossing('east', cross_dist / 2)
        
        try:
            step = 0
            dt = self.config['simulation']['step_size']
            max_steps = int(self.config['simulation']['duration'] / dt)
            
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
                    except:
                        continue
                
                for vid in traci.simulation.getArrivedIDList():
                    self.end_vehicle(vid, t)
                
                if step % 100 == 0:
                    self.queue_samples_west.append(len(self.waiting_vehicles_west))
                    self.queue_samples_east.append(len(self.waiting_vehicles_east))
                
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
                with open(self.output_dir / 'phase2_metrics.json', 'w') as f:
                    json.dump(metrics, f, indent=2)
                
                Logger.log(f"\nPhase 2 Results:")
                Logger.log(f"  Vehicles: {metrics['n_vehicles']}")
                Logger.log(f"  Avg trip time: {metrics['trip_time']['mean']:.1f}s")
                Logger.log(f"  Avg wait time: {metrics['wait_time']['mean']:.1f}s")
                Logger.log(f"  Total fuel: {metrics['fuel']['total']:.1f}L")
                Logger.log(f"  Total CO2: {metrics['co2']['total']:.1f}kg")
            
            return metrics
    
    def compare_phases(self, phase1, phase2):
        """Compare phase 1 vs phase 2 (for poster table)"""
        if not phase1 or not phase2:
            Logger.log("Missing phase metrics")
            return
        
        trip_reduction = (phase1['trip_time']['mean'] - phase2['trip_time']['mean']) / phase1['trip_time']['mean'] * 100
        wait_reduction = (phase1['wait_time']['mean'] - phase2['wait_time']['mean']) / phase1['wait_time']['mean'] * 100
        fuel_reduction = (phase1['fuel']['total'] - phase2['fuel']['total']) / phase1['fuel']['total'] * 100
        co2_reduction = (phase1['co2']['total'] - phase2['co2']['total']) / phase1['co2']['total'] * 100
        queue_reduction = (phase1['queue']['west_max'] - phase2['queue']['west_max']) / phase1['queue']['west_max'] * 100
        
        comparison = {
            'phase1_baseline': phase1,
            'phase2_alternative': phase2,
            'improvements': {
                'trip_time_reduction_percent': float(trip_reduction),
                'wait_time_reduction_percent': float(wait_reduction),
                'fuel_reduction_percent': float(fuel_reduction),
                'co2_reduction_percent': float(co2_reduction),
                'queue_reduction_percent': float(queue_reduction)
            }
        }
        
        with open(self.output_dir / 'comparison.json', 'w') as f:
            json.dump(comparison, f, indent=2)
        
        Logger.log("COMPARISON: Baseline vs Alternative Route")
        Logger.log(f"\nTrip time reduction: {trip_reduction:.1f}%")
        Logger.log(f"Wait time reduction: {wait_reduction:.1f}%")
        Logger.log(f"Fuel reduction: {fuel_reduction:.1f}%")
        Logger.log(f"CO2 reduction: {co2_reduction:.1f}%")
        Logger.log(f"Queue reduction: {queue_reduction:.1f}%")
    
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
    parser.add_argument('--config', default='config.yaml', help='Config file path')
    args = parser.parse_args()
    
    sim = TrafficSimulation(args.config)
    
    if not sim.generate_network():
        exit(1)
    
    if args.phase == '1':
        sim.run_phase1(args.gui)
    elif args.phase == '2':
        sim.run_phase2(args.gui)
    else:
        sim.run_full_simulation(args.gui)