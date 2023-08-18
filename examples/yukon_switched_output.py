import time
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import DualSwitchedModule

# The name of the two outputs. In this case they are connected to 12V PC Fans
OUTPUT_1_NAME = "Small Fan"
OUTPUT_2_NAME = "Big Fan"

# Select the slot that the module is installed in
SLOT = 1

# Create a Yukon object to begin using the board, and a set a voltage limit just above what the fans are rated for
yukon = Yukon(voltage_limit=12.1, logging_level=3)

try:
    # Create a DualSwitchedModule and register it with a slot on Yukon
    switches = DualSwitchedModule()
    yukon.register_with_slot(switches, SLOT)

    # Initialise Yukon's registered modules
    yukon.initialise_modules(allow_unregistered=True)

    # Turn on the module power
    yukon.enable_main_output()

    # Enable the switched outputs
    switches.enable(1)
    switches.enable(2)

    offset = 0
    sw_a_state = False
    sw_b_state = False
    last_sw_a_state = False
    last_sw_b_state = False
    while not yukon.is_boot_pressed():
        sw_a_state = yukon.is_pressed('A')
        sw_b_state = yukon.is_pressed('B')

        if sw_a_state is True and sw_a_state != last_sw_a_state:
            new_state = not switches.read_output(1)
            switches.output(1, new_state)
            yukon.set_led('A', new_state)
            if new_state:
                print(f"{OUTPUT_1_NAME} = On")
            else:
                print(f"{OUTPUT_1_NAME} = Off")

        if sw_b_state is True and sw_b_state != last_sw_b_state:
            new_state = not switches.read_output(2)
            switches.output(2, new_state)
            yukon.set_led('B', new_state)
            if new_state:
                print(f"{OUTPUT_2_NAME} = On")
            else:
                print(f"{OUTPUT_2_NAME} = Off")

        last_sw_a_state = sw_a_state
        last_sw_b_state = sw_b_state

        # Use the Yukon class to sleep, which lets it monitor voltage, current, and temperature
        yukon.monitored_sleep(0.1)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
