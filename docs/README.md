# Yukon - Library Reference <!-- omit in toc -->

This is the library reference for the [Pimoroni Yukon](https://pimoroni.com/yukon), a high-powered modular robotics and engineering platform, powered by the Raspberry Pi RP2040.


## Table of Content <!-- omit in toc -->
- [Getting Started](#getting-started)
- [Reading the User Buttons](#reading-the-user-buttons)
- [Setting the User LEDs](#setting-the-user-leds)
- [Time Delays and Sleeping](#time-delays-and-sleeping)
- [Reading Sensors Directly](#reading-sensors-directly)
- [Program Lifecycle](#program-lifecycle)
- [Function Reference](#function-reference)
  - [Yukon](#yukon)
    - [Constants](#constants)
    - [Methods](#methods)
  - [Yukon Module](#yukon-module)
- [Constants Reference](#constants-reference)
  - [Slot Constants](#slot-constants)


## Getting Started

To start coding your Yukon, you will need to add the following lines to the start of your code file.

```python
from pimoroni_yukon import Yukon
yukon = Yukon()
```

This will create a `Yukon` class called `yukon` that will be used in the rest of the examples going forward.


## Reading the User Buttons

Yukon has three user buttons along its bottom edge, labelled **A**, **B** and **Boot/User**. These can be read using the `is_pressed()` and `is_boot_pressed()` functions, respectively. To read all three buttons you would write:

```python
state_a = yukon.is_pressed('A')
state_b = yukon.is_pressed('B')
state_boot = yukon.is_boot_pressed()
```

In addition to the onboard buttons, it is possible to wire up external **A**, **B** and **Boot/User** buttons, letting you interact with Yukon when inside of an enclosure. These are exposed on the **Expansion** and **CTRL** headers along the top edge of the board, either side of the USB and power inputs.


## Setting the User LEDs

Yukon has two user LEDs along its bottom edge, labelled **A** and **B**. These can be set using the `set_led()` function. To set both LEDs you would write, passing in either `True` or `False`:

```python
yukon.set_led('A', True)
yukon.set_led('B', False)
```

It is also possible to read back the current state of the LEDs using the `.is_led_on()` function.

```python
state_a = yukon.is_led_on('A')
state_b = yukon.is_led_on('B')
```


## Time Delays and Sleeping

Yukon features onboard sensors for monitoring voltage, current and temperature, both of the board itself, and its attached modules.

Although it is possible to read these sensors standalone, it is recommended to let the library handle this as part of its range of monitoring functions. These are:

* `monitored_sleep(seconds)` - Repeatedly checks each sensor for a given number of seconds
* `monitored_sleep_ms(ms)` - Repeatedly checks each sensor for a given number of milliseconds
* `monitor_until_ms(end_ms)` - Repeatedly checks each sensor until a given end time has been reached (in milliseconds)
* `monitor_once()` - Checks each sensor once, and summarises the readings

:warning: These functions should be used in place of the regular `time.sleep()`. This lets Yukon turn off the main output and raise exceptions in the event of dangerous conditions, protecting your hardware.

The kinds of exceptions raised are: `OverVoltageError`, `UnderVoltageError`, `OverCurrentError`, `OverTemperatureError`, and `FaultError`. These are in addition to any standard python errors that may occur as a result of code running within monitor.

:information_source: The end time that `monitor_until_ms()` expects is a value from the `time.ticks_ms()`.

Depending on the logging level set on Yukon, the monitor functions will print out the readings they have accumulated over their operation. For example, the minimum, maximum, and average voltage detected. For heavily populated Yukon boards, this printout can be quite lengthy, so the values shown can be filtered with optional `allowed` and `excluded` parameters. Below is an example of a sleep that will only report the maximum current.

```python
yukon.monitored_sleep(0.01, allowed="C_max")
```

After a monitor function has completed, the values it obtained can be accessed with the `get_readings()` function, which returns an ordered dictionary of key value pairs. The below example shows how the average temperature over the monitoring period can be read.

```python
readings = yukon.get_readings()
temperature = readings["T_avg"]
```

## Reading Sensors Directly

In the event that your code needs to read Yukon's sensors directly, the following functions can be used:

* `read_voltage()`
* `read_current()`
* `read_temperature()`
* `read_expansion()`
* `read_slot_adc1(slot)`
* `read_slot_adc2(slot)`

In addition, each module will have functions for reading its various sensors:


| Function           | Audio Amp | Bench Power | Big Motor | Dual Motor | Dual Switched | LED Strip | Quad Servo Direct | Quad Servo Reg | Serial Servo |
|--------------------|-----------|-------------|-----------|------------|---------------|-----------|-------------------|----------------|--------------|
`read_voltage()`     | -         | Yes         | -         | -          | -             | -         | -                 | -              | -            |
`read_current()`     | -         | -           | Yes       | -          | -             | -         | -                 | -              | -            |
`read_temperature()` | Yes       | Yes         | Yes       | Yes        | Yes           | Yes       | -                 | Yes            | -            |
`read_power_good()`  | -         | Yes         | -         | -          | Yes           | Yes       | -                 | Yes            | -            |
`read_fault()`       | -         | -           | Yes       | Yes        | -             | -         | -                 | -              | -            |
`read_adc1()`        | -         | -           | -         | -          | -             | -         | Yes               | -              | -            |
`read_adc2()`        | -         | -           | -         | -          | -             | -         | Yes               | -              | -            |


## Program Lifecycle

When writing a program for Yukon, there are a number of steps that should be included to make best use of the board's capabilities.


```python
# Start with any imports needed for your program
from pimoroni_yukon import Yukon

# Import the classes for the modules you intend to use
from pimoroni_yukon.modules import <ModuleClass>  # e.g. LEDStripModule

# Import the logging levels to use (if you wish to change from the default)
from pimoroni_yukon.logging import LOG_NONE, LOG_WARN, LOG_INFO, LOG_DEBUG

# Create an instance of the Yukon class, configuring any software limits for voltage, current, and temperature. The logging level can also be set here.
yukon = Yukon(voltage_limit=<?>, current_limit=<?>, temperature_limit=<?>, logging_level=<?>)

# Create instances of your modules here, if their slots are known
module = <ModuleClass>

# Start a try block to catch any exceptions and put the board back into a safe state
try:

  # Register modules with the Yukon class
  yukon.register_with_slot(module, 1)

  # Initialise Yukon's registered modules
  yukon.verify_and_initialise()

  # Turn on the module power
  yukon.enable_main_output()

  # Enable the module
  module.enable()

  # Loop forever
  while True:
    <User Code Goes Here>

    # Perform a monitored sleep
    yukon.monitored_sleep(0.1)

# Reset the yukon instance if the program completes successfully or an exception occurs
finally:
    yukon.reset()
```


## Function Reference

### Yukon

#### Constants
```python
VOLTAGE_MAX = 17.0
VOLTAGE_MIN_MEASURE = 0.030
VOLTAGE_MAX_MEASURE = 2.294

CURRENT_MAX = 10.0
CURRENT_MIN_MEASURE = 0.0147
CURRENT_MAX_MEASURE = 0.9307

SWITCH_A = 0
SWITCH_B = 1
SWITCH_A_NAME = 'A'
SWITCH_B_NAME = 'B'
SWITCH_USER = 2
NUM_SLOTS = 6

DEFAULT_VOLTAGE_LIMIT = 17.2
VOLTAGE_LOWER_LIMIT = 4.8
VOLTAGE_ZERO_LEVEL = 0.05
DEFAULT_CURRENT_LIMIT = 20
DEFAULT_TEMPERATURE_LIMIT = 90
ABSOLUTE_MAX_VOLTAGE_LIMIT = 18

DETECTION_SAMPLES = 64
DETECTION_ADC_LOW = 0.1
DETECTION_ADC_HIGH = 3.2
```

#### Methods
Here is the complete list of methods available on the `Yukon` class:
```python
# Initialisation
Yukon(voltage_limit=DEFAULT_VOLTAGE_LIMIT : float,
      current_limit=DEFAULT_CURRENT_LIMIT : float,
      temperature_limit=DEFAULT_TEMPERATURE_LIMIT : float
      logging_level=logging.LOG_INFO : int)
reset() -> None

# Misc
change_logging(logging_level : int) -> None

# Slot
find_slots_with(module_type : type[YukonModule]) -> list[SLOT]
register_with_slot(module : YukonModule, slot : int | SLOT) -> None
deregister_slot(slot : int | SLOT) -> None
detect_in_slot(slot : int | SLOT) -> type[YukonModule]
verify_and_initialise(allow_unregistered : bool | int | SLOT | list | tuple,
                   allow_undetected : bool | int | SLOT | list | tuple
                   allow_discrepencies : bool | int | SLOT | list | tuple,
                   allow_no_modules : bool) -> None

# Interaction
is_pressed(switch : int | string) -> bool
is_boot_pressed() -> bool
is_led_on(switch: int | string) -> bool
set_led(switch : int | string, value : bool) -> None

# Power Control
enable_main_output() -> None
disable_main_output() -> None
is_main_output_enabled() -> bool

# Sensing
read_input_voltage() -> float
read_output_voltage() -> float
read_current() -> float
read_temperature() -> float
read_slot_adc1(slot : SLOT) -> float
read_slot_adc2(slot : SLOT) -> float

# Monitoring
assign_monitor_action(callback_function : Any) -> None
monitor() -> None
monitored_sleep(seconds : float, allowed : list | None, excluded : list | None) -> None
monitored_sleep_ms(ms : int, allowed : list | None, excluded : list | None) -> None
monitor_until_ms(end_ms : int, allowed : list | None, excluded : list | None) -> None
monitor_once(allowed : list | None, excluded : list | None) -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```

### Yukon Module

```python
# Address Checking
@staticmethod
is_module(adc1_level : int, adc2_level : int, slow1 : bool, slow2 : bool, slow3 :bool) -> bool

# Initialisation
YukonModule()
initialise(slot : SLOT, adc1_func : Any, adc2_func : Any) -> None
is_initialised() -> bool
deregister() -> None
reset() -> None

# Monitoring
assign_monitor_action(callback_function : Any) -> None
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```


## Constants Reference

Here is the complete list of constants on the `yukon` module:

### Slot Constants

These constants represent each of the 6 slots on Yukon. They are a namedtuple containing the ID of the slot and which pins that slot is associated with.

**`SLOT1`**
```python
ID = 1
FAST1 = Pin.board.SLOT1_FAST1
FAST2 = Pin.board.SLOT1_FAST2
FAST3 = Pin.board.SLOT1_FAST3
FAST4 = Pin.board.SLOT1_FAST4
SLOW1 = Pin.board.SLOT1_SLOW1
SLOW2 = Pin.board.SLOT1_SLOW2
SLOW3 = Pin.board.SLOT1_SLOW3
ADC1_ADDR = 0         # 0b0000
ADC2_THERM_ADDR = 3   # 0b0011
```

**`SLOT2`**
```python
ID = 2
FAST1 = Pin.board.SLOT2_FAST1
FAST2 = Pin.board.SLOT2_FAST2
FAST3 = Pin.board.SLOT2_FAST3
FAST4 = Pin.board.SLOT2_FAST4
SLOW1 = Pin.board.SLOT2_SLOW1
SLOW2 = Pin.board.SLOT2_SLOW2
SLOW3 = Pin.board.SLOT2_SLOW3
ADC1_ADDR = 1         # 0b0001
ADC2_THERM_ADDR = 6   # 0b0110
```

**`SLOT3`**
```python
ID = 3
FAST1 = Pin.board.SLOT3_FAST1
FAST2 = Pin.board.SLOT3_FAST2
FAST3 = Pin.board.SLOT3_FAST3
FAST4 = Pin.board.SLOT3_FAST4
SLOW1 = Pin.board.SLOT3_SLOW1
SLOW2 = Pin.board.SLOT3_SLOW2
SLOW3 = Pin.board.SLOT3_SLOW3
ADC1_ADDR = 4         # 0b0100
ADC2_THERM_ADDR = 2   # 0b0010
```

**`SLOT4`**
```python
ID = 4
FAST1 = Pin.board.SLOT4_FAST1
FAST2 = Pin.board.SLOT4_FAST2
FAST3 = Pin.board.SLOT4_FAST3
FAST4 = Pin.board.SLOT4_FAST4
SLOW1 = Pin.board.SLOT4_SLOW1
SLOW2 = Pin.board.SLOT4_SLOW2
SLOW3 = Pin.board.SLOT4_SLOW3
ADC1_ADDR = 5         # 0b0101
ADC2_THERM_ADDR = 7   # 0b0111
```

**`SLOT5`**
```python
ID = 5
FAST1 = Pin.board.SLOT5_FAST1
FAST2 = Pin.board.SLOT5_FAST2
FAST3 = Pin.board.SLOT5_FAST3
FAST4 = Pin.board.SLOT5_FAST4
SLOW1 = Pin.board.SLOT5_SLOW1
SLOW2 = Pin.board.SLOT5_SLOW2
SLOW3 = Pin.board.SLOT5_SLOW3
ADC1_ADDR = 8         # 0b1000
ADC2_THERM_ADDR = 11  # 0b1011
```

**`SLOT6`**
```python
ID = 6
FAST1 = Pin.board.SLOT6_FAST1
FAST2 = Pin.board.SLOT6_FAST2
FAST3 = Pin.board.SLOT6_FAST3
FAST4 = Pin.board.SLOT6_FAST4
SLOW1 = Pin.board.SLOT6_SLOW1
SLOW2 = Pin.board.SLOT6_SLOW2
SLOW3 = Pin.board.SLOT6_SLOW3
ADC1_ADDR = 9         # 0b1001
ADC2_THERM_ADDR = 10  # 0b1010
```
