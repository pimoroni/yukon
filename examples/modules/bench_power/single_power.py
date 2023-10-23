from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import BenchPowerModule

"""
How to control the variable output of a Bench Power Module connected to Slot1.
"""

# Constants
INITIAL_VOLTAGE = 5.0                       # The voltage to start the BenchPowerModule with
VOLTAGE_STEP = 0.1                          # How much to increase/decrease the voltage by each update loop
DELAY = 0.2                                 # The time to sleep after setting a new voltage before it can be read back
SAMPLES = 100                               # How many voltage readings to take to produce an average

# Variables
yukon = Yukon()                             # Create a new Yukon object
module = BenchPowerModule()                 # Create a BenchPowerModule object
voltage = INITIAL_VOLTAGE                   # The voltage to have the BenchPowerModule output


# Function to print out the target and measured voltages
def print_voltages():
    global voltage
    global module
    yukon.monitored_sleep(DELAY)
    measured = module.read_voltage(SAMPLES)                   # Measure the voltage that is actually being output
    print(f"Target = {voltage} V, Measured = {measured} V")   # Print out intended and measured voltages


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)              # Register the BenchPowerModule object with the slot
    yukon.verify_and_initialise()                       # Verify that a BenchPowerModule is attached to Yukon, and initialise it

    yukon.enable_main_output()                          # Turn on power to the module slots
    module.set_voltage(voltage)                         # Set the initial voltage to output
    module.enable()                                     # Enable the BenchPowerModule's onboard regulator
    print_voltages()                                    # Print out the new voltages

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Read the state of the onboard buttons
        state_a = yukon.is_pressed('A')
        state_b = yukon.is_pressed('B')
        
        # Have the LEDs mirror the button states to show the program is working
        yukon.set_led('A', state_a)
        yukon.set_led('B', state_b)

        if state_a != state_b:
            # Has the A button been newly pressed?
            if state_a is True:
                voltage -= 0.1                                  # Decrease the voltage
                module.set_voltage(voltage)                     # Set the new voltage to output
                print_voltages()                                # Print out the new voltages

            # Has the B button been newly pressed?
            if state_b is True:
                voltage += 0.1                                  # Increase the voltage
                module.set_voltage(voltage)                     # Set the new voltage to output
                print_voltages()                                # Print out the new voltages

        # Perform a single check of Yukon's internal voltage, current, and temperature sensors
        yukon.monitor_once()

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
