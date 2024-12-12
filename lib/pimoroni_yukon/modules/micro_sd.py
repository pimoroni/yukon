# SPDX-FileCopyrightText: 2025 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

import vfs
from machine import SPI
from sdcard import SDCard
from .common import YukonModule, ADC_LOW, ADC_FLOAT, IO_LOW, IO_HIGH


class MicroSDModule(YukonModule):
    NAME = "Micro SD Card"

    CARD_DETECT_LEVEL = 1.65

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | LOW   | LOW   | 1     | 0     | 1     | Micro SD Card        | Card Inserted               |
    # | LOW   | HIGH  | 1     | 0     | 1     | Micro SD Card        | No Card                     |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level == ADC_LOW and adc2_level != ADC_FLOAT and slow1 is IO_HIGH and slow2 is IO_LOW and slow3 is IO_HIGH

    def __init__(self):
        super().__init__()

        try:
            import sdcard
        except ImportError:
            raise RuntimeError("This build does not contain sd card support. Please flash your Yukon with a build that supports sd cards in order to use this module.")

    def initialise(self, slot, adc1_func, adc2_func):
        try:
            # Create the SPI object
            spi_id = (((slot.ID - 1) * 4) // 8) % 2
            self.__spi = SPI(spi_id, sck=slot.FAST3, mosi=slot.FAST4, miso=slot.FAST1)

        except ValueError as e:
            raise type(e)("SPI perhiperal already in use. Check that a module in another slot does not share the same SPI perhiperal") from None

        self.__card_cs = slot.FAST2
        self.__sd = None
        self.__path = None

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        self.umount()

    def mount(self, path="/sd", baudrate=26400000):
        if self.__sd is None:
            self.__sd = SDCard(self.__spi, self.__card_cs, baudrate=baudrate)
            self.__path = path
            vfs.mount(self.__sd, self.__path)

    def umount(self):
        if self.__sd is not None:
            vfs.umount(self.__path)
            self.__sd = None
            self.__path = None

    def card_present(self):
        return self.__read_adc2() >= self.CARD_DETECT_LEVEL
