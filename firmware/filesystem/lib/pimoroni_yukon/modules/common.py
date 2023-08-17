# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

import math
from collections import OrderedDict

ADC_LOW = 0
ADC_HIGH = 1
ADC_FLOAT = 2
ADC_ANY = 3
LOW = False
HIGH = True


class YukonModule:
    NAME = "Unnamed"

    ROOM_TEMP = 273.15 + 25
    RESISTOR_AT_ROOM_TEMP = 10000.0
    BETA = 3435

    def is_module(adc_level, slow1, slow2, slow3):
        return False

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

        # Configure any objects created during initialisation
        self.configure()

    def is_initialised(self):
        return self.slot is not None

    def deregister(self):
        self.slot = None
        self.__adc1_func = None
        self.__adc2_func = None

    def configure(self):
        # Function for (re)configuring pins etc to their default states needed by the module
        pass

    def __read_adc1(self):
        return self.__adc1_func(self.slot)

    def __read_adc2(self):
        return self.__adc2_func(self.slot)

    def __read_adc2_as_temp(self):
        sense = self.__adc2_func(self.slot)
        r_thermistor = sense / ((3.3 - sense) / 5100)
        t_kelvin = (self.BETA * self.ROOM_TEMP) / (self.BETA + (self.ROOM_TEMP * math.log(r_thermistor / self.RESISTOR_AT_ROOM_TEMP)))
        t_celsius = t_kelvin - 273.15
        # https://www.allaboutcircuits.com/projects/measuring-temperature-with-an-ntc-thermistor/
        return t_celsius

    def assign_monitor_action(self, callback_function):
        if not None and not callable(callback_function):
            raise TypeError("callback is not callable or None")

        self.__monitor_action_callback = callback_function

    def monitor(self):
        pass

    def get_readings(self):
        return OrderedDict()

    def process_readings(self):
        # Use this to calculate averages, or do other post-processing on readings after monitor
        pass

    def clear_readings(self):
        # Clear any readings that may accumulate, such as min, max, or average
        pass

    def __message_header(self):
        return f"[Slot{self.slot.ID} '{self.NAME}'] "
