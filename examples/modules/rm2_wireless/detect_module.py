from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT5 as SLOT
from pimoroni_yukon.modules import WirelessModule

"""
A boilerplate example showing how to detect if the RM2 Wireless Module
is attached to Yukon prior to performing any wireless operations.
"""

# Variables
yukon = Yukon()             # Create a new Yukon object, with a lower voltage limit set
module = WirelessModule()   # Create a WirelessModule object

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(module, SLOT)  # Register the WirelessModule object with the slot
    yukon.verify_and_initialise()           # Verify that a WirelessModule is attached to Yukon, and initialise it

    # Do wireless things here

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()

    # Disconnect from wireless here
