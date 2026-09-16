# Turns a Bluetooth keyboard's raw HID reports, as btclassic delivers them, into key presses and
# releases with names, and into typed characters for a US layout. Only the boot protocol report,
# id 1 with a modifier byte, a reserved byte and six key slots, is decoded. Keyboards also send
# a bitmap report for more than six keys and consumer and system control reports, which are
# ignored. update() has to be called regularly to pull new reports in.
import btclassic

REPORT_ID = 1
MODIFIERS = ("LeftCtrl", "LeftShift", "LeftAlt", "LeftGUI", "RightCtrl", "RightShift", "RightAlt", "RightGUI")

# HID usage to (unshifted, shifted) character, US layout.
CHARACTERS = {
    0x2C: (" ", " "), 0x28: ("\n", "\n"), 0x2B: ("\t", "\t"),
    0x2D: ("-", "_"), 0x2E: ("=", "+"), 0x2F: ("[", "{"), 0x30: ("]", "}"), 0x31: ("\\", "|"),
    0x33: (";", ":"), 0x34: ("'", '"'), 0x35: ("`", "~"), 0x36: (",", "<"), 0x37: (".", ">"), 0x38: ("/", "?"),
}
for i, digit in enumerate("1234567890"):
    CHARACTERS[0x1E + i] = (digit, "!@#$%^&*()"[i])
for i in range(26):
    CHARACTERS[0x04 + i] = (chr(ord("a") + i), chr(ord("A") + i))

# HID usage to key name for keys that type nothing.
NAMES = {
    0x29: "Escape", 0x2A: "Backspace", 0x39: "CapsLock", 0x4C: "Delete", 0x4F: "Right", 0x50: "Left",
    0x51: "Down", 0x52: "Up", 0x4A: "Home", 0x4D: "End", 0x4B: "PageUp", 0x4E: "PageDown", 0x49: "Insert",
    0x46: "PrintScreen", 0x47: "ScrollLock", 0x48: "Pause",
}
for i in range(12):
    NAMES[0x3A + i] = "F%d" % (i + 1)


def key_name(usage):
    """The name of a key usage, its unshifted character for keys that type one."""
    if usage in CHARACTERS:
        character = CHARACTERS[usage][0]
        return {" ": "Space", "\n": "Enter", "\t": "Tab"}.get(character, character)
    return NAMES.get(usage, "Key%02X" % usage)


class Keyboard:
    def __init__(self):
        self.modifiers = set()     # Names of the modifiers currently held
        self.keys = set()          # Usages of the keys currently held
        self.key_callback = None   # Called with (name, pressed) on each change
        self.__typed = []

    def on_key(self, callback):
        """Set the callback for every key press and release, called with the key name and True or False."""
        self.key_callback = callback

    def shifted(self):
        return "LeftShift" in self.modifiers or "RightShift" in self.modifiers

    def typed(self):
        """The characters typed since the last call, as a string."""
        text = "".join(self.__typed)
        self.__typed = []
        return text

    def reset(self):
        self.modifiers = set()
        self.keys = set()

    def update(self):
        """Decode every waiting report."""
        while True:
            report = btclassic.report()
            if report is None:
                return
            data = report[1]
            if len(data) < 10 or data[1] != REPORT_ID:
                continue
            modifiers = {MODIFIERS[i] for i in range(8) if data[2] & (1 << i)}
            keys = {usage for usage in data[4:10] if usage != 0}
            for name in sorted(modifiers - self.modifiers):
                self.__changed(name, True)
            for name in sorted(self.modifiers - modifiers):
                self.__changed(name, False)
            self.modifiers = modifiers
            for usage in sorted(keys - self.keys):
                if usage in CHARACTERS:
                    self.__typed.append(CHARACTERS[usage][1 if self.shifted() else 0])
                self.__changed(key_name(usage), True)
            for usage in sorted(self.keys - keys):
                self.__changed(key_name(usage), False)
            self.keys = keys

    def __changed(self, name, pressed):
        if self.key_callback is not None:
            self.key_callback(name, pressed)
