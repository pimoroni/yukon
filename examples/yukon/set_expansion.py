import time
from machine import Pin
from pimoroni_yukon import Yukon, GP26, GP27, LCD_CS, LCD_DC, LCD_BL

"""
Initialise the IO pins on Yukon's expansion header as outputs and set them.
"""

# Constants
SLEEP = 0.5         # The time to sleep between each reading

# Variables
yukon = Yukon()     # A new Yukon object

# Configure the pins as outputs with a low state
GP26.init(Pin.OUT, value=False)
GP27.init(Pin.OUT, value=False)
LCD_CS.init(Pin.OUT, value=False)
LCD_DC.init(Pin.OUT, value=False)
LCD_BL.init(Pin.OUT, value=False)

# Store the pins in a list for easier access
pins = [GP26, GP27, LCD_CS, LCD_DC, LCD_BL]
current_pin = 0

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Toggle the current pin
        pins[current_pin].toggle()

        # Advance the current pin, and wrap when the end of the list is reached
        current_pin = (current_pin + 1) % len(pins)

        # Read the output states of the five pins
        state_26 = GP26.value()
        state_27 = GP27.value()
        state_cs = LCD_CS.value()
        state_dc = LCD_DC.value()
        state_bl = LCD_BL.value()

        # Print out the pin output states in a nice format
        print(f"GP26 = {state_26}", end=", ")
        print(f"GP27 = {state_27}", end=", ")
        print(f"CS = {state_cs}", end=", ")
        print(f"DC = {state_dc}", end=", ")
        print(f"BL = {state_bl}")

        time.sleep(SLEEP)       # Sleep for a number of seconds

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    GP26.init(Pin.IN)
    GP27.init(Pin.IN)
    yukon.reset()
