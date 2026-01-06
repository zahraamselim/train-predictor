#ifndef MODEL_H
#define MODEL_H

#define FEAT_TIME_01 0
#define FEAT_TIME_12 1
#define FEAT_SPEED_01 2
#define FEAT_SPEED_12 3
#define FEAT_ACCEL 4
#define FEAT_DISTANCE 5

#define FEAT_ETD_TIME_01 0
#define FEAT_ETD_TIME_12 1
#define FEAT_ETD_SPEED_01 2
#define FEAT_ETD_SPEED_12 3
#define FEAT_ETD_ACCEL 4
#define FEAT_ETD_DISTANCE 5
#define FEAT_ETD_TRAIN_LENGTH 6

float predictETA(float features[6]) {
    float speed = features[FEAT_SPEED_12];
    float accel = features[FEAT_ACCEL];
    float distance = features[FEAT_DISTANCE];
    
    if (speed <= 0 || distance <= 0) return -1;
    
    if (accel > -0.1 && accel < 0.1) {
        return distance / speed;
    }
    
    float discriminant = speed * speed + 2.0 * accel * distance;
    
    if (discriminant < 0) {
        return distance / speed;
    }
    
    float t = (-speed + sqrt(discriminant)) / accel;
    
    if (t > 0 && t < 1000) {
        return t;
    }
    
    return distance / speed;
}

float predictETD(float features[7]) {
    float speed = features[FEAT_ETD_SPEED_12];
    float accel = features[FEAT_ETD_ACCEL];
    float distance = features[FEAT_ETD_DISTANCE];
    float train_length = features[FEAT_ETD_TRAIN_LENGTH];
    
    if (speed <= 0 || distance <= 0 || train_length <= 0) return -1;
    
    float total_distance = distance + train_length;
    
    if (accel > -0.1 && accel < 0.1) {
        return total_distance / speed;
    }
    
    float discriminant = speed * speed + 2.0 * accel * total_distance;
    
    if (discriminant < 0) {
        return total_distance / speed;
    }
    
    float t = (-speed + sqrt(discriminant)) / accel;
    
    if (t > 0 && t < 1000) {
        return t;
    }
    
    return total_distance / speed;
}

float estimateETD(float eta, float last_speed) {
    const float AVG_TRAIN_LENGTH = 0.15f;
    
    if (eta <= 0 || last_speed <= 0) return -1;
    
    float crossing_time = AVG_TRAIN_LENGTH / last_speed;
    return eta + crossing_time;
}

#endif
