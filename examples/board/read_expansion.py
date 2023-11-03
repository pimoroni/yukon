import time
from machine import Pin
from pimoroni_yukon import Yukon, GP26, GP27, LCD_CS, LCD_DC, LCD_BL

"""
Read the IO pins on Yukon's expansion header.

Press "Boot/User" to exit the program.
"""

# Constants
SLEEP = 0.5         # The time to sleep between each reading

# Variables
yukon = Yukon()     # A new Yukon object

# Configure the pins as inputs
GP26.init(Pin.IN)
GP27.init(Pin.IN)
LCD_CS.init(Pin.IN)
LCD_DC.init(Pin.IN)
LCD_BL.init(Pin.IN)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Read the two GP pins
        state_26 = GP26.value()
        state_27 = GP27.value()

        # Read the three 'LCD' pins. These have internal
        # pull-ups so will read 1 if left disconnected
        state_cs = LCD_CS.value()
        state_dc = LCD_DC.value()
        state_bl = LCD_BL.value()

        # Print out the pin states in a nice format
        print(f"GP26 = {state_26}", end=", ")
        print(f"GP27 = {state_27}", end=", ")
        print(f"CS = {state_cs}", end=", ")
        print(f"DC = {state_dc}", end=", ")
        print(f"BL = {state_bl}")

        time.sleep(SLEEP)       # Sleep for a number of seconds

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
