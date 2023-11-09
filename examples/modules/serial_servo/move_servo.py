from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import SerialServoModule
from pimoroni_yukon.devices.lx_servo import LXServo
from pimoroni_yukon.timing import ticks_ms, ticks_add

"""
Move a servo between two angles with Yukon's onboard buttons.
This uses a Serial Bus Servos module connected to Slot1.

Press "A" to move the servo to the first angle.
Press "B" to move the servo to the second angle.
Press "Boot/User" to exit the program.
"""

# Constants
SERVO_ID = 1                # The ID of the servo to control
VOLTAGE_LIMIT = 8.4         # The voltage to not exceed, to protect the servos
ANGLE_A = -45               # The angle (in degrees) the servo will move to when button 'A' is pressed
ANGLE_B = 45                # The angle (in degrees) the servo will move to when button 'B' is pressed
MOVEMENT_DURATION = 1.0     # The time (in seconds) the servo will perform the movements over
SLEEP = 0.1                 # The time to sleep between each update

# Variables
yukon = Yukon(voltage_limit=VOLTAGE_LIMIT)  # Create a new Yukon object, with a lower voltage limit set
module = SerialServoModule()                # Create a SerialServoModule object
last_button_states = {'A': False, 'B': False}   # The last states of the buttons


# Function to check if the button has been newly pressed
def button_newly_pressed(btn):
    global last_button_states
    button_state = yukon.is_pressed(btn)
    button_pressed = button_state and not last_button_states[btn]
    last_button_states[btn] = button_state

    return button_pressed


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)  # Register the SerialServoModule object with the slot
    yukon.verify_and_initialise()           # Verify that a SerialServoModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots

    yukon.monitored_sleep(1)                # Wait for serial servos to power up

    # Create an LXServo object to interact with the servo,
    # giving it access to the module's UART and Duplexer
    servo = LXServo(SERVO_ID, module.uart, module.duplexer)

    current_time = ticks_ms()               # Record the start time of the program loop

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Has the A button been pressed?
        if button_newly_pressed('A'):
            servo.move_to(ANGLE_A, MOVEMENT_DURATION)
            yukon.set_led('A', True)        # Show that A was pressed
        else:
            yukon.set_led('A', False)       # A is no longer newly pressed

        # Has the B button been pressed?
        if button_newly_pressed('B'):
            servo.move_to(ANGLE_B, MOVEMENT_DURATION)
            yukon.set_led('B', True)        # Show that B was pressed
        else:
            yukon.set_led('B', False)       # B is no longer newly pressed

        # Print out sensor readings from the servo
        print(f"Angle: {servo.read_angle()}, Vin: {servo.read_voltage()}, Temp: {servo.read_temperature()}")

        # Advance the current time by a number of seconds
        current_time = ticks_add(current_time, int(SLEEP * 1000))

        # Monitor sensors until the current time is reached, recording the min, max, and average for each
        # This approach accounts for the updating of the rainbows taking a non-zero amount of time to complete
        yukon.monitor_until_ms(current_time)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
