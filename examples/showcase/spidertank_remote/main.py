import time
import math
import bluetooth
import btclassic
import pad_keys
from machine import Pin
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT5 as LEFT_SLOT
from pimoroni_yukon import SLOT2 as RIGHT_SLOT
from pimoroni_yukon import SLOT4 as WIRELESS_SLOT
from pimoroni_yukon import SLOT3 as BUZZER_SLOT
from pimoroni_yukon.modules import SerialServoModule, RM2WirelessModule
from pimoroni_yukon.devices.lx_servo import LXServo
from pimoroni_yukon.timing import ticks_ms, ticks_add, ticks_diff
from pimoroni_yukon.logging import LOG_WARN
from leg_ik import Vector3, calculate_ik_3dof, Limits, rotate_y
from gamepad_mappings import create_8bitdo_sn30_pro_plus_xinput

"""
A showcase of Yukon as a hexapod robot, with 3 degrees of freedom per leg.
It uses two Serial Bus Servo modules, one to control the left side servos,
and the other to control the right side servos.

There is also a proto module wired up to a buzzer to alert the user to the
battery voltage getting too low, and a RM2 Wireless Module for reaching the game pad.

The program performs inverse kinematics for each leg, with the target
points following a tripod walking gait. The pad's right trigger sets how fast that gait
plays, from standing still to full speed, so the walk is driven by hand.

The first time, put the pad into pairing mode and Yukon finds it, pairs, and saves the link
key to a file on the board. From then on switching the pad on is enough. LED A is lit whenever
the spider tank is waiting for the pad, and it stands still while it is.

Press "Boot/User" to exit the program, only if the buzzer is not sounding.
If the buzzer sounds, disconnect power as soon as possible!
"""

# Constants
UPDATES = 20                        # How many times to update the servos per second
TIMESTEP = 1 / UPDATES
TIMESTEP_MS = int(TIMESTEP * 1000)
POWER_ON_DELAY = 1.0                # The time to sleep after turning on the power, for serial servos to power on
LOW_VOLTAGE_LEVEL = 6.8             # The voltage below which the program will terminate and start the buzzer
BUZZER_PERIOD = 0.5                 # The time between each buzz of the low voltage alarm
BUZZER_DUTY = 0.5                   # The percentage of the time that the buzz will be on for
PRINT_LEG = 1                       # Which leg to debug print the angles of
SERVO_ATTEMPTS = 5                  # How many times to ask a servo to identify itself before giving up

PAD_MAPPING = create_8bitdo_sn30_pro_plus_xinput    # The mapping function for the pad in use, see gamepad_mappings.py
SPEED_AXIS = "R2"                   # The pad control that sets how fast the gait plays
INQUIRY_SECONDS = 8                 # How long to look for a pad in pairing mode when none is stored
CONNECT_TIMEOUT_MS = 20000          # How long to give a connection attempt before trying again
RETRY_INTERVAL_MS = 5000            # How long to wait between attempts to reach a stored pad
GAMEPAD_CLASS = 0x05                # The major device class that game pads report in an inquiry
SUPERVISION_MS = 2000               # How long a silent pad may hold the link before it counts as gone

# Servo IDs  LF  LM  LR  RF  RM  RR
COXA_IDS =  ( 6,  5,  4,  1,  2,  3)
FEMUR_IDS = (12, 11, 10,  7,  8,  9)
TIBIA_IDS = (18, 17, 16, 13, 14, 15)

# Walk Parameters
NUM_LEGS = 6
FORWARD_EXTENT = 70                 # How far from zero to move the legs (in mm) in the forward/backward axis
SIDE_EXTENT = 0                     # How far from zero to move the legs (in mm) in the left/right axis
HEIGHT_EXTENT = 40                  # How far from zero to move the legs (in mm) in the up/down axis
BODY_HEIGHT = 130                   # The height of the body (in mm) above the ground
CYCLE_DURATION = 0.5                # The duration of each walk cycle

