# Serial Bus Servo Module - Micropython Examples <!-- omit in toc -->

<img src="https://shop.pimoroni.com/cdn/shop/files/yukon-serial-servo_1500x1500_crop_center.jpg" width="500">

These are the micropython examples for the [Serial Servo Module for Yukon](https://shop.pimoroni.com/products/serial-servo-module-for-yukon).

- [Examples](#examples)
  - [Detect Servo](#detect-servo)
  - [Move Servo](#move-servo)
  - [Drive Servo](#drive-servo)
  - [All Servos](#all-servos)
  - [Calibrate Servo](#calibrate-servo)


## Examples

### Detect Servo
[detect_servo.py](detect_servo.py)

Detect any servos that are attached to a Serial Bus Servo module connected to Slot1.


### Move Servo
[move_servo.py](move_servo.py)

Move a serial servo between two angles with Yukon's onboard buttons.
This uses a Serial Bus Servo module connected to Slot1.


### Drive Servo
[drive_servo.py](drive_servo.py)

Drive a serial servo continuously (aka wheel mode) at a speed with Yukon's onboard buttons.
This uses a Serial Bus Servo module connected to Slot1.


### All Servos
[all_servos.py](all_servos.py)

Move a set of serial servos attached to a set of Serial Bus Servo modules connected to Slots.
A wave pattern will be played on the attached servos.


### Calibrate Servo
[calibrate_servo.py](calibrate_servo.py)

Calibrate a serial servo's angle offset with Yukon's onboard buttons.
This uses a Serial Bus Servo module connected to Slot1.
