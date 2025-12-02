import sys
import os
sys.path.insert(0, '/app')

from datetime import datetime

def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log(message):
    print(f"[{timestamp()}] {message}")

def section(title):
    print(f"\n[{timestamp()}] {title}")

class Pipeline:
    """Execute full workflow"""
    
    def __init__(self):
        self.steps = {
            'network': self.generate_network,
            'data': self.collect_data,
            'analyze': self.analyze_thresholds,
            'train': self.train_model,
            'export': self.export_arduino
        }
    
    def run(self, step_names=None):
        section("Starting pipeline")
        
        steps_to_run = step_names or list(self.steps.keys())
        
        for i, name in enumerate(steps_to_run, 1):
            section(f"Step {i}/{len(steps_to_run)}: {name}")
            
            try:
                self.steps[name]()
            except Exception as e:
                log(f"ERROR in {name}: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        section("Pipeline completed")
        return True
    
    def generate_network(self):
        from simulation.network.generator import NetworkGenerator
        generator = NetworkGenerator(mode="complete")
        if not generator.generate():
            raise Exception("Network generation failed")
    
    def collect_data(self):
        from simulation.data.collector import DataCollector
        collector = DataCollector()
        collector.run(duration=3600)
    
    def analyze_thresholds(self):
        from simulation.data.analyzer import ThresholdAnalyzer
        analyzer = ThresholdAnalyzer()
        analyzer.analyze()
    
    def train_model(self):
        from simulation.ml.trainer import ETATrainer
        trainer = ETATrainer()
        df = trainer.collect_data(num_samples=250)
        if df is None:
            raise Exception("Data collection failed")
        
        model = trainer.train_model()
        if model is None:
            raise Exception("Model training failed")
    
    def export_arduino(self):
        from simulation.ml.exporter import ArduinoExporter
        exporter = ArduinoExporter()
        exporter.export_model()
        exporter.export_config()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--steps', nargs='+', 
                       choices=['network', 'data', 'analyze', 'train', 'export'],
                       help='Specific steps to run')
    
    args = parser.parse_args()
    
    pipeline = Pipeline()
    success = pipeline.run(args.steps)
    
    sys.exit(0 if success else 1)