# Leg Parameters
COXA_LENGTH = 45                    # The length of each leg's coxa (in mm)
FEMUR_LENGTH = 75                   # The length of each leg's femur (in mm)
TIBIA_LENGTH = 130                  # The length of each leg's tibia (in mm)
COXA_LIMITS = Limits(-50, 50)       # The allowed angle range of each leg's coxa (in degrees)
FEMUR_LIMITS = Limits(-20, 100)      # The allowed angle range of each leg's femur (in degrees)
TIBIA_LIMITS = Limits(30, 150)       # The allowed angle range of each leg's tibia (in degrees)

# The origin position of each leg on the body
LEG_ORIGINS = [Vector3(-58.75, BODY_HEIGHT,  120),  # LF (mm)
               Vector3(-92,    BODY_HEIGHT,  0),    # LM (mm)
               Vector3(-58.75, BODY_HEIGHT, -120),  # LR (mm)
               Vector3(58.75,  BODY_HEIGHT,  120),  # RF (mm)
               Vector3(92,     BODY_HEIGHT,  0),    # RM (mm)
               Vector3(58.75,  BODY_HEIGHT, -120)]  # RR (mm)

# The target positions each leg will touch when idle
LEG_TARGETS = [Vector3(-160, 0,  200),  # LF (mm)
               Vector3(-200, 0,  0),    # LM (mm)
               Vector3(-160, 0, -200),  # LR (mm)
               Vector3( 160, 0,  200),  # RF (mm)
               Vector3( 200, 0,  0),    # RM (mm)
               Vector3( 160, 0, -200)]  # RR (mm)

#                 LF  LM   LR   RF   RM    RR
LEG_ANGLES =     (45, 90, 135, -45, -90, -135)  # The angle each leg is attached to the body
LEG_SIDES =      ( 0,  0,   0,   1,   1,    1)  # The side each leg is on (0 for left, 1 for right)
STRIDE_PATTERN = (-1, +1,  -1,  +1,  -1,   +1)  # The stride each leg is associated with (either +1 or -1)

# Variables
yukon = Yukon(logging_level=LOG_WARN)      # Create a Yukon object with the logging level set to warnings to reduce print outputs
left_module = SerialServoModule()          # Create the left side SerialServoModule object
right_module = SerialServoModule()         # Create the right side SerialServoModule object
wireless_module = RM2WirelessModule()      # Create a RM2WirelessModule object, which checks this is a wireless build
buzzer = BUZZER_SLOT.FAST3                 # The pin the low voltage buzzer is attached to

ble = bluetooth.BLE()                      # The Bluetooth stack, which must be active before btclassic is used

pad = PAD_MAPPING()                        # The pad's controls, decoded from its reports
known = []                                 # The addresses of the pads that have been paired with
next_pad = 0                               # Which stored pad to page next, when more than one is stored
last_attempt = None                        # When a stored pad was last paged

coxa_servos = []                           # A list to store coxa LXServo objects created later
femur_servos = []                          # A list to store femur LXServo objects created later
tibia_servos = []                          # A list to store tibia LXServo objects created later
cycle_percent = 0                          # The percent through the walking cycle
exited_due_to_low_voltage = True           # Record if the program exited due to low voltage (assume true to start)


def address_text(address):
    return ":".join("%02X" % b for b in address)


def find_pad_in_pairing_mode():
    """Look for a discoverable pad and return its address, or None."""
    print("Looking for a pad in pairing mode ...")
    btclassic.inquiry_start(INQUIRY_SECONDS)
    while btclassic.inquiry_active():
        time.sleep_ms(100)
    for address, device_class, rssi, name in btclassic.inquiry_results():
        if (device_class >> 8) & 0x1F == GAMEPAD_CLASS:
            print("Found", name or "a pad", "at", address_text(address))
            return address
    print("No pad found")
    return None


def wait_for_connection():
    """Wait for a connection attempt to finish, returning whether it succeeded."""
    start = ticks_ms()
    while btclassic.state()[0] == btclassic.STATE_CONNECTING:
        if ticks_diff(ticks_ms(), start) > CONNECT_TIMEOUT_MS or yukon.is_boot_pressed():
            return False
        time.sleep_ms(50)
    return btclassic.state()[0] == btclassic.STATE_CONNECTED


