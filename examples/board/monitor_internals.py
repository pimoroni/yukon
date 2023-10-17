from pimoroni_yukon import Yukon

"""
Use Yukon's monitoring function to read the internal sensors.
Power needs to be provided to the XT30 connector, otherwise
the monitoring will raise an UnderVoltageError.
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
        yukon.monitored_sleep(SLEEP)

        # Print out the readings taken during monitoring
        yukon.print_readings()

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
