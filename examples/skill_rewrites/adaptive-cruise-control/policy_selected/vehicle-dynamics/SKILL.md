---
name: vehicle-dynamics
description: Use this skill when simulating vehicle motion, calculating safe following distances, time-to-collision, speed/position updates, or implementing vehicle state machines for cruise control modes.
---

# Vehicle Dynamics Simulation

## Capability and use cases
Simulating discrete-time vehicle motion, calculating safety metrics (TTC, headway), and implementing cruise control state machines.

## Required artifacts
- State variables: `current_speed`, `current_position`, `acceleration`, `dt`.
- Lead vehicle data: `lead_speed`, `current_distance`.
- Constraints: `max_accel`, `max_decel`, `time_headway`, `min_distance`, `ttc_threshold`.

## API/tool patterns
```python
# Kinematic Updates
new_speed = max(0, current_speed + acceleration * dt)
new_position = current_position + speed * dt
new_distance = current_distance - (ego_speed - lead_speed) * dt
```

## Implementation anchors
```python
def safe_following_distance(speed, time_headway, min_distance):
    return speed * time_headway + min_distance

def time_to_collision(distance, ego_speed, lead_speed):
    rel_speed = ego_speed - lead_speed
    return distance / rel_speed if rel_speed > 0 else None

def clamp_acceleration(accel, max_accel, max_decel):
    return max(max_decel, min(accel, max_accel))
```

## Workflow
1. Update ego state using kinematic equations.
2. Calculate relative metrics (TTC, distance) if lead vehicle exists.
3. Determine control mode: 'cruise' (no lead), 'emergency' (TTC < threshold), or 'follow'.
4. Apply clamped acceleration based on mode logic.

## Validation checks
- Ensure `new_speed` is never negative.
- Verify `rel_speed > 0` before TTC calculation to avoid division by zero or invalid approaching states.
- Confirm acceleration is within `[max_decel, max_accel]`.

## Pitfalls
- Division by zero in TTC when speeds are matched or lead is faster.
- Ignoring physical limits (max deceleration) during emergency braking simulations.
- Accumulating floating point error in `new_position` over long durations without reset.