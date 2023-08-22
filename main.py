# This file runs at power-up. It and files in the /lib directory get added to a LittleFS filesystem and appended to the firmware
# Overide this file with any of your own code that you wish to run at power-up, or remove the file to not have anything run.

import time
from pimoroni_yukon import Yukon

"""
A program to show that Yukon is active, by flashing the onboard LEDs in sequence.
"""


# Create a Yukon object to begin using the board
yukon = Yukon()

# Loop forever, or until a stop command from Thonny or another IDE is received
while True:
    yukon.set_led('A', True)
    time.sleep(0.2)
    yukon.set_led('B', True)
    time.sleep(0.2)
    yukon.set_led('A', False)
    time.sleep(0.2)
    yukon.set_led('B', False)
    time.sleep(1.4)
