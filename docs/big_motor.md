### Big Motor Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Big Motor + Encoder Module for Yukon](https://pimoroni.com/yukon).

- [Constants](#constants)
- [Variables \& Properties](#variables--properties)
- [Methods](#methods)


#### Constants
```python
NAME = "Big Motor + Encoder"
NUM_MOTORS = 1
DEFAULT_FREQUENCY = 25000
TEMPERATURE_THRESHOLD = 50.0
CURRENT_THRESHOLD = 25.0
SHUNT_RESISTOR = 0.001
GAIN = 80
```

#### Variables & Properties
```python
motor : Motor
```

#### Methods
```python
## Address Checking ##
@staticmethod
is_module(adc1_level : int, adc2_level : int, slow1 : bool, slow2 : bool, slow3 :bool) -> bool

## Initialisation ##
BigMotorModule(frequency=DEFAULT_FREQUENCY : float)
initialise(slot : SLOT, adc1_func : Any, adc2_func : Any) -> None
reset() -> None

## Power Control ##
enable() -> None
disable() -> None
is_enabled() -> bool

## Sensing ##
read_fault() -> bool
read_current() -> float
read_temperature() -> float

## Monitoring ##
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```