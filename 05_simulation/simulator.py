import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from map import LevelCrossingMap
from gates import RailwayGate, TrafficLight, CountdownTimer, RoadIntersectionSignal, Buzzer
from vehicles import VehicleManager


class CrossingSimulator:
    def __init__(self, width=1600, height=1000):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Level Crossing Notification System')
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        self.map = LevelCrossingMap(width, height)
        self._setup_crossing_equipment()
        self._setup_vehicles()
    
    def _setup_crossing_equipment(self):
        crossings = self.map.get_crossing_positions()
        road_bounds = self.map.get_road_bounds()
        
        self.gates = []
        self.crossing_lights = []
        self.timers = []
        
        for crossing in crossings:
            cx, cy = crossing['x'], crossing['y']
            
            gate = RailwayGate(cx, cy - 10, 'left')
            self.gates.append(gate)
            
            light = TrafficLight(cx - 65, cy - 80)
            light.set_state('green')
            self.crossing_lights.append(light)
            
            timer = CountdownTimer(cx + 85, cy - 60)
            self.timers.append(timer)
        
        self.intersection_lights = []
        self.buzzers = []
        
        intersections = [
            (road_bounds['left_road']['x'], road_bounds['top_road']['y']),
            (road_bounds['right_road']['x'], road_bounds['top_road']['y']),
            (road_bounds['left_road']['x'], road_bounds['bottom_road']['y']),
            (road_bounds['right_road']['x'], road_bounds['bottom_road']['y'])
        ]
        
        railway_y = self.map.get_railway_bounds()['y']
        
        for ix, iy in intersections:
            if iy < railway_y:
                light = TrafficLight(ix - 65, iy + 85)
                buzzer = Buzzer(ix + 65, iy + 65)
            else:
                light = TrafficLight(ix - 65, iy - 85)
                buzzer = Buzzer(ix + 65, iy - 65)
            
            light.set_state('green')
            self.intersection_lights.append(light)
            self.buzzers.append(buzzer)
    
    def _setup_vehicles(self):
        road_bounds = self.map.get_road_bounds()
        railway_bounds = self.map.get_railway_bounds()
        self.vehicle_manager = VehicleManager(
            self.width,
            self.height,
            road_bounds,
            railway_bounds
        )
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        dt = self.clock.get_time() / 1000.0
        
        for gate in self.gates:
            gate.update()
        
        for light in self.crossing_lights:
            light.update(dt)
        
        for timer in self.timers:
            timer.update(dt)
        
        for signal in self.intersection_lights:
            signal.update(dt)
        
        for buzzer in self.buzzers:
            buzzer.update(dt)
        
        self.vehicle_manager.update(dt)
    
    def render(self):
        self.screen.fill((0, 0, 0))
        self.map.draw(self.screen)
        
        self.vehicle_manager.draw(self.screen)
        
        for gate in self.gates:
            gate.draw(self.screen)
        
        for light in self.crossing_lights:
            light.draw(self.screen)
        
        for timer in self.timers:
            timer.draw(self.screen)
        
        for signal in self.intersection_lights:
            signal.draw(self.screen)
        
        for buzzer in self.buzzers:
            buzzer.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
        
        pygame.quit()


if __name__ == '__main__':
    simulator = CrossingSimulator()
    simulator.run()