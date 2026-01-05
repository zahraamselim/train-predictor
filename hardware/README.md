# Hardware Module

Exports trained ML models and thresholds to Arduino C code for physical deployment.

## What It Does

Converts Python-trained models to C headers that Arduino can use to run the railway crossing system on physical hardware.

## Physical Setup

### Layout

```
[S0] --10cm-- [S1] --10cm-- [S2] --20cm-- [Crossing] --20cm-- [Intersection]
                                              ⊥
                                        (perpendicular)
```

**Total**: ~60cm tabletop model

### Components

**Sensors**: 3x PIR Motion Sensors

- S0: 40cm from crossing (furthest)
- S1: 30cm from crossing (middle)
- S2: 20cm from crossing (nearest)

**Outputs**:

- 1x Servo motor (gate control)
- 1x TM1637 7-segment display (countdown)
- 2x Red LEDs (crossing signals)
- 2x Green LEDs (intersection signals)
- 1x Buzzer (warning sound)

**Controller**: Arduino Uno

**Movement**: Hand-moved toy train/cars

## How It Works

### Detection & Prediction

1. Train triggers S0, S1, S2 sequentially
2. Arduino calculates speed and acceleration from timing
3. Predicts ETA (time until arrival) and ETD (time until cleared)
4. **Display shows ETA countdown** (time until gate closes)

### Gate Closing

5. When ETA reaches close threshold:
   - Gate servo closes
   - Crossing green LED → OFF
   - Crossing red LED → ON
   - **Display switches to ETD countdown** (time until gate opens)

### Intersection Warning

6. When notification threshold reached:
   - Intersection green LED → OFF
   - Intersection red LED → ON
   - Buzzer starts beeping

### Gate Opening

7. When ETD countdown reaches 0:
   - Gate servo opens
   - Crossing red LED → OFF, green LED → ON
   - Intersection red LED → OFF, green LED → ON
   - Buzzer stops
   - System resets for next train

## System Behavior

```
Train at S0 → Calculate ETA/ETD
  ↓
Display shows: "00:03" (ETA countdown - time until gate closes)
  ↓
Notification time → Intersection red + buzzer starts
  ↓
Gate close time → Servo closes, crossing turns red
  ↓
Display switches to: "00:05" (ETD countdown - time until gate opens)
  ↓
ETD reaches 0 → Gate opens, all green, buzzer stops, reset
```

## Usage

### 1. Export to Arduino

```bash
make hw-export
```

Generates:

- `hardware/thresholds.h` - Sensor positions and timing
- `hardware/eta_model.h` - ETA/ETD prediction functions
- `hardware/crossing_config.h` - Helper functions

### 2. Upload to Arduino

**Using Arduino IDE**:

1. Open `hardware/sketch.ino`
2. Verify compilation
3. Upload to Arduino Uno

**Using CLI**:

```bash
arduino-cli compile --fqbn arduino:avr:uno hardware/
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno hardware/
```

### 3. Test with Serial Monitor

Open Serial Monitor at 9600 baud:

```
[00:00] Level Crossing System Ready
[00:00] Sensors at: S0=0.40m, S1=0.30m, S2=0.20m
[00:00] Gate close: 6.8s, Notify: 27.5s
```

Move toy train across sensors and observe the sequence.

## Files

### Generated Headers

- `thresholds.h` - Physical scale sensor positions and timing
- `eta_model.h` - ETA/ETD prediction functions (physics-based)
- `crossing_config.h` - Helper functions and constants

### Arduino Code

- `sketch.ino` - Main program (uses generated headers)
- `diagram.json` - Wokwi circuit layout
- `libraries.txt` - Dependencies (Servo, TM1637)

### Exporters (Python)

- `exporters/threshold.py` - Generates thresholds.h
- `exporters/model.py` - Generates eta_model.h
- `exporters/config.py` - Generates crossing_config.h

## Outputs

After `make hw-export`:

```
hardware/
├── thresholds.h           ← Sensor positions (0.4m, 0.3m, 0.2m)
├── eta_model.h            ← ETA/ETD prediction functions
├── crossing_config.h      ← Helper functions
├── sketch.ino             ← Main Arduino program
└── exporters/
    ├── threshold.py
    ├── model.py
    └── config.py
```

