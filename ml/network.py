"""
Train network generator for SUMO simulations
"""
import subprocess
from pathlib import Path
import yaml
from utils.logger import Logger


class NetworkGenerator:
    def __init__(self, config_path='config/ml.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.prefix = 'training'
    
    def generate(self):
        """Generate complete network for training data collection"""
        Logger.section("Generating training network")
        
        self._create_nodes()
        self._create_edges()
        
        if self._build_network():
            Logger.log("Network generated successfully")
            return f'{self.prefix}.net.xml'
        else:
            Logger.log("Network generation failed")
            return None
    
    def _create_nodes(self):
        """Create simple linear track nodes"""
        nodes = f"""<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="start" x="{self.config['network']['start_x']}" y="0"/>
    <node id="end" x="{self.config['network']['end_x']}" y="0"/>
</nodes>"""
        
        Path(f'{self.prefix}.nod.xml').write_text(nodes)
    
    def _create_edges(self):
        """Create track edge"""
        edges = f"""<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <edge id="track" from="start" to="end" priority="1" numLanes="1" 
          speed="{self.config['network']['max_speed']}"/>
</edges>"""
        
        Path(f'{self.prefix}.edg.xml').write_text(edges)
    
    def _build_network(self):
        """Build network using netconvert"""
        result = subprocess.run([
            'netconvert',
            f'--node-files={self.prefix}.nod.xml',
            f'--edge-files={self.prefix}.edg.xml',
            f'--output-file={self.prefix}.net.xml',
            '--no-turnarounds',
            '--no-warnings'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            Logger.log(f"Network creation failed: {result.stderr}")
            return False
        
        return True
    
    def generate_route_file(self, train_params, run_id):
        """Generate SUMO route file for a train"""
        p = train_params
        
        routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="train_{run_id}" length="{p['length']}" 
           maxSpeed="{self.config['network']['max_speed']}" 
           accel="{p['accel']}" decel="{p['decel']}" 
           speedFactor="{p['speed_factor']}" 
           speedDev="0" color="1,0,0"/>
    <route id="route_{run_id}" edges="track"/>
    <vehicle id="train_{run_id}" type="train_{run_id}" route="route_{run_id}" 
             depart="0" departSpeed="{p['depart_speed']}"/>
</routes>"""
        
        route_file = f'temp_route_{run_id}.rou.xml'
        Path(route_file).write_text(routes)
        return route_file
    
    def generate_config_file(self, route_file, run_id, net_file=None):
        """Generate SUMO configuration file"""
        if net_file is None:
            net_file = f'{self.prefix}.net.xml'
        
        config = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="{net_file}"/>
        <route-files value="{route_file}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{self.config['training']['sim_duration']}"/>
        <step-length value="0.1"/>
    </time>
    <output>
        <fcd-output value="temp_fcd_{run_id}.xml"/>
    </output>
    <processing>
        <time-to-teleport value="-1"/>
    </processing>
</configuration>"""
        
        config_file = f'temp_config_{run_id}.sumocfg'
        Path(config_file).write_text(config)
        return config_file


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate training network')
    parser.add_argument('--config', default='config/ml.yaml', help='Config file path')
    args = parser.parse_args()
    
    generato(args.config)
    generator.generate()