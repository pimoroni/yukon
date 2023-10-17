import math
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import QuadServoDirectModule
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
How to read the analog inputs on Quad Servo Direct modules connected to Slots.
"""

# Constants
SLEEP = 0.5         # The time to sleep between each reading
SAMPLES = 1         # How many times each input should be sampled. Increasing this will reduce noise but take longer to run

# Variables
yukon = Yukon()                 # Create a new Yukon object
modules = []                    # A list to store QuadServo module objects created later


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Find out which slots of Yukon have QuadServoDirectModules attached
    for slot in yukon.find_slots_with(QuadServoDirectModule):
        module = QuadServoDirectModule()        # Create a QuadServoDirectModule object
        yukon.register_with_slot(module, slot)  # Register the QuadServoDirectModule object with the slot
        modules.append(module)                  # Add the object to the module list

    # Record the number of servos that will be driven
    NUM_SERVOS = len(modules) * QuadServoDirectModule.NUM_SERVOS
    print(f"Up to {NUM_SERVOS} servos available")

    yukon.verify_and_initialise()               # Verify that QuadServo modules are attached to Yukon, and initialise them
    yukon.enable_main_output()                  # Turn on power to the module slots

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Read all the sensors and print out their values
        for index, module in enumerate(modules):
            print(f"[M{index}] A1 = {module.read_adc1()}, A2 = {module.read_adc2()}", end=", ")
        print()

        # Monitor sensors for a number of seconds, recording the min, max, and average for each
        yukon.monitored_sleep(SLEEP)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
