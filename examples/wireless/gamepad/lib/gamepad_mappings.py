# Report layouts for known game pads, one function per pad and mode. Bit offsets count from the
# start of the report as btclassic delivers it, which is the HID DATA header byte, the report id,
# then the fields.
#
# 8BitDo pads choose their layout by the button held at power on, and advertise a different name
# and address in each mode. In X-input mode (X held, "8BitDo ..." in the inquiry) they send the
# same 306 byte descriptor whatever the pad. In Switch mode (Y held, "Pro Controller") they send
# the Pro Controller's simple report. In Android mode (B held, "8BitDo ...") they send a compact
# report with 8 bit axes and Android's button order. In macOS mode (A held, "Wireless Controller")
# they send a DualShock 4 style report.
from gamepad import Gamepad


def __register_8bitdo_xinput(pad, stick_deadzone):
    """The X-input layout, report id 1 with Home alone in report id 2."""
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
    pad.register_button("LStick", 16, 0)
    pad.register_button("RStick", 16, 1)
    pad.register_button("Home", 2, 0, report_id=2)


def __register_8bitdo_switch_buttons(pad):
    """The buttons of the Pro Controller's simple report, id 0x3F."""
    pad.register_button("B", 2, 0, report_id=0x3F)
    pad.register_button("A", 2, 1, report_id=0x3F)
    pad.register_button("Y", 2, 2, report_id=0x3F)
    pad.register_button("X", 2, 3, report_id=0x3F)
    pad.register_button("L1", 2, 4, alt_name="LB", report_id=0x3F)
    pad.register_button("R1", 2, 5, alt_name="RB", report_id=0x3F)
    pad.register_button("L2", 2, 6, alt_name="LT", report_id=0x3F)
    pad.register_button("R2", 2, 7, alt_name="RT", report_id=0x3F)
    pad.register_button("Minus", 3, 0, alt_name="Select", report_id=0x3F)
    pad.register_button("Plus", 3, 1, alt_name="Start", report_id=0x3F)
    pad.register_button("LStick", 3, 2, report_id=0x3F)
    pad.register_button("RStick", 3, 3, report_id=0x3F)
    pad.register_button("Home", 3, 4, report_id=0x3F)
    pad.register_button("Star", 3, 5, alt_name="Capture", report_id=0x3F)


def create_8bitdo_lite(stick_deadzone=0.1):
    """The 8BitDo Lite in its X-input mode.

    The pad has two direction pads and no sticks. The left one reports as the hat, the right one
    as the left stick, and the star button swaps which stick that is without sending anything
    itself. The stick clicks never press.
    """
    pad = Gamepad("8BitDo Lite gamepad")
    __register_8bitdo_xinput(pad, stick_deadzone)
    return pad


def create_8bitdo_sn30_pro_plus_xinput(stick_deadzone=0.1):
    """The 8BitDo SN30 Pro+ in its X-input mode, with analogue triggers. Star sends nothing."""
    pad = Gamepad("8BitDo SN30 Pro+ gamepad")
    __register_8bitdo_xinput(pad, stick_deadzone)
    return pad


def create_8bitdo_sn30_pro_plus_android(stick_deadzone=0.1):
    """The 8BitDo SN30 Pro+ in its Android mode, with analogue triggers. Star sends nothing."""
    pad = Gamepad("8BitDo SN30 Pro+ gamepad")
    report_id = 3

    # Direction pad as a hat nibble, then four 8 bit stick axes and two 8 bit triggers.
    pad.register_hat(16, first=0, report_id=report_id)
    pad.register_axis("LX", 24, 8, deadzone=stick_deadzone, report_id=report_id)
    pad.register_axis("LY", 32, 8, deadzone=stick_deadzone, invert=True, report_id=report_id)
    pad.register_axis("RX", 40, 8, deadzone=stick_deadzone, report_id=report_id)
    pad.register_axis("RY", 48, 8, deadzone=stick_deadzone, invert=True, report_id=report_id)
    pad.register_trigger("R2", 56, 8, alt_name="RT", report_id=report_id)
    pad.register_trigger("L2", 64, 8, alt_name="LT", report_id=report_id)

    # Buttons in Android's order. Bits 0 and 1 of byte 10 repeat the triggers as buttons.
    pad.register_button("A", 9, 0, report_id=report_id)
    pad.register_button("B", 9, 1, report_id=report_id)
    pad.register_button("Home", 9, 2, report_id=report_id)
    pad.register_button("X", 9, 3, report_id=report_id)
    pad.register_button("Y", 9, 4, report_id=report_id)
    pad.register_button("L1", 9, 6, alt_name="LB", report_id=report_id)
    pad.register_button("R1", 9, 7, alt_name="RB", report_id=report_id)
    pad.register_button("Minus", 10, 2, alt_name="Select", report_id=report_id)
    pad.register_button("Plus", 10, 3, alt_name="Start", report_id=report_id)
    pad.register_button("LStick", 10, 5, report_id=report_id)
    pad.register_button("RStick", 10, 6, report_id=report_id)
    return pad