def reach_for_pad():
    """Take one step towards having a pad connected.

    A pad switched on pages Yukon by itself, so a stored one only has to be paged when it lost
    Yukon while staying on. A pad that has never been paired is found in pairing mode instead.
    """
    global known, next_pad, last_attempt

    if btclassic.state()[0] == btclassic.STATE_CONNECTING:
        return

    if not known:
        address = find_pad_in_pairing_mode()
        # An inquiry takes seconds, in which the pad may have reached us of its own accord
        if address is None or btclassic.state()[0] == btclassic.STATE_CONNECTED:
            return
        btclassic.connect(address)
        if wait_for_connection():
            pad_keys.save()
            known = pad_keys.load()
            print("Paired and saved. From now on just switch the pad on.")
        return

    if last_attempt is None or ticks_diff(ticks_ms(), last_attempt) > RETRY_INTERVAL_MS:
        last_attempt = ticks_ms()
        btclassic.connect(known[next_pad])
        next_pad = (next_pad + 1) % len(known)


def make_servo(servo_id, module):
    """Create a servo, retrying the identification read.

    The bus is half duplex, and its timing occasionally garbles the reply, so a servo that is
    present and healthy can fail to report its ID on any given attempt.
    """
    for attempt in range(SERVO_ATTEMPTS):
        try:
            return LXServo(servo_id, module.uart, module.duplexer)
        except RuntimeError:
            if attempt == SERVO_ATTEMPTS - 1:
                raise
            time.sleep_ms(20)


# Calculate target displacements from extents and the percent through a walking cycle
def extent_to_displacements(x_extent, z_extent, percent):
    if percent < 0.5:
        x_disp = ((cycle_percent * 2) * (x_extent * 2)) - x_extent
        z_disp = ((cycle_percent * 2) * (z_extent * 2)) - z_extent
    else:
        x_disp = x_extent - (((cycle_percent - 0.5) * 2) * (x_extent * 2))
        z_disp = z_extent - (((cycle_percent - 0.5) * 2) * (z_extent * 2))
    return x_disp, z_disp


