"""
Model Training Module

Trains and evaluates regression models for train ETA prediction.
Supports linear and polynomial regression with Arduino code generation.
"""

from .train_model import (
    load_train_data,
    prepare_features,
    train_linear_model,
    train_polynomial_model,
    compare_models,
    plot_predictions,
    save_model_weights,
    generate_arduino_code
)

__all__ = [
    'load_train_data',
    'prepare_features',
    'train_linear_model',
    'train_polynomial_model',
    'compare_models',
    'plot_predictions',
    'save_model_weights',
    'generate_arduino_code'
]