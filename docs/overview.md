# Pimoroni Yukon - Overview <!-- omit in toc -->

Here you will find an overview of the [Pimoroni Yukon](https://pimoroni.com/yukon), a high-power modular robotics and engineering platform, powered by the Raspberry Pi RP2040.

- [Backstory](#backstory)
- [What is Yukon?](#what-is-yukon)
- [Module Slots](#module-slots)


## Backstory

If you have ever looked at the pinout of RP2040 (or the Pico), you may have noticed how its GPIO functions like UART, SPI, and I2C repeat in groups of four. We noticed this too, which gave us the idea to create modular system that could take advantage of this.

We did not want to create another breakout system without reason though, so the idea shifted towards high-power uses that are not catered for by our [Breakout Garden](https://shop.pimoroni.com/collections/breakout-garden) range, such as driving motors and servos. After two years of development, and four hardware versions of the main board alone, Yukon is the result.


## What is Yukon?

Yukon is an RP2040-based controller for high-power projects. It consists of a main board and a range of specialised modules for driving various high-power devices. These modules can be attached to a main board in almost any combination to suit the needs of your project. This is achieved through the unique pin capabilities of the RP2040, and additional IO expanders and analog multiplexers. There are a total of 80 IO on the Yukon main board, with 64 available to the user via module slots or expansion headers.

To power your project, Yukon features an XT30 connector (common on batteries used for remote-controlled hobbies). This supports 5V to 17V with up to 15A of continuous current. An e-Fuse with switchable output is included allow for module power to be programatically controlled, as well as protect from accidental overvoltage and overcurrent events. There are also internal sensors on Yukon for monitoring voltage, current, and temperature from your program.


## Module Slots

Modules connect to Yukon via custom 2mm pitch 2 x 9 sockets and are screwed down to ensure a solid mechanical and electrical connection.

Each of Yukon's module slots provides high-power (V+), low-power (3.3V) and ground connections to any attached modules, along with 9 signal pins. These pins have the following roles:

* Four are direct GPIO connections to the [RP2040](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf), ordered as a contiguous block. This gives 24 GPIO available across Yukon's six slots. These pins can be used for any digital function that the RP2040 supports for those pins, like UART, I2C, SPI, and anything that PIO can perform. The Yukon library and documentation refers to these as **Fast IO**.

* Three are additional IO provided by two [TCA9555](https://www.ti.com/lit/ds/symlink/tca9555.pdf) I2C-based IO expanders. This gives 18 IO available across Yukon's six slots. These only support digital input and output, and are much slower to change state than fast IO due to the I2C communication involved. They are useful for enabling or otherwise configuring modules, reading back slow changing states, or even bitbanging I2C (as used by the Audio Amp module). The Yukon library refers to these as **Slow IO**. Note, when set as inputs these are pulled high by internal 100K Ohm resistors.

* Two are analog-only inputs, capable of reading from 0V to 3.3V, provided by two [74LV4051](https://assets.nexperia.com/documents/data-sheet/74LV4051.pdf) analog multiplexers connected to a single ADC pin of the RP2040. This gives 12 analogs available across Yukon's six slots. The address of the analog input being read is selected via pins on the IO expanders. The second analog-only input of each slot is primarily intended for reading a module's temperature, so has a 5.1K Ohm pull-up resistor on the Yukon board. This should be factored in if other analog signals are to be read, or overcome by adding op-amps as input buffers (as used on the Quad Servo Direct module).

Both the slow IO and analog pins of each slot are used as part of the Yukon libraries [Module Detection](/docs/module_detection.md) scheme.
