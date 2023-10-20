### Dual Motor / Bipolar Stepper Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Dual Motor / Bipolar Stepper Module for Yukon](https://pimoroni.com/yukon).

- [Constants](#constants)
- [Variables \& Properties](#variables--properties)
- [Method](#method)


#### Constants
```python
NAME = "Dual Motor"
DUAL = 0
STEPPER = 1
NUM_MOTORS = 2
NUM_STEPPERS = 1
FAULT_THRESHOLD = 0.1
DEFAULT_FREQUENCY = 25000
TEMPERATURE_THRESHOLD = 50.0
```

#### Variables & Properties
```python
motors : list[Motor]
motor1 -> Motor
motor2 -> Motor
stepper : Stepper
```

#### Method
```python
## Address Checking ##
@staticmethod
is_module(adc1_level : int, adc2_level : int, slow1 : bool, slow2 : bool, slow3 :bool) -> bool

## Initialisation ##
DualMotorModule(motor_type=DUAL : int,
                frequency=DEFAULT_FREQUENCY : float)
initialise(slot : SLOT, adc1_func : Any, adc2_func : Any) -> None
reset() -> None

## Power Control ##
enable() -> None
disable() -> None
is_enabled() -> bool

## Output Control ##
...

## Sensing
read_fault() -> bool
read_temperature() -> float

## Monitoring ##
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```