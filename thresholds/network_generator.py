"""
Generate SUMO network for threshold data collection
Run: python -m thresholds.network_generator
"""
import subprocess
import yaml
from pathlib import Path
from utils.logger import Logger

class ThresholdNetworkGenerator:
    def __init__(self, config_path='config/thresholds.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.prefix = 'thresholds'
    
    def generate(self):
        """Generate complete network for threshold collection"""
        Logger.section("Generating threshold collection network")
        
        self._create_nodes()
        self._create_edges()
        self._create_routes()
        self._create_config()
        
        if self._build_network():
            Logger.log("Network generated successfully")
            return True
        else:
            Logger.log("Network generation failed")
            return False
    
    def _create_nodes(self):
        """Create intersection nodes with rail crossing"""
        nodes = """<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="west_far" x="-800" y="0" type="priority"/>
    <node id="west_int" x="-300" y="0" type="traffic_light"/>
    <node id="crossing" x="0" y="0" type="rail_crossing"/>
    <node id="east_int" x="300" y="0" type="traffic_light"/>
    <node id="east_far" x="800" y="0" type="priority"/>
    
    <node id="rail_s" x="0" y="-1000" type="priority"/>
    <node id="rail_n" x="0" y="1000" type="priority"/>
    
    <node id="north" x="0" y="400" type="priority"/>
    <node id="south" x="0" y="-400" type="priority"/>
</nodes>
"""
        Path(f'{self.prefix}.nod.xml').write_text(nodes)
    
    def _create_edges(self):
        """Create road and rail edges"""
        edges = """<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <edge id="w_far_int" from="west_far" to="west_int" numLanes="2" speed="16.67"/>
    <edge id="w_int_cross" from="west_int" to="crossing" numLanes="2" speed="16.67"/>
    <edge id="cross_e_int" from="crossing" to="east_int" numLanes="2" speed="16.67"/>
    <edge id="e_int_far" from="east_int" to="east_far" numLanes="2" speed="16.67"/>
    
    <edge id="e_far_int" from="east_far" to="east_int" numLanes="2" speed="16.67"/>
    <edge id="e_int_cross" from="east_int" to="crossing" numLanes="2" speed="16.67"/>
    <edge id="cross_w_int" from="crossing" to="west_int" numLanes="2" speed="16.67"/>
    <edge id="w_int_far" from="west_int" to="west_far" numLanes="2" speed="16.67"/>
    
    <edge id="n_cross" from="north" to="crossing" numLanes="1" speed="13.89"/>
    <edge id="cross_s" from="crossing" to="south" numLanes="1" speed="13.89"/>
    <edge id="s_cross" from="south" to="crossing" numLanes="1" speed="13.89"/>
    <edge id="cross_n" from="crossing" to="north" numLanes="1" speed="13.89"/>
    
    <edge id="rail_track" from="rail_s" to="rail_n" numLanes="1" speed="38.89" allow="rail"/>
</edges>
"""
        Path(f'{self.prefix}.edg.xml').write_text(edges)
    
    def _create_routes(self):
        """Create traffic flows and train schedules"""
        cfg = self.config['data_collection']
        train = cfg['train']
        vehicle = cfg['vehicle']
        flow = cfg['vehicle_flow']
        
        routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="4.5" maxSpeed="{vehicle['max_speed']}" 
          accel="{vehicle['accel']}" decel="{vehicle['decel']}" 
          sigma="0.5" color="100,150,200"/>
    <vType id="truck" length="8.0" maxSpeed="{vehicle['max_speed'] * 0.9}" 
          accel="{vehicle['accel'] * 0.7}" decel="{vehicle['decel'] * 0.9}" 
          sigma="0.5" color="80,80,80"/>
    
    <vType id="train_slow" vClass="rail" length="{train['length']}" 
          maxSpeed="{train['min_speed']}" accel="0.5" decel="0.5" color="150,30,30"/>
    <vType id="train_med" vClass="rail" length="{train['length']}" 
          maxSpeed="{train['typical_speed']}" accel="0.8" decel="0.8" color="180,40,40"/>
    <vType id="train_fast" vClass="rail" length="{train['length']}" 
          maxSpeed="{train['max_speed']}" accel="1.2" decel="1.2" color="200,50,50"/>
    
    <route id="r_we" edges="w_far_int w_int_cross cross_e_int e_int_far"/>
    <route id="r_ew" edges="e_far_int e_int_cross cross_w_int w_int_far"/>
    <route id="r_ns" edges="n_cross cross_s"/>
    <route id="r_sn" edges="s_cross cross_n"/>
    <route id="r_rail" edges="rail_track"/>
    
    <flow id="f_cars_we" type="car" route="r_we" 
          begin="0" end="{cfg['duration']}" vehsPerHour="{flow['main_road']}"/>
    <flow id="f_cars_ew" type="car" route="r_ew" 
          begin="0" end="{cfg['duration']}" vehsPerHour="{flow['main_road']}"/>
    <flow id="f_trucks" type="truck" route="r_we" 
          begin="0" end="{cfg['duration']}" vehsPerHour="{flow['trucks']}"/>
    <flow id="f_side_ns" type="car" route="r_ns" 
          begin="0" end="{cfg['duration']}" vehsPerHour="{flow['side_roads']}"/>
    <flow id="f_side_sn" type="car" route="r_sn" 
          begin="0" end="{cfg['duration']}" vehsPerHour="{flow['side_roads']}"/>
    
    <flow id="f_train_slow" type="train_slow" route="r_rail" 
          begin="0" period="{cfg['train_period'] * 3}"/>
    <flow id="f_train_med" type="train_med" route="r_rail" 
          begin="{cfg['train_period']}" period="{cfg['train_period'] * 3}"/>
    <flow id="f_train_fast" type="train_fast" route="r_rail" 
          begin="{cfg['train_period'] * 2}" period="{cfg['train_period'] * 3}"/>
</routes>
"""
        Path(f'{self.prefix}.rou.xml').write_text(routes)
    
    def _create_config(self):
        """Create SUMO configuration"""
        cfg = self.config['data_collection']
        
        config = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="{self.prefix}.net.xml"/>
        <route-files value="{self.prefix}.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{cfg['duration']}"/>
        <step-length value="{cfg['step_length']}"/>
    </time>
    <processing>
        <collision.check-junctions value="true"/>
        <time-to-teleport value="-1"/>
    </processing>
    <output>
        <summary-output value="{self.prefix}_summary.xml"/>
    </output>
</configuration>
"""
        Path(f'{self.prefix}.sumocfg').write_text(config)
    
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
        
        return result.returncode == 0

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate threshold collection network')
    parser.add_argument('--config', default='config/thresholds.yaml', help='Config file path')
    args = parser.parse_args()
    
    generator = ThresholdNetworkGenerator(args.config)
    generator.generate()