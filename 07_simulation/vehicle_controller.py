"""
Vehicle controller for pygame simulation using traffic module physics.

This ensures the same physics equations used for data generation are used
in the real-time simulation, maintaining consistency.
"""

import pygame
import random
import math
import sys
import os

# Import traffic module physics
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _traffic import VehiclePhysics, VEHICLE_TYPES, VehicleRouter


class SimulatedVehicle:
    """
    Vehicle for pygame simulation using real physics from traffic module.
    
    Key Difference from Old Implementation:
        - Uses VehiclePhysics for acceleration/braking
        - Uses VehicleRouter for navigation decisions
        - Maintains safe following distances
        - Realistic queuing behavior
    """
    
    def __init__(self, x, y, direction, vehicle_type='car', road_network=None):
        """
        Initialize vehicle with physics engine.
        
        Args:
            x, y: Starting position (pixels)
            direction: 'north', 'south', 'east', 'west'
            vehicle_type: One of ['car', 'suv', 'truck', 'motorcycle']
            road_network: Road network dict for routing
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.vehicle_type = vehicle_type
        
        # Import physics from traffic module
        self.physics = VehiclePhysics(VEHICLE_TYPES[vehicle_type])
        
        # Speed in km/h (will be converted in physics calculations)
        self.speed = random.uniform(30, 50)  # km/h
        self.target_speed = self.speed
        
        # Visual properties (scale for display)
        scale_factor = 10  # pixels per meter
        self.width = int(self.physics.vehicle.length * scale_factor)
        self.height = int(self.width * 0.6)
        
        # Colors
        self.colors = {
            'car': (180, 50, 50),
            'suv': (50, 100, 180),
            'truck': (100, 100, 100),
            'motorcycle': (200, 150, 50)
        }
        self.color = self.colors.get(vehicle_type, self.colors['car'])
        
        # Routing
        if road_network:
            self.router = VehicleRouter(road_network)
            self.route = self.router.generate_random_route(
                start_pos=(x, y),
                start_direction=direction,
                min_turns=0,
                max_turns=2
            )
            self.current_route_index = 0
        else:
            self.router = None
            self.route = None
            self.current_route_index = 0
        
        # State
        self.stopped = False
        self.turning = False
        self.turn_progress = 0.0
    
    def get_speed_ms(self):
        """Get current speed in m/s for physics calculations."""
        return self.speed / 3.6
    
    def calculate_stopping_distance(self):
        """Calculate how far ahead vehicle needs to stop."""
        result = self.physics.calculate_stopping_distance(self.speed)
        return result['total_distance']  # meters
    
    def calculate_safe_following_distance(self):
        """Calculate safe distance to maintain behind other vehicles."""
        return self.physics.calculate_safe_following_distance(
            self.speed,
            time_headway=2.0  # 2-second rule
        )
    
    def should_brake_for_obstacle(self, distance_to_obstacle):
        """
        Determine if vehicle should brake for obstacle ahead.
        
        Args:
            distance_to_obstacle: Distance to obstacle in meters
        
        Returns:
            True if should brake, False otherwise
        """
        stopping_distance = self.calculate_stopping_distance()
        safe_following = self.calculate_safe_following_distance()
        
        # Brake if obstacle within stopping distance + safe margin
        return distance_to_obstacle < (stopping_distance + safe_following)
    
    def update_speed(self, dt, should_brake=False):
        """
        Update vehicle speed based on conditions.
        
        Args:
            dt: Time delta in seconds
            should_brake: Whether vehicle needs to brake
        """
        if self.stopped or should_brake:
            # Decelerate using physics max_decel
            decel_kmh_per_s = self.physics.vehicle.max_decel * 3.6
            self.speed = max(0, self.speed - decel_kmh_per_s * dt)
        else:
            # Accelerate toward target speed
            if self.speed < self.target_speed:
                accel_kmh_per_s = self.physics.vehicle.max_accel * 3.6
                self.speed = min(
                    self.target_speed,
                    self.speed + accel_kmh_per_s * dt
                )
    
    def update_position(self, dt):
        """Update position based on current speed and direction."""
        # Convert speed to pixels/second for display
        # Assume 1 meter = 10 pixels
        pixels_per_meter = 10
        speed_pixels_per_second = self.get_speed_ms() * pixels_per_meter
        
        # Update position based on direction
        if self.direction == 'east':
            self.x += speed_pixels_per_second * dt
        elif self.direction == 'west':
            self.x -= speed_pixels_per_second * dt
        elif self.direction == 'south':
            self.y += speed_pixels_per_second * dt
        elif self.direction == 'north':
            self.y -= speed_pixels_per_second * dt
    
    def check_collision_ahead(self, other_vehicles, gates, pixels_per_meter=10):
        """
        Check for obstacles ahead and calculate distance.
        
        Args:
            other_vehicles: List of other SimulatedVehicle objects
            gates: List of gate positions (closed gates are obstacles)
            pixels_per_meter: Display scale factor
        
        Returns:
            (has_obstacle, distance_in_meters)
        """
        min_distance = float('inf')
        has_obstacle = False
        
        # Check closed gates
        for gate_pos, gate_closed in gates:
            if not gate_closed:
                continue
            
            gate_x, gate_y = gate_pos
            distance_pixels = self._distance_ahead_to_point(gate_x, gate_y)
            
            if distance_pixels > 0:  # Ahead of us
                distance_meters = distance_pixels / pixels_per_meter
                if distance_meters < 200:  # Within detection range
                    has_obstacle = True
                    min_distance = min(min_distance, distance_meters)
        
        # Check other vehicles (same direction, same lane)
        for other in other_vehicles:
            if other is self or other.direction != self.direction:
                continue
            
            # Check if in same lane (within tolerance)
            if not self._in_same_lane(other):
                continue
            
            # Calculate distance to other vehicle's rear
            distance_pixels = self._distance_ahead_to_vehicle(other)
            
            if distance_pixels > 0:  # Ahead of us
                distance_meters = distance_pixels / pixels_per_meter
                min_distance = min(min_distance, distance_meters)
                has_obstacle = True
        
        return has_obstacle, min_distance
    
    def _distance_ahead_to_point(self, target_x, target_y):
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
    
    def _distance_ahead_to_vehicle(self, other):
        """Calculate distance to another vehicle's rear (pixels)."""
        # Get position of other vehicle's rear
        if other.direction in ['east', 'west']:
            if other.direction == 'east':
                other_rear = other.x - other.width / 2
            else:
                other_rear = other.x + other.width / 2
            return self._distance_ahead_to_point(other_rear, other.y)
        else:
            if other.direction == 'south':
                other_rear = other.y - other.width / 2
            else:
                other_rear = other.y + other.width / 2
            return self._distance_ahead_to_point(other.x, other_rear)
    
    def _in_same_lane(self, other):
        """Check if other vehicle is in same lane (within tolerance)."""
        lane_tolerance = 30  # pixels
        
        if self.direction in ['east', 'west']:
            return abs(self.y - other.y) < lane_tolerance
        else:
            return abs(self.x - other.x) < lane_tolerance
    
    def should_turn_at_intersection(self, intersections):
        """
        Determine if should turn at upcoming intersection.
        
        Args:
            intersections: List of intersection positions
        
        Returns:
            (should_turn, intersection_pos, new_direction)
        """
        if not self.route or not self.router:
            return False, None, None
        
        if self.current_route_index >= len(self.route.directions):
            return False, None, None
        
        next_direction = self.route.directions[self.current_route_index]
        
        if next_direction == self.direction:
            return False, None, None
        
        # Find closest intersection in path
        for intersection in intersections:
            ix, iy = intersection['x'], intersection['y']
            
            if self.router.should_turn_at_intersection(
                vehicle_pos=(self.x, self.y),
                vehicle_direction=self.direction,
                intersection_pos=(ix, iy),
                planned_route=self.route,
                current_route_index=self.current_route_index
            ):
                return True, (ix, iy), next_direction
        
        return False, None, None
    
    def update(self, dt, other_vehicles, gates, intersections):
        """
        Main update loop - physics-based motion.
        
        Args:
            dt: Time delta in seconds
            other_vehicles: List of other vehicles
            gates: List of (position, is_closed) tuples
            intersections: List of intersection dicts
        """
        # Check for turn
        should_turn, turn_pos, new_dir = self.should_turn_at_intersection(
            intersections
        )
        
        if should_turn:
            self.start_turn(turn_pos, new_dir)
            return
        
        # Handle turning animation
        if self.turning:
            self.update_turn(dt)
            return
        
        # Check for obstacles ahead
        has_obstacle, distance = self.check_collision_ahead(
            other_vehicles,
            gates
        )
        
        # Decide if should brake
        should_brake = False
        if has_obstacle:
            should_brake = self.should_brake_for_obstacle(distance)
        
        # Update speed using physics
        self.update_speed(dt, should_brake)
        
        # Update position
        self.update_position(dt)
    
    def start_turn(self, intersection_pos, new_direction):
        """Initiate turn at intersection."""
        self.turning = True
        self.turn_progress = 0.0
        self.direction = new_direction
        self.current_route_index += 1
    
    def update_turn(self, dt):
        """Update turn animation."""
        turn_speed = 1.5  # turns/second
        self.turn_progress += turn_speed * dt
        
        if self.turn_progress >= 1.0:
            self.turning = False
            self.turn_progress = 0.0
    
    def draw(self, surface):
        """Draw vehicle on pygame surface."""
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
        
        # Draw darker border
        darker = tuple(max(0, c - 40) for c in self.color)
        pygame.draw.rect(surface, darker, rect, 2, border_radius=3)
    
    def is_off_screen(self, width, height):
        """Check if vehicle has left the screen."""
        margin = 100
        return (self.x < -margin or self.x > width + margin or
                self.y < -margin or self.y > height + margin)

