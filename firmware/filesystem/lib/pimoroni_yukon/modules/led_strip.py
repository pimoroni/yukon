# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_LOW, HIGH
from machine import Pin
from ucollections import OrderedDict
from pimoroni_yukon.errors import FaultError, OverTemperatureError
import pimoroni_yukon.logging as logging


class LEDStripModule(YukonModule):
    NAME = "LED Strip"
    NEOPIXEL = 0
    DOTSTAR = 1
    TEMPERATURE_THRESHOLD = 50.0

    # | ADC1  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|----------------------|-----------------------------|
    # | LOW   | 1     | 1     | 1     | LED Strip            |                             |
    def is_module(adc_level, slow1, slow2, slow3):
        return adc_level == ADC_LOW and slow1 is HIGH and slow2 is HIGH and slow3 is HIGH

    def __init__(self, strip_type, num_pixels, brightness=1.0, halt_on_not_pgood=False):
        super().__init__()
        self.__strip_type = strip_type
        if self.__strip_type == self.NEOPIXEL:
            self.NAME += " (NeoPixel)"
        else:
            self.NAME += " (DotStar)"

        self.__num_pixels = num_pixels
        self.__brightness = brightness
        self.halt_on_not_pgood = halt_on_not_pgood

        self.__last_pgood = False

    def initialise(self, slot, adc1_func, adc2_func):
        # Create the strip driver object
        if self.__strip_type == self.NEOPIXEL:
            from neopixel import NeoPixel
            self.pixels = NeoPixel(slot.FAST4, self.__num_pixels, brightness=self.__brightness, auto_write=False)
        else:
            from adafruit_dotstar import DotStar
            self.pixels = DotStar(slot.FAST3, slot.FAST4, self.__num_pixels, brightness=self.__brightness, auto_write=False)

        # Create the power control pin objects
        self.__power_good = DigitalInOut(slot.FAST1)
        self.__power_en = DigitalInOut(slot.FAST2)

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def configure(self):
        self.__power_en.switch_to_output(False)
        self.__power_good.switch_to_input(Pull.UP)

    def enable(self):
        self.__power_en.value = True

    def disable(self):
        self.__power_en.value = False

    def is_enabled(self):
        return self.__power_en.value

    def read_power_good(self):
        return self.__power_good.value

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
