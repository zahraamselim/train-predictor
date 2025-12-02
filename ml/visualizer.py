"""
SUMO GUI visualization with sensor detection
"""
import subprocess
import pickle
from pathlib import Path
import xml.etree.ElementTree as ET
from utils import get_logger

def create_gui_config(config, model_path):
    """Create SUMO GUI configuration with visualization"""
    
    sensors = config['sensors']
    vis_config = config['visualization']
    
    # Create POI file for sensor markers
    pois = """<?xml version="1.0" encoding="UTF-8"?>
<additional>
"""
    
    for sensor_id, position in sensors.items():
        color = vis_config['sensor_colors'].get(sensor_id, "#888888")
        color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        color_str = f"{color_rgb[0]/255:.2f},{color_rgb[1]/255:.2f},{color_rgb[2]/255:.2f}"
        
        pois += f"""    <poi id="sensor_{sensor_id}" x="{position}" y="0" color="{color_str}" 
          layer="100" type="Sensor {sensor_id.upper()}" imgFile=""/>
"""
    
    pois += """</additional>
"""
    
    Path('sensors.add.xml').write_text(pois)
    
    # Create GUI settings
    gui_settings = f"""<viewsettings>
    <scheme name="real world"/>
    <delay value="{1000/vis_config['fps']}"/>
    <viewport zoom="150" x="2000" y="0"/>
    <background backgroundColor="0.20,0.22,0.25"/>
</viewsettings>"""
    
    Path('gui_settings.xml').write_text(gui_settings)
    
    # Create route with single demo train
    routes = f"""<?xml version="1.0" encoding="UTF-8"?>
<routes>
    <vType id="demo_train" length="150" maxSpeed="50" accel="1.2" decel="1.2" 
           speedFactor="1.0" color="0.9,0.1,0.1"/>
    <route id="demo_route" edges="track"/>
    <vehicle id="demo_train" type="demo_train" route="demo_route" 
             depart="0" departSpeed="30"/>
</routes>"""
    
    Path('demo.rou.xml').write_text(routes)
    
    # Create SUMO configuration
    sumo_config = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="rail.net.xml"/>
        <route-files value="demo.rou.xml"/>
        <additional-files value="sensors.add.xml"/>
        <gui-settings-file value="gui_settings.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="300"/>
        <step-length value="0.1"/>
    </time>
    <processing>
        <time-to-teleport value="-1"/>
    </processing>
    <gui_only>
        <start value="true"/>
    </gui_only>
</configuration>"""
    
    Path('demo.sumocfg').write_text(sumo_config)

def run_visualization(config):
    """Launch SUMO GUI with sensor visualization"""
    logger = get_logger(__name__)
    
    logger.info("Launching SUMO GUI visualization")
    
    model_dir = Path(config['output']['model_dir'])
    model_path = model_dir / config['output']['python_model']
    
    if not model_path.exists():
        logger.error(f"Model not found at {model_path}")
        return
    
    create_gui_config(config, model_path)
    
    try:
        subprocess.run(['sumo-gui', '-c', 'demo.sumocfg'], check=True)
    except subprocess.CalledProcessError:
        logger.error("SUMO GUI visualization failed")
    except FileNotFoundError:
        logger.error("sumo-gui not found. Make sure SUMO is installed.")