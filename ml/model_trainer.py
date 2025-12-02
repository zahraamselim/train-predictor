"""
Model training module
"""
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils import get_logger

class ModelTrainer:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.model_dir = Path(config['output']['model_dir'])
        self.model_dir.mkdir(exist_ok=True)
        
    def prepare_data(self, features_df):
        """Prepare train/val/test splits"""
        feature_cols = [col for col in features_df.columns 
                       if col not in ['run_id', 'eta_actual', 'eta_physics']]
        
        X = features_df[feature_cols]
        y = features_df['eta_actual']
        
        test_size = self.config['model']['test_size']
        val_size = self.config['model']['val_size']
        
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=42
        )
        
        self.logger.info(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test, feature_cols
    
    def train_model(self, X_train, y_train, X_val, y_val):
        """Train decision tree with hyperparameter search"""
        depth_range = self.config['model']['max_depth_range']
        min_samples = self.config['model']['min_samples_split']
        
        best_mae = float('inf')
        best_model = None
        best_depth = None
        
        for depth in range(depth_range[0], depth_range[1] + 1):
            model = DecisionTreeRegressor(
                max_depth=depth, 
                min_samples_split=min_samples, 
                random_state=42
            )
            model.fit(X_train, y_train)
            
            y_val_pred = model.predict(X_val)
            mae = mean_absolute_error(y_val, y_val_pred)
            
            if mae < best_mae:
                best_mae = mae
                best_model = model
                best_depth = depth
        
        self.logger.info(f"Best model: max_depth={best_depth}, validation MAE={best_mae:.3f}s")
        
        return best_model, best_depth
    
    def evaluate_model(self, model, X_test, y_test, X_train, y_train, features_df):
        """Evaluate model performance"""
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_r2 = r2_score(y_test, y_test_pred)
        
        physics_mae = np.mean(np.abs(features_df['eta_actual'] - features_df['eta_physics']))
        
        metrics = {
            'train_mae': train_mae,
            'test_mae': test_mae,
            'test_rmse': test_rmse,
            'test_r2': test_r2,
            'physics_baseline_mae': physics_mae,
            'improvement_over_physics': ((physics_mae - test_mae) / physics_mae) * 100
        }
        
        self.logger.info(f"Train MAE: {train_mae:.3f}s")
        self.logger.info(f"Test MAE: {test_mae:.3f}s")
        self.logger.info(f"Test RMSE: {test_rmse:.3f}s")
        self.logger.info(f"Test R2: {test_r2:.3f}")
        self.logger.info(f"Physics baseline MAE: {physics_mae:.3f}s")
        self.logger.info(f"Improvement over physics: {metrics['improvement_over_physics']:.1f}%")
        
        return metrics
    
    def save_model(self, model, feature_cols, metrics):
        """Save trained model and metadata"""
        model_data = {
            'model': model,
            'feature_cols': feature_cols,
            'metrics': metrics
        }
        
        model_path = self.model_dir / self.config['output']['python_model']
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        self.logger.info(f"Model saved to {model_path}")
    
    def train(self, features_df):
        """Execute full training pipeline"""
        self.logger.info("Starting model training")
        
        X_train, X_val, X_test, y_train, y_val, y_test, feature_cols = self.prepare_data(features_df)
        
        model, best_depth = self.train_model(X_train, y_train, X_val, y_val)
        
        metrics = self.evaluate_model(model, X_test, y_test, X_train, y_train, features_df)
        
        self.save_model(model, feature_cols, metrics)
        
        return model, metrics