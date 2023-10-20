# Dual Switched Output Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Dual Switched Output Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
- [Initialising the Module](#initialising-the-module)
- [Using the Module](#using-the-module)
  - [Controlling its Outputs](#controlling-its-outputs)
  - [Onboard Sensors](#onboard-sensors)
- [References](#references)
    - [Constants](#constants)
    - [Variables](#variables)
  - [Functions](#functions)



## Getting Started

To start using a Dual Switched Output Module, you first need to import the class from `pimoroni_yukon.modules`.

```python
from pimoroni_yukon.modules import DualOutputModule
```

Then create an instance of `DualOutputModule`.

```python
module = DualOutputModule()
```


## Initialising the Module

As with all Yukon modules, `DualOutputModule` must be initialised before it can be used. This is achieved by first registering the module with the `Yukon` class, with the slot it is attached to.

```python
from pimoroni_yukon import SLOT1 as SLOT

# Import and set up Yukon and DualOutputModule instances

yukon.register_with_slot(module, SLOT)
```

Then `Yukon` can verify and initialise its modules.

```python
yukon.verify_and_initialise()
```

This checks each slot on the board to see if the modules expected by your program are physically attached to the board. Only if they match will the `DualOutputModule` be initialised, giving it access to the GPIO of the slot it is attached to.

Power can now be provided to all modules, by calling.

```python
yukon.enable_main_output()
```


## Using the Module

### Controlling its Outputs

With the `DualOutputModule` powered, its outputs can be enabled or disabled by calling `.enable(output)` or `.disable(output)`. The state can also be queried by calling `.is_enabled(output)`. `output` is either `1` or `2`.

Enabling an output does not cause it to produce a voltage, but rather "unlocks" the output to be controllable.

Control an output by calling `.output(output, value)` where `output` is either `1` or `2` and `value` is either `True` or `False`. The control state of an output can also be read, by calling `read_output(output)`.

Here is an example that toggles one of the outputs.

```python
OUTPUT = 1

module.enable(OUTPUT)

while True:
    next_out_state = not module.read_output(OUTPUT)
    module.output(OUTPUT, next_out_state)
    yukon.monitored_sleep(1.0)
```


### Onboard Sensors

The Dual Switched Output module features an onboard thermistor, letting its temperature be monitored. This can be read by calling `.read_temperature()`.

Additionally, the power good status of the two output switches can be read by calling `.read_power_good(output)`, where `output` is either `1` or `2`. This will be `True` during normal operation, but will switch to `False` under various conditions. For details of these conditions, check the [SLG55021 datasheet](https://www.renesas.com/eu/en/document/dst/slg55021-200010v-datasheet).


## References

#### Constants

```python
NAME = "Dual Switched Output"
NUM_OUTPUTS = 2
TEMPERATURE_THRESHOLD = 50.0
```

#### Variables
```python
halt_on_not_pgood: bool
```

### Functions

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3: bool) -> bool

# Initialisation
DualOutputModule(halt_on_not_pgood=False: bool)
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
reset() -> None

# Power Control
enable(output: int) -> None
disable(output: int) -> None
is_enabled(output: int) -> bool

# Output Control
output(output: int, value: bool) -> None
read_output(output: int) -> bool

# Sensing
read_power_good(output: int) -> bool
read_temperature() -> float

# Monitoring
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```
