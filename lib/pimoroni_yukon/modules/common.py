# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from collections import OrderedDict
from pimoroni_yukon.conversion import analog_to_temp
import pimoroni_yukon.logging as logging

ADC_LOW = 0
ADC_HIGH = 1
ADC_FLOAT = 2
IO_LOW = False
IO_HIGH = True


class YukonModule:
    NAME = "Unknown"

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | FLOAT | HIGH  | 1     | 1     | 1     | Empty                |                             |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        # This will return true if a slot is detected as not being empty, so as to give useful error information
        return adc1_level is not ADC_FLOAT or adc2_level is not ADC_HIGH or slow1 is not IO_HIGH or slow2 is not IO_HIGH or slow3 is not IO_HIGH

    def __init__(self):
        self.slot = None
        self.__adc1_func = None
        self.__adc2_func = None

        self.clear_readings()

        self.__monitor_action_callback = None

    def initialise(self, slot, adc1_func, adc2_func):
        # Record the slot we are in, and the ADC functions to call
        self.slot = slot
        self.__adc1_func = adc1_func
        self.__adc2_func = adc2_func

        # Put any objects created during initialisation into a known state
        self.reset()

    def is_initialised(self):
        return self.slot is not None

    def deregister(self):
        self.slot = None
        self.__adc1_func = None
        self.__adc2_func = None

    def reset(self):
        # Override this to reset the module back into a default state post-initialisation
        pass

    def __read_adc1(self):
        return self.__adc1_func(self.slot)

    def __read_adc2(self):
        return self.__adc2_func(self.slot)

    def __read_adc2_as_temp(self):
        return analog_to_temp(self.__adc2_func(self.slot))

    def assign_monitor_action(self, callback_function):
        if not None and not callable(callback_function):
            raise TypeError("callback is not callable or None")

        self.__monitor_action_callback = callback_function

    def monitor(self):
        # Override this to perform any module specific monitoring
        pass

    def get_readings(self):
        # Override this to return any readings obtained during monitoring
        return OrderedDict()

    def get_formatted_readings(self, allowed=None, excluded=None):
        return logging.format_dict(f"[Slot{self.slot.ID}]", self.get_readings(), allowed, excluded)

    def print_readings(self, allowed=None, excluded=None):
        print(self.get_formatted_readings(allowed, excluded))

    def process_readings(self):
        # Override this to calculate averages, or do other post-processing on readings after monitor
        pass

    def clear_readings(self):
        # Override this to clear any readings that may accumulate, such as min, max, or average
        pass

    def __message_header(self):
        return f"[Slot{self.slot.ID} '{self.NAME}'] "
