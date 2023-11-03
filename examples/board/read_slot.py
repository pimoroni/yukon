import time
from machine import Pin
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT

"""
Read the IO pins of a single Yukon slot.

Press "Boot/User" to exit the program.
"""

# Constants
SLEEP = 0.5         # The time to sleep between each reading

# Variables
yukon = Yukon()     # A new Yukon object

# Configure the slot pins as inputs
SLOT.FAST1.init(Pin.IN)
SLOT.FAST2.init(Pin.IN)
SLOT.FAST3.init(Pin.IN)
SLOT.FAST4.init(Pin.IN)
SLOT.SLOW1.init(Pin.IN)
SLOT.SLOW1.init(Pin.IN)
SLOT.SLOW1.init(Pin.IN)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Read the slot's four 'Fast' pins
        state_f1 = SLOT.FAST1.value()
        state_f2 = SLOT.FAST2.value()
        state_f3 = SLOT.FAST3.value()
        state_f4 = SLOT.FAST4.value()

        # Read the slot's three 'Slow' pins. These have internal
        # pull-ups so will read 1 if left disconnected
        state_s1 = SLOT.SLOW1.value()
        state_s2 = SLOT.SLOW2.value()
        state_s3 = SLOT.SLOW3.value()

        # Read the slot's two analog pins
        adc1 = yukon.read_slot_adc1(SLOT)
        adc2 = yukon.read_slot_adc2(SLOT)

        # Print out the pin states in a nice format
        print(f"F1 = {state_f1}", end=", ")
        print(f"F2 = {state_f2}", end=", ")
        print(f"F3 = {state_f3}", end=", ")
        print(f"F4 = {state_f4}", end=", ")
        print(f"S1 = {state_s1}", end=", ")
        print(f"S2 = {state_s2}", end=", ")
        print(f"S3 = {state_s3}", end=", ")
        print(f"A1 = {adc1}", end=", ")
        print(f"A2 = {adc2}")

        time.sleep(SLEEP)       # Sleep for a number of seconds

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
