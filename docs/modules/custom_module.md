# Pimoroni Yukon - Custom Module <!-- omit in toc -->

This is instructions for defining a custom module for the [Pimoroni Yukon](https://pimoroni.com/yukon), a high-power modular robotics and engineering platform, powered by the Raspberry Pi RP2040.

- [Creating the Class](#creating-the-class)
- [Expanding the Class](#expanding-the-class)
- [Adding Monitoring](#adding-monitoring)
  - [Analog](#analog)
  - [Digital](#digital)


## Creating the Class

To have a custom module work with the Yukon library's verification and initialisation procedure, a new class should be created. For the purpose of this explanation it will be called `CustomModule`.

This class should do the following:

* Inherit from `YukonModule` e.g. `class CustomModule(YukonModule):`
* Have a constant within it called `NAME` with a user friendly name to describe the module, e.g. `Custom`
* Implement the static method `def is_module(adc1_level, adc2_level, slow1, slow2, slow3):` and have a unique address.
* Implement `def __init__(self):` and immediately call `super().__init__()` on the line below.
* Be included in the `KNOWN_MODULES` list within `pimoroni_yukon/modules/__init__.py`

Below is an example of a minimal viable module class, that will be recognised by Yukon but not perform any function:

```python
from .common import YukonModule, ADC_LOW, ADC_FLOAT, ADC_HIGH, IO_LOW, IO_HIGH

class CustomModule(YukonModule):
    NAME = "Custom"

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | ?     | ?     | ?     | ?     | ?     | Custom               |                             |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level is ? and adc2_level is ? and slow1 is ? and slow2 is ? and slow3 is ?

    def __init__(self):
        super().__init__()
```

The above `is_module` static method is intentionally missing ADC and IO states (as noted by `?`). To understand more about module addresses, refer to the [Module Detection](../module_detection.md) page.


## Expanding the Class

To make the new `CustomModule` class control hardware, it should implement the `.initialise()` and `.reset()` functions, along with any other functions to interact with the hardware. Note that `super().initialise(slot, adc1_func, adc2_func)` must be called as the last line of `.initialise()`.

For example, here our custom module is set up with a push button and a mono LED:
```python
def initialise(self, slot, adc1_func, adc2_func):

    # Create the button pin object
    self.__button = slot.FAST1
    self.__button.init(Pin.IN, Pin.PULL_UP)

    # Create the LED pin object
    self.__led = slot.FAST2
    self.__led.init(Pin.OUT)

    # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
    super().initialise(slot, adc1_func, adc2_func)

def reset(self):
    self.__led.value(False)

def is_pressed(self):
    return self.__button.value() != 1

def led_on(self):
    self.__led.value(True)

def led_off(self):
    self.__led.value(False)
```

## Adding Monitoring

If the custom module has any sensors onboard that should be monitored along with Yukon's internal sensors, `.monitor()`, `.get_readings()`, `process_readings()` and `.clear_readings()` should be implemented.

### Analog

Here's an example of the `CustomModule` class monitoring an analog sensor connected to ADC1:
```python
def read_sensor(self, samples=1):
    return self.__read_adc1(samples)

def monitor(self):
    value = self.read_sensor()

    # Run some user action based on the latest readings
    if self.__monitor_action_callback is not None:
        self.__monitor_action_callback(value)

    self.__max_value = max(value, self.__max_value)
    self.__min_value = min(value, self.__min_value)
    self.__avg_value += value
    self.__count_avg += 1

def get_readings(self):
    return OrderedDict({
        "max": self.__max_value,
        "min": self.__min_value,
        "avg": self.__avg_value
    })

def process_readings(self):
    if self.__count_avg > 0:
        self.__avg_value /= self.__count_avg
        self.__count_avg = 0    # Clear the count to prevent process readings acting more than once

def clear_readings(self):
    self.__max_value = float('-inf')
    self.__min_value = float('inf')
    self.__avg_value = 0
    self.__count_avg = 0
```

### Digital

Here's an example of the `CustomModule` class monitoring the button:
```python
def monitor(self):
    pressed = self.is_pressed()

    # Run some user action based on the latest readings
    if self.__monitor_action_callback is not None:
        self.__monitor_action_callback(pressed)

    self.__was_pressed = self.__was_pressed or pressed

def get_readings(self):
    return OrderedDict({
        "Pressed": self.__was_pressed
    })

def clear_readings(self):
    self.__was_pressed = False
```
