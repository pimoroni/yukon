import time
from pimoroni_yukon import Yukon

"""
Read Yukon's onboard Buttons.
"""

# Constants
SLEEP = 0.5     # The time to sleep between each reading

# Variables
yukon = Yukon()     # A new Yukon object

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Read both buttons
        state_a = yukon.is_pressed('A')
        state_b = yukon.is_pressed('B')

        # Print out the button states in a nice format
        print(f"A = {state_a}", end=", ")
        print(f"B = {state_b}")

        time.sleep(SLEEP)       # Sleep for a number of seconds

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
