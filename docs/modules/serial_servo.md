# Serial Bus Servo Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Serial Bus Servo Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
- [Initialising the Module](#initialising-the-module)
- [Using the Module](#using-the-module)
  - [Accessing the Serial Bus](#accessing-the-serial-bus)
  - [Initialising a Serial Servo](#initialising-a-serial-servo)
  - [Controlling a Serial Servo](#controlling-a-serial-servo)
- [Restrictions](#restrictions)
- [References](#references)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Functions](#functions)


## Getting Started

To start using a Serial Servo Module, you first need to import the class from `pimoroni_yukon.modules`.

```python
from pimoroni_yukon.modules import SerialServoModule
```

Then create an instance of `SerialServoModule`.

```python
module = SerialServoModule()
```


## Initialising the Module

As with all Yukon modules, `SerialServoModule` must be initialised before it can be used. This is achieved by first registering the module with the `Yukon` class, with the slot it is attached to.

```python
from pimoroni_yukon import SLOT1 as SLOT

# Import and set up Yukon and SerialServoModule instances

yukon.register_with_slot(module, SLOT)
```

Then `Yukon` can verify and initialise its modules.

```python
yukon.verify_and_initialise()
```

This checks each slot on the board to see if the modules expected by your program are physically attached to the board. Only if they match will the `SerialServoModule` be initialised, giving it access to the GPIO of the slot it is attached to.

Power can now be provided to all modules, by calling.

```python
yukon.enable_main_output()
```


## Using the Module

### Accessing the Serial Bus

The `SerialServoModule` class uses MicroPython's native [UART class](https://docs.micropython.org/en/latest/library/machine.UART.html) for its communication with serial bus servos. A single UART object is created and made accessible through the `.uart` variable.

To control whether TX or RX is connected to the common Data line of serial bus servos, the Yukon library includes a `Duplexer` class. This is created automatically by the `SerialServoModule` and can be accessed by calling `module.duplexer`.

The `Duplexer` has the following functions available.

```python
Duplexer(tx_to_data: bool, rx_to_data: bool, active_low: bool=False)
reset() -> None
send_on_data() -> None
receive_on_data() -> None
```

### Initialising a Serial Servo

The Yukon library currently supports the LX range of serial bus servos from LewanSoul/HiWonder (tested with the LX-16A and LX-224HV). This is offered via a `LXServo` class.

To use an LX servo with the Serial Bus Servo module, create an instance of it, giving it the ID of the servo you wish to control (from 0 to 254), along with the uart and duplexer from the `SerialServoModule`.

```python
SERVO_ID = 1
servo = LXServo(SERVO_ID, module.uart, module.duplexer)
```

This can only be done after `yukon.verify_and_initialise()`, as the module's `.uart` and `.duplexer` will not be available before then. Additionally, the presence of the servo is checked for during class creation, meaning that the main output should be enabled first and have been given sufficient time for the servo's microcontroller to power up.

```python
yukon.register_with_slot(module, SLOT)
yukon.verify_and_initialise()
yukon.enable_main_output()

yukon.monitored_sleep(1.0)

servo = LXServo(SERVO_ID, module.uart, module.duplexer)
# Create any additional LXServo objects here
```

:information_source: Serial servos from the likes of Robotis, HerkuleX, FeeTech etc, can be supported by implementing similar classes that accept a `UART` and `Duplexer`.


### Controlling a Serial Servo

With a LXServo object created, the easiest way to control it is with the `.move_to(angle, duration)` function. This takes a target angle between -120.0 degrees and + 120.0 degrees, along with the duration in seconds the movement will occur over (up to 30 seconds).

```python
servo.move_to(45, 5)  # Move to 45 degrees in 5 seconds
```

This function is non-blocking meaning your code can go and perform other actions whilst the servo moves. To check if the servo has finished moving, its current angle can be read by calling `.read_angle()`.

LX servos also support a continuous rotation mode. To use this mode, call the `.drive_at(speed)` function. This takes a speed value from -1.0 to 1.0. The servo's angle whilst in this mode can still be read, and will range from -180.0 to +180.0 degrees.

To stop an LX servo during a move or whilst driving, call `.stop()`.

For further ways to control LX servos, refer to the [LXServo Library Reference](/docs/devices/lxservo.md)


## Restrictions

:warning: SerialServoModule makes use of a single hardware UART to send data to and receive data from connected serial bus servos. RP2040 only has two hardware UARTs meaning that only two Serial Bus Servo modules may be used simultaneously, and the slots they are attached to must not use the same UART. Refer to the [Yukon Pinout Diagram](../yukon_pinout_diagram.png) for the slots you are using, and relocate your modules if there is a conflict.


## References

### Constants

```python
NAME = "Seria Bus Servo"
DEFAULT_BAUDRATE = 115200
```


### Variables

```python
uart: UART
duplexer: Duplexer
```


### Functions

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3: bool) -> bool

# Initialisation
SerialServoModule(baudrate: int=DEFAULT_BAUDRATE)
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
reset() -> None
```
