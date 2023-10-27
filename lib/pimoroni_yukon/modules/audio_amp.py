# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

import os
import tca
import math
import struct
from machine import Pin, I2S
from ucollections import OrderedDict
from .common import YukonModule, ADC_FLOAT, IO_LOW, IO_HIGH
from pimoroni_yukon.errors import OverTemperatureError

# PAGE 0 Regs
PAGE = 0x00             # Device Page Section 8.9.5
SW_RESET = 0x01         # Software Reset Section 8.9.6
MODE_CTRL = 0x02        # Device operational mode Section 8.9.7
CHNL_0 = 0x03           # Y Bridge and Channel settings Section 8.9.8
DC_BLK0 = 0x04          # SAR Filter and DC Path Blocker Section 8.9.9
DC_BLK1 = 0x05          # Record DC Blocker Section 8.9.10
MISC_CFG1 = 0x06        # Misc Configuration 1 Section 8.9.11
MISC_CFG2 = 0x07        # Misc Configuration 2 Section 8.9.12
TDM_CFG0 = 0x08         # TDM Configuration 0 Section 8.9.13
TDM_CFG1 = 0x09         # TDM Configuration 1 Section 8.9.14
TDM_CFG2 = 0x0A         # TDM Configuration 2 Section 8.9.15
LIM_MAX_ATTN = 0x0B     # Limiter Section 8.9.16
TDM_CFG3 = 0x0C         # TDM Configuration 3 Section 8.9.17
TDM_CFG4 = 0x0D         # TDM Configuration 4 Section 8.9.18
TDM_CFG5 = 0x0E         # TDM Configuration 5 Section 8.9.19
TDM_CFG6 = 0x0F         # TDM Configuration 6 Section 8.9.20
TDM_CFG7 = 0x10         # TDM Configuration 7 Section 8.9.21
TDM_CFG8 = 0x11         # TDM Configuration 8 Section 8.9.22
TDM_CFG9 = 0x12         # TDM Configuration 9 Section 8.9.23
TDM_CFG10 = 0x13        # TDM Configuration 10 Section 8.9.24
TDM_CFG11 = 0x14        # TDM Configuration 11 Section 8.9.25
ICC_CNFG2 = 0x15        # ICC Mode Section 8.9.26
TDM_CFG12 = 0x16        # TDM Configuration 12 Section 8.9.27
ICLA_CFG0 = 0x17        # Inter Chip Limiter Alignment 0 Section 8.9.28
ICLA_CFG1 = 0x18        # Inter Chip Gain Alignment 1 Section 8.9.29
DG_0 = 0x19             # Diagnostic Signal Section 8.9.30
DVC = 0x1A              # Digital Volume Control Section 8.9.31
LIM_CFG0 = 0x1B         # Limiter Configuration 0 Section 8.9.32
LIM_CFG1 = 0x1C         # Limiter Configuration 1 Section 8.9.33
BOP_CFG0 = 0x1D         # Brown Out Prevention 0 Section 8.9.34
BOP_CFG1 = 0x1E         # Brown Out Prevention 1 Section 8.9.35
BOP_CFG2 = 0x1F         # Brown Out Prevention 2 Section 8.9.36
BOP_CFG3 = 0x20         # Brown Out Prevention 3 Section 8.9.37
BOP_CFG4 = 0x21         # Brown Out Prevention 4 Section 8.9.38
BOP_CFG5 = 0x22         # BOP Configuration 5 Section 8.9.40
BOP_CFG6 = 0x23         # Brown Out Prevention 6 Section 8.9.41
BOP_CFG7 = 0x24         # Brown Out Prevention 7 Section 8.9.42
BOP_CFG8 = 0x25         # Brown Out Prevention 8 Section 8.9.43
BOP_CFG9 = 0x26         # Brown Out Prevention 9 Section 8.9.44
BOP_CFG10 = 0x27        # BOP Configuration 10 Section 8.9.45
BOP_CFG11 = 0x28        # Brown Out Prevention 11 Section 8.9.46
BOP_CFG12 = 0x29        # Brown Out Prevention 12 Section 8.9.47
BOP_CFG13 = 0x2A        # Brown Out Prevention 13 Section 8.9.48
BOP_CFG14 = 0x2B        # Brown Out Prevention 14 Section 8.9.49
BOP_CFG15 = 0x2C        # BOP Configuration 15 Section 8.9.50
BOP_CFG17 = 0x2D        # Brown Out Prevention 16 Section 8.9.51
BOP_CFG18 = 0x2E        # Brown Out Prevention 17 Section 8.9.52
BOP_CFG19 = 0x2F        # Brown Out Prevention 18 Section 8.9.53
BOP_CFG20 = 0x30        # Brown Out Prevention 19 Section 8.9.54
BOP_CFG21 = 0x31        # BOP Configuration 21 Section 8.9.55
BOP_CFG22 = 0x32        # Brown Out Prevention 22 Section 8.9.56
BOP_CFG23 = 0x33        # Lowest PVDD Measured Section 8.9.57
BOP_CFG24 = 0x34        # Lowest BOP Attack Rate Section 8.9.57
NG_CFG0 = 0x35          # Noise Gate 0 Section 8.9.60
NG_CFG1 = 0x36          # Noise Gate 1 Section 8.9.61
LVS_CFG0 = 0x37         # Low Voltage Signaling Section 8.9.62
DIN_PD = 0x38           # Digital Input Pin Pull Down Section 8.9.63
IO_DRV0 = 0x39          # Output Driver Strength Section 8.9.64
IO_DRV1 = 0x3A          # Output Driver Strength Section 8.9.65
INT_MASK0 = 0x3B        # Interrupt Mask 0 Section 8.9.66
INT_MASK1 = 0x3C        # Interrupt Mask 1 Section 8.9.67
INT_MASK4 = 0x3D        # Interrupt Mask 4 Section 8.9.68
INT_MASK2 = 0x40        # Interrupt Mask 2 Section 8.9.69
INT_MASK3 = 0x41        # Interrupt Mask 3 Section 8.9.70
INT_LIVE0 = 0x42        # Live Interrupt Read-back 0 Section 8.9.71
INT_LIVE1 = 0x43        # Live Interrupt Read-back 1 Section 8.9.72
INT_LIVE1_0 = 0x44      # Live Interrupt Read-back 1_0 Section 8.9.73
INT_LIVE2 = 0x47        # Live Interrupt Read-back 2 Section 8.9.74
INT_LIVE3 = 0x48        # Live Interrupt Read-back 3 Section 8.9.75
INT_LTCH0 = 0x49        # Latched Interrupt Read-back 0 Section 8.9.76
INT_LTCH1 = 0x4A        # Latched Interrupt Read-back 1 Section 8.9.77
INT_LTCH1_0 = 0x4B      # Latched Interrupt Read-back 1_0 Section 8.9.78
INT_LTCH2 = 0x4F        # Latched Interrupt Read-back 2 Section 8.9.79
INT_LTCH3 = 0x50        # Latched Interrupt Read-back 3 Section 8.9.80
INT_LTCH4 = 0x51        # Latched Interrupt Read-back 4 Section 8.9.81
VBAT_MSB = 0x52         # SAR VBAT1S 0 Section 8.9.82
VBAT_LSB = 0x53         # SAR VBAT1S 1 Section 8.9.83
PVDD_MSB = 0x54         # SAR PVDD 0 Section 8.9.84
PVDD_LSB = 0x55         # SAR PVDD 1 Section 8.9.85
TEMP = 0x56             # SAR ADC Conversion 2 Section 8.9.86
INT_CLK_CFG = 0x5C      # Clock Setting and IRQZ Section 8.9.87
MISC_CFG3 = 0x5D        # Misc Configuration 3 Section 8.9.88
CLOCK_CFG = 0x60        # Clock Configuration Section 8.9.89
IDLE_IND = 0x63         # Idle channel current optimization Section 8.9.90
MISC_CFG4 = 0x65        # Misc Configuration 4 Section 8.9.91
TG_CFG0 = 0x67          # Tone Generator Section 8.9.92
CLK_CFG = 0x68          # Detect Clock Ration and Sample Rate Section 8.9.93
LV_EN_CFG = 0x6A        # Class-D and LVS Delays Section 8.9.94
NG_CFG2 = 0x6B          # Noise Gate 2 Section 8.9.95
NG_CFG3 = 0x6C          # Noise Gate 3 Section 8.9.96
NG_CFG4 = 0x6D          # Noise Gate 4 Section 8.9.97
NG_CFG5 = 0x6E          # Noise Gate 5 Section 8.9.98
NG_CFG6 = 0x6F          # Noise Gate 6 Section 8.9.99
NG_CFG7 = 0x70          # Noise Gate 7 Section 8.9.100
PVDD_UVLO = 0x71        # UVLO Threshold Section 8.9.101
DMD = 0x73              # DAC Modulator Dither Section 8.9.102
I2C_CKSUM = 0x7E        # I2C Checksum Section 8.9.104
BOOK = 0x7F             # Device Book Section 8.9.105

