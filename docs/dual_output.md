### Dual Switched Output Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Dual Switched Output Module for Yukon](https://pimoroni.com/yukon).

- [Constants](#constants)
- [Variables \& Properties](#variables--properties)



#### Constants
```python
NAME = "Dual Switched Output"
NUM_OUTPUTS = 2
TEMPERATURE_THRESHOLD = 50.0
```

#### Variables & Properties
```python
halt_on_not_pgood : bool
```

```python
## Address Checking ##
@staticmethod
is_module(adc1_level : int, adc2_level : int, slow1 : bool, slow2 : bool, slow3 :bool) -> bool

## Initialisation ##
DualOutputModule(halt_on_not_pgood=False : bool)
initialise(slot : SLOT, adc1_func : Any, adc2_func : Any) -> None
reset() -> None

## Power Control ##
enable() -> None
disable() -> None
is_enabled() -> bool

## Output Control
output(switch : int, value : bool) -> None
read_output(switch : int) -> bool

## Sensing ##
read_power_good(switch : int) -> bool
read_temperature() -> float

## Monitoring ##
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```
