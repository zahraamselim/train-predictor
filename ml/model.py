"""
Model training and evaluation with statistical rigor
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
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scipy import stats
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
        
        model_config = self.config.get('model', {})
        hyperparams = model_config.get('hyperparameters', {})
        
        self.hyperparameters = {
            'n_estimators': hyperparams.get('n_estimators', 200),
            'learning_rate': hyperparams.get('learning_rate', 0.05),
            'max_depth': hyperparams.get('max_depth', 4),  # Fixed: was 5
            'min_samples_split': hyperparams.get('min_samples_split', 3),
            'min_samples_leaf': hyperparams.get('min_samples_leaf', 2),
            'subsample': hyperparams.get('subsample', 0.9),
            'max_features': hyperparams.get('max_features', 'sqrt'),
            'validation_fraction': hyperparams.get('validation_fraction', 0.15),
            'n_iter_no_change': hyperparams.get('n_iter_no_change', 15),
            'tol': hyperparams.get('tol', 0.00001),
            'random_state': hyperparams.get('random_state', 42)
        }
    
    def prepare_data(self, features_df, target_col, use_extended_features=False):
        """Split data into train/validation/test sets"""
        feature_cols = [
            'distance_remaining', 'train_length', 'last_speed', 'speed_change',
            'time_01', 'time_12', 'avg_speed_01', 'avg_speed_12'
        ]
        
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
        train_losses = []
        val_losses = []
        train_r2s = []
        val_r2s = []
        
        model = GradientBoostingRegressor(**self.hyperparameters)
        model.fit(X_train, y_train)
        
        for i in range(1, self.hyperparameters['n_estimators'] + 1):
            model_partial = GradientBoostingRegressor(
                n_estimators=i,
                learning_rate=self.hyperparameters['learning_rate'],
                max_depth=self.hyperparameters['max_depth'],
                min_samples_split=self.hyperparameters['min_samples_split'],
                min_samples_leaf=self.hyperparameters['min_samples_leaf'],
                subsample=self.hyperparameters['subsample'],
                max_features=self.hyperparameters['max_features'],
                random_state=self.hyperparameters['random_state']
            )
            model_partial.fit(X_train, y_train)
            
            y_train_pred = model_partial.predict(X_train)
            y_val_pred = model_partial.predict(X_val)
            
            train_losses.append(mean_squared_error(y_train, y_train_pred))
            val_losses.append(mean_squared_error(y_val, y_val_pred))
            train_r2s.append(max(0, r2_score(y_train, y_train_pred)))
            val_r2s.append(max(0, r2_score(y_val, y_val_pred)))
        
        history = {
            'train_loss': train_losses,
            'val_loss': val_losses,
            'train_r2': train_r2s,
            'val_r2': val_r2s
        }
        
        return model, history
    
    def calculate_confidence_intervals(self, errors, confidence=0.95):
        """Calculate confidence intervals for prediction errors"""
        n = len(errors)
        mean_error = np.mean(errors)
        std_error = np.std(errors, ddof=1)
        se = std_error / np.sqrt(n)
        t_critical = stats.t.ppf((1 + confidence) / 2, df=n-1)
        margin = t_critical * se
        
        return {
            'mean': mean_error,
            'std': std_error,
            'se': se,
            'margin': margin,
            'ci_lower': mean_error - margin,
            'ci_upper': mean_error + margin,
            'confidence': confidence
        }
    
    def cross_validate_model(self, X, y, cv=5):
        """Perform k-fold cross-validation"""
        model = GradientBoostingRegressor(**self.hyperparameters)
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring='neg_mean_absolute_error')
        cv_maes = -cv_scores
        
        return {
            'cv_scores': cv_maes,
            'cv_mean': np.mean(cv_maes),
            'cv_std': np.std(cv_maes),
            'cv_min': np.min(cv_maes),
            'cv_max': np.max(cv_maes)
        }
    
    def plot_training_history(self, history, model_name):
        """Plot training curves"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        epochs = range(1, len(history['train_loss']) + 1)
        
        ax1.plot(epochs, history['train_loss'], 'b-', label='Train', linewidth=2)
        ax1.plot(epochs, history['val_loss'], 'orange', label='Validation', linewidth=2)
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Mean Squared Error')
        ax1.set_title(f'{model_name} Training Loss')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')
        
        ax2.plot(epochs, history['train_r2'], 'b-', label='Train', linewidth=2)
        ax2.plot(epochs, history['val_r2'], 'orange', label='Validation', linewidth=2)
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('R2 Score')
        ax2.set_title(f'{model_name} Model Accuracy')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([0, 1.05])
        
        plt.tight_layout()
        plot_path = self.plots_dir / f'{model_name.lower()}_history.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved: {plot_path}")
        plt.close()
    
    def evaluate_model(self, model, scaler, X_train, X_val, X_test, y_train, y_val, y_test, 
                      features_df, target_col, physics_col, feature_cols):
        """Calculate comprehensive performance metrics"""
        y_train_pred = model.predict(X_train)
        y_val_pred = model.predict(X_val)
        y_test_pred = model.predict(X_test)
        
        train_error = mean_absolute_error(y_train, y_train_pred)
        val_error = mean_absolute_error(y_val, y_val_pred)
        test_error = mean_absolute_error(y_test, y_test_pred)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        test_r2 = r2_score(y_test, y_test_pred)
        
        train_errors = np.abs(y_train - y_train_pred)
        test_errors = np.abs(y_test - y_test_pred)
        
        train_ci = self.calculate_confidence_intervals(train_errors)
        test_ci = self.calculate_confidence_intervals(test_errors)
        
        physics_error = np.mean(np.abs(features_df[target_col] - features_df[physics_col]))
        improvement = ((physics_error - test_error) / physics_error) * 100
        
        X_combined = np.vstack([X_train, X_val])
        y_combined = pd.concat([y_train, y_val])
        cv_results = self.cross_validate_model(X_combined, y_combined, cv=5)
        
        metrics = {
            'train_error': float(train_error),
            'val_error': float(val_error),
            'test_error': float(test_error),
            'test_rmse': float(test_rmse),
            'test_r2': float(test_r2),
            'physics_error': float(physics_error),
            'improvement': float(improvement),
            'train_ci': {k: float(v) if isinstance(v, (np.floating, float)) else v 
                        for k, v in train_ci.items()},
            'test_ci': {k: float(v) if isinstance(v, (np.floating, float)) else v 
                       for k, v in test_ci.items()},
            'cv_mean': float(cv_results['cv_mean']),
            'cv_std': float(cv_results['cv_std']),
            'cv_scores': [float(x) for x in cv_results['cv_scores']],
            'train_predictions': y_train_pred,
            'val_predictions': y_val_pred,
            'test_predictions': y_test_pred,
            'train_actual': y_train.values,
            'val_actual': y_val.values,
            'test_actual': y_test.values,
            'feature_importances': model.feature_importances_.tolist(),
            'feature_names': feature_cols
        }
        
        Logger.log(f"Train MAE: {train_error:.3f}s +/- {train_ci['margin']:.3f}s (95% CI)")
        Logger.log(f"Test MAE: {test_error:.3f}s +/- {test_ci['margin']:.3f}s (95% CI)")
        Logger.log(f"Test RMSE: {test_rmse:.3f}s")
        Logger.log(f"Test R2: {test_r2:.3f}")
        Logger.log(f"CV MAE: {cv_results['cv_mean']:.3f}s +/- {cv_results['cv_std']:.3f}s")
        Logger.log(f"Physics baseline: {physics_error:.3f}s")
        Logger.log(f"Improvement: {improvement:.1f}%")
        
        return metrics
    
    def plot_comprehensive_results(self, metrics, model_name):
        """Create comprehensive visualization with 9 subplots"""
        fig = plt.figure(figsize=(18, 14))
        
        train_r2 = r2_score(metrics['train_actual'], metrics['train_predictions'])
        test_r2 = metrics['test_r2']
        
        ax1 = plt.subplot(3, 3, 1)
        ax1.scatter(metrics['train_actual'], metrics['train_predictions'], 
                   alpha=0.5, s=20, c='blue', edgecolors='none')
        min_val = min(metrics['train_actual'].min(), metrics['train_predictions'].min())
        max_val = max(metrics['train_actual'].max(), metrics['train_predictions'].max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        ax1.set_xlabel('Actual (s)')
        ax1.set_ylabel('Predicted (s)')
        ax1.set_title(f'Training Set\nR2 = {train_r2:.4f}')
        ax1.grid(True, alpha=0.3)
        
        ax2 = plt.subplot(3, 3, 2)
        ax2.scatter(metrics['test_actual'], metrics['test_predictions'], 
                   alpha=0.5, s=20, c='green', edgecolors='none')
        min_val = min(metrics['test_actual'].min(), metrics['test_predictions'].min())
        max_val = max(metrics['test_actual'].max(), metrics['test_predictions'].max())
        ax2.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        test_mae = metrics['test_error']
        test_ci = metrics['test_ci']['margin']
        ax2.set_xlabel('Actual (s)')
        ax2.set_ylabel('Predicted (s)')
        ax2.set_title(f'Test Set\nMAE = {test_mae:.3f}s +/- {test_ci:.3f}s')
        ax2.grid(True, alpha=0.3)
        
        ax3 = plt.subplot(3, 3, 3)
        errors = metrics['test_predictions'] - metrics['test_actual']
        ax3.hist(errors, bins=40, edgecolor='black', alpha=0.7, color='steelblue')
        ax3.axvline(0, color='r', linestyle='--', lw=2, label='Zero error')
        mean_err = errors.mean()
        std_err = errors.std()
        ax3.axvline(mean_err, color='orange', linestyle='--', lw=2, label=f'Mean = {mean_err:.3f}s')
        ax3.set_xlabel('Error (s)')
        ax3.set_ylabel('Frequency')
        ax3.set_title(f'Error Distribution\nStd = {std_err:.3f}s')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        ax4 = plt.subplot(3, 3, 4)
        importances = metrics['feature_importances']
        features = metrics['feature_names']
        colors = ['green' if imp > np.median(importances) else 'orange' for imp in importances]
        y_pos = np.arange(len(features))
        ax4.barh(y_pos, importances, color=colors, alpha=0.7, edgecolor='black')
        ax4.set_yticks(y_pos)
        ax4.set_yticklabels(features)
        ax4.set_xlabel('Importance')
        ax4.set_title('Feature Importance')
        ax4.grid(True, alpha=0.3, axis='x')
        
        ax5 = plt.subplot(3, 3, 5)
        categories = ['Physics\nBaseline', f'{model_name}\nModel']
        errors = [metrics['physics_error'], metrics['test_error']]
        bars = ax5.bar(categories, errors, color=['#ff6b6b', '#51cf66'], 
                      alpha=0.7, edgecolor='black', linewidth=2)
        ax5.errorbar([1], [metrics['test_error']], 
                    yerr=[metrics['test_ci']['margin']], 
                    fmt='none', color='black', capsize=10, capthick=2)
        ax5.set_ylabel('MAE (s)')
        ax5.set_title(f'Performance\n{metrics["improvement"]:.1f}% Better')
        ax5.grid(True, alpha=0.3, axis='y')
        for bar, err in zip(bars, errors):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{err:.3f}s', ha='center', va='bottom', fontweight='bold')
        
        ax6 = plt.subplot(3, 3, 6)
        test_residuals = metrics['test_predictions'] - metrics['test_actual']
        ax6.scatter(metrics['test_predictions'], test_residuals, alpha=0.5, s=20, c='purple')
        ax6.axhline(0, color='r', linestyle='--', lw=2)
        std_resid = test_residuals.std()
        ax6.axhline(std_resid, color='orange', linestyle=':', lw=1.5, alpha=0.7)
        ax6.axhline(-std_resid, color='orange', linestyle=':', lw=1.5, alpha=0.7)
        pred_min, pred_max = metrics['test_predictions'].min(), metrics['test_predictions'].max()
        ax6.fill_between([pred_min, pred_max], -std_resid, std_resid, 
                        alpha=0.2, color='orange')
        ax6.set_xlabel('Predicted (s)')
        ax6.set_ylabel('Residual (s)')
        ax6.set_title('Residual Plot')
        ax6.grid(True, alpha=0.3)
        
        ax7 = plt.subplot(3, 3, 7)
        cv_scores = metrics['cv_scores']
        ax7.bar(range(1, len(cv_scores)+1), cv_scores, color='teal', alpha=0.7, 
               edgecolor='black')
        ax7.axhline(metrics['cv_mean'], color='r', linestyle='--', lw=2, 
                   label=f'Mean = {metrics["cv_mean"]:.3f}s')
        ax7.set_xlabel('Fold')
        ax7.set_ylabel('MAE (s)')
        ax7.set_title(f'5-Fold Cross-Validation\nStd = {metrics["cv_std"]:.3f}s')
        ax7.legend()
        ax7.grid(True, alpha=0.3, axis='y')
        
        ax8 = plt.subplot(3, 3, 8)
        stats.probplot(errors, dist="norm", plot=ax8)
        ax8.set_title('Q-Q Plot')
        ax8.grid(True, alpha=0.3)
        
        ax9 = plt.subplot(3, 3, 9)
        ax9.axis('off')
        
        table_data = [
            ['Metric', 'Value'],
            ['Train MAE', f'{metrics["train_error"]:.3f}s'],
            ['Test MAE', f'{metrics["test_error"]:.3f}s'],
            ['Test RMSE', f'{metrics["test_rmse"]:.3f}s'],
            ['Test R2', f'{metrics["test_r2"]:.4f}'],
            ['95% CI', f'+/-{metrics["test_ci"]["margin"]:.3f}s'],
            ['CV MAE', f'{metrics["cv_mean"]:.3f}s'],
            ['CV Std', f'{metrics["cv_std"]:.3f}s'],
            ['Improvement', f'{metrics["improvement"]:.1f}%'],
        ]
        
        table = ax9.table(cellText=table_data, cellLoc='left', loc='center',
                         colWidths=[0.6, 0.4])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        for i in range(2):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax9.set_title(f'{model_name} Performance Summary', pad=20)
        
        plt.tight_layout()
        plot_path = self.plots_dir / f'{model_name.lower()}_comprehensive.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        Logger.log(f"Saved: {plot_path}")
        plt.close()
    
    def save_model(self, model, scaler, feature_cols, metrics, filename):
        """Save model with metadata"""
        metrics_to_save = {k: v for k, v in metrics.items() 
                          if k not in ['train_predictions', 'val_predictions', 'test_predictions', 
                                      'train_actual', 'val_actual', 'test_actual']}
        
        model_data = {
            'model': model,
            'scaler': scaler,
            'feature_cols': feature_cols,
            'metrics': metrics_to_save,
            'hyperparameters': self.hyperparameters,
            'sklearn_version': __import__('sklearn').__version__,
            'training_date': pd.Timestamp.now().isoformat()
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
            'hyperparameters': self.hyperparameters,
            'model_info': {
                'type': 'GradientBoosting',
                'eta_features': 8,
                'etd_features': 10,
            }
        }
        
        results_path = self.results_dir / 'evaluation_results.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        Logger.log(f"Saved: {results_path}")
        
        return results
    
    def print_summary(self, results):
        """Print evaluation summary"""
        Logger.log("\nML MODEL EVALUATION SUMMARY")
        Logger.log("\nDataset Statistics")
        stats = results['dataset_stats']
        Logger.log(f"Total samples: {stats['n_samples']}")
        Logger.log(f"ETA: {stats['eta_mean']:.2f}s +/- {stats['eta_std']:.2f}s")
        Logger.log(f"ETD: {stats['etd_mean']:.2f}s +/- {stats['etd_std']:.2f}s")
        
        Logger.log("\nHyperparameters")
        for key, value in results['hyperparameters'].items():
            Logger.log(f"  {key}: {value}")
        
        Logger.log("\nETA Model (Time Until Train Arrives)")
        eta = results['eta_metrics']
        Logger.log(f"Features: {results['model_info']['eta_features']}")
        Logger.log(f"Test MAE: {eta['test_error']:.3f}s +/- {eta['test_ci']['margin']:.3f}s (95% CI)")
        Logger.log(f"Test RMSE: {eta['test_rmse']:.3f}s")
        Logger.log(f"Test R2: {eta['test_r2']:.4f}")
        Logger.log(f"Cross-Val MAE: {eta['cv_mean']:.3f}s +/- {eta['cv_std']:.3f}s")
        Logger.log(f"Physics baseline: {eta['physics_error']:.3f}s")
        Logger.log(f"Improvement: {eta['improvement']:.1f}%")
        
        Logger.log("\nETD Model (Time Until Train Clears)")
        etd = results['etd_metrics']
        Logger.log(f"Features: {results['model_info']['etd_features']}")
        Logger.log(f"Test MAE: {etd['test_error']:.3f}s +/- {etd['test_ci']['margin']:.3f}s (95% CI)")
        Logger.log(f"Test RMSE: {etd['test_rmse']:.3f}s")
        Logger.log(f"Test R2: {etd['test_r2']:.4f}")
        Logger.log(f"Cross-Val MAE: {etd['cv_mean']:.3f}s +/- {etd['cv_std']:.3f}s")
        Logger.log(f"Physics baseline: {etd['physics_error']:.3f}s")
        Logger.log(f"Improvement: {etd['improvement']:.1f}%")
    
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
        Logger.log(f"Split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
        
        eta_model, eta_history = self.train_model(X_train, y_train, X_val, y_val)
        self.plot_training_history(eta_history, 'ETA')
        
        eta_metrics = self.evaluate_model(
            eta_model, scaler, X_train, X_val, X_test, y_train, y_val, y_test,
            features_df, 'eta_actual', 'eta_physics', feature_cols
        )
        self.plot_comprehensive_results(eta_metrics, 'ETA')
        self.save_model(eta_model, scaler, feature_cols, eta_metrics, 'eta_model.pkl')
        
        Logger.log("\nTraining ETD model (10 features)")
        X_train, X_val, X_test, y_train, y_val, y_test, feature_cols, scaler = self.prepare_data(
            features_df, 'etd_actual', use_extended_features=True
        )
        
        etd_model, etd_history = self.train_model(X_train, y_train, X_val, y_val)
        self.plot_training_history(etd_history, 'ETD')
        
        etd_metrics = self.evaluate_model(
            etd_model, scaler, X_train, X_val, X_test, y_train, y_val, y_test,
            features_df, 'etd_actual', 'etd_physics', feature_cols
        )
        self.plot_comprehensive_results(etd_metrics, 'ETD')
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