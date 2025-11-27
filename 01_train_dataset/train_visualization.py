"""
Live train simulation visualization using Pygame.

Shows a train approaching a level crossing with real-time physics display.
"""

import pygame
import sys
from .train_simulator import TrainSimulator
from .train_types import TRAIN_TYPES


class TrainVisualization:
    """
    Pygame visualization of train approaching level crossing.
    """
    
    def __init__(self, width=1400, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Train Level Crossing Simulation")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.DARK_GRAY = (50, 50, 50)
        self.RED = (200, 50, 50)
        self.GREEN = (50, 200, 50)
        self.BLUE = (50, 100, 200)
        self.YELLOW = (255, 200, 50)
        self.ORANGE = (255, 140, 0)
        self.BROWN = (139, 90, 43)
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        # Track dimensions (visual)
        self.track_y = height // 2
        self.track_width = 80
        self.crossing_x = width - 300  # Crossing position on screen
        
        # Train representation
        self.train_width = 150
        self.train_height = 60
        
        # Sensor positions (relative to crossing)
        self.sensor_distances = [400, 250, 100]  # meters
        self.pixels_per_meter = 0.5  # Visual scale
        
    def draw_background(self):
        """Draw grass and sky."""
        self.screen.fill((135, 206, 235))  # Sky blue
        pygame.draw.rect(self.screen, (34, 139, 34), 
                        (0, self.track_y - 50, self.width, self.height))  # Grass
    
    def draw_tracks(self):
        """Draw railway tracks."""
        # Rails (two parallel lines)
        rail_offset = self.track_width // 3
        pygame.draw.line(self.screen, self.DARK_GRAY,
                        (0, self.track_y - rail_offset),
                        (self.width, self.track_y - rail_offset), 8)
        pygame.draw.line(self.screen, self.DARK_GRAY,
                        (0, self.track_y + rail_offset),
                        (self.width, self.track_y + rail_offset), 8)
        
        # Sleepers (ties)
        sleeper_spacing = 40
        for x in range(0, self.width, sleeper_spacing):
            pygame.draw.rect(self.screen, self.BROWN,
                           (x, self.track_y - self.track_width // 2,
                            25, self.track_width))
    
    def draw_crossing(self, gate_closed=False):
        """Draw level crossing with gates."""
        crossing_width = 120
        
        # Crossing surface
        pygame.draw.rect(self.screen, self.GRAY,
                        (self.crossing_x - crossing_width // 2,
                         self.track_y - self.track_width // 2 - 40,
                         crossing_width, self.track_width + 80))
        
        # Road markings
        for i in range(5):
            pygame.draw.rect(self.screen, self.WHITE,
                           (self.crossing_x - 30 + i * 15,
                            self.track_y - self.track_width // 2 - 30,
                            8, self.track_width + 60))
        
        # Crossing sign
        sign_x = self.crossing_x + 80
        sign_y = self.track_y - 120
        pygame.draw.circle(self.screen, self.YELLOW, (sign_x, sign_y), 30)
        pygame.draw.circle(self.screen, self.BLACK, (sign_x, sign_y), 30, 3)
        
        # X shape on sign
        pygame.draw.line(self.screen, self.BLACK,
                        (sign_x - 15, sign_y - 15),
                        (sign_x + 15, sign_y + 15), 4)
        pygame.draw.line(self.screen, self.BLACK,
                        (sign_x + 15, sign_y - 15),
                        (sign_x - 15, sign_y + 15), 4)
        
        # Gates
        gate_color = self.RED if gate_closed else self.WHITE
        gate_length = 100
        
        if gate_closed:
            # Closed gates (horizontal)
            pygame.draw.rect(self.screen, gate_color,
                           (self.crossing_x - 60, self.track_y - 80, gate_length, 10))
            pygame.draw.rect(self.screen, gate_color,
                           (self.crossing_x - 60, self.track_y + 70, gate_length, 10))
            # Red and white stripes
            for i in range(0, gate_length, 20):
                pygame.draw.rect(self.screen, self.WHITE if i % 40 == 0 else self.RED,
                               (self.crossing_x - 60 + i, self.track_y - 80, 20, 10))
                pygame.draw.rect(self.screen, self.WHITE if i % 40 == 0 else self.RED,
                               (self.crossing_x - 60 + i, self.track_y + 70, 20, 10))
        else:
            # Open gates (vertical)
            pygame.draw.rect(self.screen, gate_color,
                           (self.crossing_x - 60, self.track_y - 80, 10, 30))
            pygame.draw.rect(self.screen, gate_color,
                           (self.crossing_x - 60, self.track_y + 50, 10, 30))
    
    def draw_sensors(self, distance_to_crossing):
        """Draw IR sensor zones."""
        for i, sensor_dist in enumerate(self.sensor_distances):
            sensor_screen_x = self.crossing_x - (sensor_dist * self.pixels_per_meter)
            
            # Check if train is in sensor zone
            in_zone = abs(distance_to_crossing - sensor_dist) < 20
            color = self.ORANGE if in_zone else (100, 100, 100, 50)
            
            # Draw sensor zone (semi-transparent circle)
            surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*color[:3], 80), (50, 50), 50)
            self.screen.blit(surface, (sensor_screen_x - 50, self.track_y - 50))
            
            # Sensor label
            label = self.font_small.render(f"IR{i+1} ({sensor_dist}m)", True, self.WHITE)
            self.screen.blit(label, (sensor_screen_x - 40, self.track_y + 60))
    
    def draw_train(self, train_x, train_type, speed):
        """Draw the train."""
        train_y = self.track_y - self.train_height // 2
        
        # Train colors by type
        colors = {
            'passenger': (70, 130, 180),
            'freight': (139, 90, 43),
            'express': (220, 20, 60)
        }
        train_color = colors.get(train_type, self.BLUE)
        
        # Main body
        pygame.draw.rect(self.screen, train_color,
                        (train_x, train_y, self.train_width, self.train_height), 
                        border_radius=5)
        
        # Outline
        pygame.draw.rect(self.screen, self.BLACK,
                        (train_x, train_y, self.train_width, self.train_height), 3,
                        border_radius=5)
        
        # Windows
        window_spacing = 25
        window_size = 15
        for i in range(5):
            pygame.draw.rect(self.screen, self.YELLOW,
                           (train_x + 15 + i * window_spacing,
                            train_y + 10, window_size, window_size))
        
        # Front headlight
        pygame.draw.circle(self.screen, self.YELLOW,
                          (train_x + self.train_width - 10, train_y + self.train_height // 2),
                          8)
        
        # Wheels
        wheel_y = train_y + self.train_height + 5
        wheel_positions = [30, 60, 90, 120]
        for wx in wheel_positions:
            pygame.draw.circle(self.screen, self.BLACK,
                             (train_x + wx, wheel_y), 8)
            pygame.draw.circle(self.screen, self.DARK_GRAY,
                             (train_x + wx, wheel_y), 5)
        
        # Motion lines (if moving)
        if speed > 5:
            num_lines = min(5, int(speed / 20))
            for i in range(num_lines):
                line_x = train_x - 20 - i * 15
                pygame.draw.line(self.screen, (150, 150, 150),
                               (line_x, train_y + 10),
                               (line_x - 10, train_y + 10), 2)
                pygame.draw.line(self.screen, (150, 150, 150),
                               (line_x, train_y + self.train_height - 10),
                               (line_x - 10, train_y + self.train_height - 10), 2)
    
    def draw_info_panel(self, time, distance, speed, accel, eta, grade, weather, train_type, braking):
        """Draw information panel with current state."""
        panel_x = 20
        panel_y = 20
        panel_width = 350
        panel_height = 400
        
        # Panel background
        surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 180), (0, 0, panel_width, panel_height), border_radius=10)
        self.screen.blit(surface, (panel_x, panel_y))
        
        # Title
        title = self.font_large.render("Train Status", True, self.YELLOW)
        self.screen.blit(title, (panel_x + 20, panel_y + 15))
        
        y_offset = panel_y + 70
        line_height = 35
        
        # Information lines
        info = [
            ("Train Type", train_type.capitalize(), self.GREEN),
            ("Speed", f"{speed:.1f} km/h", self.WHITE),
            ("Acceleration", f"{accel:.2f} m/s²", self.ORANGE if accel < -0.1 else self.WHITE),
            ("Distance", f"{distance:.0f} m", self.WHITE),
            ("ETA", f"{eta:.1f} s", self.RED if eta < 10 else self.WHITE),
            ("Time", f"{time:.1f} s", self.WHITE),
            ("Grade", f"{grade:+.1f}%", self.WHITE),
            ("Weather", weather.capitalize(), self.WHITE),
            ("Status", "BRAKING" if braking else "Normal", self.RED if braking else self.GREEN)
        ]
        
        for label, value, color in info:
            label_surf = self.font_small.render(f"{label}:", True, self.GRAY)
            value_surf = self.font_medium.render(value, True, color)
            self.screen.blit(label_surf, (panel_x + 20, y_offset))
            self.screen.blit(value_surf, (panel_x + 180, y_offset - 3))
            y_offset += line_height
    
    def draw_distance_scale(self, distance_to_crossing):
        """Draw distance scale at bottom."""
        scale_y = self.height - 60
        scale_start_x = 100
        scale_end_x = self.width - 100
        
        # Scale line
        pygame.draw.line(self.screen, self.WHITE,
                        (scale_start_x, scale_y),
                        (scale_end_x, scale_y), 3)
        
        # Markers
        for dist in [0, 100, 200, 300, 400, 500]:
            marker_x = self.crossing_x - (dist * self.pixels_per_meter)
            if scale_start_x <= marker_x <= scale_end_x:
                pygame.draw.line(self.screen, self.WHITE,
                               (marker_x, scale_y - 10),
                               (marker_x, scale_y + 10), 2)
                label = self.font_small.render(f"{dist}m", True, self.WHITE)
                self.screen.blit(label, (marker_x - 20, scale_y + 15))
        
        # Current distance marker
        train_marker_x = self.crossing_x - (distance_to_crossing * self.pixels_per_meter)
        if scale_start_x <= train_marker_x <= scale_end_x:
            pygame.draw.circle(self.screen, self.RED, (int(train_marker_x), scale_y), 8)
    
    def run_simulation(self, train_type='passenger', initial_speed=100, 
                      grade=0, weather='clear', crossing_distance=2000):
        """
        Run the visualization simulation.
        
        Args:
            train_type: 'passenger', 'freight', or 'express'
            initial_speed: Starting speed (km/h)
            grade: Track grade (percentage)
            weather: 'clear', 'rain', or 'fog'
            crossing_distance: Distance to simulate (meters)
        """
        # Generate trajectory
        sim = TrainSimulator(train_type, crossing_distance)
        trajectory = sim.simulate_approach(initial_speed, grade, weather, dt=0.1)
        
        # Simulation state
        current_frame = 0
        paused = False
        playback_speed = 1.0
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        current_frame = 0
                    elif event.key == pygame.K_UP:
                        playback_speed = min(5.0, playback_speed + 0.5)
                    elif event.key == pygame.K_DOWN:
                        playback_speed = max(0.1, playback_speed - 0.5)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            if not paused and current_frame < len(trajectory):
                data = trajectory[current_frame]
                
                # Extract data
                time = data['time']
                distance = data['distance_to_crossing']
                speed = data['speed']
                accel = data['acceleration']
                eta = data['ETA']
                
                # Calculate train screen position
                train_x = self.crossing_x - (distance * self.pixels_per_meter) - self.train_width
                
                # Determine if braking
                braking = accel < -0.1
                
                # Determine if gates should be closed (10 seconds before arrival)
                gates_closed = eta <= 10
                
                # Draw everything
                self.draw_background()
                self.draw_tracks()
                self.draw_sensors(distance)
                self.draw_crossing(gates_closed)
                self.draw_train(train_x, train_type, speed)
                self.draw_info_panel(time, distance, speed, accel, eta, 
                                    grade, weather, train_type, braking)
                self.draw_distance_scale(distance)
                
                # Controls display
                controls = [
                    "SPACE: Pause/Resume",
                    "R: Restart",
                    "UP/DOWN: Speed",
                    f"Speed: {playback_speed:.1f}x"
                ]
                
                y_pos = self.height - 150
                for control in controls:
                    text = self.font_small.render(control, True, self.WHITE)
                    self.screen.blit(text, (self.width - 250, y_pos))
                    y_pos += 30
                
                pygame.display.flip()
                
                # Advance frame based on playback speed
                current_frame += int(playback_speed)
                
                self.clock.tick(self.fps)
            elif current_frame >= len(trajectory):
                # Simulation ended
                self.draw_background()
                self.draw_tracks()
                self.draw_crossing(False)
                
                end_text = self.font_large.render("Simulation Complete", True, self.YELLOW)
                restart_text = self.font_medium.render("Press R to restart or ESC to exit", True, self.WHITE)
                self.screen.blit(end_text, (self.width // 2 - 200, self.height // 2 - 50))
                self.screen.blit(restart_text, (self.width // 2 - 250, self.height // 2 + 20))
                
                pygame.display.flip()
                self.clock.tick(30)
            else:
                # Paused
                pause_text = self.font_large.render("PAUSED", True, self.YELLOW)
                self.screen.blit(pause_text, (self.width // 2 - 80, 100))
                pygame.display.flip()
                self.clock.tick(30)
        
        pygame.quit()


if __name__ == "__main__":
    viz = TrainVisualization()
    
    # Example scenarios - uncomment one to try
    
    # Scenario 1: Normal passenger train
    viz.run_simulation('passenger', initial_speed=100, grade=0, weather='clear')
    
    # Scenario 2: Heavy freight on uphill
    # viz.run_simulation('freight', initial_speed=60, grade=2, weather='clear')
    
    # Scenario 3: Express train in rain
    # viz.run_simulation('express', initial_speed=140, grade=0, weather='rain')
    
    # Scenario 4: Passenger downhill
    # viz.run_simulation('passenger', initial_speed=80, grade=-2, weather='clear')