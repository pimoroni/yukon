from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import AudioAmpModule

"""
How to play wave filex out of an Audio Amp Module connected to Slot1.
"""

WAV_FILE_A = "ahoy.wav"
WAV_FILE_B = "Turret_turret_autosearch_4.wav"
I2S_ID = 0    # The I2S instance to use for audio (only 0 and 1 supported)

# Variables
yukon = Yukon()                 # Create a new Yukon object
amp = AudioAmpModule(I2S_ID)    # Create an AudioAmpModule object

# Variables for recording the button state and if it has been toggled
# Starting as True makes the song play automatically
last_button_state = {'A': False, 'B': False}


# Function to check if the button has been toggled
def check_button_toggle(btn):
    global last_button_state
    button_state = yukon.is_pressed(btn)
    if button_state and not last_button_state[btn]:
        button_toggle = True
        yukon.set_led(btn, button_toggle)
    else:
        button_toggle = False
    last_button_state[btn] = button_state

    return button_toggle


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(amp, SLOT)     # Register the AudioAmpModule object with the slot
    yukon.verify_and_initialise()           # Verify that a AudioAmpModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots

    amp.enable()

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Has the button been toggled?
        if check_button_toggle('A'):
            if not amp.player.is_playing():
                amp.player.play_wav(WAV_FILE_A, loop=False)
                amp.set_volume(0.6)
                yukon.set_led('A', True)
            else:
                amp.player.stop()

        # Has the button been toggled?
        if check_button_toggle('B'):
            if not amp.player.is_playing():
                amp.player.play_wav(WAV_FILE_B, loop=False)
                amp.set_volume(0.6)
                yukon.set_led('B', True)
            else:
                amp.player.stop()

        if not amp.player.is_playing():
            yukon.set_led('A', False)
            yukon.set_led('B', False)

        yukon.monitored_sleep(0.1)
        yukon.print_readings()

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
