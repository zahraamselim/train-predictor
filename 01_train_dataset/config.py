"""
Project configuration for real-life and demo scales.

Real-life scale: Actual railway distances
Demo scale: Scaled down to fit 75x75cm board
"""

class ProjectConfig:
    """Configuration for level crossing system."""
    
    # Scale selection
    SCALE_MODE = 'demo'  # 'real' or 'demo'
    
    # Real-life scale (meters)
    REAL_SCALE = {
        'crossing_distance': 2000,      # Distance train starts from crossing
        'sensor_positions': [400, 250, 100],  # IR sensor distances from crossing
        'train_length': 150,            # Physical length of train
        'intersection_distances': [300, 500, 1000],  # Intersection to crossing distances
        'buffer_distance': 300,         # Extra distance after crossing
    }
    
    # Demo scale for 75x75cm board
    # Scale factor: 75cm board represents 2500m real distance
    # 1 cm = 33.33 meters
    SCALE_FACTOR = 33.33  # meters per cm
    
    DEMO_SCALE = {
        'crossing_distance': 60,        # 2000m / 33.33 ≈ 60cm
        'sensor_positions': [12, 7.5, 3],  # [400, 250, 100] / 33.33
        'train_length': 4.5,            # 150m / 33.33 ≈ 4.5cm
        'intersection_distances': [9, 15, 30],  # [300, 500, 1000] / 33.33
        'buffer_distance': 9,           # 300m / 33.33 ≈ 9cm
    }
    
    @classmethod
    def get_scale(cls):
        """Get current scale configuration."""
        if cls.SCALE_MODE == 'demo':
            return cls.DEMO_SCALE
        else:
            return cls.REAL_SCALE
    
    @classmethod
    def get_unit(cls):
        """Get current unit of measurement."""
        return 'cm' if cls.SCALE_MODE == 'demo' else 'm'
    
    @classmethod
    def set_scale(cls, mode: str):
        """Set scale mode."""
        if mode not in ['real', 'demo']:
            raise ValueError("Scale mode must be 'real' or 'demo'")
        cls.SCALE_MODE = mode
    
    @classmethod
    def to_real_distance(cls, demo_distance: float) -> float:
        """Convert demo scale distance to real scale."""
        return demo_distance * cls.SCALE_FACTOR
    
    @classmethod
    def to_demo_distance(cls, real_distance: float) -> float:
        """Convert real scale distance to demo scale."""
        return real_distance / cls.SCALE_FACTOR


# Convenience functions
def get_config():
    """Get current project configuration."""
    return ProjectConfig.get_scale()

def get_unit():
    """Get current unit."""
    return ProjectConfig.get_unit()

def set_scale(mode: str):
    """Set project scale mode."""
    ProjectConfig.set_scale(mode)