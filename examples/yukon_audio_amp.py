from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import AudioAmpModule
import math
from machine import I2S
import struct

# Select the slot that the module is installed in
SLOT = 3

# Create a Yukon object to begin using the board
yukon = Yukon(logging_level=0)

I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 20000
TONE_FREQUENCY_IN_HZ = 1000
SAMPLE_SIZE_IN_BITS = 16
FORMAT = I2S.MONO  # only MONO supported in this example
SAMPLE_RATE_IN_HZ = 44_100

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

try:
    # Create an AudioAmpModule and register it with a slot on Yukon
    amp = AudioAmpModule()
    yukon.register_with_slot(amp, SLOT)

    # Initialise Yukon's registered modules
    yukon.initialise_modules(allow_unregistered=True)

    # Turn on the module power
    yukon.enable_main_output()

    # Enable the switched outputs
    amp.enable()
    amp.set_volume(0.3)

    #wave_file = open("ahoy.wav", "rb")
    #wave_file_a = open("Mech-Startup.wav", "rb")
    #wave_file_b = open("Mech-Shutdown.wav", "rb")
    #wave_file = open("TV Theme - Police Squad2.wav", "rb")
    #wave_a = WaveFile(wave_file_a)
    #wave_b = WaveFile(wave_file_b)
    #i2s = audiobusio.I2SOut(amp.I2S_CLK, amp.I2S_FS, amp.I2S_DATA)
    #i2s.stop()

    samples = make_tone(SAMPLE_RATE_IN_HZ, SAMPLE_SIZE_IN_BITS, TONE_FREQUENCY_IN_HZ)
    for i in range(len(samples) // 2):
        print(int(samples[(i * 2)]) + (int(samples[(i * 2) + 1]) * 256))

    audio_out = I2S(
        I2S_ID,
        sck=amp.I2S_CLK,
        ws=amp.I2S_FS,
        sd=amp.I2S_DATA,
        mode=I2S.TX,
        bits=SAMPLE_SIZE_IN_BITS,
        format=FORMAT,
        rate=SAMPLE_RATE_IN_HZ,
        ibuf=BUFFER_LENGTH_IN_BYTES,
    )
    
    audio_out.irq(i2s_callback)         # i2s_callback is called when buf is emptied
    num_written = audio_out.write(samples)  # returns immediately

    sw_a_state = False
    sw_b_state = False
    last_sw_a_state = False
    last_sw_b_state = False
    while not yukon.is_boot_pressed():
        sw_a_state = yukon.is_pressed('A')
        sw_b_state = yukon.is_pressed('B')

        if sw_a_state is True and sw_a_state != last_sw_a_state:
            #if not i2s.playing:
            #    i2s.play(wave_a, loop=False)
            #    amp.exit_soft_shutdown()  # This is currently needed after a second play, resulting in an 8.5m delay from sound starting to it being heard
            #    print("Playing")
            #else:
            #    i2s.stop()
            #    print("Stopping")
            pass
        
        if sw_b_state is True and sw_b_state != last_sw_b_state:
            #if not i2s.playing:
            #    i2s.play(wave_b, loop=False)
            #    amp.exit_soft_shutdown()  # This is currently needed after a second play, resulting in an 8.5m delay from sound starting to it being heard
            #    print("Playing")
            #else:
            #    i2s.stop()
            #    print("Stopping")
            pass

        last_sw_a_state = sw_a_state
        last_sw_b_state = sw_b_state

        #yukon.set_led('A', i2s.playing)

        yukon.monitored_sleep(0)  # Monitor for the shortest time possible

finally:
    audio_out.deinit()
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
