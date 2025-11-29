import pygame
import random
import sys
import os

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
    def __init__(self, x, y, direction, vehicle_type='car'):
        self.x = x
        self.y = y
        self.direction = direction
        self.vehicle_type = vehicle_type
        self.physics = VehiclePhysics(VEHICLE_TYPES[vehicle_type])
        
        scale_factor_speed = 0.15
        initial_speed_kmh = random.uniform(30, 50)
        self.speed = initial_speed_kmh * scale_factor_speed
        self.max_speed = self.physics.vehicle.max_speed * scale_factor_speed
        self.acceleration = self.physics.vehicle.max_accel * scale_factor_speed * 0.5
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
    
    def check_collision_ahead(self, other_vehicles):
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
                return True, distance
        
        return False, float('inf')
    
    def update(self, dt, other_vehicles):
        collision_ahead, distance = self.check_collision_ahead(other_vehicles)
        
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
            vehicle = Vehicle(x, y, direction, vehicle_type)
            self.vehicles.append(vehicle)
    
    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_vehicle()
            self.spawn_timer = 0
        
        for vehicle in self.vehicles[:]:
            vehicle.update(dt, self.vehicles)
            if vehicle.is_off_screen(self.map_width, self.map_height):
                self.vehicles.remove(vehicle)
    
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