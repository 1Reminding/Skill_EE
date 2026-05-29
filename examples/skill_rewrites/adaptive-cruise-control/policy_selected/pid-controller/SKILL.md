---
name: pid-controller
description: Use this skill when implementing PID control loops for adaptive cruise control, vehicle speed regulation, throttle/brake management, or any feedback control system requiring proportional-integral-derivative control.
---

# PID Controller Implementation

## Capability and use cases
Feedback control for vehicle dynamics (ACC, speed regulation, throttle/brake) and industrial systems requiring error correction based on proportional, integral, and derivative terms.

## Required artifacts
- Gains: `Kp` (Proportional), `Ki` (Integral), `Kd` (Derivative).
- Inputs: `setpoint`, `measured_value`, `dt` (timestep).

## API/tool patterns
```python
class PIDController:
    def __init__(self, kp, ki, kd, output_min=None, output_max=None):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.output_min, self.output_max = output_min, output_max
        self.integral = self.prev_error = 0.0

    def reset((self):
        self.integral = self.prev_error = 0.0

    def compute(self, error, dt):
        p_term = self.kp * error
        self.integral += error * dt
        i_term = self.ki * self.integral
        d_term = self.kd * (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error
        out = p_term + i_term + d_term
        if self.output_min is not None: out = max(out, self.output_min)
        if self.output_max is not None: out = min(out, self.output_max)
        return out
```

## Implementation anchors
- Control Law: `output = Kp * error + Ki * integral(error) + Kd * derivative(error)`
- `error = setpoint - measured_value`

## Workflow
1. **Manual Tuning**: Initialize Ki = Kd = 0.
2. **Proportional**: Increase Kp until response speed is acceptable.
3. **Integral**: Add Ki to eliminate steady-state error (may cause oscillation).
4. **Derivative**: Add Kd to reduce overshoot (increases noise sensitivity).

## Validation checks
- Ensure `dt > 0` to avoid division by zero in derivative term.
- Apply output clamping (`output_min`/`output_max`) to match actuator limits.
- Monitor for steady-state error elimination.

## Pitfalls
- **Integral Windup**: Occurs when output saturates but integral continues to accumulate. Mitigate via clamping or conditional integration.
- **Noise Sensitivity**: High Kd values amplify measurement noise.
- **Instability**: Excessive Kp or Ki leads to system oscillation.