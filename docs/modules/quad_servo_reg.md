# Quad Servo Regulated Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Quad Servo Regulated Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
- [Initialising the Module](#initialising-the-module)
- [Using the Module](#using-the-module)
  - [Enabling its Output](#enabling-its-output)
  - [Accessing the Servos](#accessing-the-servos)
    - [More than 16 Servos](#more-than-16-servos)
  - [Onboard Sensors](#onboard-sensors)
- [References](#references)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Functions](#functions)



## Getting Started

To start using a Quad Servo Regulated Module, you first need to import the class from `pimoroni_yukon.modules`.

```python
from pimoroni_yukon.modules import QuadServoRegModule
```

Then create an instance of `QuadServoRegModule`.

```python
module = QuadServoRegModule()
```


## Initialising the Module

As with all Yukon modules, `QuadServoRegModule` must be initialised before it can be used. This is achieved by first registering the module with the `Yukon` class, with the slot it is attached to.

```python
from pimoroni_yukon import SLOT1 as SLOT

# Import and set up Yukon and QuadServoRegModule instances

yukon.register_with_slot(module, SLOT)
```

Then `Yukon` can verify and initialise its modules.

```python
yukon.verify_and_initialise()
```

This checks each slot on the board to see if the modules expected by your program are physically attached to the board. Only if they match will the `QuadServoRegModule` be initialised, giving it access to the GPIO of the slot it is attached to.

Power can now be provided to all modules, by calling.

```python
yukon.enable_main_output()
```

## Using the Module

### Enabling its Output

With the `QuadServoRegModule` powered, its output to the servos can be enabled or disabled by calling `.enable()` or `.disable()`. The state can also be queried by calling `.is_enabled()`.

### Accessing the Servos

The `QuadServoRegModule` class makes use of the [Servo Library](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/servo/README.md).

By default four Servo objects are created and made accessible through the `.servos` list.

For example, to move all the servos to their zero position, the following loop can be run:

```python
for servo in module.servos:
    servo.value(0.0)
```

It is also possible to access the servos individually using the properties `.servo1`, `.servo2`, `.servo3`, and `.servo4`.

Up to four modules, for a total of 16 servos, can be used in this way, provided their PWM pins do not conflict. Refer to the Yukon board pinout for the slots you are using.

#### More than 16 Servos

To drive more than 16 servos, or use slots that would normally have conflicting PWMs, a [ServoCluster](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/servo/README.md#servocluster) object should to be used.

During creation of the `QuadServoRegModule`, instruct it to *not* create servo objects, by providing it with the `init_servos=False` parameter.

```python
module = QuadServoRegModule(init_servos=False)
```

This makes the `.servos` list inaccessible, and instead makes a `.servo_pins` tuple available. These pins can then be passed to a ServoCluster.

```python
# Constants
CLUSTER_PIO = 0
CLUSTER_SM = 0

servos = ServoCluster(CLUSTER_PIO, CLUSTER_SM, pins=module.servo_pins)
```

If you have multiple Quad Servo Modules you wish to use with a single Servo Cluster, then a technique called nested list comprehension can be used to combine all the `.servo_pins` together.

```python
pins = [pin for module in modules for pin in module.servo_pins]
```


### Onboard Sensors

The Quad Servo Regulated module features an onboard thermistor, letting its temperature be monitored. This can be read by calling `.read_temperature()`.

Additionally, the power good status of the onboard regulator can be read by calling `.read_power_good()`. This will be `True` during normal operation, but will switch to `False` under various conditions such as the input voltage dropping below what is needed for the module to achieve a stable output. For details of other conditions, check the [TPS54A24 datasheet](https://www.ti.com/lit/ds/symlink/tps54a24.pdf).


## References

### Constants

```python
NAME = "Quad Servo Regulated"
SERVO_1 = 0
SERVO_2 = 1
SERVO_3 = 2
SERVO_4 = 3
NUM_SERVOS = 4
TEMPERATURE_THRESHOLD = 70.0
```

### Variables
```python
halt_on_not_pgood: bool

# If init_servos was True
servos: list[Servo]

# If init_servos was False
servo_pins: tuple[Pin, Pin, Pin, Pin]
```

### Functions

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3: bool) -> bool

# Initialisation
QuadServoRegModule(init_servos: bool=True,halt_on_not_pgood: bool=False)
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
reset() -> None

# Power Control
enable() -> None
disable() -> None
is_enabled() -> bool

# Access (only usable if init_servos was True)
@property
servo1 -> Servo
@property
servo2 -> Servo
@property
servo3 -> Servo
@property
servo4 -> Servo

# Sensing
read_power_good() -> bool
read_temperature() -> float

# Monitoring
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```