"""
ETA Model Trainer
Trains decision tree model for train arrival prediction
Uses advanced feature engineering for Arduino deployment
"""
import traci
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import yaml


class ETADataCollector:
    def __init__(self, config_file="config/thresholds.yaml"):
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        self.sensors = config['sensor_positions']
        self.crossing_pos = 0.0
    
    def collect(self, num_samples=250):
        """Collect ETA training samples"""
        print(f"[{self._timestamp()}] Collecting ETA training data")
        print(f"Sensors: {[f'{s:.1f}m' for s in self.sensors]}")
        
        data = []
        speeds = np.linspace(25, 38, num_samples)
        
        for i, speed in enumerate(speeds):
            sample = self._collect_single_pass(speed)
            
            if sample:
                data.append(sample)
                
                if (i + 1) % 50 == 0:
                    print(f"[{self._timestamp()}] Collected {i + 1}/{num_samples}")
        
        df = pd.DataFrame(data)
        
        output_dir = Path('outputs/data')
        output_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_dir / 'eta_training.csv', index=False)
        
        print(f"[{self._timestamp()}] Collected {len(df)} samples")
        print(f"ETA range: {df['actual_eta'].min():.1f}s to {df['actual_eta'].max():.1f}s")
        
        return df
    
    def _collect_single_pass(self, train_speed):
        """Simulate single train pass"""
        traci.start(['sumo', '-c', 'sumo/simulation.sumocfg', '--start', '--quit-on-end'])
        
        try:
            traci.vehicle.add('train_test', 'r_rail', typeID='train',
                            depart='now', departSpeed=str(train_speed))
        except:
            traci.close()
            return None
        
        sensor_triggers = {}
        sensor_speeds = {}
        arrival_time = None
        
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            t = traci.simulation.getTime()
            
            if 'train_test' not in traci.vehicle.getIDList():
                break
            
            pos = traci.vehicle.getPosition('train_test')[0]
            speed = traci.vehicle.getSpeed('train_test')
            
            for i, sensor_pos in enumerate(self.sensors):
                if i not in sensor_triggers and pos >= sensor_pos:
                    sensor_triggers[i] = t
                    sensor_speeds[i] = speed
            
            if arrival_time is None and pos >= self.crossing_pos:
                arrival_time = t
            
            if len(sensor_triggers) == 3 and arrival_time is not None:
                break
        
        traci.close()
        
        if len(sensor_triggers) != 3 or arrival_time is None:
            return None
        
        # Calculate features
        t01 = sensor_triggers[1] - sensor_triggers[0]
        t12 = sensor_triggers[2] - sensor_triggers[1]
        
        d01 = self.sensors[0] - self.sensors[1]
        d12 = self.sensors[1] - self.sensors[2]
        
        v01 = d01 / t01 if t01 > 0 else 0
        v12 = d12 / t12 if t12 > 0 else 0
        
        accel = (v12 - v01) / t12 if t12 > 0 else 0
        eta = arrival_time - sensor_triggers[2]
        
        # Advanced features
        avg_speed = (v01 + v12) / 2
        speed_variance = ((v01 - avg_speed)**2 + (v12 - avg_speed)**2) / 2
        decel_rate = abs(accel) if accel < 0 else 0
        
        return {
            'time_0_to_1': t01,
            'time_1_to_2': t12,
            'speed_0_to_1': v01,
            'speed_1_to_2': v12,
            'acceleration': accel,
            'distance_remaining': self.sensors[2],
            'avg_speed': avg_speed,
            'speed_variance': speed_variance,
            'decel_rate': decel_rate,
            'actual_eta': eta
        }
    
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")


class ETAModelTrainer:
    def __init__(self):
        self.features = [
            'time_0_to_1', 'time_1_to_2', 'speed_0_to_1',
            'speed_1_to_2', 'acceleration', 'distance_remaining',
            'avg_speed', 'speed_variance', 'decel_rate'
        ]
    
    def train(self):
        """Train optimized decision tree for Arduino"""
        from sklearn.tree import DecisionTreeRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, r2_score
        import pickle
        
        print(f"[{self._timestamp()}] Training ETA model")
        
        df = pd.read_csv('outputs/data/eta_training.csv')
        
        X = df[self.features]
        y = df['actual_eta']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        
        best_mae = float('inf')
        best_model = None
        best_depth = None
        
        for depth in range(4, 10):
            model = DecisionTreeRegressor(
                max_depth=depth,
                min_samples_split=5,
                min_samples_leaf=3,
                random_state=42
            )
            model.fit(X_train, y_train)
            
            pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, pred)
            r2 = r2_score(y_test, pred)
            
            print(f"  Depth {depth}: MAE={mae:.3f}s, R²={r2:.3f}, Nodes={model.tree_.node_count}")
            
            if mae < best_mae and model.tree_.node_count <= 100:
                best_mae = mae
                best_model = model
                best_depth = depth
        
        print(f"Best model: Depth={best_depth}, MAE={best_mae:.3f}s")
        
        # Feature importance
        importances = best_model.feature_importances_
        print("Feature importance:")
        for feat, imp in sorted(zip(self.features, importances), key=lambda x: x[1], reverse=True):
            if imp > 0.01:
                print(f"  {feat}: {imp:.3f}")
        
        output_dir = Path('outputs/models')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / 'eta_model.pkl', 'wb') as f:
            pickle.dump(best_model, f)
        
        print(f"[{self._timestamp()}] Model saved")
        
        return best_model
    
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--train', action='store_true')
    parser.add_argument('--samples', type=int, default=250)
    
    args = parser.parse_args()
    
    if args.collect:
        collector = ETADataCollector()
        collector.collect(args.samples)
    
    if args.train:
        trainer = ETAModelTrainer()
        trainer.train()
    
    if not args.collect and not args.train:
        print("Usage: --collect to collect data, --train to train model")