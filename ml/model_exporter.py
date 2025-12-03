"""
Export trained models for Arduino deployment
Run: python -m ml.model_exporter
"""
import pickle
import yaml
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from utils.logger import Logger

class ModelExporter:
    def __init__(self, config_path='config/ml.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.model_dir = Path('outputs/models')
        self.arduino_dir = Path('outputs/arduino')
        
    def generate_tree_code(self, tree, feature_cols, func_name, node_id=0, indent="    "):
        """Recursively generate decision tree code"""
        if tree.children_left[node_id] == tree.children_right[node_id]:
            value = tree.value[node_id][0][0]
            return f"{indent}return {value:.4f}f;\n"
        
        feature_idx = tree.feature[node_id]
        threshold = tree.threshold[node_id]
        left_child = tree.children_left[node_id]
        right_child = tree.children_right[node_id]
        
        code = f"{indent}if (features[{feature_idx}] <= {threshold:.4f}f) {{\n"
        code += self.generate_tree_code(tree, feature_cols, func_name, left_child, indent + "    ")
        code += f"{indent}}} else {{\n"
        code += self.generate_tree_code(tree, feature_cols, func_name, right_child, indent + "    ")
        code += f"{indent}}}\n"
        
        return code
    
    def generate_arduino_code(self, model, feature_cols, func_name):
        """Generate C code for model"""
        feature_comment = "\\n * ".join([f"[{i}] {col}" for i, col in enumerate(feature_cols)])
        
        if isinstance(model, RandomForestRegressor):
            n_trees = len(model.estimators_)
            trees_code = ""
            for i, tree_model in enumerate(model.estimators_):
                tree = tree_model.tree_
                tree_body = self.generate_tree_code(tree, feature_cols, f"{func_name}_tree{i}")
                trees_code += f"""
float {func_name}_tree{i}(float features[{len(feature_cols)}]) {{
{tree_body}}}
"""
            
            ensemble_body = "    float sum = 0.0f;\n"
            for i in range(n_trees):
                ensemble_body += f"    sum += {func_name}_tree{i}(features);\n"
            ensemble_body += f"    return sum / {n_trees}.0f;\n"
            
            code = f"""
/*
 * {func_name.upper()} Prediction Model
 * Auto-generated from random forest ({n_trees} trees)
 * 
 * Feature indices:
 * {feature_comment}
 */
{trees_code}
float {func_name}(float features[{len(feature_cols)}]) {{
{ensemble_body}}}
"""
        
        return code
    
    def export(self):
        """Export both ETA and ETD models as Arduino header file"""
        Logger.section("Exporting models for Arduino")
        
        eta_path = self.model_dir / 'eta_model.pkl'
        etd_path = self.model_dir / 'etd_model.pkl'
        
        if not eta_path.exists():
            Logger.log(f"ETA model not found: {eta_path}")
            return False
        
        if not etd_path.exists():
            Logger.log(f"ETD model not found: {etd_path}")
            return False
        
        with open(eta_path, 'rb') as f:
            eta_data = pickle.load(f)
        
        with open(etd_path, 'rb') as f:
            etd_data = pickle.load(f)
        
        eta_model = eta_data['model']
        eta_features = eta_data['feature_cols']
        
        etd_model = etd_data['model']
        etd_features = etd_data['feature_cols']
        
        eta_code = self.generate_arduino_code(eta_model, eta_features, 'predictETA')
        etd_code = self.generate_arduino_code(etd_model, etd_features, 'predictETD')
        
        header = f"""#ifndef TRAIN_MODELS_H
#define TRAIN_MODELS_H
{eta_code}
{etd_code}
#endif
"""
        
        output_path = self.arduino_dir / 'train_models.h'
        output_path.write_text(header)
        
        Logger.log(f"Arduino header saved to {output_path}")
        Logger.log(f"ETA model: {len(eta_features)} features, {len(eta_model.estimators_)} trees")
        Logger.log(f"ETD model: {len(etd_features)} features, {len(etd_model.estimators_)} trees")
        
        return True

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export models for Arduino')
    parser.add_argument('--config', default='config/ml.yaml', help='Config file path')
    args = parser.parse_args()
    
    exporter = ModelExporter(args.config)
    exporter.export()