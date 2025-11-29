// Polynomial Regression Model (degree=2) for ETA Prediction

const float INTERCEPT = -182.843467;
const float COEFFICIENTS[] = {
    0.000000,
    -6.237524,
    8.575749,
    3.193779,
    -3.432302,
    0.021298,
    -0.008674,
    0.000000,
    0.078712,
    -0.020501,
    -0.030452,
    -0.000000,
    -0.021169,
    0.031446,
    -0.009700
};
const int NUM_COEFFICIENTS = 15;

float predictETA(float time_0_to_1, float time_1_to_2, float speed_0_to_1, float speed_1_to_2) {
    float features[NUM_COEFFICIENTS];
    int idx = 0;
    
    features[idx++] = 1.0;
    features[idx++] = time_0_to_1;
    features[idx++] = time_1_to_2;
    features[idx++] = speed_0_to_1;
    features[idx++] = speed_1_to_2;
    features[idx++] = time_0_to_1 * time_0_to_1;
    features[idx++] = time_0_to_1 * time_1_to_2;
    features[idx++] = time_0_to_1 * speed_0_to_1;
    features[idx++] = time_0_to_1 * speed_1_to_2;
    features[idx++] = time_1_to_2 * time_1_to_2;
    features[idx++] = time_1_to_2 * speed_0_to_1;
    features[idx++] = time_1_to_2 * speed_1_to_2;
    features[idx++] = speed_0_to_1 * speed_0_to_1;
    features[idx++] = speed_0_to_1 * speed_1_to_2;
    features[idx++] = speed_1_to_2 * speed_1_to_2;
    
    float eta = INTERCEPT;
    for (int i = 0; i < idx; i++) {
        eta += COEFFICIENTS[i] * features[i];
    }
    
    return eta;
}
