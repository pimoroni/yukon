import math
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import QuadServoDirectModule, QuadServoRegModule
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
Drive up to 16 servos from a set of Quad Servo Modules connected to Slots.
A wave pattern will be played on the attached servos.

Press "Boot/User" to exit the program.

To use more servos, or to reduce peak current draw, look at the all_servos.py example.
"""

# Constants
SPEED = 0.005                   # How much to advance the servo phase offset by each update
UPDATES = 50                    # How many times to update the servos per second
SERVO_EXTENT = 80.0             # How far from zero to move the servos
START_DELAY = 0.5               # The time to sleep between activating and animating the servos

# Variables
yukon = Yukon()                 # Create a new Yukon object
modules = []                    # A list to store QuadServo module objects created later
phase_offset = 0                # The offset used to animate the servos


# Function to get a servo angle from its index
def angle_from_index(index, offset=0.0):
    phase = ((index / NUM_SERVOS) + offset) * math.pi * 2
    angle = math.sin(phase) * SERVO_EXTENT
    return angle


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Find out which slots of Yukon have QuadServoDirectModules attached
    for slot in yukon.find_slots_with(QuadServoDirectModule):
        module = QuadServoDirectModule()        # Create a QuadServoDirectModule object
        yukon.register_with_slot(module, slot)  # Register the QuadServoDirectModule object with the slot
        modules.append(module)                  # Add the object to the module list

    # Find out which slots of Yukon have QuadServoRegModule attached
    for slot in yukon.find_slots_with(QuadServoRegModule):
        module = QuadServoRegModule()           # Create a QuadServoRegModule object
        yukon.register_with_slot(module, slot)  # Register the QuadServoDirectModule object with the slot
        modules.append(module)                  # Add the object to the module list

    # Record the number of servos that will be driven
    NUM_SERVOS = len(modules) * QuadServoDirectModule.NUM_SERVOS
    print(f"Up to {NUM_SERVOS} servos available")

    yukon.verify_and_initialise()               # Verify that QuadServo modules are attached to Yukon, and initialise them
    yukon.enable_main_output()                  # Turn on power to the module slots

    for module in modules:
        if hasattr(module, 'enable'):
            module.enable()                     # Enable each QuadServoRegModule's onboard regulator

    # Move all servos to their starting positions
    current_servo = 0
    for module in modules:
        for servo in module.servos:
            servo.value(angle_from_index(current_servo))
            yukon.monitored_sleep(START_DELAY)  # 'Sleep' for a short time for each servo to reach their position
                                                # This avoids them all drawing peak current at once
            current_servo += 1

    current_time = ticks_ms()                   # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Move all the servos to new values
        current_servo = 0
        for module in modules:
            for servo in module.servos:
                angle = angle_from_index(current_servo, phase_offset)
                servo.value(angle)
                current_servo += 1

        # Advance the phase offset, wrapping if it exceeds 1.0
        phase_offset += SPEED
        if phase_offset >= 1.0:
            phase_offset -= 1.0

        print(f"Phase = {phase_offset}")

        # Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(1000 / UPDATES))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updates takinga non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
