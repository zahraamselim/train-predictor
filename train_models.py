"""
Train Random Forest models for ETA/ETD prediction
Poster results: ETA MAE=0.031s (R²=0.986), ETD MAE=0.058s (R²=0.99)
Models: ETA (10 trees), ETD (5 trees), 14 features each
Usage: python train_models.py
"""

import pandas as pd
import numpy as np
import pickle
import json
import yaml
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils.logger import Logger


class ModelTrainer:
    def __init__(self, config_path='config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.output_dir = Path('outputs')
        self.plots_dir = self.output_dir / 'plots'
        self.plots_dir.mkdir(parents=True, exist_ok=True)
    
    def load_features(self):
        """Load extracted features"""
        features_path = self.output_dir / 'features.csv'
        
        if not features_path.exists():
            Logger.log(f"ERROR: Features file not found: {features_path}")
            Logger.log("Run: python train_data.py")
            return None
        
        return pd.read_csv(features_path)
    
    def prepare_data(self, features_df, target_col):
        """Split data into train/test sets"""
        # All 14 features (poster version)
        feature_cols = [
            'distance_remaining',
            'train_length',
            'last_speed',
            'speed_change',
            'time_01',
            'time_12',
            'avg_speed_01',
            'avg_speed_12',
            'speed_0',
            'speed_1',
            'accel_01',
            'accel_12',
            'accel_trend',
            'predicted_crossing_speed'
        ]
        
        X = features_df[feature_cols]
        y = features_df[target_col]
        
        test_size = self.config['model']['test_size']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.config['model']['random_state']
        )
        
        return X_train, X_test, y_train, y_test, feature_cols
    
    def train_eta_model(self, X_train, y_train):
        """Train ETA model with Random Forest (10 trees - poster)"""
        Logger.log("\nTraining ETA model (10 trees, 14 features)")
        
        model = RandomForestRegressor(
            n_estimators=self.config['model']['eta_n_estimators'],
            max_depth=self.config['model']['eta_max_depth'],
            min_samples_split=self.config['model']['eta_min_samples_split'],
            min_samples_leaf=self.config['model']['eta_min_samples_leaf'],
            random_state=self.config['model']['random_state'],
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        return model
    
    def train_etd_model(self, X_train, y_train):
        """Train ETD model with Random Forest (5 trees - poster)"""
        Logger.log("\nTraining ETD model (5 trees, 14 features)")
        
        model = RandomForestRegressor(
            n_estimators=self.config['model']['etd_n_estimators'],
            max_depth=self.config['model']['etd_max_depth'],
            min_samples_split=self.config['model']['etd_min_samples_split'],
            min_samples_leaf=self.config['model']['etd_min_samples_leaf'],
            random_state=self.config['model']['random_state'],
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        return model
    
    def evaluate_model(self, model, X_train, X_test, y_train, y_test, features_df, target_col, physics_col, feature_cols):
        """Calculate performance metrics (poster Table 2)"""
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_r2 = r2_score(y_test, y_test_pred)
        
        physics_error = np.mean(np.abs(features_df[target_col] - features_df[physics_col]))
        improvement = ((physics_error - test_mae) / physics_error) * 100
        
        metrics = {
            'train_mae': float(train_mae),
            'test_mae': float(test_mae),
            'test_rmse': float(test_rmse),
            'test_r2': float(test_r2),
            'physics_baseline': float(physics_error),
            'improvement_percent': float(improvement),
            'feature_importances': model.feature_importances_.tolist(),
            'feature_names': feature_cols,
            'n_estimators': model.n_estimators,
            'max_depth': model.max_depth
        }
        
        Logger.log(f"Train MAE: {train_mae:.3f}s")
        Logger.log(f"Test MAE: {test_mae:.3f}s")
        Logger.log(f"Test RMSE: {test_rmse:.3f}s")
        Logger.log(f"Test R²: {test_r2:.3f}")
        Logger.log(f"Physics baseline: {physics_error:.3f}s")
        Logger.log(f"Improvement: {improvement:.1f}%")
        
        return metrics, y_test, y_test_pred
    
    def plot_results(self, eta_metrics, etd_metrics, eta_test, eta_pred, etd_test, etd_pred):
        """Create results visualization (poster Figs 9-12)"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # ETA predictions (Fig 9)
        ax = axes[0, 0]
        ax.scatter(eta_test, eta_pred, alpha=0.5, s=20, color='blue')
        min_val = min(eta_test.min(), eta_pred.min())
        max_val = max(eta_test.max(), eta_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        ax.set_xlabel('Actual ETA (s)')
        ax.set_ylabel('Predicted ETA (s)')
        ax.set_title(f'ETA Test Data (R²={eta_metrics["test_r2"]:.3f})')
        ax.grid(True, alpha=0.3)
        
        # ETD predictions (Fig 10)
        ax = axes[0, 1]
        ax.scatter(etd_test, etd_pred, alpha=0.5, s=20, color='green')
        min_val = min(etd_test.min(), etd_pred.min())
        max_val = max(etd_test.max(), etd_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        ax.set_xlabel('Actual ETD (s)')
        ax.set_ylabel('Predicted ETD (s)')
        ax.set_title(f'ETD Test Data (R²={etd_metrics["test_r2"]:.3f})')
        ax.grid(True, alpha=0.3)
        
        # ETA error distribution (Fig 11)
        ax = axes[0, 2]
        eta_errors = eta_pred - eta_test
        ax.hist(eta_errors, bins=40, edgecolor='black', alpha=0.7, color='blue')
        ax.axvline(0, color='r', linestyle='--', lw=2)
        ax.set_xlabel('Error (s)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'ETA Training Errors (MAE={eta_metrics["test_mae"]:.3f}s)')
        ax.grid(True, alpha=0.3, axis='y')
        
        # ETD error distribution (Fig 12)
        ax = axes[1, 0]
        etd_errors = etd_pred - etd_test
        ax.hist(etd_errors, bins=40, edgecolor='black', alpha=0.7, color='green')
        ax.axvline(0, color='r', linestyle='--', lw=2)
        ax.set_xlabel('Error (s)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'ETD Training Errors (MAE={etd_metrics["test_mae"]:.3f}s)')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Feature importance (ETA)
        ax = axes[1, 1]
        importances = eta_metrics['feature_importances']
        features = eta_metrics['feature_names']
        top_n = 8
        indices = np.argsort(importances)[-top_n:]
        ax.barh(range(top_n), [importances[i] for i in indices], color='blue', alpha=0.7, edgecolor='black')
        ax.set_yticks(range(top_n))
        ax.set_yticklabels([features[i] for i in indices])
        ax.set_xlabel('Importance')
        ax.set_title('ETA Top Features')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Comparison (Table 2 visualization)
        ax = axes[1, 2]
        categories = ['ETA\nPhysics', 'ETA\nRF', 'ETD\nPhysics', 'ETD\nRF']
        values = [
            eta_metrics['physics_baseline'],
            eta_metrics['test_mae'],
            etd_metrics['physics_baseline'],
            etd_metrics['test_mae']
        ]
        colors = ['#ff6b6b', '#51cf66', '#ff6b6b', '#51cf66']
        bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        ax.set_ylabel('MAE (s)')
        ax.set_title('Model Performance')
        ax.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}s', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plot_path = self.plots_dir / 'model_results.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"\nSaved: {plot_path}")
        plt.close()
    
    def save_model(self, model, metrics, filename):
        """Save trained model"""
        model_data = {
            'model': model,
            'metrics': metrics,
            'config': self.config['model'],
            'sklearn_version': __import__('sklearn').__version__
        }
        
        model_path = self.output_dir / filename
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        Logger.log(f"Saved: {model_path}")
    
    def save_results(self, eta_metrics, etd_metrics, features_df):
        """Save evaluation results (poster Table 2)"""
        results = {
            'dataset': {
                'n_samples': len(features_df),
                'eta_mean': float(features_df['eta_actual'].mean()),
                'eta_std': float(features_df['eta_actual'].std()),
                'etd_mean': float(features_df['etd_actual'].mean()),
                'etd_std': float(features_df['etd_actual'].std())
            },
            'eta_model': {
                'type': 'RandomForest',
                'n_estimators': eta_metrics['n_estimators'],
                'max_depth': eta_metrics['max_depth'],
                'n_features': 14,
                'train_mae': eta_metrics['train_mae'],
                'test_mae': eta_metrics['test_mae'],
                'test_rmse': eta_metrics['test_rmse'],
                'test_r2': eta_metrics['test_r2'],
                'physics_baseline': eta_metrics['physics_baseline'],
                'improvement_percent': eta_metrics['improvement_percent']
            },
            'etd_model': {
                'type': 'RandomForest',
                'n_estimators': etd_metrics['n_estimators'],
                'max_depth': etd_metrics['max_depth'],
                'n_features': 14,
                'train_mae': etd_metrics['train_mae'],
                'test_mae': etd_metrics['test_mae'],
                'test_rmse': etd_metrics['test_rmse'],
                'test_r2': etd_metrics['test_r2'],
                'physics_baseline': etd_metrics['physics_baseline'],
                'improvement_percent': etd_metrics['improvement_percent']
            }
        }
        
        results_path = self.output_dir / 'model_results.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        Logger.log(f"Saved: {results_path}")
        
        return results
    
    def print_summary(self, results):
        """Print final summary (poster Table 2)"""
        Logger.log("TRAINING SUMMARY (Poster Results)")
        
        Logger.log(f"\nDataset: {results['dataset']['n_samples']} samples")
        Logger.log(f"ETA mean: {results['dataset']['eta_mean']:.2f}s ± {results['dataset']['eta_std']:.2f}s")
        Logger.log(f"ETD mean: {results['dataset']['etd_mean']:.2f}s ± {results['dataset']['etd_std']:.2f}s")
        
        Logger.log("\nETA Model (Random Forest, 10 trees, 14 features)")
        eta = results['eta_model']
        Logger.log(f"  Test MAE: {eta['test_mae']:.3f}s")
        Logger.log(f"  Test RMSE: {eta['test_rmse']:.3f}s")
        Logger.log(f"  Test R²: {eta['test_r2']:.3f}")
        Logger.log(f"  Physics baseline: {eta['physics_baseline']:.3f}s")
        Logger.log(f"  Improvement: {eta['improvement_percent']:.1f}%")
        
        Logger.log("\nETD Model (Random Forest, 5 trees, 14 features)")
        etd = results['etd_model']
        Logger.log(f"  Test MAE: {etd['test_mae']:.3f}s")
        Logger.log(f"  Test RMSE: {etd['test_rmse']:.3f}s")
        Logger.log(f"  Test R²: {etd['test_r2']:.3f}")
        Logger.log(f"  Physics baseline: {etd['physics_baseline']:.3f}s")
        Logger.log(f"  Improvement: {etd['improvement_percent']:.1f}%")
            
    def train(self):
        """Run complete training pipeline"""
        Logger.section("Training Random Forest models (Poster version)")
        
        features_df = self.load_features()
        if features_df is None:
            return False
        
        Logger.log(f"Loaded {len(features_df)} samples with 14 features each")
        
        # Train ETA model
        X_train, X_test, y_train, y_test, feature_cols = self.prepare_data(features_df, 'eta_actual')
        Logger.log(f"Split: {len(X_train)} train, {len(X_test)} test")
        
        eta_model = self.train_eta_model(X_train, y_train)
        eta_metrics, eta_test, eta_pred = self.evaluate_model(
            eta_model, X_train, X_test, y_train, y_test,
            features_df, 'eta_actual', 'eta_physics', feature_cols
        )
        self.save_model(eta_model, eta_metrics, 'eta_model.pkl')
        
        # Train ETD model
        X_train, X_test, y_train, y_test, feature_cols = self.prepare_data(features_df, 'etd_actual')
        
        etd_model = self.train_etd_model(X_train, y_train)
        etd_metrics, etd_test, etd_pred = self.evaluate_model(
            etd_model, X_train, X_test, y_train, y_test,
            features_df, 'etd_actual', 'etd_physics', feature_cols
        )
        self.save_model(etd_model, etd_metrics, 'etd_model.pkl')
        
        # Save results and visualizations
        results = self.save_results(eta_metrics, etd_metrics, features_df)
        self.plot_results(eta_metrics, etd_metrics, eta_test, eta_pred, etd_test, etd_pred)
        self.print_summary(results)
        
        return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Random Forest models')
    parser.add_argument('--config', default='config.yaml', help='Config file path')
    args = parser.parse_args()
    
    trainer = ModelTrainer(args.config)
    trainer.train()