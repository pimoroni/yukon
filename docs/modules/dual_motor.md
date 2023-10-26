# Dual Motor / Bipolar Stepper Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Dual Motor / Bipolar Stepper Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
  - [Motor Types](#motor-types)
- [Initialising the Module](#initialising-the-module)
- [Using the Module](#using-the-module)
  - [Enabling its Driver](#enabling-its-driver)
  - [Current Limiting](#current-limiting)
  - [Accessing the DC Motors](#accessing-the-dc-motors)
    - [More than 8 Motors](#more-than-8-motors)
  - [Accessing the Stepper Motor](#accessing-the-stepper-motor)
  - [Onboard Sensors](#onboard-sensors)
- [References](#references)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Functions](#functions)


## Getting Started

To start using a Dual Motor / Bipolar Stepper Module, you first need to import the class from `pimoroni_yukon.modules`.

```python
from pimoroni_yukon.modules import DualMotorModule
```

Then create an instance of `DualMotorModule`, giving it the type of motors to be driven and the frequency to drive them at.

```python
# Constants
MOTOR_TYPE = DualMotorModule.DUAL
FREQUENCY = 25000

module = DualMotorModule(MOTOR_TYPE,
                         FREQUENCY)
```

### Motor Types

The `DualMotorModule` can drive both 2x brushed DC motors, or 1x bipolar stepper motor. The type of motor driven can be chosen using the following constants:

* `DualMotorModule.DUAL` = `0`
* `DualMotorModule.STEPPER` = `1`

:warning: Stepper motor support is currently not implemented in the Yukon library. This will be added in the near future.


## Initialising the Module

As with all Yukon modules, `DualMotorModule` must be initialised before it can be used. This is achieved by first registering the module with the `Yukon` class, with the slot it is attached to.

```python
from pimoroni_yukon import SLOT1 as SLOT

# Import and set up Yukon and DualMotorModule instances

yukon.register_with_slot(module, SLOT)
```

Then `Yukon` can verify and initialise its modules.

```python
yukon.verify_and_initialise()
```

This checks each slot on the board to see if the modules expected by your program are physically attached to the board. Only if they match will the `DualMotorModule` be initialised, giving it access to the GPIO of the slot it is attached to.

Power can now be provided to all modules, by calling.

```python
yukon.enable_main_output()
```

## Using the Module

### Enabling its Driver

With the `DualMotorModule` powered, its motor driver can be enabled or disabled by calling `.enable()` or `.disable()`. The state can also be queried by calling `.is_enabled()`.


### Current Limiting

The `DualMotorModule` features adjustable current limiting, with 9 levels from 0.161A to 2.236A per channel.

To set a current limit call `.set_current_limit(amps)`, and provide it with the `amps` you want to limit to. The nearest of the 9 levels less than the provided value will be selected, with the exception of the lowest 0.161A level, which will be chosen for any values less than it too.

Once a new limit is set, its value can be read back by calling `.current_limit()`. This will be the value of the level actually selected, rather than the `amps` initially provided.

:information_source: The current limit can only be set when the `DualMotorModule` is disabled (the main output can still be enabled). If you wish to have variable current control during operation, such as to regulate stepper motor current based on step rate, it is recommended to adjust the duty cycle of the PWM signals sent.


### Accessing the DC Motors

The `DualMotorModule` class makes use of the [Motor Library](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/motor/README.md) for its DC motor control.

By default two Motor objects are created and made accessible through the `.motors` list.

For example, to move the motor at half its speed, the following line of code can be run:

```python
for motor in module.motors:
    motor.speed(0.5)
```

It is also possible to access the motors individually using the properties `.motor1`, and `.motor2`.

Up to four modules, for a total of 8 DC motors, can be used in this way, provided their PWM pins do not conflict. Refer to the [Yukon Pinout Diagram](../yukon_pinout_diagram.png) for the slots you are using.


#### More than 8 Motors

To drive more than 8 motors, or use slots that would normally have conflicting PWMs, a [MotorCluster](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/motor/README.md#motorcluster) object should to be used.

During creation of the `DualMotorModule`, instruct it to *not* create motor objects, by providing it with the `init_motors=False` parameter.

```python
module = DualMotorModule(init_motors=False)
```

This makes the `.motors` list inaccessible, and instead makes a `.motor_pins` list of tuples available. These pins can then be passed to a MotorCluster.

```python
# Constants
CLUSTER_PIO = 0
CLUSTER_SM = 0

motors = MotorCluster(CLUSTER_PIO, CLUSTER_SM, pins=module.motor_pins)
```

:warning: **Be sure to choose a PIO and State Machine that does not conflict with any others you have already set up.**

If you have multiple Dual Motor Modules you wish to use with a single Motor Cluster, then a technique called nested list comprehension can be used to combine all the `.motor_pins` together.

```python
pins = [pin for module in modules for pin in module.motor_pins]
```


### Accessing the Stepper Motor

Currently the Yukon library does not support stepper motors. For now it is recommended to make use of a 3rd-party Micropython library, and follow the instructions from the [More than 8 Motors](#more-than-8-motors) section above to get direct access to the GPIO pins that control the motor driver.


### Onboard Sensors

The Dual Motor / Bipolar Stepper module features an onboard thermistor, letting its temperature be monitored. This can be read by calling `.read_temperature()`.

Additionally, the fault state of the motor driver can be read by calling `.read_fault()`. This will be `False` during normal operation, but will switch to `True` under various conditions. For details of these conditions, check the [DRV8424P datasheet](https://www.ti.com/lit/ds/symlink/drv8424e.pdf).

## References

### Constants
```python
NAME = "Dual Motor"
DUAL = 0
STEPPER = 1
NUM_MOTORS = 2
MOTOR_1 = 0       # Only for DUAL motor_type
MOTOR_2 = 1       # Only for DUAL motor_type
NUM_STEPPERS = 1
FAULT_THRESHOLD = 0.1
DEFAULT_FREQUENCY = 25000
DEFAULT_CURRENT_LIMIT = CURRENT_LIMIT_3
TEMPERATURE_THRESHOLD = 50.0
```

### Variables

```python
# If motor_type is DUAL and init_motors was True
motors: list[Motor]

# If init_motors was False
motor_pins: tuple[tuple[Pin, Pin], tuple[Pin, Pin]]
```

### Functions

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3: bool) -> bool

# Initialisation
DualMotorModule(motor_type: int=DUAL,
                frequency: float=DEFAULT_FREQUENCY,
                current_limit: float=DEFAULT_CURRENT_LIMIT,
                init_motors: bool=True)
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
reset() -> None

# Power Control
enable() -> None
disable() -> None
is_enabled() -> bool

# Current Control
current_limit() -> float
set_current_limit(amps: float) -> None

# Access (only usable if motor_type is DUAL and init_motors was True)
@property
motor1 -> Motor
@property
motor2 -> Motor

# Sensing
read_fault() -> bool
read_temperature(samples: int=1) -> float

# Monitoring
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```
