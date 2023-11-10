import time
from machine import Pin
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as BUZZER_SLOT

"""
Drive a buzzer soldered between Fast3 and Ground on a proto module connected to Slot1.

Press "Boot/User" to exit the program.
"""

# Constants
PERIOD = 0.5                # The time between each buzz
DUTY = 0.5                  # The percentage of the time that the buzz will be on for

# Variables
yukon = Yukon()             # Create a new Yukon object
buzzer = BUZZER_SLOT.FAST3  # The pin the buzzer is attached to

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    buzzer.init(Pin.OUT)    # Set up the buzzer pin as an output

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Toggle the buzzer on and off repeatedly
        buzzer.on()
        time.sleep(PERIOD * DUTY)
        buzzer.off()
        time.sleep(PERIOD * (1.0 - DUTY))

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
