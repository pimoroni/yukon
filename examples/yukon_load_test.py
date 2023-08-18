from pimoroni_yukon import Yukon

"""
This example is purely for the use of testing Yukon's load capabilities. It enables the main output by bypassing all of the module checks, then reports the voltage, current and temperature of Yukon.
"""


# Create a Yukon object to begin using the board, and a set a voltage limit just above what the fans are rated for
yukon = Yukon(voltage_limit=15.5, logging_level=3)

try:
    # Initialise Yukon's registered modules
    yukon.initialise_modules(allow_unregistered=True, allow_undetected=True, allow_no_modules=True)

    # Turn on the module power
    yukon.enable_main_output()

    while True:
        # Use the Yukon class to sleep, which lets it monitor voltage, current, and temperature
        yukon.monitored_sleep(0.1)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
