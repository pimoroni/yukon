import time
from machine import Pin, UART
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT6 as LEFT_SLOT
from pimoroni_yukon import SLOT1 as RIGHT_SLOT
from pimoroni_yukon import SLOT5 as LED_SLOT
from pimoroni_yukon import SLOT2 as BT_SLOT
from pimoroni_yukon import SLOT3 as BUZZER_SLOT
from pimoroni_yukon.modules import BigMotorModule, LEDStripModule
from pimoroni_yukon import ticks_ms, ticks_add
from pimoroni_yukon.logging import LOG_WARN
from commander import JoyBTCommander

# Constants
UPDATES = 50                            # How many times to update LEDs and Servos per second
TIMESTEP = 1 / UPDATES
TIMESTEP_MS = int(TIMESTEP * 1000)
MOTOR_EXTENT = 0.4                      # How far from zero to drive the motors

STRIP_TYPE = LEDStripModule.NEOPIXEL    # The type of LED strip being driven
STRIP_PIO = 0                           # The PIO system to use (0 or 1) to drive the strip
STRIP_SM = 0                            # The State Machines (SM) to use to drive the strip
LEDS_PER_STRIP = 120                    # How many LEDs are on the strip
PULSE_TIME = 2.0                        # The time to perform a complete pulse of the LEDs when motors_active

BT_UART_ID = 1                          # The ID of the hardware UART to use for bluetooth comms via a serial tranceiver
BT_BAUDRATE = 9600                      # The baudrate of the bluetooth serial tranceiver's serial
BT_NO_COMMS_TIMEOUT = 1.0               # How long to wait after receiving data, to assume the transmitting device has disconnected

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

controller = JoyBTCommander(UART(BT_UART_ID,        # Create a JoyBTCommander object, providing it with
                            tx=BT_SLOT.FAST1,       # a UART object for the serial bluetooth tranceiver
                            rx=BT_SLOT.FAST2,
                            baudrate=BT_BAUDRATE),
                            BT_NO_COMMS_TIMEOUT)
buzzer = BUZZER_SLOT.FAST3                          # The pin the low voltage buzzer is attached to
exited_due_to_low_voltage = True                    # Record if the program exited due to low voltage (assume true to start)


def no_comms_callback():
    # Disable both motors, causing them to coast to a stop
    left_driver.motor.disable()
    right_driver.motor.disable()


def joystick_callback(x, y):
    x *= y      # Prevent turning on the spot (which the chassis cannot achieve) by scaling the side input by the forward input

    # Update the left and right motor speeds based on the forward and side inputs
    left_speed = -y-x
    right_speed = y-x
    left_driver.motor.speed(left_speed * MOTOR_EXTENT)
    right_driver.motor.speed(right_speed * MOTOR_EXTENT)

    MID_LED = led_module.strip.num_leds() // 2

    # Update the left side LEDs to a colour based on the left speed
    lefthue = map_float(left_speed, 1.5, -1.5, 0.999, 0.333)
    for led in range(0, MID_LED):
        led_module.strip.set_hsv(led, lefthue, 1.0, 1.0)

    # Update the right side LEDs to a colour based on the right speed
    righthue = map_float(right_speed, -1.5, 1.5, 0.999, 0.333)
    for led in range(MID_LED, led_module.strip.num_leds()):
        led_module.strip.set_hsv(led, righthue, 1.0, 1.0)

    led_module.strip.update()       # Send the new colours to the LEDs


# Function for mapping a value from one range to another
def map_float(input, in_min, in_max, out_min, out_max):
    return (((input - in_min) * (out_max - out_min)) / (in_max - in_min)) + out_min


# Ensure the input voltage is above the low level
if yukon.read_input_voltage() > LOW_VOLTAGE_LEVEL:
    exited_due_to_low_voltage = False

    # Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
    try:
        # Register the SerialServoModule objects with their respective slots
        yukon.register_with_slot(left_driver, LEFT_SLOT)
        yukon.register_with_slot(right_driver, RIGHT_SLOT)
        yukon.register_with_slot(led_module, LED_SLOT)

        # Assign timeout and joystick callbacks to the controller, and start it
        controller.set_timeout_callback(no_comms_callback)
        controller.set_joystick_callback(joystick_callback)
        controller.begin()

        yukon.verify_and_initialise()           # Verify that modules are attached to Yukon, and initialise them
        yukon.enable_main_output()              # Turn on power to the module slots

        # Enable the drivers and regulators on all modules
        left_driver.enable()
        right_driver.enable()
        led_module.enable()

        current_time = ticks_ms()               # Record the start time of the program loop

        # Loop until the BOOT/USER button is pressed
        while not yukon.is_boot_pressed():

            controller.check_receive()
            print(controller.button_states_to_string(), controller.joystick[0], controller.joystick[1], sep=", ")

            # Perform a pulsing animation on the LEDs if there is no controller connection
            if not controller.is_connected():
                # Update all the LEDs to show the same colour
                for led in range(led_module.strip.num_leds()):
                    led_module.strip.set_rgb(led, 128, 128, 128)
                led_module.strip.update()

            try:
                # Advance the current time by a number of milliseconds
                current_time = ticks_add(current_time, TIMESTEP_MS)

                # Monitor sensors until the current time is reached, recording the min, max, and average for each
                # This approach accounts for the updates takinga non-zero amount of time to complete
                yukon.monitor_until_ms(current_time)
            except RuntimeError as e:
                left_driver.disable()
                right_driver.disable()
                import time
                print(str(e))
                time.sleep(1.0)
                yukon.enable_main_output()
                left_driver.enable()
                right_driver.enable()

            # Get the average voltage recorded from monitoring, and print it out
            avg_voltage = yukon.get_readings()["Vi_avg"]
            print(f"V = {avg_voltage}")

            # Check if the average input voltage was below the low voltage level
            if avg_voltage < LOW_VOLTAGE_LEVEL:
                exited_due_to_low_voltage = True
                break           # Break out of the loop

    finally:
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

