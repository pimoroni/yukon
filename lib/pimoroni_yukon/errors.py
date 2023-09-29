# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

class OverVoltageError(Exception):
    """Exception to be used when a voltage value exceeds safe levels"""
    pass


class UnderVoltageError(Exception):
    """Exception to be used when a voltage value falls below safe levels"""
    pass


class OverCurrentError(Exception):
    """Exception to be used when a current value exceeds safe levels"""
    pass


class OverTemperatureError(Exception):
    """Exception to be used when a temperature value exceeds safe levels"""
    pass


class FaultError(Exception):
    """Exception to be used when a part of the system triggers a fault"""
    pass


class VerificationError(Exception):
    """Exception to be used when there is an issue verifying the installed hardware modules"""
    pass


class TimeoutError(Exception):
    """Exception to be used when an operation takes too long to complete"""
    pass
