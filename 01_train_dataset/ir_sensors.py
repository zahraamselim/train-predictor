"""
IR sensor simulation module for train approach detection.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import load_config


class IRSensorArray:
    """Manages IR sensor placement and readings."""
    
    def __init__(self, sensor_positions: list = None, sensor_constant: float = None, saturation_distance: float = None):
        """
        Args:
            sensor_positions: List of distances from crossing where sensors are placed
            sensor_constant: Calibration constant K for inverse square law
            saturation_distance: Distance below which sensor saturates (m)
        """
        config = load_config()
        ir_config = config['ir_sensors']
        self.sensor_positions = sensor_positions or ir_config['sensor_positions']
        self.sensor_constant = sensor_constant or ir_config['sensor_constant']
        self.saturation_distance = saturation_distance or ir_config.get('saturation_distance', 0.1)
        self.noise_factors = ir_config['noise_factors']
    
    def get_sensor_positions(self):
        """Get sensor positions."""
        return self.sensor_positions
    
    def simulate_reading(self, distance: float, weather: str) -> float:
        """
        Simulate IR sensor reading with realistic noise.
        Uses inverse square law: IR intensity = K / distance^2
        
        Args:
            distance: Distance from sensor to train
            weather: 'clear', 'rain', or 'fog'
        
        Returns:
            IR sensor reading in arbitrary units
        """
        if distance <= self.saturation_distance:
            return self.sensor_constant
        
        base_reading = self.sensor_constant / (distance ** 2)
        noise_std = base_reading * self.noise_factors.get(weather, 0.05)
        noise = np.random.normal(0, noise_std)
        
        return max(0, base_reading + noise)
    
    def get_readings(self, train_distance: float, weather: str) -> list:
        """
        Get all sensor readings for current train position.
        
        Args:
            train_distance: Distance from train to crossing
            weather: 'clear', 'rain', or 'fog'
        
        Returns:
            List of [IR1, IR2, IR3] readings
        """
        readings = []
        for sensor_pos in self.sensor_positions:
            sensor_distance = abs(train_distance - sensor_pos)
            sensor_distance = max(sensor_distance, self.saturation_distance)
            reading = self.simulate_reading(sensor_distance, weather)
            readings.append(round(reading, 4))
        return readings