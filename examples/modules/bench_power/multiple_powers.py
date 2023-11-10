import math
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import BenchPowerModule
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
Control up to 4 variable outputs from a set of Bench Power Modules connected to Slots.
A wave pattern will be played on the attached outputs.

Press "Boot/User" to exit the program.
"""

# Constants
SPEED = 0.005                               # How much to advance the phase offset by each update
UPDATES = 50                                # How many times to update the outputs per second
WAVE_SCALE = 0.25                           # A scale to apply to the phase calculation to expand or contract the wave
VOLTAGE_MIN = 3.0                           # The minimum voltage to cycle to
VOLTAGE_MAX = 12.0                          # The maximum voltage to cycle to

# Variables
yukon = Yukon()                             # Create a new Yukon object
modules = []                                # A list to store BenchPowerModule objects created later
phase_offset = 0                            # The offset used to animate the outputs


# Function to get an output voltage from its index
def voltage_from_index(index, offset=0.0):
    phase = ((index * WAVE_SCALE) + offset) * math.pi * 2
    percent = (math.sin(phase) / 2) + 0.5
    voltage = (percent * (VOLTAGE_MAX - VOLTAGE_MIN)) + VOLTAGE_MIN
    return voltage


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Find out which slots of Yukon have BenchPowerModule attached
    for slot in yukon.find_slots_with(BenchPowerModule):
        module = BenchPowerModule()             # Create a BenchPowerModule object
        yukon.register_with_slot(module, slot)  # Register the BenchPowerModule object with the slot
        modules.append(module)                  # Add the object to the module list

    # Record the number of outputs that will be driven
    NUM_OUTPUTS = len(modules)
    print(f"Up to {NUM_OUTPUTS} outputs available")

    yukon.verify_and_initialise()               # Verify that BenchPowerModules are attached to Yukon, and initialise them
    yukon.enable_main_output()                  # Turn on power to the module slots

    # Set all outputs to their starting voltages
    current_output = 0
    for module in modules:
        module.set_voltage(voltage_from_index(current_output))  # Set the initial voltage to output
        module.enable()                                         # Enable the BenchPowerModule's onboard regulator
        current_output += 1

    current_time = ticks_ms()                                   # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Give all the outputs new states
        current_output = 0
        for module in modules:
            module.set_voltage(voltage_from_index(current_output, phase_offset))    # Set the new voltage to output
            print(f"P{current_output} = {module.read_voltage()} V", end=", ")
            current_output += 1
        print()

        # Advance the phase offset, wrapping if it exceeds 1.0
        phase_offset += SPEED
        if phase_offset >= 1.0:
            phase_offset -= 1.0

        # Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(1000 / UPDATES))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updates takinga non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
