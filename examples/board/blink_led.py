import time
from pimoroni_yukon import Yukon

"""
Blink one of Yukon's onboard LEDs.

Press "Boot/User" to exit the program.
"""

# Constants
LED = 'A'      # Accepted values are 0, 1, 'A', or 'B'
SLEEP = 0.5    # The time to sleep between each toggle

# Variables
yukon = Yukon()     # A new Yukon object
led_state = False   # The state of the LED

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        led_state = not led_state       # Toggle the LED state
        yukon.set_led(LED, led_state)   # Set the LED to the new state

        time.sleep(SLEEP)               # Sleep for a number of seconds

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
