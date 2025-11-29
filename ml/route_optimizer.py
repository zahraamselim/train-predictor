"""ML model to optimize wait vs reroute decisions."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import sys
import os


class RouteOptimizer:
    """
    ML model to decide: should vehicle wait or reroute?
    
    Features:
        - train_eta: Time until train arrives (s)
        - queue_length: Number of vehicles already waiting
        - traffic_density: Encoded as 0=light, 1=medium, 2=heavy
        - intersection_distance: Distance from intersection to crossing (m)
        - alternative_route_distance: Length of alternative route (m)
    
    Output:
        - Action: 'wait' or 'reroute'
        - Confidence score
    """
    
    def __init__(self, model_path=None):
        """Initialize optimizer, optionally loading trained model."""
        self.model = None
        self.feature_columns = [
            'train_eta', 'queue_length', 'traffic_density_encoded',
            'intersection_distance', 'alternative_route_distance'
        ]
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def _encode_traffic_density(self, density):
        """Encode traffic density as numeric value."""
        density_map = {'light': 0, 'medium': 1, 'heavy': 2}
        if isinstance(density, str):
            return density_map.get(density, 1)
        return density
    
    def _prepare_features(self, data):
        """Prepare features for model input."""
        if isinstance(data, pd.DataFrame):
            df = data.copy()
            if 'traffic_density' in df.columns:
                df['traffic_density_encoded'] = df['traffic_density'].apply(
                    self._encode_traffic_density
                )
            return df[self.feature_columns]
        else:
            train_eta, queue_length, traffic_density, intersection_dist, alt_route_dist = data
            return np.array([[
                train_eta,
                queue_length,
                self._encode_traffic_density(traffic_density),
                intersection_dist,
                alt_route_dist
            ]])
    
    def train(self, data_file):
        """
        Train Random Forest model on decision dataset.
        
        Args:
            data_file: Path to decisions.csv
            
        Returns:
            Dict with training metrics
        """
        print(f"\nTraining route optimizer on: {data_file}")
        
        df = pd.read_csv(data_file)
        
        X = self._prepare_features(df)
        y = df['optimal_action']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training samples: {len(X_train)}")
        print(f"Test samples: {len(X_test)}")
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train, y_train)
        
        train_acc = accuracy_score(y_train, self.model.predict(X_train))
        test_acc = accuracy_score(y_test, self.model.predict(X_test))
        
        y_pred = self.model.predict(X_test)
        
        print(f"\nTraining accuracy: {train_acc:.4f}")
        print(f"Test accuracy: {test_acc:.4f}")
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"              Predicted")
        print(f"              Wait  Reroute")
        print(f"Actual Wait   {cm[0][0]:4d}  {cm[0][1]:4d}")
        print(f"       Reroute {cm[1][0]:4d}  {cm[1][1]:4d}")
        
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nFeature Importance:")
        for _, row in feature_importance.iterrows():
            print(f"  {row['feature']:30s}: {row['importance']:.4f}")
        
        return {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'confusion_matrix': cm.tolist(),
            'feature_importance': feature_importance.to_dict('records')
        }
    
    def predict(self, train_eta, queue_length, traffic_density, 
                intersection_distance, alternative_route_distance):
        """
        Predict optimal action for given scenario.
        
        Returns:
            Dict with action and confidence
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first or load a trained model.")
        
        features = self._prepare_features([
            train_eta, queue_length, traffic_density,
            intersection_distance, alternative_route_distance
        ])
        
        action = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        confidence = max(probabilities)
        
        return {
            'action': action,
            'confidence': round(confidence, 3),
            'wait_probability': round(probabilities[0], 3) if action == 'wait' else round(probabilities[1], 3),
            'reroute_probability': round(probabilities[1], 3) if action == 'reroute' else round(probabilities[0], 3)
        }
    
    def save_model(self, filepath):
        """Save trained model to file."""
        if self.model is None:
            raise ValueError("No model to save")
        
        model_dir = os.path.dirname(filepath)
        if model_dir and not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"\nModel saved: {filepath}")
    
    def load_model(self, filepath):
        """Load trained model from file."""
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
        
        print(f"Model loaded: {filepath}")


def train_model(data_file=None, output_model=None):
    """Train route optimizer model."""
    if data_file is None:
        data_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data_generation', 'data', 'decisions.csv'
        )
    
    if output_model is None:
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(model_dir, exist_ok=True)
        output_model = os.path.join(model_dir, 'route_optimizer.pkl')
    
    optimizer = RouteOptimizer()
    metrics = optimizer.train(data_file)
    optimizer.save_model(output_model)
    
    return metrics


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
        train_model(data_file)
    else:
        train_model()