# PAGE 1 Regs
LSR = 0x19              # Modulation Section 8.9.106
INT_LDO = 0x36          # Internal LDO Setting Section 8.9.107
SDOUT_HIZ_1 = 0x3D      # Slots Control Section 8.9.108
SDOUT_HIZ_2 = 0x3E      # Slots Control Section 8.9.109
SDOUT_HIZ_3 = 0x3F      # Slots Control Section 8.9.110
SDOUT_HIZ_4 = 0x40      # Slots Control Section 8.9.111
SDOUT_HIZ_5 = 0x41      # Slots Control Section 8.9.112
SDOUT_HIZ_6 = 0x42      # Slots Control Section 8.9.113
SDOUT_HIZ_7 = 0x43      # Slots Control Section 8.9.114
SDOUT_HIZ_8 = 0x44      # Slots Control Section 8.9.115
SDOUT_HIZ_9 = 0x45      # Slots Control Section 8.9.116
TG_EN = 0x47            # Thermal Detection Enable Section 8.9.117


# Modified from: https://github.com/miketeachman/micropython-i2s-examples/blob/master/examples/wavplayer.py
class WavPlayer:
    # Internal states
    PLAY = 0
    PAUSE = 1
    FLUSH = 2
    STOP = 3
    NONE = 4

    MODE_WAV = 0
    MODE_TONE = 1

    # Default buffer length
    SILENCE_BUFFER_LENGTH = 1000
    WAV_BUFFER_LENGTH = 10000
    INTERNAL_BUFFER_LENGTH = 20000

    TONE_SAMPLE_RATE = 44_100
    TONE_BITS_PER_SAMPLE = 16
    TONE_FULL_WAVES = 2

    def __init__(self, id, sck_pin, ws_pin, sd_pin, ibuf_len=INTERNAL_BUFFER_LENGTH, root="/"):
        self.__id = id
        self.__sck_pin = sck_pin
        self.__ws_pin = ws_pin
        self.__sd_pin = sd_pin
        self.__ibuf_len = ibuf_len

        # Set the directory to search for files in
        self.set_root(root)

        self.__state = WavPlayer.NONE
        self.__mode = WavPlayer.MODE_WAV
        self.__wav_file = None
        self.__loop_wav = False
        self.__first_sample_offset = None
        self.__flush_count = 0
        self.__audio_out = None

        # Allocate a small array of blank audio samples used for silence
        self.__silence_samples = bytearray(self.SILENCE_BUFFER_LENGTH)

        # Allocate a larger array for WAV audio samples, using a memoryview for more efficient access
        self.__wav_samples_mv = memoryview(bytearray(self.WAV_BUFFER_LENGTH))

        # Reserve a variable for audio samples used for tones
        self.__tone_samples = None
        self.__queued_samples = None

    def set_root(self, root):
        self.__root = root.rstrip("/") + "/"

    def play_wav(self, wav_file, loop=False):
        if os.listdir(self.__root).count(wav_file) == 0:
            raise ValueError("%s: not found" % wav_file)

        self.__stop_i2s()                                       # Stop any active playback and terminate the I2S instance

        self.__wav_file = open(self.__root + wav_file, "rb")    # Open the chosen WAV file in read-only, binary mode
        self.__loop_wav = loop                                  # Record if the user wants the file to loop

        # Parse the WAV file, returning the necessary parameters to initialise I2S communication
        format, sample_rate, bits_per_sample, self.__first_sample_offset = WavPlayer.__parse_wav(self.__wav_file)

        self.__wav_file.seek(self.__first_sample_offset)        # Advance to first byte of sample data

        self.__start_i2s(bits=bits_per_sample,
                         format=format,
                         rate=sample_rate,
                         state=WavPlayer.PLAY,
                         mode=WavPlayer.MODE_WAV)

    def play_tone(self, frequency, amplitude):
        if frequency < 20.0 or frequency > 20_000:
            raise ValueError("frequency out of range. Expected between 20Hz and 20KHz")

        if amplitude < 0.0 or amplitude > 1.0:
            raise ValueError("amplitude out of range. Expected 0.0 to 1.0")

        # Create a buffer containing the pure tone samples
        samples_per_cycle = self.TONE_SAMPLE_RATE // frequency
        sample_size_in_bytes = self.TONE_BITS_PER_SAMPLE // 8
        samples = bytearray(self.TONE_FULL_WAVES * samples_per_cycle * sample_size_in_bytes)
        range = pow(2, self.TONE_BITS_PER_SAMPLE) // 2

        format = "<h" if self.TONE_BITS_PER_SAMPLE == 16 else "<l"

        # Populate the buffer with multiple cycles to avoid it completing too quickly and causing drop outs
        for i in range(samples_per_cycle * self.TONE_FULL_WAVES):
            sample = int((range - 1) * (math.sin(2 * math.pi * i / samples_per_cycle)) * amplitude)
            struct.pack_into(format, samples, i * sample_size_in_bytes, sample)

        # Are we not already playing tones?
        if not (self.__mode == WavPlayer.MODE_TONE and (self.__state == WavPlayer.PLAY or self.__state == WavPlayer.PAUSE)):
            self.__stop_i2s()                                       # Stop any active playback and terminate the I2S instance
            self.__tone_samples = samples
            self.__start_i2s(bits=self.TONE_BITS_PER_SAMPLE,
                             format=I2S.MONO,
                             rate=self.TONE_SAMPLE_RATE,
                             state=WavPlayer.PLAY,
                             mode=WavPlayer.MODE_TONE)
        else:
            self.__queued_samples = samples
            self.__state = WavPlayer.PLAY

    def pause(self):
        if self.__state == WavPlayer.PLAY:
            self.__state = WavPlayer.PAUSE          # Enter the pause state on the next callback

    def resume(self):
        if self.__state == WavPlayer.PAUSE:
            self.__state = WavPlayer.PLAY           # Enter the play state on the next callback

    def stop(self):
        if self.__state == WavPlayer.PLAY or self.__state == WavPlayer.PAUSE:
            if self.__mode == WavPlayer.MODE_WAV:
                # Enter the flush state on the next callback and close the file
                # It is done in this order to prevent the callback entering the play
                # state after we close the file but before we change the state)
                self.__state = WavPlayer.FLUSH
                self.__wav_file.close()
            else:
                self.__state = WavPlayer.STOP

    def is_playing(self):
        return self.__state != WavPlayer.NONE and self.__state != WavPlayer.STOP

    def is_paused(self):
        return self.__state == WavPlayer.PAUSE

    def __start_i2s(self, bits=16, format=I2S.MONO, rate=44_100, state=STOP, mode=MODE_WAV):
        import gc
        gc.collect()
        self.__audio_out = I2S(
            self.__id,
            sck=self.__sck_pin,
            ws=self.__ws_pin,
            sd=self.__sd_pin,
            mode=I2S.TX,
            bits=bits,
            format=format,
            rate=rate,
            ibuf=self.__ibuf_len,
        )

        self.__state = state
        self.__mode = mode
        self.__flush_count = self.__ibuf_len // self.SILENCE_BUFFER_LENGTH + 1
        self.__audio_out.irq(self.__i2s_callback)
        self.__audio_out.write(self.__silence_samples)

    def __stop_i2s(self):
        self.stop()                     # Stop any active playback
        while self.is_playing():        # and wait for it to complete
            pass

        if self.__audio_out is not None:
            self.__audio_out.deinit()   # Deinit any active I2S comms

        self.__state == WavPlayer.NONE  # Return to the none state

    def __i2s_callback(self, arg):
        ### PLAY ###
        if self.__state == WavPlayer.PLAY:
            if self.__mode == WavPlayer.MODE_WAV:
                num_read = self.__wav_file.readinto(self.__wav_samples_mv)      # Read the next section of the WAV file

                # Have we reached the end of the file?
                if num_read == 0:
                    # Do we want to loop the WAV playback?
                    if self.__loop_wav:
                        _ = self.__wav_file.seek(self.__first_sample_offset)    # Play again, so advance to first byte of sample data
                    else:
                        self.__wav_file.close()                                 # Stop playing, so close the file
                        self.__state = WavPlayer.FLUSH                          # and enter the flush state on the next callback

                    self.__audio_out.write(self.__silence_samples)              # In both cases play silence to end this callback
                else:
                    self.__audio_out.write(self.__wav_samples_mv[: num_read])   # We are within the file, so write out the next audio samples
            else:
                if self.__queued_samples is not None:
                    self.__tone_samples = self.__queued_samples
                    self.__queued_samples = None
                self.__audio_out.write(self.__tone_samples)

        ### PAUSE or STOP ###
        elif self.__state == WavPlayer.PAUSE or self.__state == WavPlayer.STOP:
            self.__audio_out.write(self.__silence_samples)                  # Play silence

        ### FLUSH ###
        elif self.__state == WavPlayer.FLUSH:
            # Flush is used to allow the residual audio samples in the internal buffer to be written
            # to the I2S peripheral. This step avoids part of the sound file from being cut off
            if self.__flush_count > 0:
                self.__flush_count -= 1
            else:
                self.__state = WavPlayer.STOP                               # Enter the stop state on the next callback
            self.__audio_out.write(self.__silence_samples)                  # Play silence

        ### NONE ###
        elif self.__state == WavPlayer.NONE:
            pass

    @staticmethod
    def __parse_wav(wav_file):
        chunk_ID = wav_file.read(4)
        if chunk_ID != b"RIFF":
            raise ValueError("WAV chunk ID invalid")
        _ = wav_file.read(4)                            # chunk_size
        format = wav_file.read(4)
        if format != b"WAVE":
            raise ValueError("WAV format invalid")
        sub_chunk1_ID = wav_file.read(4)
        if sub_chunk1_ID != b"fmt ":
            raise ValueError("WAV sub chunk 1 ID invalid")
        _ = wav_file.read(4)                            # sub_chunk1_size
        _ = struct.unpack("<H", wav_file.read(2))[0]    # audio_format
        num_channels = struct.unpack("<H", wav_file.read(2))[0]

        if num_channels == 1:
            format = I2S.MONO
        else:
            format = I2S.STEREO

        sample_rate = struct.unpack("<I", wav_file.read(4))[0]
        if sample_rate != 44_100 and sample_rate != 48_000:
            raise ValueError(f"WAV sample rate of {sample_rate} invalid. Only 44.1KHz or 48KHz audio are supported")

        _ = struct.unpack("<I", wav_file.read(4))[0]    # byte_rate
        _ = struct.unpack("<H", wav_file.read(2))[0]    # block_align
        bits_per_sample = struct.unpack("<H", wav_file.read(2))[0]

        # usually the sub chunk2 ID ("data") comes next, but
        # some online MP3->WAV converters add
        # binary data before "data".  So, read a fairly large
        # block of bytes and search for "data".

        binary_block = wav_file.read(200)
        offset = binary_block.find(b"data")
        if offset == -1:
            raise ValueError("WAV sub chunk 2 ID not found")

        return (format, sample_rate, bits_per_sample, 44 + offset)


