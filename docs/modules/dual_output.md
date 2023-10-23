# Dual Switched Output Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Dual Switched Output Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
- [Initialising the Module](#initialising-the-module)
- [Using the Module](#using-the-module)
  - [Enabling its Outputs](#enabling-its-outputs)
  - [Accessing the Outputs](#accessing-the-outputs)
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

### Enabling its Outputs

With the `DualOutputModule` powered, its switches can be enabled or disabled by calling `.enable()` or `.disable()`. Without a parameter provided, these functions will control both switches. To control a single switch, provide the index of the output as a parameter e.g. `.enable(0)`.

The state can also be queried by calling `.is_enabled()`. Without a parameter provided, this will return the OR of both driver's enabled states. To query a single switch, provide the index of the output as a parameter e.g. `.is_enabled(0)`.

For convenience the constants `OUTPUT_1 = 0` and `OUTPUT_2 = 0` are provided.

:information_source: **Enabling a switch does not produce an output on its own. Rather, it "unlocks" the switch to respond to commands.**

### Accessing the Outputs

The `DualOutputModule` class uses MicroPython's native [Pin class](https://docs.micropython.org/en/latest/library/machine.Pin.html) for its outputs. To Pin objects are created and made accessible through the `.outputs` list.

Here is an example that enables and toggles one of the outputs.

```python
OUTPUT = DualOutputModule.OUTPUT_1

module.enable(OUTPUT)

while True:
    next_out_state = not module.outputs[OUTPUT].value()
    module.outputs[OUTPUT].value(next_out_state)
    yukon.monitored_sleep(1.0)
```

It is also possible to access the outputs individually using the properties `.output1`, and `.output2`.


### Onboard Sensors

The Dual Switched Output module features an onboard thermistor, letting its temperature be monitored. This can be read by calling `.read_temperature()`.

Additionally, the power good status of the two output switches can be read by calling `.read_power_good1()` and `.read_power_good2()`. These will be `True` during normal operation, but will switch to `False` under various conditions. For details of these conditions, check the [SLG55021 datasheet](https://www.renesas.com/eu/en/document/dst/slg55021-200010v-datasheet).


## References

#### Constants

```python
NAME = "Dual Switched Output"
OUTPUT_1 = 0
OUTPUT_2 = 1
NUM_OUTPUTS = 2
TEMPERATURE_THRESHOLD = 50.0
```

#### Variables
```python
halt_on_not_pgood: bool

outputs: list[Pin]
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
enable(output: int | None=None) -> None
disable(output: int | None=None) -> None
is_enabled(output: int | None=None) -> bool

# Access
@property
output1 -> Pin
@property
output2 -> Pin

# Sensing
read_power_good1() -> bool
read_power_good2() -> bool
read_temperature(samples: int=1) -> float

# Monitoring
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```
