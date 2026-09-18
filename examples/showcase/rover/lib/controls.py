# How the rover is driven from a game pad. Each scheme is given the pad and returns forward and
# steering, both -1.0 to 1.0, which mix() turns into a speed for each side of the chassis.


def sticks(pad):
    """Left stick for forward and back, right stick for steering."""
    return pad.read_axis("LY"), pad.read_axis("RX")


def triggers(pad):
    """Triggers for throttle, right stick for steering.

    R2 drives forward and L2 back, so holding both cancels out. Needs a pad whose triggers are
    analogue, which for 8BitDo pads means X-input or Android mode.
    """
    return pad.read_axis("R2") - pad.read_axis("L2"), pad.read_axis("RX")


def mix(forward, steer):
    """The left and right speeds for a forward and steering input, left negated for its mounting.

    Steering is scaled by the forward input, so the rover turns only while it is moving. It has
    too much ground friction to skid steer on the spot, whatever the motors are asked for.
    """
    steer *= forward
    return -forward - steer, forward - steer
