import time
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import DualSwitchedModule

# The name of the output. In this case it is connected to a 12V LED
OUTPUT_NAME = "Light"

# Select the slot that the module is installed in, and the output the LED is connected to
SLOT = 1
OUTPUT = 1
TOGGLE_TIME = 2.5

# Create a Yukon object to begin using the board, and a set a voltage limit just above what the LED is rated for
yukon = Yukon(voltage_limit=12.1)

try:
    # Create a DualSwitchedModule and register it with a slot on Yukon
    switches = DualSwitchedModule()
    yukon.register_with_slot(switches, SLOT)

    # Initialise Yukon's registered modules
    yukon.initialise_modules(allow_unregistered=True)

    # Turn on the module power
    yukon.enable_main_output()

    # Enable only switched output 1
    switches.enable(OUTPUT)

    while not yukon.is_boot_pressed():
        new_state = not switches.read_output(OUTPUT)
        switches.output(OUTPUT, new_state)
        if new_state:
            print(f"{OUTPUT_NAME} = On")
        else:
            print(f"{OUTPUT_NAME} = Off")

        # Use the Yukon class to sleep, which lets it monitor voltage, current, and temperature
        yukon.monitored_sleep(TOGGLE_TIME)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
