# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .common import YukonModule, IO_LOW
from servo import Servo


class QuadServoDirectModule(YukonModule):
    NAME = "Quad Servo Direct"
    SERVO_1 = 0
    SERVO_2 = 1
    SERVO_3 = 2
    SERVO_4 = 3
    NUM_SERVOS = 4

    # | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
    # |-------|-------|-------|-------|-------|----------------------|-----------------------------|
    # | LOW   | LOW   | 0     | 0     | 0     | Quad Servo Direct    | A1 near 0V.   A2 near 0V    |
    # | FLOAT | LOW   | 0     | 0     | 0     | Quad Servo Direct    | A1 between.   A2 near 0V    |
    # | HIGH  | LOW   | 0     | 0     | 0     | Quad Servo Direct    | A1 near 3.3V. A2 near 0V    |
    # | LOW   | FLOAT | 0     | 0     | 0     | Quad Servo Direct    | A1 near 0V.   A2 between    |
    # | FLOAT | FLOAT | 0     | 0     | 0     | Quad Servo Direct    | A1 between.   A2 between    |
    # | HIGH  | FLOAT | 0     | 0     | 0     | Quad Servo Direct    | A1 near 3.3V. A2 between    |
    # | LOW   | HIGH  | 0     | 0     | 0     | Quad Servo Direct    | A1 near 0V.   A2 near 3.3V  |
    # | FLOAT | HIGH  | 0     | 0     | 0     | Quad Servo Direct    | A1 between.   A2 near 3.3V  |
    # | HIGH  | HIGH  | 0     | 0     | 0     | Quad Servo Direct    | A1 near 3.3V. A2 near 3.3V  |
    @staticmethod
    def is_module(adc1_level, adc2_level, slow1, slow2, slow3):
        return slow1 is IO_LOW and slow2 is IO_LOW and slow3 is IO_LOW

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

    def read_adc1(self, samples=1):
        return self.__read_adc1(samples)

    def read_adc2(self, samples=1):
        return self.__read_adc2(samples)
