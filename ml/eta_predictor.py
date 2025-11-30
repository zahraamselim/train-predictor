"""ML-based ETA prediction for hardware integration."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config


class ETAPredictor:
    """
    ML model to predict train ETA from sensor timings.
    Uses Random Forest Regressor for accurate continuous predictions.
    
    Features (6):
        - time_0_to_1: Time between sensor 0 and 1 (seconds)
        - time_1_to_2: Time between sensor 1 and 2 (seconds)
        - speed_0_to_1: Speed calculated from first pair (m/s)
        - speed_1_to_2: Speed calculated from second pair (m/s)
        - acceleration: Calculated acceleration (m/s²)
        - distance_remaining: Distance from sensor 2 to crossing (m)
    
    Output:
        - actual_eta: Real ETA in seconds (continuous regression)
    """
    
    def __init__(self, model_path=None):
        self.model = None
        self.feature_columns = [
            'time_0_to_1',
            'time_1_to_2',
            'speed_0_to_1',
            'speed_1_to_2',
            'acceleration',
            'distance_remaining'
        ]
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def _prepare_features(self, data):
        """Prepare features for model input."""
        if isinstance(data, pd.DataFrame):
            return data[self.feature_columns]
        else:
            time_0_to_1, time_1_to_2, speed_0_to_1, speed_1_to_2, acceleration, distance = data
            return np.array([[
                time_0_to_1,
                time_1_to_2,
                speed_0_to_1,
                speed_1_to_2,
                acceleration,
                distance
            ]])
    
    def train(self, data_file):
        """Train Random Forest regressor on train approach data."""
        print(f"\nTraining ETA Predictor on: {data_file}")
        
        df = pd.read_csv(data_file)
        
        required_cols = ['time_0_to_1', 'time_1_to_2', 'speed_0_to_1', 
                        'speed_1_to_2', 'ETA', 'sensor_2_pos']
        
        if not all(col in df.columns for col in required_cols):
            print(f"ERROR: Missing required columns")
            return None
        
        df['acceleration'] = (df['speed_1_to_2'] - df['speed_0_to_1']) / df['time_1_to_2']
        df['distance_remaining'] = df['sensor_2_pos']
        
        X = self._prepare_features(df)
        y = df['ETA']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"Training samples: {len(X_train)}")
        print(f"Test samples: {len(X_test)}")
        
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        print(f"\nTraining Performance:")
        print(f"  MAE: {train_mae:.3f}s")
        print(f"  RMSE: {train_rmse:.3f}s")
        print(f"  R²: {train_r2:.4f}")
        
        print(f"\nTest Performance:")
        print(f"  MAE: {test_mae:.3f}s")
        print(f"  RMSE: {test_rmse:.3f}s")
        print(f"  R²: {test_r2:.4f}")
        
        if test_mae < 2.0 and test_r2 > 0.90:
            print("\n✓ Model meets accuracy requirements")
            print("  - MAE < 2.0s")
            print("  - R² > 0.90")
        else:
            print("\n⚠ WARNING: Model may need improvement")
            if test_mae >= 2.0:
                print(f"  - MAE too high: {test_mae:.3f}s (target < 2.0s)")
            if test_r2 <= 0.90:
                print(f"  - R² too low: {test_r2:.4f} (target > 0.90)")
        
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nFeature Importance:")
        for _, row in feature_importance.iterrows():
            print(f"  {row['feature']:20s}: {row['importance']:.4f}")
        
        comparison_df = pd.DataFrame({
            'actual': y_test,
            'predicted': test_pred,
            'error': test_pred - y_test
        })
        
        print("\nSample Predictions:")
        print(comparison_df.head(5).to_string(index=False))
        
        return {
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'feature_importance': feature_importance.to_dict('records')
        }
    
    def predict(self, time_0_to_1, time_1_to_2, speed_0_to_1, 
               speed_1_to_2, acceleration, distance_remaining):
        """
        Predict ETA from sensor data.
        
        Returns:
            Dict with eta_predicted, confidence, std_dev
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        features = self._prepare_features([
            time_0_to_1, time_1_to_2, speed_0_to_1,
            speed_1_to_2, acceleration, distance_remaining
        ])
        
        eta = self.model.predict(features)[0]
        
        trees_predictions = [tree.predict(features)[0] for tree in self.model.estimators_]
        std_dev = np.std(trees_predictions)
        confidence = 1.0 / (1.0 + std_dev)
        
        return {
            'eta_predicted': round(max(0, eta), 2),
            'confidence': round(confidence, 3),
            'std_dev': round(std_dev, 3)
        }
    
    def compare_with_physics(self, sensor_data, physics_eta):
        """Compare ML prediction with physics-based calculation."""
        ml_result = self.predict(**sensor_data)
        
        return {
            'physics_eta': physics_eta,
            'ml_eta': ml_result['eta_predicted'],
            'difference': abs(ml_result['eta_predicted'] - physics_eta),
            'ml_confidence': ml_result['confidence'],
            'better_accuracy': 'ML' if ml_result['confidence'] > 0.8 else 'Physics'
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
        
        print(f"ETA Predictor loaded: {filepath}")


def train_eta_model(data_file=None, output_model=None):
    """Train ETA predictor model."""
    if data_file is None:
        data_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data_generation', 'data', 'train_approaches.csv'
        )
    
    if output_model is None:
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(model_dir, exist_ok=True)
        output_model = os.path.join(model_dir, 'eta_predictor.pkl')
    
    if not os.path.exists(data_file):
        print(f"\nERROR: Training data not found: {data_file}")
        print("Run: make data-train")
        return None
    
    predictor = ETAPredictor()
    metrics = predictor.train(data_file)
    
    if metrics and metrics['test_mae'] < 2.0:
        predictor.save_model(output_model)
        print("\n✓ ETA Predictor training successful!")
        print(f"  Accuracy: ±{metrics['test_mae']:.2f}s")
        print(f"  Model ready for Arduino export")
        return metrics
    else:
        print("\n⚠ WARNING: Model accuracy too low")
        print("  Consider generating more training data")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
        train_eta_model(data_file)
    else:
        train_eta_model()