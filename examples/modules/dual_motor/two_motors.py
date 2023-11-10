import math
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import DualMotorModule
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
Drive up to 2 motors from a Dual Motor Module connected to Slot1.
A wave pattern will be played on the attached motors.

Press "Boot/User" to exit the program.
"""

# Constants
SPEED = 0.005                   # How much to advance the motor phase offset by each update
UPDATES = 50                    # How many times to update the motors per second
SPEED_EXTENT = 1.0              # How far from zero to drive the motors
CURRENT_LIMIT = 0.5             # The maximum current (in amps) the motors will be driven with

# Variables
yukon = Yukon()                 # Create a new Yukon object
module = DualMotorModule()      # Create a DualMotorModule object
phase_offset = 0                # The offset used to animate the motors


# Function to get a motor speed from its index
def speed_from_index(index, offset=0.0):
    phase = ((index / DualMotorModule.NUM_MOTORS) + offset) * math.pi * 2
    speed = math.sin(phase) * SPEED_EXTENT
    return speed


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)      # Register the DualMotorModule object with the slot
    yukon.verify_and_initialise()               # Verify that a DualMotorModule is attached to Yukon, and initialise it
    yukon.enable_main_output()                  # Turn on power to the module slots

    module.set_current_limit(CURRENT_LIMIT)     # Change the current limit (in amps) of the motor driver
    module.enable()                             # Enable the motor driver on the DualMotorModule

    current_time = ticks_ms()                   # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Give all the motors new speeds
        current_motor = 0
        for motor in module.motors:
            speed = speed_from_index(current_motor, phase_offset)
            motor.speed(speed)
            current_motor += 1

        # Advance the phase offset, wrapping if it exceeds 1.0
        phase_offset += SPEED
        if phase_offset >= 1.0:
            phase_offset -= 1.0

        print(f"Phase = {phase_offset}")

        # Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(1000 / UPDATES))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updates takinga non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
