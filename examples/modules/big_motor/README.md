# Big Motor Module - Micropython Examples <!-- omit in toc -->

These are the micropython examples for the [Big Motor + Encoder Module for Yukon](https://pimoroni.com/yukon).

- [Examples](#examples)
  - [Single Motor](#single-motor)
  - [Multiple Motors](#multiple-motors)
  - [All Motors (No Encoders)](#all-motors-no-encoders)
  - [Position Control](#position-control)
  - [Velocity Control](#velocity-control)
  - [Position on Velocity Control](#position-on-velocity-control)
- [Tuning](#tuning)
  - [Motor Profiler](#motor-profiler)
  - [Position Tuning](#position-tuning)
  - [Velocity Tuning](#velocity-tuning)
  - [Position on Velocity Tuning](#position-on-velocity-tuning)


## Examples

### Single Motor
[single_motor.py](single_motor.py)

Drive a single motor from a Big Motor + Encoder Module connected to Slot1.
A wave pattern will be played on the attached motor, and its speed printed out.


### Multiple Motors
[multiple_motors.py](multiple_motors.py)

Drive up to 4 motors from a set of Big Motor + Encoder Modules connected to Slots.
A wave pattern will be played on the attached motors, and their speeds printed out.


### All Motors (No Encoders)
[all_motors_no_encoders.py](all_motors_no_encoders.py)

Drive up to 6 motors from a set of Big Motor + Encoder Modules connected to Slots, using a MotorCluster.
A wave pattern will be played on the attached motors.


### Position Control
[position_control.py](position_control.py)

Drive a motor smoothly between random positions, with the help of it's attached encoder and PID control.
This uses a Big Motor + Encoder Module connected to Slot1.


### Velocity Control
[velocity_control.py](velocity_control.py)

Drive a motor smoothly between random speeds, with the help of it's attached encoder and PID control.
This uses a Big Motor + Encoder Module connected to Slot1.

### Position on Velocity Control
[position_on_velocity_control.py](position_on_velocity_control.py)

Drive a motor smoothly between random positions, with velocity limits, with the help of it's attached encoder and PID control.
This uses a Big Motor + Encoder Module connected to Slot1.


## Tuning

### Motor Profiler
[tuning/motor_profiler.py](tuning/motor_profiler.py)

Profile the speed of a motor across its PWM duty cycle range using its attached encoder for feedback.
This uses a Big Motor + Encoder Module connected to Slot1.


### Position Tuning
[tuning/position_tuning.py](tuning/position_tuning.py)

A program to aid in the discovery and tuning of motor PID values for position control.
It does this by commanding the motor to move repeatedly between two setpoint angles and
plots the measured response. This uses a Big Motor + Encoder Module connected to Slot1.


### Velocity Tuning
[tuning/velocity_tuning.py](tuning/velocity_tuning.py)

A program to aid in the discovery and tuning of motor PID values for velocity control.
It does this by commanding the motor to drive repeatedly between two setpoint speeds and
plots the measured response. This uses a Big Motor + Encoder Module connected to Slot1.

### Position on Velocity Tuning
[tuning/position_on_velocity_tuning.py](tuning/position_on_velocity_tuning.py)

A program to aid in the discovery and tuning of motor PID values for position on velocity control.
It does this by commanding the motor to move repeatedly between two setpoint angles and plots
the measured response. This uses a Big Motor + Encoder Module connected to Slot1.
