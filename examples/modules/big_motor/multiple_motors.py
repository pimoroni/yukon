import math
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import BigMotorModule
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
How to drive up to 4 motors from a set of Big Motor + Encoder Modules connected to Slots.
A wave pattern will be played on the attached motors, and their speeds printed out.

To use more motors, look at the all_motors_no_encoders.py example.
"""

# Constants
SPEED = 0.005                   # How much to advance the motor phase offset by each update
UPDATES = 50                    # How many times to update the motors per second
SPEED_EXTENT = 1.0              # How far from zero to drive the motors
WAVE_SCALE = 1.0                # A scale to apply to the phase calculation to expand or contract the wave

# Variables
yukon = Yukon()                 # Create a new Yukon object
modules = []                    # A list to store BigMotorModule objects created later
phase_offset = 0                # The offset used to animate the motors


# Function to get a motor speed from its index
def speed_from_index(index, offset=0.0):
    phase = (((index * WAVE_SCALE) / BigMotorModule.NUM_MOTORS) + offset) * math.pi * 2
    speed = math.sin(phase) * SPEED_EXTENT
    return speed


# Generator to get the next PIO and State Machine numbers
def pio_and_sm_generator():
    pio = 0
    sm = 0
    while True:
        yield (pio, sm)     # Return the next pair of PIO and SM values

        sm += 1         # Advance by one SM

        # Wrap the SM and increment the PIO
        if sm > 3:
            sm -= 4
            pio += 1


pio_and_sm = pio_and_sm_generator()     # An instance of the generator

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Find out which slots of Yukon have BigMotorModule attached
    for slot in yukon.find_slots_with(BigMotorModule):
        pio, sm = next(pio_and_sm)                  # Get the next PIO and State Machine numbers
        module = BigMotorModule(encoder_pio=pio,    # Create a BigMotorModule object, with a specific PIO and SM for each encoder
                                encoder_sm=sm)
        yukon.register_with_slot(module, slot)      # Register the BigMotorModule object with the slot
        modules.append(module)                      # Add the object to the module list

    # Record the number of motors that will be driven
    NUM_MOTORS = len(modules) * BigMotorModule.NUM_MOTORS
    print(f"Up to {NUM_MOTORS} motors available")

    yukon.verify_and_initialise()                   # Verify that BigMotorModules are attached to Yukon, and initialise them
    yukon.enable_main_output()                      # Turn on power to the module slots

    for module in modules:
        module.enable()                             # Enable the motor driver on the BigMotorModule

    current_time = ticks_ms()                       # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Read all the encoders and give all the motors new speeds
        current_motor = 0
        for module in modules:
            capture = module.encoder.capture()      # Capture the state of the encoder
            print(f"RPS{current_motor} = {capture.revolutions_per_second}", end=", ")   # Print out the measured speed of the motor

            speed = speed_from_index(current_motor, phase_offset)
            module.motor.speed(speed)
            current_motor += 1
        print()

        # Advance the phase offset, wrapping if it exceeds 1.0
        phase_offset += SPEED
        if phase_offset >= 1.0:
            phase_offset -= 1.0

        # Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(1000 / UPDATES))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updating of the rainbows taking a non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
