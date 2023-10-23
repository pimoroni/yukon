# Yukon Micropython Module Examples <!-- omit in toc -->

- [Audio Amp Module](#audio-amp-module)
- [Bench Power Module](#bench-power-module)
  - [Single Power](#single-power)
  - [Multiple Powers](#multiple-powers)
  - [Controllable Power](#controllable-power)
- [Big Motor + Encoder Module](#big-motor--encoder-module)
- [Dual Motor / Bipolar Stepper Module](#dual-motor--bipolar-stepper-module)
  - [Two Motors](#two-motors)
  - [Multiple Motors](#multiple-motors)
  - [All Motors](#all-motors)
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
- [Proto Module](#proto-module)


## Audio Amp Module

## Bench Power Module

### Single Power
[bench_power/single_power.py](bench_power/single_power.py)

How to control the variable output of a Bench Power Module connected to Slot1.
Use the A and B buttons to increase and decrease the output voltage.


### Multiple Powers
[bench_power/multiple_powers.py](bench_power/multiple_powers.py)

How to drive up to 4 variable outputs from a set of Bench Power Modules connected to Slots.
A wave pattern will be played on the attached outputs.


### Controllable Power
[bench_power/controllable_power.py](bench_power/controllable_power.py)

How to control the variable output of a Bench Power Module connected to Slot1.
A potentiometer on a Proto Module connected to Slot2 is used for input.


## Big Motor + Encoder Module

## Dual Motor / Bipolar Stepper Module

### Two Motors
[dual_motor/two_motors.py](dual_motor/two_motors.py)

How to drive up to 2 motors from a Dual Motor Module connected to Slot1.
A wave pattern will be played on the attached motors.


### Multiple Motors
[dual_motor/multiple_motors.py](dual_motor/multiple_motors.py)

How to drive up to 8 motors from a set of Dual Motor Module connected to Slots.
A wave pattern will be played on the attached motors.


### All Motors
[dual_motor/all_motors.py](dual_motor/all_motors.py)

How to drive up to 12 motors from a set of Dual Motor Modules connected to Slots, using a MotorCluster.
A wave pattern will be played on the attached motors.


## Dual Switched Output Module

### Two Outputs
[dual_output/two_outputs.py](dual_output/two_outputs.py)

How to control up to 2 powered outputs from a Dual Output Module connected to Slot1.
Buttons 'A' and 'B' toggle the state of each output.


### Multiple Outputs
[dual_output/multiple_outputs.py](dual_output/multiple_outputs.py)

How to drive up to 12 powered outputs from a set of Dual Output Modules connected to Slots.
A cycling pattern will be played on the attached outputs.


### Actioned Output
[dual_output/actioned_output.py](dual_output/actioned_output.py)

How to control a powered output from a Dual Output Module connected to Slot1, using a monitor action.


### PWM Output
[dual_output/pwm_output.py](dual_output/pwm_output.py)

How to control a powered output from a Dual Output Module connected to Slot1, using PWM.


## LED Strip Module

### Single Strip
[led_strip/single_strip.py](led_strip/single_strip.py)

How to drive a Neopixel or Dotstar LED strip with a LED Strip Module connected to Slot1.
A cycling rainbow pattern will be played on the attached strip(s).


### Multiple Strips
[led_strip/multiple_strips.py](led_strip/multiple_strips.py)

How to drive multiple Neopixel or Dotstar LED strips with a set of LED Strip Modules connected to slots.
A cycling rainbow pattern will be played on the attached strips.


## Quad Servo Module

### Four Servos
[quad_servo/four_servos.py](quad_servo/four_servos.py)

How to drive up to four servos from a Quad Servo Module connected to Slot1.
A wave pattern will be played on the attached servos.


### Multiple Servos
[quad_servo/multiple_servos.py](quad_servo/multiple_servos.py)

How to drive up to 16 servos from a set of Quad Servo Modules connected to Slots.
A wave pattern will be played on the attached servos.


### All Servos
[quad_servo/all_servos.py](quad_servo/all_servos.py)

How to drive up to 24 servos from a set of Quad Servo Modules connected to Slots, using a ServoCluster.
A wave pattern will be played on the attached servos.


### Servo Feedback
[quad_servo/servo_feedback.py](quad_servo/servo_feedback.py)

How to read the analog inputs on Quad Servo Direct modules connected to Slots.


## Serial Servo Module

## Proto Module

