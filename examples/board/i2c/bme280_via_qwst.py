import time
from pimoroni_yukon import Yukon
from breakout_bme280 import BreakoutBME280

"""
Read a BME280 sensor attached to the QwST connectors or Breakout Garden header.
"""

# Constants
ADDRESS = 0x76     # Or 0x77 if trace on rear of breakout has been cut
SLEEP = 1.0        # The time to sleep between each reading

# Variables
yukon = Yukon()                             # A new Yukon object
bme = BreakoutBME280(yukon.i2c, ADDRESS)    # A new BME280 sensor with Yukon's I2C

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        reading = bme.read()   # Take a reading from the BME sensor

        # Print out the readings in a nice format
        print(f"Temperature: {reading[0]} C", end=", ")
        print(f"Pressure: {reading[1]} hPa", end=", ")
        print(f"Humidity: {reading[2]} %")

        time.sleep(SLEEP)       # Sleep for a number of seconds

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
