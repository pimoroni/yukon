# Yukon Micropython Wireless Examples <!-- omit in toc -->

This folder contains examples that use the RM2 Wireless Module, and need the wireless build of the
Yukon firmware.

- [Game Pad](#game-pad)
- [Keyboard](#keyboard)


## Game Pad

[gamepad/main.py](gamepad/main.py)

Drives Yukon from a Bluetooth game pad paired straight to the board, with no phone or computer in
between. The first time, put the pad into pairing mode and Yukon finds it, pairs, and saves the link
key to `/bt_link_keys.txt` on the board. From then on switching the pad on is enough, and if Yukon
restarts while the pad is on it reconnects by itself. Delete that file to forget a pad.

Copy the three modules in [gamepad/lib](gamepad/lib) to the board's `lib` directory:

- `gamepad.py` turns the pad's raw reports into named buttons and axes, with callbacks.
- `gamepad_mappings.py` holds the report layout of each known pad and mode, one function each: the
  8BitDo Lite in its X-input and Switch modes, the 8BitDo SN30 Pro+ in each of its four modes, and
  the 8BitDo SN30 in its X-input and Switch modes. Set `PAD_MAPPING` in `main.py` to the one in use. 8BitDo pads pick their mode by the button
  held at power on, X for X-input, Y for Switch, B for Android and A for macOS.
- `pad_keys.py` saves and loads link keys.

The program prints every change of a button or axis, and blinks LED B on each press or movement.
Adding a pad means adding a mapping function, which names where each control sits in the pad's HID
report.


## Keyboard

[keyboard/main.py](keyboard/main.py)

Types into Yukon from a Bluetooth keyboard paired straight to the board. Pairing works as for the
game pad, and the keyboard's link key goes in the same file. Every key press and release is printed
by name, each line is printed when Enter is pressed, and LED B blinks on each press.

Copy `keyboard/lib/keyboard.py` and the game pad's `pad_keys.py` to the board's `lib` directory.
`keyboard.py` decodes the boot protocol report every keyboard sends, six keys at a time plus
modifiers, into named keys and typed characters for a US layout.
