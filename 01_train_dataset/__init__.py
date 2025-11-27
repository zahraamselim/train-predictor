"""
Train Dataset Generation Module

Generates realistic train approach data for level crossing prediction.
"""

from .train_types import TrainType, TRAIN_TYPES
from .train_physics import TrainPhysics
from .train_simulator import TrainSimulator
from .generate_dataset import generate_dataset
from .train_visualization import TrainVisualization
from .visualize_dataset import generate_dataset, print_sample_scenarios

__all__ = [
    'TrainType',
    'TRAIN_TYPES',
    'TrainPhysics',
    'TrainSimulator',
    'generate_dataset',
    'TrainVisualization',
    'generate_dataset',
    'print_sample_scenarios'
]
