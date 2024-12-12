# SPDX-FileCopyrightText: 2025 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_FLOAT, ADC_HIGH, IO_HIGH, IO_LOW
from machine import Pin
from pimoroni import RGBLED


class MechKeyModule(YukonModule):
    NAME = "Mechanical Key + RGB"

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | HIGH  | FLOAT | 1     | 0     | 0     | Mechanical Key       |                             |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level is ADC_HIGH and adc2_level is ADC_FLOAT and slow1 is IO_HIGH and slow2 is IO_LOW and slow3 is IO_LOW

    def __init__(self):
        super().__init__()

    def initialise(self, slot, adc1_func, adc2_func):

        # Create the key pin object
        self.__key = slot.FAST4
        self.__key.init(Pin.IN, Pin.PULL_UP)

        # Create the RGB LED object
        self.__led = RGBLED(slot.FAST1, slot.FAST2, slot.FAST3, invert=True)

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        self.__led.set_rgb(0, 0, 0)

    def set_rgb(self, r, g, b):
        self.__led.set_rgb(r, g, b)

    def set_hsv(self, h, s, v):
        self.__led.set_hsv(h, s, v)

    def is_pressed(self):
        return self.__key.value() != 1
