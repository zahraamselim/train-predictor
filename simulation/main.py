"""Main simulation with train detection and crossing control."""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.map import LevelCrossingMap
from simulation.crossing import RailwayGate, TrafficLight, CountdownTimer, Buzzer
from simulation.vehicles import VehicleManager
from simulation.train import Train
from physics.sensors import SensorArray
from controller.eta_calculator import ETACalculator
from controller.decision_maker import CrossingController
from controller.metrics import PerformanceMetrics
from config.utils import get_scale_config


class CrossingSimulation:
    """Complete level crossing simulation."""
    
    def __init__(self, width=1600, height=1000):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Level Crossing System Simulation')
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        config = get_scale_config()
        
        self.map = LevelCrossingMap(width, height)
        self.vehicle_manager = VehicleManager(width, height, self.map)
        
        self.sensors = SensorArray()
        self.eta_calculator = ETACalculator(self.sensors.sensor_positions)
        self.controller = CrossingController()
        self.metrics = PerformanceMetrics()
        
        self.train = Train(
            'express',
            120,
            config['train']['crossing_distance'],
            width,
            height
        )
        
        self._setup_crossing_equipment()
        
        self.train_spawned = False
        self.spawn_timer = 0
        self.spawn_interval = 45
        
        self.current_eta = None
        self.gates_should_close = False
        self.gates_closed_time = 0
    
    def _setup_crossing_equipment(self):
        crossings = self.map.get_crossing_positions()
        
        self.gates = []
        self.lights = []
        self.timers = []
        self.buzzers = []
        
        for crossing in crossings:
            cx, cy = crossing['x'], crossing['y']
            
            gate = RailwayGate(cx, cy - 40, 'right')
            self.gates.append(gate)
            
            light = TrafficLight(cx - 80, cy - 100)
            light.set_state('green')
            self.lights.append(light)
            
            timer = CountdownTimer(cx + 100, cy - 80)
            self.timers.append(timer)
            
            buzzer = Buzzer(cx + 80, cy + 70)
            self.buzzers.append(buzzer)
    
    def spawn_train(self):
        config = get_scale_config()
        self.train = Train(
            'express',
            120,
            config['train']['crossing_distance'],
            self.width,
            self.height
        )
        self.train.activate()
        self.train_spawned = True
        self.sensors.reset()
        self.current_eta = None
        self.gates_should_close = False
        self.gates_closed_time = 0
        print("\nTrain spawned at {}m".format(int(self.train.distance_to_crossing)))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if not self.train_spawned:
                        self.spawn_train()
                elif event.key == pygame.K_m:
                    self.metrics.print_report()
    
    def update(self):
        dt = self.clock.get_time() / 1000.0
        if dt > 0.1:
            dt = 0.1
        
        if not self.train_spawned:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_train()
                self.spawn_timer = 0
        
        if self.train.active and not self.train.passed:
            self.train.update(dt)
            
            events = self.sensors.update(
                self.train.distance_to_crossing,
                pygame.time.get_ticks() / 1000.0,
                self.train.length
            )
            
            for event in events:
                if event['event'] == 'entry':
                    print("Sensor {} triggered at distance {}m".format(
                        event['sensor_id'], 
                        int(self.train.distance_to_crossing)
                    ))
            
            detection_times = self.sensors.get_detection_times()
            
            if all(detection_times['sensor_{}'.format(i)]['entry_time'] is not None for i in range(3)):
                timings = {
                    'sensor_0_entry': detection_times['sensor_0']['entry_time'],
                    'sensor_1_entry': detection_times['sensor_1']['entry_time'],
                    'sensor_2_entry': detection_times['sensor_2']['entry_time']
                }
                
                if self.eta_calculator.validate_timings(timings):
                    eta_result = self.eta_calculator.calculate_eta_robust(timings)
                    self.current_eta = eta_result['eta_final']
                    
                    decisions = self.controller.process_sensor_detection(timings, self.current_eta)
                    
                    if decisions['close_gates'] and not self.gates_should_close:
                        self.gates_should_close = True
                        self._close_gates()
                        print("Gates closing - ETA: {}s, Speed: {} km/h".format(
                            int(self.current_eta),
                            int(eta_result['speed_1_to_2_kmh'])
                        ))
        
        if self.train.passed and self.gates_should_close:
            self.gates_closed_time += dt
            if self.gates_closed_time > 5:
                self._open_gates()
                self.gates_should_close = False
                self.gates_closed_time = 0
                print("Train passed, gates opening")
                self.train_spawned = False
                self.controller.reset()
                self.train.active = False
        
        for gate in self.gates:
            gate.update()
        
        for light in self.lights:
            light.update(dt)
        
        for timer in self.timers:
            timer.update(dt)
        
        for buzzer in self.buzzers:
            buzzer.update(dt)
        
        self.vehicle_manager.update(dt)
        
        completed = self.vehicle_manager.get_completed_journeys()
        for journey in completed:
            self.metrics.log_vehicle_journey(journey)
    
    def _close_gates(self):
        for gate in self.gates:
            gate.close()
        
        for light in self.lights:
            light.set_state('red')
        
        for timer in self.timers:
            if self.current_eta:
                timer.set_time(self.current_eta)
        
        for buzzer in self.buzzers:
            buzzer.activate()
        
        gate_positions = self.map.get_crossing_positions()
        self.vehicle_manager.set_closed_gates(gate_positions)
    
    def _open_gates(self):
        for gate in self.gates:
            gate.open()
        
        for light in self.lights:
            light.set_state('green')
        
        for timer in self.timers:
            timer.stop()
        
        for buzzer in self.buzzers:
            buzzer.deactivate()
        
        self.vehicle_manager.set_closed_gates([])
    
    def render(self):
        self.screen.fill((0, 0, 0))
        self.map.draw(self.screen)
        
        self.train.draw(self.screen)
        
        self.vehicle_manager.draw(self.screen)
        
        for gate in self.gates:
            gate.draw(self.screen)
        
        for light in self.lights:
            light.draw(self.screen)
        
        for timer in self.timers:
            timer.draw(self.screen)
        
        for buzzer in self.buzzers:
            buzzer.draw(self.screen)
        
        font = pygame.font.Font(None, 28)
        center_x = self.width // 2
        center_y = self.height // 2
        
        if self.train.active:
            texts = [
                "Train Distance: {}m".format(int(self.train.distance_to_crossing)),
                "Train Speed: {} km/h".format(int(self.train.speed_ms * 3.6)),
            ]
            
            if self.current_eta:
                texts.append("ETA: {}s".format(int(self.current_eta)))
            
            text_y = center_y - 120
            for text in texts:
                surface = font.render(text, True, (255, 255, 255))
                text_rect = surface.get_rect(center=(center_x, text_y))
                
                bg_rect = text_rect.inflate(20, 10)
                bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                bg_surface.fill((0, 0, 0, 180))
                self.screen.blit(bg_surface, bg_rect)
                
                self.screen.blit(surface, text_rect)
                text_y += 30
        
        stats_font = pygame.font.Font(None, 24)
        stats = [
            "Vehicles: {}".format(len(self.vehicle_manager.vehicles)),
            "Completed: {}".format(self.vehicle_manager.completed_count)
        ]
        
        stats_y = center_y + 80
        for text in stats:
            surface = stats_font.render(text, True, (200, 200, 200))
            text_rect = surface.get_rect(center=(center_x, stats_y))
            
            bg_rect = text_rect.inflate(15, 8)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            self.screen.blit(bg_surface, bg_rect)
            
            self.screen.blit(surface, text_rect)
            stats_y += 25
        
        controls_font = pygame.font.Font(None, 22)
        controls = controls_font.render("SPACE: Spawn Train | M: Show Metrics | ESC: Quit", True, (200, 200, 200))
        self.screen.blit(controls, (10, self.height - 30))
        
        pygame.display.flip()
    
    def run(self):
        print("\nLevel Crossing Simulation")
        print("SPACE - Spawn train manually")
        print("M - Show performance metrics")
        print("ESC - Quit")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
        
        print("\nFinal Metrics:")
        self.metrics.print_report()
        
        pygame.quit()


if __name__ == '__main__':
    sim = CrossingSimulation()
    sim.run()