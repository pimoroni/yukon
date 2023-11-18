# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

import math
from machine import Timer, Pin

"""
A timer-based class for driving a stepper motor.
There are likely to be many quirks and missing features of this class, that make it just "okay", hence the name.
The hope is to improve on this based on user feedback, and port it to a C++ module to improve performance.
"""


class OkayStepper:
    DEFAULT_CURRENT_SCALE = 0.5
    HOLD_CURRENT_PERCENT = 0.2

    STEP_PHASES = 4
    DEFAULT_MICROSTEPS = 8

    def __init__(self, motor_a, motor_b, alt_motor_a=None, alt_motor_b=None, steps_per_unit=1.0, current_scale=DEFAULT_CURRENT_SCALE, microsteps=DEFAULT_MICROSTEPS, debug_pin=None):
        self.__motor_a = motor_a
        self.__motor_b = motor_b
        self.__alt_motor_a = alt_motor_a
        self.__alt_motor_b = alt_motor_b
        self.__steps_per_unit = steps_per_unit
        self.__debug_pin = debug_pin
        if self.__debug_pin is not None:
            self.__debug_pin.init(Pin.OUT)

        self.__moving = False
        self.__current_microstep = 0
        self.__end_microstep = 0

        self.__step_timer = Timer()

        current_scale = max(min(current_scale, 1.0), 0.0)

        self.__microsteps = microsteps
        self.__total_microsteps = self.STEP_PHASES * microsteps
        self.__step_table = self.__create_table(current_scale)
        self.__hold_table = self.__create_table(current_scale * self.HOLD_CURRENT_PERCENT)

    def __create_table(self, current_scale):
        table = [0] * self.__total_microsteps
        for i in range(self.__total_microsteps):
            angle = (i / self.__total_microsteps) * math.pi * 2.0
            table[i] = (math.cos(angle) * current_scale,
                        0 - math.sin(angle) * current_scale)
        return table

    def __set_duties(self, table):
        stepper_entry = table[self.__current_microstep % self.__total_microsteps]
        self.__motor_a.duty(stepper_entry[0])
        self.__motor_b.duty(stepper_entry[1])
        if self.__alt_motor_a is not None:
            self.__alt_motor_a.duty(stepper_entry[0])
        if self.__alt_motor_b is not None:
            self.__alt_motor_b.duty(stepper_entry[1])

    def hold(self):
        self.__set_duties(self.__hold_table)

    def release(self):
        self.__step_timer.deinit()
        self.__motor_a.disable()
        self.__motor_b.disable()
        if self.__alt_motor_a is not None:
            self.__alt_motor_a.disable()
        if self.__alt_motor_b is not None:
            self.__alt_motor_b.disable()

    def __increase_microstep(self, timer):
        if self.__debug_pin is not None:
            self.__debug_pin.on()

        self.__current_microstep += 1
        if self.__current_microstep < self.__end_microstep:
            self.__set_duties(self.__step_table)
        else:
            timer.deinit()
            self.hold()
            self.__moving = False

        if self.__debug_pin is not None:
            self.__debug_pin.off()

    def __decrease_microstep(self, timer):
        if self.__debug_pin is not None:
            self.__debug_pin.on()

        self.__current_microstep -= 1
        if self.__current_microstep > self.__end_microstep:
            self.__set_duties(self.__step_table)
        else:
            timer.deinit()
            self.hold()
            self.__moving = False

        if self.__debug_pin is not None:
            self.__debug_pin.off()

    def __hold_microstep(self, timer):
        if self.__debug_pin is not None:
            self.__debug_pin.on()

        timer.deinit()
        self.hold()
        self.__moving = False

        if self.__debug_pin is not None:
            self.__debug_pin.off()

    def __move_by(self, microstep_diff, travel_time, debug=False):
        if microstep_diff != 0:
            self.__end_microstep = self.__current_microstep + microstep_diff

            tick_hz = 1000000
            period_per_step = int((travel_time * tick_hz) / abs(microstep_diff))
            while (period_per_step // 10) * 10 == period_per_step and tick_hz > 1000:
                period_per_step //= 10
                tick_hz //= 10

            if debug:
                print(f"> Moving from {self.__current_microstep / self.__microsteps} to {self.__end_microstep / self.__microsteps}, in {travel_time}s")

            self.__moving = True
            self.__step_timer.init(mode=Timer.PERIODIC, period=period_per_step, tick_hz=tick_hz,
                                   callback=self.__increase_microstep if microstep_diff > 0 else self.__decrease_microstep)
        else:
            if debug:
                print(f"> Idling at {self.__current_microstep / self.__microsteps} for {travel_time}s")

            self.hold()
            self.__moving = True
            self.__step_timer.init(mode=Timer.ONE_SHOT,
                                   period=int(travel_time * 1000),
                                   tick_hz=1000,
                                   callback=self.__hold_microstep)

    def move_to_step(self, step, travel_time, debug=False):
        self.__step_timer.deinit()
        if travel_time <= 0.0:
            raise ValueError("travel_time out of range. Expected greater than 0.0")

        microstep_diff = int(step * self.__microsteps) - self.__current_microstep
        self.__move_by(microstep_diff, travel_time, debug)

    def move_by_steps(self, steps, travel_time, debug=False):
        self.__step_timer.deinit()
        if travel_time <= 0.0:
            raise ValueError("travel_time out of range. Expected greater than 0.0")

        microstep_diff = int(steps * self.__microsteps)
        self.__move_by(microstep_diff, travel_time, debug)

    def move_to(self, unit, travel_time, debug=False):
        self.move_to_step(unit * self.__steps_per_unit, travel_time, debug)

    def move_by(self, units, travel_time, debug=False):
        self.move_by_steps(units * self.__steps_per_unit, travel_time, debug)

    def steps(self):
        return self.__current_microstep / self.__microsteps

    def units(self):
        return self.steps() / self.__steps_per_unit

    def step_diff(self, step):
        microstep_diff = int(step * self.__microsteps) - self.__current_microstep
        return microstep_diff / self.__microsteps

    def unit_diff(self, unit):
        step = unit * self.__steps_per_unit
        return self.step_diff(step) / self.__steps_per_unit

    def is_moving(self):
        return self.__moving

    def wait_for_move(self):
        while self.__moving:
            pass

    def zero_position(self):
        self.__current_microstep = 0
