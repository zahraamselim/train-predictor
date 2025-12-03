"""
Generate SUMO network for simulation
Run: python -m simulation.network_generator
"""
import os
import yaml
from pathlib import Path
from utils.logger import Logger

class NetworkGenerator:
    def __init__(self, config_path='config/simulation.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.output_dir = Path('sumo/complete')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self):
        """Generate complete SUMO network"""
        Logger.section("Generating SUMO network")
        
        self._write_nodes()
        self._write_edges()
        self._write_routes()
        self._write_config()
        self._write_viewsettings()
        
        if self._build_network():
            Logger.log("Network generated successfully")
            return True
        else:
            Logger.log("Network generation failed")
            return False
    
    def _write_nodes(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="n_w" x="-500" y="100" type="priority"/>
    <node id="n_e" x="500" y="100" type="priority"/>
    <node id="s_w" x="-500" y="-100" type="priority"/>
    <node id="s_e" x="500" y="-100" type="priority"/>
    
    <node id="rail_w" x="-1500" y="0" type="priority"/>
    <node id="rail_e" x="1500" y="0" type="priority"/>
    
    <node id="cross_w_n" x="-200" y="100" type="traffic_light"/>
    <node id="cross_w_rail" x="-200" y="0" type="rail_crossing"/>
    <node id="cross_w_s" x="-200" y="-100" type="traffic_light"/>
    
    <node id="cross_e_n" x="200" y="100" type="traffic_light"/>
    <node id="cross_e_rail" x="200" y="0" type="rail_crossing"/>
    <node id="cross_e_s" x="200" y="-100" type="traffic_light"/>
</nodes>
"""
        (self.output_dir / 'network.nod.xml').write_text(content)
    
    def _write_edges(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <edge id="n_e_to_cross_e" from="n_e" to="cross_e_n" numLanes="2" speed="16.67"/>
    <edge id="cross_e_to_cross_w_n" from="cross_e_n" to="cross_w_n" numLanes="2" speed="16.67"/>
    <edge id="cross_w_to_n_w" from="cross_w_n" to="n_w" numLanes="2" speed="16.67"/>
    
    <edge id="n_w_to_cross_w" from="n_w" to="cross_w_n" numLanes="2" speed="16.67"/>
    <edge id="cross_w_to_cross_e_n" from="cross_w_n" to="cross_e_n" numLanes="2" speed="16.67"/>
    <edge id="cross_e_to_n_e" from="cross_e_n" to="n_e" numLanes="2" speed="16.67"/>
    
    <edge id="s_e_to_cross_e" from="s_e" to="cross_e_s" numLanes="2" speed="16.67"/>
    <edge id="cross_e_to_cross_w_s" from="cross_e_s" to="cross_w_s" numLanes="2" speed="16.67"/>
    <edge id="cross_w_to_s_w" from="cross_w_s" to="s_w" numLanes="2" speed="16.67"/>
    
    <edge id="s_w_to_cross_w" from="s_w" to="cross_w_s" numLanes="2" speed="16.67"/>
    <edge id="cross_w_to_cross_e_s" from="cross_w_s" to="cross_e_s" numLanes="2" speed="16.67"/>
    <edge id="cross_e_to_s_e" from="cross_e_s" to="s_e" numLanes="2" speed="16.67"/>
    
    <edge id="vert_w_s_to_rail" from="cross_w_s" to="cross_w_rail" numLanes="1" speed="13.89"/>
    <edge id="vert_w_rail_to_n" from="cross_w_rail" to="cross_w_n" numLanes="1" speed="13.89"/>
    <edge id="vert_w_n_to_rail" from="cross_w_n" to="cross_w_rail" numLanes="1" speed="13.89"/>
    <edge id="vert_w_rail_to_s" from="cross_w_rail" to="cross_w_s" numLanes="1" speed="13.89"/>
    
    <edge id="vert_e_s_to_rail" from="cross_e_s" to="cross_e_rail" numLanes="1" speed="13.89"/>
    <edge id="vert_e_rail_to_n" from="cross_e_rail" to="cross_e_n" numLanes="1" speed="13.89"/>
    <edge id="vert_e_n_to_rail" from="cross_e_n" to="cross_e_rail" numLanes="1" speed="13.89"/>
    <edge id="vert_e_rail_to_s" from="cross_e_rail" to="cross_e_s" numLanes="1" speed="13.89"/>
    
    <edge id="rail_w_to_cross_w" from="rail_w" to="cross_w_rail" numLanes="1" speed="33.33" allow="rail"/>
    <edge id="rail_cross_w_to_e" from="cross_w_rail" to="cross_e_rail" numLanes="1" speed="33.33" allow="rail"/>
    <edge id="rail_cross_e_to_e" from="cross_e_rail" to="rail_e" numLanes="1" speed="33.33" allow="rail"/>
</edges>
"""
        (self.output_dir / 'network.edg.xml').write_text(content)
    
    def _write_routes(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="4.5" maxSpeed="20" accel="2.6" decel="4.5" sigma="0.5" color="100,150,200"/>
    <vType id="truck" length="8.0" maxSpeed="18" accel="1.8" decel="4.0" sigma="0.5" color="80,80,80"/>
    <vType id="train" vClass="rail" length="150" maxSpeed="33.33" accel="0.5" decel="0.5" color="150,30,30"/>
    
    <route id="r_north_eb" edges="n_w_to_cross_w cross_w_to_cross_e_n cross_e_to_n_e"/>
    <route id="r_north_wb" edges="n_e_to_cross_e cross_e_to_cross_w_n cross_w_to_n_w"/>
    <route id="r_south_eb" edges="s_w_to_cross_w cross_w_to_cross_e_s cross_e_to_s_e"/>
    <route id="r_south_wb" edges="s_e_to_cross_e cross_e_to_cross_w_s cross_w_to_s_w"/>
    
    <route id="r_vert_w_nb" edges="vert_w_s_to_rail vert_w_rail_to_n"/>
    <route id="r_vert_w_sb" edges="vert_w_n_to_rail vert_w_rail_to_s"/>
    <route id="r_vert_e_nb" edges="vert_e_s_to_rail vert_e_rail_to_n"/>
    <route id="r_vert_e_sb" edges="vert_e_n_to_rail vert_e_rail_to_s"/>
    
    <route id="r_rail" edges="rail_w_to_cross_w rail_cross_w_to_e rail_cross_e_to_e"/>
    
    <flow id="flow_north_eb" type="car" route="r_north_eb" begin="0" end="3600" vehsPerHour="200"/>
    <flow id="flow_north_wb" type="car" route="r_north_wb" begin="0" end="3600" vehsPerHour="200"/>
    <flow id="flow_south_eb" type="car" route="r_south_eb" begin="0" end="3600" vehsPerHour="200"/>
    <flow id="flow_south_wb" type="car" route="r_south_wb" begin="0" end="3600" vehsPerHour="200"/>
    
    <flow id="flow_vert_w_nb" type="car" route="r_vert_w_nb" begin="0" end="3600" vehsPerHour="80"/>
    <flow id="flow_vert_w_sb" type="car" route="r_vert_w_sb" begin="0" end="3600" vehsPerHour="80"/>
    <flow id="flow_vert_e_nb" type="car" route="r_vert_e_nb" begin="0" end="3600" vehsPerHour="80"/>
    <flow id="flow_vert_e_sb" type="car" route="r_vert_e_sb" begin="0" end="3600" vehsPerHour="80"/>
    
    <flow id="flow_trucks" type="truck" route="r_north_eb" begin="0" end="3600" vehsPerHour="50"/>
    <flow id="flow_trains" type="train" route="r_rail" begin="0" end="3600" period="300"/>
</routes>
"""
        (self.output_dir / 'routes.rou.xml').write_text(content)
    
    def _write_config(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="network.net.xml"/>
        <route-files value="routes.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <step-length value="0.1"/>
    </time>
    <processing>
        <collision.check-junctions value="true"/>
        <time-to-teleport value="-1"/>
    </processing>
</configuration>
"""
        (self.output_dir / 'simulation.sumocfg').write_text(content)
    
    def _write_viewsettings(self):
        content = """<viewsettings>
    <scheme name="crossing_view">
        <background backgroundColor="34,139,34" showGrid="0"/>
        <edges laneEdgeMode="0" scaleMode="0" laneShowBorders="1" showRails="1" railWidth="5.0"/>
        <vehicles vehicleQuality="2" vehicleSize="2.0" showBlinker="1"/>
        <junctions showLane2Lane="0" drawCrossingsAndWalkingareas="1"/>
    </scheme>
</viewsettings>
"""
        (self.output_dir / 'viewsettings.xml').write_text(content)
    
    def _build_network(self):
        cmd = (
            f"netconvert "
            f"--node-files={self.output_dir}/network.nod.xml "
            f"--edge-files={self.output_dir}/network.edg.xml "
            f"--output-file={self.output_dir}/network.net.xml "
            f"--no-warnings"
        )
        return os.system(cmd) == 0

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate SUMO network')
    parser.add_argument('--config', default='config/simulation.yaml', help='Config file path')
    args = parser.parse_args()
    
    generator = NetworkGenerator(args.config)
    generator.generate()