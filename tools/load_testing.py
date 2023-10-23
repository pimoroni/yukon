from pimoroni_yukon import Yukon
from pimoroni_yukon.logging import LOG_DEBUG

"""
This program allows for the testing of Yukon's load capabilities.
It bypasses the normal module checks, enables the main output, then reports various readings.
"""

# Constants
SLEEP = 0.1                                 # The time to sleep between each reading

# Variables
yukon = Yukon(logging_level=LOG_DEBUG)      # Create a Yukon object with the logging level set to debug

try:
    # Perform the usual verify checks, but allow for unregistered and undetected modules, as well as no modules
    yukon.verify_and_initialise(allow_unregistered=True, allow_undetected=True, allow_no_modules=True)

    yukon.enable_main_output()              # Turn on power to the module slots

    while True:
        # Monitor sensors for a number of seconds, recording the min, max, and average for each
        # As we're debug logging, printout happens automatically,
        # so filter it to only show the average voltage, current and temperature
        yukon.monitored_sleep(SLEEP, allowed=("Vi_avg", "C_avg", "T_avg"))

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
