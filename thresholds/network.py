"""
Generate SUMO network for threshold data collection
Run: python -m thresholds.network
"""
import subprocess
import yaml
from pathlib import Path
from utils.logger import Logger


class NetworkGenerator:
    def __init__(self, config_path='thresholds/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
    
    def generate(self):
        """Generate complete SUMO network"""
        Logger.section("Generating network")
        
        self._create_nodes()
        self._create_edges()
        self._create_routes()
        self._create_config()
        
        result = subprocess.run([
            'netconvert',
            '--node-files=thresholds.nod.xml',
            '--edge-files=thresholds.edg.xml',
            '--output-file=thresholds.net.xml',
            '--no-warnings'
        ], capture_output=True)
        
        if result.returncode == 0:
            Logger.log("Network generated")
            return True
        else:
            Logger.log("Network generation failed")
            return False
    
    def _create_nodes(self):
        """Create nodes"""
        nodes = """<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="west_far" x="-800" y="0" type="priority"/>
    <node id="west_int" x="-300" y="0" type="traffic_light"/>
    <node id="crossing" x="0" y="0" type="rail_crossing"/>
    <node id="east_int" x="300" y="0" type="traffic_light"/>
    <node id="east_far" x="800" y="0" type="priority"/>
    <node id="rail_s" x="0" y="-1000" type="priority"/>
    <node id="rail_n" x="0" y="1000" type="priority"/>
</nodes>"""
        Path('thresholds.nod.xml').write_text(nodes)
    
    def _create_edges(self):
        """Create edges"""
        edges = """<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <edge id="we1" from="west_far" to="west_int" numLanes="2" speed="16.67"/>
    <edge id="we2" from="west_int" to="crossing" numLanes="2" speed="16.67"/>
    <edge id="we3" from="crossing" to="east_int" numLanes="2" speed="16.67"/>
    <edge id="we4" from="east_int" to="east_far" numLanes="2" speed="16.67"/>
    <edge id="ew1" from="east_far" to="east_int" numLanes="2" speed="16.67"/>
    <edge id="ew2" from="east_int" to="crossing" numLanes="2" speed="16.67"/>
    <edge id="ew3" from="crossing" to="west_int" numLanes="2" speed="16.67"/>
    <edge id="ew4" from="west_int" to="west_far" numLanes="2" speed="16.67"/>
    <edge id="rail" from="rail_s" to="rail_n" numLanes="1" speed="40" allow="rail"/>
</edges>"""
        Path('thresholds.edg.xml').write_text(edges)
    
    def _create_routes(self):
        """Create routes and traffic"""
        cfg = self.config['data_collection']
        
        routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="4.5" maxSpeed="20" accel="2.6" decel="4.5" color="100,150,200"/>
    <vType id="train_slow" vClass="rail" length="150" maxSpeed="25" color="150,30,30"/>
    <vType id="train_med" vClass="rail" length="150" maxSpeed="33" color="180,40,40"/>
    <vType id="train_fast" vClass="rail" length="150" maxSpeed="39" color="200,50,50"/>
    
    <route id="r_we" edges="we1 we2 we3 we4"/>
    <route id="r_ew" edges="ew1 ew2 ew3 ew4"/>
    <route id="r_rail" edges="rail"/>
    
    <flow id="cars_we" type="car" route="r_we" begin="0" end="{cfg['duration']}" vehsPerHour="400"/>
    <flow id="cars_ew" type="car" route="r_ew" begin="0" end="{cfg['duration']}" vehsPerHour="400"/>
    <flow id="trains_s" type="train_slow" route="r_rail" begin="0" period="540"/>
    <flow id="trains_m" type="train_med" route="r_rail" begin="180" period="540"/>
    <flow id="trains_f" type="train_fast" route="r_rail" begin="360" period="540"/>
</routes>"""
        Path('thresholds.rou.xml').write_text(routes)
    
    def _create_config(self):
        """Create SUMO config"""
        cfg = self.config['data_collection']
        
        config = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="thresholds.net.xml"/>
        <route-files value="thresholds.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{cfg['duration']}"/>
    </time>
</configuration>"""
        Path('thresholds.sumocfg').write_text(config)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate network')
    parser.add_argument('--config', default='thresholds/config.yaml', help='Config file')
    args = parser.parse_args()
    
    generator = NetworkGenerator(args.config)
    generator.generate()