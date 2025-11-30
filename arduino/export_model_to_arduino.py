"""Export trained ML model to Arduino header file."""

import pickle
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def export_linear_regression(model, output_path):
    """Export Linear Regression model as Arduino header."""
    
    coefficients = model.coef_
    intercept = model.intercept_
    
    feature_names = [
        'time_0_to_1',
        'time_1_to_2', 
        'speed_0_to_1',
        'speed_1_to_2',
        'acceleration',
        'distance_remaining'
    ]
    
    code = "#ifndef ETA_MODEL_H\n"
    code += "#define ETA_MODEL_H\n\n"
    code += "float predictETA(float features[6]) {\n"
    code += f"    float prediction = {intercept:.6f};\n"
    
    for i, (name, coef) in enumerate(zip(feature_names, coefficients)):
        code += f"    prediction += features[{i}] * {coef:.6f}; // {name}\n"
    
    code += "    return prediction;\n"
    code += "}\n\n"
    code += "#endif\n"
    
    with open(output_path, 'w') as f:
        f.write(code)
    
    print(f"\nLinear model exported to: {output_path}")
    print(f"Memory usage: ~{len(coefficients) * 4 + 4} bytes")
    return code


def export_decision_tree(tree, output_path, max_depth=5):
    """Export Decision Tree to Arduino header."""
    
    def export_tree_recursive(tree, node_id, depth=0, indent="    "):
        if depth > max_depth:
            value = tree.value[node_id][0][0]
            return f"{indent}return {value:.3f};\n"
        
        if tree.children_left[node_id] == tree.children_right[node_id]:
            value = tree.value[node_id][0][0]
            return f"{indent}return {value:.3f};\n"
        
        feature_idx = tree.feature[node_id]
        threshold = tree.threshold[node_id]
        left_child = tree.children_left[node_id]
        right_child = tree.children_right[node_id]
        
        feature_names = ['time_0_to_1', 'time_1_to_2', 'speed_0_to_1', 
                        'speed_1_to_2', 'acceleration', 'distance']
        
        code = f"{indent}if (features[{feature_idx}] <= {threshold:.3f}f) {{\n"
        code += export_tree_recursive(tree, left_child, depth + 1, indent + "    ")
        code += f"{indent}}} else {{\n"
        code += export_tree_recursive(tree, right_child, depth + 1, indent + "    ")
        code += f"{indent}}}\n"
        
        return code
    
    tree_struct = tree.tree_
    
    code = "#ifndef ETA_MODEL_H\n"
    code += "#define ETA_MODEL_H\n\n"
    code += "float predictETA(float features[6]) {\n"
    code += export_tree_recursive(tree_struct, 0)
    code += "}\n\n"
    code += "#endif\n"
    
    with open(output_path, 'w') as f:
        f.write(code)
    
    node_count = tree_struct.node_count
    memory_bytes = node_count * 16
    
    print(f"\nDecision Tree exported to: {output_path}")
    print(f"Tree depth: {tree.get_depth()}")
    print(f"Number of nodes: {node_count}")
    print(f"Estimated memory: ~{memory_bytes} bytes")
    
    return code


def train_simplified_tree(data_path, output_path, max_depth=5):
    """Train a simplified decision tree from training data."""
    import pandas as pd
    
    print("Loading training data...")
    df = pd.read_csv(data_path)
    
    required_cols = ['time_0_to_1', 'time_1_to_2', 'speed_0_to_1', 
                    'speed_1_to_2', 'ETA', 'sensor_2_pos']
    
    if not all(col in df.columns for col in required_cols):
        print("ERROR: Missing required columns in training data")
        return None
    
    df['acceleration'] = (df['speed_1_to_2'] - df['speed_0_to_1']) / df['time_1_to_2']
    df['distance_remaining'] = df['sensor_2_pos']
    
    feature_cols = ['time_0_to_1', 'time_1_to_2', 'speed_0_to_1', 
                   'speed_1_to_2', 'acceleration', 'distance_remaining']
    
    X = df[feature_cols]
    y = df['ETA']
    
    print(f"\nTraining simplified tree (max_depth={max_depth})...")
    tree = DecisionTreeRegressor(max_depth=max_depth, random_state=42)
    tree.fit(X, y)
    
    from sklearn.metrics import mean_absolute_error, r2_score
    predictions = tree.predict(X)
    mae = mean_absolute_error(y, predictions)
    r2 = r2_score(y, predictions)
    
    print(f"Simplified model performance:")
    print(f"  MAE: {mae:.3f}s")
    print(f"  R2: {r2:.4f}")
    
    export_decision_tree(tree, output_path, max_depth)
    
    return tree


def train_linear_model(data_path, output_path):
    """Train linear regression from training data."""
    import pandas as pd
    
    print("Loading training data...")
    df = pd.read_csv(data_path)
    
    df['acceleration'] = (df['speed_1_to_2'] - df['speed_0_to_1']) / df['time_1_to_2']
    df['distance_remaining'] = df['sensor_2_pos']
    
    feature_cols = ['time_0_to_1', 'time_1_to_2', 'speed_0_to_1', 
                   'speed_1_to_2', 'acceleration', 'distance_remaining']
    
    X = df[feature_cols]
    y = df['ETA']
    
    model = LinearRegression()
    model.fit(X, y)
    
    from sklearn.metrics import mean_absolute_error, r2_score
    predictions = model.predict(X)
    mae = mean_absolute_error(y, predictions)
    r2 = r2_score(y, predictions)
    
    print(f"\nLinear model performance:")
    print(f"  MAE: {mae:.3f}s")
    print(f"  R2: {r2:.4f}")
    
    export_linear_regression(model, output_path)
    
    return model


def main():
    """Export model for Arduino."""
    
    print("ML Model to Arduino Exporter")
    
    model_path = os.path.join('ml', 'models', 'eta_predictor.pkl')
    data_path = os.path.join('data_generation', 'data', 'train_approaches.csv')
    output_path = os.path.join('arduino', 'eta_model.h')
    
    if not os.path.exists(data_path):
        print(f"\nERROR: Training data not found at {data_path}")
        print("Please generate data first: make data-train")
        return
    
    print("\nChoose export method:")
    print("1. Simplified Decision Tree (RECOMMENDED)")
    print("   - Good accuracy")
    print("   - Moderate memory (1-2KB)")
    print("2. Linear Regression")
    print("   - Fast and tiny (100 bytes)")
    print("   - May be less accurate")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == '1':
        print("\nEnter maximum tree depth (3-7 recommended):")
        print("  Depth 3: ~50 nodes")
        print("  Depth 5: ~200 nodes")
        print("  Depth 7: ~800 nodes")
        
        depth = int(input("Depth: ").strip() or "5")
        tree = train_simplified_tree(data_path, output_path, max_depth=depth)
        
        if tree:
            print("\nSUCCESS")
            print(f"\nArduino header file created: {output_path}")
            print("Already included in sketch.ino")
    
    elif choice == '2':
        model = train_linear_model(data_path, output_path)
        
        if model:
            print("\nSUCCESS")
            print(f"\nArduino header file created: {output_path}")
            print("Already included in sketch.ino")
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()