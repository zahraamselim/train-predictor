import subprocess
import yaml
from pathlib import Path
from utils.logger import Logger


class NetworkGenerator:
    def __init__(self, config_path='simulation/config.yaml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.net = self.config['network']
        
    def generate(self):
        Logger.section("Generating network")
        
        self._create_nodes()
        self._create_edges()
        self._create_routes()
        self._create_config()
        
        if self._build_network():
            Logger.log("Network created successfully")
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
    
    <node id="nw_junction" x="{west_x}" y="{north_y}" type="traffic_light"/>
    <node id="sw_junction" x="{west_x}" y="{south_y}" type="traffic_light"/>
    <node id="west_crossing" x="{west_x}" y="0" type="rail_crossing"/>
    
    <node id="ne_junction" x="{east_x}" y="{north_y}" type="traffic_light"/>
    <node id="se_junction" x="{east_x}" y="{south_y}" type="traffic_light"/>
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
    
    <edge id="n_in_e" from="n_east" to="ne_junction" numLanes="1" speed="16.67"/>
    <edge id="n_e_w" from="ne_junction" to="nw_junction" numLanes="1" speed="16.67"/>
    <edge id="n_out_w" from="nw_junction" to="n_west" numLanes="1" speed="16.67"/>
    
    <edge id="s_in_w" from="s_west" to="sw_junction" numLanes="1" speed="16.67"/>
    <edge id="s_w_e" from="sw_junction" to="se_junction" numLanes="1" speed="16.67"/>
    <edge id="s_out_e" from="se_junction" to="s_east" numLanes="1" speed="16.67"/>
    
    <edge id="s_in_e" from="s_east" to="se_junction" numLanes="1" speed="16.67"/>
    <edge id="s_e_w" from="se_junction" to="sw_junction" numLanes="1" speed="16.67"/>
    <edge id="s_out_w" from="sw_junction" to="s_west" numLanes="1" speed="16.67"/>
    
    <edge id="v_w_n_s" from="nw_junction" to="west_crossing" numLanes="1" speed="13.89"/>
    <edge id="v_w_x_s" from="west_crossing" to="sw_junction" numLanes="1" speed="13.89"/>
    <edge id="v_w_s_n" from="sw_junction" to="west_crossing" numLanes="1" speed="13.89"/>
    <edge id="v_w_x_n" from="west_crossing" to="nw_junction" numLanes="1" speed="13.89"/>
    
    <edge id="v_e_n_s" from="ne_junction" to="east_crossing" numLanes="1" speed="13.89"/>
    <edge id="v_e_x_s" from="east_crossing" to="se_junction" numLanes="1" speed="13.89"/>
    <edge id="v_e_s_n" from="se_junction" to="east_crossing" numLanes="1" speed="13.89"/>
    <edge id="v_e_x_n" from="east_crossing" to="ne_junction" numLanes="1" speed="13.89"/>
    
    <edge id="rail_in" from="rail_west" to="west_crossing" numLanes="1" speed="33.33" allow="rail"/>
    <edge id="rail_mid" from="west_crossing" to="east_crossing" numLanes="1" speed="33.33" allow="rail"/>
    <edge id="rail_out" from="east_crossing" to="rail_east" numLanes="1" speed="33.33" allow="rail"/>
</edges>
"""
        Path('simulation.edg.xml').write_text(edges)
    
    def _create_routes(self):
        traffic = self.config['traffic']
        duration = self.config['simulation']['duration']
        
        routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="car" length="4.5" width="2.0" height="1.5" maxSpeed="20" accel="2.6" decel="4.5" sigma="0.5" 
        color="70,130,180" guiShape="passenger" imgFile="car.png"/>
    <vType id="train" vClass="rail" length="150" width="3.5" height="4.0" maxSpeed="33.33" accel="0.5" decel="0.5" 
        color="178,34,34" guiShape="rail" imgFile="train.png"/>
    
    <route id="north_eastbound" edges="n_in_w n_w_e n_out_e"/>
    <route id="north_westbound" edges="n_in_e n_e_w n_out_w"/>
    <route id="south_eastbound" edges="s_in_w s_w_e s_out_e"/>
    <route id="south_westbound" edges="s_in_e s_e_w s_out_w"/>
    
    <route id="west_north_south" edges="v_w_n_s v_w_x_s"/>
    <route id="west_south_north" edges="v_w_s_n v_w_x_n"/>
    <route id="east_north_south" edges="v_e_n_s v_e_x_s"/>
    <route id="east_south_north" edges="v_e_s_n v_e_x_n"/>
    
    <route id="train_route" edges="rail_in rail_mid rail_out"/>
    
    <flow id="f_north_eb" type="car" route="north_eastbound" begin="0" end="{duration}" vehsPerHour="{traffic['cars_per_hour']}"/>
    <flow id="f_north_wb" type="car" route="north_westbound" begin="0" end="{duration}" vehsPerHour="{traffic['cars_per_hour']}"/>
    <flow id="f_south_eb" type="car" route="south_eastbound" begin="0" end="{duration}" vehsPerHour="{traffic['cars_per_hour']}"/>
    <flow id="f_south_wb" type="car" route="south_westbound" begin="0" end="{duration}" vehsPerHour="{traffic['cars_per_hour']}"/>
    
    <flow id="f_west_ns" type="car" route="west_north_south" begin="0" end="{duration}" vehsPerHour="{traffic['cars_per_hour']//4}"/>
    <flow id="f_west_sn" type="car" route="west_south_north" begin="0" end="{duration}" vehsPerHour="{traffic['cars_per_hour']//4}"/>
    <flow id="f_east_ns" type="car" route="east_north_south" begin="0" end="{duration}" vehsPerHour="{traffic['cars_per_hour']//4}"/>
    <flow id="f_east_sn" type="car" route="east_south_north" begin="0" end="{duration}" vehsPerHour="{traffic['cars_per_hour']//4}"/>
    
    <flow id="f_trains" type="train" route="train_route" begin="0" end="{duration}" period="{traffic['train_interval']}"/>
</routes>
"""
        Path('simulation.rou.xml').write_text(routes)
    
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
            edgeName.show="0" streetName.show="0" 
            edgeDataMode="0" laneWidthExaggeration="1.0"/>
        <vehicles vehicleQuality="3" vehicleSize="3.0" vehicleShape="3"
            showBlinker="1" drawMinGap="0" drawBrakeGap="0"
            vehicleName.show="0" vehicleColorMode="0"/>
        <junctions junctionMode="0" drawLinkTLIndex="0" drawLinkJunctionIndex="0"
            drawCrossingsAndWalkingareas="0" showLane2Lane="0"
            tlsPhaseIndex.show="0" junctionName.show="0"/>
        <additionals addSize="1.5" addFullName="0"/>
        <pois poiSize="3.0" poiDetail="4" poiName.show="0"/>
    </scheme>
</viewsettings>"""
        Path('view.xml').write_text(view)
    
    def _build_network(self):
        result = subprocess.run([
            'netconvert',
            '--node-files=simulation.nod.xml',
            '--edge-files=simulation.edg.xml',
            '--output-file=simulation.net.xml',
            '--no-turnarounds'
        ], capture_output=True, text=True)
        
        return result.returncode == 0


if __name__ == '__main__':
    generator = NetworkGenerator()
    generator.generate()