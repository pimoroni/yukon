import time
import math
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import QuadServoDirectModule, QuadServoRegModule

SPEED = 5             # The speed that the servos will cycle at
UPDATES = 50          # How many times to update LEDs and Servos per second
SERVO_EXTENT = 80.0   # How far from zero to move the servos

# Create a Yukon object to begin using the board
yukon = Yukon(logging_level=2)

# List to store the modules
servo_modules = []

try:
    # Create a Quad Servo Direct class for each populated module slot
    for slot in yukon.find_slots_with_module(QuadServoDirectModule):
        direct_servo = QuadServoDirectModule()
        yukon.register_with_slot(direct_servo, slot)
        servo_modules.append(direct_servo)
    
    # Create a Quad Servo Reg class for each populated module slot
    for slot in yukon.find_slots_with_module(QuadServoRegModule):
        reg_servo = QuadServoRegModule()
        yukon.register_with_slot(reg_servo, slot)
        servo_modules.append(reg_servo)
            
    # Initialise Yukon's registered modules
    yukon.initialise_modules(allow_unregistered=True)

    NUM_SERVOS = len(servo_modules) * QuadServoDirectModule.NUM_SERVOS
    print(f"Up to {NUM_SERVOS} servos available")

    # Turn on the module power
    yukon.enable_main_output()

    # Enable the outputs on the regulated servo modules
    for module in servo_modules:
        try:
            module.enable()
        except AttributeError:
            # No enable function
            pass

    offset = 0
    while not yukon.is_boot_pressed():
        offset += SPEED / 1000.0

        # Update all the Servos
        i = 0
        for module in servo_modules:
            for servo in module.servos:
                angle = ((i / NUM_SERVOS) + offset) * math.pi * 2
                servo.value(math.sin(angle) * SERVO_EXTENT)
                i += 1

        yukon.monitored_sleep(1.0 / UPDATES)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
