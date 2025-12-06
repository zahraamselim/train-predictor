"""
Export trained models for Arduino deployment with quantization
Run: python -m hardware.exporters.model
"""
import pickle
import numpy as np
from pathlib import Path
from utils.logger import Logger


class ModelExporter:
    def __init__(self):
        self.model_dir = Path('outputs/models')
        self.hardware_dir = Path('hardware')
        self.hardware_dir.mkdir(exist_ok=True)
    
    def quantize_value(self, value, min_val, max_val):
        """Quantize float to int16 range"""
        if max_val == min_val:
            return 0
        normalized = (value - min_val) / (max_val - min_val)
        return int(normalized * 32767)
    
    def extract_tree_nodes(self, tree, feature_mins, feature_maxs, value_min, value_max):
        """Extract and quantize tree nodes"""
        n_nodes = tree.node_count
        children_left = tree.children_left
        children_right = tree.children_right
        feature = tree.feature
        threshold = tree.threshold
        value = tree.value
        
        nodes = []
        for i in range(n_nodes):
            if children_left[i] == children_right[i]:
                leaf_value = value[i][0][0]
                nodes.append({
                    'feature_idx': -1,
                    'threshold': 0,
                    'value': self.quantize_value(leaf_value, value_min, value_max),
                    'left_idx': 0,
                    'right_idx': 0
                })
            else:
                feat_idx = feature[i]
                thresh = threshold[i]
                nodes.append({
                    'feature_idx': feat_idx,
                    'threshold': self.quantize_value(thresh, feature_mins[feat_idx], feature_maxs[feat_idx]),
                    'value': 0,
                    'left_idx': children_left[i],
                    'right_idx': children_right[i]
                })
        
        return nodes
    
    def get_depth(self, tree, node_id):
        """Get depth of tree from given node"""
        if tree.children_left[node_id] == tree.children_right[node_id]:
            return 0
        left_depth = self.get_depth(tree, tree.children_left[node_id])
        right_depth = self.get_depth(tree, tree.children_right[node_id])
        return 1 + max(left_depth, right_depth)
    
    def generate_header(self, model_data, model_name, max_trees=50, max_depth=4):
        """Generate Arduino header with quantized model"""
        model = model_data['model']
        scaler = model_data['scaler']
        feature_cols = model_data['feature_cols']
        
        # Get feature statistics for quantization
        feature_means = scaler.mean_
        feature_stds = scaler.scale_
        feature_mins = feature_means - 3 * feature_stds
        feature_maxs = feature_means + 3 * feature_stds
        
        # Get value range for quantization
        all_predictions = []
        for estimator in model.estimators_[:max_trees, 0]:
            all_predictions.extend(estimator.tree_.value[:, 0, 0])
        value_min = min(all_predictions)
        value_max = max(all_predictions)
        
        # Extract trees with depth limit
        all_tree_nodes = []
        max_nodes_per_tree = 0
        
        for estimator in model.estimators_[:max_trees, 0]:
            tree = estimator.tree_
            tree_depth = self.get_depth(tree, 0)
            
            if tree_depth > max_depth:
                continue
            
            nodes = self.extract_tree_nodes(tree, feature_mins, feature_maxs, value_min, value_max)
            all_tree_nodes.append(nodes)
            max_nodes_per_tree = max(max_nodes_per_tree, len(nodes))
        
        actual_n_trees = len(all_tree_nodes)
        
        if actual_n_trees == 0:
            Logger.log(f"WARNING: No trees found with depth <= {max_depth}")
            Logger.log(f"Try increasing --depth parameter")
            return "", 0
        
        if actual_n_trees < len(model.estimators_[:max_trees, 0]):
            filtered = len(model.estimators_[:max_trees, 0]) - actual_n_trees
            Logger.log(f"Filtered {filtered} trees due to depth constraint")
        
        # Generate C header
        header = f"""#ifndef {model_name.upper()}_MODEL_H
#define {model_name.upper()}_MODEL_H

#include <avr/pgmspace.h>

// Model: {model_name.upper()}
// Trees: {actual_n_trees}
// Max nodes per tree: {max_nodes_per_tree}
// Features: {len(feature_cols)}
// Estimated flash: {actual_n_trees * max_nodes_per_tree * 8} bytes

#define {model_name.upper()}_N_TREES {actual_n_trees}
#define {model_name.upper()}_N_FEATURES {len(feature_cols)}
#define {model_name.upper()}_MAX_NODES {max_nodes_per_tree}

struct Node {{
    int8_t feature_idx;
    int16_t threshold;
    int16_t value;
    uint16_t left_idx;
    uint16_t right_idx;
}};

const float {model_name}_feature_means[{model_name.upper()}_N_FEATURES] PROGMEM = {{
    {', '.join(f'{m:.6f}f' for m in feature_means)}
}};

const float {model_name}_feature_stds[{model_name.upper()}_N_FEATURES] PROGMEM = {{
    {', '.join(f'{s:.6f}f' for s in feature_stds)}
}};

const float {model_name}_feature_mins[{model_name.upper()}_N_FEATURES] PROGMEM = {{
    {', '.join(f'{m:.6f}f' for m in feature_mins)}
}};

const float {model_name}_feature_maxs[{model_name.upper()}_N_FEATURES] PROGMEM = {{
    {', '.join(f'{m:.6f}f' for m in feature_maxs)}
}};

const float {model_name}_value_min PROGMEM = {value_min:.6f}f;
const float {model_name}_value_max PROGMEM = {value_max:.6f}f;

"""
        
        # Generate tree data
        for tree_idx, nodes in enumerate(all_tree_nodes):
            header += f"const Node {model_name}_tree{tree_idx}[{len(nodes)}] PROGMEM = {{\n"
            for node in nodes:
                header += f"    {{{node['feature_idx']}, {node['threshold']}, {node['value']}, {node['left_idx']}, {node['right_idx']}}},\n"
            header += "};\n\n"
        
        # Generate tree pointer array
        header += f"const Node* {model_name}_trees[{model_name.upper()}_N_TREES] PROGMEM = {{\n"
        for i in range(actual_n_trees):
            header += f"    {model_name}_tree{i},\n"
        header += "};\n\n"
        
        # Generate tree sizes array
        header += f"const uint16_t {model_name}_tree_sizes[{model_name.upper()}_N_TREES] PROGMEM = {{\n"
        for nodes in all_tree_nodes:
            header += f"    {len(nodes)},\n"
        header += "};\n\n"
        
        # Generate prediction function
        header += f"""inline float {model_name}_dequantize(int16_t val, float min_val, float max_val) {{
    return min_val + (val / 32767.0f) * (max_val - min_val);
}}

float {model_name}_traverse_tree(uint8_t tree_idx, float features[{model_name.upper()}_N_FEATURES]) {{
    Node node;
    uint16_t node_idx = 0;
    uint16_t tree_size = pgm_read_word(&{model_name}_tree_sizes[tree_idx]);
    const Node* tree = (const Node*)pgm_read_ptr(&{model_name}_trees[tree_idx]);
    
    while (node_idx < tree_size) {{
        memcpy_P(&node, &tree[node_idx], sizeof(Node));
        
        if (node.feature_idx == -1) {{
            return {model_name}_dequantize(node.value, 
                pgm_read_float(&{model_name}_value_min),
                pgm_read_float(&{model_name}_value_max));
        }}
        
        float threshold = {model_name}_dequantize(node.threshold,
            pgm_read_float(&{model_name}_feature_mins[node.feature_idx]),
            pgm_read_float(&{model_name}_feature_maxs[node.feature_idx]));
        
        if (features[node.feature_idx] <= threshold) {{
            node_idx = node.left_idx;
        }} else {{
            node_idx = node.right_idx;
        }}
    }}
    
    return 0.0f;
}}

float predict_{model_name}(float raw_features[{model_name.upper()}_N_FEATURES]) {{
    float features[{model_name.upper()}_N_FEATURES];
    for (uint8_t i = 0; i < {model_name.upper()}_N_FEATURES; i++) {{
        float mean = pgm_read_float(&{model_name}_feature_means[i]);
        float std = pgm_read_float(&{model_name}_feature_stds[i]);
        features[i] = (raw_features[i] - mean) / std;
    }}
    
    float prediction = 0.0f;
    for (uint8_t i = 0; i < {model_name.upper()}_N_TREES; i++) {{
        prediction += {model_name}_traverse_tree(i, features);
    }}
    
    return prediction / {model_name.upper()}_N_TREES;
}}

#endif
"""
        
        return header, actual_n_trees * max_nodes_per_tree * 8
    
    def analyze_model_depths(self, model_data, model_name):
        """Analyze tree depths in model"""
        model = model_data['model']
        depths = []
        
        for estimator in model.estimators_[:, 0]:
            tree = estimator.tree_
            depth = self.get_depth(tree, 0)
            depths.append(depth)
        
        depths = np.array(depths)
        Logger.log(f"{model_name} tree depths: min={depths.min()}, max={depths.max()}, mean={depths.mean():.1f}, median={int(np.median(depths))}")
        
        return depths
    
    def export(self, max_trees=50, max_depth=4):
        """Export models for Arduino"""
        Logger.section(f"Exporting models for Arduino (max {max_trees} trees, depth {max_depth})")
        
        eta_path = self.model_dir / 'eta_model.pkl'
        etd_path = self.model_dir / 'etd_model.pkl'
        
        if not eta_path.exists():
            Logger.log(f"ETA model not found: {eta_path}")
            Logger.log("Run 'make ml-train' first to generate models")
            return False
        
        if not etd_path.exists():
            Logger.log(f"ETD model not found: {etd_path}")
            Logger.log("Run 'make ml-train' first to generate models")
            return False
        
        with open(eta_path, 'rb') as f:
            eta_data = pickle.load(f)
        
        with open(etd_path, 'rb') as f:
            etd_data = pickle.load(f)
        
        # Analyze tree depths
        Logger.log("\nAnalyzing model tree depths:")
        eta_depths = self.analyze_model_depths(eta_data, "ETA")
        etd_depths = self.analyze_model_depths(etd_data, "ETD")
        
        # Check if any trees fit the depth constraint
        eta_valid = np.sum(eta_depths <= max_depth)
        etd_valid = np.sum(etd_depths <= max_depth)
        
        if eta_valid == 0 or etd_valid == 0:
            Logger.log(f"\nNo trees found with depth <= {max_depth}")
            Logger.log(f"Valid trees: ETA={eta_valid}, ETD={etd_valid}")
            suggested_depth = int(max(np.median(eta_depths), np.median(etd_depths)))
            Logger.log(f"\nThe model was trained with max_depth={suggested_depth}")
            Logger.log(f"To deploy on Arduino Uno, you need to retrain with shallower trees:")
            Logger.log(f"\n1. Edit ml/config.yaml and change hyperparameters:")
            Logger.log(f"   max_depth: 4  (instead of 5)")
            Logger.log(f"\n2. Retrain models:")
            Logger.log(f"   make ml-train")
            Logger.log(f"\n3. Export again:")
            Logger.log(f"   make ml-export")
            return False
        
        Logger.log(f"Trees with depth <= {max_depth}: ETA={eta_valid}/{len(eta_depths)}, ETD={etd_valid}/{len(etd_depths)}")
        Logger.log("")
        
        # Export ETA model
        eta_header, eta_size = self.generate_header(eta_data, 'eta', max_trees, max_depth)
        if eta_size == 0:
            return False
            
        eta_output = self.hardware_dir / 'eta_model.h'
        eta_output.write_text(eta_header)
        Logger.log(f"ETA model: {eta_output}")
        Logger.log(f"  Estimated flash: {eta_size} bytes ({eta_size/1024:.1f} KB)")
        
        # Export ETD model
        etd_header, etd_size = self.generate_header(etd_data, 'etd', max_trees, max_depth)
        if etd_size == 0:
            return False
            
        etd_output = self.hardware_dir / 'etd_model.h'
        etd_output.write_text(etd_header)
        Logger.log(f"ETD model: {etd_output}")
        Logger.log(f"  Estimated flash: {etd_size} bytes ({etd_size/1024:.1f} KB)")
        
        total_size = eta_size + etd_size
        Logger.log(f"\nTotal estimated flash: {total_size} bytes ({total_size/1024:.1f} KB)")
        Logger.log(f"Arduino Uno flash available: 32 KB")
        
        if total_size > 28000:
            Logger.log(f"Remaining for your code: {(32768 - total_size)/1024:.1f} KB")
            Logger.log("\nWARNING: Models are too large for Arduino Uno")
            Logger.log("Recommended configurations:")
            Logger.log("  Small  (8-10 KB):  --trees 20 --depth 4")
            Logger.log("  Medium (12-15 KB): --trees 30 --depth 4")
            Logger.log("  Large  (18-20 KB): --trees 40 --depth 4")
            return False
        else:
            Logger.log(f"Remaining for your code: {(32768 - total_size)/1024:.1f} KB")
        
        # Generate example usage
        example = """// Example Arduino usage
#include "eta_model.h"
#include "etd_model.h"

void setup() {
    Serial.begin(9600);
}

void loop() {
    // Calculate features from your sensors
    float eta_features[ETA_N_FEATURES] = {
        distance_remaining,
        train_length,
        last_speed,
        speed_change,
        time_01,
        time_12,
        avg_speed_01,
        avg_speed_12
    };
    
    float etd_features[ETD_N_FEATURES] = {
        distance_remaining,
        train_length,
        last_speed,
        speed_change,
        time_01,
        time_12,
        avg_speed_01,
        avg_speed_12,
        accel_trend,
        predicted_speed_at_crossing
    };
    
    float eta_seconds = predict_eta(eta_features);
    float etd_seconds = predict_etd(etd_features);
    
    Serial.print("Train arrives in: ");
    Serial.print(eta_seconds);
    Serial.println(" seconds");
    
    Serial.print("Crossing clears in: ");
    Serial.print(etd_seconds);
    Serial.println(" seconds");
    
    delay(1000);
}
"""
        
        example_path = self.hardware_dir / 'example_usage.ino'
        example_path.write_text(example)
        Logger.log(f"\nExample Arduino sketch: {example_path}")
        
        return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export models for Arduino')
    parser.add_argument('--trees', type=int, default=50, help='Max trees per model')
    parser.add_argument('--depth', type=int, default=5, help='Max tree depth')
    args = parser.parse_args()
    
    exporter = ModelExporter()
    exporter.export(args.trees, args.depth)