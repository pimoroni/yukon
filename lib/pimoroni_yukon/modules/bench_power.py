# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_LOW, IO_LOW, IO_HIGH
from machine import Pin, PWM
from ucollections import OrderedDict
from pimoroni_yukon.errors import FaultError, OverTemperatureError
import pimoroni_yukon.logging as logging


class BenchPowerModule(YukonModule):
    NAME = "Bench Power"

    VOLTAGE_MIN = 0.6713
    VOLTAGE_MID = 6.5052
    VOLTAGE_MAX = 12.3953
    MEASURED_AT_VOLTAGE_MIN = 0.1477
    MEASURED_AT_VOLTAGE_MID = 1.1706
    MEASURED_AT_VOLTAGE_MAX = 2.2007
    PWM_MIN = 0.3
    PWM_MAX = 0.0

    TEMPERATURE_THRESHOLD = 80.0

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | LOW   | ALL   | 1     | 0     | 0     | Bench Power          |                             |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level is ADC_LOW and slow1 is IO_HIGH and slow2 is IO_LOW and slow3 is IO_LOW

    def __init__(self, halt_on_not_pgood=False):
        super().__init__()

        self.halt_on_not_pgood = halt_on_not_pgood

        self.__last_pgood = False

    def initialise(self, slot, adc1_func, adc2_func):
        try:
            # Create the voltage pwm object
            self.__voltage_pwm = PWM(slot.FAST2, freq=250000, duty_u16=0)
        except ValueError as e:
            if slot.ID <= 2 or slot.ID >= 5:
                conflicting_slot = (((slot.ID - 1) + 4) % 8) + 1
                raise type(e)(f"PWM channel(s) already in use. Check that the module in Slot{conflicting_slot} does not share the same PWM channel(s)") from None
            raise type(e)("PWM channel(s) already in use. Check that a module in another slot does not share the same PWM channel(s)") from None

        # Create the power control pin objects
        self.__power_en = slot.FAST1
        self.__power_good = slot.SLOW1

        # Create the user accessible FAST pins
        self.FAST3 = slot.FAST3
        self.FAST4 = slot.FAST4

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        self.__voltage_pwm.duty_u16(0)

        self.__power_en.init(Pin.OUT, value=False)
        self.__power_good.init(Pin.IN)

    def enable(self):
        self.__power_en.value(True)

    def disable(self):
        self.__power_en.value(False)

    def is_enabled(self):
        return self.__motors_en.value() == 1

    def __set_pwm(self, percent):
        self.__voltage_pwm.duty_u16(int(((2 ** 16) - 1) * percent))

    def set_voltage(self, voltage):
        if voltage >= self.VOLTAGE_MID:
            percent = min((voltage - self.VOLTAGE_MID) * 0.5 / (self.VOLTAGE_MAX - self.VOLTAGE_MID) + 0.5, 1.0)
        else:
            percent = max((voltage - self.VOLTAGE_MIN) * 0.5 / (self.VOLTAGE_MID - self.VOLTAGE_MIN), 0.0)
        self.set_percent(percent)

    def set_percent(self, percent):
        if percent < 0 or percent > 1.0:
            raise ValueError("percent out of range. Expected 0.0 to 1.0")

        self.__set_pwm((percent * (self.PWM_MAX - self.PWM_MIN)) + self.PWM_MIN)

    def read_voltage(self, samples=1):
        # return (self.__read_adc1(samples) * (100 + 22)) / 22
        voltage = self.__read_adc1(samples)
        if voltage >= self.MEASURED_AT_VOLTAGE_MID:
            return ((voltage - self.MEASURED_AT_VOLTAGE_MID) * (self.VOLTAGE_MAX - self.VOLTAGE_MID)) / (self.MEASURED_AT_VOLTAGE_MAX - self.MEASURED_AT_VOLTAGE_MID) + self.VOLTAGE_MID
        else:
            return max(((voltage - self.MEASURED_AT_VOLTAGE_MIN) * (self.VOLTAGE_MID - self.VOLTAGE_MIN)) / (self.MEASURED_AT_VOLTAGE_MID - self.MEASURED_AT_VOLTAGE_MIN) + self.VOLTAGE_MIN, 0.0)

    def read_power_good(self):
        return self.__power_good.value() == 1

    def read_temperature(self, samples=1):
        return self.__read_adc2_as_temp(samples)

    def monitor(self):
        pgood = self.read_power_good()
        if pgood is not True:
            if self.halt_on_not_pgood:
                raise FaultError(self.__message_header() + "Power is not good! Turning off output")

        temperature = self.read_temperature()
        if temperature > self.TEMPERATURE_THRESHOLD:
            raise OverTemperatureError(self.__message_header() + f"Temperature of {temperature}°C exceeded the limit of {self.TEMPERATURE_THRESHOLD}°C! Turning off output")

        voltage_out = self.read_voltage()

        if self.__last_pgood is True and pgood is not True:
            logging.warn(self.__message_header() + "Power is not good")
        elif self.__last_pgood is not True and pgood is True:
            logging.warn(self.__message_header() + "Power is good")

        # Run some user action based on the latest readings
        if self.__monitor_action_callback is not None:
            self.__monitor_action_callback(pgood, temperature, voltage_out)

        self.__last_pgood = pgood
        self.__power_good_throughout = self.__power_good_throughout and pgood

        self.__max_voltage_out = max(voltage_out, self.__max_voltage_out)
        self.__min_voltage_out = min(voltage_out, self.__min_voltage_out)
        self.__avg_voltage_out += voltage_out

        self.__max_temperature = max(temperature, self.__max_temperature)
        self.__min_temperature = min(temperature, self.__min_temperature)
        self.__avg_temperature += temperature

        self.__count_avg += 1

    def get_readings(self):
        return OrderedDict({
            "PGood": self.__power_good_throughout,
            "Vo_max": self.__max_voltage_out,
            "Vo_min": self.__min_voltage_out,
            "Vo_avg": self.__avg_voltage_out,
            "T_max": self.__max_temperature,
            "T_min": self.__min_temperature,
            "T_avg": self.__avg_temperature
        })

    def process_readings(self):
        if self.__count_avg > 0:
            self.__avg_voltage_out /= self.__count_avg
            self.__avg_temperature /= self.__count_avg
            self.__count_avg = 0    # Clear the count to prevent process readings acting more than once

    def clear_readings(self):
        self.__power_good_throughout = True
        self.__max_voltage_out = float('-inf')
        self.__min_voltage_out = float('inf')
        self.__avg_voltage_out = 0

        self.__max_temperature = float('-inf')
        self.__min_temperature = float('inf')
        self.__avg_temperature = 0

        self.__count_avg = 0
