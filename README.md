# Pimoroni Yukon <!-- omit in toc -->
## Firmware, Examples & Documentation <!-- omit in toc -->

Yukon is a high power modular robotics / engineering platform, powered by the Raspberry Pi RP2040. Learn more - https://shop.pimoroni.com/products/yukon

- [Install](#install)
  - [Flashing the Firmware](#flashing-the-firmware)
- [Examples and Usage](#examples-and-usage)


## Install

Grab the latest release from [https://github.com/pimoroni/yukon/releases/latest](https://github.com/pimoroni/yukon/releases/latest)

There are two .uf2 files to pick from.

:warning: Those marked `with-filesystem` contain a full filesystem image that will overwrite both the firmware *and* filesystem of your Yukon:

* pimoroni-yukon-vX.X.X-micropython-with-filesystem.uf2 

The regular builds just include the firmware, and leave your files alone:

* pimoroni-yukon-vX.X.X-micropython.uf2


### Flashing the Firmware

1. Connect your Yukon to your computer using a USB A to C cable.

2. Turn off your board by pressing the PWM button. The green light should turn off.

3. Put your device into bootloader mode by holding the BOOT/USER button whilst pressing the PWR button to turn the board on. The green light should turn on, and the lights next to the A and B buttons should have a dim glow.

4. Drag and drop one of the `yukon` .uf2 files to the "RPI-RP2" drive that appears.

5. Your device should reset and, if you used the `with-filesystem` variant, should see the A and B lights flash in a repeated pattern.


## Examples and Usage

There are many examples to get you started with Yukon, located in the examples folder of this repository. Details about what each one does can be found in the [examples readme](/examples/README.md).

To take Yukon further, the full API is described in the [documentation readme](/docs/README.md)
