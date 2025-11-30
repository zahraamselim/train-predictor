"""Vehicle simulation with proper traffic rules and turning."""

import pygame
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from physics.vehicle import VehiclePhysics, VEHICLE_SPECS


class SimVehicle:
    """Vehicle with realistic physics and traffic rules."""
    
    def __init__(self, x, y, direction, vehicle_type='car'):
        self.x = x
        self.y = y
        self.direction = direction
        self.vehicle_type = vehicle_type
        
        self.physics = VehiclePhysics(VEHICLE_SPECS[vehicle_type])
        self.speed_kmh = random.uniform(40, 60)
        self.target_speed = self.speed_kmh
        
        self.scale = 10
        self.width = int(self.physics.spec.length * self.scale)
        self.height = int(self.width * 0.6)
        
        self.colors = {
            'car': (180, 50, 50),
            'suv': (50, 100, 180),
            'truck': (100, 100, 100),
            'motorcycle': (200, 150, 50)
        }
        self.color = self.colors.get(vehicle_type, self.colors['car'])
        
        self.stopped = False
        self.journey_start_time = pygame.time.get_ticks() / 1000.0
        self.total_wait_time = 0
        self.wait_start_time = None
        self.completed = False
        self.turned_at_intersections = []
    
    def get_speed_ms(self):
        return self.speed_kmh / 3.6
    
    def calculate_stopping_distance_meters(self):
        return self.physics.calculate_stopping_distance(self.speed_kmh)['total_distance']
    
    def should_brake_for_obstacle(self, distance_meters):
        stopping_distance = self.calculate_stopping_distance_meters()
        safe_margin = self.physics.calculate_safe_following_distance(self.speed_kmh)
        return distance_meters < (stopping_distance + safe_margin)
    
    def check_and_execute_turn(self, intersections):
        turn_chance = 0.25
        
        for inter in intersections:
            inter_id = (inter['x'], inter['y'])
            
            if inter_id in self.turned_at_intersections:
                continue
            
            distance = abs(self.x - inter['x']) if self.direction == 'west' else abs(self.y - inter['y'])
            
            if distance < 15:
                if random.random() < turn_chance:
                    if self.direction == 'west':
                        self.direction = 'south'
                        self.x = inter['x']
                        self.y = inter['y']
                    elif self.direction == 'south':
                        self.direction = 'west'
                        self.x = inter['x']
                        self.y = inter['y']
                
                self.turned_at_intersections.append(inter_id)
                break
    
    def update(self, dt, should_brake=False, intersections=None):
        if self.completed:
            return
        
        if intersections:
            self.check_and_execute_turn(intersections)
        
        if should_brake or self.stopped:
            decel_kmh_per_s = self.physics.spec.max_decel * 3.6
            self.speed_kmh = max(0, self.speed_kmh - decel_kmh_per_s * dt)
            
            if self.speed_kmh == 0 and not self.stopped:
                self.stopped = True
                self.wait_start_time = pygame.time.get_ticks() / 1000.0
        else:
            if self.speed_kmh < self.target_speed:
                accel_kmh_per_s = self.physics.spec.max_accel * 3.6
                self.speed_kmh = min(self.target_speed, self.speed_kmh + accel_kmh_per_s * dt)
            
            if self.stopped and self.speed_kmh > 0:
                self.stopped = False
                if self.wait_start_time is not None:
                    current_time = pygame.time.get_ticks() / 1000.0
                    self.total_wait_time += current_time - self.wait_start_time
                    self.wait_start_time = None
        
        speed_pixels_per_s = self.get_speed_ms() * self.scale
        
        if self.direction == 'west':
            self.x -= speed_pixels_per_s * dt
        elif self.direction == 'south':
            self.y += speed_pixels_per_s * dt
    
    def draw(self, surface):
        if self.completed:
            return
        
        if self.direction == 'west':
            rect = pygame.Rect(
                self.x - self.width // 2,
                self.y - self.height // 2,
                self.width,
                self.height
            )
        else:
            rect = pygame.Rect(
                self.x - self.height // 2,
                self.y - self.width // 2,
                self.height,
                self.width
            )
        
        pygame.draw.rect(surface, self.color, rect, border_radius=3)
        darker = tuple(max(0, c - 40) for c in self.color)
        pygame.draw.rect(surface, darker, rect, 2, border_radius=3)
    
    def is_off_screen(self, width, height):
        margin = 100
        return (self.x < -margin or self.x > width + margin or
                self.y < -margin or self.y > height + margin)
    
    def distance_to_point(self, target_x, target_y):
        if self.direction == 'west':
            return self.x - target_x
        elif self.direction == 'south':
            return target_y - self.y
        return float('inf')
    
    def get_journey_data(self):
        current_time = pygame.time.get_ticks() / 1000.0
        total_time = current_time - self.journey_start_time
        driving_time = total_time - self.total_wait_time
        
        return {
            'vehicle_id': id(self),
            'vehicle_type': self.vehicle_type,
            'total_travel_time': total_time,
            'driving_time': driving_time,
            'waiting_time': self.total_wait_time,
            'system_active': self.total_wait_time > 0,
            'action_taken': 'wait' if self.total_wait_time > 0 else 'none',
            'knew_wait_time': self.total_wait_time > 0,
            'reroute_distance': 0,
            'engine_off_time': 0
        }


