# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_FLOAT, LOW, HIGH
from machine import Pin
from servo import Servo
from ucollections import OrderedDict
from pimoroni_yukon.errors import FaultError, OverTemperatureError
import pimoroni_yukon.logging as logging


class QuadServoRegModule(YukonModule):
    NAME = "Quad Servo Regulated"
    NUM_SERVOS = 4
    TEMPERATURE_THRESHOLD = 50.0

    # | ADC1  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|----------------------|-----------------------------|
    # | FLOAT | 0     | 1     | 0     | Quad Servo Regulated |                             |
    def is_module(adc_level, slow1, slow2, slow3):
        return adc_level == ADC_FLOAT and slow1 is LOW and slow2 is HIGH and slow3 is LOW

    def __init__(self, halt_on_not_pgood=False):
        super().__init__()
        self.halt_on_not_pgood = halt_on_not_pgood

        self.__last_pgood = False

    def initialise(self, slot, adc1_func, adc2_func):
        try:
            # Create pwm objects
            self.__pwms = (slot.FAST1,
                           slot.FAST2,
                           slot.FAST3,
                           slot.FAST4)
        except ValueError as e:
            if slot.ID <= 2 or slot.ID >= 5:
                conflicting_slot = (((slot.ID - 1) + 4) % 8) + 1
                raise type(e)(f"PWM channel(s) already in use. Check that the module in Slot{conflicting_slot} does not share the same PWM channel(s)") from None
            raise type(e)("PWM channel(s) already in use. Check that a module in another slot does not share the same PWM channel(s)") from None

        # Create servo objects
        self.servos = [Servo(self.__pwms[i], freq=50) for i in range(len(self.__pwms))]

        # Create the power control pin objects
        self.__power_en = slot.SLOW1
        self.__power_good = slot.SLOW2

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def configure(self):
        for servo in self.servos:
            servo.disable()

        self.__power_en.init(Pin.OUT, value=False)
        self.__power_good.init(Pin.IN)

    def enable(self):
        self.__power_en.value(True)

    def disable(self):
        self.__power_en.value(False)

    def is_enabled(self):
        return self.__power_en.value() == 1

    @property
    def servo1(self):
        return self.servos[0]

    @property
    def servo2(self):
        return self.servos[1]

    @property
    def servo3(self):
        return self.servos[2]

    @property
    def servo4(self):
        return self.servos[3]

    def read_power_good(self):
        return self.__power_good.value() == 1

    def read_temperature(self):
        return self.__read_adc2_as_temp()

    def monitor(self):
        pgood = self.read_power_good()
        if pgood is not True:
            if self.halt_on_not_pgood:
                raise FaultError(self.__message_header() + "Power is not good! Turning off output")

        temperature = self.read_temperature()
        if temperature > self.TEMPERATURE_THRESHOLD:
            raise OverTemperatureError(self.__message_header() + f"Temperature of {temperature}°C exceeded the user set level of {self.TEMPERATURE_THRESHOLD}°C! Turning off output")

        if self.__last_pgood is True and pgood is not True:
            logging.warn(self.__message_header() + "Power is not good")
        elif self.__last_pgood is not True and pgood is True:
            logging.warn(self.__message_header() + "Power is good")

        # Run some user action based on the latest readings
        if self.__monitor_action_callback is not None:
            self.__monitor_action_callback(pgood, temperature)

        self.__last_pgood = pgood
        self.__power_good_throughout = self.__power_good_throughout and pgood

        self.__max_temperature = max(temperature, self.__max_temperature)
        self.__min_temperature = min(temperature, self.__min_temperature)
        self.__avg_temperature += temperature
        self.__count_avg += 1

    def get_readings(self):
        return OrderedDict({
            "PGood": self.__power_good_throughout,
            "T_max": self.__max_temperature,
            "T_min": self.__min_temperature,
            "T_avg": self.__avg_temperature
        })

    def process_readings(self):
        if self.__count_avg > 0:
            self.__avg_temperature /= self.__count_avg

    def clear_readings(self):
        self.__power_good_throughout = True
        self.__max_temperature = float('-inf')
        self.__min_temperature = float('inf')
        self.__avg_temperature = 0
        self.__count_avg = 0
