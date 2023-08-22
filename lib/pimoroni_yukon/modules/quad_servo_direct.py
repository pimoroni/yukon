# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, LOW
from servo import Servo


class QuadServoDirectModule(YukonModule):
    NAME = "Quad Servo Direct"
    NUM_SERVOS = 4

    # | ADC1  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|----------------------|-----------------------------|
    # | LOW   | 0     | 0     | 0     | Quad Servo Direct    | A1 input near 0V            |
    # | FLOAT | 0     | 0     | 0     | Quad Servo Direct    | A1 input between 0 and 3.3V |
    # | HIGH  | 0     | 0     | 0     | Quad Servo Direct    | A1 input near 3.3V          |
    def is_module(adc_level, slow1, slow2, slow3):
        # Current protos need Slow3 jumpered to GND
        return slow1 is LOW and slow2 is LOW and slow3 is LOW

    def __init__(self):
        super().__init__()

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

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def configure(self):
        for servo in self.servos:
            servo.disable()

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

    def read_adc1(self):
        return self.__read_adc1()

    def read_adc2(self):
        return self.__read_adc2()
