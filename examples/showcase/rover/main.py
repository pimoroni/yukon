import time
import bluetooth
import btclassic
import pad_keys
from machine import Pin
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT6 as LEFT_SLOT
from pimoroni_yukon import SLOT1 as RIGHT_SLOT
from pimoroni_yukon import SLOT5 as LED_SLOT
from pimoroni_yukon import SLOT4 as WIRELESS_SLOT
from pimoroni_yukon import SLOT3 as BUZZER_SLOT
from pimoroni_yukon.modules import BigMotorModule, LEDStripModule, RM2WirelessModule
from pimoroni_yukon import ticks_ms, ticks_add, ticks_diff
from pimoroni_yukon.logging import LOG_WARN
from gamepad_mappings import create_8bitdo_sn30_pro_plus_xinput
from controls import triggers, sticks, mix

"""
A showcase of Yukon as a differential drive rover.
It uses two Big Motor modules, one to control the left side motors,
and the other to control the right side motors.

There is a LED Strip module controlling left and right strips that represent
each side's speed as a colour from green -> blue -> red. Additionally, there is
a proto module wired up to a buzzer to alert the user to the battery voltage getting
too low, and a RM2 Wireless Module for reaching the game pad.

The program is driven by a Bluetooth game pad paired straight to the board. The first time,
put the pad into pairing mode and Yukon finds it, pairs, and saves the link key to a file on
the board. From then on switching the pad on is enough. LED A is lit whenever the rover is
waiting for the pad, and the motors coast to a stop while it is.

The pad's Plus button swaps between driving on the sticks and driving on the triggers.

Press "Boot/User" to exit the program, only if the buzzer is not sounding.
If the buzzer sounds, disconnect power as soon as possible!
"""

# Constants
UPDATES = 50                            # How many times to update motors and LEDs per second
TIMESTEP = 1 / UPDATES
TIMESTEP_MS = int(TIMESTEP * 1000)
MOTOR_SPEED = 0.4                       # The top speed to drive each motor at

PAD_MAPPING = create_8bitdo_sn30_pro_plus_xinput    # The mapping function for the pad in use, see gamepad_mappings.py
CONTROL_SCHEMES = (triggers, sticks)    # The ways to drive, the first one to start with, see controls.py
SCHEME_BUTTON = "Plus"                  # The pad button that swaps to the next way of driving
INQUIRY_SECONDS = 8                     # How long to look for a pad in pairing mode when none is stored
CONNECT_TIMEOUT_MS = 20000              # How long to give a connection attempt before trying again
RETRY_INTERVAL_MS = 5000                # How long to wait between attempts to reach a stored pad
GAMEPAD_CLASS = 0x05                    # The major device class that game pads report in an inquiry
SUPERVISION_MS = 2000                   # How long a silent pad may hold the link before it counts as gone

STRIP_TYPE = LEDStripModule.NEOPIXEL    # The type of LED strip being driven
STRIP_PIO = 0                           # The PIO system to use (0 or 1) to drive the strip
STRIP_SM = 0                            # The State Machines (SM) to use to drive the strip
LEDS_PER_STRIP = 120                    # How many LEDs are on the strip
SPEED_HUE_RANGE = 1.5                   # The speed range that will result in the full green -> blue -> red hue range

LOW_VOLTAGE_LEVEL = 10.0                # The voltage below which the program will terminate and start the buzzer
BUZZER_PERIOD = 0.5                     # The time between each buzz of the low voltage alarm
BUZZER_DUTY = 0.5                       # The percentage of the time that the buzz will be on for

# Variables
yukon = Yukon(logging_level=LOG_WARN)               # Create a Yukon object with the logging level set to warnings to reduce print outputs
left_driver = BigMotorModule(init_encoder=False)    # Create the left side BigMotorDriver object, without the encoder
right_driver = BigMotorModule(init_encoder=False)   # Create the left side BigMotorDriver object, without the encoder
led_module = LEDStripModule(STRIP_TYPE,             # Create a LEDStripModule object, with the details of the attached strip
                            STRIP_PIO,
                            STRIP_SM,
                            LEDS_PER_STRIP)
wireless_module = RM2WirelessModule()               # Create a RM2WirelessModule object, which checks this is a wireless build

ble = bluetooth.BLE()                   # The Bluetooth stack, which must be active before btclassic is used
pad = PAD_MAPPING()                     # The pad's controls, decoded from its reports
buzzer = BUZZER_SLOT.FAST3              # The pin the low voltage buzzer is attached to
exited_due_to_low_voltage = True        # Record if the program exited due to low voltage (assume true to start)
known = []                              # The addresses of the pads that have been paired with
next_pad = 0                            # Which stored pad to page next, when more than one is stored
last_attempt = None                     # When a stored pad was last paged
last_speeds = None                      # The speeds the LEDs were last coloured for
scheme = 0                              # Which of CONTROL_SCHEMES is driving


