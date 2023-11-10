from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import SerialServoModule
from pimoroni_yukon.devices.lx_servo import LXServo

"""
Detect any servos that are attached to a Serial Bus Servo module connected to Slot1.
"""

# Constants
VOLTAGE_LIMIT = 8.4         # The voltage to not exceed, to protect the servos
RESPONSE_TIMEOUT = 0.005    # How long to wait for a serial servo to respond
POWER_ON_DELAY = 1.0        # The time to sleep after turning on the power, for serial servos to power on

# Variables
yukon = Yukon(voltage_limit=VOLTAGE_LIMIT)  # Create a new Yukon object, with a lower voltage limit set
module = SerialServoModule()                # Create a SerialServoModule object
servos_found = 0                            # The number of servos found after the scan has completed


# Function to print the header row of the servo scan
def print_header_row():
    print("   ", end="")
    for i in range(0, 0x10):
        print(f"  {i:x}", end="")


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)  # Register the SerialServoModule object with the slot
    yukon.verify_and_initialise()           # Verify that a SerialServoModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots

    yukon.monitored_sleep(POWER_ON_DELAY)   # Wait for serial servos to power up

    print("> Scanning for servos ...")
    print_header_row()

    # Go through each servo ID
    for servo_id in range(0, LXServo.BROADCAST_ID):
        # Print out the row heading, if this servo is the first of the block of 16
        if servo_id % 0x10 == 0:
            print(f"\n{servo_id:02x}:", end="")

        # Is there a servo with the current ID?
        if LXServo.detect(servo_id, module.uart, module.duplexer, timeout=RESPONSE_TIMEOUT):
            print(f" {servo_id:02x}", end="")   # Print out its ID
            servos_found += 1                   # Increment the number of servos found
        else:
            print(" --", end="")                # Print a blank entry
    print()     # New Line

    print(f"> Scan complete. Found {servos_found} servos")

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
