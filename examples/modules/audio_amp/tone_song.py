from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT1 as SLOT
from pimoroni_yukon.modules import AudioAmpModule

"""
Play a sequence of tones out of an Audio Amp Module connected to Slot1.

Press "A" to start or stop the tone song.
Press "Boot/User" to exit the program.
"""

# This handy list converts notes into frequencies, which you can use with the inventor.play_tone function
TONES = {
    "B0": 31,
    "C1": 33,
    "CS1": 35,
    "D1": 37,
    "DS1": 39,
    "E1": 41,
    "F1": 44,
    "FS1": 46,
    "G1": 49,
    "GS1": 52,
    "A1": 55,
    "AS1": 58,
    "B1": 62,
    "C2": 65,
    "CS2": 69,
    "D2": 73,
    "DS2": 78,
    "E2": 82,
    "F2": 87,
    "FS2": 93,
    "G2": 98,
    "GS2": 104,
    "A2": 110,
    "AS2": 117,
    "B2": 123,
    "C3": 131,
    "CS3": 139,
    "D3": 147,
    "DS3": 156,
    "E3": 165,
    "F3": 175,
    "FS3": 185,
    "G3": 196,
    "GS3": 208,
    "A3": 220,
    "AS3": 233,
    "B3": 247,
    "C4": 262,
    "CS4": 277,
    "D4": 294,
    "DS4": 311,
    "E4": 330,
    "F4": 349,
    "FS4": 370,
    "G4": 392,
    "GS4": 415,
    "A4": 440,
    "AS4": 466,
    "B4": 494,
    "C5": 523,
    "CS5": 554,
    "D5": 587,
    "DS5": 622,
    "E5": 659,
    "F5": 698,
    "FS5": 740,
    "G5": 784,
    "GS5": 831,
    "A5": 880,
    "AS5": 932,
    "B5": 988,
    "C6": 1047,
    "CS6": 1109,
    "D6": 1175,
    "DS6": 1245,
    "E6": 1319,
    "F6": 1397,
    "FS6": 1480,
    "G6": 1568,
    "GS6": 1661,
    "A6": 1760,
    "AS6": 1865,
    "B6": 1976,
    "C7": 2093,
    "CS7": 2217,
    "D7": 2349,
    "DS7": 2489,
    "E7": 2637,
    "F7": 2794,
    "FS7": 2960,
    "G7": 3136,
    "GS7": 3322,
    "A7": 3520,
    "AS7": 3729,
    "B7": 3951,
    "C8": 4186,
    "CS8": 4435,
    "D8": 4699,
    "DS8": 4978
}

# Put the notes for your song in here!
SONG = ("F6", "F6", "E6", "F6", "F5", "P", "F5", "P", "C6", "AS5", "A5", "C6", "F6", "P", "F6", "P",
        "G6", "FS6", "G6", "G5", "P", "G5", "P", "G6", "F6", "E6", "D6", "C6", "P", "C6", "P", "D6",
        "E6", "F6", "E6", "D6", "C6", "D6", "C6", "AS5", "A5", "AS5", "A5", "G5", "F5", "G5", "F5", "E5",
        "D5", "C5", "D5", "E5", "F5", "G5", "AS5", "A5", "G5", "A5", "F5", "P", "F5")


# Constants
I2S_ID = 0                      # The I2S instance to use for outputting audio
NOTE_DURATION = 0.150           # The time (in seconds) to play each note for. Change this to make the song play faster or slower
NOTE_VOLUME = 0.6               # The volume (between 0.0 and 1.0) to play the notes at

# Variables
yukon = Yukon()                 # Create a new Yukon object
amp = AudioAmpModule(I2S_ID)    # Create an AudioAmpModule object


# Variables for recording the button state and if it has been toggled
# Starting as True makes the song play automatically
button_toggle = True
last_button_state = False


# Function to check if the button has been toggled
def check_button_toggle():
    global button_toggle
    global last_button_state
    button_state = yukon.is_pressed('A')
    if button_state and not last_button_state:
        button_toggle = not button_toggle
        yukon.set_led('A', button_toggle)
    last_button_state = button_state

    return button_toggle


# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(amp, SLOT)     # Register the AudioAmpModule object with the slot
    yukon.verify_and_initialise()           # Verify that a AudioAmpModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots

    amp.enable()                            # Enable the audio amp. This includes I2C configuration
    amp.set_volume(NOTE_VOLUME)             # Set the output volume of the audio amp

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        yukon.set_led('A', button_toggle)

        # Has the button been toggled?
        if check_button_toggle():

            # Play the song
            for i in range(len(SONG)):
                if check_button_toggle():
                    if SONG[i] == "P":
                        # Pause for the duration of this note
                        amp.player.pause()
                    else:
                        # Get the frequency of the note and play it
                        amp.player.play_tone(TONES[SONG[i]], 1.0)

                    yukon.monitored_sleep(NOTE_DURATION)

            button_toggle = False

            amp.player.stop()

        # Perform a single check of Yukon's internal voltage, current, and temperature sensors
        yukon.monitor_once()

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
