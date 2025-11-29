"""IR sensor array detection logic."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config


class SensorArray:
    """
    IR sensor array for train detection.
    
    Binary detection: sensor triggers when train passes over it.
    Records entry and exit times for speed calculation.
    """
    
    def __init__(self, sensor_positions=None):
        """
        Initialize sensor array.
        
        Args:
            sensor_positions: List of distances from crossing (m), ordered furthest to nearest
                Default: Load from config
        """
        if sensor_positions is None:
            config = load_config()
            scale_mode = config['system']['scale_mode']
            self.sensor_positions = config['train'][f'{scale_mode}_scale']['sensor_positions']
        else:
            self.sensor_positions = sensor_positions
        
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
            List of detection events [{'sensor_id', 'event', 'time', 'position'}]
        """
        events = []
        
        train_front = train_distance
        train_rear = train_distance + train_length
        
        for i, sensor_pos in enumerate(self.sensor_positions):
            sensor_detecting = (train_front <= sensor_pos <= train_rear)
            
            if sensor_detecting and not self.sensor_states[i]['detected']:
                self.sensor_states[i]['detected'] = True
                self.sensor_states[i]['entry_time'] = current_time
                events.append({
                    'sensor_id': i,
                    'event': 'entry',
                    'time': current_time,
                    'position': sensor_pos
                })
            
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


def calculate_sensor_positions(verbose=True):
    """
    Calculate optimal sensor positions based on traffic clearance requirements.
    
    Returns:
        List of sensor positions [furthest, middle, nearest] in meters
    """
    config = load_config()
    scale_mode = config['system']['scale_mode']
    
    vehicle_clearance = config['vehicle_clearance']
    max_clearance = max(
        vehicle_clearance['light']['max_time'],
        vehicle_clearance['medium']['max_time'],
        vehicle_clearance['heavy']['max_time']
    )
    
    gate_closure_offset = config['gates']['closure_before_eta']
    safety_buffer = config['traffic'][f'{scale_mode}_scale']['safety_buffer']
    
    train_types = config['train_types']
    max_train_speed_kmh = max(t['max_speed'] for t in train_types.values())
    max_train_speed_ms = max_train_speed_kmh / 3.6
    
    total_warning_time = max_clearance + safety_buffer + gate_closure_offset
    ideal_detection_distance = max_train_speed_ms * total_warning_time
    
    crossing_distance = config['train'][f'{scale_mode}_scale']['crossing_distance']
    max_sensor_distance = crossing_distance * 0.9
    
    detection_distance = min(ideal_detection_distance, max_sensor_distance)
    
    sensor_positions = [
        round(detection_distance * 1.0, 1),
        round(detection_distance * 0.6, 1),
        round(detection_distance * 0.3, 1)
    ]
    
    if verbose:
        unit = 'cm' if scale_mode == 'demo' else 'm'
        print(f"\nSensor Position Calculation ({scale_mode} scale)")
        print(f"Max clearance time: {max_clearance:.2f}s")
        print(f"Total warning time needed: {total_warning_time:.2f}s")
        print(f"Fastest train speed: {max_train_speed_kmh:.1f} km/h")
        print(f"Detection distance: {detection_distance:.1f}{unit}")
        print(f"Sensor positions: {sensor_positions} {unit}")
        
        actual_warning = detection_distance / max_train_speed_ms
        if actual_warning < total_warning_time:
            print(f"\nWARNING: Actual warning ({actual_warning:.1f}s) < Required ({total_warning_time:.1f}s)")
        else:
            print(f"Warning time adequate: {actual_warning:.1f}s")
    
    return sensor_positions