# RM2 Wireless Module - Library Reference <!-- omit in toc -->

This is the library reference for the [RM2 Wireless Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
- [Initialising the Module](#initialising-the-module)
- [Reference](#reference)
  - [Constants](#constants)
  - [Functions](#functions)


**:information-source: Wireless is a baked-in feature of MicroPython, so the normal import and initialisation steps for Yukon modules are not strictly required to get your project online. There are still some advantages to doing these though, so the steps are explained below.**

## Getting Started

To start using a Wireless Module, you first need to import the class from `pimoroni_yukon.modules`.

```python
from pimoroni_yukon.modules import WirelessModule
```

Then create an instance of `WirelessModule`. This will also confirm that you have a wireless capable build flashed to your Yukon.

```python
module = WirelessModule()
```


## Initialising the Module

As with all Yukon modules, `WirelessModule` must be initialised before it can be used. This is achieved by first registering the module with the `Yukon` class, with the slot it is attached to.

```python
from pimoroni_yukon import SLOT5 as SLOT    # Only SLOT5 supports the RM2 Wireless Module at present

# Import and set up Yukon and WirelessModule instances

yukon.register_with_slot(module, SLOT)
```

Then `Yukon` can verify and initialise its modules.

```python
yukon.verify_and_initialise()
```

This checks each slot on the board to see if the modules expected by your program are physically attached to the board. Only if they match will the `WirelessModule` be initialised.

The RM2 Wireless Module is now ready to use. It can be interacted with using Micropython's `network` libraries, see Raspberry Pi's [Pico W tutorial](https://projects.raspberrypi.org/en/projects/get-started-pico-w/2).

From here you can optionally provide power to all your other modules by calling.
```python
yukon.enable_main_output()
```


## Reference

### Constants

```python
NAME = "RM2 Wireless"
```


### Functions

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3: bool) -> bool

# Initialisation
WirelessModule()
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
```
