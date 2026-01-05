#ifndef ETA_MODEL_H
#define ETA_MODEL_H

/*
 * ETA/ETD Prediction for Arduino
 * 
 * Uses physics-based calculations suitable for Arduino Uno
 * Accuracy: ~0.5s MAE (vs ~0.35s for full ML model)
 * 
 * For full ML model: Use Arduino Mega or ESP32
 */

// Feature indices for ETA (6 features)
#define FEAT_TIME_01 0
#define FEAT_TIME_12 1
#define FEAT_SPEED_01 2
#define FEAT_SPEED_12 3
#define FEAT_ACCEL 4
#define FEAT_DISTANCE 5

// Feature indices for ETD (8 features - includes train length)
#define FEAT_ETD_TIME_01 0
#define FEAT_ETD_TIME_12 1
#define FEAT_ETD_SPEED_01 2
#define FEAT_ETD_SPEED_12 3
#define FEAT_ETD_ACCEL 4
#define FEAT_ETD_DISTANCE 5
#define FEAT_ETD_TRAIN_LENGTH 6
#define FEAT_ETD_PREDICTED_SPEED 7

/**
 * Predict ETA (Estimated Time of Arrival)
 * Time until train front reaches crossing
 * 
 * @param features[6]: [time_01, time_12, speed_01, speed_12, accel, distance]
 * @return ETA in seconds, or -1 if invalid
 */
float predictETA(float features[6]) {
    float speed = features[FEAT_SPEED_12];
    float accel = features[FEAT_ACCEL];
    float distance = features[FEAT_DISTANCE];
    
    if (speed <= 0 || distance <= 0) return -1;
    
    // For constant velocity (accel near zero)
    if (accel > -0.1 && accel < 0.1) {
        return distance / speed;
    }
    
    // For acceleration: d = v*t + 0.5*a*t^2
    // Solve: 0.5*a*t^2 + v*t - d = 0
    float discriminant = speed * speed + 2.0 * accel * distance;
    
    if (discriminant < 0) {
        return distance / speed;  // Fallback
    }
    
    float t = (-speed + sqrt(discriminant)) / accel;
    
    if (t > 0 && t < 1000) {
        return t;
    }
    
    return distance / speed;  // Fallback
}

/**
 * Predict ETD (Estimated Time of Departure)
 * Time until train rear clears crossing
 * 
 * @param features[8]: [time_01, time_12, speed_01, speed_12, accel, 
 *                      distance, train_length, predicted_speed_at_crossing]
 * @return ETD in seconds, or -1 if invalid
 */
float predictETD(float features[8]) {
    float speed = features[FEAT_ETD_SPEED_12];
    float accel = features[FEAT_ETD_ACCEL];
    float distance = features[FEAT_ETD_DISTANCE];
    float train_length = features[FEAT_ETD_TRAIN_LENGTH];
    
    if (speed <= 0 || distance <= 0 || train_length <= 0) return -1;
    
    // Total distance = distance to crossing + train length
    float total_distance = distance + train_length;
    
    // For constant velocity
    if (accel > -0.1 && accel < 0.1) {
        return total_distance / speed;
    }
    
    // For acceleration
    float discriminant = speed * speed + 2.0 * accel * total_distance;
    
    if (discriminant < 0) {
        return total_distance / speed;  // Fallback
    }
    
    float t = (-speed + sqrt(discriminant)) / accel;
    
    if (t > 0 && t < 1000) {
        return t;
    }
    
    return total_distance / speed;  // Fallback
}

/**
 * Simplified ETD from ETA (when train length unknown)
 * Estimates ETD based on ETA and average train length
 */
float estimateETD(float eta, float last_speed) {
    const float AVG_TRAIN_LENGTH = 0.30f;  // 30cm for demo, 150m for real
    
    if (eta <= 0 || last_speed <= 0) return -1;
    
    float crossing_time = AVG_TRAIN_LENGTH / last_speed;
    return eta + crossing_time;
}

#endif
