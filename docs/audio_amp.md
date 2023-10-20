# Audio Amp Module - Library Reference <!-- omit in toc -->

This is the library reference for the [Audio Amp Module for Yukon](https://pimoroni.com/yukon).

- [Constants](#constants)
- [Variables \& Properties](#variables--properties)
- [Methods](#methods)


## Constants
```python
NAME = "Audio Amp"
AMP_I2C_ADDRESS = 0x38
TEMPERATURE_THRESHOLD = 50.0
```

## Variables & Properties
```python
I2S_DATA : SLOT
I2S_CLK : SLOT
I2S_FS : SLOT
```

## Methods
```python
## Address Checking ##
@staticmethod
is_module(adc1_level : int, adc2_level : int, slow1 : bool, slow2 : bool, slow3 :bool) -> bool

## Initialisation ##
AudioAmpModule()
initialise(slot : SLOT, adc1_func : Any, adc2_func : Any) -> None
reset() -> None

## Power Control ##
enable() -> None
disable() -> None
is_enabled() -> bool

## Output Control ##
exit_soft_shutdown() -> None
set_volume(volume : float) -> None

## Sensing ##
read_temperature() -> float

## Monitoring ##
monitor() -> None
get_readings() -> OrderedDict
process_readings() -> None
clear_readings() -> None

## Soft I2C ##
write_i2c_reg(register : int, data : int) -> None
read_i2c_reg(register : int) -> int
detect_i2c() -> int
```
