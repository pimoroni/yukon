### Quad Servo Regulated Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Quad Servo Regulated Module for Yukon](https://pimoroni.com/yukon).

- [Constants](#constants)
- [Variables \& Properties](#variables--properties)
- [Methods](#methods)



#### Constants
```python
NAME = "Quad Servo Direct"
NUM_SERVOS = 4
```

#### Variables & Properties
```python
halt_on_not_pgood : bool
servos : list[Servo]
servo1 -> Servo
servo2 -> Servo
servo3 -> Servo
servo4 -> Servo
```




#### Methods
```python
## Address Checking ##
@staticmethod
is_module(adc1_level : int, adc2_level : int, slow1 : bool, slow2 : bool, slow3 :bool) -> bool

## Initialisation ##
QuadServoRegModule(halt_on_not_pgood=False : bool)
initialise(slot : SLOT, adc1_func : Any, adc2_func : Any) -> None
reset() -> None

## Power Control ##
enable() -> None
disable() -> None
is_enabled() -> bool

## Sensing ##
read_power_good() -> bool
read_temperature() -> float

## Monitoring ##
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```