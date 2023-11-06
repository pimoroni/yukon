# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, ADC_FLOAT, IO_LOW, IO_HIGH
from machine import Pin, UART
from ucollections import OrderedDict
from pimoroni_yukon.errors import OverTemperatureError


class Duplexer:
    def __init__(self, tx_to_data, rx_to_data, active_low=False):
        self.__tx_to_data_en = tx_to_data
        self.__data_to_rx_en = rx_to_data
        self.__active_low = active_low

    def reset(self):
        self.__tx_to_data_en.init(Pin.OUT, value=self.__active_low)  # Active low
        self.__data_to_rx_en.init(Pin.OUT, value=self.__active_low)  # Active low

    def send_on_data(self):
        self.__data_to_rx_en.value(self.__active_low)
        self.__tx_to_data_en.value(not self.__active_low)

    def receive_on_data(self):
        self.__tx_to_data_en.value(self.__active_low)
        self.__data_to_rx_en.value(not self.__active_low)


class SerialServoModule(YukonModule):
    NAME = "Serial Bus Servo"
    DEFAULT_BAUDRATE = 115200

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | FLOAT | ALL   | 1     | 0     | 0     | Serial Servo         |                             |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return adc1_level is ADC_FLOAT and slow1 is IO_HIGH and slow2 is IO_LOW and slow3 is IO_LOW

    def __init__(self, baudrate=DEFAULT_BAUDRATE):
        super().__init__()

        self.__baudrate = baudrate

    def initialise(self, slot, adc1_func, adc2_func):
        try:
            # Create the serial object
            uart_id = ((slot.ID * 4) // 8) % 2
            self.uart = UART(uart_id, tx=slot.FAST1, rx=slot.FAST2, baudrate=self.__baudrate)
        except ValueError as e:
            raise type(e)("UART perhiperal already in use. Check that a module in another slot does not share the same UART perhiperal") from None

        self.duplexer = Duplexer(tx_to_data=slot.FAST3, rx_to_data=slot.FAST4, active_low=True)

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        while self.uart.any():
            self.uart.read()

        self.duplexer.reset()
