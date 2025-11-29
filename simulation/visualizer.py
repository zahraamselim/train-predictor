"""Real-time metrics visualization overlay for simulation."""

import pygame


class MetricsVisualizer:
    """Display live performance metrics during simulation."""
    
    def __init__(self, x, y, width=300, height=250):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = False
        
        self.colors = {
            'background': (30, 30, 35, 230),
            'border': (80, 80, 90),
            'text': (220, 220, 230),
            'title': (100, 200, 255),
            'good': (100, 255, 100),
            'neutral': (255, 200, 100),
            'bad': (255, 100, 100)
        }
        
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
    
    def toggle(self):
        """Toggle visibility."""
        self.visible = not self.visible
    
    def draw(self, surface, metrics_report):
        """Draw metrics overlay."""
        if not self.visible:
            return
        
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill(self.colors['background'])
        
        title = self.font_large.render("Performance Metrics", True, self.colors['title'])
        bg_surface.blit(title, (10, 10))
        
        y_offset = 45
        
        if 'total_vehicles' in metrics_report:
            text = self.font_small.render(
                f"Vehicles: {metrics_report['total_vehicles']} total",
                True, self.colors['text']
            )
            bg_surface.blit(text, (10, y_offset))
            y_offset += 25
        
        if 'travel_time' in metrics_report and 'error' not in metrics_report['travel_time']:
            tt = metrics_report['travel_time']
            
            label = self.font_medium.render("Travel Time", True, self.colors['text'])
            bg_surface.blit(label, (10, y_offset))
            y_offset += 22
            
            improvement = tt.get('improvement_percent', 0)
            color = self.colors['good'] if improvement > 0 else self.colors['neutral']
            
            value = self.font_small.render(
                f"  {tt['improvement_seconds']:.1f}s saved ({improvement:.1f}%)",
                True, color
            )
            bg_surface.blit(value, (10, y_offset))
            y_offset += 25
        
        if 'fuel_consumption' in metrics_report:
            fc = metrics_report['fuel_consumption']
            
            label = self.font_medium.render("Fuel Savings", True, self.colors['text'])
            bg_surface.blit(label, (10, y_offset))
            y_offset += 22
            
            savings = fc.get('savings_percent', 0)
            color = self.colors['good'] if savings > 0 else self.colors['neutral']
            
            value = self.font_small.render(
                f"  {fc['savings_liters']:.3f}L ({savings:.1f}%)",
                True, color
            )
            bg_surface.blit(value, (10, y_offset))
            y_offset += 25
        
        if 'emissions' in metrics_report:
            em = metrics_report['emissions']
            
            label = self.font_medium.render("CO2 Reduction", True, self.colors['text'])
            bg_surface.blit(label, (10, y_offset))
            y_offset += 22
            
            reduction = em.get('reduction_percent', 0)
            color = self.colors['good'] if reduction > 0 else self.colors['neutral']
            
            value = self.font_small.render(
                f"  {em['reduction_kg']:.3f}kg ({reduction:.1f}%)",
                True, color
            )
            bg_surface.blit(value, (10, y_offset))
            y_offset += 25
        
        if 'comfort' in metrics_report and 'error' not in metrics_report['comfort']:
            cf = metrics_report['comfort']
            
            label = self.font_medium.render("Comfort", True, self.colors['text'])
            bg_surface.blit(label, (10, y_offset))
            y_offset += 22
            
            improvement = cf.get('improvement_percent', 0)
            color = self.colors['good'] if improvement > 0 else self.colors['neutral']
            
            value = self.font_small.render(
                f"  {improvement:.1f}% better",
                True, color
            )
            bg_surface.blit(value, (10, y_offset))
        
        pygame.draw.rect(bg_surface, self.colors['border'], (0, 0, self.width, self.height), 2)
        
        surface.blit(bg_surface, (self.x, self.y))
    
    def draw_simple(self, surface, vehicle_count, system_active):
        """Draw simplified metrics when full report not available."""
        if not self.visible:
            return
        
        bg_surface = pygame.Surface((self.width, 120), pygame.SRCALPHA)
        bg_surface.fill(self.colors['background'])
        
        title = self.font_large.render("Live Stats", True, self.colors['title'])
        bg_surface.blit(title, (10, 10))
        
        status_color = self.colors['good'] if system_active else self.colors['neutral']
        status_text = "ACTIVE" if system_active else "IDLE"
        status = self.font_medium.render(f"System: {status_text}", True, status_color)
        bg_surface.blit(status, (10, 45))
        
        vehicles = self.font_medium.render(f"Vehicles: {vehicle_count}", True, self.colors['text'])
        bg_surface.blit(vehicles, (10, 75))
        
        pygame.draw.rect(bg_surface, self.colors['border'], (0, 0, self.width, 120), 2)
        
        surface.blit(bg_surface, (self.x, self.y))


class SensorStatusDisplay:
    """Display sensor detection status."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sensor_states = [False, False, False]
        
        self.colors = {
            'background': (30, 30, 35, 200),
            'border': (80, 80, 90),
            'text': (220, 220, 230),
            'active': (100, 255, 100),
            'inactive': (100, 100, 110)
        }
        
        self.font = pygame.font.Font(None, 20)
    
    def update_sensors(self, sensor_detections):
        """Update sensor states from detection dict."""
        for i in range(3):
            key = f'sensor_{i}'
            if key in sensor_detections:
                self.sensor_states[i] = sensor_detections[key].get('entry_time') is not None
    
    def draw(self, surface):
        """Draw sensor status."""
        width = 200
        height = 100
        
        bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_surface.fill(self.colors['background'])
        
        title = self.font.render("Sensors", True, self.colors['text'])
        bg_surface.blit(title, (10, 10))
        
        y_offset = 35
        for i in range(3):
            color = self.colors['active'] if self.sensor_states[i] else self.colors['inactive']
            pygame.draw.circle(bg_surface, color, (20, y_offset + 5), 6)
            
            label = self.font.render(f"Sensor {i} (Furthest)" if i == 0 else f"Sensor {i}", True, self.colors['text'])
            bg_surface.blit(label, (35, y_offset))
            y_offset += 20
        
        pygame.draw.rect(bg_surface, self.colors['border'], (0, 0, width, height), 2)
        
        surface.blit(bg_surface, (self.x, self.y))