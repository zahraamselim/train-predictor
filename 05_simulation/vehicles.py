import pygame
import random
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config

try:
    from vehicle_physics import VehiclePhysics
    from vehicle_types import VEHICLE_TYPES
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '02_traffic_parameters'))
    from vehicle_physics import VehiclePhysics
    from vehicle_types import VEHICLE_TYPES


class Vehicle:
    def __init__(self, x, y, direction, vehicle_type='car', target_pos=None):
        self.x = x
        self.y = y
        self.direction = direction
        self.vehicle_type = vehicle_type
        self.physics = VehiclePhysics(VEHICLE_TYPES[vehicle_type])
        
        scale_factor_speed = 0.08
        initial_speed_kmh = random.uniform(30, 50)
        self.speed = initial_speed_kmh * scale_factor_speed
        self.max_speed = self.physics.vehicle.max_speed * scale_factor_speed
        self.acceleration = self.physics.vehicle.max_accel * scale_factor_speed * 0.3
        self.deceleration = self.physics.vehicle.max_decel * scale_factor_speed * 0.8
        self.stopped = False
        self.following_distance = 40
        
        scale_factor = 10
        self.width = int(self.physics.vehicle.length * scale_factor)
        self.height = int(self.width * 0.6)
        
        self.colors = {
            'car': (180, 50, 50),
            'suv': (50, 100, 180),
            'truck': (100, 100, 100),
            'motorcycle': (200, 150, 50)
        }
        self.color = self.colors.get(vehicle_type, self.colors['car'])
        
        self.target_pos = target_pos
        self.route = []
        self.current_route_index = 0
        self.turning = False
        self.turn_progress = 0
        self.turn_start_pos = None
        self.turn_end_pos = None
        self.turn_center = None
        self.turn_start_angle = 0
        self.turn_direction_sign = 1
    
    def stop(self):
        self.stopped = True
    
    def resume(self):
        self.stopped = False
    
    def get_front_position(self):
        if self.direction == 'right':
            return self.x + self.width / 2
        elif self.direction == 'left':
            return self.x - self.width / 2
        elif self.direction == 'down':
            return self.y + self.width / 2
        elif self.direction == 'up':
            return self.y - self.width / 2
        return self.x
    
    def get_lane_position(self):
        if self.direction in ['left', 'right']:
            return self.y
        else:
            return self.x
    
    def should_turn_at_intersection(self, intersection_pos, timers):
        if not self.route or self.current_route_index >= len(self.route):
            return False
        
        next_direction = self.route[self.current_route_index]
        if next_direction == self.direction:
            return False
        
        ix, iy = intersection_pos['x'], intersection_pos['y']
        distance_to_intersection = 0
        
        if self.direction == 'right':
            distance_to_intersection = ix - self.x
        elif self.direction == 'left':
            distance_to_intersection = self.x - ix
        elif self.direction == 'down':
            distance_to_intersection = iy - self.y
        elif self.direction == 'up':
            distance_to_intersection = self.y - iy
        
        in_turn_zone = 5 < distance_to_intersection < 15
        
        if in_turn_zone:
            timer_at_current = self._get_timer_for_direction(intersection_pos, self.direction, timers)
            timer_at_next = self._get_timer_for_direction(intersection_pos, next_direction, timers)
            
            if timer_at_current and timer_at_next:
                wait_if_turn = timer_at_next.time_remaining if timer_at_next.active else 0
                wait_if_straight = timer_at_current.time_remaining if timer_at_current.active else 0
                
                if wait_if_turn <= wait_if_straight:
                    return True
            else:
                return True
        
        return False
    
    def _get_timer_for_direction(self, intersection_pos, direction, timers):
        for timer_info in timers:
            timer_ix = timer_info['intersection']['x']
            timer_iy = timer_info['intersection']['y']
            
            if abs(timer_ix - intersection_pos['x']) < 10 and abs(timer_iy - intersection_pos['y']) < 10:
                if direction in ['right', 'left']:
                    if timer_iy < intersection_pos['y']:
                        return timer_info['timer']
                else:
                    if timer_ix < intersection_pos['x']:
                        return timer_info['timer']
        
        return None
    
    def start_turn(self, intersection_pos, new_direction):
        self.turning = True
        self.turn_progress = 0
        
        ix, iy = intersection_pos['x'], intersection_pos['y']
        turn_radius = 40
        
        self.turn_start_pos = (self.x, self.y)
        
        direction_coords = {
            'right': (1, 0),
            'left': (-1, 0),
            'down': (0, 1),
            'up': (0, -1)
        }
        
        current_dir = direction_coords[self.direction]
        new_dir = direction_coords[new_direction]
        
        cross_product = current_dir[0] * new_dir[1] - current_dir[1] * new_dir[0]
        
        if cross_product > 0:
            self.turn_direction_sign = 1
        else:
            self.turn_direction_sign = -1
        
        if self.direction == 'right':
            if new_direction == 'down':
                self.turn_center = (ix, iy - turn_radius)
                self.turn_start_angle = 90
            else:
                self.turn_center = (ix, iy + turn_radius)
                self.turn_start_angle = 270
        elif self.direction == 'left':
            if new_direction == 'down':
                self.turn_center = (ix, iy + turn_radius)
                self.turn_start_angle = 270
            else:
                self.turn_center = (ix, iy - turn_radius)
                self.turn_start_angle = 90
        elif self.direction == 'down':
            if new_direction == 'right':
                self.turn_center = (ix - turn_radius, iy)
                self.turn_start_angle = 0
            else:
                self.turn_center = (ix + turn_radius, iy)
                self.turn_start_angle = 180
        elif self.direction == 'up':
            if new_direction == 'right':
                self.turn_center = (ix + turn_radius, iy)
                self.turn_start_angle = 180
            else:
                self.turn_center = (ix - turn_radius, iy)
                self.turn_start_angle = 0
        
        self.direction = new_direction
        self.current_route_index += 1
    
    def update_turn(self, dt):
        turn_speed = 1.5
        self.turn_progress += turn_speed * dt
        
        if self.turn_progress >= 1.0:
            self.turning = False
            self.turn_progress = 0
            return
        
        angle_change = 90 * self.turn_progress * self.turn_direction_sign
        current_angle = self.turn_start_angle + angle_change
        
        angle_rad = math.radians(current_angle)
        turn_radius = 40
        
        self.x = self.turn_center[0] + turn_radius * math.cos(angle_rad)
        self.y = self.turn_center[1] + turn_radius * math.sin(angle_rad)
    
    def check_collision_ahead(self, other_vehicles, gates, gate_objects):
        min_distance = float('inf')
        has_collision = False
        
        for gate_pos, gate_obj in zip(gates, gate_objects):
            if not gate_obj.is_closed:
                continue
                
            gate_x, gate_y = gate_pos['x'], gate_pos['y']
            
            if self.direction in ['left', 'right']:
                if abs(self.y - gate_y) < 50:
                    if self.direction == 'right':
                        distance = gate_x - self.get_front_position()
                    else:
                        distance = self.get_front_position() - gate_x
                    
                    if 0 < distance < 150:
                        has_collision = True
                        min_distance = min(min_distance, distance)
            else:
                if abs(self.x - gate_x) < 50:
                    if self.direction == 'down':
                        distance = gate_y - self.get_front_position()
                    else:
                        distance = self.get_front_position() - gate_y
                    
                    if 0 < distance < 150:
                        has_collision = True
                        min_distance = min(min_distance, distance)
        
        for other in other_vehicles:
            if other is self or other.direction != self.direction:
                continue
            
            if abs(self.get_lane_position() - other.get_lane_position()) > 30:
                continue
            
            my_front = self.get_front_position()
            other_back = other.get_front_position()
            
            distance = 0
            if self.direction == 'right':
                distance = other_back - my_front
            elif self.direction == 'left':
                distance = my_front - other_back
            elif self.direction == 'down':
                distance = other_back - my_front
            elif self.direction == 'up':
                distance = my_front - other_back
            
            if 0 < distance < self.following_distance + self.speed * 2:
                has_collision = True
                min_distance = min(min_distance, distance)
        
        return has_collision, min_distance
    
    def update(self, dt, other_vehicles, gates, gate_objects, intersections, timers):
        if self.turning:
            self.update_turn(dt)
            return
        
        for intersection in intersections:
            if self.should_turn_at_intersection(intersection, timers):
                if self.route and self.current_route_index < len(self.route):
                    self.start_turn(intersection, self.route[self.current_route_index])
                    return
        
        collision_ahead, distance = self.check_collision_ahead(other_vehicles, gates, gate_objects)
        
        if self.stopped or collision_ahead:
            self.speed = max(0, self.speed - self.deceleration * dt)
        else:
            if self.speed < self.max_speed:
                self.speed = min(self.max_speed, self.speed + self.acceleration * dt)
        
        if self.direction == 'right':
            self.x += self.speed
        elif self.direction == 'left':
            self.x -= self.speed
        elif self.direction == 'down':
            self.y += self.speed
        elif self.direction == 'up':
            self.y -= self.speed
    
    def draw(self, surface):
        if self.direction in ['left', 'right']:
            rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, 
                             self.width, self.height)
        else:
            rect = pygame.Rect(self.x - self.height // 2, self.y - self.width // 2, 
                             self.height, self.width)
        
        pygame.draw.rect(surface, self.color, rect, border_radius=3)
        
        darker = tuple(max(0, c - 40) for c in self.color)
        pygame.draw.rect(surface, darker, rect, 2, border_radius=3)
        
        window_color = (100, 150, 200)
        if self.direction in ['left', 'right']:
            window_rect = pygame.Rect(
                rect.centerx - self.width // 4,
                rect.centery - self.height // 4,
                self.width // 2,
                self.height // 2
            )
        else:
            window_rect = pygame.Rect(
                rect.centerx - self.height // 4,
                rect.centery - self.width // 4,
                self.height // 2,
                self.width // 2
            )
        pygame.draw.rect(surface, window_color, window_rect)
    
    def is_off_screen(self, width, height):
        return self.x < -100 or self.x > width + 100 or self.y < -100 or self.y > height + 100
    
    def get_position(self):
        return (self.x, self.y)


