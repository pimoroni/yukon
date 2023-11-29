import time
from machine import Pin
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT

"""
This program reports the state of all slot IO along with the output
voltage, so that the addresses a module uses can be determined.

Power can be provided either through the XT30 connector,
or in via a slot, with the latter allowing for the discovery of
addresses at voltages below the e-Fuse's activation voltage.
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
SLOT.SLOW2.init(Pin.IN)
SLOT.SLOW3.init(Pin.IN)

# Turn on the main output
Pin.board.MAIN_EN.on()

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop until the BOOT/USER button is pressed
    while True:

        voltage_out = yukon.read_output_voltage(samples=2)

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
        adc1 = yukon.read_slot_adc1(SLOT, yukon.DETECTION_SAMPLES)
        adc2 = yukon.read_slot_adc2(SLOT, yukon.DETECTION_SAMPLES)

        # Print out the pin states in a nice format
        print(f"Vo = {int(voltage_out * 100000) / 100000}", end=",\t")
        print(f"F1 = {state_f1}", end=", ")
        print(f"F2 = {state_f2}", end=", ")
        print(f"F3 = {state_f3}", end=", ")
        print(f"F4 = {state_f4}", end=",\t\t")
        print(f"S1 = {state_s1}", end=", ")
        print(f"S2 = {state_s2}", end=", ")
        print(f"S3 = {state_s3}", end=",\t\t")
        print(f"A1 = {adc1}", end=", ")
        print(f"A2 = {adc2}")

        time.sleep(SLEEP)       # Sleep for a number of seconds

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
