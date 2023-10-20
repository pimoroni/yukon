# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_LOW, IO_HIGH
from machine import Pin
from ucollections import OrderedDict
from pimoroni_yukon.errors import FaultError, OverTemperatureError
import pimoroni_yukon.logging as logging


class LEDStripModule(YukonModule):
    NAME = "LED Strip"
    NEOPIXEL = 0
    DUAL_NEOPIXEL = 1
    DOTSTAR = 2
    STRIP_1 = 0       # Only for DUAL_NEOPIXEL strip_type
    STRIP_2 = 1       # Only for DUAL_NEOPIXEL strip_type
    NUM_STRIPS = 1    # Becomes 2 with the DUAL_NEOPIXEL strip_type
    TEMPERATURE_THRESHOLD = 70.0

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | LOW   | ALL   | 1     | 1     | 1     | LED Strip            |                             |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level == ADC_LOW and slow1 is IO_HIGH and slow2 is IO_HIGH and slow3 is IO_HIGH

    def __init__(self, strip_type, pio, sm, num_leds, brightness=1.0, halt_on_not_pgood=False):
        super().__init__()

        if strip_type < 0 or strip_type > 2:
            raise ValueError("strip_type out of range. Expected 0 (NEOPIXEL), 1 (DUAL_NEOPIXEL) or 2 (DOTSTAR)")

        if pio < 0 or pio > 1:
            raise ValueError("pio out of range. Expected 0 or 1")

        if sm < 0 or sm > 3:
            raise ValueError("sm out of range. Expected 0 to 3")

        if strip_type == self.DUAL_NEOPIXEL and isinstance(num_leds, (list, tuple)):
            if len(num_leds) != 2:
                raise ValueError("num_leds list or tuple should only contain two values")

            if num_leds[0] <= 0 or num_leds[1] <= 0:
                raise ValueError("value in num_leds list or tuple out of range. Expected greater than 0")
        else:
            if isinstance(num_leds, (list, tuple)):
                raise ValueError("num_leds should not be a list or tuple for the NEOPIXEL and DOTSTAR strip types")

            if num_leds <= 0:
                raise ValueError("num_leds out of range. Expected greater than 0")

        if strip_type == self.DOTSTAR and (brightness < 0.0 or brightness > 1.0):
            raise ValueError("brightness out of range. Expected 0.0 to 1.0")

        self.__strip_type = strip_type
        if self.__strip_type == self.NEOPIXEL:
            self.NAME += " (NeoPixel)"
        elif self.__strip_type == self.DUAL_NEOPIXEL:
            self.NAME += " (Dual NeoPixel)"
            self.NUM_STRIPS = 2
        else:
            self.NAME += " (DotStar)"

        self.__pio = pio
        self.__sm = sm
        self.__num_leds = num_leds
        self.__brightness = brightness
        self.halt_on_not_pgood = halt_on_not_pgood

        self.__last_pgood = False

    def initialise(self, slot, adc1_func, adc2_func):
        # Create the strip driver object
        if self.__strip_type == self.NEOPIXEL or self.__strip_type == self.DUAL_NEOPIXEL:
            from plasma import WS2812
            if self.__strip_type == self.DUAL_NEOPIXEL:
                num_leds = self.__num_leds
                if not isinstance(num_leds, (list, tuple)):
                    num_leds = (num_leds, num_leds)

                self.strips = [WS2812(num_leds[0], self.__pio, self.__sm, slot.FAST4),
                               WS2812(num_leds[1], self.__pio, (self.__sm + 1) % 4, slot.FAST3)]
            else:
                self.strip = WS2812(self.__num_leds, self.__pio, self.__sm, slot.FAST4)
        else:
            from plasma import APA102
            self.strip = APA102(self.__num_leds, self.__pio, self.__sm, slot.FAST4, slot.FAST3)
            self.strip.set_brightness(int(self.__brightness * 31))

        # Create the power control pin objects
        self.__power_good = slot.FAST1
        self.__power_en = slot.FAST2

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        self.__power_en.init(Pin.OUT, value=False)
        self.__power_good.init(Pin.IN, Pin.PULL_UP)

    def enable(self):
        self.__power_en.value(True)

    def disable(self):
        self.__power_en.value(False)

    def is_enabled(self):
        return self.__power_en.value() == 1

    @property
    def strip1(self):
        if self.__strip_type == self.DUAL_NEOPIXEL:
            return self.strips[0]
        raise RuntimeError("strip1 is only accessible with the DUAL_NEOPIXEL strip_type")

    @property
    def strip2(self):
        if self.__strip_type == self.DUAL_NEOPIXEL:
            return self.strips[1]
        raise RuntimeError("strip2 is only accessible with the DUAL_NEOPIXEL strip_type")

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
            raise OverTemperatureError(self.__message_header() + f"Temperature of {temperature}°C exceeded the limit of {self.TEMPERATURE_THRESHOLD}°C! Turning off output")

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
            self.__count_avg = 0    # Clear the count to prevent process readings acting more than once

    def clear_readings(self):
        self.__power_good_throughout = True
        self.__max_temperature = float('-inf')
        self.__min_temperature = float('inf')
        self.__avg_temperature = 0
        self.__count_avg = 0
