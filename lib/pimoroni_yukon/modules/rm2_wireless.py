# SPDX-FileCopyrightText: 2025 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_LOW, ADC_FLOAT, IO_LOW, IO_HIGH


class RM2WirelessModule(YukonModule):
    NAME = "RM2 Wireless"

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | LOW   | FLOAT | 1     | 0     | 1     | RM2 Wireless         |                             |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level == ADC_LOW and adc2_level == ADC_FLOAT and slow1 is IO_HIGH and slow2 is IO_LOW and slow3 is IO_HIGH

    def __init__(self):
        super().__init__()

        try:
            import cyw43
            import network
        except ImportError:
            raise RuntimeError("This build does not contain wireless networking support. Please flash your Yukon with a build that supports wireless in order to use this module.")

        self.__cyw43 = cyw43

    def initialise(self, slot, adc1_func, adc2_func):
        # Move the wireless chip's bus onto this slot's fast pins, and power the chip up
        self.__cyw43.CYW43(pin_on=slot.FAST1,
                           pin_cs=slot.FAST2,
                           pin_clock=slot.FAST3,
                           pin_dat=slot.FAST4)

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)