# Ensure the input voltage is above the low level
if yukon.read_input_voltage() > LOW_VOLTAGE_LEVEL:
    exited_due_to_low_voltage = False

    # Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
    try:
        # Register the SerialServoModule objects with their respective slots
        yukon.register_with_slot(left_module, LEFT_SLOT)
        yukon.register_with_slot(right_module, RIGHT_SLOT)
        yukon.register_with_slot(wireless_module, WIRELESS_SLOT)

        yukon.verify_and_initialise()           # Verify that the modules are attached to Yukon, and initialise them

        ble.active(True)                        # Bring up the Bluetooth stack

        # A pad only reports when a control moves, so a held trigger and a pad that has gone look
        # alike. Shortening the link supervision timeout is what tells them apart, and it decides
        # how long the gait can keep playing on the last thing it was told.
        btclassic.supervision_timeout(SUPERVISION_MS)

        known = pad_keys.load()                 # Put any saved link keys back into the stack
        btclassic.connectable(True)             # Now let pads connect to us
        if known:
            print("Stored pads:", ", ".join(address_text(address) for address in known))

        yukon.enable_main_output()              # Turn on power to the module slots

        yukon.monitored_sleep(POWER_ON_DELAY)   # Wait for serial servos to power up

        # Create LXServo objects for each leg and add them to their respective lists
        for i in range(NUM_LEGS):
            module = right_module if LEG_SIDES[i] == 1 else left_module
            coxa_servos.append(make_servo(COXA_IDS[i], module))
            femur_servos.append(make_servo(FEMUR_IDS[i], module))
            tibia_servos.append(make_servo(TIBIA_IDS[i], module))

        current_time = ticks_ms()               # Record the start time of the program loop

        # Loop until the BOOT/USER button is pressed
        while not yukon.is_boot_pressed():

            # Read how fast the gait should play, standing still without a pad to ask
            if pad.is_connected():
                yukon.set_led('A', False)
                pad.update()
                speed = pad.read_axis(SPEED_AXIS)
            else:
                yukon.set_led('A', True)
                pad.reset()
                reach_for_pad()
                speed = 0.0

            # Calculate how far to offset each leg target in x, y and z
            target_displacements = extent_to_displacements(SIDE_EXTENT, FORWARD_EXTENT, cycle_percent)
            target_height = math.sin(cycle_percent * math.pi * 2) * HEIGHT_EXTENT

            # Go through each leg and perform their part of the walkng
            for i in range(NUM_LEGS):
                # Create a copy of the current leg's target position
                target = Vector3(LEG_TARGETS[i].x, LEG_TARGETS[i].y, LEG_TARGETS[i].z)

                # Modify the target by the displacement and height, based on which pattern it should follow
                target.x += target_displacements[0] * STRIDE_PATTERN[i]
                target.z += target_displacements[1] * STRIDE_PATTERN[i]
                target.y += target_height * STRIDE_PATTERN[i]
                target.y = max(target.y, 0.0)   # Prevent the target Y from going negative, to produce smooth walking

                # Calculate the position of each leg's target, relative to its origin, accounting for its angle
                origin_to_target = rotate_y(target - LEG_ORIGINS[i], LEG_ANGLES[i])

                # Calculate the inverse kinematics for this style of 3 degrees of freedom leg
                coxa_angle, femur_angle, tibia_angle = calculate_ik_3dof(origin_to_target, COXA_LENGTH, FEMUR_LENGTH, TIBIA_LENGTH,
                                                                         COXA_LIMITS, FEMUR_LIMITS, TIBIA_LIMITS)

                # Print out the angles of a single leg
                if i == PRINT_LEG:
                    print(f"C{i} = {coxa_angle}, F{i} = {femur_angle}, T{i} = {tibia_angle}", end=", ")

                # Send the calculated angles to each serial servo
                coxa_servos[i].move_to(0.0 - coxa_angle, TIMESTEP)
                if LEG_SIDES[i] == 1:
                    femur_servos[i].move_to(femur_angle, TIMESTEP)
                    tibia_servos[i].move_to(90.0 - tibia_angle, TIMESTEP)
                else:
                    femur_servos[i].move_to(0.0 - femur_angle, TIMESTEP)
                    tibia_servos[i].move_to(0.0 - (90.0 - tibia_angle), TIMESTEP)

            # Advance the cycle percent, based on the timestep, the cycle time, and how far the
            # trigger is pulled. At rest the cycle stops where it is and the legs hold their pose.
            cycle_percent += (TIMESTEP / CYCLE_DURATION) * speed
            if cycle_percent >= 1.0:
                cycle_percent -= 1.0

            # Advance the current time by a number of milliseconds
            current_time = ticks_add(current_time, TIMESTEP_MS)

            # Monitor sensors until the current time is reached, recording the min, max, and average for each
            # This approach accounts for the updates taking a non-zero amount of time to complete
            yukon.monitor_until_ms(current_time)

            # Get the average voltage recorded from monitoring, and print it out
            avg_voltage = yukon.get_readings()["Vi_avg"]
            print(f"V = {avg_voltage}")

            # Check if the average input voltage was below the low voltage level
            if avg_voltage < LOW_VOLTAGE_LEVEL:
                exited_due_to_low_voltage = True
                break           # Break out of the loop

    finally:
        btclassic.disconnect()      # Leave the pad disconnected rather than holding a link to nothing
        ble.active(False)

        # Put the board back into a safe state, regardless of how the program may have ended
        yukon.reset()
else:
    print(f"> Input voltage below {LOW_VOLTAGE_LEVEL}V!")

# Was the exit caused by the input voltage dropping too low
if exited_due_to_low_voltage:
    buzzer.init(Pin.OUT)    # Set up the buzzer pin as an output

    yukon.set_led('A', True)
    while True:
        # Toggle the buzzer on and off repeatedly
        buzzer.on()
        time.sleep(BUZZER_PERIOD * BUZZER_DUTY)
        buzzer.off()
        time.sleep(BUZZER_PERIOD * (1.0 - BUZZER_DUTY))
