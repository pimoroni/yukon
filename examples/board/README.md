# Yukon Micropython Board Examples <!-- omit in toc -->

<img src="https://shop.pimoroni.com/cdn/shop/files/yukon-host-front_1500x1500_crop_center.jpg" width="500">

- [Function Examples](#function-examples)
  - [Blink LED](#blink-led)
  - [Read Buttons](#read-buttons)
  - [Read Slot](#read-slot)
  - [Read Internals](#read-internals)
  - [Read Expansion](#read-expansion)
  - [Set Slot](#set-slot)
  - [Set Expansion](#set-expansion)
  - [Monitor Internals](#monitor-internals)
- [I2C Examples](#i2c-examples)
  - [BME280 via Expansion](#bme280-via-expansion)
  - [BME280 via QwST](#bme280-via-qwst)


## Function Examples

### Blink LED
[blink_led.py](blink_led.py)

Blink one of Yukon's onboard LEDs.


### Read Buttons
[read_buttons.py](read_buttons.py)

Read Yukon's onboard Buttons.


### Read Slot
[read_slot.py](read_slot.py)

Read the IO pins of a single Yukon slot.


### Read Internals
[read_internals.py](read_internals.py)

Read the internal sensors of Yukon.


### Read Expansion
[read_expansion.py](read_expansion.py)

Read the IO pins on Yukon's expansion header.


### Set Slot
[set_slot.py](set_slot.py)

Initialise the IO pins on a Yukon slot as outputs and set them.


### Set Expansion
[set_expansion.py](set_expansion.py)

Initialise the IO pins on Yukon's expansion header as outputs and set them.


### Monitor Internals
[monitor_internals.py](monitor_internals.py)

Use Yukon's monitoring function to read the internal sensors.


## I2C Examples

### BME280 via Expansion
[i2c/bme280_via_expansion.py](i2c/bme280_via_expansion.py)

Read a BME280 sensor attached to the Expansion header.


### BME280 via QwST
[i2c/bme280_via_qwst.py](i2c/bme280_via_qwst.py)

Read a BME280 sensor attached to the QwST connectors or Breakout Garden header.
