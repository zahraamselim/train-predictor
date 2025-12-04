import traci
import yaml
from pathlib import Path
from utils.logger import Logger
from simulation.metrics import MetricsTracker


class RailroadCrossing:
    def __init__(self, name, position, config):
        self.name = name
        self.position = position
        self.actual_x = None
        self.actual_y = None
        
        self.sensor_distances = config['sensors']
        self.sensor_positions = [position - d for d in self.sensor_distances]
        
        self.close_time = config['close_before_arrival']
        self.open_time = config['open_after_departure']
        self.warning_time = config['warning_time']
        
        self.trains = {}
        self.gate_closed = False
        self.warning_active = False
        self.countdown = 0
        self.gate_close_time = None
    
    def detect_train(self, train_id, x_position, speed, current_time):
        if train_id not in self.trains:
            self.trains[train_id] = {
                'detections': {},
                'eta': None,
                'eta_time': None,
                'arrived': False,
                'departed': False
            }
        
        train = self.trains[train_id]
        
        for i, sensor_x in enumerate(self.sensor_positions):
            if i not in train['detections'] and x_position >= sensor_x:
                train['detections'][i] = {'time': current_time, 'speed': speed}
                
                if i == 0:
                    Logger.log(f"{self.name}: Train detected")
        
        if len(train['detections']) == 3 and train['eta'] is None:
            train['eta'] = self._calculate_eta(train)
            train['eta_time'] = current_time
            self.countdown = train['eta']
            Logger.log(f"{self.name}: ETA = {train['eta']:.1f}s")
        
        if x_position >= self.position and not train['arrived']:
            train['arrived'] = True
            train['arrival_time'] = current_time
            Logger.log(f"{self.name}: Train arrived")
        
        if train['arrived'] and x_position >= self.position + 150 and not train['departed']:
            train['departed'] = True
            train['departure_time'] = current_time
            Logger.log(f"{self.name}: Train departed")
    
    def _calculate_eta(self, train):
        d = train['detections']
        
        time_0_1 = d[1]['time'] - d[0]['time']
        time_1_2 = d[2]['time'] - d[1]['time']
        
        dist_0_1 = abs(self.sensor_positions[1] - self.sensor_positions[0])
        dist_1_2 = abs(self.sensor_positions[2] - self.sensor_positions[1])
        
        speed_recent = dist_1_2 / time_1_2 if time_1_2 > 0 else 30.0
        
        distance_remaining = abs(self.position - self.sensor_positions[2])
        eta = distance_remaining / speed_recent if speed_recent > 0 else distance_remaining / 30.0
        
        return eta
    
    def update(self, current_time):
        for train in self.trains.values():
            if train['eta'] is None:
                continue
            
            time_since_eta = current_time - train['eta_time']
            time_until_arrival = train['eta'] - time_since_eta
            
            if time_until_arrival <= self.close_time and not self.gate_closed:
                self.gate_closed = True
                self.gate_close_time = current_time
                Logger.log(f"{self.name}: GATE CLOSED")
            
            if train['departed'] and self.gate_closed:
                time_since_departure = current_time - train['departure_time']
                if time_since_departure >= self.open_time:
                    self.gate_closed = False
                    self.warning_active = False
                    Logger.log(f"{self.name}: GATE OPENED")
                    del self.trains[list(self.trains.keys())[0]]
                    break
            
            if not self.gate_closed and time_until_arrival > 0:
                self.countdown = time_until_arrival - self.close_time
            elif self.gate_closed:
                if train['departed']:
                    self.countdown = self.open_time - (current_time - train['departure_time'])
                else:
                    self.countdown = max(0, time_until_arrival)
            
            if time_until_arrival <= self.warning_time and not self.warning_active:
                self.warning_active = True
                Logger.log(f"{self.name}: Warning activated")
    
    def get_traffic_light_ids(self):
        """Get the traffic light junction IDs for this crossing"""
        if self.name == "West":
            return ["nw_junction", "sw_junction"]
        else:
            return ["ne_junction", "se_junction"]
    
    def get_wait_time(self, current_time):
        for train in self.trains.values():
            if train['eta'] is not None and not train['departed']:
                if train['arrived']:
                    return self.open_time + 2.0
                else:
                    time_since_eta = current_time - train['eta_time']
                    time_until_arrival = train['eta'] - time_since_eta
                    return max(0, time_until_arrival + self.open_time + 2.0)
        return 0
    
    def setup_visuals(self):
        crossing_id = "west_crossing" if self.name == "West" else "east_crossing"
        actual_pos = traci.junction.getPosition(crossing_id)
        self.actual_x = actual_pos[0]
        self.actual_y = actual_pos[1]
        
        Logger.log(f"{self.name} crossing at SUMO coords: x={self.actual_x}, y={self.actual_y}")
        
        self._add_gates()
        self._add_sensors()
        self._add_warning_lights()
        self._add_countdown_timer()
        self._add_buildings_and_landscape()
    
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
    
    def _add_sensors(self):
        sensor_distances = [1500, 1000, 500]
        
        for i, sensor_distance in enumerate(sensor_distances):
            sensor_x = self.actual_x - sensor_distance
            sensor_y = 75
            sensor = [
                (sensor_x - 6, sensor_y - 6),
                (sensor_x + 6, sensor_y - 6),
                (sensor_x + 6, sensor_y + 6),
                (sensor_x - 6, sensor_y + 6)
            ]
            traci.polygon.add(f"{self.name}_sensor_{i}", sensor, (255, 165, 0, 200), True, "sensor", 5)
        
        self.sensor_positions = [self.actual_x - d for d in sensor_distances]
    
    def _add_warning_lights(self):
        light_y = self.actual_y - 15
        light_size = 4
        
        light_left = [
            (self.actual_x - 20, light_y - light_size),
            (self.actual_x - 20 + light_size*2, light_y - light_size),
            (self.actual_x - 20 + light_size*2, light_y + light_size),
            (self.actual_x - 20, light_y + light_size)
        ]
        traci.polygon.add(f"{self.name}_light_left", light_left, (80, 80, 80, 255), True, "light", 9)
        
        light_right = [
            (self.actual_x + 20 - light_size*2, light_y - light_size),
            (self.actual_x + 20, light_y - light_size),
            (self.actual_x + 20, light_y + light_size),
            (self.actual_x + 20 - light_size*2, light_y + light_size)
        ]
        traci.polygon.add(f"{self.name}_light_right", light_right, (80, 80, 80, 255), True, "light", 9)
    
    def _add_countdown_timer(self):
        if self.name == "West":
            timer_x = 1800
            timer_y = 125
        else:
            timer_x = 2100
            timer_y = 125
        
        timer_w = 60
        timer_h = 20
        
        timer_bg = [
            (timer_x - timer_w/2, timer_y - timer_h/2),
            (timer_x + timer_w/2, timer_y - timer_h/2),
            (timer_x + timer_w/2, timer_y + timer_h/2),
            (timer_x - timer_w/2, timer_y + timer_h/2)
        ]
        traci.polygon.add(f"{self.name}_timer_bg", timer_bg, (30, 30, 30, 240), True, "display", 12)
        
        for i in range(5):
            digit_w = 8
            digit_h = 12
            x_offset = timer_x - 20 + i * 10
            y_base = timer_y - digit_h/2
            
            digit_shape = [
                (x_offset, y_base),
                (x_offset + digit_w, y_base),
                (x_offset + digit_w, y_base + digit_h),
                (x_offset, y_base + digit_h)
            ]
            traci.polygon.add(f"{self.name}_digit_{i}", digit_shape, (30, 30, 30, 255), True, "digit", 13)
    
    def _add_buildings_and_landscape(self):
        road_sep = 200
        north_y = self.actual_y + road_sep / 2
        south_y = self.actual_y - road_sep / 2
        
        building_data = [
            (self.actual_x - 40, north_y + 15, 25, 35),
            (self.actual_x + 20, north_y + 12, 28, 40),
            (self.actual_x - 45, south_y - 70, 30, 38),
            (self.actual_x + 25, south_y - 65, 26, 36),
        ]
        
        for i, (x, y, w, h) in enumerate(building_data):
            wall_color = (170 + i*10, 150 + i*5, 130, 255)
            
            building = [
                (x, y),
                (x + w, y),
                (x + w, y + h),
                (x, y + h)
            ]
            traci.polygon.add(f"{self.name}_building_{i}", building, wall_color, True, "building", 2)
            
            for row in range(3):
                for col in range(2):
                    win_x = x + 5 + col * 12
                    win_y = y + 8 + row * 10
                    window = [
                        (win_x, win_y),
                        (win_x + 6, win_y),
                        (win_x + 6, win_y + 6),
                        (win_x, win_y + 6)
                    ]
                    traci.polygon.add(f"{self.name}_window_{i}_{row}_{col}", window, (135, 206, 235, 255), True, "window", 3)
            
            roof = [
                (x - 2, y + h),
                (x + w/2, y + h + 8),
                (x + w + 2, y + h)
            ]
            traci.polygon.add(f"{self.name}_roof_{i}", roof, (139, 69, 19, 255), True, "roof", 3)
        
        tree_positions = [
            (self.actual_x - 15, north_y + 12),
            (self.actual_x + 50, north_y + 18),
            (self.actual_x - 20, south_y - 85),
            (self.actual_x + 55, south_y - 90),
            (self.actual_x - 60, north_y + 25),
            (self.actual_x + 10, south_y - 75),
        ]
        
        for i, (x, y) in enumerate(tree_positions):
            trunk = [
                (x - 2, y),
                (x + 2, y),
                (x + 2, y + 10),
                (x - 2, y + 10)
            ]
            traci.polygon.add(f"{self.name}_trunk_{i}", trunk, (101, 67, 33, 255), True, "trunk", 3)
            
            r = 7
            foliage = [
                (x, y + 10 + r),
                (x + r * 0.95, y + 10 + r * 0.31),
                (x + r * 0.59, y + 10 - r * 0.81),
                (x - r * 0.59, y + 10 - r * 0.81),
                (x - r * 0.95, y + 10 + r * 0.31)
            ]
            traci.polygon.add(f"{self.name}_foliage_{i}", foliage, (34, 139, 34, 255), True, "foliage", 4)
    
    def update_visuals(self):
        gate_color = (200, 0, 0, 255) if self.gate_closed else (0, 200, 0, 255)
        traci.polygon.setColor(f"{self.name}_gate_n", gate_color)
        traci.polygon.setColor(f"{self.name}_gate_s", gate_color)
        
        sensor_color = (255, 0, 0, 255) if self.trains else (255, 165, 0, 200)
        for i in range(3):
            traci.polygon.setColor(f"{self.name}_sensor_{i}", sensor_color)
        
        if self.warning_active and not self.gate_closed:
            light_color = (255, 200, 0, 255)
        elif self.gate_closed:
            light_color = (200, 0, 0, 255)
        else:
            light_color = (80, 80, 80, 255)
        
        traci.polygon.setColor(f"{self.name}_light_left", light_color)
        traci.polygon.setColor(f"{self.name}_light_right", light_color)
        
        if self.trains and abs(self.countdown) > 0.1:
            countdown_val = max(0, int(abs(self.countdown)))
            time_str = f"{countdown_val:02d}"
            
            digit_color = (255, 50, 50, 255) if self.gate_closed else (50, 255, 50, 255)
            
            for i in range(5):
                if i == 2:
                    traci.polygon.setColor(f"{self.name}_digit_{i}", (200, 200, 0, 255))
                elif i < 2:
                    digit_idx = i
                    if digit_idx < len(time_str):
                        digit_val = int(time_str[digit_idx])
                        brightness = 150 + (digit_val * 10)
                        if self.gate_closed:
                            color = (brightness, 50, 50, 255)
                        else:
                            color = (50, brightness, 50, 255)
                        traci.polygon.setColor(f"{self.name}_digit_{i}", color)
                    else:
                        traci.polygon.setColor(f"{self.name}_digit_{i}", digit_color)
                else:
                    traci.polygon.setColor(f"{self.name}_digit_{i}", digit_color)
        else:
            for i in range(5):
                traci.polygon.setColor(f"{self.name}_digit_{i}", (30, 30, 30, 255))


