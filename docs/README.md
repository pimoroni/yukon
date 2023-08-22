# Inventor HAT Mini - Library Reference <!-- omit in toc -->

This is the library reference for the [Pimoroni Yukon](https://pimoroni.com/yukon), a high-powered modular robotics / engineering platform, powered by the Raspberry Pi RP2040.


## Table of Content <!-- omit in toc -->
- [Getting Started](#getting-started)
- [Reading the User Buttons](#reading-the-user-buttons)
- [Setting the User LEDs](#setting-the-user-leds)
- [Time Delays and Sleeping](#time-delays-and-sleeping)
- [Reading Sensors Directly](#reading-sensors-directly)
- [Function Reference](#function-reference)
  - [Yukon](#yukon)
  - [Yukon Module](#yukon-module)
  - [Audio Amp Module](#audio-amp-module)
  - [Bench Power Module](#bench-power-module)
  - [Big Motor Module](#big-motor-module)
  - [Dual Motor Module](#dual-motor-module)
  - [Dual Switched Module](#dual-switched-module)
  - [LED Strip Module](#led-strip-module)
  - [Quad Servo Direct Module](#quad-servo-direct-module)
  - [Quad Servo Reg Module](#quad-servo-reg-module)
- [Constants Reference](#constants-reference)
  - [Slot Constants](#slot-constants)
  - [Sensor Addresses](#sensor-addresses)


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
state_boot = yukon.is_bool_pressed()
```

In addition to the onboard buttons, it is possible to wire up external **A**, **B** and **Boot/User** buttons, letting you interact with Yukon when inside of an enclosure. These are exposed on the **Expansion** and **CTRL** headers along the top edge of the board, either side of the USB and power inputs.


## Setting the User LEDs

Yukon has two user LEDs along its bottom edge, labelled **A** and **B**. These can be set using the `set_led()` function. To set both LEDs you would write, passing in either `True` or `False`:

```python
yukon.set_led('A', True)
yukon.set_led('B', False)
```


## Time Delays and Sleeping

Yukon features onboard sensors for monitoring voltage, current and temperature, both of the board itself, and its attached modules.

Although it is possible to read these sensors standalone, it is recommended to let the library handle this as part of its range of monitoring functions. These are:

* `monitored_sleep(seconds)` - Repeatedly checks each sensor for a given number of seconds
* `monitored_sleep_ms(ms)` - Repeatedly checks each sensor for a given number of milliseconds
* `monitor_until_ms(end_ms)` - Repeatedly checks each sensor until a given end time has been reached (in milliseconds)
* `monitor_once()` - Checks each sensor once, and summarises the readings
* `monitor()` - The base monitoring function, all the other functions are based on.

:warning: These functions should be used in place of the regular `time.sleep()`. This lets Yukon turn off the main output and raise exceptions in the event of dangerous conditions, protecting your hardware.

The kinds of exceptions raised are: `OverVoltageError`, `UnderVoltageError`, `OverCurrentError`, `OverTemperatureError`, and `FaultError`. These are in addition to any standard python errors that may occur as a result of code running within monitor.

:info: The end time that `monitor_until_ms()` expects is a value from the `time.ticks_ms()`.

Depending on the logging level set on Yukon, the monitor functions will print out the readings they have accumulated over their operation. For example, the minimum, maximum, and average voltage detected. For heavily populated Yukon boards, this printout can be quite lengthy, so the values shown can be filtered with optional `allowed` and `excluded` parameters. Below is an example of a sleep that will only report the maximum current.

```python
yukon.monitored_sleep(0.01, allowed="C_max")
```

After a monitor function has completed, the values it obtained can be accessed with the `get_readings()` function, which returns an ordered dictionary of key value pairs. The below example shows how the average temperature over the monitoring period can be read.

```python
readings = yukon.GetReadings()
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


| Function | Audio Amp | Bench Power | Big Motor | Dual Motor | Dual Switched | LED Strip | Quad Servo Direct | Quad Servo Reg |
|----------|-----------|-------------|-----------|------------|---------------|-----------|-------------------|----------|
`read_voltage()` | - | Yes | - | - | - | - | - | - |
`read_current()` | - | - | Yes | - | - | - | - | - |
`read_temperature()` | Yes | Yes | Yes | Yes | Yes | Yes | - | Yes |
`read_power_good()` | - | Yes | - | - | Yes | Yes | - | Yes |
`read_fault()` | - | - | Yes | Yes | - | - | - | - |
`read_adc1()` | - | - | - | - | - | - | Yes | - |
`read_adc2()` | - | - | - | - | - | - | Yes | - |


## Function Reference

### Yukon

Here is the complete list of functions available on the `Yukon` class:

```python
Yukon(voltage_limit=17.2, current_limit=20, temperature_limit=90, logging_level=2)
change_logging(logging_level)
find_slots_with_module(module_type)
register_with_slot(module, slot)
deregister_slot(slot)
detect_module(slot)
initialise_modules(allow_unregistered=False, allow_undetected=False, allow_discrepencies=False, allow_no_modules=False)
is_pressed(switch)
is_boot_pressed()
set_led(switch, value)
enable_main_output()
disable_main_output()
is_main_output()
read_voltage()
read_current()
read_temperature()
read_expansion()
read_slot_adc1(slot)
read_slot_adc2(slot)
assign_monitor_action(callback_function)
monitor()
monitored_sleep()
monitored_sleep_ms()
monitor_until_ms()
monitor_once()
get_readings()
process_readings()
clear_readings()
reset()
```

### Yukon Module

```python
YukonModule()
initialise(slot, adc1_func, adc2_func)
is_initialised()
deregister()
configure()
assign_monitor_action(callback_function)
monitor()
get_readings()
process_readings()
clear_readings()
```

### Audio Amp Module

```python
AudioAmpModule()
is_module(adc_level, slow1, slow2, slow3)
initialise(slot, adc1_func, adc2_func)
configure()
enable()
disable()
is_enabled()
exit_soft_shutdown()
set_volume(volume)
read_temperature()
monitor()
get_readings()
process_readings()
clear_readings()
write_i2c_reg(register, data)
read_i2c_reg(register)
detect_i2c()
```

### Bench Power Module

```python
BenchPowerModule(halt_on_not_pgood=False)
is_module(adc_level, slow1, slow2, slow3)
initialise(slot, adc1_func, adc2_func)
configure()
enable()
disable()
is_enabled()
set_target_voltage(voltage)
set_target(percent)
read_voltage()
read_power_good()
read_temperature()
monitor()
get_readings()
process_readings()
clear_readings()
```

### Big Motor Module

```python
BigMotorModule(frequency)
is_module(adc_level, slow1, slow2, slow3)
initialise(slot, adc1_func, adc2_func)
configure()
enable()
disable()
is_enabled()
read_fault()
read_current()
read_temperature()
monitor()
get_readings()
process_readings()
clear_readings()
```

### Dual Motor Module

```python
DualMotorModule(motor_type, frequency)
is_module(adc_level, slow1, slow2, slow3)
initialise(slot, adc1_func, adc2_func)
configure()
enable()
disable()
is_enabled()
decay()
decay(value)
toff()
toff(value)
motor1
motor2
read_fault()
read_temperature()
monitor()
get_readings()
process_readings()
clear_readings()
```

### Dual Switched Module

```python
DualSwitchedModule(halt_on_not_pgood=False)
is_module(adc_level, slow1, slow2, slow3)
initialise(slot, adc1_func, adc2_func)
configure()
enable()
disable()
is_enabled()
output(switch, value)
read_output(switch)
read_power_good(switch)
read_temperature()
monitor()
get_readings()
process_readings()
clear_readings()
```

### LED Strip Module

```python
LEDStripModule(strip_type, num_pixels, brightness=1.0, halt_on_not_pgood=False)
is_module(adc_level, slow1, slow2, slow3)
initialise(slot, adc1_func, adc2_func)
configure()
count()
enable()
disable()
is_enabled()
read_power_good()
read_temperature()
monitor()
get_readings()
process_readings()
clear_readings()
```

### Quad Servo Direct Module

```python
QuadServoDirect()
is_module(adc_level, slow1, slow2, slow3)
initialise(slot, adc1_func, adc2_func)
configure()
servo1
servo2
servo3
servo4
read_adc1()
read-adc2()
```

### Quad Servo Reg Module

```python
QuadServoRegModule(halt_on_not_pgood=False)
is_module(adc_level, slow1, slow2, slow3)
initialise(slot, adc1_func, adc2_func)
configure()
enable()
disable()
is_enabled()
servo1
servo2
servo3
servo4
read_power_good()
read_temperature()
monitor()
get_readings()
process_readings()
clear_readings()
```



## Constants Reference

Here is the complete list of constants on the `yukon` module:

### Slot Constants

These constants represent each of the 6 slots on Yukon. They are a namedtuple containing the ID of the slot and which pins that slot is associated with.

**`SLOT1`**
* `ID` = `1`
* `FAST1` = `Pin.board.SLOT1_FAST1`
* `FAST2` = `Pin.board.SLOT1_FAST2`
* `FAST3` = `Pin.board.SLOT1_FAST3`
* `FAST4` = `Pin.board.SLOT1_FAST4`
* `SLOW1` = `Pin.board.SLOT1_SLOW1`
* `SLOW2` = `Pin.board.SLOT1_SLOW2`
* `SLOW3` = `Pin.board.SLOT1_SLOW3`
* `ADC1-ADDR` = `0`  # 0b0000
* `ADC2_TEMP_ADDR` = `3`  # 0b0011

**`SLOT2`**
* `ID` = `2`
* `FAST1` = `Pin.board.SLOT2_FAST1`
* `FAST2` = `Pin.board.SLOT2_FAST2`
* `FAST3` = `Pin.board.SLOT2_FAST3`
* `FAST4` = `Pin.board.SLOT2_FAST4`
* `SLOW1` = `Pin.board.SLOT2_SLOW1`
* `SLOW2` = `Pin.board.SLOT2_SLOW2`
* `SLOW3` = `Pin.board.SLOT2_SLOW3`
* `ADC1-ADDR` = `1`  # 0b0001
* `ADC2_TEMP_ADDR` = `6`  # 0b0110

**`SLOT3`**
* `ID` = `3`
* `FAST1` = `Pin.board.SLOT3_FAST1`
* `FAST2` = `Pin.board.SLOT3_FAST2`
* `FAST3` = `Pin.board.SLOT3_FAST3`
* `FAST4` = `Pin.board.SLOT3_FAST4`
* `SLOW1` = `Pin.board.SLOT3_SLOW1`
* `SLOW2` = `Pin.board.SLOT3_SLOW2`
* `SLOW3` = `Pin.board.SLOT3_SLOW3`
* `ADC1-ADDR` = `4`  # 0b0100
* `ADC2_TEMP_ADDR` = `2`  # 0b0010

**`SLOT4`**
* `ID` = `4`
* `FAST1` = `Pin.board.SLOT4_FAST1`
* `FAST2` = `Pin.board.SLOT4_FAST2`
* `FAST3` = `Pin.board.SLOT4_FAST3`
* `FAST4` = `Pin.board.SLOT4_FAST4`
* `SLOW1` = `Pin.board.SLOT4_SLOW1`
* `SLOW2` = `Pin.board.SLOT4_SLOW2`
* `SLOW3` = `Pin.board.SLOT4_SLOW3`
* `ADC1-ADDR` = `5`  # 0b0101
* `ADC2_TEMP_ADDR` = `7`  # 0b0111

**`SLOT5`**
* `ID` = `5`
* `FAST1` = `Pin.board.SLOT5_FAST1`
* `FAST2` = `Pin.board.SLOT5_FAST2`
* `FAST3` = `Pin.board.SLOT5_FAST3`
* `FAST4` = `Pin.board.SLOT5_FAST4`
* `SLOW1` = `Pin.board.SLOT5_SLOW1`
* `SLOW2` = `Pin.board.SLOT5_SLOW2`
* `SLOW3` = `Pin.board.SLOT5_SLOW3`
* `ADC1-ADDR` = `8`  # 0b1000
* `ADC2_TEMP_ADDR` = `11` # 0b1011

**`SLOT6`**
* `ID` = `6`
* `FAST1` = `Pin.board.SLOT6_FAST1`
* `FAST2` = `Pin.board.SLOT6_FAST2`
* `FAST3` = `Pin.board.SLOT6_FAST3`
* `FAST4` = `Pin.board.SLOT6_FAST4`
* `SLOW1` = `Pin.board.SLOT6_SLOW1`
* `SLOW2` = `Pin.board.SLOT6_SLOW2`
* `SLOW3` = `Pin.board.SLOT6_SLOW3`
* `ADC1-ADDR` = `9`  # 0b1001
* `ADC2_TEMP_ADDR` = `10` # 0b1010


### Sensor Addresses

* `CURRENT_SENSE_ADDR` = `12` # 0b1100
* `TEMP_SENSE_ADDR` = `13`    # 0b1101
* `VOLTAGE_SENSE_ADDR` = `14` # 0b1110
* `EX_ADC_ADDR` = `15`        # 0b1111
