#ifndef CONFIG_H
#define CONFIG_H

#include "thresholds.h"

inline float getGateCloseThreshold() {
    return GATE_CLOSE_THRESHOLD;
}

inline float getNotificationThreshold() {
    return NOTIFICATION_THRESHOLD;
}

inline float getGateOpenDelay() {
    return GATE_OPEN_DELAY;
}

inline float getSensor0Position() {
    return SENSOR_0_POS;
}

inline float getSensor1Position() {
    return SENSOR_1_POS;
}

inline float getSensor2Position() {
    return SENSOR_2_POS;
}

inline unsigned long getBuzzerInterval() {
    return 500;
}

inline unsigned long getDisplayUpdateInterval() {
    return 100;
}

inline float getDefaultTrainLength() {
    return 0.15f;
}

#define GATE_OPEN_ANGLE 90
#define GATE_CLOSED_ANGLE 0
#define DISPLAY_BRIGHTNESS 0x0f

#endif
