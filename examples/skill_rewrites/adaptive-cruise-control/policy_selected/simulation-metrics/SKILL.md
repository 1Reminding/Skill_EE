---
name: simulation-metrics
description: Use this skill when calculating control system performance metrics such as rise time, overshoot percentage, steady-state error, or settling time for evaluating simulation results.
---

# Control System Performance Metrics

## Capability and use cases
Quantifying transient and steady-state response characteristics of control systems from time-series simulation data.

## Required artifacts
- `times`: List/array of time steps.
- `values`: List/array of system response values.
- `target`: Scalar setpoint value.

## API/tool patterns
```python
def rise_time(times, values, target):
    t10 = next((t for t, v in zip(times, values) if v >= 0.1 * target), None)
    t90 = next((t for t, v in zip(times, values) if v >= 0.9 * target), None)
    return t90 - t10 if (t10 is not None and t90 is not None) else None

def overshoot_percent(values, target):
    max_v = max(values)
    return ((max_v - target) / target) * 100 if max_v > target else 0.0

def steady_state_error(values, target, final_fraction=0.1):
    idx = int(len(values) * (1 - final_fraction))
    avg = sum(values[idx:]) / len(values[idx:])
    return abs(target - avg)

def settling_time(times, values, target, tolerance=0.02):
    band = target * tolerance
    settled_at = None
    for t, v in zip(times, values):
        if abs(v - target) > band: settled_at = None
        elif settled_at is None: settled_at = t
    return settled_at
```

## Implementation anchors
- **Rise Time**: Interval between 10% and 90% of `target`.
- **Overshoot**: Percentage by which `max(values)` exceeds `target`.
- **Steady-State Error**: Absolute difference between `target` and the average of the final 10% of data.
- **Settling Time**: The first time step after which the signal remains within `+/- tolerance` of `target`.

## Workflow
1. Extract `times` and `values` from simulation results.
2. Define the `target` setpoint.
3. Calculate metrics using the provided functions.
4. Evaluate system stability and performance against requirements.

## Validation checks
- Ensure `t90 > t10` for rise time.
- Verify `len(values) > 0` before calculating averages.
- Confirm `target != 0` for overshoot percentage calculations.

## Pitfalls
- **Noisy Data**: High-frequency noise can cause `settling_time` to return `None` or an incorrectly late value.
- **Zero Target**: `overshoot_percent` will fail if `target` is zero due to division by zero.
- **Insufficient Duration**: If the simulation ends before the system settles, `settling_time` and `steady_state_error` will be inaccurate.