"""
Train ETA and ETD prediction models
Run: python -m ml.model_trainer
"""
import pandas as pd
import numpy as np
import pickle
import yaml
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils.logger import Logger

class ModelTrainer:
    def __init__(self, config_path='config/ml.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.model_dir = Path('outputs/models')
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
    def prepare_data(self, features_df, target_col):
        """Prepare train/val/test splits"""
        feature_cols = [col for col in features_df.columns 
                       if col not in ['run_id', 'eta_actual', 'etd_actual', 'eta_physics', 'etd_physics']]
        
        X = features_df[feature_cols]
        y = features_df[target_col]
        
        test_size = self.config['model']['test_size']
        val_size = self.config['model']['val_size']
        
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=42
        )
        
        return X_train, X_val, X_test, y_train, y_val, y_test, feature_cols
    
    def train_model(self, X_train, y_train, X_val, y_val, model_type='eta'):
        """Train model with hyperparameter search"""
        best_mae = float('inf')
        best_model = None
        best_params = None
        
        for n_trees in [5, 10, 15]:
            for depth in range(4, 10):
                for min_leaf in [5, 8, 10]:
                    model = RandomForestRegressor(
                        n_estimators=n_trees,
                        max_depth=depth,
                        min_samples_leaf=min_leaf,
                        random_state=42,
                        n_jobs=-1
                    )
                    
                    model.fit(X_train, y_train)
                    y_val_pred = model.predict(X_val)
                    mae = mean_absolute_error(y_val, y_val_pred)
                    
                    if mae < best_mae:
                        best_mae = mae
                        best_model = model
                        best_params = {'n_trees': n_trees, 'depth': depth, 'min_leaf': min_leaf}
        
        Logger.log(f"Best params: n_trees={best_params['n_trees']}, depth={best_params['depth']}, min_leaf={best_params['min_leaf']}, val MAE={best_mae:.3f}s")
        
        return best_model
    
    def evaluate_model(self, model, X_test, y_test, X_train, y_train, features_df, target_col, physics_col):
        """Evaluate model performance"""
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_r2 = r2_score(y_test, y_test_pred)
        
        physics_mae = np.mean(np.abs(features_df[target_col] - features_df[physics_col]))
        
        metrics = {
            'train_mae': float(train_mae),
            'test_mae': float(test_mae),
            'test_rmse': float(test_rmse),
            'test_r2': float(test_r2),
            'physics_baseline_mae': float(physics_mae),
            'improvement_over_physics': float(((physics_mae - test_mae) / physics_mae) * 100)
        }
        
        Logger.log(f"Train MAE: {train_mae:.3f}s")
        Logger.log(f"Test MAE: {test_mae:.3f}s")
        Logger.log(f"Test RMSE: {test_rmse:.3f}s")
        Logger.log(f"Test R2: {test_r2:.3f}")
        Logger.log(f"Physics baseline: {physics_mae:.3f}s")
        Logger.log(f"Improvement: {metrics['improvement_over_physics']:.1f}%")
        
        return metrics
    
    def save_model(self, model, feature_cols, metrics, filename):
        """Save trained model and metadata"""
        model_data = {
            'model': model,
            'feature_cols': feature_cols,
            'metrics': metrics,
            'config': self.config
        }
        
        model_path = self.model_dir / filename
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        Logger.log(f"Model saved to {model_path}")
    
    def train(self, features_path=None):
        """Execute full training pipeline"""
        if features_path is None:
            features_path = Path('outputs/data/features.csv')
        
        Logger.section("Training ETA and ETD prediction models")
        
        if not Path(features_path).exists():
            Logger.log(f"Features file not found: {features_path}")
            return None
        
        features_df = pd.read_csv(features_path)
        
        Logger.log("Training ETA model")
        X_train, X_val, X_test, y_train, y_val, y_test, feature_cols = self.prepare_data(
            features_df, 'eta_actual'
        )
        Logger.log(f"Data split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
        
        eta_model = self.train_model(X_train, y_train, X_val, y_val, 'eta')
        eta_metrics = self.evaluate_model(
            eta_model, X_test, y_test, X_train, y_train, 
            features_df, 'eta_actual', 'eta_physics'
        )
        self.save_model(eta_model, feature_cols, eta_metrics, 'eta_model.pkl')
        
        Logger.log("")
        Logger.log("Training ETD model")
        X_train, X_val, X_test, y_train, y_val, y_test, feature_cols = self.prepare_data(
            features_df, 'etd_actual'
        )
        
        etd_model = self.train_model(X_train, y_train, X_val, y_val, 'etd')
        etd_metrics = self.evaluate_model(
            etd_model, X_test, y_test, X_train, y_train,
            features_df, 'etd_actual', 'etd_physics'
        )
        self.save_model(etd_model, feature_cols, etd_metrics, 'etd_model.pkl')
        
        return {'eta': (eta_model, eta_metrics), 'etd': (etd_model, etd_metrics)}

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train ETA and ETD prediction models')
    parser.add_argument('--input', help='Input features CSV file')
    parser.add_argument('--config', default='config/ml.yaml', help='Config file path')
    args = parser.parse_args()
    
    trainer = ModelTrainer(args.config)
    trainer.train(args.input)