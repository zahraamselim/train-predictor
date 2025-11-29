"""Railway crossing equipment: gates, lights, timers, buzzers."""

import pygame
import math


class RailwayGate:
    """Animated railway crossing gate."""
    
    def __init__(self, x, y, pivot='left'):
        self.x = x
        self.y = y
        self.pivot = pivot
        self.is_closed = False
        self.angle = 90
        self.target_angle = 90
        self.animation_speed = 2
        
        self.colors = {
            'pole': (80, 80, 90),
            'pole_base': (60, 60, 70),
            'barrier': (40, 40, 50),
            'stripe_yellow': (255, 220, 0),
            'stripe_black': (30, 30, 35)
        }
        
        self.pole_width = 12
        self.pole_height = 60
        self.barrier_length = 140
        self.barrier_width = 8
    
    def close(self):
        """Lower gate."""
        self.is_closed = True
        self.target_angle = 0
    
    def open(self):
        """Raise gate."""
        self.is_closed = False
        self.target_angle = 90
    
    def update(self):
        """Animate gate movement."""
        if self.angle < self.target_angle:
            self.angle = min(self.angle + self.animation_speed, self.target_angle)
        elif self.angle > self.target_angle:
            self.angle = max(self.angle - self.animation_speed, self.target_angle)
    
    def draw(self, surface):
        """Draw gate."""
        if self.pivot == 'left':
            pole_x = self.x - 70
        elif self.pivot == 'right':
            pole_x = self.x + 70
        else:
            pole_x = self.x
        
        pole_top_y = self.y - self.pole_height
        
        base_rect = pygame.Rect(pole_x - self.pole_width, self.y - 5, self.pole_width * 2, 10)
        pygame.draw.rect(surface, self.colors['pole_base'], base_rect)
        
        pole_rect = pygame.Rect(pole_x - self.pole_width // 2, pole_top_y, self.pole_width, self.pole_height)
        pygame.draw.rect(surface, self.colors['pole'], pole_rect)
        
        barrier_surface = pygame.Surface((self.barrier_length, self.barrier_width), pygame.SRCALPHA)
        
        stripe_width = 10
        for i in range(0, self.barrier_length, stripe_width * 2):
            pygame.draw.rect(barrier_surface, self.colors['stripe_yellow'], (i, 0, stripe_width, self.barrier_width))
            pygame.draw.rect(barrier_surface, self.colors['stripe_black'], (i + stripe_width, 0, stripe_width, self.barrier_width))
        
        angle_rad = math.radians(-self.angle)
        rotated_barrier = pygame.transform.rotate(barrier_surface, math.degrees(angle_rad))
        
        barrier_rect = rotated_barrier.get_rect()
        
        if self.pivot == 'left':
            barrier_rect.bottomleft = (pole_x, pole_top_y + self.barrier_width // 2)
        elif self.pivot == 'right':
            barrier_rect.bottomright = (pole_x, pole_top_y + self.barrier_width // 2)
        else:
            barrier_rect.center = (pole_x, pole_top_y + self.barrier_width // 2)
        
        surface.blit(rotated_barrier, barrier_rect)


class TrafficLight:
    """Traffic light with red/green states."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = 'green'
        self.blink_timer = 0
        self.blink_visible = True
        
        self.colors = {
            'housing': (50, 50, 55),
            'red_on': (255, 50, 50),
            'red_off': (100, 30, 30),
            'green_on': (50, 255, 50),
            'green_off': (30, 100, 30)
        }
        
        self.light_radius = 12
        self.housing_width = 35
        self.housing_height = 80
    
    def set_state(self, state):
        """Set light state: 'red', 'green', 'red_blink'."""
        self.state = state
        self.blink_timer = 0
        self.blink_visible = True
    
    def update(self, dt):
        """Update blinking if needed."""
        if self.state == 'red_blink':
            self.blink_timer += dt
            if self.blink_timer >= 0.5:
                self.blink_visible = not self.blink_visible
                self.blink_timer = 0
    
    def draw(self, surface):
        """Draw traffic light."""
        housing_rect = pygame.Rect(
            self.x - self.housing_width // 2,
            self.y - self.housing_height // 2,
            self.housing_width,
            self.housing_height
        )
        pygame.draw.rect(surface, self.colors['housing'], housing_rect)
        pygame.draw.rect(surface, (30, 30, 35), housing_rect, 2)
        
        red_center = (self.x, self.y - 20)
        green_center = (self.x, self.y + 20)
        
        if self.state == 'red' or (self.state == 'red_blink' and self.blink_visible):
            pygame.draw.circle(surface, self.colors['red_on'], red_center, self.light_radius)
            pygame.draw.circle(surface, (255, 100, 100), red_center, self.light_radius - 3)
        else:
            pygame.draw.circle(surface, self.colors['red_off'], red_center, self.light_radius)
        
        if self.state == 'green':
            pygame.draw.circle(surface, self.colors['green_on'], green_center, self.light_radius)
            pygame.draw.circle(surface, (100, 255, 100), green_center, self.light_radius - 3)
        else:
            pygame.draw.circle(surface, self.colors['green_off'], green_center, self.light_radius)


class CountdownTimer:
    """7-segment countdown display."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.time_remaining = 0
        self.active = False
        
        self.colors = {
            'background': (20, 20, 25),
            'border': (60, 60, 70),
            'segment_on': (255, 50, 50),
            'segment_off': (40, 15, 15)
        }
        
        self.width = 80
        self.height = 40
        self.segment_width = 3
        self.digit_spacing = 18
        
        self.segments = {
            '0': [1,1,1,1,1,1,0], '1': [0,1,1,0,0,0,0], '2': [1,1,0,1,1,0,1],
            '3': [1,1,1,1,0,0,1], '4': [0,1,1,0,0,1,1], '5': [1,0,1,1,0,1,1],
            '6': [1,0,1,1,1,1,1], '7': [1,1,1,0,0,0,0], '8': [1,1,1,1,1,1,1],
            '9': [1,1,1,1,0,1,1]
        }
    
    def set_time(self, seconds):
        """Start countdown from seconds."""
        self.time_remaining = seconds
        self.active = True
    
    def stop(self):
        """Stop and hide timer."""
        self.active = False
        self.time_remaining = 0
    
    def update(self, dt):
        """Update countdown."""
        if self.active and self.time_remaining > 0:
            self.time_remaining -= dt
            if self.time_remaining < 0:
                self.time_remaining = 0
    
    def _draw_segment(self, surface, x, y, segment_type, is_on):
        """Draw single 7-segment piece."""
        color = self.colors['segment_on'] if is_on else self.colors['segment_off']
        w = self.segment_width
        
        if segment_type == 'horizontal':
            points = [(x, y), (x + 10, y), (x + 8, y + w), (x + 2, y + w)]
        elif segment_type == 'vertical_top':
            points = [(x, y), (x + w, y + 2), (x + w, y + 8), (x, y + 10)]
        else:
            points = [(x, y), (x + w, y + 2), (x + w, y + 8), (x, y + 10)]
        
        pygame.draw.polygon(surface, color, points)
    
    def _draw_digit(self, surface, x, y, digit):
        """Draw complete digit."""
        segments = self.segments.get(digit, self.segments['0'])
        
        seg_positions = [
            (x + 2, y, 'horizontal'), (x + 12, y + 2, 'vertical_top'),
            (x + 12, y + 12, 'vertical_top'), (x + 2, y + 20, 'horizontal'),
            (x, y + 12, 'vertical_top'), (x, y + 2, 'vertical_top'),
            (x + 2, y + 10, 'horizontal')
        ]
        
        for i, (sx, sy, seg_type) in enumerate(seg_positions):
            self._draw_segment(surface, sx, sy, seg_type, segments[i] == 1)
    
    def draw(self, surface):
        """Draw countdown timer."""
        if not self.active:
            return
        
        bg_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
        pygame.draw.rect(surface, self.colors['background'], bg_rect)
        pygame.draw.rect(surface, self.colors['border'], bg_rect, 2)
        
        total_seconds = int(self.time_remaining)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_str = f"{minutes:02d}{seconds:02d}"
        
        start_x = self.x - (4 * self.digit_spacing) // 2 + 5
        
        for i, digit in enumerate(time_str):
            digit_x = start_x + i * self.digit_spacing
            self._draw_digit(surface, digit_x, self.y - 10, digit)
            
            if i == 1:
                pygame.draw.circle(surface, self.colors['segment_on'], (digit_x + 16, self.y - 3), 2)
                pygame.draw.circle(surface, self.colors['segment_on'], (digit_x + 16, self.y + 3), 2)


class Buzzer:
    """Warning buzzer with visual indicator."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = False
        self.blink_timer = 0
        self.blink_visible = False
        
        self.colors = {
            'housing': (60, 60, 65),
            'speaker': (40, 40, 45),
            'active': (255, 200, 0),
            'inactive': (100, 100, 110)
        }
        
        self.size = 20
    
    def activate(self):
        """Turn on buzzer."""
        self.active = True
        self.blink_timer = 0
    
    def deactivate(self):
        """Turn off buzzer."""
        self.active = False
        self.blink_visible = False
    
    def update(self, dt):
        """Update blinking animation."""
        if self.active:
            self.blink_timer += dt
            if self.blink_timer >= 0.3:
                self.blink_visible = not self.blink_visible
                self.blink_timer = 0
    
    def draw(self, surface):
        """Draw buzzer."""
        pygame.draw.circle(surface, self.colors['housing'], (self.x, self.y), self.size)
        pygame.draw.circle(surface, self.colors['speaker'], (self.x, self.y), self.size - 4)
        
        if self.active and self.blink_visible:
            for i in range(3):
                radius = self.size + 5 + i * 8
                pygame.draw.circle(surface, self.colors['active'], (self.x, self.y), radius, 2)
        
        indicator_color = self.colors['active'] if self.active else self.colors['inactive']
        pygame.draw.circle(surface, indicator_color, (self.x, self.y), 6)