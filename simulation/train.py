"""Train visualization and simulation."""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from physics.train import TrainPhysics, TRAIN_SPECS
from config.utils import get_scale_config


class Train:
    """Train object with physics and visualization."""
    
    def __init__(self, train_type, initial_speed, crossing_distance, screen_width, screen_height):
        self.train_type = train_type
        self.physics = TrainPhysics(TRAIN_SPECS[train_type])
        
        config = get_scale_config()
        self.length = config['train']['train_length']
        
        self.distance_to_crossing = crossing_distance
        self.speed_ms = initial_speed / 3.6
        self.target_speed_ms = self.speed_ms
        
        self.active = False
        self.passed = False
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale = 10
        
        self.crossing_x = screen_width // 2 - 500
        self.y = screen_height // 2
        
        self.colors = {
            'body': (200, 50, 50),
            'window': (100, 150, 200),
            'stripe': (255, 200, 0)
        }
    
    def update(self, dt):
        """Update train physics and position."""
        if not self.active or self.passed:
            return
        
        accel = self.physics.calculate_acceleration(
            self.speed_ms, 0, self.target_speed_ms
        )
        
        self.speed_ms += accel * dt
        self.distance_to_crossing -= self.speed_ms * dt
        
        if self.distance_to_crossing < -self.length - 50:
            self.passed = True
    
    def draw(self, surface):
        """Draw train on screen."""
        if not self.active or self.passed:
            return
        
        train_x = self.crossing_x + (self.distance_to_crossing * self.scale)
        
        if train_x < -self.length * self.scale or train_x > self.screen_width + 100:
            return
        
        train_width = self.length * self.scale
        train_height = 30
        
        train_rect = pygame.Rect(
            train_x - train_width,
            self.y - train_height // 2,
            train_width,
            train_height
        )
        
        pygame.draw.rect(surface, self.colors['body'], train_rect)
        
        stripe_height = 4
        stripe_rect = pygame.Rect(
            train_rect.x,
            train_rect.y + train_height // 2 - stripe_height // 2,
            train_rect.width,
            stripe_height
        )
        pygame.draw.rect(surface, self.colors['stripe'], stripe_rect)
        
        window_width = 8
        window_height = 12
        window_spacing = 15
        window_y = train_rect.y + 6
        
        for i in range(int(train_width // window_spacing)):
            window_x = train_rect.x + 5 + i * window_spacing
            if window_x + window_width < train_rect.right:
                window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
                pygame.draw.rect(surface, self.colors['window'], window_rect)
        
        pygame.draw.rect(surface, (150, 30, 30), train_rect, 2)
    
    def activate(self):
        """Start train approaching."""
        self.active = True
        self.passed = False
    
    def reset(self):
        """Reset train state."""
        self.active = False
        self.passed = False
        config = get_scale_config()
        self.distance_to_crossing = config['train']['crossing_distance']
        self.speed_ms = 120 / 3.6
        self.target_speed_ms = self.speed_ms