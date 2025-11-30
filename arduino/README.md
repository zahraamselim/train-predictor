# Arduino Hardware Implementation

Complete standalone system that runs on battery power with embedded ML model.

## Files

```
arduino/
├── sketch.ino                    # Main Arduino code
├── export_model_to_arduino.py    # Exports trained ML model
└── README.md                     # This file
```

## Quick Start

### 1. Train ML Model

```bash
make data-train    # Generate training data
make ml-train      # Train ETA predictor
```

### 2. Export Model to Arduino

```bash
make ml-export
```

This creates `arduino/eta_model.h` with the ML prediction function.

### 3. Update Arduino Sketch

Open `sketch.ino` and replace the `predictETA()` function with the contents of `eta_model.h`.

### 4. Upload to Arduino

- Open Arduino IDE
- Install library: TM1637Display
- Select Board: Arduino Uno
- Upload sketch

## Hardware Setup

### Components (from Wokwi diagram)

**Railway Detection:**

- 3× PIR Motion Sensors (or IR obstacle sensors)
- Connected to D2, D3, D4

**Crossing Control:**

- 1× Servo Motor → D5
- 1× TM1637 Display → D11 (CLK), D12 (DIO)
- 1× Red LED → D6 (via 220Ω resistor)
- 1× Green LED → D7 (via 220Ω resistor)

**Intersection Warning:**

- 1× Red LED → D8 (via 220Ω resistor)
- 1× Green LED → D9 (via 220Ω resistor)
- 1× Buzzer → D10 (via 100Ω resistor)

### Wiring Diagram

```
Arduino Uno
├── D2 ← PIR Sensor 0 (Furthest)
├── D3 ← PIR Sensor 1 (Middle)
├── D4 ← PIR Sensor 2 (Nearest)
├── D5 → Servo Signal
├── D6 → Crossing Red LED → 220Ω → GND
├── D7 → Crossing Green LED → 220Ω → GND
├── D8 → Intersection Red LED → 220Ω → GND
├── D9 → Intersection Green LED → 220Ω → GND
├── D10 → Buzzer → 100Ω → GND
├── D11 → TM1637 CLK
├── D12 → TM1637 DIO
├── 5V → All VCC pins
└── GND → All GND pins
```

## How It Works

### 1. Train Detection

```
Sensor 0 (54cm) ──→ Sensor 1 (32.4cm) ──→ Sensor 2 (16.2cm) ──→ Crossing
```

Sensors trigger sequentially as train approaches.

### 2. ETA Calculation

**Features extracted:**

- Time between sensor pairs
- Speed at each segment
- Acceleration/deceleration
- Distance remaining

**ML Model predicts:**

- Accurate ETA accounting for train dynamics
- More precise than simple physics

### 3. Gate Control

```
ETA > 15s → Notify intersections (red light, buzzer)
ETA ≤ 10s → Close gates, start countdown
ETA = 0s  → Wait 5 seconds, open gates
```

## Testing

### Wokwi Simulation

1. Go to https://wokwi.com
2. Create new Arduino Uno project
3. Add components and wire as shown
4. Upload sketch
5. Click sensors to simulate train

### Physical Hardware

1. Power Arduino via USB or battery
2. Trigger sensors manually or with object
3. Observe gate, lights, buzzer, countdown
4. System resets automatically after train passes

## Serial Monitor Output

```
=================================
Level Crossing System Ready
Standalone Mode - ML Embedded
=================================
[SENSOR 0] Train detected (furthest)
[SENSOR 1] Train detected (middle)
[SENSOR 2] Train detected (nearest)
[ML] Predicted ETA: 8.5 seconds
[INFO] Train speed: 67.3 km/h
[INFO] Acceleration: 0.152 m/s²
[NOTIFICATION] Intersections alerted
[GATE] CLOSED - Train approaching
[TRAIN] Passed crossing - waiting 5s
[GATE] OPENED - Safe to cross
[SYSTEM] Reset - Ready for next train
=================================
```

## Model Export Options

When running `make ml-export`, choose:

### Option 1: Simplified Decision Tree (Recommended)

