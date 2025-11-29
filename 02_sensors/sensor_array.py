"""IR sensor array for train detection."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config


class SensorArray:
    """
    Manages IR sensor array for train detection.
    
    Uses binary detection: sensor triggers when train passes over it.
    Records entry and exit times for speed calculation.
    """
    
    def __init__(self, sensor_positions=None):
        """
        Initialize sensor array.
        
        Args:
            sensor_positions: List of distances from crossing (m)
                Default: Load from config
        """
        config = load_config()
        scale_mode = config['system']['scale_mode']
        train_config = config['train'][f'{scale_mode}_scale']
        
        if sensor_positions is None:
            self.sensor_positions = train_config['sensor_positions']
        else:
            self.sensor_positions = sensor_positions
        
        # State for each sensor: {detected, entry_time, exit_time}
        self.sensor_states = {
            i: {'detected': False, 'entry_time': None, 'exit_time': None}
            for i in range(len(self.sensor_positions))
        }
    
    def update(self, train_distance, current_time, train_length=0):
        """
        Update sensor states based on train position.
        
        Args:
            train_distance: Distance from train front to crossing (m)
            current_time: Current simulation time (s)
            train_length: Length of train (m)
        
        Returns:
            List of detection events [{'sensor_id', 'event', 'time'}]
        """
        events = []
        
        train_front = train_distance
        train_rear = train_distance + train_length
        
        for i, sensor_pos in enumerate(self.sensor_positions):
            # Sensor detects if train is over it
            # Train covers sensor when: train_front <= sensor_pos <= train_rear
            sensor_detecting = (train_front <= sensor_pos <= train_rear)
            
            # Entry event: wasn't detecting, now detecting
            if sensor_detecting and not self.sensor_states[i]['detected']:
                self.sensor_states[i]['detected'] = True
                self.sensor_states[i]['entry_time'] = current_time
                events.append({
                    'sensor_id': i,
                    'event': 'entry',
                    'time': current_time,
                    'position': sensor_pos
                })
            
            # Exit event: was detecting, now not detecting
            elif not sensor_detecting and self.sensor_states[i]['detected']:
                self.sensor_states[i]['detected'] = False
                self.sensor_states[i]['exit_time'] = current_time
                events.append({
                    'sensor_id': i,
                    'event': 'exit',
                    'time': current_time,
                    'position': sensor_pos
                })
        
        return events
    
    def get_detection_times(self):
        """
        Get entry and exit times for all sensors.
        
        Returns:
            Dict: {sensor_id: {position, entry_time, exit_time}}
        """
        result = {}
        for i in range(len(self.sensor_positions)):
            result[f'sensor_{i}'] = {
                'position': self.sensor_positions[i],
                'entry_time': self.sensor_states[i]['entry_time'],
                'exit_time': self.sensor_states[i]['exit_time']
            }
        return result
    
    def calculate_speed(self, sensor1_id, sensor2_id):
        """
        Calculate train speed between two sensors.
        
        Args:
            sensor1_id: Index of first sensor (furthest)
            sensor2_id: Index of second sensor (nearest)
        
        Returns:
            Speed in m/s, or None if insufficient data
        """
        s1 = self.sensor_states[sensor1_id]
        s2 = self.sensor_states[sensor2_id]
        
        if s1['entry_time'] is None or s2['entry_time'] is None:
            return None
        
        time_diff = abs(s2['entry_time'] - s1['entry_time'])
        distance_diff = abs(
            self.sensor_positions[sensor2_id] - self.sensor_positions[sensor1_id]
        )
        
        if time_diff > 0:
            return distance_diff / time_diff
        return None
    
    def reset(self):
        """Reset all sensor states."""
        for i in range(len(self.sensor_positions)):
            self.sensor_states[i] = {
                'detected': False,
                'entry_time': None,
                'exit_time': None
            }