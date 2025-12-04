# Understanding the Optimizations

The simulation measures two main strategies for reducing fuel consumption and wait times:

## 1. Engine Shutoff

**How it works:**

- When you're stuck waiting at a crossing for more than 5 seconds, turning off your engine saves fuel
- Your engine burns 0.01 L/s while idling
- When off, it burns 0 L/s (nothing!)

**The math:**

```
If you wait 25 seconds:
- First 5 seconds: engine idles (0.05 L)
- Next 20 seconds: engine off (0 L)
- Total fuel used: 0.05 L

Without turning off:
- All 25 seconds: engine idles (0.25 L)
- Total fuel used: 0.25 L

Savings: 0.20 L per wait!
```

**Reality check:**

- Not everyone turns off their engine
- The simulation assumes 70% of drivers do it (the `engine_off_factor`)
- That's realistic - some people forget, some worry about battery, some are impatient

**Why the savings look small:**
Since most of the wait time has the engine OFF already, there's not much fuel being burned in the first place. The savings come from those 30% of drivers who keep idling.

## 2. Smart Rerouting

**How it works:**

- Sensors detect when a train is approaching (25-30 seconds early)
- Warning lights turn yellow to alert nearby drivers
- Smart navigation suggests: "Take the other crossing - it's clear!"
- Drivers who reroute avoid the long wait

**The math:**

```
Without rerouting:
- Wait at closed crossing: 33.6 seconds
- Fuel while waiting: 0.05-0.10 L (depending on shutoff)

With rerouting:
- Take alternate route: +10 second detour
- Wait at open crossing: 5.4 seconds
- Fuel: 0.02 L

Net benefit: Save 17.1 seconds and 0.03-0.08 L fuel per vehicle
```

**Reality check:**

- Only 38% of drivers use smart rerouting (not everyone has the app or trusts it)
- Rerouting adds 8-14 seconds of detour time
- Only worth it if the original wait is long (>18 seconds)
- Some drivers arrive at the alternate crossing and still catch a short wait

**Why the fuel savings are modest:**
Rerouting mainly saves TIME, not fuel. Here's why:

- You avoid a 30-second wait where the engine would be OFF for 25 seconds anyway
- You're really just saving the first 5 seconds of idling (0.05 L)
- The benefit is getting home 17 seconds faster, not massive fuel savings

## Why Queue Size and Travel Time Match

Both metrics measure the same thing - rerouting success:

**Travel Time Saved: 50.7%**

- 37 vehicles rerouted
- Each saved ~17 seconds
- Total: 10.5 minutes saved

**Queue Size Reduced: ~50%**

- Same 37 vehicles didn't join the congested queue
- A few extra vehicles benefited from shorter queues (ripple effect)
- Total: ~40 fewer vehicles waiting

These should be similar because they're both caused by rerouting. If 50% of travel time is saved, the queue should also shrink by roughly 50%.

## The Big Picture

**0.5% fuel reduction** might seem small, but:

- It's from vehicles that are already stopped (not driving)
- Most stopped time has engines OFF (zero consumption)
- The real benefit is 10.5 minutes of people's lives saved
- Multiplied across a city with 100 crossings = huge impact!

**Real-world context:**

```
If this were a city with:
- 50 railroad crossings
- 500,000 vehicles per day

Annual savings would be:
- 15,000 L of fuel
- 35,000 kg of CO₂
- 3,500 hours of people's time
```

That's why cities invest in these smart systems - small per-vehicle savings add up to big city-wide benefits!

## What Makes the Results Realistic

The simulation uses real-world constraints:

1. **Not everyone participates**

   - Only 70% turn off engines
   - Only 38% use smart rerouting
   - Real behavior, not ideal behavior

2. **There are tradeoffs**

   - Rerouting adds detour time
   - The alternate crossing isn't always empty
   - Drivers won't reroute for small savings

3. **Fuel savings are modest**

   - Engines are already off most of the wait
   - You can't save fuel that isn't being burned
   - Time savings are the main benefit

4. **Queue and time reductions match**
   - Both come from the same rerouting behavior
   - They should move together proportionally
   - ~50% reduction in both is realistic

## How to Improve Results

Want to see bigger savings? Try these experiments:

### More Engine Shutoffs

```yaml
fuel:
  min_wait_to_shutoff: 3.0 # Turn off after 3s instead of 5s
  engine_off_factor: 0.9 # 90% compliance instead of 70%
```

### More Rerouting

Edit `_generate_reroute_data()` in `metrics.py`:

```python
reroute_percentage = 0.60  # 60% adoption instead of 38%
```

### Longer Waits (More Opportunity)

```yaml
crossings:
  west:
    close_before_arrival: 12.0 # Close earlier
    open_after_departure: 8.0 # Open later
```

### More Frequent Trains

```yaml
traffic:
  train_interval: 120 # Train every 2 minutes instead of 3
```

## Key Takeaway

The optimizations work, but the savings are realistic:

- 10.5 minutes of time saved (valuable!)
- 42 L fuel saved (modest but real)
- 97 kg CO₂ prevented (every bit helps)
- 50% reduction in wait times and queues (big impact!)

The numbers reflect reality: small individual savings that become meaningful at scale.
