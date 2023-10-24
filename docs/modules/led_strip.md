# LED Strip Module - Library Reference <!-- omit in toc -->

This is the library reference for the [LED Strip Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
  - [Strip Types](#strip-types)
- [Initialising the Module](#initialising-the-module)
- [Using the Module](#using-the-module)
  - [Enabling its Output](#enabling-its-output)
  - [Accessing the LED Strip](#accessing-the-led-strip)
  - [Onboard Sensors](#onboard-sensors)
- [References](#references)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Functions](#functions)


## Getting Started

To start using a LED Strip Module, you first need to import the class from `pimoroni_yukon.modules`.

```python
from pimoroni_yukon.modules import LEDStripModule
```

Then create an instance of `LEDStripModule`, giving it details of the LEDs you wish to drive, and which PIO and State Machine (SM) to use.

```python
# Constants
STRIP_TYPE = LEDStripModule.NEOPIXEL
STRIP_PIO = 0
STRIP_SM = 0
LEDS_PER_STRIP = 60
BRIGHTNESS = 1.0        # Only functional with APA102 (DOTSTAR)

module = LEDStripModule(STRIP_TYPE,
                        STRIP_PIO,
                        STRIP_SM, 
                        LEDS_PER_STRIP,
                        BRIGHTNESS)
```

:warning: **Be sure to choose a PIO and State Machine that does not conflict with any others you have already set up.**

### Strip Types

Both WS2812's (aka NeoPixels) and APA102's (aka DotStars) are supported by the `LEDStripModule`.

There is also a third mode, where two WS2812 strips can be driven off the one module, by wiring one to the DAT line as normal, and the other to the CLK line.

Strip types can accessed with the following constants:

* `LEDStripModule.NEOPIXEL` = `0`
* `LEDStripModule.DUAL_NEOPIXEL` = `1`
* `LEDStripModule.DOTSTAR` = `2`

When using the `DUAL_NEOPIXEL` strip type, the lengths of the two strips can be provided as a tuple pair as the `LEDS_PER_STRIP` constant from the getting started section, or left as a single value if both strips are the same length.

## Initialising the Module

As with all Yukon modules, `LEDStripModule` must be initialised before it can be used. This is achieved by first registering the module with the `Yukon` class, with the slot it is attached to.

```python
from pimoroni_yukon import SLOT1 as SLOT

# Import and set up Yukon and LEDStripModule instances

yukon.register_with_slot(module, SLOT)
```

Then `Yukon` can verify and initialise its modules.

```python
yukon.verify_and_initialise()
```

This checks each slot on the board to see if the modules expected by your program are physically attached to the board. Only if they match will the `LEDStripModule` be initialised, giving it access to the GPIO of the slot it is attached to.

Power can now be provided to all modules, by calling.

```python
yukon.enable_main_output()
```

## Using the Module

### Enabling its Output

With the `LEDStripModule` powered, its output to the strip(s) can be enabled or disabled by calling `.enable()` or `.disable()`. The state can also be queried by calling `.is_enabled()`.

### Accessing the LED Strip

The `LEDStripModule` class makes use of the [Plasma Library](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/plasma/README.md). Depending on the strip type provided during creation, either an APA102 objects or WS2812 objects will be accessible through the variable `.strip`.

For example, to set all the LEDs of the strip to full (for either APA102 or WS2812), the following loop can be run:

```python
for led in range(module.strip.num_leds()):
    module.strip.set_rgb(led, 255, 255, 255)

module.strip.update()
```

For the case of the `DUAL_NEOPIXEL` strip type, a `.strips` list is accessible containing two WS2812 objects, instead of a `.strip` variable. There are also `.strip1` and `.strip2` properties to make access to these strips easier.

### Onboard Sensors

The LED Strip module features an onboard thermistor, letting its temperature be monitored. This can be read by calling `.read_temperature()`.

Additionally, the power good status of the onboard regulator can be read by calling `.read_power_good()`. This will be `True` during normal operation, but will switch to `False` under various conditions such as the input voltage dropping below what is needed for the module to achieve a stable output. For details of other conditions, check the [TPS54A24 datasheet](https://www.ti.com/lit/ds/symlink/tps54a24.pdf).


## References

### Constants

```python
NAME = "LED Strip"
NEOPIXEL = 0
DUAL_NEOPIXEL = 1
DOTSTAR = 2
STRIP_1 = 0       # Only for DUAL_NEOPIXEL strip_type
STRIP_2 = 1       # Only for DUAL_NEOPIXEL strip_type
NUM_STRIPS = 1    # Becomes 2 with the DUAL_NEOPIXEL strip_type
TEMPERATURE_THRESHOLD = 70.0
```

### Variables
```python
halt_on_not_pgood: bool

# If strip_type is NEOPIXEL or DOTSTAR
strip: APA102 | WS2812

# If strip_type is DUAL_NEOPIXEL
strips: list[WS2812]
```

### Functions

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3: bool) -> bool

# Initialisation
LEDStripModule(strip_type: int, pio: int, sm: int, num_leds: int, brightness: float=1.0, halt_on_not_pgood: bool=False)
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
reset() -> None

# Power Control
enable() -> None
disable() -> None
is_enabled() -> bool

# Access (only usable when strip_type is DUAL_NEOPIXEL)
@property
strip1 -> WS2812
@property
strip2 -> WS2812

# Sensing
read_power_good() -> bool
read_temperature(samples: int=1) -> float

# Monitoring
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```
