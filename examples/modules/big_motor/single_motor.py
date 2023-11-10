import math
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import BigMotorModule
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
Drive a single motor from a Big Motor + Encoder Module connected to Slot1.
A wave pattern will be played on the attached motor, and its speed printed out.

Press "Boot/User" to exit the program.
"""

# Constants
GEAR_RATIO = 30                         # The gear ratio of the motor
ENCODER_CPR = 12                        # The number of counts a single encoder shaft revolution will produce
MOTOR_CPR = GEAR_RATIO * ENCODER_CPR    # The number of counts a single motor shaft revolution will produce
ENCODER_PIO = 0                         # The PIO system to use (0 or 1) for the motor's encoder
ENCODER_SM = 0                          # The State Machines (SM) to use for the motor's encoder

SPEED = 0.005                           # How much to advance the motor phase offset by each update
UPDATES = 50                            # How many times to update the motors per second
SPEED_EXTENT = 1.0                      # How far from zero to drive the motors

# Variables
yukon = Yukon()                         # Create a new Yukon object
module = BigMotorModule(encoder_pio=ENCODER_PIO,    # Create a BigMotorModule object, with details of the encoder
                        encoder_sm=ENCODER_SM,
                        counts_per_rev=MOTOR_CPR)
phase_offset = 0                        # The offset used to animate the motor

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)      # Register the BigMotorModule object with the slot
    yukon.verify_and_initialise()               # Verify that a BigMotorModule is attached to Yukon, and initialise it
    yukon.enable_main_output()                  # Turn on power to the module slots

    module.enable()                             # Enable the motor driver on the BigMotorModule

    current_time = ticks_ms()                   # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        capture = module.encoder.capture()                  # Capture the state of the encoder
        print(f"RPS = {capture.revolutions_per_second}")    # Print out the measured speed of the motor

        # Give the motor a new speed
        phase = phase_offset * math.pi * 2
        speed = math.sin(phase) * SPEED_EXTENT
        module.motor.speed(speed)

        # Advance the phase offset, wrapping if it exceeds 1.0
        phase_offset += SPEED
        if phase_offset >= 1.0:
            phase_offset -= 1.0

        # Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(1000 / UPDATES))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updates takinga non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
