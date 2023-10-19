import math
import struct
from machine import I2S
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT6 as SLOT
from pimoroni_yukon.modules import AudioAmpModule

"""
How to play a pure sinewave tone out of an Audio Amp Module connected to Slot1.
"""

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


# Callback function to queue up the next section of audio
def i2s_callback(arg):
    global audio_out
    global samples
    audio_out.write(samples)


# Using this for testing: https://github.com/miketeachman/micropython-i2s-examples/tree/master
def make_tone(rate, bits, frequency):
    # create a buffer containing the pure tone samples
    samples_per_cycle = rate // frequency
    sample_size_in_bytes = bits // 8
    samples = bytearray(4 * samples_per_cycle * sample_size_in_bytes)
    range = pow(2, bits) // 2
    
    if bits == 16:
        format = "<h"
    else:  # assume 32 bits
        format = "<l"
    
    # I had to extend the sine buffer as it completed too quickly for code to react, causing drop outs
    for i in range(samples_per_cycle * 4):
        sample = range + int((range - 1) * (math.sin(2 * math.pi * i / samples_per_cycle)) * 0.2)
        struct.pack_into(format, samples, i * sample_size_in_bytes, sample)

    return samples

# Wrap the code in a try block, to catch any exceptions (including KeyboardInterrupt)
try:
    yukon.register_with_slot(amp, SLOT)     # Register the AudioAmpModule object with the slot
    yukon.verify_and_initialise()           # Verify that a AudioAmpModule is attached to Yukon, and initialise it
    yukon.enable_main_output()              # Turn on power to the module slots

    # Construct a buffer containing the tone to play
    samples = make_tone(SAMPLE_RATE_IN_HZ, SAMPLE_SIZE_IN_BITS, TONE_FREQUENCY_IN_HZ)

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
    audio_out.write(samples)    

    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():

        # Monitor sensors for a number of seconds, recording the min, max, and average for each
        yukon.monitored_sleep(SLEEP)

        # Print out the average temperature of the Audio Amp Module over the monitoring period
        amp.print_readings(allowed=("T_avg"))

finally:
    if audio_out is not None:
        audio_out.deinit()
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
