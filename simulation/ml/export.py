"""
Arduino Export
Exports ML model and configuration to Arduino C headers
"""
import pickle
import yaml
from pathlib import Path
from datetime import datetime


class ArduinoExporter:
    def __init__(self):
        self.output_dir = Path('hardware/arduino')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_model(self):
        """Export trained model to Arduino C header"""
        print(f"[{self._timestamp()}] Exporting ML model to Arduino")
        
        with open('outputs/models/eta_model.pkl', 'rb') as f:
            model = pickle.load(f)
        
        tree = model.tree_
        
        header = self._generate_header(tree)
        
        with open(self.output_dir / 'eta_model.h', 'w') as f:
            f.write(header)
        
        print(f"Model exported: Depth={model.get_depth()}, Nodes={tree.node_count}")
    
    def export_config(self):
        """Export thresholds to Arduino config header"""
        print(f"[{self._timestamp()}] Exporting config to Arduino")
        
        with open('config/thresholds.yaml') as f:
            thresholds = yaml.safe_load(f)
        
        # Hardware scaling
        sim_scale = 50.0
        hw_scale = 1.0 / sim_scale
        
        sensors_hw = [pos * hw_scale * 100 for pos in thresholds['sensor_positions']]
        
        max_notification = max(thresholds['notification_times'].values())
        
        header = f"""#ifndef CROSSING_CONFIG_H
#define CROSSING_CONFIG_H

float getGateCloseThreshold() {{ return {thresholds['closure_before_eta']:.1f}f; }}
float getGateOpenThreshold() {{ return {thresholds['opening_after_etd']:.1f}f; }}
float getNotificationThreshold() {{ return {max_notification:.1f}f; }}
float getEngineOffThreshold() {{ return {thresholds['engine_off_threshold']:.1f}f; }}

unsigned long getBuzzerInterval() {{ return 500; }}
unsigned long getTrainClearDelay() {{ return 3000; }}

const float SENSOR_0_POS = {sensors_hw[0]:.2f}f;
const float SENSOR_1_POS = {sensors_hw[1]:.2f}f;
const float SENSOR_2_POS = {sensors_hw[2]:.2f}f;

#endif
"""
        
        with open(self.output_dir / 'config.h', 'w') as f:
            f.write(header)
        
        print("Config exported:")
        print(f"  Gate close: {thresholds['closure_before_eta']:.1f}s")
        print(f"  Gate open: {thresholds['opening_after_etd']:.1f}s")
        print(f"  Notification: {max_notification:.1f}s")
        print(f"  Engine off: {thresholds['engine_off_threshold']:.1f}s")
        print(f"  Sensors (cm): {[f'{s:.2f}' for s in sensors_hw]}")
    
    def _generate_header(self, tree):
        """Generate C header from decision tree"""
        header = "#ifndef ETA_MODEL_H\n#define ETA_MODEL_H\n\n"
        header += f"// Decision Tree: Depth={tree.max_depth}, Nodes={tree.node_count}\n"
        header += "// Features: [0]=time_0_to_1, [1]=time_1_to_2, [2]=speed_0_to_1\n"
        header += "//           [3]=speed_1_to_2, [4]=acceleration, [5]=distance_remaining\n"
        header += "//           [6]=avg_speed, [7]=speed_variance, [8]=decel_rate\n\n"
        header += "float predictETA(float features[9]) {\n"
        header += self._generate_node(tree, 0, "    ")
        header += "}\n\n#endif\n"
        
        return header
    
    def _generate_node(self, tree, node_id, indent):
        """Recursively generate C code for tree nodes"""
        if tree.children_left[node_id] == tree.children_right[node_id]:
            return f"{indent}return {tree.value[node_id][0][0]:.3f}f;\n"
        
        feature = tree.feature[node_id]
        threshold = tree.threshold[node_id]
        left = tree.children_left[node_id]
        right = tree.children_right[node_id]
        
        code = f"{indent}if (features[{feature}] <= {threshold:.3f}f) {{\n"
        code += self._generate_node(tree, left, indent + "    ")
        code += f"{indent}}} else {{\n"
        code += self._generate_node(tree, right, indent + "    ")
        code += f"{indent}}}\n"
        
        return code
    
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', action='store_true')
    parser.add_argument('--config', action='store_true')
    parser.add_argument('--all', action='store_true')
    
    args = parser.parse_args()
    
    exporter = ArduinoExporter()
    
    if args.all or args.model:
        exporter.export_model()
    
    if args.all or args.config:
        exporter.export_config()
    
    if not any([args.model, args.config, args.all]):
        print("Usage: --model, --config, or --all")