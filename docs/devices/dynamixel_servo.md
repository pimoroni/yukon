# Dynamixel Servo Class - Library Reference <!-- omit in toc -->

This is the library reference for the `AXServo` class used to drive Dynamixel AX-series servos (for example, AX-12W) with Pimoroni Yukon's [Serial Bus Servo Module](https://pimoroni.com/yukon).

- [Reference](#reference)
  - [Constants](#constants)
  - [Functions](#functions)

## Reference

### Constants

```python
BAUD_RATE = 1000000
SERVO_MODE = 0
MOTOR_MODE = 1
DEFAULT_READ_TIMEOUT = 50.0
```

### Functions

```python
# Initialisation
AXServo(id: int, uart, duplexer, timeout: float=AXServo.DEFAULT_READ_TIMEOUT, debug_pin=None)

# Identification
id -> int

@staticmethod
detect(id: int, uart, duplexer, timeout: float=AXServo.DEFAULT_READ_TIMEOUT) -> bool

verify_id() -> None
change_id(new_id: int) -> None

# Power Control
enable() -> None
disable() -> None
is_enabled() -> int

# Movement Control
mode() -> int
move_to(angle: float, deg_per_sec: float) -> None
queue_move(angle: float, deg_per_sec: float) -> None
start_queued() -> None
drive_at(speed: float) -> None
last_move() -> tuple[float, float]
last_speed() -> float
stop() -> None

# LED Control
is_led_on() -> int
set_led(value: int) -> None

# Sensing
read_angle() -> float
read_voltage() -> float
read_temperature() -> int

# Limit Settings
angle_limits() -> tuple[float, float]
voltage_limits() -> tuple[float, float]
temperature_limit() -> int
torque_limit() -> int
punch() -> int
set_angle_limits(lower_degrees: float, upper_degrees: float) -> None
set_voltage_limits(low_v: float, high_v: float) -> None
set_temperature_limit(limit: int) -> None
set_torque_limit(torque_limit: int) -> None
set_punch(punch: int) -> None

# Fault Settings
fault_config() -> tuple[int, int]
configure_faults(led_bits: int=None, shutdown_bits: int=None) -> None


```

```python
AXServoBroadcaster(uart: UART,
                   duplexer: Duplexer,
                   timeout: float=DEFAULT_READ_TIMEOUT,
                   debug_pin: Pin=None)

# Power Control
enable_all() -> None
disable_all() -> None

# Movement Control
move_all_to(angle: float, deg_per_sec: float) -> None
queue_move_all(angle: float, deg_per_sec: float) -> None
start_all_queued() -> None
drive_all_at(speed: float) -> None

# LED Control
set_all_leds(value: int) -> None

# Limit Settings
set_all_angle_limits(lower: float, upper: float) -> None
set_all_voltage_limits(lower: float, upper: float) -> None
set_all_temperature_limits(limit: int) -> None
set_all_torque_limit(torque_limit: int) -> None
set_all_punch(punch: int) -> None

# Fault Settings
configure_all_faults(led_bits: int, shutdown_bits: int) -> None
```

#### Notes

- `AXServo.detect()` checks whether a servo with the specified ID is present on the bus.
- `move_to()` and `queue_move()` operate in servo mode, while `drive_at()` operates in motor mode.
- `angle_limits()` returns `(-150.0, -150.0)` when the servo is in motor mode.
- Broadcasting operations are limited; some reads and actions are not allowed when using `AXServo.BROADCAST_ID`.
