"""Traffic control for intersections and crossing notifications."""

from typing import Dict, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config


class IntersectionNotification:
    def __init__(self, intersection_id: str, position: tuple, notification_lead_time: float):
        self.intersection_id = intersection_id
        self.position = position
        self.notification_lead_time = notification_lead_time
        
        self.active = False
        self.activation_time = None
        self.affected_crossing = None
    
    def activate(self, crossing_id: str, current_time: float):
        self.active = True
        self.affected_crossing = crossing_id
        self.activation_time = current_time
    
    def deactivate(self):
        self.active = False
        self.activation_time = None
        self.affected_crossing = None


class CrossingState:
    def __init__(self, crossing_id: str, position: tuple):
        self.crossing_id = crossing_id
        self.position = position
        
        self.gate_closed = False
        self.gate_closure_time = None
        self.train_eta = None
        self.countdown_time = None
    
    def close_gate(self, train_eta: float, current_time: float):
        self.gate_closed = True
        self.gate_closure_time = current_time
        self.train_eta = train_eta
        self.countdown_time = train_eta
    
    def update(self, dt: float):
        if self.gate_closed and self.countdown_time is not None:
            self.countdown_time = max(0, self.countdown_time - dt)
    
    def open_gate(self):
        self.gate_closed = False
        self.gate_closure_time = None
        self.train_eta = None
        self.countdown_time = None


class TrafficController:
    def __init__(self, map_config: Dict):
        self.config = load_config()
        self.map_config = map_config
        
        self.notification_lead_time = self.config['simulation']['notification_lead_time']
        
        self.crossings = {}
        self.intersections = {}
        
        self._initialize_crossings()
        self._initialize_intersections()
    
    def _initialize_crossings(self):
        crossings = self.map_config.get('crossings', [])
        for crossing in crossings:
            self.crossings[crossing['name']] = CrossingState(
                crossing['name'],
                (crossing['x'], crossing['y'])
            )
    
    def _initialize_intersections(self):
        intersections = self.map_config.get('intersections', [])
        for inter in intersections:
            self.intersections[inter['name']] = IntersectionNotification(
                inter['name'],
                (inter['x'], inter['y']),
                self.notification_lead_time
            )
    
    def process_train_detection(self, crossing_id: str, train_eta: float, current_time: float):
        if crossing_id not in self.crossings:
            return
        
        crossing = self.crossings[crossing_id]
        gate_closure_offset = self.config['gates']['closure_before_eta']
        
        time_until_closure = train_eta - gate_closure_offset
        
        if time_until_closure <= self.notification_lead_time:
            affected_intersections = self._get_affected_intersections(crossing_id)
            for inter_id in affected_intersections:
                if inter_id in self.intersections:
                    self.intersections[inter_id].activate(crossing_id, current_time)
        
        if time_until_closure <= 0 and not crossing.gate_closed:
            crossing.close_gate(train_eta, current_time)
            return True
        
        return False
    
    def _get_affected_intersections(self, crossing_id: str) -> List[str]:
        mapping = {
            'cross_left': ['inter_tl', 'inter_bl'],
            'cross_right': ['inter_tr', 'inter_br']
        }
        return mapping.get(crossing_id, [])
    
    def open_crossing(self, crossing_id: str):
        if crossing_id in self.crossings:
            self.crossings[crossing_id].open_gate()
            
            affected_intersections = self._get_affected_intersections(crossing_id)
            for inter_id in affected_intersections:
                if inter_id in self.intersections:
                    self.intersections[inter_id].deactivate()
    
    def update(self, dt: float):
        for crossing in self.crossings.values():
            crossing.update(dt)
    
    def is_crossing_closed(self, crossing_id: str) -> bool:
        if crossing_id in self.crossings:
            return self.crossings[crossing_id].gate_closed
        return False
    
    def get_crossing_eta(self, crossing_id: str) -> Optional[float]:
        if crossing_id in self.crossings:
            return self.crossings[crossing_id].train_eta
        return None
    
    def get_crossing_countdown(self, crossing_id: str) -> Optional[float]:
        if crossing_id in self.crossings:
            return self.crossings[crossing_id].countdown_time
        return None
    
    def is_intersection_notified(self, intersection_id: str) -> bool:
        if intersection_id in self.intersections:
            return self.intersections[intersection_id].active
        return False
    
    def get_intersection_affected_crossing(self, intersection_id: str) -> Optional[str]:
        if intersection_id in self.intersections:
            inter = self.intersections[intersection_id]
            return inter.affected_crossing if inter.active else None
        return None
    
    def get_all_closed_crossings(self) -> List[str]:
        return [cid for cid, crossing in self.crossings.items() if crossing.gate_closed]
    
    def reset_crossing(self, crossing_id: str):
        self.open_crossing(crossing_id)