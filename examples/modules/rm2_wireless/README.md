# RM2 Wireless Module - Micropython Examples <!-- omit in toc -->

<img src="https://shop.pimoroni.com/cdn/shop/files/wireless-1_1500x1500_crop_center.jpg" width="500">

These are micropython examples for the [RM2 Wireless Module for Yukon](https://shop.pimoroni.com/products/rm2-wireless-module-for-yukon).

- [Examples](#examples)
  - [Detect Module](#detect-module)
  - [WiFi Scan](#wifi-scan)
  - [Cheerlights](#cheerlights)


## Examples

### Detect Module
[detect_module.py](detect_module.py)

A boilerplate example showing how to detect if the RM2 Wireless Module is attached to Yukon prior to performing any wireless operations.


### WiFi Scan
[wifi_scan.py](wifi_scan.py)

Periodically scan for available WiFi networks using a RM2 Wireless Module connected to Slot 5, and print out their details.


### Cheerlights

[cheerlights.py](cheerlights.py)

Obtain the current CheerLights colour from the internet and show it on an LED Strip connected to Yukon. For more information about CheerLights, visit: https://cheerlights.com/

This example requires a secrets.py file to be on your board's file system with the credentials of your WiFi network.