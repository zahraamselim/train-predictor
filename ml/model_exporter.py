"""
Model export for Arduino and Python deployment
"""
import pickle
from pathlib import Path
from utils import get_logger

class ModelExporter:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.model_dir = Path(config['output']['model_dir'])
        
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
    
    def export_arduino(self, model):
        """Export model as Arduino header file"""
        self.logger.info("Exporting Arduino header")
        
        model_path = self.model_dir / self.config['output']['python_model']
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        tree = model_data['model'].tree_
        feature_cols = model_data['feature_cols']
        
        arduino_code = self.generate_arduino_code(tree, feature_cols)
        
        output_path = self.model_dir / self.config['output']['arduino_header']
        output_path.write_text(arduino_code)
        
        self.logger.info(f"Arduino header saved to {output_path}")
        self.logger.info(f"Model size: {len(feature_cols)} features, {tree.node_count} nodes")
    
    def export_python(self, model):
        """Python model already saved during training"""
        self.logger.info("Python model export complete")