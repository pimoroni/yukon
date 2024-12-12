# SPDX-FileCopyrightText: 2025 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_LOW, ADC_FLOAT, IO_LOW, IO_HIGH


class WirelessModule(YukonModule):
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
            import network
        except ImportError:
            raise RuntimeError("This build does not contain wireless networking support. Please flash your Yukon with a build that supports wireless in order to use this module.")

    def initialise(self, slot, adc1_func, adc2_func):
        if slot.ID != 5:
            raise RuntimeError("Currently the wireless module is only supported in Slot 5. Please relocate your module.")

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)
