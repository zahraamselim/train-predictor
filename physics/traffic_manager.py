"""Traffic management with spawning and routing logic."""

import random
from typing import List, Dict, Tuple, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from physics.vehicle import VehiclePhysics, VEHICLE_SPECS, RouteDecision, VehicleQueue
from config.utils import load_config


class Vehicle:
    def __init__(self, vehicle_id: int, start_node: str, end_node: str, 
                 vehicle_type: str, spawn_time: float):
        self.id = vehicle_id
        self.start_node = start_node
        self.end_node = end_node
        self.vehicle_type = vehicle_type
        self.spawn_time = spawn_time
        
        self.physics = VehiclePhysics(VEHICLE_SPECS[vehicle_type])
        self.speed_kmh = random.uniform(40, min(60, self.physics.spec.max_speed))
        
        self.x = 0.0
        self.y = 0.0
        self.current_route = []
        self.current_route_index = 0
        self.direction = None
        
        self.waiting = False
        self.wait_start_time = None
        self.total_wait_time = 0.0
        self.engine_off = False
        self.engine_off_time = 0.0
        self.engine_off_start = None
        
        self.completed = False
        self.decision_made = None
        self.time_saved = 0.0
        self.color_override = None
    
    def get_speed_ms(self) -> float:
        return self.speed_kmh / 3.6
    
    def set_position(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def set_route(self, route: List[str], initial_direction: str):
        self.current_route = route
        self.current_route_index = 0
        self.direction = initial_direction
    
    def get_next_waypoint(self) -> Optional[str]:
        if self.current_route_index < len(self.current_route):
            return self.current_route[self.current_route_index]
        return None
    
    def advance_waypoint(self):
        self.current_route_index += 1
    
    def start_waiting(self, current_time: float):
        if not self.waiting:
            self.waiting = True
            self.wait_start_time = current_time
    
    def stop_waiting(self, current_time: float):
        if self.waiting and self.wait_start_time is not None:
            self.total_wait_time += current_time - self.wait_start_time
            self.waiting = False
            self.wait_start_time = None
    
    def turn_engine_off(self, current_time: float):
        if not self.engine_off:
            self.engine_off = True
            self.engine_off_start = current_time
    
    def turn_engine_on(self, current_time: float):
        if self.engine_off and self.engine_off_start is not None:
            self.engine_off_time += current_time - self.engine_off_start
            self.engine_off = False
            self.engine_off_start = None
    
    def get_journey_data(self, current_time: float) -> Dict:
        total_time = current_time - self.spawn_time
        driving_time = total_time - self.total_wait_time
        
        return {
            'vehicle_id': self.id,
            'vehicle_type': self.vehicle_type,
            'total_travel_time': total_time,
            'driving_time': max(0, driving_time),
            'waiting_time': self.total_wait_time,
            'system_active': self.decision_made is not None,
            'action_taken': self.decision_made if self.decision_made else 'none',
            'knew_wait_time': self.decision_made == 'wait',
            'reroute_distance': 0,
            'engine_off_time': self.engine_off_time
        }


class TrafficManager:
    def __init__(self, map_config: Dict):
        self.config = load_config()
        self.map_config = map_config
        
        self.vehicles = []
        self.next_vehicle_id = 0
        self.current_time = 0.0
        
        self.traffic_density = 'medium'
        self.spawn_timer = 0.0
        
        self.queues = {}
        self._initialize_queues()
        
        self.completed_journeys = []
    
    def _initialize_queues(self):
        crossings = self.map_config.get('crossings', [])
        for crossing in crossings:
            for direction in ['north', 'south']:
                queue_id = f"{crossing['name']}_{direction}"
                self.queues[queue_id] = VehicleQueue(
                    (crossing['x'], crossing['y']), 
                    direction
                )
    
    def set_traffic_density(self, density: str):
        if density in ['light', 'medium', 'heavy']:
            self.traffic_density = density
    
    def get_spawn_interval(self) -> float:
        intervals = self.config['simulation']['spawn_interval']
        return intervals.get(self.traffic_density, 2.0)
    
    def get_spawn_nodes(self) -> List[str]:
        return ['top_left', 'top_right', 'right_top', 'right_bottom']
    
    def get_destination_nodes(self) -> List[str]:
        return ['bottom_left', 'bottom_right', 'left_top', 'left_bottom']
    
    def generate_route(self, start_node: str, end_node: str) -> List[str]:
        route_map = {
            ('top_left', 'bottom_left'): ['top_left', 'inter_tl', 'inter_bl', 'cross_left', 'bottom_left'],
            ('top_left', 'bottom_right'): ['top_left', 'inter_tl', 'inter_tr', 'inter_br', 'cross_right', 'bottom_right'],
            ('top_left', 'left_top'): ['top_left', 'inter_tl', 'left_top'],
            ('top_left', 'left_bottom'): ['top_left', 'inter_tl', 'inter_bl', 'left_bottom'],
            
            ('top_right', 'bottom_right'): ['top_right', 'inter_tr', 'inter_br', 'cross_right', 'bottom_right'],
            ('top_right', 'bottom_left'): ['top_right', 'inter_tr', 'inter_tl', 'inter_bl', 'cross_left', 'bottom_left'],
            ('top_right', 'left_top'): ['top_right', 'inter_tr', 'inter_tl', 'left_top'],
            ('top_right', 'left_bottom'): ['top_right', 'inter_tr', 'inter_br', 'inter_bl', 'left_bottom'],
            
            ('right_top', 'bottom_right'): ['right_top', 'inter_tr', 'inter_br', 'cross_right', 'bottom_right'],
            ('right_top', 'bottom_left'): ['right_top', 'inter_tr', 'inter_br', 'inter_bl', 'cross_left', 'bottom_left'],
            ('right_top', 'left_top'): ['right_top', 'inter_tr', 'inter_tl', 'left_top'],
            ('right_top', 'left_bottom'): ['right_top', 'inter_tr', 'inter_tl', 'inter_bl', 'left_bottom'],
            
            ('right_bottom', 'bottom_right'): ['right_bottom', 'inter_br', 'cross_right', 'bottom_right'],
            ('right_bottom', 'bottom_left'): ['right_bottom', 'inter_br', 'inter_bl', 'cross_left', 'bottom_left'],
            ('right_bottom', 'left_top'): ['right_bottom', 'inter_br', 'inter_tr', 'inter_tl', 'left_top'],
            ('right_bottom', 'left_bottom'): ['right_bottom', 'inter_br', 'inter_bl', 'left_bottom'],
        }
        
        return route_map.get((start_node, end_node), [start_node, end_node])
    
    def calculate_alternative_route(self, start_node: str, end_node: str, blocked_crossing: str) -> List[str]:
        all_routes = {
            ('inter_tl', 'bottom_left', 'cross_left'): ['inter_tl', 'inter_tr', 'inter_br', 'inter_bl', 'cross_left', 'bottom_left'],
            ('inter_tl', 'bottom_right', 'cross_right'): ['inter_tl', 'inter_bl', 'cross_left', 'bottom_left'],
            ('inter_tr', 'bottom_right', 'cross_right'): ['inter_tr', 'inter_tl', 'inter_bl', 'cross_left', 'bottom_left'],
            ('inter_tr', 'bottom_left', 'cross_left'): ['inter_tr', 'inter_br', 'cross_right', 'bottom_right'],
        }
        
        key = (start_node, end_node, blocked_crossing)
        return all_routes.get(key, self.generate_route(start_node, end_node))
    
    def spawn_vehicle(self):
        if len(self.vehicles) >= self.config['simulation']['max_vehicles']:
            return
        
        spawn_nodes = self.get_spawn_nodes()
        dest_nodes = self.get_destination_nodes()
        
        start_node = random.choice(spawn_nodes)
        end_node = random.choice(dest_nodes)
        
        vehicle_type = random.choices(
            ['car', 'suv', 'truck', 'motorcycle'],
            weights=[0.60, 0.25, 0.10, 0.05]
        )[0]
        
        vehicle = Vehicle(
            self.next_vehicle_id,
            start_node,
            end_node,
            vehicle_type,
            self.current_time
        )
        self.next_vehicle_id += 1
        
        route = self.generate_route(start_node, end_node)
        initial_direction = self._get_initial_direction(start_node)
        vehicle.set_route(route, initial_direction)
        
        self.vehicles.append(vehicle)
    
    def _get_initial_direction(self, start_node: str) -> str:
        if 'top' in start_node:
            return 'south'
        elif 'right' in start_node:
            return 'west'
        return 'south'
    
    def update(self, dt: float):
        self.current_time += dt
        self.spawn_timer += dt
        
        if self.spawn_timer >= self.get_spawn_interval():
            self.spawn_vehicle()
            self.spawn_timer = 0.0
        
        config = self.config
        engine_off_delay = config['fuel_rates']['engine_off_delay']
        
        for vehicle in self.vehicles:
            if vehicle.waiting:
                wait_duration = self.current_time - vehicle.wait_start_time
                
                if not vehicle.engine_off and wait_duration >= engine_off_delay:
                    vehicle.turn_engine_off(self.current_time)
            else:
                if vehicle.engine_off:
                    vehicle.turn_engine_on(self.current_time)
    
    def remove_completed_vehicle(self, vehicle: Vehicle):
        journey_data = vehicle.get_journey_data(self.current_time)
        self.completed_journeys.append(journey_data)
        self.vehicles.remove(vehicle)
    
    def get_completed_journeys(self) -> List[Dict]:
        completed = self.completed_journeys.copy()
        self.completed_journeys = []
        return completed
    
    def get_queue_length(self, crossing_id: str, direction: str) -> int:
        queue_id = f"{crossing_id}_{direction}"
        if queue_id in self.queues:
            return self.queues[queue_id].get_queue_length()
        return 0
    
    def add_to_queue(self, crossing_id: str, direction: str, vehicle: Vehicle):
        queue_id = f"{crossing_id}_{direction}"
        if queue_id in self.queues:
            self.queues[queue_id].add_vehicle(vehicle.id, (vehicle.x, vehicle.y))
    
    def remove_from_queue(self, crossing_id: str, direction: str, vehicle: Vehicle):
        queue_id = f"{crossing_id}_{direction}"
        if queue_id in self.queues:
            self.queues[queue_id].remove_vehicle(vehicle.id)
    
    def clear_queue(self, crossing_id: str, direction: str):
        queue_id = f"{crossing_id}_{direction}"
        if queue_id in self.queues:
            self.queues[queue_id].clear()
    
    def make_routing_decision(self, vehicle: Vehicle, train_eta: float, 
                             queue_length: int, crossing_id: str) -> str:
        """Use physics-based logic to decide wait vs reroute."""
        
        config = self.config['train']['simulation_scale']
        intersection_distance = config['intersection_distances'][1]
        alternative_distance = intersection_distance * 2.0
        
        gate_closure_offset = self.config['gates']['closure_before_eta']
        
        route_decision = RouteDecision(
            (vehicle.x, vehicle.y),
            (0, 0),
            (0, 0),
            alternative_distance
        )
        
        decision, time_saved = route_decision.should_wait_or_reroute(
            train_eta, queue_length, self.traffic_density,
            vehicle.get_speed_ms(), gate_closure_offset
        )
        
        vehicle.time_saved = time_saved
        
        if decision == 'wait':
            vehicle.color_override = (255, 150, 150)
        else:
            vehicle.color_override = (150, 255, 150)
        
        return decision