def create_8bitdo_sn30_pro_plus_macos(stick_deadzone=0.1):
    """The 8BitDo SN30 Pro+ in its macOS mode, with analogue triggers. Star sends nothing."""
    pad = Gamepad("8BitDo SN30 Pro+ gamepad")

    # Four 8 bit stick axes, the direction pad as a hat nibble, the buttons in DualShock order with
    # bits 2 and 3 of byte 7 repeating the triggers, then two 8 bit triggers.
    pad.register_axis("LX", 16, 8, deadzone=stick_deadzone)
    pad.register_axis("LY", 24, 8, deadzone=stick_deadzone, invert=True)
    pad.register_axis("RX", 32, 8, deadzone=stick_deadzone)
    pad.register_axis("RY", 40, 8, deadzone=stick_deadzone, invert=True)
    pad.register_hat(48, first=0)
    pad.register_button("Y", 6, 4, alt_name="Square")
    pad.register_button("B", 6, 5, alt_name="Cross")
    pad.register_button("A", 6, 6, alt_name="Circle")
    pad.register_button("X", 6, 7, alt_name="Triangle")
    pad.register_button("L1", 7, 0, alt_name="LB")
    pad.register_button("R1", 7, 1, alt_name="RB")
    pad.register_button("Minus", 7, 4, alt_name="Share")
    pad.register_button("Plus", 7, 5, alt_name="Options")
    pad.register_button("LStick", 7, 6)
    pad.register_button("RStick", 7, 7)
    pad.register_button("Home", 8, 0)
    pad.register_trigger("L2", 72, 8, alt_name="LT")
    pad.register_trigger("R2", 80, 8, alt_name="RT")
    return pad


def create_8bitdo_sn30_pro_plus_switch(stick_deadzone=0.1):
    """The 8BitDo SN30 Pro+ in its Switch mode. L2 and R2 are buttons here, and Star sends."""
    pad = Gamepad("8BitDo SN30 Pro+ gamepad")
    __register_8bitdo_switch_buttons(pad)

    # Direction pad as a hat nibble, then four 16 bit stick axes.
    pad.register_hat(32, first=0, report_id=0x3F)
    pad.register_axis("LX", 40, 16, deadzone=stick_deadzone, report_id=0x3F)
    pad.register_axis("LY", 56, 16, deadzone=stick_deadzone, invert=True, report_id=0x3F)
    pad.register_axis("RX", 72, 16, deadzone=stick_deadzone, report_id=0x3F)
    pad.register_axis("RY", 88, 16, deadzone=stick_deadzone, invert=True, report_id=0x3F)
    return pad


def create_8bitdo_sn30_switch():
    """The 8BitDo SN30 in its Switch mode.

    The direction pad arrives on the left stick fields. The buttons the pad lacks, L2, R2, the
    stick clicks, Home and Star, never press.
    """
    pad = Gamepad("8BitDo SN30 gamepad")
    __register_8bitdo_switch_buttons(pad)
    pad.register_axis_buttons("Left", "Right", 40, 16, report_id=0x3F)
    pad.register_axis_buttons("Up", "Down", 56, 16, report_id=0x3F)
    return pad
