"""Main simulation coordinating physics and rendering."""

import pygame
import sys
import os
import random
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.renderer import SimulationRenderer
from simulation.map import LevelCrossingMap
from physics.sensors import SensorArray
from physics.train import TrainPhysics, TRAIN_SPECS
from controller.eta_calculator import ETACalculator
from controller.decision_maker import CrossingController
from controller.metrics import PerformanceMetrics
from config.utils import load_config


class Vehicle:
    def __init__(self, vehicle_id, x, y, direction, vehicle_type, end_x, end_y):
        self.id = vehicle_id
        self.x = x
        self.y = y
        self.direction = direction
        self.vehicle_type = vehicle_type
        self.end_x = end_x
        self.end_y = end_y
        self.speed_kmh = random.uniform(40, 60)
        self.waiting = False
        self.completed = False
        self.engine_off = False
        self.engine_off_time = 0
        self.wait_start_time = None
        self.spawn_time = pygame.time.get_ticks() / 1000.0
        self.color_override = None
        self.decision_made = None
    
    def get_speed_ms(self):
        return self.speed_kmh / 3.6


class TrainSimulator:
    def __init__(self, train_type: str, initial_speed: float, crossing_distance: float):
        self.train_type = train_type
        self.physics = TrainPhysics(TRAIN_SPECS[train_type])
        
        config = load_config()
        self.length = config['train']['simulation_scale']['train_length']
        
        self.distance_to_crossing = crossing_distance
        self.speed_ms = initial_speed / 3.6
        self.target_speed_ms = self.speed_ms
        
        self.active = False
        self.passed = False
    
    def update(self, dt: float):
        if not self.active or self.passed:
            return
        
        accel = self.physics.calculate_acceleration(
            self.speed_ms, 0, self.target_speed_ms
        )
        
        self.speed_ms += accel * dt
        self.distance_to_crossing -= self.speed_ms * dt
        
        if self.distance_to_crossing < -self.length - 50:
            self.passed = True
    
    def activate(self):
        self.active = True
        self.passed = False
    
    def reset(self, crossing_distance: float):
        self.distance_to_crossing = crossing_distance
        self.active = False
        self.passed = False


