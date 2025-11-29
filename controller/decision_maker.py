"""Core decision logic for level crossing system."""

from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config


class CrossingController:
    """
    Main controller for level crossing notification system.
    Coordinates gate control and intersection notifications.
    """
    
    def __init__(self):
        """Initialize controller with system configuration."""
        config = load_config()
        scale_mode = config['system']['scale_mode']
        
        self.gate_closure_offset = config['gates']['closure_before_eta']
        self.safety_buffer = config['traffic'][f'{scale_mode}_scale']['safety_buffer']
        self.clearance_times = config['vehicle_clearance']
        
        self.gates_closed = False
        self.notifications_sent = []
        self.train_detected = False
        self.current_eta = None
    
    def process_sensor_detection(self, sensor_timings: Dict[str, float], eta: float) -> Dict:
        """
        Process sensor detection and make decisions.
        
        Args:
            sensor_timings: Detection times from sensors
            eta: Calculated ETA in seconds
        
        Returns:
            Dict with decisions: close_gates, notify_intersections, warnings
        """
        self.train_detected = True
        self.current_eta = eta
        
        decisions = {
            'close_gates': False,
            'notify_intersections': [],
            'warnings': [],
            'eta': eta,
            'time_to_gate_closure': eta - self.gate_closure_offset
        }
        
        if eta <= self.gate_closure_offset:
            decisions['close_gates'] = True
            if not self.gates_closed:
                decisions['warnings'].append(f"Gates closing - ETA {eta:.1f}s")
                self.gates_closed = True
        
        gate_closure_time = eta - self.gate_closure_offset
        max_clearance = self.clearance_times['heavy']['max_time']
        notification_threshold = gate_closure_time - max_clearance - self.safety_buffer
        
        if notification_threshold > 0:
            decisions['notify_intersections'] = ['all']
            decisions['notification_lead_time'] = notification_threshold
        else:
            decisions['warnings'].append(
                f"WARNING: Insufficient clearance time ({notification_threshold:.1f}s)"
            )
        
        return decisions
    
    def reset(self):
        """Reset controller state after train passes."""
        self.gates_closed = False
        self.notifications_sent = []
        self.train_detected = False
        self.current_eta = None


class SafetyValidator:
    """Validate system safety constraints."""
    
    def __init__(self):
        config = load_config()
        scale_mode = config['system']['scale_mode']
        
        self.gate_closure_offset = config['gates']['closure_before_eta']
        self.safety_buffer = config['traffic'][f'{scale_mode}_scale']['safety_buffer']
        self.clearance_times = config['vehicle_clearance']
    
    def validate_notification_timing(self, train_eta: float, notification_time: float,
                                    traffic_density: str, intersection_distance: float) -> Dict:
        """
        Validate notification timing provides safe clearance.
        
        Returns:
            Dict with validation result and safety margins
        """
        max_clearance = self.clearance_times[traffic_density]['max_time']
        gate_closure_time = train_eta - self.gate_closure_offset
        time_available = gate_closure_time - notification_time
        time_required = max_clearance + self.safety_buffer
        safety_margin = time_available - time_required
        
        return {
            'is_safe': safety_margin >= 0,
            'safety_margin': round(safety_margin, 2),
            'time_available': round(time_available, 2),
            'time_required': round(time_required, 2),
            'max_clearance': max_clearance,
            'notification_time': notification_time,
            'gate_closure_time': gate_closure_time
        }
    
    def check_system_constraints(self, sensor_positions: List[float],
                                 crossing_distance: float, max_train_speed: float) -> Dict:
        """
        Check if system configuration meets safety requirements.
        
        Returns:
            Dict with constraint check results
        """
        max_speed_ms = max_train_speed / 3.6
        furthest_sensor = max(sensor_positions)
        warning_time = furthest_sensor / max_speed_ms
        
        max_clearance = max(
            self.clearance_times['light']['max_time'],
            self.clearance_times['medium']['max_time'],
            self.clearance_times['heavy']['max_time']
        )
        required_time = max_clearance + self.safety_buffer + self.gate_closure_offset
        
        return {
            'warning_time_available': round(warning_time, 2),
            'warning_time_required': round(required_time, 2),
            'meets_requirements': warning_time >= required_time,
            'shortfall': round(required_time - warning_time, 2) if warning_time < required_time else 0
        }