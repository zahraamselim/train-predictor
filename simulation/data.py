import traci
import yaml
from pathlib import Path


class RailroadCrossing:
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.actual_x = None
        self.actual_y = None
        self.gate_closed = False
        self.gate_close_time = None
        self.stopped_vehicles = set()
        self.waiting_vehicles = {}
    
    def setup_visuals(self):
        crossing_id = f"{self.name.lower()}_crossing"
        actual_pos = traci.junction.getPosition(crossing_id)
        self.actual_x = actual_pos[0]
        self.actual_y = actual_pos[1]
        self._add_gates()
    
    def _add_gates(self):
        gate_w = 25
        gate_h = 3
        road_sep = 200
        
        north_y = self.actual_y + road_sep / 2
        south_y = self.actual_y - road_sep / 2
        
        gate_north = [
            (self.actual_x - gate_w/2, north_y + 2),
            (self.actual_x + gate_w/2, north_y + 2),
            (self.actual_x + gate_w/2, north_y + 2 + gate_h),
            (self.actual_x - gate_w/2, north_y + 2 + gate_h)
        ]
        traci.polygon.add(f"{self.name}_gate_n", gate_north, (0, 200, 0, 255), True, "gate", 10)
        
        gate_south = [
            (self.actual_x - gate_w/2, south_y - 2),
            (self.actual_x + gate_w/2, south_y - 2),
            (self.actual_x + gate_w/2, south_y - 2 - gate_h),
            (self.actual_x - gate_w/2, south_y - 2 - gate_h)
        ]
        traci.polygon.add(f"{self.name}_gate_s", gate_south, (0, 200, 0, 255), True, "gate", 10)
    
    def close_gate(self, current_time):
        if not self.gate_closed:
            self.gate_closed = True
            self.gate_close_time = current_time
            print(f"[{self.name}] Gate closed at T={current_time:.0f}s")
    
    def open_gate(self, current_time):
        if self.gate_closed:
            self.gate_closed = False
            self.stopped_vehicles.clear()
            print(f"[{self.name}] Gate opened at T={current_time:.0f}s")
    
    def control_vehicles(self):
        if not self.gate_closed or self.actual_x is None:
            return
        
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            try:
                x, _ = traci.vehicle.getPosition(vid)
                distance = abs(x - self.actual_x)
                
                if distance < 50 and vid not in self.stopped_vehicles:
                    traci.vehicle.setSpeed(vid, 0)
                    self.stopped_vehicles.add(vid)
            except:
                continue
    
    def release_vehicles(self):
        for vid in list(self.stopped_vehicles):
            try:
                traci.vehicle.setSpeed(vid, -1)
            except:
                pass
        self.stopped_vehicles.clear()
    
    def track_vehicle_waiting(self, vid, x_pos, speed, current_time):
        distance = abs(x_pos - self.actual_x) if self.actual_x else 999
        
        if distance > 100:
            return None, None
        
        is_stopped = speed < 0.5
        
        if is_stopped and vid not in self.waiting_vehicles:
            self.waiting_vehicles[vid] = current_time
            return 'start', self.name.lower()
        
        elif not is_stopped and vid in self.waiting_vehicles:
            del self.waiting_vehicles[vid]
            return 'end', self.name.lower()
        
        return None, None
    
    def update_visuals(self):
        gate_color = (200, 0, 0, 255) if self.gate_closed else (0, 200, 0, 255)
        traci.polygon.setColor(f"{self.name}_gate_n", gate_color)
        traci.polygon.setColor(f"{self.name}_gate_s", gate_color)


class DataCollector:
    def __init__(self, config_path='simulation/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        cross_dist = self.config['network']['crossing_distance']
        self.west = RailroadCrossing("West", -cross_dist/2)
        self.east = RailroadCrossing("East", cross_dist/2)
    
    def generate_routes(self, route_type):
        traffic = self.config['traffic']
        
        if route_type == 'west':
            routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="4.5" maxSpeed="20" accel="2.6" decel="4.5" sigma="0.5" color="70,130,180"/>
    <route id="route_west" edges="n_in_w v_w_n_s v_w_x_s s_w_e s_out_e"/>
    <flow id="cars" type="car" route="route_west" begin="0" end="1800" vehsPerHour="{traffic['cars_per_hour']}"/>
</routes>
"""
        else:
            routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="4.5" maxSpeed="20" accel="2.6" decel="4.5" sigma="0.5" color="255,140,0"/>
    <route id="route_east" edges="n_in_w n_w_e v_e_n_s v_e_x_s s_out_e"/>
    <flow id="cars" type="car" route="route_east" begin="0" end="1800" vehsPerHour="{traffic['cars_per_hour']}"/>
</routes>
"""
        
        Path('simulation.rou.xml').write_text(routes)
    
    def track_vehicles(self, t, metrics):
        for vid in traci.vehicle.getIDList():
            try:
                x, _ = traci.vehicle.getPosition(vid)
                speed = traci.vehicle.getSpeed(vid)
                
                if vid not in metrics.vehicles:
                    route = traci.vehicle.getRoute(vid)
                    
                    if 'v_e_n_s' in route or 'v_e_x_s' in route:
                        metrics.start_vehicle(vid, 'east', 'phase2_route', t)
                    else:
                        metrics.start_vehicle(vid, 'west', 'phase1_route', t)
                
                action_west, _ = self.west.track_vehicle_waiting(vid, x, speed, t)
                if action_west == 'start':
                    metrics.record_wait_start(vid, 'west', t)
                elif action_west == 'end':
                    metrics.record_wait_end(vid, t)
                
                action_east, _ = self.east.track_vehicle_waiting(vid, x, speed, t)
                if action_east == 'start':
                    metrics.record_wait_start(vid, 'east', t)
                elif action_east == 'end':
                    metrics.record_wait_end(vid, t)
            
            except Exception:
                continue
        
        arrived = traci.simulation.getArrivedIDList()
        for vid in arrived:
            if vid in metrics.vehicles:
                metrics.end_vehicle(vid, t)