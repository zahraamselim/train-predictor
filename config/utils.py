"""
System-wide configuration loader/writer.
Reads and writes config/system.yaml
"""

import yaml
from pathlib import Path


def get_config_path():
    """Get path to config/system.yaml"""
    current = Path(__file__).resolve().parent
    return current / 'system.yaml'


def load_config():
    """Load system configuration from YAML."""
    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_config(config):
    """Save system configuration to YAML."""
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_scale_config():
    """Get configuration for current scale mode."""
    config = load_config()
    scale_mode = config['system']['scale_mode']
    
    train_config = config['train'][f'{scale_mode}_scale']
    traffic_config = config['traffic'][f'{scale_mode}_scale']
    
    return {
        'scale_mode': scale_mode,
        'train': train_config,
        'traffic': traffic_config,
        'gates': config['gates'],
        'ir_sensors': config['ir_sensors'],
        'vehicle_clearance': config['vehicle_clearance'],
        'train_speeds': config['train_speeds'],
        'train_types': config['train_types'],
        'vehicle_types': config['vehicle_types']
    }


def get_unit():
    """Get current unit of measurement."""
    config = load_config()
    scale_mode = config['system']['scale_mode']
    return 'cm' if scale_mode == 'demo' else 'm'


def update_vehicle_clearance(density, min_time, max_time, avg_time):
    """Update vehicle clearance times after traffic simulation."""
    config = load_config()
    config['vehicle_clearance'][density] = {
        'min_time': float(min_time),
        'max_time': float(max_time),
        'avg_time': float(avg_time)
    }
    save_config(config)


def set_scale_mode(mode):
    """Change scale mode (demo or real)."""
    if mode not in ['demo', 'real']:
        raise ValueError("Scale mode must be 'demo' or 'real'")
    
    config = load_config()
    config['system']['scale_mode'] = mode
    save_config(config)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        try:
            set_scale_mode(mode)
            print(f"Scale mode set to: {mode}")
        except ValueError as e:
            print(f"Error: {e}")
            print("Usage: python -m config.utils [demo|real]")
            sys.exit(1)
    else:
        config = load_config()
        print(f"Current scale mode: {config['system']['scale_mode']}")