if __name__ == "__main__":
    """
    Example showing how to use physics-based vehicles in simulation.
    """
    
    pygame.init()
    screen = pygame.display.set_mode((1400, 800))
    clock = pygame.time.Clock()
    
    # Define road network for routing
    road_network = {
        'intersections': [
            (500, 400), (900, 400),  # Horizontal road
            (500, 150), (500, 650)   # Vertical road
        ],
        'roads': {
            'horizontal': [(0, 400), (1400, 400)],
            'vertical': [(500, 0), (500, 800)]
        }
    }
    
    # Create vehicles using traffic module physics
    vehicles = [
        SimulatedVehicle(0, 400, 'east', 'car', road_network),
        SimulatedVehicle(1400, 400, 'west', 'truck', road_network),
        SimulatedVehicle(500, 0, 'south', 'suv', road_network)
    ]
    
    # Simulation parameters
    gates = [
        ({'x': 700, 'y': 400}, False),  # (position, is_closed)
    ]
    
    intersections = [
        {'x': 500, 'y': 400},
        {'x': 900, 'y': 400}
    ]
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update all vehicles with physics
        for vehicle in vehicles:
            vehicle.update(dt, vehicles, gates, intersections)
        
        # Remove off-screen vehicles
        vehicles = [v for v in vehicles if not v.is_off_screen(1400, 800)]
        
        # Draw
        screen.fill((180, 215, 175))  # Grass
        for vehicle in vehicles:
            vehicle.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()