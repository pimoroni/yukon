import time
from pimoroni_yukon import Yukon

"""
Read the internal sensors of Yukon.

Press "Boot/User" to exit the program.
"""

# Constants
SLEEP = 0.5         # The time to sleep between each reading

# Variables
yukon = Yukon()     # A new Yukon object

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Read Yukon's voltage sensors
        voltage_in = yukon.read_input_voltage()
        voltage_out = yukon.read_output_voltage()

        # Read Yukon's current sensor, but only if the input voltage
        # is high enough to turn it on, otherwise set the value to zero
        current = yukon.read_current() if voltage_in > 2.5 else 0.0

        # Read Yukon's temperature sensor
        temperature = yukon.read_temperature()

        # Print out the pin states in a nice format
        print(f"Vin = {voltage_in} V", end=", ")
        print(f"Vout = {voltage_out} V", end=", ")
        print(f"Cur = {current} A", end=", ")
        print(f"Temp = {temperature} °C")

        time.sleep(SLEEP)       # Sleep for a number of seconds

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
