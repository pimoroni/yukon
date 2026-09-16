import time
import bluetooth
import btclassic
import pad_keys
from pimoroni_yukon import Yukon
from keyboard import Keyboard

"""
Type into Yukon from a Bluetooth keyboard paired straight to the board, using the RM2 Wireless
Module. Pairing works as for the game pad example, and the keyboard shares its link key file.

LED A is lit while waiting for a keyboard, LED B while one is connected, and LED B blinks off on
each key press. Every press and release is printed by name, and each line typed is printed when
Enter is pressed.

Press "Boot/User" to exit the program.
"""

# Constants
INQUIRY_SECONDS = 8                 # How long to look for a keyboard in pairing mode when none is stored
CONNECT_TIMEOUT_MS = 20000          # How long to give a connection attempt before trying again
RETRY_INTERVAL_MS = 5000            # How long to wait between attempts to reach a stored device
PAGING_WINDOW_MS = 30000            # How long to keep paging stored devices after start up or a lost one
PERIPHERAL_CLASS = 0x05             # The major device class that keyboards and game pads report
KEYBOARD_MINOR = 0x10               # The keyboard bit of the minor device class
UPDATE_MS = 10                      # How often to read the keyboard
BLINK_MS = 100                      # How long LED B goes off for on a key press

# Variables
yukon = Yukon()                     # A new Yukon object
ble = bluetooth.BLE()               # The Bluetooth stack, which must be active before btclassic is used
keyboard = Keyboard()               # The keyboard's keys, decoded from its reports
last_attempt = None                 # When a stored device was last paged
next_device = 0                     # Which stored device to page next
paging_until = time.ticks_add(time.ticks_ms(), PAGING_WINDOW_MS)    # When to stop paging and just listen
was_connected = False               # Whether a keyboard was connected on the last pass
blink_until = time.ticks_ms()       # When LED B comes back on after a press
line = ""                           # The characters typed since the last Enter


def address_text(address):
    return ":".join("%02X" % b for b in address)


def find_keyboard_in_pairing_mode():
    """Look for a discoverable keyboard and return its address, or None."""
    print("Looking for a keyboard in pairing mode ...")
    btclassic.inquiry_start(INQUIRY_SECONDS)
    while btclassic.inquiry_active():
        time.sleep_ms(100)
    for address, device_class, rssi, name in btclassic.inquiry_results():
        if (device_class >> 8) & 0x1F == PERIPHERAL_CLASS and (device_class >> 2) & KEYBOARD_MINOR:
            print("Found", name or "a keyboard", "at", address_text(address))
            return address
    print("No keyboard found")
    return None


def wait_for_connection():
    """Wait for a connection attempt to finish, returning whether it succeeded."""
    start = time.ticks_ms()
    while btclassic.state()[0] == btclassic.STATE_CONNECTING:
        if time.ticks_diff(time.ticks_ms(), start) > CONNECT_TIMEOUT_MS or yukon.is_boot_pressed():
            return False
        time.sleep_ms(50)
    return btclassic.state()[0] == btclassic.STATE_CONNECTED


def key_changed(name, pressed):
    global blink_until
    if pressed:
        blink_until = time.ticks_add(time.ticks_ms(), BLINK_MS)
    print(name, "down" if pressed else "up")


keyboard.on_key(key_changed)

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    ble.active(True)
    known = pad_keys.load()         # Put any saved link keys back into the stack
    btclassic.connectable(True)     # Now let devices connect to us
    if known:
        print("Stored devices:", ", ".join(address_text(address) for address in known))

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():
        state = btclassic.state()[0]

        if state == btclassic.STATE_CONNECTED:
            yukon.set_led('A', False)
            keyboard.update()
            for character in keyboard.typed():
                if character == "\n":
                    print("Typed:", line)
                    line = ""
                else:
                    line += character
            yukon.set_led('B', time.ticks_diff(time.ticks_ms(), blink_until) >= 0)
            time.sleep_ms(UPDATE_MS)
            was_connected = True
            continue

        yukon.set_led('B', False)
        yukon.set_led('A', True)
        keyboard.reset()
        if was_connected:
            was_connected = False
            paging_until = time.ticks_add(time.ticks_ms(), PAGING_WINDOW_MS)

        if known:
            # A keyboard switched on connects by itself. One that lost us waits to be paged for a
            # while, so page each stored device in turn for that long, then only listen.
            if state != btclassic.STATE_CONNECTING and time.ticks_diff(paging_until, time.ticks_ms()) > 0:
                if last_attempt is None or time.ticks_diff(time.ticks_ms(), last_attempt) > RETRY_INTERVAL_MS:
                    last_attempt = time.ticks_ms()
                    btclassic.connect(known[next_device])
                    next_device = (next_device + 1) % len(known)
            time.sleep_ms(50)
        else:
            address = find_keyboard_in_pairing_mode()
            if address is not None:
                btclassic.connect(address)
                if wait_for_connection():
                    pad_keys.save()
                    known = pad_keys.load()
                    print("Paired and saved. From now on just switch the keyboard on.")

finally:
    btclassic.disconnect()
    yukon.set_led('A', False)
    yukon.set_led('B', False)
    ble.active(False)
