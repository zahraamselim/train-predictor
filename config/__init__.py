"""
Configuration management for level crossing system.
"""

from .utils import (
    load_config,
    save_config,
    get_scale_config,
    get_unit,
    update_vehicle_clearance,
    set_scale_mode
)

__all__ = [
    'load_config',
    'save_config',
    'get_scale_config',
    'get_unit',
    'update_vehicle_clearance',
    'set_scale_mode'
]