### Big Motor Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Big Motor + Encoder Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
- [Initialising the Module](#initialising-the-module)
- [Using the Module](#using-the-module)
  - [Enabling its Driver](#enabling-its-driver)
  - [Accessing the Motor](#accessing-the-motor)
    - [More than 4 Big Motors](#more-than-4-big-motors)
  - [Accessing the Encoder](#accessing-the-encoder)
    - [Direct GPIO Access](#direct-gpio-access)
  - [Onboard Sensors](#onboard-sensors)
- [References](#references)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Methods](#methods)


## Getting Started

To start using a Big Motor + Encoder Module, you first need to import the class from `pimoroni_yukon.modules`.

```python
from pimoroni_yukon.modules import BigMotorModule
```

Then create an instance of `BigMotorModule`, giving it the frequency to drive the motor at, which PIO and State Machine (SM) to use for the encoder, and how many counts the encoder will produce per revolution of the motor shaft.

```python
# Constants
FREQUENCY = 25000
ENCODER_PIO = 0
ENCODER_SM = 0
COUNTS_PER_REV = 12

module = BigMotorModule(FREQUENCY,
                        ENCODER_PIO,
                        ENCODER_SM,
                        COUNTS_PER_REV)
```

:warning: **Be sure to choose a PIO and State Machine that does not conflict with any others you have already set up.**


## Initialising the Module

As with all Yukon modules, `BigMotorModule` must be initialised before it can be used. This is achieved by first registering the module with the `Yukon` class, with the slot it is attached to.

```python
from pimoroni_yukon import SLOT1 as SLOT

# Import and set up Yukon and BigMotorModule instances

yukon.register_with_slot(module, SLOT)
```

Then `Yukon` can verify and initialise its modules.

```python
yukon.verify_and_initialise()
```

This checks each slot on the board to see if the modules expected by your program are physically attached to the board. Only if they match will the `BigMotorModule` be initialised, giving it access to the GPIO of the slot it is attached to.

Power can now be provided to all modules, by calling.

```python
yukon.enable_main_output()
```

## Using the Module

### Enabling its Driver

With the `BigMotorModule` powered, its motor driver can be enabled or disabled by calling `.enable()` or `.disable()`. The state can also be queried by calling `.is_enabled()`.

### Accessing the Motor

The `BigMotorModule` class makes use of the [Motor Library](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/motor/README.md).

By default a single Motor object is created and made accessible through the `.motor` variable.

For example, to move the motor at half its speed, the following line of code can be run:

```python
module.motor.speed(0.5)
```

Up to four modules, for a total of 4 big motors, can be used in this way, provided their PWM pins do not conflict. Refer to the Yukon board pinout for the slots you are using.


#### More than 4 Big Motors

To drive more than 4 big motors, or use slots that would normally have conflicting PWMs, a [MotorCluster](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/motor/README.md#motorcluster) object should to be used.

During creation of the `BigMotorModule`, instruct it to *not* create the motor object, by providing it with the `init_motor=False` parameter.

```python
module = BigMotorModule(init_motor=False)
```

This makes the `.motor` variable inaccessible, and instead makes a `.motor_pins` tuple available. These pins can then be passed to a MotorCluster.

```python
# Constants
CLUSTER_PIO = 0
CLUSTER_SM = 0

motors = MotorCluster(CLUSTER_PIO, CLUSTER_SM, pins=module.motor_pins)
```

:warning: **Be sure to choose a PIO and State Machine that does not conflict with any others you have already set up.**

If you have multiple Big Motor + Encoder Modules you wish to use with a single Motor Cluster, then a technique called list comprehension can be used to combine all the `.motor_pins` together.

```python
pins = [module.motor_pins for module in modules]
```


### Accessing the Encoder

The `BigMotorModule` class makes use of the [Encoder Library](https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/encoder/README.md).

By default a single Encoder object is created and made accessible through the `.encoder` variable.

For example, to read the current angle of the encoder, the following line of code can be run:

```python
angle = module.encoder.degrees()
```

#### Direct GPIO Access

If your project does not need an encoder, then the pins on Big Motor + Encoder Module can be made available as GPIO. During creation of the `BigMotorModule`, instruct it to *not* create the encoder object, by providing it with the `init_encoder=False` parameter. Other encoder specific parameters, such as the PIO and SM, can also be omitted.

```python
module = BigMotorModule(init_encoder=False)
```

This makes the `.encoder` variable inaccessible, and instead makes an `.encoder_pins` tuple available. These pins can then be passed to a MotorCluster.


### Onboard Sensors

The Big Motor + Encoder module's motor driver features a current output, letting its draw be monitored. This can be read by calling `.read_current()`.

There is also an onboard thermistor, letting its temperature be monitored. This can be read by calling `.read_temperature()`.

Additionally, the fault state of the motor driver can be read by calling `.read_fault()`. This will be `False` during normal operation, but will switch to `True` under various conditions. For details of these conditions, check the [DRV8706H datasheet](https://www.ti.com/lit/ds/symlink/drv8706-q1.pdf).


## References

### Constants

```python
NAME = "Big Motor + Encoder"
NUM_MOTORS = 1
DEFAULT_FREQUENCY = 25000
DEFAULT_COUNTS_PER_REV = MMME_CPR   # 12
TEMPERATURE_THRESHOLD = 50.0
CURRENT_THRESHOLD = 25.0
SHUNT_RESISTOR = 0.001
GAIN = 80
```

### Variables

```python
# If init_motor was True
motor: Motor

# If init_motor was False
motor_pins: tuple[Pin, Pin]

# If init_encoder was True
encoder: Encoder

# If init_encoder was False
encoder_pins: tuple[Pin, Pin]
```

### Methods

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3: bool) -> bool

# Initialisation
BigMotorModule(frequency: float=DEFAULT_FREQUENCY, 
               encoder_pio: int=0,
               encoder_sm: int=0,
               counts_per_rev: float=DEFAULT_COUNTS_PER_REV,
               init_motor: bool=True,
               init_encoder: bool=True)
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
reset() -> None

# Power Control
enable() -> None
disable() -> None
is_enabled() -> bool

# Sensing
read_fault() -> bool
read_current(samples: int=1) -> float
read_temperature(samples: int=1) -> float

# Monitoring
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None
```
