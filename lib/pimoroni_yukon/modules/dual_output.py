# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_FLOAT, IO_LOW, IO_HIGH
from machine import Pin
from ucollections import OrderedDict
from pimoroni_yukon.errors import FaultError, OverTemperatureError
import pimoroni_yukon.logging as logging


class DualOutputModule(YukonModule):
    NAME = "Dual Switched Output"
    OUTPUT_1 = 0
    OUTPUT_2 = 1
    NUM_OUTPUTS = 2
    TEMPERATURE_THRESHOLD = 50.0

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | FLOAT | ALL   | 1     | 0     | 1     | Dual Switched Output |                             |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level == ADC_FLOAT and slow1 is IO_HIGH and slow2 is IO_LOW and slow3 is IO_HIGH

    def __init__(self, halt_on_not_pgood=False):
        super().__init__()
        self.halt_on_not_pgood = halt_on_not_pgood

        self.__last_pgood1 = False
        self.__last_pgood2 = False

    def initialise(self, slot, adc1_func, adc2_func):
        # Create the switch and power control pin objects
        self.outputs = [slot.FAST1,
                        slot.FAST3]

        self.__sw_enable = (slot.FAST2,
                            slot.FAST4)

        self.__power_good = (slot.SLOW3,
                             slot.SLOW1)

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        self.outputs[0].init(Pin.OUT, value=False)
        self.outputs[1].init(Pin.OUT, value=False)

        self.__sw_enable[0].init(Pin.OUT, value=False)
        self.__sw_enable[1].init(Pin.OUT, value=False)

        self.__power_good[0].init(Pin.IN)
        self.__power_good[1].init(Pin.IN)

    def enable(self, output=None):
        if output is None:
            self.__sw_enable[0].value(True)
            self.__sw_enable[1].value(True)
        elif isinstance(output, int):
            if output < 0 or output >= self.NUM_OUTPUTS:
                raise ValueError("output index out of range. Expected 0 to 1")
            self.__sw_enable[output].value(True)

    def disable(self, output=None):
        if output is None:
            self.__sw_enable[0].value(False)
            self.__sw_enable[1].value(False)
        elif isinstance(output, int):
            if output < 0 or output >= self.NUM_OUTPUTS:
                raise ValueError("output index out of range. Expected 0 to 1")
            self.__sw_enable[output].value(False)

    def is_enabled(self, output=None):
        if output is None:
            return self.__sw_enable[0].value() == 1 or self.__sw_enable[1].value() == 1
        elif isinstance(output, int):
            if output < 0 or output >= self.NUM_OUTPUTS:
                raise ValueError("output index out of range. Expected 0 to 1")
            return self.__sw_enable[output].value() == 1

    @property
    def output1(self):
        return self.output[0]

    @property
    def output2(self):
        return self.output[1]

    def read_power_good1(self):
        return self.__power_good[0].value() == 1

    def read_power_good2(self):
        return self.__power_good[1].value() == 1

    def read_temperature(self):
        return self.__read_adc2_as_temp()

    def monitor(self):
        pgood1 = self.read_power_good1()
        if pgood1 is not True:
            if self.halt_on_not_pgood:
                raise FaultError(self.__message_header() + "Power1 is not good! Turning off output")
        pgood2 = self.read_power_good2()
        if pgood2 is not True:
            if self.halt_on_not_pgood:
                raise FaultError(self.__message_header() + "Power2 is not good! Turning off output")

        temperature = self.read_temperature()
        if temperature > self.TEMPERATURE_THRESHOLD:
            raise OverTemperatureError(self.__message_header() + f"Temperature of {temperature}°C exceeded the limit of {self.TEMPERATURE_THRESHOLD}°C! Turning off output")

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
            self.__count_avg = 0    # Clear the count to prevent process readings acting more than once

    def clear_readings(self):
        self.__power_good_throughout1 = True
        self.__power_good_throughout2 = True
        self.__max_temperature = float('-inf')
        self.__min_temperature = float('inf')
        self.__avg_temperature = 0
        self.__count_avg = 0
