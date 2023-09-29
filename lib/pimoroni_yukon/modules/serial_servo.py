# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_FLOAT, LOW, HIGH
from machine import Pin, UART
from ucollections import OrderedDict
from pimoroni_yukon.errors import OverTemperatureError


class SerialServoModule(YukonModule):
    NAME = "Serial Bus Servo"
    DEFAULT_BAUDRATE = 115200
    TEMPERATURE_THRESHOLD = 50.0

    # | ADC1  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|----------------------|-----------------------------|
    # | FLOAT | 1     | 0     | 0     | Serial Servo         |                             |
    @staticmethod
    def is_module(adc_level, slow1, slow2, slow3):
        return adc_level is ADC_FLOAT and slow1 is HIGH and slow2 is LOW and slow3 is LOW

    def __init__(self, baudrate=DEFAULT_BAUDRATE):
        super().__init__()

        self.__baudrate = baudrate

    def initialise(self, slot, adc1_func, adc2_func):
        try:
            # Create the serial object
            uart_id = ((slot.ID * 4) // 8) % 2
            print(f"Slot {slot.ID}, {uart_id}")
            self.uart = UART(uart_id, tx=slot.FAST1, rx=slot.FAST2, baudrate=self.__baudrate)
        except ValueError as e:
            raise type(e)("UART perhiperal already in use. Check that a module in another slot does not share the same UART perhiperal") from None

        # Create the direction pin objects
        self.__tx_to_data_en = slot.FAST3
        self.__data_to_rx_en = slot.FAST4

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        while self.uart.any():
            self.uart.read()

        self.__tx_to_data_en.init(Pin.OUT, True)  # Active low
        self.__data_to_rx_en.init(Pin.OUT, True)  # Active low
        
    def send_on_data(self):
        self.__data_to_rx_en.value(True)
        self.__tx_to_data_en.value(False)
        
    def receive_on_data(self):
        self.__tx_to_data_en.value(True)
        self.__data_to_rx_en.value(False)

    def read_temperature(self):
        return self.__read_adc2_as_temp()

    def monitor(self):
        temperature = self.read_temperature()
        if temperature > self.TEMPERATURE_THRESHOLD:
            raise OverTemperatureError(self.__message_header() + f"Temperature of {temperature}°C exceeded the limit of {self.TEMPERATURE_THRESHOLD}°C! Turning off output")

        # Run some user action based on the latest readings
        if self.__monitor_action_callback is not None:
            self.__monitor_action_callback(temperature)

        self.__max_temperature = max(temperature, self.__max_temperature)
        self.__min_temperature = min(temperature, self.__min_temperature)
        self.__avg_temperature += temperature

        self.__count_avg += 1

    def get_readings(self):
        return OrderedDict({
            "T_max": self.__max_temperature,
            "T_min": self.__min_temperature,
            "T_avg": self.__avg_temperature
        })

    def process_readings(self):
        if self.__count_avg > 0:
            self.__avg_temperature /= self.__count_avg

    def clear_readings(self):
        self.__max_temperature = float('-inf')
        self.__min_temperature = float('inf')
        self.__avg_temperature = 0

        self.__count_avg = 0
