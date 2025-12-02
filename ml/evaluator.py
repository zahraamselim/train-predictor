"""
Model evaluation and results visualization
"""
import json
from pathlib import Path
from utils import get_logger

class ModelEvaluator:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.results_dir = Path(config['output']['results_dir'])
        self.results_dir.mkdir(exist_ok=True)
        
    def evaluate(self, model, features_df, metrics):
        """Evaluate and save results"""
        self.logger.info("Evaluating model performance")
        
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
                'n_features': len([col for col in features_df.columns 
                                  if col not in ['run_id', 'eta_actual', 'eta_physics']]),
                'n_nodes': model.tree_.node_count,
                'max_depth': model.get_depth()
            }
        }
        
        results_path = self.results_dir / 'evaluation_results.json'
        with open(results_path, 'w') as f:
            json.dump(results, indent=2, fp=f)
        
        self.logger.info(f"Results saved to {results_path}")
        
        self.print_summary(results)
    
    def print_summary(self, results):
        """Print evaluation summary"""
        print("\n" + "=" * 60)
        print("MODEL EVALUATION SUMMARY")
        print("=" * 60)
        
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
        print(f"  Max Depth: {info['max_depth']}")
        
        print("=" * 60 + "\n")