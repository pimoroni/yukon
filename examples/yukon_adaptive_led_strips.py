from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import LEDStripModule
from pimoroni_yukon.timing import ticks_ms, ticks_add

STRIP_TYPE = LEDStripModule.NEOPIXEL  # change to LEDStripModule.DOTSTAR for APA102 style strips
SPEED = 2
LEDS_PER_STRIP = 60
BRIGHTNESS = 1.0

# Create a Yukon object to begin using the board
yukon = Yukon(logging_level=2)

# List to store the strip modules
modules = []


def update_rainbow(strip, offset):
    for px in range(strip.num_leds()):
        rc_index = (px / strip.num_leds()) + offset / 255
        strip.set_hsv(px, rc_index, 1.0, 1.0)

    strip.update()


try:
    # Create a LED Strip class for each populated module slot
    for slot in yukon.find_slots_with_module(LEDStripModule):
        module = LEDStripModule(STRIP_TYPE, LEDS_PER_STRIP, BRIGHTNESS)
        yukon.register_with_slot(module, slot)
        modules.append(module)

    # Initialise Yukon's registered modules
    yukon.initialise_modules()

    # Turn on the module power
    yukon.enable_main_output()

    # Enable each strip module's regulator
    for module in modules:
        module.enable()

    offset = 0
    while not yukon.is_boot_pressed():
        start_time = ticks_ms()
        for module in modules:
            if STRIP_TYPE == LEDStripModule.DUAL_NEOPIXEL:
                update_rainbow(module.strip1, offset)
                update_rainbow(module.strip2, offset)
            else:
                update_rainbow(module.strip, offset)

        offset += SPEED
        if offset >= 255:
            offset -= 255

        start_time = ticks_add(start_time, 100)
        yukon.monitor_until_ms(start_time)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
