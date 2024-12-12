# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_HIGH, ADC_LOW, IO_HIGH, IO_LOW
from machine import Pin
from pimoroni import RGBLED


class PotModule(YukonModule):
    NAME = "Potentiometer + RGB"

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | HIGH  | LOW   | 1     | 1     | 0     | Potentiometer + RGB  |                             |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level is ADC_HIGH and adc2_level is ADC_LOW and slow1 is IO_HIGH and slow2 is IO_HIGH and slow3 is IO_LOW

    def __init__(self):
        super().__init__()

    def initialise(self, slot, adc1_func, adc2_func):

        # Create the potentiometer end pin object
        self.__pot_a = slot.SLOW1
        self.__pot_b = slot.SLOW2
        self.__pot_a.init(Pin.OUT, value=False)
        self.__pot_b.init(Pin.OUT, value=True)

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

    def read(self, samples=1):
        return self.__read_adc1(samples) / 3.3
