# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_LOW, LOW, HIGH
from machine import Pin
from motor import Motor, SLOW_DECAY
from ucollections import OrderedDict
from pimoroni_yukon.errors import FaultError, OverCurrentError, OverTemperatureError


class BigMotorModule(YukonModule):
    NAME = "Big Motor + Encoder"
    NUM_MOTORS = 1
    DEFAULT_FREQUENCY = 25000
    TEMPERATURE_THRESHOLD = 50.0
    CURRENT_THRESHOLD = 25.0
    SHUNT_RESISTOR = 0.001
    GAIN = 80

    # | ADC1  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|----------------------|-----------------------------|
    # | LOW   | 0     | 0     | 1     | Big Motor            | Not in fault                |
    # | LOW   | 0     | 1     | 1     | Big Motor            | In fault                    |
    @staticmethod
    def is_module(adc_level, slow1, slow2, slow3):
        return adc_level == ADC_LOW and slow1 is LOW and slow3 is HIGH

    def __init__(self, frequency=DEFAULT_FREQUENCY):
        super().__init__()
        self.__frequency = frequency

    def initialise(self, slot, adc1_func, adc2_func):
        try:
            # Create pwm objects
            self.__pwm_p = slot.FAST4
            self.__pwm_n = slot.FAST3
        except ValueError as e:
            if slot.ID <= 2 or slot.ID >= 5:
                conflicting_slot = (((slot.ID - 1) + 4) % 8) + 1
                raise type(e)(f"PWM channel(s) already in use. Check that the module in Slot{conflicting_slot} does not share the same PWM channel(s)") from None
            raise type(e)("PWM channel(s) already in use. Check that a module in another slot does not share the same PWM channel(s)") from None

        # Create motor object
        self.motor = Motor((self.__pwm_p, self.__pwm_n), freq=self.__frequency)

        # Create motor control pin objects
        self.__motor_en = slot.SLOW3
        self.__motor_nfault = slot.SLOW2

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        self.motor.disable()
        self.motor.decay_mode(SLOW_DECAY)

        self.__motor_nfault.init(Pin.IN)
        self.__motor_en.init(Pin.OUT, value=False)

    def enable(self):
        self.__motor_en.value(True)

    def disable(self):
        self.__motor_en.value(False)

    def is_enabled(self):
        return self.__motor_en.value() == 1

    def read_fault(self):
        return self.__motor_nfault.value() != 1

    def read_current(self):
        # This needs more validation
        return (abs(self.__read_adc1() - (3.3 / 2))) / (self.SHUNT_RESISTOR * self.GAIN)

    def read_temperature(self):
        return self.__read_adc2_as_temp()

    def monitor(self):
        fault = self.read_fault()
        if fault is True:
            raise FaultError(self.__message_header() + "Fault detected on motor driver! Turning off output")

        current = self.read_current()
        if current > self.CURRENT_THRESHOLD:
            raise OverCurrentError(self.__message_header() + f"Current of {current}A exceeded the user set level of {self.CURRENT_THRESHOLD}A! Turning off output")

        temperature = self.read_temperature()
        if temperature > self.TEMPERATURE_THRESHOLD:
            raise OverTemperatureError(self.__message_header() + f"Temperature of {temperature}°C exceeded the user set level of {self.TEMPERATURE_THRESHOLD}°C! Turning off output")

        # Run some user action based on the latest readings
        if self.__monitor_action_callback is not None:
            self.__monitor_action_callback(fault, current, temperature)

        self.__fault_triggered = self.__fault_triggered or fault

        self.__max_current = max(current, self.__max_current)
        self.__min_current = min(current, self.__min_current)
        self.__avg_current += current

        self.__max_temperature = max(temperature, self.__max_temperature)
        self.__min_temperature = min(temperature, self.__min_temperature)
        self.__avg_temperature += temperature

        self.__count_avg += 1

    def get_readings(self):
        return OrderedDict({
            "Fault": self.__fault_triggered,
            "C_max": self.__max_current,
            "C_min": self.__min_current,
            "C_avg": self.__avg_current,
            "T_max": self.__max_temperature,
            "T_min": self.__min_temperature,
            "T_avg": self.__avg_temperature
        })

    def process_readings(self):
        if self.__count_avg > 0:
            self.__avg_current /= self.__count_avg
            self.__avg_temperature /= self.__count_avg

    def clear_readings(self):
        self.__fault_triggered = False

        self.__max_current = float('-inf')
        self.__min_current = float('inf')
        self.__avg_current = 0

        self.__max_temperature = float('-inf')
        self.__min_temperature = float('inf')
        self.__avg_temperature = 0

        self.__count_avg = 0
