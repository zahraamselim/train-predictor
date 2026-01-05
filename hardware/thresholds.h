#ifndef THRESHOLDS_H
#define THRESHOLDS_H

/*
 * SUMO Simulation Configuration
 * Scale: Full-scale network (1000+ meter distances)
 * Movement: Simulated trains with realistic physics
 */

// Simulation mode flag
#define DEMO_MODE false

// Sensor positions (meters from crossing) - Full scale
#define SENSOR_0_POS 1500.00f
#define SENSOR_1_POS 1000.00f
#define SENSOR_2_POS 800.00f

// Calculated thresholds (seconds)
#define GATE_CLOSE_THRESHOLD 16.00f
#define NOTIFICATION_THRESHOLD 40.55f
#define GATE_OPEN_DELAY 3.00f

// Train parameters
#define MAX_TRAIN_SPEED 39.00f

// Statistics
// Clearance 95th: 14.00s
// Travel 95th: 22.05s
// Data: 400 clearances, 400 travels

#endif
