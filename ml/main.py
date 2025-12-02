#!/usr/bin/env python3
"""
Main training script for Train ETA prediction system
"""
import argparse
from pathlib import Path
from data_generator import DataGenerator
from feature_extractor import FeatureExtractor
from model_trainer import ModelTrainer
from model_exporter import ModelExporter
from evaluator import ModelEvaluator
from utils import load_config, setup_logging

def main():
    parser = argparse.ArgumentParser(description='Train ETA Prediction System')
    parser.add_argument('--config', type=str, default='config.yaml', help='Config file path')
    parser.add_argument('--samples', type=int, default=None, help='Number of samples (overrides config)')
    parser.add_argument('--quick', action='store_true', help='Quick test with 50 samples')
    parser.add_argument('--visualize', action='store_true', help='Run visualization after training')
    args = parser.parse_args()
    
    logger = setup_logging()
    
    if args.quick:
        samples = 50
    elif args.samples:
        samples = args.samples
    else:
        samples = None
    
    logger.info("Starting Train ETA ML Pipeline")
    
    config = load_config(args.config)
    if samples:
        config['training']['n_samples'] = samples
    
    # Stage 1: Generate simulation data
    logger.info("Stage 1: Data Generation")
    generator = DataGenerator(config)
    trajectory_df = generator.run()
    
    if trajectory_df is None or len(trajectory_df) == 0:
        logger.error("Data generation failed")
        return 1
    
    # Stage 2: Feature extraction
    logger.info("Stage 2: Feature Extraction")
    extractor = FeatureExtractor(config)
    features_df = extractor.extract(trajectory_df)
    
    if features_df is None or len(features_df) < 20:
        logger.error("Feature extraction failed or insufficient features")
        return 1
    
    # Stage 3: Model training
    logger.info("Stage 3: Model Training")
    trainer = ModelTrainer(config)
    model, metrics = trainer.train(features_df)
    
    if model is None:
        logger.error("Model training failed")
        return 1
    
    # Stage 4: Model evaluation
    logger.info("Stage 4: Model Evaluation")
    evaluator = ModelEvaluator(config)
    evaluator.evaluate(model, features_df, metrics)
    
    # Stage 5: Export for deployment
    logger.info("Stage 5: Model Export")
    exporter = ModelExporter(config)
    exporter.export_arduino(model)
    exporter.export_python(model)
    
    logger.info("Training pipeline completed successfully")
    
    if args.visualize:
        logger.info("Launching visualization")
        from src.visualizer import run_visualization
        run_visualization(config)
    
    return 0

if __name__ == '__main__':
    exit(main())