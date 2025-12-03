# Arduino Demonstration System

## Overview

This is a small-scale demonstration of the level crossing control system designed for manual train movement. The scale is set to centimeters (5cm between sensors) to make it practical for tabletop demonstration.

## Scale Configuration

**Physical Layout:**

- Sensor 0: 20cm before crossing
- Sensor 1: 15cm before crossing
- Sensor 2: 10cm before crossing
- Crossing: 0cm (reference point)
- Intersection: 20cm before crossing (west side)

**Spacing:**

- 5cm between sensors
- Total detection distance: 20cm

**Train Parameters:**

- Length: 10cm
- Typical speed: 5 cm/s (for demonstration)

## System Operation Flow

The system follows this sequence when a train is detected:

### 1. Train Detection (Sensors 0, 1, 2 triggered)

When all three sensors detect the train:

- ML model calculates ETA and ETD
- System transitions to prediction mode
- Countdown timer shows time until gate closure: `ETA - CLOSURE_THRESHOLD`

Console output:

```
[00:15] Sensor 0 triggered (20cm from crossing)
[00:16] Sensor 1 triggered (15cm from crossing)
[00:17] Sensor 2 triggered (10cm from crossing)
[00:17] Train parameters calculated:
[00:17]   Speed: 5.23 cm/s
[00:17]   Acceleration: 0.15 cm/s²
[00:17]   ETA: 3.5s
[00:17]   ETD: 5.8s
```

### 2. Intersection Notification (ETA - 3s)

When remaining ETA reaches notification threshold:

- Intersection red LED turns ON
- Intersection green LED turns OFF
- Buzzer starts beeping (500ms interval)
- Timer continues countdown to gate closure

Console output:

```
[00:18] INTERSECTION NOTIFIED - Buzzer activated
[00:18]   Time to gate closure: 1.5s
```

### 3. Gate Closure (ETA - 2s)

When remaining ETA reaches closure threshold:

- Servo closes gate (moves to 0 degrees)
- Crossing red LED turns ON
- Crossing green LED turns OFF
- Buzzer continues beeping
- Timer switches to show time until gate reopens: `ETD + OPENING_THRESHOLD`

Console output:

```
[00:20] GATES CLOSED
[00:20]   Wait time: 6.8s
```

### 4. Gate Opening (ETD + 1s)

After train completely clears and opening threshold passes:

- Servo opens gate (moves to 90 degrees)
- All red LEDs turn OFF
- All green LEDs turn ON
- Buzzer stops
- Timer clears
- System resets and ready for next train

Console output:

```
[00:26] GATES OPEN - System ready
[00:26] System reset - Ready for next train
```

## Hardware Connections

### Components:

- Arduino Uno
- 3x PIR Motion Sensors (simulating train detection)
- 1x Servo motor (gate mechanism)
- 4x LEDs (2 red, 2 green)
- 1x Buzzer
- 1x TM1637 4-digit 7-segment display
- 5x 220Ω resistors (for LEDs)
- 1x 100Ω resistor (for buzzer)
- Breadboard and jumper wires

### Pin Configuration:

```
Digital Pins:
  2  - Sensor 0 (PIR 1)
  3  - Sensor 1 (PIR 2)
  4  - Sensor 2 (PIR 3)
  5  - Servo PWM
  6  - Crossing Green LED
  7  - Crossing Red LED
  8  - Intersection Green LED
  9  - Intersection Red LED
  10 - Buzzer
  11 - TM1637 CLK
  12 - TM1637 DIO

Power:
  5V  - Servo, sensors, display
  GND - Common ground
```

## Demonstration Procedure

### Setup:

1. Upload sketch to Arduino
2. Power on system
3. Verify all green LEDs are ON
4. Verify display is clear

### Train Detection Test:

1. Move train model past Sensor 0 (trigger detection)
2. Continue moving past Sensor 1
3. Continue moving past Sensor 2
4. Observe ETA/ETD calculation on serial monitor
5. Watch countdown timer on display

### Full Cycle Test:

1. Detect train at all three sensors
2. Wait for intersection notification (buzzer + red LED at 3s before ETA)
3. Watch countdown timer showing time to closure
4. Observe gate closure at 2s before ETA
5. Watch timer switch to showing time to reopening
6. Continue moving train across crossing
7. Wait for gate to reopen after ETD + 1s
8. Verify system resets to green lights

## Thresholds (Demonstration Scale)

These thresholds are set for quick demonstration cycles:

```yaml
closure_before_eta: 2.0s # Close gates 2 seconds before train arrives
opening_after_etd: 1.0s # Open gates 1 second after train clears
notification_time: 3.0s # Notify intersection 3 seconds before
```

For a typical manual push at 5 cm/s:

- Detection to crossing: ~4 seconds
- Notification occurs: 1 second after detection
- Gate closes: 2 seconds after detection
- Gate reopens: ~6-7 seconds after detection

## Display Format

The TM1637 display shows countdown time in MM:SS format:

```
Waiting for detection: ----
Countdown to closure:  00:02
Countdown to opening:  00:06
System ready:          ----
```

## Serial Monitor Output

Example complete cycle:

```
[00:00] Demonstration Level Crossing System
[00:00] Scale: 5cm between sensors, 20cm to crossing
[00:00] Ready - waiting for train detection

[00:15] Sensor 0 triggered (20cm from crossing)
[00:16] Sensor 1 triggered (15cm from crossing)
[00:17] Sensor 2 triggered (10cm from crossing)
[00:17] Train parameters calculated:
[00:17]   Speed: 5.23 cm/s
[00:17]   Acceleration: 0.15 cm/s²
[00:17]   ETA: 3.5s
[00:17]   ETD: 5.8s

[00:18] INTERSECTION NOTIFIED - Buzzer activated
[00:18]   Time to gate closure: 1.5s

[00:20] GATES CLOSED
[00:20]   Wait time: 6.8s

[00:26] GATES OPEN - System ready
[00:26] System reset - Ready for next train
```

## Customization

Edit `config/arduino_scale.yaml` to adjust parameters:

```yaml
sensors:
  s0: 20.0 # Distance from crossing (cm)
  s1: 15.0
  s2: 10.0

train:
  length: 10.0 # Train model length (cm)
  typical_speed: 5.0 # Expected speed (cm/s)

thresholds:
  closure_before_eta: 2.0 # Gate closure timing
  opening_after_etd: 1.0 # Gate opening timing
  notification_time: 3.0 # Intersection warning time
```

Then run:

```bash
python -m hardware.scale_config_generator
```

## Troubleshooting

**Gates don't close:**

- Check sensor connections and triggering
- Verify servo connection to pin 5
- Check serial monitor for ETA calculation

**Timer doesn't count down:**

- Verify TM1637 connections (CLK=11, DIO=12)
- Check display brightness in code
- Ensure proper power supply

**Buzzer doesn't beep:**

- Check resistor value (100Ω)
- Verify pin 10 connection
- Reduce volume in code if too loud

**LEDs don't change:**

- Check LED polarity (long leg = anode)
- Verify resistor connections (220Ω)
- Test individual LEDs with multimeter

**System doesn't reset:**

- Manually move train past all sensors
- Wait for full cycle to complete
- Press Arduino reset button if needed

## Notes

- This is a demonstration system, not production hardware
- ML models are trained on full-scale data but work with small-scale inputs
- Timing accuracy depends on consistent manual train movement
- System demonstrates the control logic, not real-world timing precision
- Buzzer volume can be adjusted in `diagram.json` (currently 0.1)
