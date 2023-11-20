# Audio Amp Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Audio Amp Module for Yukon](https://pimoroni.com/yukon).

- [Getting Started](#getting-started)
- [Initialising the Module](#initialising-the-module)
- [Using the Module](#using-the-module)
  - [Controlling its Output](#controlling-its-output)
  - [Playing Audio](#playing-audio)
  - [Changing its Volume](#changing-its-volume)
  - [Advanced Control](#advanced-control)
  - [Onboard Sensors](#onboard-sensors)
- [Restrictions](#restrictions)
- [References](#references)
  - [Constants](#constants)
  - [Variables](#variables)
  - [Functions](#functions)


## Getting Started

To start using an Audio Amp Module, you first need to import the class from `pimoroni_yukon.modules`.

```python
from pimoroni_yukon.modules import AudioAmpModule
```

Then create an instance of `AudioAmpModule`, giving it the ID of the I2S audio instance to use (either 0 or 1).

```python
# Constants
I2S_ID = 0

module = AudioAmpModule(I2S_ID)
```


## Initialising the Module

As with all Yukon modules, `AudioAmpModule` must be initialised before it can be used. This is achieved by first registering the module with the `Yukon` class, with the slot it is attached to.

```python
from pimoroni_yukon import SLOT1 as SLOT

# Import and set up Yukon and AudioAmpModule instances

yukon.register_with_slot(module, SLOT)
```

Then `Yukon` can verify and initialise its modules.

```python
yukon.verify_and_initialise()
```

This checks each slot on the board to see if the modules expected by your program are physically attached to the board. Only if they match will the `AudioAmpModule` be initialised, giving it access to the GPIO of the slot it is attached to.

Power can now be provided to all modules, by calling.

```python
yukon.enable_main_output()
```

## Using the Module

### Controlling its Output

With the `AudioAmpModule` powered, its output can be enabled or disabled by calling `.enable()` or `.disable()`. The state can also be queried by calling `.is_enabled()`.


### Playing Audio

For playing audio out of the Audio Amp module, the Yukon library includes a `WavPlayer` class. This is created automatically by the `AudioAmpModule` and can be accessed by calling `module.player`.

The WavePlayer lets you play both WAV files and pure tones. To play a WAV file, call `.play_wav(wav_file)` with the name of the file to play. To play a tone, call `.play_tone(frequency, amplitude)` with the frequency and amplitude of the tone to play. It is also possible to `.pause()`, `.resume()`, and `.stop()` playback, as well as query whether audio `.is_playing()` or `.is_paused()`.

For more information on how to use the WavPlayer, refer to the [WavPlayer Library Reference](/docs/devices/wavplayer.md), as well as the [tone_song.py](/examples/modules/audio_amp/tone_song.py) and [wav_play.py](/examples/modules/audio_amp/wav_play.py) examples.

:information_source: WAV files should be 16-bit signed, with a sample rate of either 44100 or 48000. Both stereo and mono files are supported, although as the module only drives a single speaker, saving your audio as mono will reduce your file sizes.

### Changing its Volume

The output volume of the Audio Amp module can be changed by calling `.set_volume(volume)`, and providing it with a volume between `0.0` and `1.0`. Note that although this value is linear, the perceived volume change will be non-linear due to human hearing perception.


### Advanced Control

The Audio Amp module uses the TAS2780 class-D audio amplifier, which features I2C communication to let its parameters be adjusted. Outside of an initial configuration that is sent when the chip is enabled, the only parameters that are currently user adjustable are the volume and a command to wake the chip up from software shutdown. Full details of the rest of the chips parameters can be found in the [TAS2780 datasheet](https://www.ti.com/lit/ds/symlink/tas2780.pdf).

For anyone wishing to play about with the TAS2780's other parameters, the following I2C functions are exposed on the `AudioAmpModule`.

```python
write_i2c_reg(register: int, data: int) -> None
read_i2c_reg(register: int) -> int
detect_i2c() -> int
```

### Onboard Sensors

The Audio Amp module features an onboard thermistor, letting its temperature be monitored. This can be read by calling `.read_temperature()`.


## Restrictions

:warning: AudioAmpModule makes use of MicroPython's I2S system to drive the amplifier. Currently this system only supports two instances at any one time, meaning only two modules can be used simultaneously.


## References

### Constants

```python
NAME = "Audio Amp"
AMP_I2C_ADDRESS = 0x38
TEMPERATURE_THRESHOLD = 50.0
```


### Variables

```python
player: WavPlayer
```


### Functions

```python
# Address Checking
@staticmethod
is_module(adc1_level: int, adc2_level: int, slow1: bool, slow2: bool, slow3: bool) -> bool

# Initialisation
AudioAmpModule(i2s_id: int)
initialise(slot: SLOT, adc1_func: Callable, adc2_func: Callable) -> None
reset() -> None

# Power Control
enable() -> None
disable() -> None
is_enabled() -> bool

# Output Control
exit_soft_shutdown() -> None
set_volume(volume: float) -> None

# Sensing
read_temperature(samples: int=1) -> float

# Monitoring
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None

# Soft I2C
write_i2c_reg(register: int, data: int) -> None
read_i2c_reg(register: int) -> int
detect_i2c() -> int
```
