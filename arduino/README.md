# Arduino Hardware Implementation

Hardware deployment for level crossing notification system.

## Components

### Railway Sensors (3x)

- IR Obstacle Avoidance Sensors
- Purpose: Detect train at multiple points before crossing
- Positions: Furthest (2700m), Middle (1620m), Nearest (810m)
- Pins: D2, D3, D4

### Crossing Equipment

- Servo Motor: Gate control (0° closed, 90° open)
- TM1637 Display: Countdown timer (MM:SS format)
- Red LED: Warning light when gates closed
- Green LED: Safe to cross indicator
- Pins: D5 (servo), D11/D12 (display), D6 (red), D7 (green)

### Intersection Equipment

- Red LED: Stop signal for vehicles
- Green LED: Go signal for vehicles
- Buzzer: Warning sound
- Pins: D8 (red), D9 (green), D10 (buzzer)

## Wiring Diagram

```
Arduino Uno:

Railway Sensors:
  Sensor 0 (Furthest) → D2
  Sensor 1 (Middle)   → D3
  Sensor 2 (Nearest)  → D4
  All VCC → 5V
  All GND → GND

Crossing:
  Servo Signal → D5
  Servo VCC → 5V (or external if high torque)
  Servo GND → GND

  TM1637 CLK → D11
  TM1637 DIO → D12
  TM1637 VCC → 5V
  TM1637 GND → GND

  Red LED Anode → D6 (with 220Ω resistor)
  Red LED Cathode → GND

  Green LED Anode → D7 (with 220Ω resistor)
  Green LED Cathode → GND

Intersection:
  Red LED Anode → D8 (with 220Ω resistor)
  Red LED Cathode → GND

  Green LED Anode → D9 (with 220Ω resistor)
  Green LED Cathode → GND

  Buzzer Positive → D10 (with 100Ω resistor)
  Buzzer Negative → GND
```

## Libraries Required

Install via Arduino IDE Library Manager:

- Servo (built-in)
- TM1637Display by Avishay Orpaz

## Upload Instructions

1. Install Arduino IDE
2. Install required libraries
3. Connect Arduino via USB
4. Select Board: Arduino Uno
5. Select correct COM port
6. Open `sketch.ino`
7. Click Upload

## System Operation

### Initial State

- Gates: Open (90°)
- Crossing lights: Green
- Intersection lights: Green
- Buzzer: Off
- Display: Blank

### Train Detected

1. Sensors trigger sequentially (0 → 1 → 2)
2. System calculates train speed
3. System predicts ETA

### Gates Close (ETA < 15s)

1. Gates lower to 0°
2. All lights turn red
3. Buzzer activates (0.5s intervals)
4. Display shows countdown

### Train Passes

1. Countdown reaches 0
2. System waits 5 seconds
3. Gates open to 90°
4. All lights turn green
5. Buzzer deactivates
6. Display clears
7. System resets for next train

## ETA Calculation

Simple constant speed formula (implemented on Arduino):

```cpp
speed = distance_1_to_2 / time_1_to_2  // m/s
ETA = remaining_distance / speed       // seconds
```

Where:

- distance_1_to_2 = 810m (sensor 1 to sensor 2)
- time_1_to_2 = measured time between sensor triggers
- remaining_distance = 810m (sensor 2 to crossing)

## Testing

### Sensor Test

1. Wave hand in front of each sensor
2. Serial monitor should show: "Sensor X triggered"
3. All 3 sensors must trigger in order

### Gate Test

1. Manually trigger all 3 sensors quickly
2. If ETA < 15s, gate should close
3. After countdown, gate should reopen

### Display Test

1. Display should show MM:SS format
2. Countdown should decrement every second
3. Display should clear when gates open

## Troubleshooting

**Sensors not triggering:**

- Check wiring (VCC, GND, Signal)
- Verify sensor range (usually 2-30cm)
- Ensure sensors face correct direction

**Gate not moving:**

- Check servo power supply
- Verify servo signal wire on D5
- Test servo separately with sweep example

**Display not working:**

- Verify CLK on D11, DIO on D12
- Check library installation
- Test brightness setting

**LEDs not lighting:**

- Check resistor values (220Ω recommended)
- Verify correct polarity (long leg = anode)
- Test LEDs with simple blink sketch

## Serial Monitor Output

Enable at 9600 baud to see:

```
Level Crossing System Ready
Sensor 0 triggered
Sensor 1 triggered
Sensor 2 triggered
Speed: 120.5 km/h
ETA: 24.2 seconds
Gates closed
```

## Customization

### Adjust Gate Timing

Change `GATE_CLOSED_ANGLE` (default 0°) if servo range differs.

### Adjust ETA Threshold

Modify condition in `loop()`:

```cpp
if (calculated_eta < 15.0) {  // Change 15.0 to desired seconds
```

### Change Sensor Positions

Update constants:

```cpp
const float SENSOR_0_POS = 2700.0;  // Your distance in meters
const float SENSOR_1_POS = 1620.0;
const float SENSOR_2_POS = 810.0;
```

### Buzzer Pattern

Modify in `activateBuzzer()`:

```cpp
if (now - last_beep > 500) {  // Change 500 for different frequency
```

## Safety Notes

- Never test with real trains
- Ensure gate servo cannot trap objects
- Buzzer volume should be appropriate for environment
- LEDs should be visible in daylight
- Always have manual override for gates

## Scale Modes

### Demo Scale (1:87)

Real positions / 87 = Demo positions

- Sensor 0: 31cm
- Sensor 1: 18.6cm
- Sensor 2: 9.3cm

### Real Scale

Use actual meter values as shown in code.

## Power Requirements

- Arduino: USB (5V, ~500mA)
- Servo: May need external 5-6V supply if high torque
- LEDs: ~20mA each
- Buzzer: ~30mA
- Display: ~80mA

Total: ~200-300mA (without high-torque servo)

Recommendation: Use external 5V supply if servo draws >500mA.
