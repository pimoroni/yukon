from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import DualOutputModule

"""
How to control a powered output from a Dual Output Module connected to Slot1, using a monitor action.
"""

# Constants
OUTPUT = 1                                  # The output from the Dual Switched Module to use
VOLTAGE_LIMIT = 12.1                        # The voltage to not exceed, to protect the output
ACTION_HIGH_TEMP = 25.0                     # The temperature above which the output (e.g. a fan) should be on
ACTION_LOW_TEMP = 23.0                      # The temperature below which the output (e.g. a fan) should be off
SLEEP = 1.0                                 # The time to sleep between each reading

# Variables
yukon = Yukon(voltage_limit=VOLTAGE_LIMIT)  # Create a new Yukon object, with a lower voltage limit set
module = DualOutputModule()                 # Create a DualOutputModule object


# A function that Yukon will call every time it gets new readings
# Here we turn the output on if it exceeds a high temperature,
# and off if it falls below a low temperature.
def temperature_check(voltage_in, voltage_out, current, temperature):
    if temperature > ACTION_HIGH_TEMP:
        module.output(OUTPUT, True)
    elif temperature < ACTION_LOW_TEMP:
        module.output(OUTPUT, False)


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)          # Register the DualOutputModule object with the slot
    yukon.assign_monitor_action(temperature_check)  # Pass the monitor action function to Yukon
    yukon.verify_and_initialise()                   # Verify that a DualOutputModule is attached to Yukon, and initialise it
    yukon.enable_main_output()                      # Turn on power to the module slots

    module.enable(OUTPUT)                           # Enable the output driver

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Monitor sensors for a number of seconds, recording the min, max, and average for each
        yukon.monitored_sleep(SLEEP)

        # Print out the average temperature of the Yukon board over the monitoring period
        yukon.print_readings(allowed="T_avg", include_modules=False)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
