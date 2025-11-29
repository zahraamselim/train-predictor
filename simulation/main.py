"""Main simulation with train detection and crossing control."""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.map import LevelCrossingMap
from simulation.crossing import RailwayGate, TrafficLight, CountdownTimer, Buzzer
from simulation.vehicles import VehicleManager
from physics.train import TrainPhysics, TRAIN_SPECS
from physics.sensors import SensorArray
from controller.eta_calculator import ETACalculator
from controller.decision_maker import CrossingController
from controller.metrics import PerformanceMetrics
from config.utils import get_scale_config


class Train:
    """Train object for simulation."""
    
    def __init__(self, train_type, initial_speed, crossing_distance):
        self.train_type = train_type
        self.physics = TrainPhysics(TRAIN_SPECS[train_type])
        
        config = get_scale_config()
        self.length = config['train']['train_length']
        
        self.distance_to_crossing = crossing_distance
        self.speed_ms = initial_speed / 3.6
        self.target_speed_ms = self.speed_ms
        
        self.active = False
        self.passed = False
    
    def update(self, dt):
        """Update train position."""
        if not self.active or self.passed:
            return
        
        accel = self.physics.calculate_acceleration(
            self.speed_ms, 0, self.target_speed_ms
        )
        
        self.speed_ms += accel * dt
        self.distance_to_crossing -= self.speed_ms * dt
        
        if self.distance_to_crossing < -(self.length + 100):
            self.passed = True
            self.active = False
    
    def activate(self):
        """Start train approaching."""
        self.active = True
        self.passed = False


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
        self.vehicle_manager = VehicleManager(width, height)
        
        self.sensors = SensorArray()
        self.eta_calculator = ETACalculator(self.sensors.sensor_positions)
        self.controller = CrossingController()
        self.metrics = PerformanceMetrics()
        
        self.train = Train(
            'express',
            120,
            config['train']['crossing_distance']
        )
        
        self._setup_crossing_equipment()
        
        self.train_spawned = False
        self.spawn_timer = 0
        self.spawn_interval = 30
        
        self.current_eta = None
        self.gates_should_close = False
    
    def _setup_crossing_equipment(self):
        """Setup gates, lights, timers."""
        crossings = self.map.get_crossing_positions()
        
        self.gates = []
        self.lights = []
        self.timers = []
        self.buzzers = []
        
        for crossing in crossings:
            cx, cy = crossing['x'], crossing['y']
            
            gate = RailwayGate(cx, cy - 40, 'right')
            self.gates.append(gate)
            
            light = TrafficLight(cx - 65, cy - 80)
            light.set_state('green')
            self.lights.append(light)
            
            timer = CountdownTimer(cx + 85, cy - 60)
            self.timers.append(timer)
            
            buzzer = Buzzer(cx + 65, cy + 60)
            self.buzzers.append(buzzer)
    
    def spawn_train(self):
        """Spawn new train."""
        config = get_scale_config()
        self.train = Train(
            'express',
            120,
            config['train']['crossing_distance']
        )
        self.train.activate()
        self.train_spawned = True
        self.sensors.reset()
        print("\nTrain spawned!")
    
    def handle_events(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.spawn_train()
                elif event.key == pygame.K_m:
                    self.metrics.print_report()
    
    def update(self):
        """Main update loop."""
        dt = self.clock.get_time() / 1000.0
        
        if not self.train_spawned:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_train()
                self.spawn_timer = 0
        
        if self.train.active:
            self.train.update(dt)
            
            events = self.sensors.update(
                self.train.distance_to_crossing,
                pygame.time.get_ticks() / 1000.0,
                self.train.length
            )
            
            for event in events:
                if event['event'] == 'entry':
                    print(f"Sensor {event['sensor_id']} triggered at t={event['time']:.1f}s")
            
            detection_times = self.sensors.get_detection_times()
            
            if all(detection_times[f'sensor_{i}']['entry_time'] is not None for i in range(3)):
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
                        print(f"Gates closing! ETA: {self.current_eta:.1f}s")
                        print(f"Speed: {eta_result['speed_1_to_2_kmh']:.1f} km/h")
        
        if self.train.passed:
            if self.gates_should_close:
                self._open_gates()
                self.gates_should_close = False
                print("Train passed, gates opening")
            
            self.train_spawned = False
            self.controller.reset()
            self.current_eta = None
        
        for gate in self.gates:
            gate.update()
        
        for light in self.lights:
            light.update(dt)
        
        for timer in self.timers:
            timer.update(dt)
        
        for buzzer in self.buzzers:
            buzzer.update(dt)
        
        self.vehicle_manager.update(dt)
        
        journey_data = self.vehicle_manager.get_journey_data()
        for journey in journey_data:
            self.metrics.log_vehicle_journey(journey)
    
    def _close_gates(self):
        """Close gates and activate warnings."""
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
        """Open gates and deactivate warnings."""
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
        """Render everything."""
        self.screen.fill((0, 0, 0))
        self.map.draw(self.screen)
        self.vehicle_manager.draw(self.screen)
        
        for gate in self.gates:
            gate.draw(self.screen)
        
        for light in self.lights:
            light.draw(self.screen)
        
        for timer in self.timers:
            timer.draw(self.screen)
        
        for buzzer in self.buzzers:
            buzzer.draw(self.screen)
        
        font = pygame.font.Font(None, 24)
        
        if self.train.active:
            info_y = 20
            texts = [
                f"Train Distance: {self.train.distance_to_crossing:.1f}m",
                f"Train Speed: {self.train.speed_ms * 3.6:.1f} km/h",
            ]
            
            if self.current_eta:
                texts.append(f"ETA: {self.current_eta:.1f}s")
            
            for text in texts:
                surface = font.render(text, True, (255, 255, 255))
                self.screen.blit(surface, (10, info_y))
                info_y += 30
        
        controls = font.render("SPACE: Spawn Train | M: Show Metrics | ESC: Quit", True, (200, 200, 200))
        self.screen.blit(controls, (10, self.height - 30))
        
        pygame.display.flip()
    
    def run(self):
        """Main simulation loop."""
        print("\nLevel Crossing Simulation")
        print("Controls:")
        print("  SPACE - Spawn train manually")
        print("  M - Show performance metrics")
        print("  ESC - Quit")
        
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