"""Vehicle simulation using physics module."""

import pygame
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from physics.vehicle import VehiclePhysics, VEHICLE_SPECS


class SimVehicle:
    """Vehicle for pygame simulation with realistic physics."""
    
    def __init__(self, x, y, direction, vehicle_type='car'):
        self.x = x
        self.y = y
        self.direction = direction
        self.vehicle_type = vehicle_type
        
        self.physics = VehiclePhysics(VEHICLE_SPECS[vehicle_type])
        self.speed_kmh = random.uniform(30, 50)
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
        self.route = None
        self.journey_start_time = 0
        self.total_wait_time = 0
        self.wait_start_time = None
        self.engine_off = False
    
    def get_speed_ms(self):
        """Get speed in m/s."""
        return self.speed_kmh / 3.6
    
    def calculate_stopping_distance_meters(self):
        """Calculate stopping distance in meters."""
        return self.physics.calculate_stopping_distance(self.speed_kmh)['total_distance']
    
    def should_brake_for_obstacle(self, distance_meters):
        """Check if should brake for obstacle."""
        stopping_distance = self.calculate_stopping_distance_meters()
        safe_margin = self.physics.calculate_safe_following_distance(self.speed_kmh)
        return distance_meters < (stopping_distance + safe_margin)
    
    def update(self, dt, should_brake=False):
        """Update vehicle physics."""
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
        
        if self.direction == 'east':
            self.x += speed_pixels_per_s * dt
        elif self.direction == 'west':
            self.x -= speed_pixels_per_s * dt
        elif self.direction == 'south':
            self.y += speed_pixels_per_s * dt
        elif self.direction == 'north':
            self.y -= speed_pixels_per_s * dt
    
    def draw(self, surface):
        """Draw vehicle."""
        if self.direction in ['east', 'west']:
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
        """Check if off screen."""
        margin = 100
        return (self.x < -margin or self.x > width + margin or
                self.y < -margin or self.y > height + margin)
    
    def distance_to_point(self, target_x, target_y):
        """Calculate distance to point in direction of travel (pixels)."""
        if self.direction == 'east':
            return target_x - self.x
        elif self.direction == 'west':
            return self.x - target_x
        elif self.direction == 'south':
            return target_y - self.y
        elif self.direction == 'north':
            return self.y - target_y
        return float('inf')


class VehicleManager:
    """Manage all vehicles in simulation."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.vehicles = []
        self.spawn_timer = 0
        self.spawn_interval = 3.0
        self.closed_gates = []
        self.scale = 10
    
    def set_closed_gates(self, gate_positions):
        """Update closed gate positions."""
        self.closed_gates = gate_positions
    
    def spawn_vehicle(self):
        """Spawn new vehicle at random entry point."""
        spawn_points = [
            (0, self.screen_height // 2 - 350, 'east'),
            (self.screen_width, self.screen_height // 2 - 350, 'west'),
            (self.screen_width // 2 - 500, 0, 'south'),
            (self.screen_width // 2 - 500, self.screen_height, 'north'),
        ]
        
        x, y, direction = random.choice(spawn_points)
        vehicle_type = random.choice(['car', 'car', 'car', 'suv', 'truck'])
        
        vehicle = SimVehicle(x, y, direction, vehicle_type)
        vehicle.journey_start_time = pygame.time.get_ticks() / 1000.0
        self.vehicles.append(vehicle)
    
    def check_obstacle_ahead(self, vehicle):
        """Check for obstacles ahead of vehicle."""
        min_distance_pixels = float('inf')
        has_obstacle = False
        
        for gate_pos in self.closed_gates:
            gate_x, gate_y = gate_pos['x'], gate_pos['y']
            distance_pixels = vehicle.distance_to_point(gate_x, gate_y)
            
            if 0 < distance_pixels < 2000:
                has_obstacle = True
                min_distance_pixels = min(min_distance_pixels, distance_pixels)
        
        for other in self.vehicles:
            if other is vehicle or other.direction != vehicle.direction:
                continue
            
            if abs((other.y if vehicle.direction in ['east', 'west'] else other.x) -
                   (vehicle.y if vehicle.direction in ['east', 'west'] else vehicle.x)) > 30:
                continue
            
            distance_pixels = vehicle.distance_to_point(other.x, other.y)
            
            if 0 < distance_pixels < min_distance_pixels:
                has_obstacle = True
                min_distance_pixels = distance_pixels
        
        distance_meters = min_distance_pixels / self.scale
        return has_obstacle, distance_meters
    
    def update(self, dt):
        """Update all vehicles."""
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_vehicle()
            self.spawn_timer = 0
        
        for vehicle in self.vehicles:
            has_obstacle, distance = self.check_obstacle_ahead(vehicle)
            should_brake = has_obstacle and vehicle.should_brake_for_obstacle(distance)
            vehicle.update(dt, should_brake)
        
        self.vehicles = [v for v in self.vehicles if not v.is_off_screen(
            self.screen_width, self.screen_height
        )]
    
    def draw(self, surface):
        """Draw all vehicles."""
        for vehicle in self.vehicles:
            vehicle.draw(surface)
    
    def get_journey_data(self):
        """Get journey data for metrics calculation."""
        data = []
        current_time = pygame.time.get_ticks() / 1000.0
        
        for vehicle in self.vehicles:
            if vehicle.is_off_screen(self.screen_width, self.screen_height):
                total_time = current_time - vehicle.journey_start_time
                driving_time = total_time - vehicle.total_wait_time
                
                data.append({
                    'vehicle_id': id(vehicle),
                    'vehicle_type': vehicle.vehicle_type,
                    'total_travel_time': total_time,
                    'driving_time': driving_time,
                    'waiting_time': vehicle.total_wait_time,
                    'system_active': len(self.closed_gates) > 0,
                    'action_taken': 'wait',
                    'knew_wait_time': False,
                    'reroute_distance': 0,
                    'engine_off_time': 0
                })
        
        return data