def next_scheme():
    """Swap to the next way of driving, on a press of the pad's scheme button."""
    global scheme
    scheme = (scheme + 1) % len(CONTROL_SCHEMES)
    print("Driving with the", CONTROL_SCHEMES[scheme].__name__)


# Function for mapping a value from one range to another
def map_float(input, in_min, in_max, out_min, out_max):
    return (((input - in_min) * (out_max - out_min)) / (in_max - in_min)) + out_min


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


def stop_driving():
    """Disable both motors, causing them to coast to a stop, and grey out the LEDs."""
    global last_speeds
    left_driver.motor.disable()
    right_driver.motor.disable()

    if last_speeds is not None:
        last_speeds = None
        for led in range(led_module.strip.num_leds()):
            led_module.strip.set_rgb(led, 128, 128, 128)
        led_module.strip.update()


def drive(forward, steer):
    """Set the motor speeds for a forward and steering input, and colour the LEDs to match."""
    global last_speeds
    left_speed, right_speed = mix(forward, steer)
    left_driver.motor.speed(left_speed * MOTOR_SPEED)
    right_driver.motor.speed(right_speed * MOTOR_SPEED)

    # Redrawing the strip only when a speed changes leaves the loop free at a standstill
    if last_speeds == (left_speed, right_speed):
        return
    last_speeds = (left_speed, right_speed)

    MID_LED = led_module.strip.num_leds() // 2

    # Update the left side LEDs to a colour based on the left speed
    left_hue = map_float(left_speed, SPEED_HUE_RANGE, -SPEED_HUE_RANGE, 0.999, 0.333)
    for led in range(0, MID_LED):
        led_module.strip.set_hsv(led, left_hue, 1.0, 1.0)

    # Update the right side LEDs to a colour based on the right speed
    right_hue = map_float(right_speed, -SPEED_HUE_RANGE, SPEED_HUE_RANGE, 0.999, 0.333)
    for led in range(MID_LED, led_module.strip.num_leds()):
        led_module.strip.set_hsv(led, right_hue, 1.0, 1.0)

    led_module.strip.update()       # Send the new colours to the LEDs


# Ensure the input voltage is above the low level
if yukon.read_input_voltage() > LOW_VOLTAGE_LEVEL:
    exited_due_to_low_voltage = False

    # Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
    try:
        # Register the module objects with their respective slots
        yukon.register_with_slot(left_driver, LEFT_SLOT)
        yukon.register_with_slot(right_driver, RIGHT_SLOT)
        yukon.register_with_slot(led_module, LED_SLOT)
        yukon.register_with_slot(wireless_module, WIRELESS_SLOT)

        yukon.verify_and_initialise()           # Verify that modules are attached to Yukon, and initialise them

        ble.active(True)                        # Bring up the Bluetooth stack

        # A pad only reports when a control moves, so a held stick and a pad that has gone look
        # alike. Shortening the link supervision timeout is what tells them apart, and it decides
        # how long the rover can keep driving on the last thing it was told.
        btclassic.supervision_timeout(SUPERVISION_MS)

        known = pad_keys.load()                 # Put any saved link keys back into the stack
        btclassic.connectable(True)             # Now let pads connect to us
        if known:
            print("Stored pads:", ", ".join(address_text(address) for address in known))

        pad.on_button(SCHEME_BUTTON, pressed=next_scheme)
        print("Driving with the", CONTROL_SCHEMES[scheme].__name__)

        yukon.enable_main_output()              # Turn on power to the module slots

        # Enable the drivers and regulators on all modules
        left_driver.enable()
        right_driver.enable()
        led_module.enable()

        current_time = ticks_ms()               # Record the start time of the program loop

        # Loop until the BOOT/USER button is pressed
        while not yukon.is_boot_pressed():

            if pad.is_connected():
                yukon.set_led('A', False)
                pad.update()                    # Decode every report the pad has sent since the last loop
                drive(*CONTROL_SCHEMES[scheme](pad))
                print(f"LSpeed = {0.0 - left_driver.motor.speed()}, RSpeed = {right_driver.motor.speed()}", end=", ")
            else:
                # Without a pad the rover must not drive, so it stops and reaches for one
                yukon.set_led('A', True)
                stop_driving()
                pad.reset()
                reach_for_pad()
                print("Waiting for a pad", end=", ")

            try:
                # Advance the current time by a number of milliseconds
                current_time = ticks_add(current_time, TIMESTEP_MS)

                # Monitor sensors until the current time is reached, recording the min, max, and average for each
                # This approach accounts for the updates taking a non-zero amount of time to complete
                yukon.monitor_until_ms(current_time)
            except RuntimeError as e:
                left_driver.disable()
                right_driver.disable()
                led_module.disable()
                print(str(e))
                time.sleep(1.0)
                yukon.enable_main_output()
                left_driver.enable()
                right_driver.enable()
                led_module.enable()

            # Get the average voltage recorded from monitoring, and print it out
            readings = yukon.get_readings()
            avg_voltage = readings["Vi_avg"]
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
