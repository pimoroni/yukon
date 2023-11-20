# WavPlayer Class - Library Reference <!-- omit in toc -->

This is the library reference for the `WavPlayer` class used to play audio out of Pimoroni Yukon's [Audio Amp Module](https://pimoroni.com/yukon).

- [References](#references)
  - [Constants](#constants)
  - [Functions](#functions)


## References

### Constants

```python
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
```


### Functions

```python
# Initialisation
WavPlayer(id: int,
          sck_pin: Pin
          ws_pin: Pin
          sd_pin: Pin
          ibuf_len: int=INTERNAL_BUFFER_LENGTH,
          root: string="/")

# Directories
set_root(root: string) -> None

# Player Control
play_wav(wav_file: string, loop: bool=False) -> None
play_tone(frequency: float, amplitude: float) -> None
pause() -> None
resume() -> None
stop() -> None
is_playing() -> bool
is_paused() -> bool
```
