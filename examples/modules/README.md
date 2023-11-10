# Yukon Micropython Module Examples <!-- omit in toc -->

- [Audio Amp Module](#audio-amp-module)
  - [Tone Song](#tone-song)
  - [Wav Play](#wav-play)
- [Bench Power Module](#bench-power-module)
  - [Single Power](#single-power)
  - [Multiple Powers](#multiple-powers)
  - [Controllable Power](#controllable-power)
- [Big Motor + Encoder Module](#big-motor--encoder-module)
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
- [Dual Motor / Bipolar Stepper Module](#dual-motor--bipolar-stepper-module)
  - [Two Motors](#two-motors)
  - [Multiple Motors](#multiple-motors-1)
  - [All Motors](#all-motors)
  - [Single Stepper](#single-stepper)
- [Dual Switched Output Module](#dual-switched-output-module)
  - [Two Outputs](#two-outputs)
  - [Multiple Outputs](#multiple-outputs)
  - [Actioned Output](#actioned-output)
  - [PWM Output](#pwm-output)
- [LED Strip Module](#led-strip-module)
  - [Single Strip](#single-strip)
  - [Multiple Strips](#multiple-strips)
- [Quad Servo Module](#quad-servo-module)
  - [Four Servos](#four-servos)
  - [Multiple Servos](#multiple-servos)
  - [All Servos](#all-servos)
  - [Servo Feedback](#servo-feedback)
- [Serial Servo Module](#serial-servo-module)
  - [Detect Servo](#detect-servo)
  - [Move Servo](#move-servo)
  - [Drive Servo](#drive-servo)
  - [All Servos](#all-servos-1)
  - [Calibrate Servo](#calibrate-servo)
- [Proto Module](#proto-module)


## Audio Amp Module

### Tone Song
[audio_amp/tone_song.py](audio_amp/tone_song.py)

Play a sequence of tones out of an Audio Amp Module connected to Slot1.

### Wav Play
[audio_amp/wav_play.py](audio_amp/wav_play.py)

Play wave files out of an Audio Amp Module connected to Slot1.


## Bench Power Module

### Single Power
[bench_power/single_power.py](bench_power/single_power.py)

Control the variable output of a Bench Power Module connected to Slot1.


### Multiple Powers
[bench_power/multiple_powers.py](bench_power/multiple_powers.py)

Control up to 4 variable outputs from a set of Bench Power Modules connected to Slots.
A wave pattern will be played on the attached outputs.


### Controllable Power
[bench_power/controllable_power.py](bench_power/controllable_power.py)

Control the variable output of a Bench Power Module connected to Slot1.
A potentiometer on a Proto Module connected to Slot2 is used for input.


## Big Motor + Encoder Module

### Single Motor
[big_motor/single_motor.py](big_motor/single_motor.py)

Drive a single motor from a Big Motor + Encoder Module connected to Slot1.
A wave pattern will be played on the attached motor, and its speed printed out.


### Multiple Motors
[big_motor/multiple_motors.py](big_motor/multiple_motors.py)

Drive up to 4 motors from a set of Big Motor + Encoder Modules connected to Slots.
A wave pattern will be played on the attached motors, and their speeds printed out.


### All Motors (No Encoders)
[big_motor/all_motors_no_encoders.py](big_motor/all_motors_no_encoders.py)

Drive up to 6 motors from a set of Big Motor + Encoder Modules connected to Slots, using a MotorCluster.
A wave pattern will be played on the attached motors.


### Position Control
[big_motor/position_control.py](big_motor/position_control.py)

Drive a motor smoothly between random positions, with the help of it's attached encoder and PID control.
This uses a Big Motor + Encoder Module connected to Slot1.


### Velocity Control
[big_motor/velocity_control.py](big_motor/velocity_control.py)

Drive a motor smoothly between random speeds, with the help of it's attached encoder and PID control.
This uses a Big Motor + Encoder Module connected to Slot1.

### Position on Velocity Control
[big_motor/position_on_velocity_control.py](big_motor/position_on_velocity_control.py)

Drive a motor smoothly between random positions, with velocity limits, with the help of it's attached encoder and PID control.
This uses a Big Motor + Encoder Module connected to Slot1.


### Tuning

#### Motor Profiler
[big_motor/tuning/motor_profiler.py](big_motor/tuning/motor_profiler.py)

Profile the speed of a motor across its PWM duty cycle range using its attached encoder for feedback.
This uses a Big Motor + Encoder Module connected to Slot1.


#### Position Tuning
[big_motor/tuning/position_tuning.py](big_motor/tuning/position_tuning.py)

A program to aid in the discovery and tuning of motor PID values for position control.
It does this by commanding the motor to move repeatedly between two setpoint angles and
plots the measured response. This uses a Big Motor + Encoder Module connected to Slot1.


#### Velocity Tuning
[big_motor/tuning/velocity_tuning.py](big_motor/tuning/velocity_tuning.py)

A program to aid in the discovery and tuning of motor PID values for velocity control.
It does this by commanding the motor to drive repeatedly between two setpoint speeds and
plots the measured response. This uses a Big Motor + Encoder Module connected to Slot1.

#### Position on Velocity Tuning
[big_motor/tuning/position_on_velocity_tuning.py](big_motor/tuning/position_on_velocity_tuning.py)

A program to aid in the discovery and tuning of motor PID values for position on velocity control.
It does this by commanding the motor to move repeatedly between two setpoint angles and plots
the measured response. This uses a Big Motor + Encoder Module connected to Slot1.


## Dual Motor / Bipolar Stepper Module

### Two Motors
[dual_motor/two_motors.py](dual_motor/two_motors.py)

Drive up to 2 motors from a Dual Motor Module connected to Slot1.
A wave pattern will be played on the attached motors.


### Multiple Motors
[dual_motor/multiple_motors.py](dual_motor/multiple_motors.py)

Drive up to 8 motors from a set of Dual Motor Modules connected to Slots.
A wave pattern will be played on the attached motors.


### All Motors
[dual_motor/all_motors.py](dual_motor/all_motors.py)

Drive up to 12 motors from a set of Dual Motor Modules connected to Slots, using a MotorCluster.
A wave pattern will be played on the attached motors.


### Single Stepper
[dual_motor/single_stepper.py](dual_motor/single_stepper.py)

Drive a stepper motor from a Dual Motor Module connected to Slot1.
A sequence of movements will be played.


## Dual Switched Output Module

### Two Outputs
[dual_output/two_outputs.py](dual_output/two_outputs.py)

Control up to 2 powered outputs from a Dual Output Module connected to Slot1.


### Multiple Outputs
[dual_output/multiple_outputs.py](dual_output/multiple_outputs.py)

Control up to 12 powered outputs from a set of Dual Output Modules connected to Slots.
A cycling pattern will be played on the attached outputs.


### Actioned Output
[dual_output/actioned_output.py](dual_output/actioned_output.py)

Control a powered output from a Dual Output Module connected to Slot1, using a monitor action.


### PWM Output
[dual_output/pwm_output.py](dual_output/pwm_output.py)

Control a powered output from a Dual Output Module connected to Slot1, using PWM.


## LED Strip Module

### Single Strip
[led_strip/single_strip.py](led_strip/single_strip.py)

Drive a Neopixel or Dotstar LED strip with a LED Strip Module connected to Slot1.
A cycling rainbow pattern will be played on the attached strip(s).


### Multiple Strips
[led_strip/multiple_strips.py](led_strip/multiple_strips.py)

Drive multiple Neopixel or Dotstar LED strips with a set of LED Strip Modules connected to slots.
A cycling rainbow pattern will be played on the attached strips.


## Quad Servo Module

### Four Servos
[quad_servo/four_servos.py](quad_servo/four_servos.py)

Drive up to four servos from a Quad Servo Module connected to Slot1.
A wave pattern will be played on the attached servos.


### Multiple Servos
[quad_servo/multiple_servos.py](quad_servo/multiple_servos.py)

Drive up to 16 servos from a set of Quad Servo Modules connected to Slots.
A wave pattern will be played on the attached servos.


### All Servos
[quad_servo/all_servos.py](quad_servo/all_servos.py)

Drive up to 24 servos from a set of Quad Servo Modules connected to Slots, using a ServoCluster.
A wave pattern will be played on the attached servos.


### Servo Feedback
[quad_servo/servo_feedback.py](quad_servo/servo_feedback.py)

Read the analog inputs of Quad Servo Direct modules connected to Slots.


## Serial Servo Module

### Detect Servo
[serial_servo/detect_servo.py](serial_servo/detect_servo.py)

Detect any servos that are attached to a Serial Bus Servo module connected to Slot1.


### Move Servo
[serial_servo/move_servo.py](serial_servo/move_servo.py)

Move a serial servo between two angles with Yukon's onboard buttons.
This uses a Serial Bus Servo module connected to Slot1.


### Drive Servo
[serial_servo/drive_servo.py](serial_servo/drive_servo.py)

Drive a serial servo continuously (aka wheel mode) at a speed with Yukon's onboard buttons.
This uses a Serial Bus Servo module connected to Slot1.


### All Servos
[serial_servo/all_servos.py](serial_servo/all_servos.py)

Move a set of serial servos attached to a set of Serial Bus Servo modules connected to Slots.
A wave pattern will be played on the attached servos.


### Calibrate Servo 
[serial_servo/calibrate_servo.py](serial_servo/calibrate_servo.py)

Calibrate a serial servo's angle offset with Yukon's onboard buttons.
This uses a Serial Bus Servo module connected to Slot1.


## Proto Module

