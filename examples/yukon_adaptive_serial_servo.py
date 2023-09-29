import time
import math
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import SerialServoModule
from pimoroni_yukon.protocols.lx_servos import *

SPEED = 5             # The speed that the servos will cycle at
UPDATES = 5          # How many times to update LEDs and Servos per second
SERVO_EXTENT = 80.0   # How far from zero to move the servos

# Create a Yukon object to begin using the board
yukon = Yukon(logging_level=1)

# List to store the modules
servo_modules = []

try:
    # Create a Quad Servo Direct class for each populated module slot
    for slot in yukon.find_slots_with_module(SerialServoModule):
        serial_servo = SerialServoModule()
        yukon.register_with_slot(serial_servo, slot)
        servo_modules.append(serial_servo)
            
    # Initialise Yukon's registered modules
    yukon.initialise_modules(allow_unregistered=True)

    # Turn on the module power
    yukon.enable_main_output()
    
    time.sleep(1)
    
    old_id = 1
    new_id = 11
    
    servo_ids = [1, 2, 3]

    #for module in servo_modules:
    #     module.send_on_data()
    #     SerialServoSetID(module.uart, old_id, new_id)

    # for module in servo_modules:
    #    module.send_on_data()
    #     SerialServoSetMode(module.uart, 2, 1, 1000)
    
    offset = 0
    toggle = False
    while not yukon.is_boot_pressed():
        offset += SPEED / 1000.0

        # Update all the Servos
        for module in servo_modules:
            for sid in servo_ids:
                angle = SerialServoReadPosition(module.uart, module.send_on_data, module.receive_on_data, sid)
                angle = ((angle - 500) / 360) * 90
                voltage = SerialServoReadVin(module.uart, module.send_on_data, module.receive_on_data, sid)
                voltage = (voltage / 1000)
                temp = SerialServoReadTemperature(module.uart, module.send_on_data, module.receive_on_data, sid)
                print(f"ID: {sid}, Angle: {angle}, Vin: {voltage}, Temp: {temp}", end=", ")
            print()

        if yukon.is_pressed('A'):
            SerialServoMove(module.uart, 1, 500, 1000)

        if yukon.is_pressed('B'):
            SerialServoMove(module.uart, 1, 800, 1000)

        toggle = not toggle
        if toggle:
            SerialServoActivateLED(module.uart, 1)
        else:
            SerialServoDeactivateLED(module.uart, 1)

        yukon.monitored_sleep(1.0 / UPDATES)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
