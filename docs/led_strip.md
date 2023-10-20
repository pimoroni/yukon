### LED Strip Module - Library Reference <!-- omit in toc -->

This is the library reference for the [LED Strip Module for Yukon](https://pimoroni.com/yukon).

- [Constants](#constants)
- [Variables \& Properties](#variables--properties)
- [Methods](#methods)



#### Constants
```python
NAME = "LED Strip"
NEOPIXEL = 0
DOTSTAR = 1
TEMPERATURE_THRESHOLD = 50.0
```

#### Variables & Properties
```python
halt_on_not_pgood -> bool
```

#### Methods
```python
## Address Checking ##
@staticmethod
is_module(adc1_level : int, adc2_level : int, slow1 : bool, slow2 : bool, slow3 :bool) -> bool

## Initialisation ##
LEDStripModule(strip_type : int, num_pixels : int, brightness=1.0 : float, halt_on_not_pgood=False : bool)
initialise(slot : SLOT, adc1_func : Any, adc2_func : Any) -> None
reset() -> None

## Misc ##
count() -> int

## Power Control
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