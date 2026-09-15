# Report layouts for known game pads. Bit offsets count from the start of the report as btclassic
# delivers it, which is the HID DATA header byte, the report id, then the fields.
from gamepad import Gamepad


def create_8bitdo_lite(stick_deadzone=0.1):
    """The 8BitDo Lite in its Android mode, held with B at power on.

    The pad has two direction pads and no sticks. The left one reports as the hat, the right one
    as a stick, and the star button swaps which stick that is without sending anything itself.
    """
    pad = Gamepad("8BitDo Lite gamepad")

    # Four 16 bit stick axes, then two 10 bit triggers each padded to 16.
    pad.register_axis("LX", 16, 16, deadzone=stick_deadzone)
    pad.register_axis("LY", 32, 16, deadzone=stick_deadzone, invert=True)
    pad.register_axis("RX", 48, 16, deadzone=stick_deadzone)
    pad.register_axis("RY", 64, 16, deadzone=stick_deadzone, invert=True)
    pad.register_trigger("L2", 80, 10, alt_name="LT")
    pad.register_trigger("R2", 96, 10, alt_name="RT")

    # Direction pad as a hat nibble, then the buttons in HID order.
    pad.register_hat(112)
    pad.register_button("B", 15, 0)
    pad.register_button("A", 15, 1)
    pad.register_button("Y", 15, 2)
    pad.register_button("X", 15, 3)
    pad.register_button("L1", 15, 4, alt_name="LB")
    pad.register_button("R1", 15, 5, alt_name="RB")
    pad.register_button("Minus", 15, 6, alt_name="Select")
    pad.register_button("Plus", 15, 7, alt_name="Start")
    pad.register_button("Button9", 16, 0)
    pad.register_button("Button10", 16, 1)

    # Home arrives in a report of its own, one byte.
    pad.register_button("Home", 2, 0, report_id=2)
    return pad
