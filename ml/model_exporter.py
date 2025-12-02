"""
Export trained model for Arduino deployment
Run: python -m ml.model_exporter
"""
import pickle
import yaml
from pathlib import Path
from utils.logger import Logger

class ModelExporter:
    def __init__(self, config_path='config/ml.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.model_dir = Path('outputs/models')
        
    def generate_arduino_code(self, tree, feature_cols):
        """Generate C code for Arduino deployment"""
        
        def generate_node(node_id, indent="    "):
            """Recursively generate decision tree code"""
            if tree.children_left[node_id] == tree.children_right[node_id]:
                value = tree.value[node_id][0][0]
                return f"{indent}return {value:.4f}f;\n"
            
            feature_idx = tree.feature[node_id]
            threshold = tree.threshold[node_id]
            left_child = tree.children_left[node_id]
            right_child = tree.children_right[node_id]
            
            code = f"{indent}if (features[{feature_idx}] <= {threshold:.4f}f) {{\n"
            code += generate_node(left_child, indent + "    ")
            code += f"{indent}}} else {{\n"
            code += generate_node(right_child, indent + "    ")
            code += f"{indent}}}\n"
            
            return code
        
        feature_comment = "\\n * ".join([f"[{i}] {col}" for i, col in enumerate(feature_cols)])
        
        header = f"""#ifndef ETA_MODEL_H
#define ETA_MODEL_H

/*
 * Train ETA Prediction Model
 * Auto-generated from decision tree
 * 
 * Feature indices:
 * {feature_comment}
 */

float predictETA(float features[{len(feature_cols)}]) {{
{generate_node(0)}}}

#endif
"""
        
        return header
    
    def export(self, model_path=None):
        """Export model as Arduino header file"""
        if model_path is None:
            model_path = self.model_dir / 'eta_model.pkl'
        
        Logger.section("Exporting model for Arduino")
        
        if not Path(model_path).exists():
            Logger.log(f"Model file not found: {model_path}")
            return False
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        tree = model_data['model'].tree_
        feature_cols = model_data['feature_cols']
        
        arduino_code = self.generate_arduino_code(tree, feature_cols)
        
        output_path = self.model_dir / 'eta_model.h'
        output_path.write_text(arduino_code)
        
        Logger.log(f"Arduino header saved to {output_path}")
        Logger.log(f"Model size: {len(feature_cols)} features, {tree.node_count} nodes")
        
        return True

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export model for Arduino')
    parser.add_argument('--input', help='Input model pickle file')
    parser.add_argument('--config', default='config/ml.yaml', help='Config file path')
    args = parser.parse_args()
    
    exporter = ModelExporter(args.config)
    exporter.export(args.input)