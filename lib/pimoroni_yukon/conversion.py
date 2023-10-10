# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from math import log

# -----------------------------------------------------
# Input Voltage Conversion
# -----------------------------------------------------
VOLTAGE_IN_MIN = 5.0
VOLTAGE_IN_MAX = 17.0

# ADC measurements were taken from 10 Yukon units, and set to the average. Raw values are included for reference
MEASURED_AT_VOLTAGE_IN_ZERO = 432   # (  534,   456,   503,   395,   320,   340,   315,   382,   533,   450)
MEASURED_AT_VOLTAGE_IN_MIN = 13677  # (13666, 13700, 13787, 13645, 13573, 13693, 13535, 13639, 13728, 13802)
MEASURED_AT_VOLTAGE_IN_MAX = 45874  # (46159, 45798, 45906, 45767, 45688, 46068, 45580, 45784, 45776, 46215)

MEASURED_TO_VOLTAGE_IN_MAX_MIN = (VOLTAGE_IN_MAX - VOLTAGE_IN_MIN) / (MEASURED_AT_VOLTAGE_IN_MAX - MEASURED_AT_VOLTAGE_IN_MIN)
MEASURED_TO_VOLTAGE_IN_MIN_ZERO = VOLTAGE_IN_MIN / (MEASURED_AT_VOLTAGE_IN_MIN - MEASURED_AT_VOLTAGE_IN_ZERO)


def u16_to_voltage_in(u16):
    # return (((u16 * 3.3) / 65535) * (100 + 16)) / 16  # Ideal equation, kept for reference
    if u16 >= MEASURED_AT_VOLTAGE_IN_MIN:
        return ((u16 - MEASURED_AT_VOLTAGE_IN_MIN) * MEASURED_TO_VOLTAGE_IN_MAX_MIN) + VOLTAGE_IN_MIN
    else:
        return max((u16 - MEASURED_AT_VOLTAGE_IN_ZERO) * MEASURED_TO_VOLTAGE_IN_MIN_ZERO, 0.0)


# -----------------------------------------------------
# Output Voltage Conversion
# -----------------------------------------------------
VOLTAGE_OUT_MIN = 5.0
VOLTAGE_OUT_MAX = 17.0

# ADC measurements were taken from 10 Yukon units. Average is used, and set to the average. Raw values are included for reference
MEASURED_AT_VOLTAGE_OUT_ZERO = 579   # (  695,   608,   667,   552,   475,   491,   470,   539,   692,   605)
MEASURED_AT_VOLTAGE_OUT_MIN = 13760  # (13920, 13758, 13830, 13779, 13687, 13670, 13646, 13765, 13762, 13780)
MEASURED_AT_VOLTAGE_OUT_MAX = 45636  # (45888, 45575, 45627, 45809, 45651, 45577, 45469, 45802, 45346, 45615)

MEASURED_TO_VOLTAGE_OUT_MAX_MIN = (VOLTAGE_OUT_MAX - VOLTAGE_OUT_MIN) / (MEASURED_AT_VOLTAGE_OUT_MAX - MEASURED_AT_VOLTAGE_OUT_MIN)
MEASURED_TO_VOLTAGE_OUT_MIN_ZERO = VOLTAGE_OUT_MIN / (MEASURED_AT_VOLTAGE_OUT_MIN - MEASURED_AT_VOLTAGE_OUT_ZERO)


def u16_to_voltage_out(u16):
    # return (((u16 * 3.3) / 65535) * (100 + 16)) / 16  # Ideal equation, kept for reference
    if u16 >= MEASURED_AT_VOLTAGE_OUT_MIN:
        return ((u16 - MEASURED_AT_VOLTAGE_OUT_MIN) * MEASURED_TO_VOLTAGE_OUT_MAX_MIN) + VOLTAGE_OUT_MIN
    else:
        return max((u16 - MEASURED_AT_VOLTAGE_OUT_ZERO) * MEASURED_TO_VOLTAGE_OUT_MIN_ZERO, 0.0)


# -----------------------------------------------------
# Current Conversion
# -----------------------------------------------------
CURRENT_MIN = 0.03
CURRENT_MID = 1.0
CURRENT_MAX = 15.0

# ADC measurements were taken from 10 Yukon units. Average is used, and set to the average. Raw values are included for reference
MEASURED_AT_CURRENT_MIN = 397    # (  522  , 439,   472,   350,   317,   315,   287,   356,   491,   422)
MEASURED_AT_CURRENT_MID = 1015   # ( 1172,  1054,  1040,  1030,   928,   948,   916,   899,  1066,  1094)
MEASURED_AT_CURRENT_MAX = 14255  # (14544, 14257, 14445, 14155, 13937, 14067, 14205, 14153, 14372, 14414)

MEASURED_TO_CURRENT_MAX_MID = (CURRENT_MAX - CURRENT_MID) / (MEASURED_AT_CURRENT_MAX - MEASURED_AT_CURRENT_MID)
MEASURED_TO_CURRENT_MID_MIN = (CURRENT_MID - CURRENT_MIN) / (MEASURED_AT_CURRENT_MID - MEASURED_AT_CURRENT_MIN)


def u16_to_current(u16):
    # return (((u16 * 3.3) / 65535) * ( 1 / (2.99 * 4020 * 0.0005 / 120)))  # Ideal equation, kept for reference

    # Commented the below out as it reported underestimates for low current draws
    # if u16 >= MEASURED_AT_CURRENT_MID:
    #     return ((u16 - MEASURED_AT_CURRENT_MID) * MEASURED_TO_CURRENT_MAX_MID) + CURRENT_MID
    # else:
    #     return max(((u16 - MEASURED_AT_CURRENT_MIN) * MEASURED_TO_CURRENT_MID_MIN) + CURRENT_MIN, 0.0)

    return max(((u16 - MEASURED_AT_CURRENT_MID) * MEASURED_TO_CURRENT_MAX_MID) + CURRENT_MID, 0.0)  # This sadly overreports low current draws


# -----------------------------------------------------
# Temperature Conversion
# -----------------------------------------------------
ADC_REF = 3.3
ZERO_TEMP = 273.15
ROOM_TEMP = ZERO_TEMP + 25
PULLUP_RESISTANCE = 5100
RESISTANCE_AT_ROOM_TEMP = 10000.0
BETA = 3435


def analog_to_temp(sense):
    r_thermistor = sense / ((ADC_REF - sense) / PULLUP_RESISTANCE)
    t_kelvin = (BETA * ROOM_TEMP) / (BETA + (ROOM_TEMP * log(r_thermistor / RESISTANCE_AT_ROOM_TEMP)))
    t_celsius = t_kelvin - ZERO_TEMP
    # https://www.allaboutcircuits.com/projects/measuring-temperature-with-an-ntc-thermistor/
    return t_celsius
