# Bench Power Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Bench Power Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
- [Initialising the Module](#initialising-the-module)
- [Using the Module](#using-the-module)
  - [Controlling its Output](#controlling-its-output)
  - [Changing its Voltage](#changing-its-voltage)
  - [Onboard Sensors](#onboard-sensors)
- [References](#references)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Methods](#methods)


## Getting Started

To start using a Bench Power Module, you first need to import the class from `pimoroni_yukon.modules`.

```python
from pimoroni_yukon.modules import BenchPowerModule
```

Then create an instance of `BenchPowerModule`.

```python
module = BenchPowerModule()
```


## Initialising the Module

As with all Yukon modules, `BenchPowerModule` must be initialised before it can be used. This is achieved by first registering the module with the `Yukon` class, with the slot it is attached to.

```python
from pimoroni_yukon import SLOT1 as SLOT

# Import and set up Yukon and BenchPowerModule instances

yukon.register_with_slot(module, SLOT)
```

Then `Yukon` can verify and initialise its modules.

```python
yukon.verify_and_initialise()
```

This checks each slot on the board to see if the modules expected by your program are physically attached to the board. Only if they match will the `BenchPowerModule` be initialised, giving it access to the GPIO of the slot it is attached to.

Power can now be provided to all modules, by calling.

```python
yukon.enable_main_output()
```


## Using the Module

### Controlling its Output

With the `BenchPowerModule` powered, its output can be enabled or disabled by calling `.enable()` or `.disable()`. The state can also be queried by calling `.is_enabled()`.


### Changing its Voltage

The output voltage of the Bench Power module can be changed in two ways.

The first is by calling `.set_voltage(voltage)`, and providing it with a voltage up to 12.4V.

The second is by calling `.set_percent(percent)`, and providing it with a value from `0.0` to `1.0`.


### Onboard Sensors

The Bench Power module features a voltage divider, letting its output be measured by calling `.read_voltage()`.

There is also an onboard thermistor, letting its temperature be monitored. This can be read by calling `.read_temperature()`.

Additionally, the power good status of the onboard regulator can be read by calling `.read_power_good()`. This will be `True` during normal operation, but will switch to `False` under various conditions such as the input voltage dropping below what is needed for the module to achieve a stable output. For details of other conditions, check the [TPS54A24 datasheet](https://www.ti.com/lit/ds/symlink/tps54a24.pdf).


## References

### Constants

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
TEMPERATURE_THRESHOLD = 80.0
```


### Variables

```python
halt_on_not_pgood: bool

FAST3 = Pin
FAST4 = Pin
```


### Methods

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3: bool) -> bool

# Initialisation
BenchPowerModule(halt_on_not_pgood: bool=False)
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
reset() -> None

# Power Control
enable() -> None
disable() -> None
is_enabled() -> bool

# Output Control
set_voltage(voltage: float) -> None
set_percent(percent: float) -> None

# Sensing
read_voltage(samples: int=1) -> float
read_power_good() -> bool
read_temperature(samples: int=1) -> float

# Monitoring
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```
