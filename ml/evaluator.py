"""
Evaluate and save model results
Run: python -m ml.evaluator
"""
import json
import pickle
import pandas as pd
import yaml
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from utils.logger import Logger

class ModelEvaluator:
    def __init__(self, config_path='config/ml.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.results_dir = Path('outputs/results')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def evaluate(self, features_path=None):
        """Evaluate and save results"""
        if features_path is None:
            features_path = Path('outputs/data/features.csv')
        
        Logger.section("Evaluating model performance")
        
        eta_path = Path('outputs/models/eta_model.pkl')
        etd_path = Path('outputs/models/etd_model.pkl')
        
        if not eta_path.exists():
            Logger.log(f"ETA model not found: {eta_path}")
            return None
        
        if not etd_path.exists():
            Logger.log(f"ETD model not found: {etd_path}")
            return None
        
        if not features_path.exists():
            Logger.log(f"Features file not found: {features_path}")
            return None
        
        with open(eta_path, 'rb') as f:
            eta_data = pickle.load(f)
        
        with open(etd_path, 'rb') as f:
            etd_data = pickle.load(f)
        
        features_df = pd.read_csv(features_path)
        
        eta_model = eta_data['model']
        etd_model = etd_data['model']
        
        results = {
            'eta_metrics': eta_data['metrics'],
            'etd_metrics': etd_data['metrics'],
            'dataset_stats': {
                'n_samples': len(features_df),
                'eta_mean': float(features_df['eta_actual'].mean()),
                'eta_std': float(features_df['eta_actual'].std()),
                'eta_min': float(features_df['eta_actual'].min()),
                'eta_max': float(features_df['eta_actual'].max()),
                'etd_mean': float(features_df['etd_actual'].mean()),
                'etd_std': float(features_df['etd_actual'].std()),
                'etd_min': float(features_df['etd_actual'].min()),
                'etd_max': float(features_df['etd_actual'].max())
            },
            'model_info': {
                'eta': {
                    'type': type(eta_model).__name__,
                    'n_features': len(eta_data['feature_cols']),
                    'n_trees': len(eta_model.estimators_)
                },
                'etd': {
                    'type': type(etd_model).__name__,
                    'n_features': len(etd_data['feature_cols']),
                    'n_trees': len(etd_model.estimators_)
                }
            }
        }
        
        results_path = self.results_dir / 'evaluation_results.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        Logger.log(f"Results saved to {results_path}")
        
        self.print_summary(results)
        
        return results
    
    def print_summary(self, results):
        """Print evaluation summary"""
        print("\nModel Evaluation Summary")
        
        print("\nDataset Statistics:")
        stats = results['dataset_stats']
        print(f"  Samples: {stats['n_samples']}")
        print(f"  ETA Mean: {stats['eta_mean']:.2f}s, Std: {stats['eta_std']:.2f}s")
        print(f"  ETA Range: [{stats['eta_min']:.2f}s, {stats['eta_max']:.2f}s]")
        print(f"  ETD Mean: {stats['etd_mean']:.2f}s, Std: {stats['etd_std']:.2f}s")
        print(f"  ETD Range: [{stats['etd_min']:.2f}s, {stats['etd_max']:.2f}s]")
        
        print("\nETA Model Performance:")
        metrics = results['eta_metrics']
        print(f"  Test MAE: {metrics['test_mae']:.3f}s")
        print(f"  Test RMSE: {metrics['test_rmse']:.3f}s")
        print(f"  Test R2: {metrics['test_r2']:.3f}")
        print(f"  Physics baseline: {metrics['physics_baseline_mae']:.3f}s")
        print(f"  Improvement: {metrics['improvement_over_physics']:.1f}%")
        
        print("\nETD Model Performance:")
        metrics = results['etd_metrics']
        print(f"  Test MAE: {metrics['test_mae']:.3f}s")
        print(f"  Test RMSE: {metrics['test_rmse']:.3f}s")
        print(f"  Test R2: {metrics['test_r2']:.3f}")
        print(f"  Physics baseline: {metrics['physics_baseline_mae']:.3f}s")
        print(f"  Improvement: {metrics['improvement_over_physics']:.1f}%")
        
        print("\nModel Info:")
        print("  ETA:")
        info = results['model_info']['eta']
        print(f"    Type: {info['type']}")
        print(f"    Features: {info['n_features']}")
        print(f"    Trees: {info['n_trees']}")
        
        print("  ETD:")
        info = results['model_info']['etd']
        print(f"    Type: {info['type']}")
        print(f"    Features: {info['n_features']}")
        print(f"    Trees: {info['n_trees']}\n")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate trained models')
    parser.add_argument('--features', help='Features CSV file')
    parser.add_argument('--config', default='config/ml.yaml', help='Config file path')
    args = parser.parse_args()
    
    evaluator = ModelEvaluator(args.config)
    evaluator.evaluate(args.features)