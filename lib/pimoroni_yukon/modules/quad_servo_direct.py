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
    @staticmethod
    def is_module(adc_level, slow1, slow2, slow3):
        # Current protos need Slow3 jumpered to GND
        return slow1 is LOW and slow2 is LOW and slow3 is LOW

    def __init__(self, init_servos=True):
        super().__init__()
        self.__init_servos = init_servos

    def initialise(self, slot, adc1_func, adc2_func):
        # Store the pwm pins
        pins = (slot.FAST1, slot.FAST2, slot.FAST3, slot.FAST4)

        if self.__init_servos:
            # Create servo objects
            self.servos = [Servo(pins[i], freq=50) for i in range(len(pins))]
        else:
            self.servo_pins = pins

        # Pass the slot and adc functions up to the parent now that module specific initialisation has finished
        super().initialise(slot, adc1_func, adc2_func)

    def reset(self):
        if self.__init_servos:
            for servo in self.servos:
                servo.disable()

    @property
    def servo1(self):
        if self.__init_servos:
            return self.servos[0]
        raise RuntimeError("servo1 is only accessible if init_servos was True during initialisation")

    @property
    def servo2(self):
        if self.__init_servos:
            return self.servos[1]
        raise RuntimeError("servo2 is only accessible if init_servos was True during initialisation")

    @property
    def servo3(self):
        if self.__init_servos:
            return self.servos[2]
        raise RuntimeError("servo3 is only accessible if init_servos was True during initialisation")

    @property
    def servo4(self):
        if self.__init_servos:
            return self.servos[3]
        raise RuntimeError("servo4 is only accessible if init_servos was True during initialisation")

    def read_adc1(self):
        return self.__read_adc1()

    def read_adc2(self):
        return self.__read_adc2()