```
Depth 3: ~50 nodes,  ~800 bytes,  fast
Depth 5: ~200 nodes, ~3KB,        balanced ✓
Depth 7: ~800 nodes, ~13KB,       best accuracy
```

**Recommended:** Depth 5 for good accuracy with reasonable memory.

### Option 2: Linear Regression

```
Memory: ~100 bytes
Speed: Very fast
Accuracy: May be lower for complex patterns
```

**Use when:** Memory is extremely limited.

## Battery Operation

### Power Requirements

- Arduino Uno: ~50mA idle, ~100mA active
- Servo: ~500-1000mA when moving
- LEDs: ~80mA total
- Display: ~80mA
- Buzzer: ~30mA
- **Total:** ~300-400mA average

### Battery Options

**Option 1: 9V Battery**

- Capacity: ~500mAh
- Runtime: ~1-2 hours
- Connect to Arduino VIN pin

**Option 2: 4× AA Batteries (6V)**

- Capacity: ~2500mAh
- Runtime: ~6-8 hours
- Use battery holder with barrel jack

**Option 3: USB Power Bank**

- Capacity: 5000-10000mAh
- Runtime: 12-25 hours
- Connect via USB cable

**Recommendation:** USB power bank for longest runtime.

## Customization

### Adjust Sensor Positions

```cpp
// Demo scale (cm)
const float SENSOR_0_POS = 54.0;
const float SENSOR_1_POS = 32.4;
const float SENSOR_2_POS = 16.2;

// Or real scale (m)
const float SENSOR_0_POS = 2700.0;
const float SENSOR_1_POS = 1620.0;
const float SENSOR_2_POS = 810.0;
```

### Adjust Timing Thresholds

```cpp
const float GATE_CLOSE_THRESHOLD = 10.0;      // Close gate at 10s
const float NOTIFICATION_THRESHOLD = 15.0;    // Notify at 15s
```

### Change Buzzer Pattern

```cpp
if (now - last_buzzer_toggle >= 300) {  // Faster beeps (300ms)
```

## Troubleshooting

### Sensors Not Triggering

- Check wiring: OUT → D2/D3/D4, VCC → 5V, GND → GND
- PIR sensors may need 30s warmup time
- Test with Serial Monitor

### Gate Not Moving

- Check servo power connection
- May need external 5V supply if high torque
- Test angles: `gateServo.write(0);` then `gateServo.write(90);`

### Display Blank

- Verify CLK → D11, DIO → D12
- Check brightness: `display.setBrightness(0x0f);`
- Install TM1637Display library

### Wrong ETA Predictions

- Retrain model: `make ml-train`
- Check sensor positions match training data scale
- Verify sensors trigger in correct order

### System Doesn't Reset

- Check for infinite loops in code
- Ensure countdown reaches 0
- Power cycle Arduino

## Advanced Features

### Multi-Train Support

Currently resets after each train. To support multiple trains:

1. Track multiple train states
2. Store sensor readings in arrays
3. Process each train independently

### Remote Monitoring

Add ESP8266/ESP32 for WiFi:

1. Send notifications to mobile app
2. Log all train passages
3. Remote system status

### Solar Power

For permanent outdoor installation:

1. Solar panel (5-10W)
2. Battery (12V, 7Ah)
3. Charge controller
4. Run continuously

## Safety Notes

- This is a demonstration system
- Not certified for actual railway use
- Always have manual override
- Test thoroughly before deployment
- Never rely solely on automated systems

## Files Summary

| File                         | Purpose                            |
| ---------------------------- | ---------------------------------- |
| `sketch.ino`                 | Main Arduino code (upload this)    |
| `export_model_to_arduino.py` | Converts ML model to C++           |
| `eta_model.h`                | Generated ML code (copy to sketch) |
| `README.md`                  | This documentation                 |

## Next Steps

1. ✅ Train ML model: `make ml-train`
2. ✅ Export to Arduino: `make ml-export`
3. ✅ Copy `eta_model.h` code to `sketch.ino`
4. ✅ Upload to Arduino
5. ✅ Test with sensors
6. ✅ Deploy on battery power
