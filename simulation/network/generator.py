import os
from pathlib import Path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class NetworkGenerator:
    """Generate SUMO networks for simulation or training"""
    
    def __init__(self, mode="complete", output_dir=None):
        self.mode = mode
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path("sumo") / mode
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, sensor_positions=None):
        if self.mode == "training":
            return self._generate_training(sensor_positions or [1130.0, 645.7, 322.9])
        return self._generate_complete()
    
    def _generate_training(self, sensors):
        self.sensor_positions = sensors
        self._write_training_nodes()
        self._write_training_edges()
        self._write_training_routes()  # NEW: Add routes file for training
        self._write_training_config()
        return self._build_network()
    
    def _generate_complete(self):
        self._write_complete_nodes()
        self._write_complete_edges()
        self._write_complete_routes()
        self._write_complete_config()
        self._write_viewsettings()
        return self._build_network()
    
    def _write_training_nodes(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="track_start" x="-2000" y="0" type="priority"/>
    <node id="crossing" x="0" y="0" type="rail_crossing"/>
    <node id="track_end" x="1000" y="0" type="priority"/>
</nodes>
"""
        self._write_file("network.nod.xml", content)
    
    def _write_training_edges(self):
        content = """<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <edge id="track_to_crossing" from="track_start" to="crossing" numLanes="1" speed="50.0" allow="rail"/>
    <edge id="crossing_to_end" from="crossing" to="track_end" numLanes="1" speed="50.0" allow="rail"/>
</edges>
"""
        self._write_file("network.edg.xml", content)
    
    def _write_training_routes(self):
        """NEW: Write routes file for training mode with vehicle type definitions"""
        content = """<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="train_type" vClass="rail" length="150" maxSpeed="45.0" accel="2.0" decel="2.0" color="150,30,30"/>
    <route id="train_route" edges="track_to_crossing crossing_to_end"/>
</routes>
"""
        self._write_file("routes.rou.xml", content)
    
    def _write_training_config(self):
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
        <time-to-teleport value="-1"/>
        <collision.check-junctions value="false"/>
    </processing>
</configuration>
"""
        self._write_file("training.sumocfg", content)
    
    def _write_complete_nodes(self):
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
        self._write_file("network.nod.xml", content)
    
    def _write_complete_edges(self):
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
        self._write_file("network.edg.xml", content)
    
    def _write_complete_routes(self):
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
        self._write_file("routes.rou.xml", content)
    
    def _write_complete_config(self):
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
        self._write_file("simulation.sumocfg", content)
    
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
        self._write_file("viewsettings.xml", content)
    
    def _write_file(self, filename, content):
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
    
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
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    from simulation.utils.logger import Logger
    
    Logger.section("Generating complete network")
    generator = NetworkGenerator(mode="complete")
    if generator.generate():
        Logger.log("Network generated successfully")
        sys.exit(0)
    else:
        Logger.log("Network generation failed")
        sys.exit(1)