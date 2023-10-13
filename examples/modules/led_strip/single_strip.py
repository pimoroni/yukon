from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import LEDStripModule
from pimoroni_yukon.timing import ticks_ms, ticks_add
from pimoroni_yukon.logging import LOG_WARN

"""
How to drive a Neopixel or Dotstar LED strip with a LED Strip Module connected to Slot1.
A cycling rainbow pattern will be played on the attached strip(s).
"""

# Constants
STRIP_TYPE = LEDStripModule.NEOPIXEL    # Change to LEDStripModule.DOTSTAR for APA102 style strips
                                        # Two Neopixel strips can be driven too, by using LEDStripModule.DUAL_NEOPIXEL
STRIP_PIO = 0                           # The PIO system to use (0 or 1) to drive the strip(s)
STRIP_SM = 0                            # The State Machines (SM) to use to drive the strip(s)
LEDS_PER_STRIP = 60                     # How many LEDs are on the strip. If using DUAL_NEOPIXEL this can be a single value or a list or tuple
BRIGHTNESS = 1.0                        # The max brightness of the LEDs (only supported by APA102s)
SLEEP = 0.02                            # The time to sleep between each update
SPEED = 0.01                            # How much to advance the rainbow hue offset by each update
RAINBOW_SAT = 1.0                       # The saturation of the rainbow
RAINBOW_VAL = 1.0                       # The value (brightness) of the rainbow

# Variables
yukon = Yukon(logging_level=LOG_WARN)   # Create a new Yukon object, with its logging level lowered
module = LEDStripModule(STRIP_TYPE,     # Create a LEDStripModule object, with the details of the attached strip(s)
                        STRIP_PIO,
                        STRIP_SM,
                        LEDS_PER_STRIP,
                        BRIGHTNESS)
hue_offset = 0                          # The offset used to animate the rainbow


# Function for applying a rainbow pattern to an LED strip
def update_rainbow(strip, offset):
    for led in range(strip.num_leds()):
        # Calculate a hue for the LED based on its position in the strip and the offset
        hue = (led / strip.num_leds()) + offset
        strip.set_hsv(led, hue, RAINBOW_SAT, RAINBOW_VAL)

    # Send the new colours to the LED strip
    strip.update()


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)  # Register the LEDStripModule object with the slot
    yukon.verify_and_initialise()           # Verify that a LEDStripModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots
    module.enable()                         # Enable the LEDStripModule's onboard regulator

    current_time = ticks_ms()               # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        if STRIP_TYPE == LEDStripModule.DUAL_NEOPIXEL:
            # Update the rainbows of both Neopixel strips, if in that mode
            update_rainbow(module.strip1, hue_offset)
            update_rainbow(module.strip2, hue_offset)
        else:
            # Otherwise, just update the single Neopixel or Dotstar strip
            update_rainbow(module.strip, hue_offset)

        # Advance the hue offset, wrapping if it exceeds 1.0
        hue_offset += SPEED
        if hue_offset >= 1.0:
            hue_offset -= 1.0

        # Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(SLEEP * 1000))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updating of the rainbows taking a non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
