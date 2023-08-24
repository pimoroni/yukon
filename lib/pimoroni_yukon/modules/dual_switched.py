# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_FLOAT, LOW, HIGH
from machine import Pin
from ucollections import OrderedDict
from pimoroni_yukon.errors import FaultError, OverTemperatureError
import pimoroni_yukon.logging as logging


class DualSwitchedModule(YukonModule):
    NAME = "Dual Switched Output"
    NUM_SWITCHES = 2
    TEMPERATURE_THRESHOLD = 50.0

    # | ADC1  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|----------------------|-----------------------------|
    # | FLOAT | 1     | 0     | 1     | Dual Switched Output |                             |
    @staticmethod
    def is_module(adc_level, slow1, slow2, slow3):
        return adc_level == ADC_FLOAT and slow1 is HIGH and slow2 is LOW and slow3 is HIGH

    def __init__(self, halt_on_not_pgood=False):
        super().__init__()
        self.halt_on_not_pgood = halt_on_not_pgood

        self.__last_pgood1 = False
        self.__last_pgood2 = False

    def initialise(self, slot, adc1_func, adc2_func):
        # Create the switch and power control pin objects
        self.__sw_output = (slot.FAST1,
                            slot.FAST3)

        self.__sw_enable = (slot.FAST2,
                            slot.FAST4)

        self.__power_good = (slot.SLOW3,
                             slot.SLOW1)

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def configure(self):
        self.__sw_output[0].init(Pin.OUT, value=False)
        self.__sw_output[1].init(Pin.OUT, value=False)

        self.__sw_enable[0].init(Pin.OUT, value=False)
        self.__sw_enable[1].init(Pin.OUT, value=False)

        self.__power_good[0].init(Pin.IN)
        self.__power_good[1].init(Pin.IN)

    def enable(self, switch):
        if switch < 1 or switch > self.NUM_SWITCHES:
            raise ValueError("switch index out of range. Expected 1 to 2")

        self.__sw_enable[switch - 1].value(True)

    def disable(self, switch):
        if switch < 1 or switch > self.NUM_SWITCHES:
            raise ValueError("switch index out of range. Expected 1 to 2")

        self.__sw_enable[switch - 1].value(False)

    def is_enabled(self, switch):
        if switch < 1 or switch > self.NUM_SWITCHES:
            raise ValueError("switch index out of range. Expected 1 to 2")

        return self.__sw_enable[switch - 1].value() == 1

    def output(self, switch, value):
        if switch < 1 or switch > self.NUM_SWITCHES:
            raise ValueError("switch index out of range. Expected 1 to 2")

        self.__sw_output[switch - 1].value(value)

    def read_output(self, switch):
        if switch < 1 or switch > self.NUM_SWITCHES:
            raise ValueError("switch index out of range. Expected 1 to 2")

        return self.__sw_output[switch - 1].value() == 1

    def read_power_good(self, switch):
        if switch < 1 or switch > self.NUM_SWITCHES:
            raise ValueError("switch index out of range. Expected 1 to 2")

        return self.__power_good[switch - 1].value() == 1

    def read_temperature(self):
        return self.__read_adc2_as_temp()

    def monitor(self):
        pgood1 = self.read_power_good(1)
        if pgood1 is not True:
            if self.halt_on_not_pgood:
                raise FaultError(self.__message_header() + "Power1 is not good! Turning off output")
        pgood2 = self.read_power_good(2)
        if pgood2 is not True:
            if self.halt_on_not_pgood:
                raise FaultError(self.__message_header() + "Power2 is not good! Turning off output")

        temperature = self.read_temperature()
        if temperature > self.TEMPERATURE_THRESHOLD:
            raise OverTemperatureError(self.__message_header() + f"Temperature of {temperature}°C exceeded the user set level of {self.TEMPERATURE_THRESHOLD}°C! Turning off output")

        if self.__last_pgood1 is True and pgood1 is not True:
            logging.warn(self.__message_header() + "Power1 is not good")
        elif self.__last_pgood1 is not True and pgood1 is True:
            logging.warn(self.__message_header() + "Power1 is good")

        if self.__last_pgood2 is True and pgood2 is not True:
            logging.warn(self.__message_header() + "Power2 is not good")
        elif self.__last_pgood2 is not True and pgood2 is True:
            logging.warn(self.__message_header() + "Power2 is good")

        # Run some user action based on the latest readings
        if self.__monitor_action_callback is not None:
            self.__monitor_action_callback(pgood1, pgood2, temperature)

        self.__last_pgood1 = pgood1
        self.__last_pgood2 = pgood2
        self.__power_good_throughout1 = self.__power_good_throughout1 and pgood1
        self.__power_good_throughout2 = self.__power_good_throughout2 and pgood2

        self.__max_temperature = max(temperature, self.__max_temperature)
        self.__min_temperature = min(temperature, self.__min_temperature)
        self.__avg_temperature += temperature
        self.__count_avg += 1

    def get_readings(self):
        return OrderedDict({
            "PGood1": self.__power_good_throughout1,
            "PGood2": self.__power_good_throughout2,
            "T_max": self.__max_temperature,
            "T_min": self.__min_temperature,
            "T_avg": self.__avg_temperature
        })

    def process_readings(self):
        if self.__count_avg > 0:
            self.__avg_temperature /= self.__count_avg

    def clear_readings(self):
        self.__power_good_throughout1 = True
        self.__power_good_throughout2 = True
        self.__max_temperature = float('-inf')
        self.__min_temperature = float('inf')
        self.__avg_temperature = 0
        self.__count_avg = 0
