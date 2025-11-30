"""Rendering engine for simulation visualization."""

import pygame
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config


class SimulationRenderer:
    def __init__(self, width: int, height: int, road_map):
        self.width = width
        self.height = height
        self.map = road_map
        self.config = load_config()
        
        self.scale = self.config['simulation']['scale_pixels_per_meter']
        
        self.colors = {
            'train_body': (200, 50, 50),
            'train_stripe': (255, 200, 0),
            'train_window': (100, 150, 200),
            'car': (180, 50, 50),
            'suv': (50, 100, 180),
            'truck': (100, 100, 100),
            'motorcycle': (200, 150, 50),
            'gate_arm': (255, 255, 0),
            'light_red': (255, 50, 50),
            'light_green': (50, 255, 50),
            'text_bg': (0, 0, 0, 180),
            'text': (255, 255, 255),
            'buzzer_active': (255, 200, 0),
            'buzzer_inactive': (100, 100, 100),
            'timer_inactive': (100, 100, 100)
        }
        
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
    
    def render(self, screen, train, vehicles, traffic_controller, metrics=None, 
               current_eta=None, traffic_density='medium', fuel_saved_rate=0.0):
        screen.fill((0, 0, 0))
        
        self.map.draw(screen)
        
        self._render_traffic_flow_arrows(screen)
        
        self._render_train(screen, train)
        self._render_vehicles(screen, vehicles)
        
        self._render_crossings(screen, traffic_controller, vehicles)
        self._render_intersections(screen, traffic_controller)
        
        self._render_info_panel(screen, train, current_eta, len(vehicles), traffic_density, fuel_saved_rate)
        
        if metrics:
            self._render_metrics(screen, metrics)
        
        self._render_controls(screen)
    
    def _render_train(self, screen, train):
        if not train.active or train.passed:
            return
        
        crossing_x = self.width // 2 - 500
        y = self.height // 2
        
        train_x = crossing_x + (train.distance_to_crossing * self.scale)
        
        if train_x < -train.length * self.scale or train_x > self.width + 100:
            return
        
        train_width = train.length * self.scale
        train_height = 30
        
        train_rect = pygame.Rect(
            int(train_x - train_width),
            int(y - train_height // 2),
            int(train_width),
            train_height
        )
        
        pygame.draw.rect(screen, self.colors['train_body'], train_rect)
        
        stripe_height = 4
        stripe_rect = pygame.Rect(
            train_rect.x,
            train_rect.y + train_height // 2 - stripe_height // 2,
            train_rect.width,
            stripe_height
        )
        pygame.draw.rect(screen, self.colors['train_stripe'], stripe_rect)
        
        window_width = 8
        window_height = 12
        window_spacing = 15
        window_y = train_rect.y + 6
        
        for i in range(int(train_width // window_spacing)):
            window_x = train_rect.x + 5 + i * window_spacing
            if window_x + window_width < train_rect.right:
                window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
                pygame.draw.rect(screen, self.colors['train_window'], window_rect)
        
        pygame.draw.rect(screen, (150, 30, 30), train_rect, 2)
    
    def _render_vehicle_simple(self, screen, vehicle, scale):
        """Render a single vehicle."""
        if vehicle.completed:
            return
        
        color = self.colors.get(vehicle.vehicle_type, self.colors['car'])
        if vehicle.color_override:
            color = vehicle.color_override
        
        width = int(4.5 * scale)
        height = int(width * 0.6)
        
        if vehicle.direction in ['west', 'east']:
            rect = pygame.Rect(
                int(vehicle.x - width // 2),
                int(vehicle.y - height // 2),
                width,
                height
            )
        else:
            rect = pygame.Rect(
                int(vehicle.x - height // 2),
                int(vehicle.y - width // 2),
                height,
                width
            )
        
        pygame.draw.rect(screen, color, rect, border_radius=3)
        darker = tuple(max(0, c - 40) for c in color)
        pygame.draw.rect(screen, darker, rect, 2, border_radius=3)
        
        if vehicle.engine_off:
            icon_x = rect.centerx
            icon_y = rect.centery
            pygame.draw.circle(screen, (100, 100, 100), (icon_x, icon_y), 6)
            pygame.draw.line(screen, (255, 255, 255), 
                           (icon_x - 3, icon_y), (icon_x + 3, icon_y), 2)
    
    def _render_crossing_simple(self, screen, x, y, is_closed, countdown):
        """Render crossing with gate, lights, buzzer, and timer."""
        self._render_gate(screen, x, y - 40, is_closed)
        self._render_traffic_light(screen, x - 80, y - 100, is_closed)
        self._render_countdown_timer(screen, x + 100, y - 80, countdown, is_closed)
        self._render_buzzer(screen, x + 80, y + 70, is_closed)
    
    def _render_intersection_simple(self, screen, x, y, is_notified):
        """Render intersection notification (light and buzzer)."""
        self._render_traffic_light(screen, x + 50, y - 30, is_notified)
        self._render_buzzer(screen, x + 80, y, is_notified)
    
    def _render_vehicles(self, screen, vehicles):
        for vehicle in vehicles:
            if vehicle.completed:
                continue
            
            if vehicle.color_override:
                color = vehicle.color_override
            else:
                color = self.colors.get(vehicle.vehicle_type, self.colors['car'])
            
            width = int(vehicle.physics.spec.length * self.scale)
            height = int(width * 0.6)
            
            if vehicle.direction in ['west', 'east']:
                rect = pygame.Rect(
                    int(vehicle.x - width // 2),
                    int(vehicle.y - height // 2),
                    width,
                    height
                )
            else:
                rect = pygame.Rect(
                    int(vehicle.x - height // 2),
                    int(vehicle.y - width // 2),
                    height,
                    width
                )
            
            pygame.draw.rect(screen, color, rect, border_radius=3)
            darker = tuple(max(0, c - 40) for c in color)
            pygame.draw.rect(screen, darker, rect, 2, border_radius=3)
            
            if vehicle.engine_off:
                icon_x = rect.centerx
                icon_y = rect.centery - 15
                pygame.draw.circle(screen, (100, 100, 100), (icon_x, icon_y), 6)
                pygame.draw.line(screen, (255, 255, 255), 
                               (icon_x - 3, icon_y), (icon_x + 3, icon_y), 2)
    
    def _render_crossings(self, screen, traffic_controller, vehicles):
        crossings = self.map.get_crossing_positions()
        
        for i, crossing in enumerate(crossings):
            cx, cy = crossing['x'], crossing['y']
            crossing_id = 'cross_left' if i == 0 else 'cross_right'
            
            is_closed = traffic_controller.is_crossing_closed(crossing_id)
            countdown = traffic_controller.get_crossing_countdown(crossing_id)
            
            queue_count = sum(1 for v in vehicles 
                            if not v.completed and v.waiting and 
                            abs(v.x - cx) < 100 and abs(v.y - cy) < 100)
            
            self._render_gate(screen, cx, cy - 40, is_closed)
            self._render_traffic_light(screen, cx - 80, cy - 100, is_closed)
            self._render_countdown_timer(screen, cx + 100, cy - 80, countdown, is_closed)
            self._render_buzzer(screen, cx + 80, cy + 70, is_closed)
            
            if queue_count > 0:
                self._render_queue_indicator(screen, cx, cy + 50, queue_count)
    
    def _render_gate(self, screen, x, y, closed):
        if closed:
            pygame.draw.line(screen, self.colors['gate_arm'], 
                           (x - 35, y), (x + 35, y), 6)
            pygame.draw.circle(screen, (0, 0, 0), (x - 35, y), 4)
            pygame.draw.circle(screen, (0, 0, 0), (x + 35, y), 4)
        else:
            pygame.draw.line(screen, (100, 100, 100), 
                           (x - 35, y - 30), (x - 30, y - 30), 4)
    
    def _render_traffic_light(self, screen, x, y, red):
        pygame.draw.rect(screen, (50, 50, 50), (x, y, 30, 60), border_radius=5)
        
        if red:
            pygame.draw.circle(screen, self.colors['light_red'], (x + 15, y + 15), 10)
            pygame.draw.circle(screen, (30, 60, 30), (x + 15, y + 45), 10)
        else:
            pygame.draw.circle(screen, (60, 30, 30), (x + 15, y + 15), 10)
            pygame.draw.circle(screen, self.colors['light_green'], (x + 15, y + 45), 10)
    
    def _render_countdown_timer(self, screen, x, y, countdown, active):
        if countdown is not None and countdown > 0 and active:
            text = f"{int(countdown)}s"
            color = (255, 255, 0)
        else:
            text = "--"
            color = self.colors['timer_inactive']
        
        surface = self.font_medium.render(text, True, color)
        
        bg_rect = surface.get_rect(center=(x, y))
        bg_rect.inflate_ip(10, 6)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        screen.blit(bg_surface, bg_rect)
        
        screen.blit(surface, surface.get_rect(center=(x, y)))
    
    def _render_buzzer(self, screen, x, y, active):
        color = self.colors['buzzer_active'] if active else self.colors['buzzer_inactive']
        pygame.draw.circle(screen, color, (x, y), 12)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), 12, 2)
        
        if active:
            for r in [16, 20, 24]:
                pygame.draw.circle(screen, (255, 200, 0, 100), (x, y), r, 2)
    
    def _render_intersections(self, screen, traffic_controller):
        intersections = self.map.get_intersection_positions()
        inter_names = ['inter_tl', 'inter_tr', 'inter_bl', 'inter_br']
        
        for i, inter in enumerate(intersections):
            ix, iy = inter['x'], inter['y']
            inter_id = inter_names[i]
            
            is_notified = traffic_controller.is_intersection_notified(inter_id)
            
            if i < 2:
                self._render_traffic_light(screen, ix + 50, iy - 30, is_notified)
                self._render_buzzer(screen, ix + 80, iy, is_notified)
    
    def _render_info_panel(self, screen, train, current_eta, vehicle_count, traffic_density, fuel_saved_rate):
        center_x = self.width // 2
        center_y = self.height // 2
        
        if train.active:
            texts = [
                f"Train: {int(train.distance_to_crossing)}m",
                f"Speed: {int(train.speed_ms * 3.6)} km/h"
            ]
            
            if current_eta:
                texts.append(f"ETA: {int(current_eta)}s")
            
            y = center_y - 150
            for text in texts:
                self._render_text_with_bg(screen, text, center_x, y, self.font_medium)
                y += 30
        
        stats = [
            f"Vehicles: {vehicle_count}",
            f"Traffic: {traffic_density.upper()}"
        ]
        
        if fuel_saved_rate > 0.001:
            stats.append(f"Fuel Saving: {fuel_saved_rate:.3f}L/s")
        
        y = center_y + 80
        for text in stats:
            self._render_text_with_bg(screen, text, center_x, y, self.font_small)
            y += 25
    
    def _render_metrics(self, screen, metrics):
        report = metrics.generate_full_report()
        
        x = 20
        y = 20
        width = 350
        height = 250
        
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((30, 30, 35, 230))
        
        title = self.font_large.render("Performance Metrics", True, (100, 200, 255))
        bg.blit(title, (10, 10))
        
        y_offset = 50
        
        if 'total_vehicles' in report:
            text = self.font_small.render(
                f"Total: {report['total_vehicles']} vehicles",
                True, (220, 220, 230)
            )
            bg.blit(text, (10, y_offset))
            y_offset += 30
        
        if 'travel_time' in report and 'error' not in report['travel_time']:
            tt = report['travel_time']
            label = self.font_medium.render("Travel Time", True, (220, 220, 230))
            bg.blit(label, (10, y_offset))
            y_offset += 25
            
            value = self.font_small.render(
                f"  Saved: {tt['improvement_seconds']:.1f}s ({tt['improvement_percent']:.1f}%)",
                True, (100, 255, 100)
            )
            bg.blit(value, (10, y_offset))
            y_offset += 30
        
        if 'fuel_consumption' in report:
            fc = report['fuel_consumption']
            label = self.font_medium.render("Fuel Savings", True, (220, 220, 230))
            bg.blit(label, (10, y_offset))
            y_offset += 25
            
            value = self.font_small.render(
                f"  {fc['savings_liters']:.3f}L ({fc['savings_percent']:.1f}%)",
                True, (100, 255, 100)
            )
            bg.blit(value, (10, y_offset))
            y_offset += 30
        
        if 'emissions' in report:
            em = report['emissions']
            label = self.font_medium.render("CO2 Reduction", True, (220, 220, 230))
            bg.blit(label, (10, y_offset))
            y_offset += 25
            
            value = self.font_small.render(
                f"  {em['reduction_kg']:.3f}kg ({em['reduction_percent']:.1f}%)",
                True, (100, 255, 100)
            )
            bg.blit(value, (10, y_offset))
        
        pygame.draw.rect(bg, (80, 80, 90), (0, 0, width, height), 2)
        screen.blit(bg, (x, y))
    
    def _render_controls(self, screen):
        controls = [
            "SPACE: Spawn Train",
            "T: Toggle Multi-Train",
            "M: Toggle Metrics",
            "L: Light Traffic",
            "N: Normal Traffic",
            "H: Heavy Traffic",
            "ESC: Quit"
        ]
        
        y = self.height - 30 - (len(controls) * 20)
        for text in controls:
            surface = self.font_small.render(text, True, (200, 200, 200))
            screen.blit(surface, (10, y))
            y += 20
        
        legend = [
            "Green: Reroute",
            "Red: Wait",
            "Engine Off Icon: Saving Fuel"
        ]
        
        legend_x = self.width - 220
        legend_y = self.height - 100
        
        for text in legend:
            surface = self.font_small.render(text, True, (180, 180, 180))
            screen.blit(surface, (legend_x, legend_y))
            legend_y += 20
    
    def _render_text_with_bg(self, screen, text, center_x, center_y, font):
        surface = font.render(text, True, self.colors['text'])
        text_rect = surface.get_rect(center=(center_x, center_y))
        
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill(self.colors['text_bg'])
        screen.blit(bg_surface, bg_rect)
        
        screen.blit(surface, text_rect)
    
    def _render_queue_indicator(self, screen, x, y, count):
        text = f"Queue: {count}"
        surface = self.font_small.render(text, True, (255, 200, 100))
        
        bg_rect = surface.get_rect(center=(x, y))
        bg_rect.inflate_ip(10, 6)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        screen.blit(bg_surface, bg_rect)
        
        screen.blit(surface, surface.get_rect(center=(x, y)))
    
    def _render_traffic_flow_arrows(self, screen):
        center_x = self.width // 2
        center_y = self.height // 2
        spacing_h = 350
        spacing_v = 500
        
        arrow_color = (100, 100, 120, 150)
        arrow_size = 20
        
        top_y = center_y - spacing_h
        bottom_y = center_y + spacing_h
        left_x = center_x - spacing_v
        right_x = center_x + spacing_v
        
        positions = [
            (left_x - 100, top_y, 'left'),
            (left_x - 100, bottom_y, 'left'),
            (left_x, top_y - 100, 'down'),
            (right_x, top_y - 100, 'down')
        ]
        
        for x, y, direction in positions:
            if direction == 'left':
                points = [
                    (x - arrow_size, y),
                    (x, y - arrow_size // 2),
                    (x, y + arrow_size // 2)
                ]
            else:
                points = [
                    (x, y + arrow_size),
                    (x - arrow_size // 2, y),
                    (x + arrow_size // 2, y)
                ]
            
            surface = pygame.Surface((arrow_size * 2, arrow_size * 2), pygame.SRCALPHA)
            adjusted_points = [(p[0] - x + arrow_size, p[1] - y + arrow_size) for p in points]
            pygame.draw.polygon(surface, arrow_color, adjusted_points)
            screen.blit(surface, (x - arrow_size, y - arrow_size))