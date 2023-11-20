from pimoroni_yukon import Yukon

# Perform system level imports here
# e.g. import math

# Import any slots needed for your modules
# e.g. from pimoroni_yukon import SLOT1 as SLOT

# Import any Yukon modules you are using
# e.g. from pimoroni_yukon.modules import DualMotorModule

# Import the logging level to use (if you wish to change from the default)
# e.g. from pimoroni_yukon.logging import LOG_NONE, LOG_WARN, LOG_INFO, LOG_DEBUG

from pimoroni_yukon.timing import ticks_ms, ticks_add  # This import is only needed if using .monitor_until_ms()

# Perform any other imports here
# e.g. from pimoroni_yukon.devices.stepper import OkayStepper

"""
This is a boilerplate example for Yukon. Use it as a base for your own programs.

Press "Boot/User" to exit the program.
"""

# Constants
SLEEP_TIME = 0.1

# Place other constants here
# e.g. VOLTAGE_LIMIT = 12

# Variables
yukon = Yukon()     # Create a new Yukon object. These optional keyword parameters are supported:
                    # `voltage_limit`, `current_limit`, `temperature_limit`, and `logging_level`

# Create your module objects here
# e.g. module = DualMotorModule()

# Place other variables here
# e.g. button_state = False


# Put any functions needed for your program here
# e.g. def my_function():
#          pass


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Register your module with their respective slots
    # e.g. yukon.register_with_slot(module, SLOT)

    # Verify that the correct modules are attached to Yukon, and initialise them
    # This is not necessary if your program uses Yukon's IO directly, or via proto modules
    # yukon.verify_and_initialise()

    # Set up any variables or objects that need initialised modules
    # e.g. stepper = OkayStepper(module.motor1, module.motor2)

    yukon.enable_main_output()                  # Turn on power to the module slots

    # Enable any modules or objects
    # e.g. module.enable()

    current_time = ticks_ms()                   # Record the start time of the program loop. Only needed if using .monitor_until_ms()

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        #######################
        # Put your program here
        #######################

        # Choose one of three options for monitoring Yukon's sensors

        # 1) Perform a single check of Yukon's internal voltage, current, and temperature sensors
        # yukon.monitor_once()

        # 2) Monitor sensors for a number of seconds, recording the min, max, and average for each
        # yukon.monitored_sleep(SLEEP_TIME)

        # 3) Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(SLEEP_TIME * 1000))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updates taking a non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

        # Print out any readings from the monitoring period that may be useful
        yukon.print_readings(allowed="Vi_avg")

# Reset the yukon instance if the program completes successfully or an exception occurs
finally:
    # Clean up any objects that hold on to hardware resources
    # e.g. if stepper is not None:
    #          stepper.release()

    yukon.reset()
