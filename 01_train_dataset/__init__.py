"""
Train Dataset Generation Module

Generates realistic train approach data for level crossing prediction.
"""

from .train_types import TrainType, TRAIN_TYPES
from .train_physics import TrainPhysics
from .train_simulator import TrainSimulator
from .generate_dataset import generate_dataset

__all__ = [
    'TrainType',
    'TRAIN_TYPES',
    'TrainPhysics',
    'TrainSimulator',
    'generate_dataset'
]