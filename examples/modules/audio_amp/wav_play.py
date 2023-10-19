import time
import math
import struct
from machine import I2S
from pimoroni_yukon import Yukon
from pimoroni_yukon import SLOT6 as SLOT
from pimoroni_yukon.modules import AudioAmpModule
import micropython
from collections import namedtuple

"""
How to play a wave file out of an Audio Amp Module connected to Slot1.
"""

WAV_FILE = "ahoy.wav"


# Constants
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 20000
TONE_FREQUENCY_IN_HZ = 1000
SAMPLE_SIZE_IN_BITS = 16
SAMPLE_RATE_IN_HZ = 44_100
SLEEP = 1.0                                 # The time to sleep between each reading

# Variables
yukon = Yukon()                 # Create a new Yukon object
amp = AudioAmpModule()          # Create an AudioAmpModule object
audio_out = None                # Stores the I2S audio output object created later
samples = None

is_playing = False

header = bytearray(44)


WavHeader = namedtuple("WavHeader", ("riff_desc",
                                     "file_size",
                                     "wave_fmt_desc",
                                     "chunk_size",
                                     "format",
                                     "channels",
                                     "frequency",
                                     "bytes_per_sec",
                                     "block_alignment",
                                     "bits_per_sample",
                                     "data_desc",
                                     "data_size"))


wav = open(WAV_FILE, "rb")

def parse_wav_file(wav):
    header = bytearray(44)
    bytes_read = wav.readinto(header)
    if bytes_read < 44:
        raise OSError("File too small")
    
    unpacked = WavHeader(*struct.unpack('<4sI8sIHHIIHH4sI', header))
    print(unpacked)
    
    if unpacked.riff_desc != b"RIFF":
        raise OSError("Invalid WAV file")

    if unpacked.wave_fmt_desc != b"WAVEfmt ":
        raise OSError("Invalid WAV file")
    
    if unpacked.data_desc != b"data":
        raise OSError("Invalid WAV file")

    if unpacked.chunk_size != 16:
        raise OSError("Invalid WAV file")

    if unpacked.format != 0x01:
        raise OSError("Invalid WAV file")
    
    if unpacked.bits_per_sample != 16:
        raise OSError(f"Invalid WAV file. Only 16 bits per sample is supported")
    
    if unpacked.frequency != 44_100 and unpacked.frequency != 48_000:
        raise OSError(f"Invalid WAV file frequency of {unpacked.frequency}Hz. Only 44.1Hz or 48KHz audio is supported")

    if unpacked.data_size == 0:
        raise OSError("No audio data")
    
    return unpacked


wav_header = parse_wav_file(wav)
    
pos = wav.seek(44)  # advance to first byte of Data section in WAV file

# allocate sample array
# memoryview used to reduce heap allocation
wav_samples = bytearray(10000)
wav_samples_mv = memoryview(wav_samples)


PLAY = 0
PAUSE = 1
RESUME = 2
STOP = 3
state = PAUSE

silence = bytearray(1000)

def eof_callback(arg):
    global state
    print("end of audio file")
    state = STOP  # uncomment to stop looping playback



# Callback function to queue up the next section of audio
def i2s_callback(arg):
    global state
    global wav_samples_mv
    global pos
    global wav
    if state == PLAY:
        num_read = wav.readinto(wav_samples_mv)
        # end of WAV file?
        if num_read == 0:
            # end-of-file, advance to first byte of Data section
            pos = wav.seek(44)
            play_silence()
            state = STOP
            micropython.schedule(eof_callback, None)
        else:
            _ = audio_out.write(wav_samples_mv[:num_read])
    elif state == RESUME:
        state = PLAY
        play_silence()
    elif state == PAUSE:
        play_silence()
    elif state == STOP:
        # cleanup
        wav.close()
        audio_out.deinit()
        print("Done")
    else:
        print("Not a valid state.  State ignored")


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
        bits=wav_header.bits_per_sample,
        format=I2S.STEREO if wav_header.channels > 1 else I2S.MONO,
        rate=wav_header.frequency,
        ibuf=BUFFER_LENGTH_IN_BYTES,
    )

    # Enable the switched outputs
    amp.enable()                            # Enable the audio amp. This includes I2C configuration
    amp.set_volume(0.5)                     # Set the output volume of the audio amp

    audio_out.irq(i2s_callback)             # i2s_callback is called when buf is emptied
    play_silence()
    
    state = PLAY
    
    # Loop until the BOOT/USER button is pressed
    while not yukon.is_boot_pressed():
        
        yukon.set_led('A', button_toggle)
        
        yukon.monitor_once()

finally:
    if audio_out is not None:
        audio_out.deinit()
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
