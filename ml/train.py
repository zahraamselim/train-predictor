"""Train and evaluate route optimizer model."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from route_optimizer import RouteOptimizer


def main():
    """Train route optimizer and save model."""
    data_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data_generation', 'data', 'decisions.csv'
    )
    
    if not os.path.exists(data_file):
        print(f"ERROR: Training data not found: {data_file}")
        print("Run: make data-decisions")
        return 1
    
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)
    output_model = os.path.join(model_dir, 'route_optimizer.pkl')
    
    print("Training Route Optimizer Model")
    print(f"Data: {data_file}")
    print(f"Output: {output_model}\n")
    
    optimizer = RouteOptimizer()
    metrics = optimizer.train(data_file)
    
    if metrics['test_accuracy'] > 0.8:
        optimizer.save_model(output_model)
        print("\nModel training successful!")
        
        print("\nTesting model with example scenarios:")
        
        test_scenarios = [
            {
                'train_eta': 30,
                'queue_length': 8,
                'traffic_density': 'heavy',
                'intersection_distance': 500,
                'alternative_route_distance': 1500,
                'description': 'Short ETA, long queue, long reroute'
            },
            {
                'train_eta': 90,
                'queue_length': 2,
                'traffic_density': 'light',
                'intersection_distance': 300,
                'alternative_route_distance': 600,
                'description': 'Long ETA, short queue, short reroute'
            },
            {
                'train_eta': 45,
                'queue_length': 5,
                'traffic_density': 'medium',
                'intersection_distance': 500,
                'alternative_route_distance': 1200,
                'description': 'Medium ETA, medium queue, medium reroute'
            }
        ]
        
        for scenario in test_scenarios:
            result = optimizer.predict(
                scenario['train_eta'],
                scenario['queue_length'],
                scenario['traffic_density'],
                scenario['intersection_distance'],
                scenario['alternative_route_distance']
            )
            
            print(f"\nScenario: {scenario['description']}")
            print(f"  ETA: {scenario['train_eta']}s, Queue: {scenario['queue_length']}, Density: {scenario['traffic_density']}")
            print(f"  Prediction: {result['action'].upper()} (confidence: {result['confidence']:.1%})")
        
        return 0
    else:
        print(f"\nWARNING: Model accuracy too low ({metrics['test_accuracy']:.1%})")
        print("Consider generating more training data")
        return 1


if __name__ == "__main__":
    sys.exit(main())