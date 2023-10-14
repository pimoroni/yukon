# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

LOG_NONE = 0
LOG_WARN = 1
LOG_INFO = 2
LOG_DEBUG = 3

level = LOG_INFO


def warn(objects='', sep='', end='\n'):
    if level >= LOG_WARN:
        print(objects, sep=sep, end=end)


def info(objects='', sep='', end='\n'):
    if level >= LOG_INFO:
        print(objects, sep=sep, end=end)


def debug(objects='', sep='', end='\n'):
    if level >= LOG_DEBUG:
        print(objects, sep=sep, end=end)


def format_dict(section_name, readings, allowed, excluded):
    text = ""
    if len(readings) > 0:
        text += f"{section_name} "
        for name, value in readings.items():
            if ((allowed is None) or (allowed is not None and name in allowed)) and ((excluded is None) or (excluded is not None and name not in excluded)):
                if isinstance(value, bool):
                    text += f"{name} = {int(value)}, "  # Output 0 or 1 rather than True of False, so bools can appear on plotter charts
                else:
                    text += f"{name} = {value}, "
    return text
