from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import SerialServoModule
from pimoroni_yukon.devices.lx_servo import LXServo

"""
Calibrate a serial servo's angle offset with Yukon's onboard buttons.
This uses a Serial Bus Servo module connected to Slot1.

Press "A" to increment the servo angle offset.
Press "B" to decrement the servo angle offset.
Press "Boot/User" to save the angle offset to the servo and exit the program.
"""

# Constants
SERVO_ID = 1                # The ID of the servo to control
VOLTAGE_LIMIT = 8.4         # The voltage to not exceed, to protect the servos
ANGLE_INCREMENT = 5         # The angle (in degrees) the servo will move to when button 'A' or 'B' are pressed
POWER_ON_DELAY = 1.0        # The time to sleep after turning on the power, for serial servos to power on
START_DURATION = 2.0        # The duration over which the servo will move to its starting angle
SAVE_DURATION = 0.5         # The duration to wait after sending a save command, for it to take effect

# Variables
yukon = Yukon(voltage_limit=VOLTAGE_LIMIT)      # Create a new Yukon object, with a lower voltage limit set
module = SerialServoModule()                    # Create a SerialServoModule object
last_button_states = {'A': False, 'B': False}   # The last states of the buttons
angle_offset = 0                                # The angle offset being tried


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
    yukon.verify_and_initialise(allow_unregistered=True)           # Verify that a SerialServoModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots

    yukon.monitored_sleep(POWER_ON_DELAY)   # Wait for serial servos to power up

    # Create an LXServo object to interact with the servo,
    # giving it access to the module's UART and Duplexer
    servo = LXServo(SERVO_ID, module.uart, module.duplexer)

    # Print out the initial angle offset stored on the servo
    print(f"Angle Offset: {servo.angle_offset()}")

    servo.move_to(0, START_DURATION)        # Move the servo to its starting angle
    yukon.monitored_sleep(START_DURATION)   # Wait for serial servos to move to their starting angles

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Has the A button been pressed?
        if button_newly_pressed('A'):
            angle_offset += ANGLE_INCREMENT
            servo.try_angle_offset(angle_offset)
            print(f"Trying Offset: {angle_offset}")
            yukon.set_led('A', True)        # Show that A was pressed
        else:
            yukon.set_led('A', False)       # A is no longer newly pressed

        # Has the B button been pressed?
        if button_newly_pressed('B'):
            angle_offset -= ANGLE_INCREMENT
            servo.try_angle_offset(angle_offset)
            print(f"Trying Offset: {angle_offset}")
            yukon.set_led('B', True)        # Show that B was pressed
        else:
            yukon.set_led('B', False)       # B is no longer newly pressed

        # Perform a single check of Yukon's internal voltage, current, and temperature sensors
        yukon.monitor_once()

    # Print out the angle offset stored on the servo
    print(f"Saving Angle Offset: {servo.angle_offset()}")

    servo.save_angle_offset()               # Save the angle offset back onto the servo
    yukon.monitored_sleep(START_DURATION)   # Give the serial servo some time to save the new offset

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
