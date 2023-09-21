# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from time import ticks_ms, ticks_add, ticks_diff


# Handy class for performing consistent time intervals
class RollingTime:
    def __init__(self):
        self.reset()

    def reset(self):
        self.ticks = ticks_ms()

    def advance(self, seconds):
        # Convert and handle the advance as milliseconds
        self.advance_ms(1000.0 * seconds + 0.5)

    def advance_ms(self, ms):
        if ms < 0:
            raise ValueError("advance length must be non-negative")

        self.ticks = ticks_add(self.ticks, int(ms))

    def reached(self):
        return ticks_diff(ticks_ms(), self.ticks) >= 0

    def value(self):
        return self.ticks


# Inspired by the Arduino Metro library: https://github.com/thomasfredericks/Metro-Arduino-Wiring
class TimeChecker:
    def __init__(self, interval=1.0):
        if interval <= 0:
            raise ValueError("interval must be positive")

        self.interval = int(1000.0 * interval + 0.5)
        self.restart()

    def restart(self):
        self.ticks = ticks_ms()

    def new_interval(self, interval):
        if interval <= 0:
            raise ValueError("interval must be positive")

        self.new_interval_ms(1000.0 * interval + 0.5)

    def new_interval_ms(self, interval):
        if interval <= 0:
            raise ValueError("interval must be positive")

        self.interval = int(interval)

    def check(self):
        current = ticks_ms()
        if ticks_diff(current, self.ticks) >= self.interval:
            self.ticks = current
            # without catchup would be: self.ticks = ticks_add(self.ticks, self.interval)
            return True
        return False
