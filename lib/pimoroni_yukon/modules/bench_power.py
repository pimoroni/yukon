# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_HIGH, IO_LOW, IO_HIGH
from machine import Pin, PWM
from ucollections import OrderedDict
from pimoroni_yukon.errors import FaultError, OverTemperatureError
import pimoroni_yukon.logging as logging


class BenchPowerModule(YukonModule):
    NAME = "Bench Power"

    PWM_MIN = 0.3
    PWM_MAX = 0.0
    VOLTAGE_AT_PWM_MIN = 0.6017     # (0.6105,  0.5918,  0.5943,  0.6096,  0.6018,  0.6150,  0.5971,  0.5936)
    VOLTAGE_AT_PWM_MID = 6.4864     # (6.5311,  6.4563,  6.4727,  6.4795,  6.4663,  6.4972,  6.4605,  6.5276)
    VOLTAGE_AT_PWM_MAX = 12.4303    # (12.4997, 12.3775, 12.4170, 12.4091, 12.3959, 12.4310, 12.3937, 12.5184)
    MEASURED_AT_PWM_MIN = 0.1439    # (0.1459, 0.1416,  0.1425,  0.1454,  0.1438,  0.1472,  0.1427,  0.1420)
    MEASURED_AT_PWM_MID = 1.3094    # (1.3197, 1.3008,  1.3074,  1.3070,  1.3047,  1.3185,  1.3029,  1.3145)
    MEASURED_AT_PWM_MAX = 2.4976    # (2.5145, 2.4823,  2.4964,  2.4915,  2.4893,  2.5106,  2.4879,  2.5083)

    TEMPERATURE_THRESHOLD = 80.0

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | LOW   | ALL   | 1     | 0     | 0     | Bench Power          | Output Discharged           |
    # | FLOAT | ALL   | 1     | 0     | 0     | Bench Power          | Output Discharging          |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level is not ADC_HIGH and slow1 is IO_HIGH and slow2 is IO_LOW and slow3 is IO_LOW

    def __init__(self, halt_on_not_pgood=False):
        super().__init__()

        self.halt_on_not_pgood = halt_on_not_pgood

        self.__last_pgood = False

    def initialise(self, slot, adc1_func, adc2_func):
        # Create the voltage pwm object
        self.__voltage_pwm = PWM(slot.FAST2, freq=250000, duty_u16=0)

        # Create the power control pin objects
        self.__power_en = slot.SLOW2
        self.__power_good = slot.FAST1

        # Create the user accessible FAST pins
        self.FAST3 = slot.FAST3
        self.FAST4 = slot.FAST4

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        self.__voltage_pwm.duty_u16(0)

        self.__power_en.init(Pin.OUT, value=False)
        self.__power_good.init(Pin.IN, Pin.PULL_UP)

    def enable(self):
        self.__power_en.value(True)

    def disable(self):
        self.__power_en.value(False)

    def is_enabled(self):
        return self.__motors_en.value() == 1

    def __set_pwm(self, percent):
        self.__voltage_pwm.duty_u16(int(((2 ** 16) - 1) * percent))

    def set_voltage(self, voltage):
        if voltage >= self.VOLTAGE_AT_PWM_MID:
            percent = min((voltage - self.VOLTAGE_AT_PWM_MID) * 0.5 / (self.VOLTAGE_AT_PWM_MAX - self.VOLTAGE_AT_PWM_MID) + 0.5, 1.0)
        else:
            percent = max((voltage - self.VOLTAGE_AT_PWM_MIN) * 0.5 / (self.VOLTAGE_AT_PWM_MID - self.VOLTAGE_AT_PWM_MIN), 0.0)
        self.set_percent(percent)

    def set_percent(self, percent):
        if percent < 0 or percent > 1.0:
            raise ValueError("percent out of range. Expected 0.0 to 1.0")

        self.__set_pwm((percent * (self.PWM_MAX - self.PWM_MIN)) + self.PWM_MIN)

    def read_voltage(self, samples=1):
        # return (self.__read_adc1(samples) * (39 + 10)) / 10   # Ideal equation, kept for reference
        voltage = self.__read_adc1(samples)
        if voltage >= self.MEASURED_AT_PWM_MID:
            return ((voltage - self.MEASURED_AT_PWM_MID) * (self.VOLTAGE_AT_PWM_MAX - self.VOLTAGE_AT_PWM_MID)) / (self.MEASURED_AT_PWM_MAX - self.MEASURED_AT_PWM_MID) + self.VOLTAGE_AT_PWM_MID
        else:
            return max(((voltage - self.MEASURED_AT_PWM_MIN) * (self.VOLTAGE_AT_PWM_MID - self.VOLTAGE_AT_PWM_MIN)) / (self.MEASURED_AT_PWM_MID - self.MEASURED_AT_PWM_MIN) + self.VOLTAGE_AT_PWM_MIN, 0.0)

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
