// Example Arduino usage
#include "eta_model.h"
#include "etd_model.h"

void setup() {
    Serial.begin(9600);
}

void loop() {
    // Calculate features from your sensors
    float eta_features[ETA_N_FEATURES] = {
        distance_remaining,
        train_length,
        last_speed,
        speed_change,
        time_01,
        time_12,
        avg_speed_01,
        avg_speed_12
    };
    
    float etd_features[ETD_N_FEATURES] = {
        distance_remaining,
        train_length,
        last_speed,
        speed_change,
        time_01,
        time_12,
        avg_speed_01,
        avg_speed_12,
        accel_trend,
        predicted_speed_at_crossing
    };
    
    float eta_seconds = predict_eta(eta_features);
    float etd_seconds = predict_etd(etd_features);
    
    Serial.print("Train arrives in: ");
    Serial.print(eta_seconds);
    Serial.println(" seconds");
    
    Serial.print("Crossing clears in: ");
    Serial.print(etd_seconds);
    Serial.println(" seconds");
    
    delay(1000);
}
