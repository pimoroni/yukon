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
A showcase of Yukon as a 3-axis CNC pen plotter.
It uses four Dual Motor modules, to control for stepper motors (the Y-Axis has two steppers).
It also uses two Quad Servo Direct modules to provide convenient wiring for the machine's limit switches.

The program first homes the 3 axes of the machine to give an origin from which to plot from.
Then after pressing 'A' it executes commands from a .gcode file loaded onto Yukon.

Only a subset of G-Code is supported, sufficient for performing linear moves of the machine, and raising and lowering its pen.

Press "Boot/User" to exit the program.
Press "A" to start plotting once homed.
Press "B" to re-home the machine after plotting.
"""

# Constants
GCODE_FILE = "yukon_logo.gcode"     # The file containing gcode instructions for drawing with the plotter
HOME_ON_PROGRAM_RUN = True          # Should homing happen automatically when the program is first run, or require a button to be pressed?

CURRENT_SCALE = 0.5
IDLE_CURRENT_SCALE = 0.1

STEPS_PER_REV = 200                 # The number of steps each stepper motor takes to perform a full revolution
BELT_PITCH = 3                      # The spacing between each notch of the belts used on the X and Y axes
PULLEY_TOOTH_COUNT = 20             # The number of teeth on the X and Y axes direct-driven pulleys
BELT_STEPS_PER_MM = STEPS_PER_REV / (BELT_PITCH * PULLEY_TOOTH_COUNT)

SCREW_MM_PER_REV = 8                # How many millimeters of travel a single revolution of the Z axis lead screw produces
SCREW_STEPS_PER_MM = STEPS_PER_REV / SCREW_MM_PER_REV

PLOT_ORIGIN_X_MM = 200              # The X position to start the plotting from
PLOT_ORIGIN_Y_MM = 100              # The X position to start the plotting from
PLOT_SIZE_MM = 300                  # The size to scale the largest dimension (width or height) of the gcode data to

BELT_SPEED_MM_PER_SEC = 50          # The speed to move the X and Y axes at when plotting
SCREW_SPEED_MM_PER_SEC = 20         # The speed to move the Z axis at when plotting

PEN_LOWER_HEIGHT_MM = 62            # The height to lower the Z axis by to make the pen touch the paper
PEN_LIFT_AMOUNT_MM = 10             # The height to raise the pen by when switching between shapes to draw
PEN_LIFT_HEIGHT_MM = PEN_LOWER_HEIGHT_MM - PEN_LIFT_AMOUNT_MM

X_RETREAT_STEPS = 20                # The number of steps the X axis will retreat from its limit switch by, when homing
Y_RETREAT_STEPS = 50                # The number of steps the Y axis will retreat from its limit switch by, when homing
Z_RETREAT_STEPS = 20                # The number of steps the Z axis will retreat from its limit switch by, when homing
HOMING_SPEED_STEPS_PER_SEC = 5      # The speed to move each axis towards their limit switches by, when homing
RETREAT_SPEED_STEPS_PER_SEC = 200   # The speed to move each axis away (retreat) from their limit switches by, when homing
MAX_HOMING_STEPS = 3000             # The number of steps allowed before homing is considered to have failed

# Variables
yukon = Yukon()                     # Create a new Yukon object
x_module = DualMotorModule()        # Create a DualMotorModule object for the X axis
y1_module = DualMotorModule()       # Create a DualMotorModule object for one side of the Y axis
y2_module = DualMotorModule()       # Create a DualMotorModule object for the other side of the Y axis
z_module = DualMotorModule()        # Create a DualMotorModule object for the Z axis
l1_module = QuadServoDirectModule(init_servos=False)    # Create a QuadServoDirectModule object for reading two limit switches
l2_module = QuadServoDirectModule(init_servos=False)    # Create a QuadServoDirectModule object for reading two more limit switches
x_stepper = None                    # Variable for storing the X axis OkayStepper object created later
y_stepper = None                    # Variable for storing the Y axis OkayStepper object created later
z_stepper = None                    # Variable for storing the Z axis OkayStepper object created later
has_homed = False                   # Record if the plotter has been homed, meaning it knows its position
first_home = HOME_ON_PROGRAM_RUN    # Is this the first time homing?


# Activate the main power, all modules, and all steppers
def activate():
    yukon.enable_main_output()
    x_module.enable()
    y1_module.enable()
    y2_module.enable()
    z_module.enable()
    x_stepper.hold()
    y_stepper.hold()
    z_stepper.hold()


# Deactivate all steppers, all modules and the main output
def deactivate():
    x_stepper.release()
    y_stepper.release()
    z_stepper.release()
    x_module.disable()
    y1_module.disable()
    y2_module.disable()
    z_module.disable()
    yukon.disable_main_output()


# Home a single plotter axis, given a stepper, retreat steps, and limit switch
def home_axis(name, stepper, retreat_steps, limit_switch):
    print(f"Homing {name} ... ", end="")

    # Perform two passes of the homing, first at a high speed, then at a lower speed
    iteration = 0
    while iteration < 2:
        iteration += 1
        # Is the limit switch pressed?
        if limit_switch.value() == 1:
            # Move away from the limit switch by an amount sufficient to release the limit switch
            stepper.move_by_steps(retreat_steps, (1.0 / HOMING_SPEED_STEPS_PER_SEC) * (iteration * iteration))
            stepper.wait_for_move()

        # Move towards the limit switch one step at a time, until it is pressed or too many steps occur
        steps = 0
        while limit_switch.value() != 1:
            stepper.move_by_steps(-1, (1.0 / RETREAT_SPEED_STEPS_PER_SEC) * (iteration * iteration))
            stepper.wait_for_move()
            steps += 1

            # Have too many steps passed?
            if steps > MAX_HOMING_STEPS:
                yukon.disable_main_output()
                raise RuntimeError(f"Could not home {name}")

    stepper.hold()              # Keep the stepper energized but at a lower power than when moving
    stepper.zero_position()     # Use the stepper's current position as its zero value
    print("done")


# Move the plotter to a given x and y position (in mm) at a set speed
def move_to_xy(x, y, speed=BELT_SPEED_MM_PER_SEC):
    dx = x_stepper.unit_diff(x)
    dy = y_stepper.unit_diff(y)

    travel_time = math.sqrt(dx * dx + dy * dy) / speed
    if travel_time > 0:
        print(f"Moving to X {x}, Y {y}, in T {travel_time}")
        x_stepper.move_to(x, travel_time)
        y_stepper.move_to(y, travel_time)

        x_stepper.wait_for_move()
        y_stepper.wait_for_move()


# Move the plotter by a given x and y position (in mm) at a set speed
def move_by_xy(dx, dy, speed=BELT_SPEED_MM_PER_SEC):
    travel_time = math.sqrt(dx * dx + dy * dy) / speed
    if travel_time > 0:
        print(f"Moving by X {dx}, Y {dy}, in T {travel_time}")
        x_stepper.move_by(dx, travel_time)
        y_stepper.move_by(dy, travel_time)

        x_stepper.wait_for_move()
        y_stepper.wait_for_move()


# Move the plotter's pen to its drawing height
def lower_pen():
    dz = z_stepper.unit_diff(PEN_LOWER_HEIGHT_MM)
    travel_time = abs(dz) / SCREW_SPEED_MM_PER_SEC
    if travel_time > 0:
        print(f"Lowering Pen to {PEN_LOWER_HEIGHT_MM}, in T {travel_time}")
        z_stepper.move_to(PEN_LOWER_HEIGHT_MM, travel_time)
        z_stepper.wait_for_move()


# Move the plotter's pen to just above its drawing height
def lift_pen():
    dz = z_stepper.unit_diff(PEN_LIFT_HEIGHT_MM)
    travel_time = abs(dz) / SCREW_SPEED_MM_PER_SEC
    if travel_time > 0:
        print(f"Lifting Pen to {PEN_LIFT_HEIGHT_MM}, in T {travel_time}")
        z_stepper.move_to(PEN_LIFT_HEIGHT_MM, travel_time)
        z_stepper.wait_for_move()


# Move the plotter's pen to its home height
def raise_pen():
    dz = z_stepper.units()
    travel_time = abs(dz) / SCREW_SPEED_MM_PER_SEC
    if travel_time > 0:
        print(f"Raising Pen to 0, in T {travel_time}")
        z_stepper.move_to(0, travel_time)
        z_stepper.wait_for_move()


# Create an instance of the GCodeParser, giving it the functions to call for movement and pen control
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

    # Create OkayStepper classes to drive the plotter's stepper motors, with their units scaled to be in millimeters
    x_stepper = OkayStepper(x_module.motor1, x_module.motor2,
                            steps_per_unit=BELT_STEPS_PER_MM)
    y_stepper = OkayStepper(y1_module.motor1, y1_module.motor2,
                            y2_module.motor2, y2_module.motor1,     # The Y axis has two sets of motors as it is driven from both sides
                            steps_per_unit=BELT_STEPS_PER_MM)
    z_stepper = OkayStepper(z_module.motor1, z_module.motor2,
                            steps_per_unit=SCREW_STEPS_PER_MM)

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

    # Have the parser load in the GCode file
    print(f"Loading '{GCODE_FILE}' ... ", end="")
    parser.load_file(GCODE_FILE)
    print("done")

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
                    print("Plotting finished. Press 'B' to re-home")

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
                print("Plotting started")

        # Should homing be started?
        elif first_home or yukon.is_pressed('B'):
            if not first_home:
                # Wait for the button to be released
                while yukon.is_pressed('B'):
                    pass
            yukon.set_led('B', False)   # Stop showing that button B can be pressed
            activate()                  # Turn on power and energize the steppers

            # Home each axis in turn
            home_axis("Z", z_stepper, Z_RETREAT_STEPS, z_up_limit)
            home_axis("X", x_stepper, X_RETREAT_STEPS, x_right_limit)
            home_axis("Y", y_stepper, Y_RETREAT_STEPS, y_back_limit)

            # Move to the origin of the plot
            move_to_xy(PLOT_ORIGIN_X_MM, PLOT_ORIGIN_Y_MM)

            has_homed = True
            first_home = False

            yukon.set_led('A', True)    # Show that button A can be pressed
            print("Homing finished. Press 'A' to start plotting")

finally:
    # Release each stepper motor (if not already done so)
    if x_stepper is not None:
        x_stepper.release()

    if y_stepper is not None:
        y_stepper.release()

    if z_stepper is not None:
        z_stepper.release()

    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
