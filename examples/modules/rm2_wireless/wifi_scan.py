import time
import network
import binascii
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT5 as SLOT
from pimoroni_yukon.modules import RM2WirelessModule

"""
Periodically scan for available WiFi networks using a RM2 Wireless Module connected to Slot 5,
and print out their details.

Hold "Boot" to exit the program (can take up to 5 seconds).
"""

# Constants
SCAN_INTERVAL = 5.0             # The time to sleep between each network scan

# Variables
yukon = Yukon()                 # Create a new Yukon object, with a lower voltage limit set
module = RM2WirelessModule()    # Create a RM2WirelessModule object


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)  # Register the RM2WirelessModule object with the slot
    yukon.verify_and_initialise()           # Verify that a RM2WirelessModule is attached to Yukon, and initialise it

    wlan = network.WLAN(network.STA_IF)     # Create a new network object for interacting with WiFi
    wlan.active(True)                       # Turn on WLAN communications

    while not yukon.is_boot_pressed():
        # Scan for nearby networks and print them out
        networks = wlan.scan()                  # Returns a list of tuples with 6 fields: ssid, bssid, channel, RSSI, security, hidden
        for i, w in enumerate(networks):
            print(i, w[0].decode(), binascii.hexlify(w[1]).decode(),
                  w[2], w[3], w[4], w[5])
        print()

        time.sleep(SCAN_INTERVAL)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()

    # Attempt to disconnect from WiFi
    try:
        wlan.disconnect()
    except Exception:
        pass
