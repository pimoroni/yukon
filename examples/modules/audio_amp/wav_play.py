from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import AudioAmpModule

"""
Play wave files out of an Audio Amp Module connected to Slot1.
You will need to copy the files "ahoy.wav" and "bye.wav" over to the root of your Yukon's filesystem.

Press "A" to start the first WAV file, or stop if anything is already playing.
Press "B" to start the second WAV file, or stop if anything is already playing.
Press "Boot/User" to exit the program.
"""

# Constants
I2S_ID = 0                  # The I2S instance to use for audio (only 0 and 1 supported)
WAV_FILE_A = "ahoy.wav"     # The first wave file. Make sure this file is present in the root directory of your Yukon
WAV_FILE_B = "bye.wav"      # The second wave file. Make sure this file is present in the root directory of your Yukon
VOLUME_A = 0.6              # The volume (between 0.0 and 1.0) to play the first file at
VOLUME_B = 0.6              # The volume (between 0.0 and 1.0) to play the second file at

# Variables
yukon = Yukon()                                 # Create a new Yukon object
amp = AudioAmpModule(I2S_ID)                    # Create an AudioAmpModule object
last_button_states = {'A': False, 'B': False}   # The last states of the buttons


# Function to check if the button has been newly pressed
def button_newly_pressed(btn):
    global last_button_states
    button_state = yukon.is_pressed(btn)
    button_pressed = button_state and not last_button_states[btn]
    last_button_states[btn] = button_state

    return button_pressed


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(amp, SLOT)     # Register the AudioAmpModule object with the slot
    yukon.verify_and_initialise()           # Verify that a AudioAmpModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots

    amp.enable()                            # Enable the audio amplifier

    print()  # New line
    print("Controls:")
    print(f"- Press 'A' to play '{WAV_FILE_A}', or stop what is currently playing")
    print(f"- Press 'B' to play '{WAV_FILE_B}', or stop what is currently playing")
    print()  # New line

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Has the button been pressed?
        if button_newly_pressed('A'):
            # Is nothing playing?
            if not amp.player.is_playing():
                amp.player.play_wav(WAV_FILE_A)     # Play file A
                amp.set_volume(VOLUME_A)            # Set the volume to play file A at
                yukon.set_led('A', True)            # Show that file A is playing
                print("Playing the first WAV file")
            else:
                amp.player.stop()                   # Stop whichever file is currently playing
                print("Stopping playback")

        # Has the button been pressed?
        if button_newly_pressed('B'):
            # Is nothing playing?
            if not amp.player.is_playing():
                amp.player.play_wav(WAV_FILE_B)     # Play file B
                amp.set_volume(VOLUME_B)            # Set the volume to play file B at
                yukon.set_led('B', True)            # Show that file B is playing
                print("Playing the second WAV file")
            else:
                amp.player.stop()                   # Stop whichever file is currently playing
                print("Stopping playback")

        # Has either file stopped playing?
        if not amp.player.is_playing():
            yukon.set_led('A', False)
            yukon.set_led('B', False)

        # Perform a single check of Yukon's internal voltage, current, and temperature sensors
        yukon.monitor_once()

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
