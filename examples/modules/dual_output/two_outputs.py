from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import DualOutputModule

"""
Control up to 2 powered outputs from a Dual Output Module connected to Slot1.

Press "A" to toggle the state of Output 1.
Press "B" to toggle the state of Output 2.
Press "Boot/User" to exit the program.
"""

# Constants
OUTPUT_NAMES = ("Small Fan", "Big Fan")     # The names to give the two outputs when printing
VOLTAGE_LIMIT = 12.1                        # The voltage to not exceed, to protect the outputs

# Variables
yukon = Yukon(voltage_limit=VOLTAGE_LIMIT)  # Create a new Yukon object, with a lower voltage limit set
module = DualOutputModule()                 # Create a DualOutputModule object
last_button_states = [False, False]         # The last states of the buttons

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)  # Register the DualOutputModule object with the slot
    yukon.verify_and_initialise()           # Verify that a DualOutputModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots
    module.enable()                         # Enable the output switches

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        for i in range(DualOutputModule.NUM_OUTPUTS):
            state = yukon.is_pressed(i)                         # Read the state of each onboard button

            # Has the button been newly pressed?
            if state is True and state != last_button_states[i]:
                next_out_state = not module.outputs[i].value()  # Read the current output state, and invert it
                module.outputs[i].value(next_out_state)         # Set the output to the inverted state
                yukon.set_led(i, next_out_state)                # Set the button LED to match

                # Print out the new state of the output with its name
                print(f"{OUTPUT_NAMES[i]} = {'On' if next_out_state else 'Off'}")

            last_button_states[i] = state                       # Record the button state

        # Perform a single check of Yukon's internal voltage, current, and temperature sensors
        yukon.monitor_once()

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
