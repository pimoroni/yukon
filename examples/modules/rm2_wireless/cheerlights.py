import network
import requests
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT2 as STRIP_SLOT
from pimoroni_yukon import SLOT5 as RM2_SLOT
from pimoroni_yukon.modules import LEDStripModule, WirelessModule


"""
Obtain the current CheerLights colour from the internet and show it on an LED Strip connected to Yukon.
For more information about CheerLights, visit: https://cheerlights.com/

This example requires a secrets.py file to be on your board's file system with the credentials of your WiFi network.

Hold "Boot" to exit the program (can take up to 5 seconds).
"""

try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
    if len(WIFI_SSID) == 0:
        raise ValueError("no WiFi network set. Open the 'secrets.py' file on your device to add your WiFi credentials")
except ImportError:
    raise ImportError("no module named 'secrets'. Create a 'secrets.py' file on your device with your WiFi credentials")


# Constants
COLOUR_NAMES = ("R", "G", "B")
CONNECTION_INTERVAL = 1.0               # The time to sleep between each connection check
REQUEST_INTERVAL = 5.0                  # The time to sleep between each internet request
STRIP_TYPE = LEDStripModule.NEOPIXEL    # Change to LEDStripModule.DOTSTAR for APA102 style strips
                                        # Two Neopixel strips can be driven too, by using LEDStripModule.DUAL_NEOPIXEL
STRIP_PIO = 0                           # The PIO system to use (0 or 1) to drive the strip(s)
STRIP_SM = 0                            # The State Machines (SM) to use to drive the strip(s)
LEDS_PER_STRIP = 60                     # How many LEDs are on the strip. If using DUAL_NEOPIXEL this can be a single value or a list or tuple
BRIGHTNESS = 1.0                        # The max brightness of the LEDs (only supported by APA102s)

# Variables
yukon = Yukon()                         # Create a new Yukon object
leds = LEDStripModule(STRIP_TYPE,       # Create a LEDStripModule object, with the details of the attached strip(s)
                      STRIP_PIO,
                      STRIP_SM,
                      LEDS_PER_STRIP,
                      BRIGHTNESS)
wireless = WirelessModule()             # Create a WirelessModule object


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(leds, STRIP_SLOT)      # Register the LEDStripModule object with the slot
    yukon.register_with_slot(wireless, RM2_SLOT)    # Register the WirelessModule object with the slot
    yukon.verify_and_initialise()                   # Verify that the modules are attached to Yukon, and initialise them

    wlan = network.WLAN(network.STA_IF)             # Create a new network object for interacting with WiFi
    wlan.active(True)                               # Turn on WLAN communications

    # Connect to WLAN
    print(f"Connecting to network '{WIFI_SSID}'")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # Wait until the connection is established
    while not wlan.isconnected():
        print('Waiting for connection...')
        yukon.monitored_sleep(CONNECTION_INTERVAL)

    # Print out our IP address
    print(f'Connected on {wlan.ifconfig()[0]}')

    # Turn on power to the module slots and the LED strip
    yukon.enable_main_output()
    leds.enable()

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Get the current CheerLights colour from the internet
        req = requests.get("http://api.thingspeak.com/channels/1417/field/2/last.json")
        json = req.json()
        req.close()

        # Use the second to get the colour components for the RGB output
        colour = tuple(int(json['field2'][i:i + 2], 16) for i in (1, 3, 5))

        # Print out the Cheerlights colour
        for i in range(len(colour)):
            print(f"{COLOUR_NAMES[i]} = {colour[i]}", end=", ")
        print()

        # Apply the colour to all the LEDs and send them to the strip
        for led in range(leds.strip.num_leds()):
            leds.strip.set_rgb(led, *colour)
        leds.strip.update()

        # Monitor sensors for a number of seconds, recording the min, max, and average for each
        yukon.monitored_sleep(REQUEST_INTERVAL)


finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()

    # Attempt to disconnect from WiFi
    try:
        wlan.disconnect()
    except Exception:
        pass
