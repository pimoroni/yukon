# LX Servo Class - Library Reference <!-- omit in toc -->

This is the library reference for the `LXServo` class used to drive [LX-16A](https://pimoroni.com/yukon) servos with Pimoroni Yukon's [Serial Bus Servo Module](https://pimoroni.com/yukon).

- [References](#references)
  - [Constants](#constants)
  - [Functions](#functions)


## References

### Constants

```python
SERVO_MODE = 0
MOTOR_MODE = 1
DEFAULT_READ_TIMEOUT = 1.0

OVER_TEMPERATURE = 0b001
OVER_VOLTAGE = 0b010
OVER_LOADED = 0b100
```


### Functions

```python
# Initialisation
LXServo(id: int,
        uart: UART,
        duplexer: Duplexer,
        timeout: float=DEFAULT_READ_TIMEOUT,
        debug_pin: Pin=None)

# Identification
@property
id -> int

@staticmethod
detect(id: int, uart: UART, duplexer: Duplexer, timeout: float=DEFAULT_READ_TIMEOUT) -> bool

verify_id() -> None
change_id(new_id: int) -> None

# Power Control
enable() -> None
disable() -> None
is_enabled() -> bool

# Movement Control
mode() -> int
move_to(angle: float, duration: float) -> None
queue_move(angle: float, duration: float) -> None
start_queued() -> None
drive_at(speed: float) -> None
last_move() -> tuple[float, float]
last_speed() -> float
stop() -> None

# LED Control
is_led_on() -> bool
set_led(value: bool) -> None

# Sensing
read_angle() -> float
read_voltage() -> float
read_temperature() -> int

# Angle Settings
angle_offset() -> float
try_angle_offset(offset: float) -> None
save_angle_offset() -> None

# Limit Settings
angle_limits() -> tuple[float, float]
voltage_limits() -> tuple[float, float]
temperature_limit() -> int
set_angle_limits(lower: float, upper: float) -> None
set_voltage_limits(lower: float, upper: float) -> None
set_temperature_limit(limit: int) -> None

# Fault Settings
fault_config() -> int
configure_faults(conditions: int) -> None
```

```python
LXServoBroadcaster(uart: UART,
                   duplexer: Duplexer,
                   timeout: float=DEFAULT_READ_TIMEOUT,
                   debug_pin: Pin=None)

# Power Control
enable_all() -> None
disable_all() -> None

# Movement Control
move_all_to(angle: float, duration: float) -> None
queue_move_all(angle: float, duration: float) -> None
start_all_queued() -> None
drive_all_at(speed: float) -> None
stop_all() -> None

# LED Control
set_all_leds(value: bool) -> None

# Sensing
read_angle() -> float
read_voltage() -> float
read_temperature() -> int

# Angle Settings
angle_offset() -> float
try_angle_offset(offset: float) -> None
save_angle_offset() -> None

# Limit Settings
set_all_angle_limits(lower: float, upper: float) -> None
set_all_voltage_limits(lower: float, upper: float) -> None
set_all_temperature_limits(limit: int) -> None

# Fault Settings
configure_all_faults(conditions: int) -> None
```
