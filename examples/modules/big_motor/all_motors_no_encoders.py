import math
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import BigMotorModule
from pimoroni_yukon.timing import ticks_ms, ticks_add
from motor import MotorCluster

"""
Drive up to 6 motors from a set of Big Motor + Encoder Modules connected to Slots, using a MotorCluster.
A wave pattern will be played on the attached motors.

Press "Boot/User" to exit the program.

The MotorCluster controls the whole set of motors using PIO.

Note: Is not possible to use more than 4 encoders whilst using a motor cluster, hence encoders being omitted from this example.
Attempting to do so causes a hard lock. This is likely a PIO program space limitation, though this needs to be investigated
"""

# Constants
SPEED = 0.005                           # How much to advance the motor phase offset by each update
UPDATES = 50                            # How many times to update the motors per second
SPEED_EXTENT = 1.0                      # How far from zero to drive the motors
CURRENT_LIMIT = 0.5                     # The maximum current (in amps) the motors will be driven with
WAVE_SCALE = 1.0                        # A scale to apply to the phase calculation to expand or contract the wave
CLUSTER_PIO = 0                         # The PIO system to use (0 or 1) to drive the motor cluster
CLUSTER_SM = 0                          # The State Machines (SM) to use to drive the motor cluster

# Variables
yukon = Yukon()                         # Create a new Yukon object
modules = []                            # A list to store QuadServo module objects created later
phase_offset = 0                        # The offset used to animate the motors


# Function to get a motor speed from its index
def speed_from_index(index, offset=0.0):
    phase = (((index * WAVE_SCALE) / BigMotorModule.NUM_MOTORS) + offset) * math.pi * 2
    speed = math.sin(phase) * SPEED_EXTENT
    return speed


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Find out which slots of Yukon have BigMotorModule attached
    for slot in yukon.find_slots_with(BigMotorModule):
        module = BigMotorModule(init_motor=False,       # Create a BigMotorModule object
                                init_encoder=False)
        yukon.register_with_slot(module, slot)          # Register the BigMotorModule object with the slot
        modules.append(module)                          # Add the object to the module list

    # Record the number of motors that will be driven
    NUM_MOTORS = len(modules) * BigMotorModule.NUM_MOTORS
    print(f"Up to {NUM_MOTORS} motors available")

    yukon.verify_and_initialise()                   # Verify that BigMotorModules are attached to Yukon, and initialise them

    # Create a MotorCluster object, with a list of motor pin pairs to control.
    # The pin list is created using list comprehension
    motors = MotorCluster(CLUSTER_PIO, CLUSTER_SM,
                          pins=[module.motor_pins for module in modules])

    yukon.enable_main_output()                      # Turn on power to the module slots

    for module in modules:
        module.enable()                             # Enable the motor driver on the BigMotorModule

    current_time = ticks_ms()                       # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Give all the motors new speeds
        for current_motor in range(motors.count()):
            speed = speed_from_index(current_motor, phase_offset)
            motors.speed(current_motor, speed)

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
