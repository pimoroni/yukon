# Quad Servo Direct Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Quad Servo Direct Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
- [Initialising the Module](#initialising-the-module)
- [Using the Module](#using-the-module)
  - [Accessing the Servos](#accessing-the-servos)
    - [More than 16 Servos](#more-than-16-servos)
  - [External Sensors](#external-sensors)
- [References](#references)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Functions](#functions)


## Getting Started

To start using a Quad Servo Direct Module, you first need to import the class from `pimoroni_yukon.modules`.

```python
from pimoroni_yukon.modules import QuadServoDirectModule
```

Then create an instance of `QuadServoDirectModule`.

```python
module = QuadServoDirectModule()
```


## Initialising the Module

As with all Yukon modules, `QuadServoDirectModule` must be initialised before it can be used. This is achieved by first registering the module with the `Yukon` class, with the slot it is attached to.

```python
from pimoroni_yukon import SLOT1 as SLOT

# Import and set up Yukon and QuadServoDirectModule instances

yukon.register_with_slot(module, SLOT)
```

Then `Yukon` can verify and initialise its modules.

```python
yukon.verify_and_initialise()
```

This checks each slot on the board to see if the modules expected by your program are physically attached to the board. Only if they match will the `QuadServoDirectModule` be initialised, giving it access to the GPIO of the slot it is attached to.

Power can now be provided to all modules, by calling.

```python
yukon.enable_main_output()
```

## Using the Module

### Accessing the Servos

The `QuadServoDirectModule` class makes use of the [Servo Library](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/servo/README.md).

By default four Servo objects are created and made assessible through the `.servos` list.

For example, to move all the servos to their zero position, the following loop can be run:

```python
for servo in module.servos:
    servo.value(0.0)
```

Up to four modules, for a total of 16 servos, can be used in this way, provided their PWM pins do not conflict. Refer to the Yukon board pinout for the slots you are using.

#### More than 16 Servos

To drive more than 16 servos, or use slots that would normally have conflicting PWMs, a [ServoCluster](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/servo/README.md#servocluster) object should to be used.

During creation of the `QuadServoDirectModule`, instruct it to *not* create servo objects, by providing it with the `init_servos=False` parameter.

```python
module = QuadServoDirectModule(init_servos=False)
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


### External Sensors

The Quad Servo Direct module supports connecting two external 3.3V sensors via an unpopulated header. These can be read by calling `.read_adc1()` and `.read_adc2()`.

There is also an optional `samples` parameter that lets multiple readings be taken in quick succession to produce a more accurate reading.


## References

### Constants

```python
NAME = "Quad Servo Direct"
NUM_SERVOS = 4
```

### Variables
```python
# If init_servos was True
servos: list[Servo]

# If init_servos was False
servo_pins: tuple[Pin, Pin, Pin, Pin]
```

### Functions

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3:bool) -> bool

# Initialisation
QuadServoDirect(init_servos: bool=True)
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
reset() -> None

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
read_adc1(samples: int=1) -> float
read_adc2(samples: int=1) -> float
```