## Example Serial Output

```
[00:05] [SENSOR 0] Train detected (furthest)
[00:06] [SENSOR 1] Train detected (middle)
[00:06] [TIMING] S0->S1: 0.850s
[00:07] [SENSOR 2] Train detected (nearest)
[00:07] [TIMING] S1->S2: 0.920s
[00:07] [CALCULATING] Computing ETA and ETD...
[00:07] [PREDICTION] ETA: 3.2s, ETD: 5.1s
[00:07] [INFO] Train speed: 23.5 km/h, Accel: -0.023 m/s^2
[00:10] [NOTIFICATION] Intersection alerted - Red light + Buzzer
[00:11] [GATE] CLOSED - Crossing red, now showing ETD countdown
[00:17] [GATE] OPENED - All clear, buzzer stopped
[00:17] [SYSTEM] Reset - Ready for next train
```

## Physical Constraints

### Arduino Uno Limits

- **Flash**: 32KB program storage
- **RAM**: 2KB runtime memory
- **Full ML model**: ~120KB (won't fit!)

### Solution: Physics Fallback

Uses simplified physics calculations:

```cpp
ETA = distance / speed
ETD = (distance + train_length) / speed
```

**Accuracy**: ~0.5s (vs ~0.35s for full ML)

**For full ML**: Use Arduino Mega (256KB) or ESP32 (4MB)

## Configuration

### Timing Adjustments

Edit `hardware/thresholds.h` (or regenerate):

```cpp
#define GATE_CLOSE_THRESHOLD 6.80f    // Seconds before train
#define NOTIFICATION_THRESHOLD 27.50f  // Seconds warning
#define GATE_OPEN_DELAY 3.00f          // Seconds after train
```

### Display/Buzzer

Edit `hardware/crossing_config.h`:

```cpp
#define BUZZER_INTERVAL 500            // Beep interval (ms)
#define DISPLAY_BRIGHTNESS 0x0f        // 0-15
```

## Troubleshooting

### Headers Not Found

**Problem**: "thresholds.h: No such file"

**Fix**:

```bash
make hw-export  # Generate all headers
```

### Wrong Sensor Positions

**Problem**: Sensors don't match physical layout

**Fix**: Run thresholds pipeline first:

```bash
make th-pipeline  # Generate correct thresholds
make hw-export    # Export to Arduino
```

Or manually edit `hardware/thresholds.h`

### Servo Not Moving

**Causes**:

- Insufficient power (servos need ≥500mA)
- Wrong pin (should be pin 5)
- No Servo library

**Fix**: Use external 5V power supply for servo

### Very Fast Timing

With 10cm spacing at 0.5 m/s hand speed:

- Time between sensors: ~0.2s
- ETA: ~0.5-1.0s
- ETD: ~1.0-2.0s

**Solutions**:

1. Move hand slower (~0.2 m/s)
2. Use motor for consistent speed
3. Increase sensor spacing

## Demo Tips

### Hand Movement

- Speed: Slow walk pace (~0.5 m/s)
- Smooth: Maintain steady speed
- Visible: Don't block sensors with hand

### For Better Visibility

- Move slower for longer countdowns
- Announce stages: "Train detected", "Gate closing", etc.
- Point to LEDs as they change

## Scale Comparison

| Aspect         | Physical Demo | SUMO Simulation |
| -------------- | ------------- | --------------- |
| Distance       | 60cm          | 4000m           |
| Sensor spacing | 10cm          | 500m            |
| Speed          | 0.5 m/s       | 30 m/s          |
| Timing         | ~1-2s         | ~10-30s         |
| Purpose        | Show logic    | Test accuracy   |

## Summary

**Purpose**: Physical demonstration of railway crossing control

**Method**: Export Python models → Arduino C code

**Features**:

- Real ETA/ETD calculation from sensors
- Two countdowns (before/after gate close)
- Proper LED control (green ↔ red)
- Buzzer warning (notification → clear)

**Result**: Working tabletop demonstration system

Perfect for science fairs, school projects, or embedded systems education!
