import math
from machine import Pin
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT2 as SLOT_X
from pimoroni_yukon import SLOT3 as SLOT_Y1
from pimoroni_yukon import SLOT1 as SLOT_Y2
from pimoroni_yukon import SLOT4 as SLOT_Z
from pimoroni_yukon import SLOT5 as SLOT_LIMITS_1
from pimoroni_yukon import SLOT6 as SLOT_LIMITS_2
from pimoroni_yukon.modules import DualMotorModule, QuadServoDirectModule
from pimoroni_yukon.devices.stepper import OkayStepper
from parser import GCodeParser

"""
A showcase of Yukon as a pen plotter.
"""

# Constants
GCODE_FILE = "yukon_logo.gcode"     # The file containing gcode instructions for drawing with the plotter

CURRENT_SCALE = 0.5
IDLE_CURRENT_SCALE = 0.1

BELT_PITCH = 3
PULLEY_TOOTH_COUNT = 20
STEPS_PER_REV = 200
STEPS_PER_MM = STEPS_PER_REV / (BELT_PITCH * PULLEY_TOOTH_COUNT)

PLOT_ORIGIN_X_MM = 200
PLOT_ORIGIN_Y_MM = 100
PLOT_SIZE_MM = 300
SPEED_MM_PER_SEC = 50

# Variables
yukon = Yukon()                 # Create a new Yukon object
x_module = DualMotorModule()      # Create a DualMotorModule object
y1_module = DualMotorModule()      # Create a DualMotorModule object
y2_module = DualMotorModule()      # Create a DualMotorModule object
z_module = DualMotorModule()      # Create a DualMotorModule object
l1_module = QuadServoDirectModule(init_servos=False)
l2_module = QuadServoDirectModule(init_servos=False)

# Store OkayStepper objects created later
x_stepper = None
y_stepper = None
z_stepper = None

has_homed = False
movement_index = -1
first_home = True


# Function to activate the main power, all modules, and all steppers
def activate():
    yukon.enable_main_output()
    x_module.enable()
    y1_module.enable()
    y2_module.enable()
    z_module.enable()
    x_stepper.hold()
    y_stepper.hold()
    z_stepper.hold()


# Function to deactivate all steppers, modules and the main output
def deactivate():
    x_stepper.release()
    y_stepper.release()
    z_stepper.release()
    x_module.disable()
    y1_module.disable()
    y2_module.disable()
    z_module.disable()
    yukon.disable_main_output()


# Function that homes a single plotter axis, given a stepper, speed, and limit switch
def home_axis(name, stepper, speed, limit_switch):
    print(f"Homing {name} ... ", end="")
    iteration = 0
    while iteration < 2:
        iteration += 1
        if limit_switch.value() == 1:
            stepper.move_by_steps(speed, 0.2 * (iteration * iteration), debug=False)
            stepper.wait_for_move()

        steps = 0
        while limit_switch.value() != 1:
            stepper.move_by_steps(-1, 0.005 * (iteration * iteration), debug=False)
            stepper.wait_for_move()
            steps += 1
            if steps > 3000:
                yukon.disable_main_output()
                raise RuntimeError("Could not home Z")
        stepper.hold()
        stepper.zero_position()
    print("done")


def move_to_xy(x, y, speed=SPEED_MM_PER_SEC):
    dx = x_stepper.unit_diff(x)
    dy = y_stepper.unit_diff(y)

    travel_time = math.sqrt(dx * dx + dy * dy) / speed
    if travel_time > 0:
        print(f"Moving to X {x}, Y {y}, in T {travel_time}")
        x_stepper.move_to(x, travel_time)
        y_stepper.move_to(y, travel_time)

        x_stepper.wait_for_move()
        y_stepper.wait_for_move()


def move_by_xy(dx, dy, speed=SPEED_MM_PER_SEC):
    travel_time = math.sqrt(dx * dx + dy * dy) / speed
    if travel_time > 0:
        print(f"Moving by X {dx}, Y {dy}, in T {travel_time}")
        x_stepper.move_by(dx, travel_time)
        y_stepper.move_by(dy, travel_time)

        x_stepper.wait_for_move()
        y_stepper.wait_for_move()


def lower_pen():
    z = 1550
    dz = z_stepper.step_diff(z)
    travel_time = abs(dz) / 300
    if travel_time > 0:
        print(f"Lowering Pen, in T {travel_time}")
        z_stepper.move_to_step(z, travel_time)
        z_stepper.wait_for_move()


def lift_pen():
    z = 1000
    dz = z_stepper.step_diff(z)
    travel_time = abs(dz) / 300
    if travel_time > 0:
        print(f"Lifting Pen, in T {travel_time}")
        z_stepper.move_to_step(z, travel_time)
        z_stepper.wait_for_move()


def raise_pen():
    z = 0
    dz = z_stepper.step_diff(z)
    travel_time = abs(dz) / 300
    if travel_time > 0:
        print(f"Raising Pen, in T {travel_time}")
        z_stepper.move_to_step(z, travel_time)
        z_stepper.wait_for_move()


