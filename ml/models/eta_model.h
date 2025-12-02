#ifndef ETA_MODEL_H
#define ETA_MODEL_H

/*
 * Train ETA Prediction Model
 * Auto-generated from decision tree
 * 
 * Feature indices:
 * [0] distance_remaining\n * [1] last_speed\n * [2] last_accel\n * [3] speed_trend\n * [4] speed_variance\n * [5] time_variance\n * [6] avg_speed_overall\n * [7] dt_interval_0\n * [8] dt_interval_1\n * [9] avg_speed_0\n * [10] avg_speed_1
 */

float predictETA(float features[11]) {
    if (features[1] <= 47.0100f) {
        if (features[6] <= 41.8438f) {
            return 7.5500f;
        } else {
            if (features[1] <= 46.2100f) {
                if (features[6] <= 45.7863f) {
                    return 7.0667f;
                } else {
                    return 7.0000f;
                }
            } else {
                if (features[5] <= 4.0400f) {
                    return 6.9250f;
                } else {
                    return 6.8000f;
                }
            }
        }
    } else {
        if (features[8] <= 6.5500f) {
            if (features[6] <= 50.0403f) {
                if (features[1] <= 49.6650f) {
                    return 6.5000f;
                } else {
                    return 6.4000f;
                }
            } else {
                return 6.5000f;
            }
        } else {
            if (features[3] <= 0.0961f) {
                return 6.7000f;
            } else {
                return 6.6000f;
            }
        }
    }
}

#endif
