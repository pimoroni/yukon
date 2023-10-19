import time
import math
import struct
from machine import I2S
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT6 as SLOT
from pimoroni_yukon.modules import AudioAmpModule

"""
How to play a pure sinewave tone out of an Audio Amp Module connected to Slot1.
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
SONG = ("F6", "F6", "E6", "F6", "F5", "P", "F5", "P", "C6", "AS5", "A5", "C6", "F6", "P", "F6", "P", "G6", "FS6", "G6", "G5", "P", "G5", "P", "G6", "F6", "E6", "D6", "C6", "P", "C6", "P", "D6", "E6", "F6", "E6", "D6", "C6", "D6", "C6", "AS5", "A5", "AS5", "A5", "G5", "F5", "G5", "F5", "E5", "D5", "C5", "D5", "E5", "F5", "G5", "AS5", "A5", "G5", "A5", "F5", "P", "F5")

NOTE_DURATION = 0.150           # The time (in seconds) to play each note for. Change this to make the song play faster or slower


# Constants
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 20000
TONE_FREQUENCY_IN_HZ = 1000
SAMPLE_SIZE_IN_BITS = 16
FORMAT = I2S.MONO  # only MONO supported in this example
SAMPLE_RATE_IN_HZ = 44_100
SLEEP = 1.0                                 # The time to sleep between each reading

# Variables
yukon = Yukon()                 # Create a new Yukon object
amp = AudioAmpModule()          # Create an AudioAmpModule object
audio_out = None                # Stores the I2S audio output object created later
samples = None

is_playing = False

# Callback function to queue up the next section of audio
def i2s_callback(arg):
    global audio_out
    global samples
    if samples != None:
        audio_out.write(samples)
    else:
        audio_out.deinit()


# Using this for testing: https://github.com/miketeachman/micropython-i2s-examples/tree/master
def make_silence(rate, bits, frequency=1000):
    # create a buffer containing the pure tone samples
    samples_per_cycle = rate // frequency
    sample_size_in_bytes = bits // 8
    samples = bytearray(2 * samples_per_cycle * sample_size_in_bytes)
    range = pow(2, bits) // 2
    
    if bits == 16:
        format = "<h"
    else:  # assume 32 bits
        format = "<l"
    
    # I had to extend the sine buffer as it completed too quickly for code to react, causing drop outs
    for i in range(samples_per_cycle * 2):
        sample = range
        struct.pack_into(format, samples, i * sample_size_in_bytes, sample)

    return samples

# Using this for testing: https://github.com/miketeachman/micropython-i2s-examples/tree/master
def make_tone(rate, bits, frequency, volume=0.2):
    complete_waves = 2
    if volume < 0.0 or volume > 1.0:
        raise ValueError("volume out of range. Expected 0.0 to 1.0")

    # create a buffer containing the pure tone samples
    samples_per_cycle = rate // frequency
    sample_size_in_bytes = bits // 8
    samples = bytearray(complete_waves * samples_per_cycle * sample_size_in_bytes)
    range = pow(2, bits) // 2
    
    format = "<h" if bits == 16 else "<l"
    
    # I had to extend the sine buffer as it completed too quickly for code to react, causing drop outs
    for i in range(samples_per_cycle * complete_waves):
        sample = range + int((range - 1) * (math.sin(2 * math.pi * i / samples_per_cycle)) * volume)
        struct.pack_into(format, samples, i * sample_size_in_bytes, sample)
        
    print(samples_per_cycle * 2)

    return samples




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

def play_silence():
    global audio_out
    global samples
    print("silence")
    samples = bytearray(1000)#make_silence(SAMPLE_RATE_IN_HZ, SAMPLE_SIZE_IN_BITS)
    audio_out.write(samples)   
    pass

def play_tone(frequency):
    global audio_out
    global samples
    print(f"{frequency}Hz")
    samples = make_tone(SAMPLE_RATE_IN_HZ, SAMPLE_SIZE_IN_BITS, frequency)
    audio_out.write(samples)   
    pass

def stop_playing():
    global audio_out
    print("stop")
    audio_out.deinit()   
    pass



# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(amp, SLOT)     # Register the AudioAmpModule object with the slot
    yukon.verify_and_initialise()           # Verify that a AudioAmpModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots

    audio_out = I2S(
        I2S_ID,
        sck=amp.I2S_CLK,
        ws=amp.I2S_FS,
        sd=amp.I2S_DATA,
        mode=I2S.TX,
        bits=SAMPLE_SIZE_IN_BITS,
        format=I2S.MONO,
        rate=SAMPLE_RATE_IN_HZ,
        ibuf=BUFFER_LENGTH_IN_BYTES,
    )

    # Enable the switched outputs
    amp.enable()                            # Enable the audio amp. This includes I2C configuration
    amp.set_volume(0.3)                     # Set the output volume of the audio amp

    audio_out.irq(i2s_callback)             # i2s_callback is called when buf is emptied
    play_silence()
    
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():
        
        yukon.set_led('A', button_toggle)
        
        # Has the button been toggled?
        if check_button_toggle():

            # Play the song
            for i in range(len(SONG)):
                if check_button_toggle():
                    if SONG[i] == "P":
                        # This is a "pause" note, so stop the motors
                        play_silence()
                    else:
                        # Get the frequency of the note and play it
                        play_tone(TONES[SONG[i]])

                    yukon.monitored_sleep(NOTE_DURATION)

            button_toggle = False

            play_silence()

        yukon.monitor_once()

finally:
    if audio_out is not None:
        audio_out.deinit()
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
