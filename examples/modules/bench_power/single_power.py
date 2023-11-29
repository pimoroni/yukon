from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import BenchPowerModule

"""
Control the variable output of a Bench Power Module connected to Slot1,
and print out the voltage that is measured.

Press "A" to increase the output voltage.
Press "B" to decrease the output voltage.
Press "Boot/User" to exit the program.

Note: Due to variations in component values on the Bench Power module and Yukon
board itself, the measured voltage may over or under report what is actually output.
It is always best to verify the output voltage with a multimeter.
"""

# Constants
INITIAL_VOLTAGE = 5.0                       # The voltage to start the BenchPowerModule with
VOLTAGE_STEP = 0.1                          # How much to increase/decrease the voltage by each update loop
DELAY = 0.5                                 # The time to monitor before reading back what was measured

# Variables
yukon = Yukon()                             # Create a new Yukon object
module = BenchPowerModule()                 # Create a BenchPowerModule object
voltage = INITIAL_VOLTAGE                   # The voltage to have the BenchPowerModule output


# Function to monitor for a set duration, then print out the bench power's measured output voltage
def monitor_and_print(duration):
    global voltage
    global module
    yukon.monitored_sleep(duration)
    measured_avg = module.get_readings()["Vo_avg"]
    print(f"Target = {round(voltage, 3)} V, Measured = {round(measured_avg, 3)} V")


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)              # Register the BenchPowerModule object with the slot
    yukon.verify_and_initialise()                       # Verify that a BenchPowerModule is attached to Yukon, and initialise it

    yukon.enable_main_output()                          # Turn on power to the module slots
    module.set_voltage(voltage)                         # Set the initial voltage to output
    module.enable()                                     # Enable the BenchPowerModule's onboard regulator

    print()  # New line
    print("Controls:")
    print(f"- Press 'A' to increase the output voltage by {VOLTAGE_STEP}V")
    print(f"- Press 'B' to decrease the output voltage by {VOLTAGE_STEP}V")
    print()  # New line

    monitor_and_print(DELAY)                            # Monitor for the set duration, then print out the measured voltage

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
                voltage -= VOLTAGE_STEP                 # Decrease the voltage
                module.set_voltage(voltage)             # Set the new voltage to output

            # Has the B button been newly pressed?
            if state_b is True:
                voltage += VOLTAGE_STEP                 # Increase the voltage
                module.set_voltage(voltage)             # Set the new voltage to output

        monitor_and_print(DELAY)                        # Monitor for the set duration, then print out the measured voltage

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
