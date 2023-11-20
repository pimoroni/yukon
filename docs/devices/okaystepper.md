# OkayStepper Class - Library Reference <!-- omit in toc -->

This is the library reference for the `OkayStepper` class used to drive bipolar stepper motors with Pimoroni Yukon's [Dual Motor Module](https://pimoroni.com/yukon).

- [References](#references)
  - [Constants](#constants)
  - [Functions](#functions)


## References

### Constants

```python
DEFAULT_CURRENT_SCALE = 0.5
HOLD_CURRENT_PERCENT = 0.2
STEP_PHASES = 4
DEFAULT_MICROSTEPS = 8
```


### Functions

```python
# Initialisation
OkayStepper(motor_a: Motor,
            motor_b: Motor,
            alt_motor_a: Motor=None,
            alt_motor_b: Motor=None,
            steps_per_unit: float=1.0,
            current_scale: float=DEFAULT_CURRENT_SCALE,
            microsteps: int=DEFAULT_MICROSTEPS,
            debug_pin: Pin=None)

# Power Control
hold() -> None
release() -> None

# Movement
is_moving() -> bool
wait_for_move() -> None
move_to_step(step: float, duration: float, debug: bool=False) -> None
move_by_steps(steps: float, duration: float, debug: bool=False) -> None
move_to(unit: float, duration: float, debug: bool=False) -> None
move_by(units: float, duration: float, debug: bool=False) -> None

# Position
steps() -> float
units() -> float
step_diff(step: float) -> float
unit_diff(unit: float) -> float
zero_position() -> None
```
