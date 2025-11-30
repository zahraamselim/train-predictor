"""Update Arduino crossing configuration from simulation results."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.utils import load_config


def generate_crossing_config_header(output_path=None):
    """Generate crossing_config.h from system configuration."""
    
    if output_path is None:
        output_path = os.path.join('arduino', 'crossing_config.h')
    
    config = load_config()
    
    gate_close_threshold = config['gates']['closure_before_eta']
    
    vehicle_clearance = config['vehicle_clearance']
    max_clearance = max(
        vehicle_clearance['light']['max_time'],
        vehicle_clearance['medium']['max_time'],
        vehicle_clearance['heavy']['max_time']
    )
    
    scale_mode = config['system']['scale_mode']
    safety_buffer = config['traffic'][f'{scale_mode}_scale']['safety_buffer']
    
    notification_threshold = max_clearance + safety_buffer + gate_close_threshold
    
    code = "#ifndef CROSSING_CONFIG_H\n"
    code += "#define CROSSING_CONFIG_H\n\n"
    
    code += "struct CrossingConfig {\n"
    code += "    float gate_close_threshold;\n"
    code += "    float notification_threshold;\n"
    code += "    float safety_buffer;\n"
    code += "    unsigned long buzzer_interval;\n"
    code += "    unsigned long train_clear_delay;\n"
    code += "};\n\n"
    
    code += "CrossingConfig config = {\n"
    code += f"    {gate_close_threshold:.1f},    // gate_close_threshold: Close gate when ETA <= {gate_close_threshold:.1f}s\n"
    code += f"    {notification_threshold:.1f},    // notification_threshold: Notify intersections when ETA <= {notification_threshold:.1f}s\n"
    code += f"    {safety_buffer:.1f},     // safety_buffer: Extra safety time (seconds)\n"
    code += "    500,     // buzzer_interval: Buzzer beep interval (ms)\n"
    code += "    5000     // train_clear_delay: Wait time after train passes (ms)\n"
    code += "};\n\n"
    
    code += "void updateGateThreshold(float eta_threshold) {\n"
    code += "    config.gate_close_threshold = eta_threshold;\n"
    code += "}\n\n"
    
    code += "void updateNotificationThreshold(float eta_threshold) {\n"
    code += "    config.notification_threshold = eta_threshold;\n"
    code += "}\n\n"
    
    code += "void updateBuzzerInterval(unsigned long interval_ms) {\n"
    code += "    config.buzzer_interval = interval_ms;\n"
    code += "}\n\n"
    
    code += "float getGateCloseThreshold() {\n"
    code += "    return config.gate_close_threshold;\n"
    code += "}\n\n"
    
    code += "float getNotificationThreshold() {\n"
    code += "    return config.notification_threshold;\n"
    code += "}\n\n"
    
    code += "unsigned long getBuzzerInterval() {\n"
    code += "    return config.buzzer_interval;\n"
    code += "}\n\n"
    
    code += "unsigned long getTrainClearDelay() {\n"
    code += "    return config.train_clear_delay;\n"
    code += "}\n\n"
    
    code += "#endif\n"
    
    with open(output_path, 'w') as f:
        f.write(code)
    
    print(f"\nCrossing configuration exported to: {output_path}")
    print(f"\nConfiguration values:")
    print(f"  Gate close threshold: {gate_close_threshold:.1f}s")
    print(f"  Notification threshold: {notification_threshold:.1f}s")
    print(f"  Safety buffer: {safety_buffer:.1f}s")
    print(f"  Max vehicle clearance time: {max_clearance:.1f}s")
    
    return code


def main():
    """Generate crossing configuration header."""
    
    print("Crossing Configuration Exporter")
    generate_crossing_config_header()
    print("\nSUCCESS")
    print("Header file created and ready for Arduino")


if __name__ == "__main__":
    main()