class AudioAmpModule(YukonModule):
    NAME = "Audio Amp"
    AMP_I2C_ADDRESS = 0x38
    TEMPERATURE_THRESHOLD = 50.0

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | FLOAT | ALL   | 0     | 1     | 1     | Audio Amp            |                             |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level == ADC_FLOAT and slow1 is IO_LOW and slow2 is IO_HIGH and slow3 is IO_HIGH

    def __init__(self, i2s_id):
        super().__init__()
        self.__i2s_id = i2s_id
        self.player = None

    def initialise(self, slot, adc1_func, adc2_func):
        # Create the enable pin object
        self.__amp_en = slot.SLOW1

        # Create the "I2C" pin objects
        self.__slow_sda = slot.SLOW2
        self.__slow_scl = slot.SLOW3

        self.__chip = tca.get_chip(slot.SLOW2)
        self.__sda_bit = 1 << tca.get_number(slot.SLOW2)
        self.__scl_bit = 1 << tca.get_number(slot.SLOW3)

        self.__i2s_data = slot.FAST1
        self.__i2s_clk = slot.FAST2
        self.__i2s_fs = slot.FAST3

        # Create the Player object, with the needed I2S pins
        self.player = WavPlayer(id=self.__i2s_id,
                                sck_pin=self.__i2s_clk,
                                ws_pin=self.__i2s_fs,
                                sd_pin=self.__i2s_data)

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        self.__slow_sda.init(Pin.OUT, value=True)
        self.__slow_scl.init(Pin.OUT, value=True)
        self.__amp_en.init(Pin.OUT, value=False)

        # Stop and clean up the Player object if it exists
        if self.player is not None:
            self.player.__stop_i2s()

    def enable(self):
        if not self.is_enabled():
            self.__amp_en.value(True)

            # Pre-Reset Configuration
            self.write_i2c_reg(PAGE, 0x01)  # Page 1
            self.write_i2c_reg(0x37, 0x3a)  # Bypass

            self.write_i2c_reg(PAGE, 0xFD)  # Page FD
            self.write_i2c_reg(0x0D, 0x0D)  # Access page
            self.write_i2c_reg(0x06, 0xC1)  # Set Dmin

            self.write_i2c_reg(PAGE, 0x01)  # Page 1
            self.write_i2c_reg(0x19, 0xC0)  # Force modulation
            self.write_i2c_reg(PAGE, 0xFD)  # Page FD
            self.write_i2c_reg(0x0D, 0x0D)  # Access page
            self.write_i2c_reg(0x06, 0xD5)  # Set Dmin

            # Software Reset
            self.write_i2c_reg(PAGE, 0x00)  # Page 0
            self.write_i2c_reg(0x7F, 0x00)  # Book 0
            self.write_i2c_reg(0x01, 0x01)  # Software Reset

            # Post-Reset Configuration
            self.write_i2c_reg(PAGE, 0x01)  # Page 1
            self.write_i2c_reg(0x37, 0x3a)  # Bypass

            self.write_i2c_reg(PAGE, 0xFD)  # Page FD
            self.write_i2c_reg(0x0D, 0x0D)  # Access page
            self.write_i2c_reg(0x06, 0xC1)  # Set Dmin
            self.write_i2c_reg(0x06, 0xD5)  # Set Dmin

            # Initial Device Configuration - PWR_MODE0
            self.write_i2c_reg(PAGE, 0x00)  # Page 0
            self.write_i2c_reg(0x0E, 0x44)  # TDM tx vsns transmit enable with slot 4
            self.write_i2c_reg(0x0F, 0x40)  # TDM tx isns transmit enable with slot 0

            self.write_i2c_reg(PAGE, 0x01)  # Page 1
            self.write_i2c_reg(0x21, 0x00)  # Disable Comparator Hysterisis
            self.write_i2c_reg(0x17, 0xC8)  # SARBurstMask=0
            self.write_i2c_reg(0x19, 0x00)  # LSR Mode
            self.write_i2c_reg(0x35, 0x74)  # Noise minimized

            self.write_i2c_reg(PAGE, 0xFD)  # Page FD
            self.write_i2c_reg(0x0D, 0x0D)  # Access page
            self.write_i2c_reg(0x3E, 0x4A)  # Optimal Dmin
            self.write_i2c_reg(0x0D, 0x00)  # Remove access

            self.write_i2c_reg(PAGE, 0x00)  # Page 0
            self.write_i2c_reg(CHNL_0, 0xA8)  # PWR_MODE0 selected
            self.write_i2c_reg(PVDD_UVLO, 0x00)  # PVDD UVLO set to 2.76V
            # My addition
            self.write_i2c_reg(DC_BLK0, 0xA1)  # VBAT1S_MODE set to internally generated
            self.write_i2c_reg(DVC, 0x68)  # Go to a low default
            self.write_i2c_reg(INT_CLK_CFG, 0x99 + 0b0100000)  # CLK_PWR_UD_EN abled, with long time. This causes output to stay active without mute.

            self.write_i2c_reg(INT_MASK0, 0xFF)
            self.write_i2c_reg(INT_MASK1, 0xFF)
            self.write_i2c_reg(INT_MASK2, 0xFF)
            self.write_i2c_reg(INT_MASK3, 0xFF)
            self.write_i2c_reg(INT_MASK4, 0xFF)

            self.write_i2c_reg(MODE_CTRL, 0x80)  # Play audio, power up with playback, IV enabled

            # Initiate I2S communication on the Player
            self.player.__start_i2s()

    def disable(self):
        if self.is_enabled():
            self.player.__stop_i2s()

        self.__amp_en.value(False)

    def is_enabled(self):
        return self.__amp_en.value() == 1

    def exit_soft_shutdown(self):
        self.write_i2c_reg(MODE_CTRL, 0x80)  # Calling this after a play seems to wake the amp up, but adds around 16ms

    def set_volume(self, volume):
        if volume < 0 or volume > 1.0:
            raise ValueError("Volume out of range. Expected 0.0 to 1.0")

        self.write_i2c_reg(DVC, int((1.0 - volume) * 0xC8))

    def read_temperature(self, samples=1):
        return self.__read_adc2_as_temp(samples)

    def monitor(self):
        temperature = self.read_temperature()
        if temperature > self.TEMPERATURE_THRESHOLD:
            raise OverTemperatureError(self.__message_header() + f"Temperature of {temperature}°C exceeded the limit of {self.TEMPERATURE_THRESHOLD}°C! Turning off output")

        # Run some user action based on the latest readings
        if self.__monitor_action_callback is not None:
            self.__monitor_action_callback(temperature)

        self.__max_temperature = max(temperature, self.__max_temperature)
        self.__min_temperature = min(temperature, self.__min_temperature)
        self.__avg_temperature += temperature
        self.__count_avg += 1

    def get_readings(self):
        return OrderedDict({
            "T_max": self.__max_temperature,
            "T_min": self.__min_temperature,
            "T_avg": self.__avg_temperature
        })

    def process_readings(self):
        if self.__count_avg > 0:
            self.__avg_temperature /= self.__count_avg
            self.__count_avg = 0    # Clear the count to prevent process readings acting more than once

    def clear_readings(self):
        self.__max_temperature = float('-inf')
        self.__min_temperature = float('inf')
        self.__avg_temperature = 0
        self.__count_avg = 0

    def __start_i2c(self):
        tca.change_output_mask(self.__chip, self.__sda_bit, 0)  # Data to low
        tca.change_output_mask(self.__chip, self.__scl_bit, 0)  # Clock to low

    def __end_i2c(self):
        tca.change_output_mask(self.__chip, self.__scl_bit, self.__scl_bit)  # Clock to high
        tca.change_output_mask(self.__chip, self.__sda_bit, self.__sda_bit)  # Data to high

    def __write_i2c_byte(self, number):
        bit = 128
        mask = self.__scl_bit | self.__sda_bit  # Set the mask for both SDA and SCL pins
        while bit > 0:
            # New data and clock to low
            tca.change_output_mask(self.__chip, mask, self.__sda_bit if number & bit else 0)

            # Clock to high
            tca.change_output_mask(self.__chip, self.__scl_bit, self.__scl_bit)
            bit >>= 1

        # Clock to low
        tca.change_output_mask(self.__chip, self.__scl_bit, 0)

        """
        # Do real ACK, with checking ACK value
        self.__slow_sda.init(Pin.IN)
        tca.change_output_mask(self.__chip, self.__scl_bit, self.__scl_bit)  # Clock to high
        ack = self.__slow_sda.value()
        tca.change_output_mask(self.__chip, self.__scl_bit, 0)        # Clock to low
        self.__slow_sda.init(Pin.OUT)
        return ack
        """

        # Do real ACK, without checking value
        self.__slow_sda.init(Pin.IN)
        tca.change_output_mask(self.__chip, self.__scl_bit, self.__scl_bit)  # Clock to high
        tca.change_output_mask(self.__chip, self.__scl_bit, 0)        # Clock to low
        self.__slow_sda.init(Pin.OUT)

        """
        # Do fake ACK
        tca.change_output_mask(self.__chip, self.__scl_bit, self.__scl_bit)  # Clock to high
        tca.change_output_mask(self.__chip, self.__scl_bit, 0)        # Clock to low
        """

    def __read_i2c_byte(self):
        self.__slow_sda.init(Pin.IN)
        number = 0
        bit = 128
        while bit > 0:
            # print(number & bit)
            tca.change_output_mask(self.__chip, self.__scl_bit, self.__scl_bit)  # Clock to high
            if self.__slow_sda.value:
                number |= bit
            tca.change_output_mask(self.__chip, self.__scl_bit, 0)  # Clock to low
            bit >>= 1

        # Do fake ACK
        tca.change_output_mask(self.__chip, self.__scl_bit, self.__scl_bit)  # Clock to high
        tca.change_output_mask(self.__chip, self.__scl_bit, 0)  # Clock to low
        self.__slow_sda.init(Pin.OUT)

        return number

    def write_i2c_reg(self, register, data):
        self.__start_i2c()
        self.__write_i2c_byte(self.AMP_I2C_ADDRESS << 1)
        self.__write_i2c_byte(register)
        self.__write_i2c_byte(data)
        self.__end_i2c()

    def read_i2c_reg(self, register):
        self.__start_i2c()
        self.__write_i2c_byte(self.AMP_I2C_ADDRESS << 1)
        self.__write_i2c_byte(register)
        self.__end_i2c()

        self.__start_i2c()
        self.__write_i2c_byte(self.AMP_I2C_ADDRESS << 1 | 0x01)
        number = self.__read_i2c_byte()
        self.__end_i2c()

        return number

    def detect_i2c(self):
        self.__start_i2c()
        ack = self.__write_i2c_byte(self.AMP_I2C_ADDRESS << 1 | 0x01)
        self.__end_i2c()
        return ack
