# Yukon Micropython Showcase Examples <!-- omit in toc -->

This folder contains a collection of *Showcase* examples, that bring together concepts presented by individual board and module examples to create functional projects.

- [RC Rover](#rc-rover)
- [Spider Tank](#spider-tank)


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
