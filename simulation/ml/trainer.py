import sys
import os
sys.path.insert(0, '/app')

import traci
import pandas as pd
import numpy as np
from pathlib import Path
import yaml
import signal
import time

class ETATrainer:
    """Train ETA prediction model"""
    
    def __init__(self, config_file="config/thresholds.yaml"):
        self.interrupted = False
        signal.signal(signal.SIGINT, self._signal_handler)
        
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
            self.sensors = config['sensor_positions']
        except:
            self.sensors = [1130.0, 645.7, 322.9]
        
        self.crossing_pos = 0.0
        self.sensor_positions = [-s for s in self.sensors]
        
        self.features = [
            'time_0_to_1', 'time_1_to_2', 'speed_0_to_1',
            'speed_1_to_2', 'acceleration', 'distance_remaining',
            'avg_speed', 'speed_variance', 'decel_rate'
        ]
    
    def _signal_handler(self, sig, frame):
        self.interrupted = True
        self._safe_close_traci()
        sys.exit(0)
    
    def _safe_close_traci(self):
        """Safely close TraCI connection"""
        try:
            if traci.isLoaded():
                traci.close()
        except:
            pass
        time.sleep(0.2)
    
    def collect_data(self, num_samples=250):
        from datetime import datetime
        from simulation.network.generator import NetworkGenerator
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Collecting {num_samples} ETA samples")
        
        generator = NetworkGenerator(mode="training")
        if not generator.generate(self.sensors):
            print("ERROR: Failed to generate training network")
            return None
        
        data = []
        speeds = np.linspace(25, 38, 15)
        accels = [-0.3, -0.1, 0.0, 0.1, 0.3]
        
        successful = 0
        attempts = 0
        consecutive_failures = 0
        
        while successful < num_samples and not self.interrupted:
            speed = speeds[successful % len(speeds)]
            accel = accels[successful % len(accels)]
            
            sample = self._collect_single_pass(speed, accel)
            attempts += 1
            
            if sample:
                data.append(sample)
                successful += 1
                consecutive_failures = 0
                
                if successful % 25 == 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Progress: {successful}/{num_samples} samples")
            else:
                consecutive_failures += 1
                if consecutive_failures > 50:
                    print(f"ERROR: {consecutive_failures} consecutive failures, aborting")
                    break
            
            if attempts > num_samples * 5:
                print(f"Too many attempts ({attempts}), stopping")
                break
        
        if successful == 0:
            print("ERROR: No successful samples collected")
            return None
        
        df = pd.DataFrame(data)
        
        output_dir = Path('outputs/data')
        output_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_dir / 'eta_training.csv', index=False)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Collected {len(df)} samples (success rate: {successful/attempts*100:.1f}%)")
        
        return df
    
    def _collect_single_pass(self, train_speed, accel_rate):
        """Collect a single training sample"""
        
        self._safe_close_traci()
        
        try:
            traci.start([
                'sumo',
                '-c', 'sumo/training/training.sumocfg',
                '--start',
                '--quit-on-end',
                '--no-warnings',
                '--no-step-log',
                '--time-to-teleport', '-1',
                '--step-length', '0.1',
                '--collision.action', 'none'
            ])
        except Exception as e:
            self._safe_close_traci()
            return None
        
        sensor_triggers = {}
        arrival_time = None
        train_id = f'train_{int(time.time() * 1000000) % 1000000}'
        
        try:
            # Initial stabilization
            for _ in range(5):
                traci.simulationStep()
            
            # Add train using the predefined type from routes.rou.xml
            traci.vehicle.add(
                train_id,
                'train_route',
                typeID='train_type',
                depart='now',
                departLane='first',
                departPos='base',
                departSpeed='0'
            )
            
            # Step to let train appear
            for _ in range(10):
                traci.simulationStep()
                if train_id in traci.vehicle.getIDList():
                    break
            
            # Verify train exists
            if train_id not in traci.vehicle.getIDList():
                return None
            
            # Set speed control mode and initial speed
            traci.vehicle.setSpeedMode(train_id, 0)  # Disable safety checks
            traci.vehicle.setSpeed(train_id, train_speed)
            
            # Wait for speed to stabilize
            for _ in range(30):
                traci.simulationStep()
                if train_id not in traci.vehicle.getIDList():
                    return None
            
            # Apply acceleration if needed
            if abs(accel_rate) > 0.01:
                target_speed = max(20.0, min(45.0, train_speed + accel_rate * 10))
                traci.vehicle.setSpeed(train_id, target_speed)
            
            # Main simulation loop
            max_steps = 2000
            step = 0
            
            while step < max_steps and not self.interrupted:
                traci.simulationStep()
                t = traci.simulation.getTime()
                step += 1
                
                # Check if train still exists
                if train_id not in traci.vehicle.getIDList():
                    break
                
                try:
                    pos = traci.vehicle.getPosition(train_id)[0]
                    speed = traci.vehicle.getSpeed(train_id)
                except:
                    break
                
                # Check sensor triggers
                for i, sensor_x in enumerate(self.sensor_positions):
                    if i not in sensor_triggers and pos >= sensor_x:
                        sensor_triggers[i] = {'time': t, 'speed': speed, 'position': pos}
                
                # Check arrival at crossing
                if arrival_time is None and pos >= self.crossing_pos:
                    arrival_time = t
                
                # If we have all data, we can stop
                if len(sensor_triggers) == 3 and arrival_time is not None:
                    break
                
                # Safety check
                if pos > self.crossing_pos + 500:
                    break
        
        except Exception as e:
            pass
        
        finally:
            self._safe_close_traci()
        
        # Validate we have all required data
        if len(sensor_triggers) != 3 or arrival_time is None:
            return None
        
        # Extract timing data
        t0, t1, t2 = sensor_triggers[0]['time'], sensor_triggers[1]['time'], sensor_triggers[2]['time']
        
        time_0_to_1 = t1 - t0
        time_1_to_2 = t2 - t1
        
        # Validate timing
        if time_0_to_1 <= 0 or time_1_to_2 <= 0:
            return None
        
        # Calculate speeds
        d01 = abs(self.sensor_positions[1] - self.sensor_positions[0])
        d12 = abs(self.sensor_positions[2] - self.sensor_positions[1])
        
        speed_0_to_1 = d01 / time_0_to_1
        speed_1_to_2 = d12 / time_1_to_2
        
        # Calculate actual ETA
        actual_eta = arrival_time - t2
        
        # Validate ETA
        if actual_eta <= 0 or actual_eta > 100:
            return None
        
        # Calculate features
        acceleration = (speed_1_to_2 - speed_0_to_1) / time_1_to_2
        distance_remaining = abs(self.crossing_pos - self.sensor_positions[2])
        avg_speed = (speed_0_to_1 + speed_1_to_2) / 2
        speed_variance = ((speed_0_to_1 - avg_speed)**2 + (speed_1_to_2 - avg_speed)**2) / 2
        decel_rate = abs(acceleration) if acceleration < 0 else 0
        
        return {
            'time_0_to_1': time_0_to_1,
            'time_1_to_2': time_1_to_2,
            'speed_0_to_1': speed_0_to_1,
            'speed_1_to_2': speed_1_to_2,
            'acceleration': acceleration,
            'distance_remaining': distance_remaining,
            'avg_speed': avg_speed,
            'speed_variance': speed_variance,
            'decel_rate': decel_rate,
            'actual_eta': actual_eta
        }
    
    def train_model(self):
        from sklearn.tree import DecisionTreeRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, r2_score
        import pickle
        from datetime import datetime
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Training ETA model")
        
        df = pd.read_csv('outputs/data/eta_training.csv')
        
        if len(df) < 10:
            print(f"ERROR: Not enough samples ({len(df)})")
            return None
        
        X = df[self.features]
        y = df['actual_eta']
        
        print(f"Training on {len(df)} samples")
        
        if len(df) >= 20:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        else:
            X_train, X_test = X, X
            y_train, y_test = y, y
        
        best_mae = float('inf')
        best_model = None
        best_depth = None
        
        for depth in range(3, 9):
            model = DecisionTreeRegressor(
                max_depth=depth,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42
            )
            model.fit(X_train, y_train)
            
            pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, pred)
            
            if mae < best_mae and model.tree_.node_count <= 100:
                best_mae = mae
                best_model = model
                best_depth = depth
        
        print(f"Best model: Depth={best_depth}, MAE={best_mae:.3f}s, Nodes={best_model.tree_.node_count}")
        
        output_dir = Path('outputs/models')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / 'eta_model.pkl', 'wb') as f:
            pickle.dump(best_model, f)
        
        print("Model saved")
        
        return best_model


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', type=int, default=250)
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()
    
    if args.quick:
        args.samples = 20
    
    trainer = ETATrainer()
    
    df = trainer.collect_data(args.samples)
    if df is None:
        print("ERROR: Data collection failed")
        sys.exit(1)
    
    model = trainer.train_model()
    if model is None:
        print("ERROR: Model training failed")
        sys.exit(1)
    
    print("Training completed successfully")