"""
Evaluate and save model results
Run: python -m ml.evaluator
"""
import json
import pickle
import pandas as pd
import yaml
from pathlib import Path
from utils.logger import Logger

class ModelEvaluator:
    def __init__(self, config_path='config/ml.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.results_dir = Path('outputs/results')
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def evaluate(self, model_path=None, features_path=None):
        """Evaluate and save results"""
        if model_path is None:
            model_path = Path('outputs/models/eta_model.pkl')
        if features_path is None:
            features_path = Path('outputs/data/features.csv')
        
        Logger.section("Evaluating model performance")
        
        if not model_path.exists():
            Logger.log(f"Model file not found: {model_path}")
            return None
        
        if not features_path.exists():
            Logger.log(f"Features file not found: {features_path}")
            return None
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data['model']
        metrics = model_data['metrics']
        features_df = pd.read_csv(features_path)
        
        results = {
            'metrics': metrics,
            'dataset_stats': {
                'n_samples': len(features_df),
                'eta_mean': float(features_df['eta_actual'].mean()),
                'eta_std': float(features_df['eta_actual'].std()),
                'eta_min': float(features_df['eta_actual'].min()),
                'eta_max': float(features_df['eta_actual'].max())
            },
            'model_info': {
                'type': 'DecisionTreeRegressor',
                'n_features': len(model_data['feature_cols']),
                'n_nodes': model.tree_.node_count,
                'max_depth': model.get_depth()
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
        print(f"  ETA Mean: {stats['eta_mean']:.2f}s")
        print(f"  ETA Std: {stats['eta_std']:.2f}s")
        print(f"  ETA Range: [{stats['eta_min']:.2f}s, {stats['eta_max']:.2f}s]")
        
        print("\nModel Performance:")
        metrics = results['metrics']
        print(f"  Test MAE: {metrics['test_mae']:.3f}s")
        print(f"  Test RMSE: {metrics['test_rmse']:.3f}s")
        print(f"  Test R2: {metrics['test_r2']:.3f}")
        
        print("\nBaseline Comparison:")
        print(f"  Physics MAE: {metrics['physics_baseline_mae']:.3f}s")
        print(f"  ML Improvement: {metrics['improvement_over_physics']:.1f}%")
        
        print("\nModel Info:")
        info = results['model_info']
        print(f"  Features: {info['n_features']}")
        print(f"  Tree Nodes: {info['n_nodes']}")
        print(f"  Max Depth: {info['max_depth']}\n")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate trained model')
    parser.add_argument('--model', help='Model pickle file')
    parser.add_argument('--features', help='Features CSV file')
    parser.add_argument('--config', default='config/ml.yaml', help='Config file path')
    args = parser.parse_args()
    
    evaluator = ModelEvaluator(args.config)
    evaluator.evaluate(args.model, args.features)