# Bench Power Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Bench Power Module for Yukon](https://pimoroni.com/yukon).

- [Constants](#constants)
- [Variables \& Properties](#variables--properties)
- [Methods](#methods)


#### Constants
```python
NAME = "Bench Power"

VOLTAGE_MAX = 12.3953
VOLTAGE_MID = 6.5052
VOLTAGE_MIN = 0.6713
VOLTAGE_MIN_MEASURE = 0.1477
VOLTAGE_MID_MEASURE = 1.1706
VOLTAGE_MAX_MEASURE = 2.2007
PWM_MIN = 0.3
PWM_MAX = 0.0

TEMPERATURE_THRESHOLD = 50.0
```

#### Variables & Properties
```python
halt_on_not_pgood : bool
```

#### Methods
```python
## Address Checking ##
@staticmethod
is_module(adc1_level : int, adc2_level : int, slow1 : bool, slow2 : bool, slow3 :bool) -> bool

## Initialisation ##
BenchPowerModule(halt_on_not_pgood=False : bool)
initialise(slot : SLOT, adc1_func : Any, adc2_func : Any) -> None
reset() -> None

## Power Control
enable() -> None
disable() -> None
is_enabled() -> bool

## Output Control ##
set_target_voltage(voltage : float) -> None
set_target(percent : float) -> None

## Sensing ##
read_voltage() -> float
read_power_good() -> bool
read_temperature() -> float

## Monitoring ##
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```