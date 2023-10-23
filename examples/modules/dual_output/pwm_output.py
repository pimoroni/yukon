from machine import PWM
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import DualOutputModule

"""
How to control a powered output from a Dual Output Module connected to Slot1, using PWM.
"""

# Constants
OUTPUT = DualOutputModule.OUTPUT_1          # The output from the Dual Switched Module to use
VOLTAGE_LIMIT = 12.1                        # The voltage to not exceed, to protect the output
FREQUENCY = 8                               # The frequency to run the PWM at (8 is the lowest supported)
                                            # The highest is a result of the output's rise time of 2V/ms (e.g. 6ms for 12V)
PERCENT = 0.5                               # The duty cycle percent of the PWM signal
SLEEP = 1.0                                 # The time to sleep between each reading

# Variables
yukon = Yukon(voltage_limit=VOLTAGE_LIMIT)  # Create a new Yukon object, with a lower voltage limit set
module = DualOutputModule()                 # Create a DualOutputModule object

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)              # Register the DualOutputModule object with the slot
    yukon.verify_and_initialise()                       # Verify that a DualOutputModule is attached to Yukon, and initialise it

    yukon.enable_main_output()                          # Turn on power to the module slots
    module.enable(OUTPUT)                               # Enable a single output switch

    pwm = PWM(module.outputs[OUTPUT], freq=FREQUENCY)   # Create a PWM object to control the output
    pwm.duty_u16(int(min(max(PERCENT, 0), 1) * 65535))  # Convert the duty cycle percent to a u16 value and set it

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Monitor sensors for a number of seconds, recording the min, max, and average for each
        yukon.monitored_sleep(SLEEP)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
