# Named buttons and axes over the raw HID input reports that btclassic delivers.
#
# A Gamepad is built by a mapping function that registers each control with its position in a
# report. Buttons live at a byte and bit, axes at a bit offset with a width, a hat as a nibble whose
# values run clockwise from up. Offsets count from the start of the report as delivered, which is
# the HID DATA header, the report id, then the fields, so the first field byte is byte 2. A pad may
# use several report ids, and each control names the id it arrives in. Reads return the latest
# decoded state, and update() has to be called regularly to pull new reports in.
import btclassic

# Hat switch positions clockwise from Up. Any other value is centred.
HAT_DIRECTIONS = (
    ("Up",), ("Up", "Right"), ("Right",), ("Down", "Right"),
    ("Down",), ("Down", "Left"), ("Left",), ("Up", "Left"),
)


def _map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def _field(report, bit_offset, width):
    """The unsigned integer held in width bits at bit_offset, little endian."""
    value = 0
    for i in range(width):
        bit = bit_offset + i
        if report[bit >> 3] & (1 << (bit & 7)):
            value |= 1 << i
    return value


class Button:
    def __init__(self, name, alt_name):
        self.name = name
        self.alt_name = alt_name
        self.pressed = False
        self.pressed_callback = None
        self.released_callback = None

    def set(self, pressed):
        if pressed == self.pressed:
            return
        self.pressed = pressed
        callback = self.pressed_callback if pressed else self.released_callback
        if callback:
            callback()


class Axis:
    def __init__(self, name, alt_name, deadzone):
        self.name = name
        self.alt_name = alt_name
        self.deadzone = deadzone
        self.value = 0.0
        self.changed_callback = None

    def set(self, value):
        if -self.deadzone < value < self.deadzone:
            value = 0.0
        if value == self.value:
            return
        self.value = value
        if self.changed_callback:
            self.changed_callback(value)


class Gamepad:
    def __init__(self, name):
        self.name = name
        self.buttons = []
        self.axes = []
        # Per report id, the decoders to run and the shortest report they can read.
        self.__decoders = {}
        self.__lengths = {}
        self.__report_count = 0

    def __find(self, collection, name):
        for item in collection:
            if name in (item.name, item.alt_name):
                return item
        return None

    def __check_free(self, collection, name, alt_name):
        for candidate in (name, alt_name):
            if candidate is not None and self.__find(collection, candidate) is not None:
                raise ValueError("'%s' is already registered" % candidate)

    def __add_decoder(self, report_id, last_bit, decode):
        self.__decoders.setdefault(report_id, []).append(decode)
        needed = (last_bit >> 3) + 1
        if needed > self.__lengths.get(report_id, 0):
            self.__lengths[report_id] = needed

    # Registration, called by a mapping function

    def register_button(self, name, byte, bit, alt_name=None, report_id=1):
        self.__check_free(self.buttons, name, alt_name)
        button = Button(name, alt_name)
        self.buttons.append(button)
        mask = 1 << bit
        self.__add_decoder(report_id, byte * 8 + bit, lambda r: button.set(bool(r[byte] & mask)))

    def register_axis(self, name, bit_offset, width, alt_name=None, deadzone=0.0, invert=False, report_id=1):
        """A centred axis, reported as -1.0 to 1.0."""
        self.__check_free(self.axes, name, alt_name)
        axis = Axis(name, alt_name, deadzone)
        self.axes.append(axis)
        full = (1 << width) - 1
        low, high = (1.0, -1.0) if invert else (-1.0, 1.0)
        self.__add_decoder(report_id, bit_offset + width - 1,
                           lambda r: axis.set(_map(_field(r, bit_offset, width), 0, full, low, high)))

    def register_trigger(self, name, bit_offset, width, alt_name=None, deadzone=0.0, report_id=1):
        """A one sided axis, reported as 0.0 to 1.0."""
        self.__check_free(self.axes, name, alt_name)
        axis = Axis(name, alt_name, deadzone)
        self.axes.append(axis)
        full = (1 << width) - 1
        self.__add_decoder(report_id, bit_offset + width - 1,
                           lambda r: axis.set(_field(r, bit_offset, width) / full))

    def register_hat(self, bit_offset, width=4, first=1, report_id=1):
        """A direction pad reported as a hat switch, exposed as Up, Down, Left and Right buttons.

        first is the value that means Up, the hat's logical minimum in its report descriptor.
        """
        directions = {}
        for direction in ("Up", "Down", "Left", "Right"):
            self.__check_free(self.buttons, direction, None)
            directions[direction] = Button(direction, None)
            self.buttons.append(directions[direction])

        def decode(r):
            position = _field(r, bit_offset, width) - first
            active = HAT_DIRECTIONS[position] if 0 <= position < len(HAT_DIRECTIONS) else ()
            for direction, button in directions.items():
                button.set(direction in active)

        self.__add_decoder(report_id, bit_offset + width - 1, decode)

    def register_axis_buttons(self, low_name, high_name, bit_offset, width, report_id=1):
        """A direction pad reported as a centred axis, exposed as a button at each end."""
        for name in (low_name, high_name):
            self.__check_free(self.buttons, name, None)
        low, high = Button(low_name, None), Button(high_name, None)
        self.buttons.extend((low, high))
        centre = (1 << width) // 2

        def decode(r):
            value = _field(r, bit_offset, width)
            low.set(value < centre // 2)
            high.set(value >= centre + centre // 2)

        self.__add_decoder(report_id, bit_offset + width - 1, decode)

    # Callbacks

    def on_button(self, name, pressed=None, released=None):
        button = self.__find(self.buttons, name)
        if button is None:
            raise ValueError("no button '%s'" % name)
        button.pressed_callback = pressed
        button.released_callback = released

    def on_axis(self, name, changed):
        axis = self.__find(self.axes, name)
        if axis is None:
            raise ValueError("no axis '%s'" % name)
        axis.changed_callback = changed

    # Reading

    def read_button(self, name):
        button = self.__find(self.buttons, name)
        if button is None:
            raise ValueError("no button '%s'" % name)
        return button.pressed

    def read_axis(self, name):
        axis = self.__find(self.axes, name)
        if axis is None:
            raise ValueError("no axis '%s'" % name)
        return axis.value

    def is_connected(self):
        return btclassic.state()[0] == btclassic.STATE_CONNECTED

    def update(self):
        """Decode every report received since the last call. Returns how many were decoded."""
        decoded = 0
        while True:
            queued = btclassic.report()
            if queued is None:
                return decoded
            report = queued[1]
            if len(report) < 2:
                continue
            decoders = self.__decoders.get(report[1])
            if decoders is None or len(report) < self.__lengths[report[1]]:
                continue
            for decode in decoders:
                decode(report)
            decoded += 1

    def reset(self):
        for button in self.buttons:
            button.set(False)
        for axis in self.axes:
            axis.set(0.0)