class CrossingSimulation:
    def __init__(self, width=1600, height=1000):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Level Crossing System')
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        self.config = load_config()
        self.scale = self.config['simulation']['scale_pixels_per_meter']
        
        self.map = LevelCrossingMap(width, height)
        
        center_x = width // 2
        center_y = height // 2
        self.spacing_h = 350
        self.spacing_v = 500
        
        self.top_y = center_y - self.spacing_h
        self.bottom_y = center_y + self.spacing_h
        self.left_x = center_x - self.spacing_v
        self.right_x = center_x + self.spacing_v
        self.rail_y = center_y
        
        self.vehicles = []
        self.next_vehicle_id = 0
        self.spawn_timer = 0
        self.traffic_density = 'medium'
        
        self.sensors = SensorArray()
        self.eta_calculator = ETACalculator(self.sensors.sensor_positions)
        self.crossing_controller = CrossingController()
        self.metrics = PerformanceMetrics()
        
        crossing_distance = self.config['train']['simulation_scale']['crossing_distance']
        self.train = TrainSimulator('express', 120, crossing_distance)
        self.sensors_array = SensorArray()
        
        self.renderer = SimulationRenderer(width, height, self.map)
        
        self.current_eta = None
        self.gate_left_closed = False
        self.gate_right_closed = False
        self.gate_close_time = None
        
        self.show_metrics = False
        self.total_fuel_saved = 0.0
        self.fuel_save_rate = 0.0
        
        self.notification_lead_time = self.config['simulation']['notification_lead_time']
        self.inter_tl_notified = False
        self.inter_tr_notified = False
    
    def spawn_train(self):
        crossing_distance = self.config['train']['simulation_scale']['crossing_distance']
        self.train.reset(crossing_distance)
        self.train.activate()
        self.sensors_array.reset()
        self.gate_left_closed = False
        self.gate_right_closed = False
        self.gate_close_time = None
        self.current_eta = None
        self.inter_tl_notified = False
        self.inter_tr_notified = False
    
    def spawn_vehicle(self):
        if len(self.vehicles) >= self.config['simulation']['max_vehicles']:
            return
        
        spawn_choice = random.choice(['top_left', 'top_right', 'right_top', 'right_bottom'])
        
        if spawn_choice == 'top_left':
            x, y = self.left_x, -50
            direction = 'south'
            end_x, end_y = self.left_x, self.height + 50
        elif spawn_choice == 'top_right':
            x, y = self.right_x, -50
            direction = 'south'
            end_x, end_y = self.right_x, self.height + 50
        elif spawn_choice == 'right_top':
            x, y = self.width + 50, self.top_y
            direction = 'west'
            end_x, end_y = -50, self.top_y
        else:
            x, y = self.width + 50, self.bottom_y
            direction = 'west'
            end_x, end_y = -50, self.bottom_y
        
        vehicle_type = random.choices(
            ['car', 'suv', 'truck', 'motorcycle'],
            weights=[0.60, 0.25, 0.10, 0.05]
        )[0]
        
        vehicle = Vehicle(self.next_vehicle_id, x, y, direction, vehicle_type, end_x, end_y)
        self.next_vehicle_id += 1
        self.vehicles.append(vehicle)
    
    def update_vehicle(self, vehicle, dt):
        if vehicle.completed or vehicle.waiting:
            return
        
        speed_pixels = vehicle.get_speed_ms() * self.scale
        move_dist = speed_pixels * dt
        
        if vehicle.direction == 'south':
            next_y = vehicle.y + move_dist
            
            if not self.gate_left_closed and not self.gate_right_closed:
                vehicle.y = next_y
            else:
                if abs(vehicle.x - self.left_x) < 40 and not self.gate_left_closed:
                    vehicle.y = next_y
                elif abs(vehicle.x - self.right_x) < 40 and not self.gate_right_closed:
                    vehicle.y = next_y
                elif abs(vehicle.x - self.left_x) < 40 and vehicle.y < self.rail_y - 60:
                    vehicle.y = next_y
                elif abs(vehicle.x - self.right_x) < 40 and vehicle.y < self.rail_y - 60:
                    vehicle.y = next_y
                else:
                    if abs(vehicle.x - self.left_x) < 40 and self.gate_left_closed and vehicle.y >= self.rail_y - 60:
                        vehicle.waiting = True
                        vehicle.wait_start_time = pygame.time.get_ticks() / 1000.0
                    elif abs(vehicle.x - self.right_x) < 40 and self.gate_right_closed and vehicle.y >= self.rail_y - 60:
                        vehicle.waiting = True
                        vehicle.wait_start_time = pygame.time.get_ticks() / 1000.0
                    else:
                        vehicle.y = next_y
            
            if vehicle.y > self.height + 50:
                vehicle.completed = True
        
        elif vehicle.direction == 'west':
            next_x = vehicle.x - move_dist
            
            if not self.gate_left_closed and not self.gate_right_closed:
                vehicle.x = next_x
            else:
                if abs(vehicle.y - self.top_y) < 40 or abs(vehicle.y - self.bottom_y) < 40:
                    if vehicle.x > self.right_x + 60 or vehicle.x < self.left_x - 60:
                        vehicle.x = next_x
                    elif vehicle.x <= self.right_x + 60 and vehicle.x > self.right_x - 60 and self.gate_right_closed:
                        vehicle.waiting = True
                        vehicle.wait_start_time = pygame.time.get_ticks() / 1000.0
                    elif vehicle.x <= self.left_x + 60 and vehicle.x > self.left_x - 60 and self.gate_left_closed:
                        vehicle.waiting = True
                        vehicle.wait_start_time = pygame.time.get_ticks() / 1000.0
                    else:
                        vehicle.x = next_x
            
            if vehicle.x < -50:
                vehicle.completed = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if not self.train.active:
                        self.spawn_train()
                elif event.key == pygame.K_m:
                    self.show_metrics = not self.show_metrics
                elif event.key == pygame.K_l:
                    self.traffic_density = 'light'
                elif event.key == pygame.K_h:
                    self.traffic_density = 'heavy'
                elif event.key == pygame.K_n:
                    self.traffic_density = 'medium'
    
    def update(self):
        dt = self.clock.get_time() / 1000.0
        if dt > 0.1:
            dt = 0.1
        
        intervals = self.config['simulation']['spawn_interval']
        spawn_interval = intervals.get(self.traffic_density, 2.0)
        
        self.spawn_timer += dt
        if self.spawn_timer >= spawn_interval:
            self.spawn_vehicle()
            self.spawn_timer = 0
        
        if self.train.active and not self.train.passed:
            self.train.update(dt)
            
            events = self.sensors_array.update(
                self.train.distance_to_crossing,
                pygame.time.get_ticks() / 1000.0,
                self.train.length
            )
            
            detection_times = self.sensors_array.get_detection_times()
            
            if all(detection_times[f'sensor_{i}']['entry_time'] is not None for i in range(3)):
                timings = {
                    'sensor_0_entry': detection_times['sensor_0']['entry_time'],
                    'sensor_1_entry': detection_times['sensor_1']['entry_time'],
                    'sensor_2_entry': detection_times['sensor_2']['entry_time']
                }
                
                if self.eta_calculator.validate_timings(timings):
                    eta_result = self.eta_calculator.calculate_eta_robust(timings)
                    self.current_eta = eta_result['eta_final']
                    
                    gate_closure_offset = self.config['gates']['closure_before_eta']
                    
                    if self.current_eta <= gate_closure_offset + self.notification_lead_time and not self.inter_tl_notified:
                        self.inter_tl_notified = True
                        self.inter_tr_notified = True
                    
                    if self.current_eta <= gate_closure_offset:
                        if not self.gate_left_closed:
                            self.gate_left_closed = True
                            self.gate_close_time = pygame.time.get_ticks() / 1000.0
                        if not self.gate_right_closed:
                            self.gate_right_closed = True
        
        if self.train.passed:
            if self.gate_left_closed or self.gate_right_closed:
                current_time = pygame.time.get_ticks() / 1000.0
                if self.gate_close_time and current_time - self.gate_close_time > 5:
                    self.gate_left_closed = False
                    self.gate_right_closed = False
                    self.current_eta = None
                    self.inter_tl_notified = False
                    self.inter_tr_notified = False
                    
                    for vehicle in self.vehicles:
                        if vehicle.waiting:
                            vehicle.waiting = False
                    
                    self.train.active = False
        
        for vehicle in self.vehicles[:]:
            if vehicle.completed:
                self.vehicles.remove(vehicle)
            else:
                self.update_vehicle(vehicle, dt)
                
                if vehicle.waiting:
                    current_time = pygame.time.get_ticks() / 1000.0
                    wait_duration = current_time - vehicle.wait_start_time
                    
                    if not vehicle.engine_off and wait_duration >= 2.0:
                        vehicle.engine_off = True
                        vehicle.engine_off_time = current_time
        
        fuel_rates = self.config.get('fuel_rates', {})
        idling_rate = fuel_rates.get('idling', 0.01)
        off_rate = fuel_rates.get('off', 0.0)
        
        engines_off_count = sum(1 for v in self.vehicles if v.engine_off)
        self.fuel_save_rate = engines_off_count * (idling_rate - off_rate) / 60.0
        self.total_fuel_saved += self.fuel_save_rate * dt
    
    def render(self):
        self.screen.fill((0, 0, 0))
        self.map.draw(self.screen)
        
        self.renderer._render_traffic_flow_arrows(self.screen)
        self.renderer._render_train(self.screen, self.train)
        
        for vehicle in self.vehicles:
            self.renderer._render_vehicle_simple(self.screen, vehicle, self.scale)
        
        self.renderer._render_crossing_simple(
            self.screen, self.left_x, self.rail_y, 
            self.gate_left_closed, self.current_eta if self.gate_left_closed else None
        )
        self.renderer._render_crossing_simple(
            self.screen, self.right_x, self.rail_y,
            self.gate_right_closed, self.current_eta if self.gate_right_closed else None
        )
        
        self.renderer._render_intersection_simple(
            self.screen, self.left_x, self.top_y, self.inter_tl_notified
        )
        self.renderer._render_intersection_simple(
            self.screen, self.right_x, self.top_y, self.inter_tr_notified
        )
        
        self.renderer._render_info_panel(
            self.screen, self.train, self.current_eta, 
            len(self.vehicles), self.traffic_density, self.fuel_save_rate
        )
        
        self.renderer._render_controls(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
        
        pygame.quit()


if __name__ == '__main__':
    sim = CrossingSimulation()
    sim.run()