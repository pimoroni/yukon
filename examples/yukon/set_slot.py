import time
from machine import Pin
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT

"""
Initialise the IO pins on a Yukon slot as outputs and set them.
"""

# Constants
SLEEP = 0.5         # The time to sleep between each reading

# Variables
yukon = Yukon()     # A new Yukon object

# Configure the slot pins as outputs with a low state
SLOT.FAST1.init(Pin.OUT, value=False)
SLOT.FAST2.init(Pin.OUT, value=False)
SLOT.FAST3.init(Pin.OUT, value=False)
SLOT.FAST4.init(Pin.OUT, value=False)
SLOT.SLOW1.init(Pin.OUT, value=False)
SLOT.SLOW2.init(Pin.OUT, value=False)
SLOT.SLOW3.init(Pin.OUT, value=False)

# Store the slot pins in a list for easier access
pins = [SLOT.FAST1, SLOT.FAST2, SLOT.FAST3, SLOT.FAST4,
        SLOT.SLOW1, SLOT.SLOW2, SLOT.SLOW3]
current_pin = 0

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Toggle the current slot pin
        pins[current_pin].toggle()

        # Advance the current pin, and wrap when the end of the list is reached
        current_pin = (current_pin + 1) % len(pins)

        # Read the output states of the slot pins
        state_f1 = SLOT.FAST1.value()
        state_f2 = SLOT.FAST2.value()
        state_f3 = SLOT.FAST3.value()
        state_f4 = SLOT.FAST4.value()
        state_s1 = SLOT.SLOW1.value()
        state_s2 = SLOT.SLOW2.value()
        state_s3 = SLOT.SLOW3.value()

        # Print out the pin states in a nice format
        print(f"F1 = {state_f1}", end=", ")
        print(f"F2 = {state_f2}", end=", ")
        print(f"F3 = {state_f3}", end=", ")
        print(f"F4 = {state_f4}", end=", ")
        print(f"S1 = {state_s1}", end=", ")
        print(f"S2 = {state_s2}", end=", ")
        print(f"S3 = {state_s3}")

        time.sleep(SLEEP)       # Sleep for a number of seconds

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
