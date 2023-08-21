import time
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import LEDStripModule

STRIP_TYPE = LEDStripModule.NEOPIXEL  # change to LEDStripModule.DOTSTAR for APA102 style strips
SPEED = 2
LEDS_PER_STRIP = 60
BRIGHTNESS = 1.0

# Create a Yukon object to begin using the board
yukon = Yukon(logging_level=2)

# List to store the strips
strips = []


def update_rainbow(strip, offset):
    for px in range(strip.count()):
        rc_index = (px / strip.count()) + offset / 255
        strip.pixels.set_hsv(px, rc_index, 1.0, 1.0)

    strip.pixels.update()


try:
    # Create a LED Strip class for each populated module slot
    for slot in yukon.find_slots_with_module(LEDStripModule):
        strip = LEDStripModule(STRIP_TYPE, LEDS_PER_STRIP, BRIGHTNESS)
        yukon.register_with_slot(strip, slot)
        strips.append(strip)

    # Initialise Yukon's registered modules
    yukon.initialise_modules(allow_unregistered=True)

    # Turn on the module power
    yukon.enable_main_output()

    # Enable each strip module's regulator
    for strip in strips:
        strip.enable()

    offset = 0
    while not yukon.is_boot_pressed():
        start_time = time.ticks_ms()
        for strip in strips:
            update_rainbow(strip, offset)

        offset += SPEED
        if offset >= 255:
            offset -= 255

        yukon.monitor_until_ms(start_time + 100, excluded=("V_max", "V_min", "C_min", "C_avg", "T_min", "T_avg"))

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
