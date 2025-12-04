"""
Model training and evaluation
Run: python -m ml.model
"""
import pandas as pd
import numpy as np
import pickle
import json
import yaml
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils.logger import Logger


class Model:
    def __init__(self, config_path='ml/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.model_dir = Path('outputs/models')
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.plots_dir = Path('outputs/plots')
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_dir = Path('outputs/results')
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def prepare_data(self, features_df, target_col, use_extended_features=False):
        """Split data into train/validation/test sets"""
        # Base 8 features for ETA
        feature_cols = [
            'distance_remaining', 'train_length', 'last_speed', 'speed_change',
            'time_01', 'time_12', 'avg_speed_01', 'avg_speed_12'
        ]
        
        # Add 2 extra features for ETD (helps predict clearance speed)
        if use_extended_features:
            feature_cols.extend(['accel_trend', 'predicted_speed_at_crossing'])
        
        X = features_df[feature_cols]
        y = features_df[target_col]
        
        test_size = self.config['model']['test_size']
        
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=0.2, random_state=42
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        
        return X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test, feature_cols, scaler
    
    def train_model(self, X_train, y_train, X_val, y_val):
        """Train model with Gradient Boosting"""
        n_estimators = 200
        train_losses = []
        val_losses = []
        train_accs = []
        val_accs = []
        
        model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            learning_rate=0.05,
            max_depth=5,
            min_samples_split=3,
            min_samples_leaf=2,
            subsample=0.9,
            max_features='sqrt',
            random_state=42,
            validation_fraction=0.15,
            n_iter_no_change=15,
            tol=0.00001
        )
        
        model.fit(X_train, y_train)
        
        for i in range(1, n_estimators + 1):
            model_partial = GradientBoostingRegressor(
                n_estimators=i,
                learning_rate=0.05,
                max_depth=5,
                min_samples_split=3,
                min_samples_leaf=2,
                subsample=0.9,
                max_features='sqrt',
                random_state=42
            )
            model_partial.fit(X_train, y_train)
            
            y_train_pred = model_partial.predict(X_train)
            y_val_pred = model_partial.predict(X_val)
            
            train_loss = mean_squared_error(y_train, y_train_pred)
            val_loss = mean_squared_error(y_val, y_val_pred)
            
            train_r2 = r2_score(y_train, y_train_pred)
            val_r2 = r2_score(y_val, y_val_pred)
            
            train_losses.append(train_loss)
            val_losses.append(val_loss)
            train_accs.append(max(0, train_r2))
            val_accs.append(max(0, val_r2))
        
        history = {
            'train_loss': train_losses,
            'val_loss': val_losses,
            'train_acc': train_accs,
            'val_acc': val_accs
        }
        
        return model, history
    
    def plot_training_history(self, history, model_name):
        """Plot training curves"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        epochs = range(1, len(history['train_loss']) + 1)
        
        ax1.plot(epochs, history['train_loss'], 'b-', label='Train', linewidth=2)
        ax1.plot(epochs, history['val_loss'], 'orange', label='Validation', linewidth=2)
        ax1.set_xlabel('Epoch', fontsize=12)
        ax1.set_ylabel('Loss', fontsize=12)
        ax1.set_title('Loss', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(epochs, history['train_acc'], 'b-', label='Train', linewidth=2)
        ax2.plot(epochs, history['val_acc'], 'orange', label='Validation', linewidth=2)
        ax2.set_xlabel('Epoch', fontsize=12)
        ax2.set_ylabel('Accuracy', fontsize=12)
        ax2.set_title('Accuracy', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = self.plots_dir / f'{model_name.lower()}_history.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved: {plot_path}")
        plt.close()
    
    def evaluate_model(self, model, scaler, X_train, X_val, X_test, y_train, y_val, y_test, 
                      features_df, target_col, physics_col):
        """Calculate performance metrics"""
        y_train_pred = model.predict(X_train)
        y_val_pred = model.predict(X_val)
        y_test_pred = model.predict(X_test)
        
        train_error = mean_absolute_error(y_train, y_train_pred)
        val_error = mean_absolute_error(y_val, y_val_pred)
        test_error = mean_absolute_error(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_r2 = r2_score(y_test, y_test_pred)
        
        physics_error = np.mean(np.abs(features_df[target_col] - features_df[physics_col]))
        improvement = ((physics_error - test_error) / physics_error) * 100
        
        metrics = {
            'train_error': float(train_error),
            'val_error': float(val_error),
            'test_error': float(test_error),
            'test_rmse': float(test_rmse),
            'test_r2': float(test_r2),
            'physics_error': float(physics_error),
            'improvement': float(improvement),
            'train_predictions': y_train_pred,
            'val_predictions': y_val_pred,
            'test_predictions': y_test_pred,
            'train_actual': y_train.values,
            'val_actual': y_val.values,
            'test_actual': y_test.values
        }
        
        Logger.log(f"Train error: {train_error:.3f}s")
        Logger.log(f"Val error: {val_error:.3f}s")
        Logger.log(f"Test error: {test_error:.3f}s")
        Logger.log(f"R² score: {test_r2:.3f}")
        Logger.log(f"Physics baseline: {physics_error:.3f}s")
        Logger.log(f"Improvement: {improvement:.1f}%")
        
        return metrics
    
    def plot_results(self, metrics, model_name, feature_cols, model, scaler):
        """Create visualization plots"""
        fig = plt.figure(figsize=(16, 10))
        
        train_r2 = r2_score(metrics['train_actual'], metrics['train_predictions'])
        
        ax1 = plt.subplot(2, 3, 1)
        ax1.scatter(metrics['train_actual'], metrics['train_predictions'], alpha=0.5, s=20)
        min_val = min(metrics['train_actual'].min(), metrics['train_predictions'].min())
        max_val = max(metrics['train_actual'].max(), metrics['train_predictions'].max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect prediction')
        ax1.set_xlabel('Actual Time (seconds)', fontsize=11)
        ax1.set_ylabel('Predicted Time (seconds)', fontsize=11)
        ax1.set_title(f'{model_name} - Training Data\nR² = {train_r2:.3f}', 
                     fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2 = plt.subplot(2, 3, 2)
        ax2.scatter(metrics['test_actual'], metrics['test_predictions'], alpha=0.5, s=20, color='green')
        min_val = min(metrics['test_actual'].min(), metrics['test_predictions'].min())
        max_val = max(metrics['test_actual'].max(), metrics['test_predictions'].max())
        ax2.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect prediction')
        ax2.set_xlabel('Actual Time (seconds)', fontsize=11)
        ax2.set_ylabel('Predicted Time (seconds)', fontsize=11)
        ax2.set_title(f'{model_name} - Test Data\nMAE = {metrics["test_error"]:.3f}s', 
                     fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        ax3 = plt.subplot(2, 3, 3)
        errors = metrics['test_predictions'] - metrics['test_actual']
        ax3.hist(errors, bins=30, edgecolor='black', alpha=0.7)
        ax3.axvline(0, color='r', linestyle='--', lw=2, label='Zero error')
        ax3.set_xlabel('Prediction Error (seconds)', fontsize=11)
        ax3.set_ylabel('Frequency', fontsize=11)
        ax3.set_title(f'Error Distribution\nMean = {errors.mean():.3f}s, Std = {errors.std():.3f}s', 
                     fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        ax4 = plt.subplot(2, 3, 4)
        importances = model.feature_importances_
        colors = ['green' if imp > np.median(importances) else 'orange' for imp in importances]
        ax4.barh(range(len(feature_cols)), importances, color=colors, alpha=0.7)
        ax4.set_yticks(range(len(feature_cols)))
        ax4.set_yticklabels(feature_cols, fontsize=9)
        ax4.set_xlabel('Feature Importance', fontsize=11)
        ax4.set_title('Feature Importance\n(higher = more important)', 
                     fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='x')
        
        ax5 = plt.subplot(2, 3, 5)
        categories = ['Physics\nBaseline', f'{model_name}\nModel']
        errors_bar = [metrics['physics_error'], metrics['test_error']]
        bars = ax5.bar(categories, errors_bar, color=['#ff6b6b', '#51cf66'], 
                      alpha=0.7, edgecolor='black', linewidth=2)
        ax5.set_ylabel('Mean Absolute Error (seconds)', fontsize=11)
        ax5.set_title(f'Model Performance\nImprovement: {metrics["improvement"]:.1f}%', 
                     fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}s',
                    ha='center', va='bottom', fontweight='bold')
        
        ax6 = plt.subplot(2, 3, 6)
        ax6.scatter(metrics['test_predictions'], errors, alpha=0.5, s=20)
        ax6.axhline(0, color='r', linestyle='--', lw=2)
        ax6.set_xlabel('Predicted Time (seconds)', fontsize=11)
        ax6.set_ylabel('Residual Error (seconds)', fontsize=11)
        ax6.set_title('Residual Plot\n(should be random around zero)', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        plot_path = self.plots_dir / f'{model_name.lower()}_training.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved: {plot_path}")
        plt.close()
    
    def save_model(self, model, scaler, feature_cols, metrics, filename):
        """Save model to file"""
        metrics_to_save = {k: v for k, v in metrics.items() 
                          if k not in ['train_predictions', 'val_predictions', 'test_predictions', 
                                      'train_actual', 'val_actual', 'test_actual']}
        
        model_data = {
            'model': model,
            'scaler': scaler,
            'feature_cols': feature_cols,
            'metrics': metrics_to_save
        }
        
        model_path = self.model_dir / filename
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        Logger.log(f"Saved: {model_path}")
    
    def save_evaluation(self, eta_metrics, etd_metrics, features_df):
        """Save evaluation results"""
        results = {
            'eta_metrics': {k: v for k, v in eta_metrics.items() 
                          if k not in ['train_predictions', 'val_predictions', 'test_predictions', 
                                      'train_actual', 'val_actual', 'test_actual']},
            'etd_metrics': {k: v for k, v in etd_metrics.items() 
                          if k not in ['train_predictions', 'val_predictions', 'test_predictions', 
                                      'train_actual', 'val_actual', 'test_actual']},
            'dataset_stats': {
                'n_samples': len(features_df),
                'eta_mean': float(features_df['eta_actual'].mean()),
                'eta_std': float(features_df['eta_actual'].std()),
                'etd_mean': float(features_df['etd_actual'].mean()),
                'etd_std': float(features_df['etd_actual'].std())
            },
            'model_info': {
                'type': 'GradientBoosting',
                'eta_features': 8,
                'etd_features': 10,
                'n_estimators': 200
            }
        }
        
        results_path = self.results_dir / 'evaluation_results.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        Logger.log(f"Saved: {results_path}")
        
        return results
    
    def print_summary(self, results):
        """Print evaluation summary"""
        print("\n" + "="*50)
        print("MODEL EVALUATION SUMMARY")
        print("="*50)
        
        print("\nDataset:")
        stats = results['dataset_stats']
        print(f"  Total samples: {stats['n_samples']}")
        print(f"  ETA average: {stats['eta_mean']:.2f}s (±{stats['eta_std']:.2f}s)")
        print(f"  ETD average: {stats['etd_mean']:.2f}s (±{stats['etd_std']:.2f}s)")
        
        print("\nETA Model (Time Until Train Arrives):")
        metrics = results['eta_metrics']
        print(f"  Features: {results['model_info']['eta_features']}")
        print(f"  Test error: {metrics['test_error']:.3f}s")
        print(f"  R² score: {metrics['test_r2']:.3f}")
        print(f"  Physics baseline: {metrics['physics_error']:.3f}s")
        print(f"  Improvement: {metrics['improvement']:.1f}%")
        
        print("\nETD Model (Time Until Train Clears):")
        metrics = results['etd_metrics']
        print(f"  Features: {results['model_info']['etd_features']} (includes accel_trend + predicted_speed)")
        print(f"  Test error: {metrics['test_error']:.3f}s")
        print(f"  R² score: {metrics['test_r2']:.3f}")
        print(f"  Physics baseline: {metrics['physics_error']:.3f}s")
        print(f"  Improvement: {metrics['improvement']:.1f}%")
        
        print("\nModel Structure:")
        print(f"  Type: {results['model_info']['type']}")
        print(f"  Trees: {results['model_info']['n_estimators']}")
        print()
    
    def train(self, features_path=None):
        """Train and evaluate both models"""
        if features_path is None:
            features_path = Path('outputs/data/features.csv')
        
        Logger.section("Training and evaluating models")
        
        if not Path(features_path).exists():
            Logger.log(f"Features file not found: {features_path}")
            return None
        
        features_df = pd.read_csv(features_path)
        
        Logger.log("\nTraining ETA model (8 features)")
        X_train, X_val, X_test, y_train, y_val, y_test, feature_cols, scaler = self.prepare_data(
            features_df, 'eta_actual', use_extended_features=False
        )
        Logger.log(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        eta_model, eta_history = self.train_model(X_train, y_train, X_val, y_val)
        self.plot_training_history(eta_history, 'ETA')
        
        eta_metrics = self.evaluate_model(
            eta_model, scaler, X_train, X_val, X_test, y_train, y_val, y_test,
            features_df, 'eta_actual', 'eta_physics'
        )
        self.plot_results(eta_metrics, 'ETA', feature_cols, eta_model, scaler)
        self.save_model(eta_model, scaler, feature_cols, eta_metrics, 'eta_model.pkl')
        
        Logger.log("\nTraining ETD model (10 features - includes acceleration prediction)")
        X_train, X_val, X_test, y_train, y_val, y_test, feature_cols, scaler = self.prepare_data(
            features_df, 'etd_actual', use_extended_features=True
        )
        
        etd_model, etd_history = self.train_model(X_train, y_train, X_val, y_val)
        self.plot_training_history(etd_history, 'ETD')
        
        etd_metrics = self.evaluate_model(
            etd_model, scaler, X_train, X_val, X_test, y_train, y_val, y_test,
            features_df, 'etd_actual', 'etd_physics'
        )
        self.plot_results(etd_metrics, 'ETD', feature_cols, etd_model, scaler)
        self.save_model(etd_model, scaler, feature_cols, etd_metrics, 'etd_model.pkl')
        
        results = self.save_evaluation(eta_metrics, etd_metrics, features_df)
        self.print_summary(results)
        
        return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train and evaluate models')
    parser.add_argument('--input', help='Input features CSV file')
    parser.add_argument('--config', default='ml/config.yaml', help='Config file path')
    args = parser.parse_args()
    
    model = Model(args.config)
    model.train(args.input)