class SimulationController:
    def __init__(self, config_path='simulation/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        cross_dist = self.config['network']['crossing_distance']
        
        self.west = RailroadCrossing("West", -cross_dist/2, self.config['crossings']['west'])
        self.east = RailroadCrossing("East", cross_dist/2, self.config['crossings']['east'])
        
        self.metrics = MetricsTracker(self.config)
        
        self.reroute_decisions = {}
        
        self.reroute_threshold = self.config['rerouting']['min_time_saved']
        self.decision_distance = self.config['rerouting']['decision_point']
        
        # Track gate states for detecting open events
        self.last_west_closed = False
        self.last_east_closed = False
    
    def run(self, gui=False):
        duration = self.config['simulation']['duration']
        Logger.section(f"Starting simulation ({duration}s)")
        
        cmd = ['sumo-gui' if gui else 'sumo', '-c', 'simulation.sumocfg', '--start', '--quit-on-end', '--delay', '0']
        traci.start(cmd)
        
        self.west.setup_visuals()
        self.east.setup_visuals()
        
        try:
            step = 0
            dt = self.config['simulation']['step_size']
            max_steps = int(duration / dt)
            
            while traci.simulation.getMinExpectedNumber() > 0 and step < max_steps:
                traci.simulationStep()
                t = traci.simulation.getTime()
                
                self._process_trains(t)
                self._control_crossings(t)
                self._track_vehicles(t, dt)
                self._handle_rerouting(t)
                self._collect_metrics(t, dt)
                
                step += 1
                
                if step % 600 == 0:
                    Logger.log(f"T={t:.0f}s | West: {'CLOSED' if self.west.gate_closed else 'OPEN'} | "
                             f"East: {'CLOSED' if self.east.gate_closed else 'OPEN'}")
        
        except KeyboardInterrupt:
            Logger.log("Stopped by user")
        
        finally:
            traci.close()
            self.metrics.finalize_and_save()
    
    def _process_trains(self, t):
        for vid in traci.vehicle.getIDList():
            if 'train' not in vid.lower():
                continue
            
            x, _ = traci.vehicle.getPosition(vid)
            speed = traci.vehicle.getSpeed(vid)
            
            self.west.detect_train(vid, x, speed, t)
            self.east.detect_train(vid, x, speed, t)
    
    def _control_crossings(self, t):
        self.west.update(t)
        self.east.update(t)
        self.west.update_visuals()
        self.east.update_visuals()
    
    def _track_vehicles(self, t, dt):
        """Track vehicles waiting at traffic lights near crossings"""
        
        # Only track when gate just opened (transition from closed to open)
        if self.last_west_closed and not self.west.gate_closed:
            # Gate just opened - count how many were waiting
            total_waiting = 0
            for tl_id in self.west.get_traffic_light_ids():
                try:
                    # Get number of vehicles waiting at this traffic light
                    # Sum across all lanes at this junction
                    lanes = traci.trafficlight.getControlledLanes(tl_id)
                    for lane in lanes:
                        total_waiting += traci.lane.getLastStepHaltingNumber(lane)
                except:
                    pass
            
            if total_waiting > 0:
                # Calculate how long gate was closed
                gate_closed_duration = t - self.west.gate_close_time if hasattr(self.west, 'gate_close_time') else 10.0
                avg_wait = gate_closed_duration * 0.6  # Assume average car waited 60% of closure time
                
                Logger.log(f"{self.west.name}: {total_waiting} vehicles waited (avg {avg_wait:.1f}s)")
                
                # Record wait events
                for i in range(total_waiting):
                    vid = f"vehicle_west_{int(t)}_{i}"
                    if avg_wait >= self.metrics.min_wait_to_shutoff:
                        engine_off = avg_wait - self.metrics.min_wait_to_shutoff
                    else:
                        engine_off = 0
                    self.metrics.record_wait_event(vid, 'west', avg_wait, engine_off, t)
        
        if self.last_east_closed and not self.east.gate_closed:
            total_waiting = 0
            for tl_id in self.east.get_traffic_light_ids():
                try:
                    lanes = traci.trafficlight.getControlledLanes(tl_id)
                    for lane in lanes:
                        total_waiting += traci.lane.getLastStepHaltingNumber(lane)
                except:
                    pass
            
            if total_waiting > 0:
                gate_closed_duration = t - self.east.gate_close_time if hasattr(self.east, 'gate_close_time') else 10.0
                avg_wait = gate_closed_duration * 0.6
                
                Logger.log(f"{self.east.name}: {total_waiting} vehicles waited (avg {avg_wait:.1f}s)")
                
                for i in range(total_waiting):
                    vid = f"vehicle_east_{int(t)}_{i}"
                    if avg_wait >= self.metrics.min_wait_to_shutoff:
                        engine_off = avg_wait - self.metrics.min_wait_to_shutoff
                    else:
                        engine_off = 0
                    self.metrics.record_wait_event(vid, 'east', avg_wait, engine_off, t)
        
        # Track when gates close to calculate duration
        if not self.last_west_closed and self.west.gate_closed:
            self.west.gate_close_time = t
        
        if not self.last_east_closed and self.east.gate_closed:
            self.east.gate_close_time = t
        
        # Update state for next iteration
        self.last_west_closed = self.west.gate_closed
        self.last_east_closed = self.east.gate_closed
    
    def _handle_rerouting(self, t):
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower() or vid in self.reroute_decisions:
                continue
            
            try:
                x, _ = traci.vehicle.getPosition(vid)
                route = traci.vehicle.getRoute(vid)
                
                crossing = None
                if abs(x - self.west.actual_x) < self.decision_distance and self.west.warning_active:
                    if any('v_w' in edge for edge in route):
                        crossing = 'west'
                elif abs(x - self.east.actual_x) < self.decision_distance and self.east.warning_active:
                    if any('v_e' in edge for edge in route):
                        crossing = 'east'
                
                if crossing:
                    should_reroute, time_saved = self._evaluate_reroute(t, crossing, x)
                    self.reroute_decisions[vid] = True
                    
                    if should_reroute:
                        self._reroute_vehicle(vid, crossing, route)
                        self.metrics.record_reroute(vid, crossing, time_saved, t)
                        Logger.log(f"Vehicle {vid} rerouted from {crossing} (saves {time_saved:.1f}s)")
            except:
                continue
    
    def _reroute_vehicle(self, vid, from_crossing, current_route):
        try:
            if from_crossing == 'west':
                if 'v_w_n_s' in current_route:
                    new_route = ['n_w_e', 'v_e_n_s', 'v_e_x_s'] + [e for e in current_route if 's_' in e]
                elif 'v_w_s_n' in current_route:
                    new_route = ['s_w_e', 'v_e_s_n', 'v_e_x_n'] + [e for e in current_route if 'n_' in e]
                else:
                    return
            else:
                if 'v_e_n_s' in current_route:
                    new_route = ['n_e_w', 'v_w_n_s', 'v_w_x_s'] + [e for e in current_route if 's_' in e]
                elif 'v_e_s_n' in current_route:
                    new_route = ['s_e_w', 'v_w_s_n', 'v_w_x_n'] + [e for e in current_route if 'n_' in e]
                else:
                    return
            
            traci.vehicle.setRoute(vid, new_route)
        except:
            pass
    
    def _evaluate_reroute(self, t, current_crossing, x):
        if current_crossing == 'west':
            wait_here = self.west.get_wait_time(t)
            wait_other = self.east.get_wait_time(t)
            distance = abs(self.east.actual_x - x)
        else:
            wait_here = self.east.get_wait_time(t)
            wait_other = self.west.get_wait_time(t)
            distance = abs(self.west.actual_x - x)
        
        travel_time = distance / 15.0
        time_saved = wait_here - (travel_time + wait_other)
        
        return time_saved > self.reroute_threshold, time_saved
    
    def _collect_metrics(self, t, dt):
        for vid in traci.vehicle.getIDList():
            if 'train' in vid.lower():
                continue
            
            try:
                speed = traci.vehicle.getSpeed(vid)
                waiting = speed < 0.5
                self.metrics.track_fuel(vid, t, dt, waiting)
            except:
                continue


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--gui', action='store_true')
    args = parser.parse_args()
    
    controller = SimulationController()
    controller.run(args.gui)