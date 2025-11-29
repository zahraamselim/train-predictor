"""IR sensor simulation module for train approach detection."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config


class IRSensorArray:
    """Manages IR sensor placement and detection events."""
    
    def __init__(self, sensor_positions: list = None, detection_threshold: float = None):
        """
        Args:
            sensor_positions: List of distances from crossing where sensors are placed
            detection_threshold: Distance within which sensor detects train (m)
        """
        config = load_config()
        ir_config = config['ir_sensors']
        self.sensor_positions = sensor_positions or ir_config['sensor_positions']
        self.detection_threshold = detection_threshold or ir_config.get('detection_threshold', 5.0)
        
        self.sensor_states = {
            i: {'detected': False, 'entry_time': None, 'exit_time': None} 
            for i in range(len(self.sensor_positions))
        }
    
    def get_sensor_positions(self):
        """Get sensor positions."""
        return self.sensor_positions
    
    def update_sensors(self, train_distance: float, current_time: float, 
                      train_length: float = 0) -> dict:
        """
        Update sensor detection states based on train position.
        
        Args:
            train_distance: Distance from train front to crossing
            current_time: Current simulation time
            train_length: Length of train (to detect when rear passes)
        
        Returns:
            Dictionary of sensor detection states and events
        """
        events = []
        
        for i, sensor_pos in enumerate(self.sensor_positions):
            train_front = train_distance
            train_rear = train_distance + train_length
            
            sensor_detecting = (train_front <= sensor_pos <= train_rear)
            
            if sensor_detecting and not self.sensor_states[i]['detected']:
                self.sensor_states[i]['detected'] = True
                self.sensor_states[i]['entry_time'] = current_time
                events.append({
                    'sensor_id': i,
                    'event': 'entry',
                    'time': current_time,
                    'train_distance': train_distance
                })
            
            elif not sensor_detecting and self.sensor_states[i]['detected']:
                self.sensor_states[i]['detected'] = False
                self.sensor_states[i]['exit_time'] = current_time
                events.append({
                    'sensor_id': i,
                    'event': 'exit',
                    'time': current_time,
                    'train_distance': train_distance
                })
        
        return {
            'states': [self.sensor_states[i]['detected'] 
                      for i in range(len(self.sensor_positions))],
            'events': events
        }
    
    def get_detection_times(self):
        """
        Get entry and exit times for all sensors.
        
        Returns:
            Dictionary with sensor detection timing data
        """
        result = {}
        for i in range(len(self.sensor_positions)):
            result[f'sensor_{i}'] = {
                'position': self.sensor_positions[i],
                'entry_time': self.sensor_states[i]['entry_time'],
                'exit_time': self.sensor_states[i]['exit_time']
            }
        return result
    
    def calculate_speed_between_sensors(self, sensor1_idx: int, 
                                       sensor2_idx: int) -> float:
        """
        Calculate train speed between two sensors.
        
        Args:
            sensor1_idx: Index of first sensor
            sensor2_idx: Index of second sensor
        
        Returns:
            Speed in m/s (or None if not enough data)
        """
        s1 = self.sensor_states[sensor1_idx]
        s2 = self.sensor_states[sensor2_idx]
        
        if s1['entry_time'] is None or s2['entry_time'] is None:
            return None
        
        time_diff = abs(s2['entry_time'] - s1['entry_time'])
        distance_diff = abs(
            self.sensor_positions[sensor2_idx] - self.sensor_positions[sensor1_idx]
        )
        
        if time_diff > 0:
            return distance_diff / time_diff
        return None
    
    def reset(self):
        """Reset all sensor states."""
        self.sensor_states = {
            i: {'detected': False, 'entry_time': None, 'exit_time': None} 
            for i in range(len(self.sensor_positions))
        }