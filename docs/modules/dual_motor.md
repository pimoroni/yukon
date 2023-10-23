# Dual Motor / Bipolar Stepper Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Dual Motor / Bipolar Stepper Module for Yukon](https://pimoroni.com/yukon).

- [Constants](#constants)
- [Variables](#variables)
- [Functions](#functions)


### Constants
```python
NAME = "Dual Motor"
DUAL = 0
STEPPER = 1
NUM_MOTORS = 2
NUM_STEPPERS = 1
FAULT_THRESHOLD = 0.1
DEFAULT_FREQUENCY = 25000
DEFAULT_CURRENT_LIMIT = CURRENT_LIMIT_3
TEMPERATURE_THRESHOLD = 50.0
```

### Variables

```python
# If init_motors was True
motors: list[Motor]

# If init_motors was False
motor_pins: tuple[tuple[Pin, Pin], tuple[Pin, Pin]]
```

### Functions

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3:bool) -> bool

# Initialisation
DualMotorModule(motor_type: int=DUAL,
                frequency: float=DEFAULT_FREQUENCY,
                current_limit: float=DEFAULT_CURRENT_LIMIT,init_motors: bool=True)
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
reset() -> None

# Power Control
enable() -> None
disable() -> None
is_enabled() -> bool

# Current Control
current_limit() -> float
set_current_limit(amps: float) -> None

# Access (only usable if init_motors was True)
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
