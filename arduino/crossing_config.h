#ifndef CROSSING_CONFIG_H
#define CROSSING_CONFIG_H

struct CrossingConfig {
    float gate_close_threshold;
    float notification_threshold;
    float safety_buffer;
    unsigned long buzzer_interval;
    unsigned long train_clear_delay;
};

CrossingConfig config = {
    10.0,    // gate_close_threshold: Close gate when ETA <= 10.0s
    189.1,    // notification_threshold: Notify intersections when ETA <= 189.1s
    2.0,     // safety_buffer: Extra safety time (seconds)
    500,     // buzzer_interval: Buzzer beep interval (ms)
    5000     // train_clear_delay: Wait time after train passes (ms)
};

void updateGateThreshold(float eta_threshold) {
    config.gate_close_threshold = eta_threshold;
}

void updateNotificationThreshold(float eta_threshold) {
    config.notification_threshold = eta_threshold;
}

void updateBuzzerInterval(unsigned long interval_ms) {
    config.buzzer_interval = interval_ms;
}

float getGateCloseThreshold() {
    return config.gate_close_threshold;
}

float getNotificationThreshold() {
    return config.notification_threshold;
}

unsigned long getBuzzerInterval() {
    return config.buzzer_interval;
}

unsigned long getTrainClearDelay() {
    return config.train_clear_delay;
}

#endif
