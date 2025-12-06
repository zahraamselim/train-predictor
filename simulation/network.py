import subprocess
import yaml
from pathlib import Path


class NetworkGenerator:
    def __init__(self, config_path='simulation/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.net = self.config['network']
        
    def generate(self):
        print("\nGenerating network...")
        
        self._create_nodes()
        self._create_edges()
        self._create_connections()
        self._create_config()
        
        if self._build_network():
            print("Network created successfully\n")
            return True
        return False
    
    def _create_nodes(self):
        road_sep = self.net['road_separation']
        cross_dist = self.net['crossing_distance']
        length = self.net['road_length']
        
        north_y = road_sep / 2
        south_y = -road_sep / 2
        west_x = -cross_dist / 2
        east_x = cross_dist / 2
        
        nodes = f"""<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="n_west" x="-{length}" y="{north_y}" type="priority"/>
    <node id="n_east" x="{length}" y="{north_y}" type="priority"/>
    <node id="s_west" x="-{length}" y="{south_y}" type="priority"/>
    <node id="s_east" x="{length}" y="{south_y}" type="priority"/>
    
    <node id="rail_west" x="-{length}" y="0" type="priority"/>
    <node id="rail_east" x="{length}" y="0" type="priority"/>
    
    <node id="nw_junction" x="{west_x}" y="{north_y}" type="priority"/>
    <node id="sw_junction" x="{west_x}" y="{south_y}" type="priority"/>
    <node id="west_crossing" x="{west_x}" y="0" type="rail_crossing"/>
    
    <node id="ne_junction" x="{east_x}" y="{north_y}" type="priority"/>
    <node id="se_junction" x="{east_x}" y="{south_y}" type="priority"/>
    <node id="east_crossing" x="{east_x}" y="0" type="rail_crossing"/>
</nodes>
"""
        Path('simulation.nod.xml').write_text(nodes)
    
    def _create_edges(self):
        edges = """<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <edge id="n_in_w" from="n_west" to="nw_junction" numLanes="1" speed="16.67"/>
    <edge id="n_w_e" from="nw_junction" to="ne_junction" numLanes="1" speed="16.67"/>
    <edge id="n_out_e" from="ne_junction" to="n_east" numLanes="1" speed="16.67"/>
    
    <edge id="s_in_w" from="s_west" to="sw_junction" numLanes="1" speed="16.67"/>
    <edge id="s_w_e" from="sw_junction" to="se_junction" numLanes="1" speed="16.67"/>
    <edge id="s_out_e" from="se_junction" to="s_east" numLanes="1" speed="16.67"/>
    
    <edge id="v_w_n_s" from="nw_junction" to="west_crossing" numLanes="1" speed="13.89"/>
    <edge id="v_w_x_s" from="west_crossing" to="sw_junction" numLanes="1" speed="13.89"/>
    
    <edge id="v_e_n_s" from="ne_junction" to="east_crossing" numLanes="1" speed="13.89"/>
    <edge id="v_e_x_s" from="east_crossing" to="se_junction" numLanes="1" speed="13.89"/>
    
    <edge id="rail_in" from="rail_west" to="west_crossing" numLanes="1" speed="33.33" allow="rail"/>
    <edge id="rail_mid" from="west_crossing" to="east_crossing" numLanes="1" speed="33.33" allow="rail"/>
    <edge id="rail_out" from="east_crossing" to="rail_east" numLanes="1" speed="33.33" allow="rail"/>
</edges>
"""
        Path('simulation.edg.xml').write_text(edges)
    
    def _create_connections(self):
        connections = """<?xml version="1.0" encoding="UTF-8"?>
<connections>
    <connection from="n_in_w" to="v_w_n_s" fromLane="0" toLane="0"/>
    <connection from="n_in_w" to="n_w_e" fromLane="0" toLane="0"/>
    <connection from="v_w_x_s" to="s_w_e" fromLane="0" toLane="0"/>
    <connection from="n_w_e" to="v_e_n_s" fromLane="0" toLane="0"/>
    <connection from="v_e_x_s" to="s_out_e" fromLane="0" toLane="0"/>
    <connection from="s_w_e" to="s_out_e" fromLane="0" toLane="0"/>
</connections>
"""
        Path('simulation.con.xml').write_text(connections)
    
    def _create_config(self):
        sim = self.config['simulation']
        
        config = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="simulation.net.xml"/>
        <route-files value="simulation.rou.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="{sim['duration']}"/>
        <step-length value="{sim['step_size']}"/>
    </time>
    <processing>
        <ignore-route-errors value="true"/>
        <time-to-teleport value="-1"/>
    </processing>
    <gui_only>
        <gui-settings-file value="view.xml"/>
    </gui_only>
</configuration>
"""
        Path('simulation.sumocfg').write_text(config)
        self._create_view_settings()
    
    def _create_view_settings(self):
        view = """<?xml version="1.0" encoding="UTF-8"?>
<viewsettings>
    <scheme name="realistic">
        <background backgroundColor="102,178,102" showGrid="0"/>
        <edges laneEdgeMode="0" scaleMode="0" laneShowBorders="1" 
            edgeColor="70,70,70" edgeColorSelected="255,255,0"
            edgeName.show="0" streetName.show="0"/>
        <vehicles vehicleQuality="3" vehicleSize="3.0" vehicleShape="3"
            showBlinker="1" drawMinGap="0" drawBrakeGap="0"
            vehicleName.show="0" vehicleColorMode="0"/>
        <junctions junctionMode="0" drawLinkTLIndex="0" drawLinkJunctionIndex="0"
            drawCrossingsAndWalkingareas="0" showLane2Lane="0"
            tlsPhaseIndex.show="0" junctionName.show="0"/>
    </scheme>
</viewsettings>"""
        Path('view.xml').write_text(view)
    
    def _build_network(self):
        result = subprocess.run([
            'netconvert',
            '--node-files=simulation.nod.xml',
            '--edge-files=simulation.edg.xml',
            '--connection-files=simulation.con.xml',
            '--output-file=simulation.net.xml',
            '--no-turnarounds'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Network build error: {result.stderr}")
        
        return result.returncode == 0


if __name__ == '__main__':
    generator = NetworkGenerator()
    generator.generate()