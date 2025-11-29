"""ML-based notification timing optimizer (OPTIONAL - for capstone ML requirement)."""

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_scale_config

package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)


class NotificationOptimizer:
    """
    ML model to optimize notification timing.
    
    Learns from simulated scenarios to minimize:
    - Vehicle wait time (efficiency)
    - Safety violations (critical)
    
    This is where ML adds value - learning complex tradeoffs.
    """
    
    def __init__(self, model_path=None):
        """Initialize optimizer, optionally loading trained model."""
        self.model = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def generate_training_data(self, num_scenarios=500):
        """
        Generate training data by simulating notification outcomes.
        
        Returns:
            X: Features [train_eta, traffic_density_encoded, intersection_distance]
            y: Optimal notification times
        """
        # Import traffic simulator
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), '01_traffic'))
        from simulator import TrafficSimulator
        
        config = get_scale_config()
        clearance_times = config['vehicle_clearance']
        gate_offset = config['gates']['closure_before_eta']
        safety_buffer = config['traffic']['safety_buffer']
        intersection_distances = config['traffic']['intersection_distances']
        
        X = []
        y = []
        
        print(f"\nGenerating {num_scenarios} training scenarios for ML...")
        
        for i in range(num_scenarios):
            # Random scenario
            train_eta = np.random.uniform(30, 120)  # 30-120 seconds
            density = np.random.choice(['light', 'medium', 'heavy'])
            intersection_dist = np.random.choice(intersection_distances)
            
            # Encode density as number
            density_map = {'light': 0, 'medium': 1, 'heavy': 2}
            density_encoded = density_map[density]
            
            # Calculate optimal notification time
            # Rule: notify early enough for worst-case clearance
            max_clearance = clearance_times[density]['max_time']
            gate_closure_time = train_eta - gate_offset
            
            # Optimal = just enough time for clearance + safety
            optimal_notification = gate_closure_time - max_clearance - safety_buffer
            
            # Add some noise to simulate real-world variation
            optimal_notification += np.random.normal(0, 2)  # ±2 second variance
            
            # Clip to reasonable range
            optimal_notification = max(5, min(optimal_notification, train_eta - 15))
            
            X.append([train_eta, density_encoded, intersection_dist])
            y.append(optimal_notification)
            
            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{num_scenarios}")
        
        return np.array(X), np.array(y)
    
    def train(self, X, y):
        """Train Random Forest model."""
        print("\nTraining ML model...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"  Train R²: {train_score:.4f}")
        print(f"  Test R²: {test_score:.4f}")
        
        # Calculate MAE
        y_pred = self.model.predict(X_test)
        mae = np.mean(np.abs(y_test - y_pred))
        print(f"  Mean Absolute Error: {mae:.2f}s")
        
        return {
            'train_r2': train_score,
            'test_r2': test_score,
            'mae': mae
        }
    
    def predict(self, train_eta, traffic_density, intersection_distance):
        """
        Predict optimal notification time.
        
        Args:
            train_eta: Train ETA in seconds
            traffic_density: 'light', 'medium', or 'heavy'
            intersection_distance: Distance to crossing in meters
        
        Returns:
            Optimal notification time in seconds
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Encode density
        density_map = {'light': 0, 'medium': 1, 'heavy': 2}
        density_encoded = density_map[traffic_density]
        
        # Predict
        features = np.array([[train_eta, density_encoded, intersection_distance]])
        notification_time = self.model.predict(features)[0]
        
        return round(notification_time, 2)
    
    def save_model(self, filepath):
        """Save trained model to file."""
        if self.model is None:
            raise ValueError("No model to save")
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"\nModel saved: {filepath}")
    
    def load_model(self, filepath):
        """Load trained model from file."""
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
        
        print(f"Model loaded: {filepath}")
