import math
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import SerialServoModule
from pimoroni_yukon.devices.lx_servo import LXServo
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
Move a set of serial servos attached to a set of Quad Servo Modules connected to Slots.
A wave pattern will be played on the attached servos.

Press "Boot/User" to exit the program.
"""

# Constants
VOLTAGE_LIMIT = 8.4             # The voltage to not exceed, to protect the servos
SPEED = 0.005                   # How much to advance the servo phase offset by each update
UPDATES = 50                    # How many times to update the servos per second
SERVO_EXTENT = 45.0             # How far from zero to move the servos
RESPONSE_TIMEOUT = 0.005        # How long to wait for a serial servo to respond
POWER_ON_DELAY = 1.0            # The time to sleep after turning on the power, for serial servos to power on
START_DURATION = 2.0            # The duration over which the servos will move to their starting angles

# Variables
yukon = Yukon()                 # Create a new Yukon object
modules = []                    # A list to store SerialServoModule objects created later
servos = []                     # A list to store LXServo objects created later
phase_offset = 0                # The offset used to animate the servos


# Function to get a servo angle from its index
def angle_from_index(index, offset=0.0):
    phase = ((index / NUM_SERVOS) + offset) * math.pi * 2
    angle = math.sin(phase) * SERVO_EXTENT
    return angle


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Find out which slots of Yukon have QuadServoDirectModules attached
    for slot in yukon.find_slots_with(SerialServoModule):
        module = SerialServoModule()        # Create a SerialServoModule object
        yukon.register_with_slot(module, slot)  # Register the SerialServoModule object with the slot
        modules.append(module)                  # Add the object to the module list

    yukon.verify_and_initialise()               # Verify that QuadServo modules are attached to Yukon, and initialise them
    yukon.enable_main_output()                  # Turn on power to the module slots

    yukon.monitored_sleep(POWER_ON_DELAY)       # Wait for serial servos to power up

    # Go through each servo ID
    for module in modules:
        for servo_id in range(0, LXServo.BROADCAST_ID):
            # Is there a servo with the current ID?
            if LXServo.detect(servo_id, module.uart, module.duplexer, timeout=RESPONSE_TIMEOUT):
                servo = LXServo(servo_id, module.uart, module.duplexer)
                servos.append(servo)                # Add the object to the servo list

    # Record the number of servos that will be driven
    NUM_SERVOS = len(servos)
    print(f"{NUM_SERVOS} servos available")

    # Move all servos to their starting positions
    current_servo = 0
    for servo in servos:
        servo.move_to(angle_from_index(current_servo), START_DURATION)
        current_servo += 1

    yukon.monitored_sleep(START_DURATION)       # Wait for serial servos to move to their starting angles

    current_time = ticks_ms()                   # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Move all the servos to new values
        current_servo = 0
        for servo in servos:
            angle = angle_from_index(current_servo, phase_offset)
            servo.move_to(angle, 1.0 / UPDATES)
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
