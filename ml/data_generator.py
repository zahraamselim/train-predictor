"""
Data generation module using SUMO simulations
"""
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET
from utils import get_logger

class DataGenerator:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.data_dir = Path(config['output']['data_dir'])
        self.data_dir.mkdir(exist_ok=True)
        
    def create_network(self):
        """Create SUMO network from config"""
        nodes = f"""<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="start" x="{self.config['network']['start_x']}" y="0"/>
    <node id="end" x="{self.config['network']['end_x']}" y="0"/>
</nodes>"""
        
        edges = f"""<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <edge id="track" from="start" to="end" priority="1" numLanes="1" 
          speed="{self.config['network']['max_speed']}"/>
</edges>"""
        
        Path('rail.nod.xml').write_text(nodes)
        Path('rail.edg.xml').write_text(edges)
        
        result = subprocess.run([
            'netconvert', 
            '--node-files=rail.nod.xml', 
            '--edge-files=rail.edg.xml',
            '--output-file=rail.net.xml', 
            '--no-turnarounds',
            '--no-warnings'
        ], capture_output=True, text=True)
        
        return result.returncode == 0
    
    def generate_train_params(self, n_samples):
        """Generate diverse train parameters"""
        np.random.seed(self.config['training']['random_seed'])
        
        params = []
        speed_dist = self.config['training']['speed_distribution']
        train_cfg = self.config['training']['train_params']
        
        for _ in range(n_samples):
            speed_type = np.random.choice(['fast', 'medium', 'slow'], p=[0.3, 0.5, 0.2])
            
            speed_range = speed_dist[speed_type]
            speed = np.random.uniform(speed_range['min'], speed_range['max'])
            
            accel_min, accel_max = train_cfg['accel_range']
            decel_min, decel_max = train_cfg['decel_range']
            
            if speed_type == 'fast':
                accel = np.random.uniform(1.5, accel_max)
                decel = np.random.uniform(1.5, decel_max)
            elif speed_type == 'medium':
                accel = np.random.uniform(0.8, 1.5)
                decel = np.random.uniform(0.8, 1.5)
            else:
                accel = np.random.uniform(accel_min, 0.8)
                decel = np.random.uniform(decel_min, 0.8)
            
            if np.random.random() < 0.2:
                accel *= np.random.uniform(0.5, 0.7)
            
            if np.random.random() < 0.15:
                decel *= np.random.uniform(1.3, 1.8)
            
            sf_min, sf_max = train_cfg['speed_factor_range']
            
            params.append({
                'depart_speed': speed,
                'accel': accel,
                'decel': decel,
                'length': np.random.choice(train_cfg['lengths']),
                'speed_factor': np.random.uniform(sf_min, sf_max)
            })
        
        return params
    
    def run_simulation(self, train_params, run_id):
        """Run single SUMO simulation"""
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
        
        config = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="rail.net.xml"/>
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
        
        result = subprocess.run(
            ['sumo', '-c', config_file, '--no-step-log', '--no-warnings'], 
            capture_output=True
        )
        
        Path(route_file).unlink(missing_ok=True)
        Path(config_file).unlink(missing_ok=True)
        
        if result.returncode != 0:
            return None
        
        fcd_file = f'temp_fcd_{run_id}.xml'
        if not Path(fcd_file).exists():
            return None
        
        data = self.parse_fcd(fcd_file, run_id)
        Path(fcd_file).unlink(missing_ok=True)
        
        return data
    
    def parse_fcd(self, fcd_file, run_id):
        """Parse FCD XML output"""
        try:
            tree = ET.parse(fcd_file)
            root = tree.getroot()
        except:
            return None
        
        data = []
        for timestep in root.findall('timestep'):
            time = float(timestep.get('time'))
            for vehicle in timestep.findall('vehicle'):
                if vehicle.get('id').startswith('train_'):
                    data.append({
                        'time': time,
                        'pos': float(vehicle.get('pos')),
                        'speed': float(vehicle.get('speed')),
                        'acceleration': float(vehicle.get('acceleration', 0)),
                        'run_id': run_id
                    })
        
        return pd.DataFrame(data) if data else None
    
    def run(self):
        """Execute full data generation pipeline"""
        self.logger.info("Creating SUMO network")
        if not self.create_network():
            self.logger.error("Network creation failed")
            return None
        
        n_samples = self.config['training']['n_samples']
        self.logger.info(f"Generating {n_samples} simulation samples")
        
        train_params = self.generate_train_params(n_samples)
        all_data = []
        successful = 0
        
        for i, params in enumerate(train_params):
            df = self.run_simulation(params, i)
            
            if df is not None and len(df) > 10:
                all_data.append(df)
                successful += 1
                
                if (i + 1) % 50 == 0:
                    self.logger.info(f"Progress: {successful}/{i+1} ({successful/(i+1)*100:.1f}%)")
        
        if not all_data:
            self.logger.error("No successful simulations")
            return None
        
        combined = pd.concat(all_data, ignore_index=True)
        output_path = self.data_dir / 'raw_trajectories.csv'
        combined.to_csv(output_path, index=False)
        
        self.logger.info(f"Generated {successful} trajectories with {len(combined)} data points")
        self.logger.info(f"Saved to {output_path}")
        
        return combined