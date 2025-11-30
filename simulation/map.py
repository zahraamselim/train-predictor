import pygame


class LevelCrossingMap:
    def __init__(self, width=1600, height=1000):
        self.width = width
        self.height = height
        
        self.colors = {
            'grass': (180, 215, 175),
            'road_asphalt': (60, 60, 70),
            'road_marking': (255, 255, 255),
            'road_edge': (40, 40, 50),
            'rail_tie': (100, 80, 65),
            'rail_metal': (180, 180, 190),
            'gravel': (140, 135, 125),
        }
        
        self.road_width = 80
        self.track_width = 40
        self.rail_width = 6
        
        self.horizontal_road_spacing = 350
        self.vertical_road_spacing = 500
        
    def draw(self, surface):
        self._draw_background(surface)
        self._draw_road_network(surface)
        self._draw_railway_line(surface)
    
    def _draw_background(self, surface):
        surface.fill(self.colors['grass'])
    
    def _draw_road_network(self, surface):
        top_road_y = self.height // 2 - self.horizontal_road_spacing
        bottom_road_y = self.height // 2 + self.horizontal_road_spacing
        left_road_x = self.width // 2 - self.vertical_road_spacing
        right_road_x = self.width // 2 + self.vertical_road_spacing
        
        for road_y in [top_road_y, bottom_road_y]:
            self._draw_horizontal_road(surface, road_y)
        
        for road_x in [left_road_x, right_road_x]:
            self._draw_vertical_road(surface, road_x)
        
        self._draw_intersections(surface, top_road_y, bottom_road_y, left_road_x, right_road_x)
    
    def _draw_horizontal_road(self, surface, road_y):
        road_rect = pygame.Rect(
            0,
            road_y - self.road_width // 2,
            self.width,
            self.road_width
        )
        
        pygame.draw.rect(surface, self.colors['road_asphalt'], road_rect)
        
        pygame.draw.rect(surface, self.colors['road_edge'],
                       (0, road_rect.top, self.width, 3))
        pygame.draw.rect(surface, self.colors['road_edge'],
                       (0, road_rect.bottom - 3, self.width, 3))
        
        left_road_x = self.width // 2 - self.vertical_road_spacing
        right_road_x = self.width // 2 + self.vertical_road_spacing
        intersection_gap = self.road_width + 30
        
        for x in range(30, self.width - 30, 40):
            if (left_road_x - intersection_gap//2 < x < left_road_x + intersection_gap//2 or
                right_road_x - intersection_gap//2 < x < right_road_x + intersection_gap//2):
                continue
            pygame.draw.rect(surface, self.colors['road_marking'],
                           (x, road_y - 2, 20, 4))
    
    def _draw_vertical_road(self, surface, road_x):
        road_rect = pygame.Rect(
            road_x - self.road_width // 2,
            0,
            self.road_width,
            self.height
        )
        
        pygame.draw.rect(surface, self.colors['road_asphalt'], road_rect)
        
        pygame.draw.rect(surface, self.colors['road_edge'],
                       (road_rect.left, 0, 3, self.height))
        pygame.draw.rect(surface, self.colors['road_edge'],
                       (road_rect.right - 3, 0, 3, self.height))
        
        top_road_y = self.height // 2 - self.horizontal_road_spacing
        bottom_road_y = self.height // 2 + self.horizontal_road_spacing
        railway_y = self.height // 2
        intersection_gap = self.road_width + 30
        railway_gap = 80
        
        for y in range(30, self.height - 30, 40):
            if (top_road_y - intersection_gap//2 < y < top_road_y + intersection_gap//2 or
                bottom_road_y - intersection_gap//2 < y < bottom_road_y + intersection_gap//2 or
                railway_y - railway_gap//2 < y < railway_y + railway_gap//2):
                continue
            pygame.draw.rect(surface, self.colors['road_marking'],
                           (road_x - 2, y, 4, 20))
    
    def _draw_intersections(self, surface, top_road_y, bottom_road_y, left_road_x, right_road_x):
        intersections = [
            (left_road_x, top_road_y),
            (right_road_x, top_road_y),
            (left_road_x, bottom_road_y),
            (right_road_x, bottom_road_y)
        ]
        
        for inter_x, inter_y in intersections:
            inter_size = self.road_width
            inter_rect = pygame.Rect(
                inter_x - inter_size // 2,
                inter_y - inter_size // 2,
                inter_size,
                inter_size
            )
            pygame.draw.rect(surface, self.colors['road_asphalt'], inter_rect)
    
    def _draw_railway_line(self, surface):
        railway_y = self.height // 2
        corridor_width = 70
        
        corridor_rect = pygame.Rect(
            0,
            railway_y - corridor_width // 2,
            self.width,
            corridor_width
        )
        pygame.draw.rect(surface, self.colors['gravel'], corridor_rect)
        
        left_road_x = self.width // 2 - self.vertical_road_spacing
        right_road_x = self.width // 2 + self.vertical_road_spacing
        crossing_gap = self.road_width
        
        tie_width = 4
        tie_spacing = 8
        
        for x in range(0, self.width, tie_width + tie_spacing):
            skip = False
            for road_x in [left_road_x, right_road_x]:
                if road_x - crossing_gap//2 < x < road_x + crossing_gap//2:
                    skip = True
                    break
            
            if not skip:
                tie_rect = pygame.Rect(
                    x,
                    railway_y - corridor_width // 2 + 5,
                    tie_width,
                    corridor_width - 10
                )
                pygame.draw.rect(surface, self.colors['rail_tie'], tie_rect)
        
        rail_spacing = 24
        rail_top_y = railway_y - rail_spacing // 2
        rail_bottom_y = railway_y + rail_spacing // 2
        
        pygame.draw.rect(surface, self.colors['rail_metal'],
                        (0, rail_top_y - self.rail_width // 2,
                         self.width, self.rail_width))
        pygame.draw.rect(surface, self.colors['rail_metal'],
                        (0, rail_bottom_y - self.rail_width // 2,
                         self.width, self.rail_width))
        
        for road_x in [left_road_x, right_road_x]:
            crossing_rect = pygame.Rect(
                road_x - crossing_gap // 2,
                railway_y - corridor_width // 2,
                crossing_gap,
                corridor_width
            )
            
            plank_height = 6
            plank_spacing = 3
            
            for y in range(crossing_rect.top, crossing_rect.bottom, plank_height + plank_spacing):
                plank_rect = pygame.Rect(
                    crossing_rect.left,
                    y,
                    crossing_rect.width,
                    plank_height
                )
                pygame.draw.rect(surface, self.colors['rail_tie'], plank_rect)
            
            pygame.draw.rect(surface, self.colors['rail_metal'],
                            (crossing_rect.left, rail_top_y - self.rail_width // 2,
                             crossing_rect.width, self.rail_width))
            pygame.draw.rect(surface, self.colors['rail_metal'],
                            (crossing_rect.left, rail_bottom_y - self.rail_width // 2,
                             crossing_rect.width, self.rail_width))
    
    def get_crossing_positions(self):
        railway_y = self.height // 2
        left_road_x = self.width // 2 - self.vertical_road_spacing
        right_road_x = self.width // 2 + self.vertical_road_spacing
        
        return [
            {'x': left_road_x, 'y': railway_y},
            {'x': right_road_x, 'y': railway_y}
        ]
    
    def get_intersection_positions(self):
        top_road_y = self.height // 2 - self.horizontal_road_spacing
        bottom_road_y = self.height // 2 + self.horizontal_road_spacing
        left_road_x = self.width // 2 - self.vertical_road_spacing
        right_road_x = self.width // 2 + self.vertical_road_spacing
        
        return [
            {'x': left_road_x, 'y': top_road_y},
            {'x': right_road_x, 'y': top_road_y},
            {'x': left_road_x, 'y': bottom_road_y},
            {'x': right_road_x, 'y': bottom_road_y}
        ]
    
    def get_spawn_points(self):
        margin = 50
        top_road_y = self.height // 2 - self.horizontal_road_spacing
        bottom_road_y = self.height // 2 + self.horizontal_road_spacing
        left_road_x = self.width // 2 - self.vertical_road_spacing
        right_road_x = self.width // 2 + self.vertical_road_spacing
        
        return [
            {'x': self.width + margin, 'y': top_road_y, 'direction': 'west'},
            {'x': self.width + margin, 'y': bottom_road_y, 'direction': 'west'},
            {'x': left_road_x, 'y': -margin, 'direction': 'south'},
            {'x': right_road_x, 'y': -margin, 'direction': 'south'}
        ]