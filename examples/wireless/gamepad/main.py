import time
import bluetooth
import btclassic
import pad_keys
from pimoroni_yukon import Yukon
from gamepad_mappings import create_8bitdo_lite

"""
Drive Yukon from a Bluetooth game pad paired straight to the board, using the RM2 Wireless Module.

The first time, put the pad into pairing mode. Yukon finds it, pairs, and saves the link key to a
file on the board. From then on switching the pad on is enough, and if Yukon restarts while the pad
is on it reconnects to the pad by itself.

LED A is lit while waiting for a pad, LED B while one is connected, and LED B blinks off on each
button press or axis movement. Every change of a button or axis is printed.

Press "Boot/User" to exit the program.
"""

# Constants
PAD_MAPPING = create_8bitdo_lite    # The mapping function for the pad in use, see gamepad_mappings.py
INQUIRY_SECONDS = 8                 # How long to look for a pad in pairing mode when none is stored
CONNECT_TIMEOUT_MS = 20000          # How long to give a connection attempt before trying again
RETRY_INTERVAL_MS = 5000            # How long to wait between attempts to reach a stored pad
PAGING_WINDOW_MS = 30000            # How long to keep paging stored pads after start up or a lost pad
GAMEPAD_CLASS = 0x05                # The major device class that game pads report in an inquiry
UPDATE_MS = 10                      # How often to read the pad
BLINK_MS = 100                      # How long LED B goes off for on a press or movement

# Variables
yukon = Yukon()                     # A new Yukon object
ble = bluetooth.BLE()               # The Bluetooth stack, which must be active before btclassic is used
pad = PAD_MAPPING()                 # The pad's controls, decoded from its reports
last_attempt = None                 # When a stored pad was last paged
next_pad = 0                        # Which stored pad to page next, when more than one is stored
paging_until = time.ticks_add(time.ticks_ms(), PAGING_WINDOW_MS)    # When to stop paging and just listen
was_connected = False               # Whether a pad was connected on the last pass
blink_until = time.ticks_ms()       # When LED B comes back on after a press


def address_text(address):
    return ":".join("%02X" % b for b in address)


def find_pad_in_pairing_mode():
    """Look for a discoverable pad and return its address, or None."""
    print("Looking for a pad in pairing mode ...")
    btclassic.inquiry_start(INQUIRY_SECONDS)
    while btclassic.inquiry_active():
        time.sleep_ms(100)
    for address, device_class, rssi, name in btclassic.inquiry_results():
        if (device_class >> 8) & 0x1F == GAMEPAD_CLASS:
            print("Found", name or "a pad", "at", address_text(address))
            return address
    print("No pad found")
    return None


def wait_for_connection():
    """Wait for a connection attempt to finish, returning whether it succeeded."""
    start = time.ticks_ms()
    while btclassic.state()[0] == btclassic.STATE_CONNECTING:
        if time.ticks_diff(time.ticks_ms(), start) > CONNECT_TIMEOUT_MS or yukon.is_boot_pressed():
            return False
        time.sleep_ms(50)
    return btclassic.state()[0] == btclassic.STATE_CONNECTED


def print_state():
    """Print every held button and every axis away from rest on one line."""
    held = [button.name for button in pad.buttons if button.pressed]
    moved = ["%s %+.2f" % (axis.name, axis.value) for axis in pad.axes if axis.value != 0.0]
    print("Buttons:", ", ".join(held) if held else "-", "|", " ".join(moved) if moved else "-")


def blink_and_print():
    global blink_until
    blink_until = time.ticks_add(time.ticks_ms(), BLINK_MS)
    print_state()


for button in pad.buttons:
    pad.on_button(button.name, pressed=blink_and_print, released=print_state)
for axis in pad.axes:
    pad.on_axis(axis.name, lambda value: blink_and_print() if value != 0.0 else print_state())

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    ble.active(True)
    known = pad_keys.load()         # Put any saved link keys back into the stack
    btclassic.connectable(True)     # Now let pads connect to us
    if known:
        print("Stored pads:", ", ".join(address_text(address) for address in known))

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():
        state = btclassic.state()[0]

        if state == btclassic.STATE_CONNECTED:
            yukon.set_led('A', False)
            pad.update()
            yukon.set_led('B', time.ticks_diff(time.ticks_ms(), blink_until) >= 0)
            time.sleep_ms(UPDATE_MS)
            was_connected = True
            continue

        yukon.set_led('B', False)
        yukon.set_led('A', True)
        pad.reset()
        if was_connected:
            was_connected = False
            paging_until = time.ticks_add(time.ticks_ms(), PAGING_WINDOW_MS)

        if known:
            # A pad switched on pages us by itself, but one that lost us waits to be paged for about
            # half a minute. So page each stored pad in turn for that long after start up and after
            # a pad is lost, then only listen, since a page in progress turns away a pad paging us.
            if state != btclassic.STATE_CONNECTING and time.ticks_diff(paging_until, time.ticks_ms()) > 0:
                if last_attempt is None or time.ticks_diff(time.ticks_ms(), last_attempt) > RETRY_INTERVAL_MS:
                    last_attempt = time.ticks_ms()
                    btclassic.connect(known[next_pad])
                    next_pad = (next_pad + 1) % len(known)
            time.sleep_ms(50)
        else:
            address = find_pad_in_pairing_mode()
            if address is not None:
                btclassic.connect(address)
                if wait_for_connection():
                    pad_keys.save()
                    known = pad_keys.load()
                    print("Paired and saved. From now on just switch the pad on.")

finally:
    btclassic.disconnect()
    yukon.set_led('A', False)
    yukon.set_led('B', False)
    ble.active(False)
