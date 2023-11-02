from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import DualMotorModule
from pimoroni_yukon.extras.stepper import OkayStepper

"""
How to drive a stepper motor from a Dual Motor Module connected to Slot1.
A sequence of movements will be played.
"""

# Put your movements here!
# First value is the position (in steps) to go to, second is the duration (in seconds) to get there
# 200 steps will produce a complete rotation for a typical stepper with 1.8 degrees per step
MOVEMENTS = [(200, 2),
             (400, 1),
             (0, 3),
             (0, 2),
             (-100, 2),
             (0, 5)]

# Constants
CURRENT_SCALE = 0.5             # How much to scale the output current to the stepper motor by, between 0.0 and 1.0

# Variables
yukon = Yukon()                 # Create a new Yukon object
module = DualMotorModule()      # Create a DualMotorModule object
stepper = None                  # A variable to store an OkayStepper object created later
next_movement = 0               # The index of the next movement to perform

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)      # Register the DualMotorModule object with the slot
    yukon.verify_and_initialise()               # Verify that a DualMotorModule is attached to Yukon, and initialise it
    yukon.enable_main_output()                  # Turn on power to the module slots

    # Create a class for controlling the stepper motor, in this case OkayStepper, and provide it with the DualMotorModule's two outputs
    stepper = OkayStepper(module.motor1, module.motor2, current_scale=CURRENT_SCALE)

    # Set the hardware current limit to its maximum (OkayStepper controls current with PWM instead)
    module.set_current_limit(DualMotorModule.MAX_CURRENT_LIMIT)
    module.enable()                             # Enable the motor driver on the DualMotorModule

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        if not stepper.is_moving():
            # Have we reached the end of the movements?
            if next_movement >= len(MOVEMENTS):
                stepper.release()                           # Release the stepper motor
                module.disable()                            # Disable the motor driver
                yukon.set_led('A', False)                   # Show that the stepper motor is no longer moving
                break                                       # Exit the main while loop

            step, travel_time = MOVEMENTS[next_movement]    # Extract the current movement from the list
            stepper.move_to(step, travel_time)              # Initiate the movement
            yukon.set_led('A', True)                        # Show that the stepper motor is moving
            next_movement += 1                              # Advance the next movement index

        # Perform a single check of Yukon's internal voltage, current, and temperature sensors
        # NOTE. This is currently commented out as it interfers with the precise timing needed by stepper motors
        # yukon.monitor_once()

finally:
    if stepper is not None:
        stepper.release()                       # Release the stepper motor (if not already done so)

    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
