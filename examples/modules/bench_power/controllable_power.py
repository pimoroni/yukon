from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as PWR_SLOT
from pimoroni_yukon import SLOT2 as POT_SLOT
from pimoroni_yukon.modules import BenchPowerModule, ProtoPotModule
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
Control the variable output of a Bench Power Module connected to Slot1.
A potentiometer on a Proto Module connected to Slot2 is used for input.

Press "Boot/User" to exit the program.
"""

# Constants
UPDATES = 10                                # How many times to update the outputs per second

# Variables
yukon = Yukon()                             # Create a new Yukon object
bench = BenchPowerModule()                  # Create a BenchPowerModule object
pot = ProtoPotModule()                      # Create a ProtoPotModule object

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(bench, PWR_SLOT)           # Register the BenchPowerModule object with the slot
    yukon.register_with_slot(pot, POT_SLOT)             # Register the ProtoPotModule object with the slot
    yukon.verify_and_initialise()                       # Verify that the two modules areattached to Yukon, and initialise them
    yukon.enable_main_output()                          # Turn on power to the module slots

    percent = pot.read()                                # Read the potentiometer value
    bench.set_percent(pot.read())                       # Set the initial voltage to output, as a percent
    bench.enable()                                      # Enable the BenchPowerModule's onboard regulator

    current_time = ticks_ms()                                   # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        percent = pot.read()                            # Read the potentiometer value
        bench.set_percent(percent)                      # Set the new voltage to output, as a percent
        print(f"Percent = {percent}, Voltage = {bench.read_voltage()}")

        # Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(1000 / UPDATES))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updating of the rainbows taking a non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
