"""Live train simulation visualization using Pygame."""

import pygame
import sys

try:
    from .train_simulator import TrainSimulator
    from .train_types import TRAIN_TYPES
except ImportError:
    from train_simulator import TrainSimulator
    from train_types import TRAIN_TYPES


class TrainVisualization:
    """Pygame visualization of train approaching level crossing."""
    
    def __init__(self, width=1400, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Train Level Crossing Simulation")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        self.BLACK = (20, 20, 25)
        self.WHITE = (245, 245, 250)
        self.GRAY = (90, 90, 95)
        self.RED = (220, 53, 69)
        self.GREEN = (40, 167, 69)
        self.BLUE = (13, 110, 253)
        self.YELLOW = (255, 193, 7)
        self.ORANGE = (253, 126, 20)
        self.SKY = (135, 185, 210)
        self.GRASS = (85, 107, 47)
        self.RAIL_METAL = (70, 70, 75)
        
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        self.track_y = height // 2
        self.track_width = 40
        self.crossing_x = width // 2
        
        self.train_width = 200
        self.train_height = 50
        
        self.sensor_distances = [400, 250, 100]
        self.pixels_per_meter = 0.6
    
    def draw_background(self):
        """Draw grass and sky."""
        self.screen.fill(self.SKY)
        pygame.draw.rect(self.screen, self.GRASS, 
                        (0, self.track_y - 50, self.width, self.height))
    
    def draw_tracks(self):
        """Draw railway tracks."""
        rail_offset = 15
        
        ballast_height = 25
        pygame.draw.rect(self.screen, (80, 80, 82),
                        (0, self.track_y - ballast_height // 2,
                         self.width, ballast_height))
        
        sleeper_spacing = 30
        sleeper_width = 12
        sleeper_height = 45
        for x in range(0, self.width, sleeper_spacing):
            pygame.draw.rect(self.screen, (110, 110, 115),
                           (x - sleeper_width // 2, self.track_y - sleeper_height // 2,
                            sleeper_width, sleeper_height))
        
        for offset in [-rail_offset, rail_offset]:
            pygame.draw.line(self.screen, self.RAIL_METAL,
                            (0, self.track_y + offset),
                            (self.width, self.track_y + offset), 6)
            pygame.draw.line(self.screen, (100, 100, 105),
                            (0, self.track_y + offset - 1),
                            (self.width, self.track_y + offset - 1), 2)
    
    def draw_crossing(self, gate_closed=False):
        """Draw level crossing with gates."""
        crossing_width = 60
        
        pygame.draw.rect(self.screen, (50, 50, 55),
                        (self.crossing_x - crossing_width // 2,
                         self.track_y - 80,
                         crossing_width, 160))
        
        for i in range(4):
            pygame.draw.rect(self.screen, (255, 215, 0),
                           (self.crossing_x - 2,
                            self.track_y - 70 + i * 40,
                            4, 25))
        
        sign_x = self.crossing_x + 60
        sign_y = self.track_y - 100
        
        pygame.draw.rect(self.screen, (80, 80, 85),
                        (sign_x - 3, sign_y, 6, 100))
        
        pygame.draw.circle(self.screen, self.YELLOW, (sign_x, sign_y), 22)
        pygame.draw.circle(self.screen, self.BLACK, (sign_x, sign_y), 22, 2)
        
        pygame.draw.line(self.screen, self.BLACK,
                        (sign_x - 10, sign_y - 10),
                        (sign_x + 10, sign_y + 10), 2)
        pygame.draw.line(self.screen, self.BLACK,
                        (sign_x + 10, sign_y - 10),
                        (sign_x - 10, sign_y + 10), 2)
        
        gate_stripe_color = self.RED if gate_closed else (180, 180, 185)
        gate_length = 70
        
        if gate_closed:
            for gate_y in [self.track_y - 70, self.track_y + 62]:
                pygame.draw.rect(self.screen, self.WHITE,
                               (self.crossing_x - 50, gate_y, gate_length, 6))
                for i in range(0, gate_length, 12):
                    if i % 24 < 12:
                        pygame.draw.rect(self.screen, gate_stripe_color,
                                       (self.crossing_x - 50 + i, gate_y, 12, 6))
        else:
            for gate_x in [self.crossing_x - 50, self.crossing_x - 50]:
                pygame.draw.rect(self.screen, (200, 200, 205),
                               (gate_x, self.track_y - 70, 6, 20))
                pygame.draw.rect(self.screen, (200, 200, 205),
                               (gate_x, self.track_y + 50, 6, 20))
    
    def draw_sensors(self, distance_to_crossing):
        """Draw IR sensor zones."""
        for i, sensor_dist in enumerate(self.sensor_distances):
            sensor_screen_x = self.crossing_x - (sensor_dist * self.pixels_per_meter)
            
            in_zone = abs(distance_to_crossing - sensor_dist) < 20
            
            if in_zone:
                pygame.draw.circle(self.screen, (255, 140, 0), 
                                 (int(sensor_screen_x), self.track_y), 8)
                pygame.draw.circle(self.screen, (255, 100, 0), 
                                 (int(sensor_screen_x), self.track_y), 8, 2)
            else:
                pygame.draw.circle(self.screen, (100, 100, 105), 
                                 (int(sensor_screen_x), self.track_y), 5)
            
            label = self.font_small.render(f"IR{i+1}", True, (180, 180, 185))
            self.screen.blit(label, (sensor_screen_x - 15, self.track_y + 25))
    
    def draw_train(self, train_x, train_type, speed):
        """Draw the train (clipped to visible area)."""
        if train_x > self.width:
            return
        
        train_y = self.track_y - self.train_height // 2
        
        colors = {
            'passenger': (40, 90, 140),
            'freight': (90, 70, 50),
            'express': (180, 30, 50)
        }
        train_color = colors.get(train_type, self.BLUE)
        
        visible_x = max(0, train_x)
        visible_width = min(self.train_width, self.width - train_x)
        
        if visible_width <= 0:
            return
        
        clip_offset = max(0, -train_x)
        
        pygame.draw.rect(self.screen, train_color,
                        (visible_x, train_y, visible_width, self.train_height))
        
        highlight_color = tuple(min(c + 30, 255) for c in train_color)
        pygame.draw.rect(self.screen, highlight_color,
                        (visible_x, train_y, visible_width, 8))
        
        pygame.draw.rect(self.screen, (30, 30, 35),
                        (visible_x, train_y, visible_width, self.train_height), 2)
        
        window_spacing = 35
        window_width = 25
        window_height = 20
        for i in range(5):
            window_x = train_x + 20 + i * window_spacing
            if 0 <= window_x < self.width - window_width:
                pygame.draw.rect(self.screen, (180, 200, 220),
                               (window_x, train_y + 12, window_width, window_height))
                pygame.draw.rect(self.screen, (50, 50, 55),
                               (window_x, train_y + 12, window_width, window_height), 1)
        
        headlight_x = train_x + self.train_width - 12
        if 0 <= headlight_x < self.width:
            pygame.draw.circle(self.screen, (255, 255, 200),
                              (headlight_x, train_y + self.train_height // 2), 6)
            pygame.draw.circle(self.screen, (200, 200, 150),
                              (headlight_x, train_y + self.train_height // 2), 6, 1)
        
        wheel_y = train_y + self.train_height + 3
        wheel_positions = [25, 60, 140, 175]
        for wx in wheel_positions:
            wheel_x = train_x + wx
            if 0 <= wheel_x < self.width:
                pygame.draw.circle(self.screen, (30, 30, 35),
                                 (wheel_x, wheel_y), 7)
                pygame.draw.circle(self.screen, (60, 60, 65),
                                 (wheel_x, wheel_y), 4)
    
    def draw_info_panel(self, time, distance, speed, accel, eta, grade, weather, 
                       train_type, braking, crossing_status):
        """Draw information panel with current state."""
        panel_x = 20
        panel_y = 20
        panel_width = 340
        panel_height = 440
        
        pygame.draw.rect(self.screen, (25, 30, 35), 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (60, 65, 70), 
                        (panel_x, panel_y, panel_width, panel_height), 1)
        
        pygame.draw.rect(self.screen, (35, 40, 45),
                        (panel_x, panel_y, panel_width, 50))
        title = self.font_large.render("Train Status", True, (200, 205, 210))
        self.screen.blit(title, (panel_x + 15, panel_y + 12))
        
        y_offset = panel_y + 70
        line_height = 34
        
        status_colors = {
            'approaching': (40, 167, 69),
            'entering': (255, 193, 7),
            'occupying': (220, 53, 69),
            'clearing': (255, 140, 0),
            'cleared': (40, 167, 69)
        }
        status_color = status_colors.get(crossing_status, self.WHITE)
        
        info = [
            ("Type", train_type.capitalize(), (100, 150, 200)),
            ("Speed", f"{speed:.1f} km/h", (200, 205, 210)),
            ("Accel", f"{accel:.2f} m/s²", (255, 140, 0) if accel < -0.1 else (150, 155, 160)),
            ("Distance", f"{distance:.0f} m", (180, 185, 190)),
            ("ETA", f"{eta:.1f} s" if eta > 0 else "Passed", (220, 53, 69) if 0 < eta < 10 else (150, 155, 160)),
            ("Time", f"{time:.1f} s", (150, 155, 160)),
            ("Grade", f"{grade:+.1f}%", (150, 155, 160)),
            ("Weather", weather.capitalize(), (150, 155, 160)),
            ("Crossing", crossing_status.capitalize(), status_color),
        ]
        
        for label, value, color in info:
            label_surf = self.font_small.render(f"{label}", True, (120, 125, 130))
            value_surf = self.font_medium.render(value, True, color)
            self.screen.blit(label_surf, (panel_x + 18, y_offset))
            self.screen.blit(value_surf, (panel_x + 160, y_offset - 3))
            y_offset += line_height
    
    def draw_distance_scale(self, distance_to_crossing):
        """Draw distance scale at bottom."""
        scale_y = self.height - 60
        scale_start_x = 100
        scale_end_x = self.width - 100
        
        pygame.draw.line(self.screen, self.WHITE,
                        (scale_start_x, scale_y),
                        (scale_end_x, scale_y), 3)
        
        for dist in [-400, -300, -200, -100, 0, 100, 200, 300, 400, 500, 600]:
            marker_x = self.crossing_x - (dist * self.pixels_per_meter)
            if scale_start_x <= marker_x <= scale_end_x:
                pygame.draw.line(self.screen, self.WHITE,
                               (marker_x, scale_y - 10),
                               (marker_x, scale_y + 10), 2)
                label = self.font_small.render(f"{dist}m", True, self.WHITE)
                self.screen.blit(label, (marker_x - 20, scale_y + 15))
        
        train_marker_x = self.crossing_x - (distance_to_crossing * self.pixels_per_meter)
        if scale_start_x <= train_marker_x <= scale_end_x:
            pygame.draw.circle(self.screen, self.RED, (int(train_marker_x), scale_y), 8)
    
    def run_simulation(self, train_type='passenger', initial_speed=100, 
                      grade=0, weather='clear', crossing_distance=2000):
        """Run the visualization simulation."""
        sim = TrainSimulator(train_type, crossing_distance)
        trajectory = sim.simulate_approach(initial_speed, grade, weather, dt=0.1)
        
        current_frame = 0
        frame_accumulator = 0.0
        paused = False
        playback_speed = 1.0
        auto_slow_near_crossing = True
        
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
                        frame_accumulator = 0.0
                    elif event.key == pygame.K_UP:
                        playback_speed = min(5.0, playback_speed + 0.5)
                    elif event.key == pygame.K_DOWN:
                        playback_speed = max(0.1, playback_speed - 0.5)
                    elif event.key == pygame.K_a:
                        auto_slow_near_crossing = not auto_slow_near_crossing
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            if current_frame >= len(trajectory):
                self.draw_background()
                self.draw_tracks()
                self.draw_crossing(False)
                
                end_text = self.font_large.render("Simulation Complete", True, self.YELLOW)
                restart_text = self.font_medium.render("Press R to restart or ESC to exit", True, self.WHITE)
                self.screen.blit(end_text, (self.width // 2 - 200, self.height // 2 - 50))
                self.screen.blit(restart_text, (self.width // 2 - 250, self.height // 2 + 20))
                
                pygame.display.flip()
                self.clock.tick(30)
                continue
            
            if paused:
                pause_text = self.font_large.render("PAUSED", True, self.YELLOW)
                self.screen.blit(pause_text, (self.width // 2 - 80, 100))
                pygame.display.flip()
                self.clock.tick(30)
                continue
            
            data = trajectory[current_frame]
            
            time = data['time']
            distance = data['distance_to_crossing']
            speed = data['speed']
            accel = data['acceleration']
            eta = data['ETA']
            crossing_status = data['crossing_status']
            
            effective_speed = playback_speed
            if auto_slow_near_crossing:
                if crossing_status in ['entering', 'occupying', 'clearing']:
                    effective_speed = playback_speed * 0.2
            
            train_x = self.crossing_x - (distance * self.pixels_per_meter) - self.train_width
            braking = accel < -0.1
            gates_closed = crossing_status in ['entering', 'occupying', 'clearing'] or (eta <= 10 and eta > 0)
            
            self.draw_background()
            self.draw_tracks()
            self.draw_sensors(distance)
            self.draw_crossing(gates_closed)
            self.draw_train(train_x, train_type, speed)
            
            debug_text = self.font_small.render(
                f"Frame: {current_frame}/{len(trajectory)} | Dist: {distance:.1f}m | Speed: {effective_speed:.2f}x", 
                True, (180, 185, 190)
            )
            self.screen.blit(debug_text, (self.width - 650, 20))
            
            if crossing_status == 'cleared':
                cleared_text = self.font_large.render("TRAIN CLEARED", True, self.GREEN)
                self.screen.blit(cleared_text, (self.width // 2 - 150, 100))
            elif crossing_status == 'clearing':
                clearing_text = self.font_large.render("CLEARING CROSSING", True, self.ORANGE)
                self.screen.blit(clearing_text, (self.width // 2 - 180, 100))
            
            self.draw_info_panel(time, distance, speed, accel, eta, 
                                grade, weather, train_type, braking, crossing_status)
            self.draw_distance_scale(distance)
            
            controls = [
                "SPACE: Pause",
                "R: Restart",
                "UP/DOWN: Speed",
                f"Speed: {playback_speed:.1f}x",
                "A: Auto-slow " + ("ON" if auto_slow_near_crossing else "OFF")
            ]
            
            y_pos = self.height - 150
            for control in controls:
                text = self.font_small.render(control, True, (160, 165, 170))
                self.screen.blit(text, (self.width - 250, y_pos))
                y_pos += 30
            
            pygame.display.flip()
            
            frame_accumulator += effective_speed
            if frame_accumulator >= 1.0:
                current_frame += 1
                frame_accumulator -= 1.0
            
            self.clock.tick(self.fps)
        
        pygame.quit()


if __name__ == "__main__":
    viz = TrainVisualization()
    viz.run_simulation('passenger', initial_speed=100, grade=0, weather='clear')