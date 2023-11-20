import math
import random
from pimoroni import PID, NORMAL_DIR  # , REVERSED_DIR
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import BigMotorModule
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
Drive a motor smoothly between random positions, with the help of it's attached encoder and PID control.
This uses a Big Motor + Encoder Module connected to Slot1.

Press "Boot/User" to exit the program.
"""

# Constants
GEAR_RATIO = 30                         # The gear ratio of the motor
ENCODER_CPR = 12                        # The number of counts a single encoder shaft revolution will produce
MOTOR_CPR = GEAR_RATIO * ENCODER_CPR    # The number of counts a single motor shaft revolution will produce

MOTOR_DIRECTION = NORMAL_DIR            # The direction to spin the motor in. NORMAL_DIR (0), REVERSED_DIR (1)
ENCODER_DIRECTION = NORMAL_DIR          # The direction the encoder counts positive in. NORMAL_DIR (0), REVERSED_DIR (1)
SPEED_SCALE = 3.4                       # The scaling to apply to the motor's speed to match its real-world speed

UPDATES = 100                           # How many times to update the motor per second
UPDATE_RATE = 1 / UPDATES
TIME_FOR_EACH_MOVE = 1                  # The time to travel between each random value
UPDATES_PER_MOVE = TIME_FOR_EACH_MOVE * UPDATES
PRINT_DIVIDER = 4                       # How many of the updates should be printed (i.e. 2 would be every other update)

# Multipliers for the different printed values, so they appear nicely on the Thonny plotter
SPD_PRINT_SCALE = 20                    # Driving Speed multipler

POSITION_EXTENT = 180                   # How far from zero to move the motor, in degrees
INTERP_MODE = 2                         # The interpolating mode between setpoints. STEP (0), LINEAR (1), COSINE (2)

# PID values
POS_KP = 0.14                           # Position proportional (P) gain
POS_KI = 0.0                            # Position integral (I) gain
POS_KD = 0.0022                         # Position derivative (D) gain


# Variables
yukon = Yukon()                                     # Create a new Yukon object
module = BigMotorModule(counts_per_rev=MOTOR_CPR)   # Create a BigMotorModule object
pos_pid = PID(POS_KP, POS_KI, POS_KD, UPDATE_RATE)  # Create a PID object for position control
update = 0
print_count = 0

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)  # Register the BigMotorModule object with the slot
    yukon.verify_and_initialise()           # Verify that a BigMotorModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots

    module.motor.speed_scale(SPEED_SCALE)   # Set the motor's speed scale

    # Set the motor and encoder's direction
    module.motor.direction(MOTOR_DIRECTION)
    module.encoder.direction(ENCODER_DIRECTION)

    module.enable()                         # Enable the motor driver on the BigMotorModule
    module.motor.enable()                   # Enable the motor to get started

    # Set the initial value and create a random end value between the extents
    start_value = 0.0
    end_value = random.uniform(-POSITION_EXTENT, POSITION_EXTENT)

    current_time = ticks_ms()               # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        capture = module.encoder.capture()  # Capture the state of the encoder

        # Calculate how far along this movement to be
        percent_along = min(update / UPDATES_PER_MOVE, 1.0)

        if INTERP_MODE == 0:
            # Move the motor instantly to the end value
            pos_pid.setpoint = end_value
        elif INTERP_MODE == 2:
            # Move the motor between values using cosine
            pos_pid.setpoint = (((-math.cos(percent_along * math.pi) + 1.0) / 2.0) * (end_value - start_value)) + start_value
        else:
            # Move the motor linearly between values
            pos_pid.setpoint = (percent_along * (end_value - start_value)) + start_value

        # Calculate the velocity to move the motor closer to the position setpoint
        vel = pos_pid.calculate(capture.degrees, capture.degrees_per_second)

        module.motor.speed(vel)             # Set the new motor driving speed

        # Print out the current motor values and their setpoints, but only on every multiple
        if print_count == 0:
            print("Pos =", capture.degrees, end=", ")
            print("Pos SP =", pos_pid.setpoint, end=", ")
            print("Speed = ", module.motor.speed() * SPD_PRINT_SCALE)

        # Increment the print count, and wrap it
        print_count = (print_count + 1) % PRINT_DIVIDER

        update += 1     # Move along in time

        # Have we reached the end of this movement?
        if update >= UPDATES_PER_MOVE:
            update = 0  # Reset the counter

            # Set the start as the last end and create a new random end value
            start_value = end_value
            end_value = random.uniform(-POSITION_EXTENT, POSITION_EXTENT)

        # Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(1000 * UPDATE_RATE))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updates taking a non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

    module.motor.disable()      # Disable the motor

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
