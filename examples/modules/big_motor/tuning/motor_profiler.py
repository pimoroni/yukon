from pimoroni import NORMAL_DIR  # , REVERSED_DIR
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import BigMotorModule

"""
Profile the speed of a motor across its PWM duty cycle range using its attached encoder for feedback.
This uses a Big Motor + Encoder Module connected to Slot1.

Note that the returned readings will only be valid for a single input voltage.
"""

# Constants
GEAR_RATIO = 30                         # The gear ratio of the motor
ENCODER_CPR = 12                        # The number of counts a single encoder shaft revolution will produce
MOTOR_CPR = GEAR_RATIO * ENCODER_CPR    # The number of counts a single motor shaft revolution will produce

DIRECTION = NORMAL_DIR                  # The direction to spin the motor in. NORMAL_DIR (0), REVERSED_DIR (1)
SPEED_SCALE = 3.4                       # The scaling to apply to the motor's speed. Set this to the maximum measured speed
ZERO_POINT = 0.0                        # The duty cycle that corresponds with zero speed when plotting the motor's speed as a straight line
DEAD_ZONE = 0.0                         # The duty cycle below which the motor's friction prevents it from moving

DUTY_STEPS = 100                        # How many duty cycle steps to sample the speed of
SETTLE_TIME = 0.1                       # How long to wait after changing motor duty cycle
CAPTURE_TIME = 0.2                      # How long to capture the motor's speed at each step

# Variables
yukon = Yukon()                                     # Create a new Yukon object
module = BigMotorModule(counts_per_rev=MOTOR_CPR)   # Create a BigMotorModule object

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)      # Register the BigMotorModule object with the slot
    yukon.verify_and_initialise()               # Verify that a BigMotorModule is attached to Yukon, and initialise it
    yukon.enable_main_output()                  # Turn on power to the module slots

    # Set the motor's speed scale, zeropoint, and deadzone
    module.motor.speed_scale(SPEED_SCALE)
    module.motor.zeropoint(ZERO_POINT)
    module.motor.deadzone(DEAD_ZONE)

    # Set the motor and encoder's direction
    module.motor.direction(DIRECTION)
    module.encoder.direction(DIRECTION)

    # Function that performs a single profiling step
    def profile_at_duty(motor, encoder, duty):
        # Set the motor to a new duty cycle and wait for it to settle
        if DIRECTION == 1:
            motor.duty(0.0 - duty)
        else:
            motor.duty(duty)
        yukon.monitored_sleep(SETTLE_TIME)

        # Perform a dummy capture to clear the encoder
        encoder.capture()

        # Wait for the capture time to pass
        yukon.monitored_sleep(CAPTURE_TIME)

        # Perform a capture and read the measured speed
        capture = encoder.capture()
        measured_speed = capture.revolutions_per_second

        # These are some alternate speed measurements from the encoder
        # measured_speed = capture.revolutions_per_minute
        # measured_speed = capture.degrees_per_second
        # measured_speed = capture.radians_per_second

        # Print out the expected and measured speeds, as well as their difference
        print("Duty =", motor.duty(), end=", ")
        print("Expected =", motor.speed(), end=", ")
        print("Measured =", measured_speed, end=", ")
        print("Diff =", motor.speed() - measured_speed)

    module.enable()             # Enable the motor driver on the BigMotorModule
    module.motor.enable()       # Enable the motor to get started

    print("Profiler Starting...")

    # Profile from 0% up to one step below 100%
    for i in range(DUTY_STEPS):
        profile_at_duty(module.motor, module.encoder, i / DUTY_STEPS)

    # Profile from 100% down to one step above 0%
    for i in range(DUTY_STEPS):
        profile_at_duty(module.motor, module.encoder, (DUTY_STEPS - i) / DUTY_STEPS)

    # Profile from 0% down to one step above -100%
    for i in range(DUTY_STEPS):
        profile_at_duty(module.motor, module.encoder, -i / DUTY_STEPS)

    # Profile from -100% up to one step below 0%
    for i in range(DUTY_STEPS):
        profile_at_duty(module.motor, module.encoder, -(DUTY_STEPS - i) / DUTY_STEPS)

    # Profile 0% again
    profile_at_duty(module.motor, module.encoder, 0)

    print("Profiler Finished...")

    # Disable the motor now the profiler has finished
    module.motor.disable()

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
