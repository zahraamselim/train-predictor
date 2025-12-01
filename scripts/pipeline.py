"""
Complete Pipeline
Executes full workflow from network generation to Arduino export
"""
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.network.generator import NetworkGenerator
from simulation.data.collector import DataCollector
from simulation.data.analyzer import ThresholdAnalyzer
from simulation.ml.train_eta import ETADataCollector, ETAModelTrainer
from simulation.ml.export import ArduinoExporter


class Pipeline:
    def __init__(self):
        self.steps = [
            ('generate_network', self.generate_network),
            ('collect_data', self.collect_data),
            ('analyze_thresholds', self.analyze_thresholds),
            ('collect_eta_data', self.collect_eta_data),
            ('train_model', self.train_model),
            ('export_arduino', self.export_arduino)
        ]
    
    def run(self, steps=None):
        """Run pipeline steps"""
        print(f"[{self._timestamp()}] Starting pipeline")
        
        if steps:
            steps_to_run = [(name, func) for name, func in self.steps if name in steps]
        else:
            steps_to_run = self.steps
        
        for i, (name, func) in enumerate(steps_to_run, 1):
            print(f"\n[{self._timestamp()}] Step {i}/{len(steps_to_run)}: {name}")
            
            try:
                func()
            except Exception as e:
                print(f"[{self._timestamp()}] Error in {name}: {e}")
                return False
        
        print(f"\n[{self._timestamp()}] Pipeline completed successfully")
        return True
    
    def generate_network(self):
        """Generate SUMO network"""
        generator = NetworkGenerator()
        if not generator.generate():
            raise Exception("Network generation failed")
    
    def collect_data(self):
        """Collect training data"""
        collector = DataCollector()
        collector.run(duration=3600)
    
    def analyze_thresholds(self):
        """Analyze and calculate thresholds"""
        analyzer = ThresholdAnalyzer()
        analyzer.analyze()
    
    def collect_eta_data(self):
        """Collect ETA training data"""
        collector = ETADataCollector()
        collector.collect(num_samples=250)
    
    def train_model(self):
        """Train ETA prediction model"""
        trainer = ETAModelTrainer()
        trainer.train()
    
    def export_arduino(self):
        """Export to Arduino"""
        exporter = ArduinoExporter()
        exporter.export_model()
        exporter.export_config()
    
    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--steps', nargs='+', 
                       choices=['generate_network', 'collect_data', 'analyze_thresholds',
                               'collect_eta_data', 'train_model', 'export_arduino'],
                       help='Specific steps to run')
    parser.add_argument('--all', action='store_true', help='Run all steps')
    
    args = parser.parse_args()
    
    pipeline = Pipeline()
    
    if args.all or not args.steps:
        success = pipeline.run()
    else:
        success = pipeline.run(steps=args.steps)
    
    sys.exit(0 if success else 1)