class VehicleManager:
    """Manage vehicles with proper traffic rules."""
    
    def __init__(self, screen_width, screen_height, road_map):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map = road_map
        self.vehicles = []
        self.spawn_timer = 0
        self.spawn_interval = 2.5
        self.closed_gates = []
        self.scale = 10
        self.completed_count = 0
        self.completed_journeys = []
    
    def set_closed_gates(self, gate_positions):
        self.closed_gates = gate_positions if gate_positions else []
    
    def spawn_vehicle(self):
        spawn_points = self.map.get_spawn_points()
        spawn = random.choice(spawn_points)
        
        vehicle_type = random.choice(['car', 'car', 'car', 'suv', 'truck'])
        
        vehicle = SimVehicle(spawn['x'], spawn['y'], spawn['direction'], vehicle_type)
        self.vehicles.append(vehicle)
    
    def check_obstacle_ahead(self, vehicle):
        min_distance_pixels = float('inf')
        has_obstacle = False
        
        for gate in self.closed_gates:
            gate_x, gate_y = gate['x'], gate['y']
            distance_pixels = vehicle.distance_to_point(gate_x, gate_y)
            
            if 0 < distance_pixels < 2000:
                has_obstacle = True
                min_distance_pixels = min(min_distance_pixels, distance_pixels)
        
        for other in self.vehicles:
            if other is vehicle or other.completed:
                continue
            
            if other.direction != vehicle.direction:
                continue
            
            distance_pixels = vehicle.distance_to_point(other.x, other.y)
            
            if 0 < distance_pixels < min_distance_pixels:
                collision_margin = 50
                if vehicle.direction == 'west':
                    lateral_distance = abs(vehicle.y - other.y)
                else:
                    lateral_distance = abs(vehicle.x - other.x)
                
                if lateral_distance < collision_margin:
                    has_obstacle = True
                    min_distance_pixels = distance_pixels
        
        distance_meters = min_distance_pixels / self.scale
        return has_obstacle, distance_meters
    
    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_vehicle()
            self.spawn_timer = 0
        
        intersections = self.map.get_intersection_positions()
        
        for vehicle in self.vehicles:
            if vehicle.completed:
                continue
            
            has_obstacle, distance = self.check_obstacle_ahead(vehicle)
            should_brake = has_obstacle and vehicle.should_brake_for_obstacle(distance)
            vehicle.update(dt, should_brake, intersections)
            
            if vehicle.is_off_screen(self.screen_width, self.screen_height):
                vehicle.completed = True
                self.completed_count += 1
                self.completed_journeys.append(vehicle.get_journey_data())
        
        self.vehicles = [v for v in self.vehicles if not v.completed or 
                        (pygame.time.get_ticks() / 1000.0 - v.journey_start_time) < 120]
    
    def draw(self, surface):
        for vehicle in self.vehicles:
            vehicle.draw(surface)
    
    def get_completed_journeys(self):
        completed = self.completed_journeys.copy()
        self.completed_journeys = []
        return completed