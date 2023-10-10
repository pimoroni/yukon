from pimoroni_yukon import Yukon

"""
Use Yukon's monitoring function to read the internal sensors.
"""

# Constants
SLEEP = 0.5         # The time to sleep between each reading

# Variables
yukon = Yukon()     # A new Yukon object

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Monitor sensors for a number of seconds, recording the min, max, and average for each
        # With the default logging level, these values will be also be printed out
        yukon.monitored_sleep(SLEEP)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
