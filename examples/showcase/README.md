# Yukon Micropython Showcase Examples <!-- omit in toc -->

This folder contains a collection of *Showcase* examples, that bring together concepts presented by individual board and module examples to create functional projects.

- [RC Rover](#rc-rover)
- [Spider Tank](#spider-tank)
- [Remote Spider Tank](#remote-spider-tank)
- [CNC Plotter](#cnc-plotter)


## RC Rover

<img src="https://shop.pimoroni.com/cdn/shop/files/yukon-projects-4_1500x1500_crop_center.jpg" width="500">

[rover/main.py](rover/main.py)

A showcase of Yukon as a differential drive rover. It uses two Big Motor modules, one to control the left side motors, and the other to control the right side motors.

There is a LED Strip module controlling left and right strips that represent each side's speed as a colour from green -> blue -> red. Additionally, there is a proto module wired up to a buzzer to alert the user to the battery voltage getting too low, and a RM2 Wireless Module for reaching the game pad.

The program is driven by a Bluetooth game pad paired straight to the board, with no phone or computer in between. The first time, put the pad into pairing mode and Yukon finds it, pairs, and saves the link key to a file on the board. From then on switching the pad on is enough. LED A is lit whenever the rover is waiting for the pad, and the motors coast to a stop while it is.

`rover/lib/controls.py` holds the control schemes, one function each, and the mixing that turns them into a speed per side. `triggers` uses the analogue triggers as a throttle and steers with the right stick, and is what the rover starts with. `sticks` drives with the left stick and steers with the right. The pad's Plus button swaps between them while driving. Set `PAD_MAPPING` in `main.py` to suit your pad. The rover steers only while it is moving, since it has too much ground friction to skid steer on the spot.

The wireless module goes in slot 4, though any free slot will do. The LED Strip module keeps slot 5.


## Spider Tank

<img src="https://shop.pimoroni.com/cdn/shop/files/yukon-projects-3_1500x1500_crop_center.jpg" width="500">

[spidertank/main.py](spidertank/main.py)

A showcase of Yukon as a hexapod robot, with 3 degrees of freedom per leg. It uses two Serial Bus Servo modules, one to control the left side servos, and the other to control the right side servos.

There is also a proto module wired up to a buzzer to alert the user to the battery voltage getting too low.

The program performs inverse kinematics for each leg, with the target points following a tripod walking gait.


## Remote Spider Tank

[spidertank_remote/main.py](spidertank_remote/main.py)

The same hexapod, walked by hand from a Bluetooth game pad paired straight to the board. The pad's right trigger sets how fast the gait plays, from standing still at rest to full speed pulled in, so the walk starts, slows and stops under your thumb.

Pairing works as for the RC Rover, and the two share the same link key file format. Copy `gamepad.py`, `gamepad_mappings.py` and `pad_keys.py` from [spidertank_remote/lib](spidertank_remote/lib) to the board's `lib` directory alongside `leg_ik.py`, and set `PAD_MAPPING` in `main.py` to suit your pad.

The wireless module goes in slot 4, though any slot the servo modules and buzzer are not using will do. LED A is lit whenever the spider tank is waiting for the pad, and it stands still while it is.


## CNC Plotter

<img src="https://shop.pimoroni.com/cdn/shop/files/yukon-projects-7_1500x1500_crop_center.jpg" width="500">

[plotter/main.py](plotter/main.py)

A showcase of Yukon as a 3-axis CNC pen plotter. It uses four Dual Motor modules, to control for stepper motors (the Y-Axis has two steppers). It also uses two Quad Servo Direct modules to provide convenient wiring for the machine's limit switches.

The program first homes the 3 axes of the machine to give an origin from which to plot from. Then after pressing 'A' it executes commands from a .gcode file loaded onto Yukon.

Only a subset of G-Code is supported, sufficient for performing linear moves of the machine, and raising and lowering its pen.
