"""
Validation Module

Validates outputs and integrity of all project modules.
"""

from .validate_traffic import (
    validate_traffic_dataset,
    validate_vehicle_clearance_times,
    validate_sensor_positions
)

from .validate_train import (
    validate_train_dataset,
    validate_sensor_configuration,
    validate_train_speeds
)

from .validate_model import (
    validate_model_weights,
    validate_arduino_code,
    validate_model_performance,
    validate_plots,
    validate_training_data_compatibility
)

__all__ = [
    'validate_traffic_dataset',
    'validate_vehicle_clearance_times',
    'validate_sensor_positions',
    'validate_train_dataset',
    'validate_sensor_configuration',
    'validate_train_speeds',
    'validate_model_weights',
    'validate_arduino_code',
    'validate_model_performance',
    'validate_plots',
    'validate_training_data_compatibility'
]