class VehicleManager:
    def __init__(self, map_width, map_height, road_bounds, railway_bounds):
        self.map_width = map_width
        self.map_height = map_height
        self.road_bounds = road_bounds
        self.railway_bounds = railway_bounds
        
        self.vehicles = []
        self.spawn_timer = 0
        self.spawn_interval = 3.0
        self.min_spawn_distance = 100
        
        self.vehicle_types = ['car', 'suv', 'truck', 'motorcycle']
        self.type_probabilities = [0.6, 0.25, 0.1, 0.05]
        
        self.closed_gates = []
        self.gate_objects = []
        self.intersections = []
        self.timers = []
    
    def set_intersections(self, intersections):
        self.intersections = intersections
    
    def set_timers(self, timers):
        self.timers = timers
    
    def set_gate_objects(self, gate_objects):
        self.gate_objects = gate_objects
    
    def _generate_route(self, start_direction):
        route = [start_direction]
        
        num_turns = random.choice([0, 1, 1, 2])
        
        for _ in range(num_turns):
            current = route[-1]
            
            if current in ['right', 'left']:
                next_dir = random.choice(['down', 'up'])
            else:
                next_dir = random.choice(['right', 'left'])
            
            route.append(next_dir)
        
        return route
    
    def can_spawn_at(self, x, y, direction):
        for vehicle in self.vehicles:
            if vehicle.direction != direction:
                continue
            
            distance = 0
            if direction in ['left', 'right']:
                if abs(vehicle.y - y) < 30:
                    distance = abs(vehicle.x - x)
            else:
                if abs(vehicle.x - x) < 30:
                    distance = abs(vehicle.y - y)
            
            if distance < self.min_spawn_distance:
                return False
        
        return True
    
    def spawn_vehicle(self):
        vehicle_type = random.choices(self.vehicle_types, self.type_probabilities)[0]
        
        roads = [
            ('top_horizontal', 'left', self.map_width, self.road_bounds['top_road']['y']),
            ('bottom_horizontal', 'left', self.map_width, self.road_bounds['bottom_road']['y']),
            ('left_vertical', 'down', self.road_bounds['left_road']['x'], 0),
            ('right_vertical', 'down', self.road_bounds['right_road']['x'], 0)
        ]
        
        road_name, direction, x, y = random.choice(roads)
        
        if self.can_spawn_at(x, y, direction):
            route = self._generate_route(direction)
            vehicle = Vehicle(x, y, direction, vehicle_type)
            vehicle.route = route
            self.vehicles.append(vehicle)
    
    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_vehicle()
            self.spawn_timer = 0
        
        for vehicle in self.vehicles[:]:
            vehicle.update(dt, self.vehicles, self.closed_gates, self.gate_objects, self.intersections, self.timers)
            if vehicle.is_off_screen(self.map_width, self.map_height):
                self.vehicles.remove(vehicle)
    
    def set_closed_gates(self, gate_positions):
        self.closed_gates = gate_positions
    
    def draw(self, surface):
        for vehicle in self.vehicles:
            vehicle.draw(surface)
    
    def stop_all_vehicles(self):
        for vehicle in self.vehicles:
            vehicle.stop()
    
    def resume_all_vehicles(self):
        for vehicle in self.vehicles:
            vehicle.resume()
    
    def get_vehicle_count(self):
        return len(self.vehicles)