parser = GCodeParser(absolute_callback=move_to_xy,
                     relative_callback=move_by_xy,
                     lower_pen_callback=lower_pen,
                     lift_pen_callback=lift_pen,
                     raise_pen_callback=raise_pen)


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    # Register the four DualMotorModule objects with their respective slots
    yukon.register_with_slot(x_module, SLOT_X)
    yukon.register_with_slot(y1_module, SLOT_Y1)
    yukon.register_with_slot(y2_module, SLOT_Y2)
    yukon.register_with_slot(z_module, SLOT_Z)
    yukon.register_with_slot(l1_module, SLOT_LIMITS_1)
    yukon.register_with_slot(l2_module, SLOT_LIMITS_2)

    # Verify that the DualMotorModules are attached to Yukon, and initialise them
    yukon.verify_and_initialise()

    # Create OkayStepper classes to drive the plotter's stepper motors
    # The Y axis has two sets of motors as it is driven from both sides
    x_stepper = OkayStepper(x_module.motor1, x_module.motor2,
                            steps_per_unit=STEPS_PER_MM)
    y_stepper = OkayStepper(y1_module.motor1, y1_module.motor2,
                            y2_module.motor2, y2_module.motor1,
                            steps_per_unit=STEPS_PER_MM)
    z_stepper = OkayStepper(z_module.motor1, z_module.motor2)

    # Set the hardware current limit of each DualMotorModule to its maximum as OkayStepper controls current with PWM instead
    x_module.set_current_limit(DualMotorModule.MAX_CURRENT_LIMIT)
    y1_module.set_current_limit(DualMotorModule.MAX_CURRENT_LIMIT)
    y2_module.set_current_limit(DualMotorModule.MAX_CURRENT_LIMIT)
    z_module.set_current_limit(DualMotorModule.MAX_CURRENT_LIMIT)

    # Access the pins of the QuadServoDirect modules and set them up to use with limit switches
    z_up_limit = l1_module.servo_pins[0]
    x_left_limit = l1_module.servo_pins[2]
    x_right_limit = l2_module.servo_pins[0]
    y_back_limit = l2_module.servo_pins[2]
    z_up_limit.init(Pin.IN, Pin.PULL_UP)
    x_left_limit.init(Pin.IN, Pin.PULL_UP)
    x_right_limit.init(Pin.IN, Pin.PULL_UP)
    y_back_limit.init(Pin.IN, Pin.PULL_UP)

    parser.load_file(GCODE_FILE)

    if has_homed:
        yukon.set_led('A', True)    # Show that button A can be pressed
    else:
        yukon.set_led('B', True)    # Show that button B can be pressed

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Has the plotter been homed?
        if has_homed:
            # Are we be parsing gcode / plotting?
            if parser.is_parsing():
                # Attempt to parse the next gcode command.
                # If there are no more commands to parse, False is returned
                if not parser.parse_next():
                    # Move to the origin of the plot
                    move_to_xy(PLOT_ORIGIN_X_MM, PLOT_ORIGIN_Y_MM)

                    deactivate()                        # De-energize the steppers and turn off power
                    has_homed = False                   # Plotter could be moved, so require re-homing
                    yukon.set_led('B', True)            # Show that button B can be pressed

            # Should gcode parsing / plotting be started?
            elif yukon.is_pressed('A'):
                # Wait for the button to be released
                while yukon.is_pressed('A'):
                    pass
                yukon.set_led('A', False)   # Stop showing that button A can be pressed
                activate()                  # Turn on power and energize the steppers

                # Start parsing the gcode, with the given origin and size
                parser.start_parsing(PLOT_ORIGIN_X_MM,
                                     PLOT_ORIGIN_Y_MM,
                                     PLOT_SIZE_MM)

        # Should homing be started?
        elif first_home or yukon.is_pressed('B'):
            # Wait for the button to be released
            if not first_home:
                while yukon.is_pressed('B'):
                    pass
            yukon.set_led('B', False)   # Stop showing that button B can be pressed
            activate()                  # Turn on power and energize the steppers

            # Home each axis in turn
            home_axis("Z", z_stepper, 20, z_up_limit)
            home_axis("X", x_stepper, 20, x_right_limit)
            home_axis("Y", y_stepper, 50, y_back_limit)

            # Move to the origin of the plot
            move_to_xy(PLOT_ORIGIN_X_MM, PLOT_ORIGIN_Y_MM)

            print("Homing Complete")
            has_homed = True
            first_home = False

            yukon.set_led('A', True)    # Show that button A can be pressed

finally:
    if x_stepper is not None:
        x_stepper.release()     # Release the X axis stepper motor (if not already done so)

    if y_stepper is not None:
        y_stepper.release()     # Release the Y axis stepper motor (if not already done so)

    if z_stepper is not None:
        z_stepper.release()     # Release the Z axis stepper motor (if not already done so)

    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
