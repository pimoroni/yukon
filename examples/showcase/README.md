# Yukon Micropython Showcase Examples <!-- omit in toc -->

This folder contains a collection of *Showcase* examples, that bring together concepts presented by individual board and module examples to create functional projects.

- [RC Rover](#rc-rover)
- [Spider Tank](#spider-tank)
- [CNC Plotter](#cnc-plotter)


## RC Rover
[rover/main.py](rover/main.py)

A showcase of Yukon as a differential drive rover. It uses two Big Motor modules, one to control the left side motors, and the other to control the right side motors.

There is a LED Strip module controlling left and right strips that represent each side's speed as a colour from green -> blue -> red. Additionally, there is a proto module wired up to a buzzer to alert the user to the battery voltage getting too low, which also exposes the UART for connection to a bluetooth serial transceiver.

The program receives commands from the JoyBTCommander Android App and converts them to motor speeds. it also sends the voltage, current, and temperature of Yukon back to the App.


## Spider Tank
[spidertank/main.py](spidertank/main.py)

A showcase of Yukon as a hexapod robot, with 3 degrees of freedom per leg. It uses two Serial Bus Servo modules, one to control the left side servos, and the other to control the right side servos.

There is also a proto module wired up to a buzzer to alert the user to the battery voltage getting too low.

The program performs inverse kinematics for each leg, with the target points following a tripod walking gait.


## CNC Plotter
[plotter/main.py](plotter/main.py)

A showcase of Yukon as a 3-axis CNC pen plotter. It uses four Dual Motor modules, to control for stepper motors (the Y-Axis has two steppers). It also uses two Quad Servo Direct modules to provide convenient wiring for the machine's limit switches.

The program first homes the 3 axes of the machine to give an origin from which to plot from. Then after pressing 'A' it executes commands from a .gcode file loaded onto Yukon.

Only a subset of G-Code is supported, sufficient for performing linear moves of the machine, and raising and lowering its pen.
