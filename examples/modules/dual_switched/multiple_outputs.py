import math
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import DualSwitchedModule
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
How to drive up to 12 powered outputs from a set of Dual Switched Modules connected to Slots.
A cycling pattern will be played on the attached outputs.
"""

# Constants
SPEED = 0.005                               # How much to advance the phase offset by each update
UPDATES = 50                                # How many times to update the outputs per second
TRIGGER_LEVEL = 0.0                         # The value the sinewave should be above to activate an output
WAVE_SCALE = 0.5                            # A scale to apply to the phase calculation to expand or contract the wave
VOLTAGE_LIMIT = 12.1                        # The voltage to not exceed, to protect the output

# Variables
yukon = Yukon(voltage_limit=VOLTAGE_LIMIT)  # Create a new Yukon object, with a lower voltage limit set
modules = []                                # A list to store DualMotorModule objects created later
phase_offset = 0                            # The offset used to animate the outputs


# Function to get an output state from its index
def state_from_index(index, offset=0.0):
    phase = (((index * WAVE_SCALE) / DualSwitchedModule.NUM_OUTPUTS) + offset) * math.pi * 2
    state = math.sin(phase) > TRIGGER_LEVEL
    return state


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Find out which slots of Yukon have DualMotorModule attached
    for slot in yukon.find_slots_with(DualSwitchedModule):
        module = DualSwitchedModule()           # Create a DualSwitchedModule object
        yukon.register_with_slot(module, slot)  # Register the DualSwitchedModule object with the slot
        modules.append(module)                  # Add the object to the module list

    # Record the number of outputs that will be driven
    NUM_OUTPUTS = len(modules) * DualSwitchedModule.NUM_OUTPUTS
    print(f"Up to {NUM_OUTPUTS} outputs available")

    yukon.verify_and_initialise()               # Verify that DualMotorModules are attached to Yukon, and initialise them
    yukon.enable_main_output()                  # Turn on power to the module slots

    for module in modules:
        for i in range(DualSwitchedModule.NUM_OUTPUTS):
            module.enable(i + 1)                # Enable each output driver

    current_time = ticks_ms()                   # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Give all the outputs new states
        current_output = 0
        for module in modules:
            for i in range(DualSwitchedModule.NUM_OUTPUTS):
                state = state_from_index(current_output, phase_offset)
                module.output(i + 1, state)
                current_output += 1

        # Advance the phase offset, wrapping if it exceeds 1.0
        phase_offset += SPEED
        if phase_offset >= 1.0:
            phase_offset -= 1.0

        print(f"Phase = {phase_offset}")

        # Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(1000 / UPDATES))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updating of the rainbows taking a non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
