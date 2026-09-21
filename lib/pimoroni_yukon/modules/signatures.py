# SPDX-FileCopyrightText: 2025 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

# A signature is how a module is recognised, held as data so that a slot can be identified before
# any module class is imported. Each lists the values accepted for ADC1, ADC2, SLOW1, SLOW2 and
# SLOW3, in that order, and a reading matches when all five are accepted. A field listing every
# value is one the module does not care about.
#
# A module class names its signature in SIGNATURE, and YukonModule does the matching.

ADC_LOW = 0
ADC_HIGH = 1
ADC_FLOAT = 2
IO_LOW = False
IO_HIGH = True

ANY_ADC = (ADC_LOW, ADC_HIGH, ADC_FLOAT)
ANY_IO = (IO_LOW, IO_HIGH)

AUDIO_AMP = ((ADC_FLOAT,), ANY_ADC, (IO_LOW,), (IO_HIGH,), (IO_HIGH,))
BENCH_POWER = ((ADC_LOW, ADC_FLOAT), ANY_ADC, (IO_HIGH,), (IO_LOW,), (IO_LOW,))
BIG_MOTOR = ((ADC_LOW,), ANY_ADC, (IO_LOW,), ANY_IO, (IO_HIGH,))
DUAL_MOTOR = ((ADC_HIGH,), ANY_ADC, (IO_LOW,), (IO_LOW,), (IO_HIGH,))
DUAL_OUTPUT = ((ADC_FLOAT,), ANY_ADC, (IO_HIGH,), (IO_LOW,), (IO_HIGH,))
LED_STRIP = ((ADC_LOW,), ANY_ADC, (IO_HIGH,), (IO_HIGH,), (IO_HIGH,))
PROTO_POT = (ANY_ADC, (ADC_HIGH,), (IO_HIGH,), (IO_HIGH,), (IO_LOW,))
PROTO_POT_2 = ((ADC_FLOAT,), ANY_ADC, (IO_HIGH,), (IO_HIGH,), (IO_LOW,))
QUAD_SERVO_DIRECT = (ANY_ADC, ANY_ADC, (IO_LOW,), (IO_LOW,), (IO_LOW,))
QUAD_SERVO_REG = ((ADC_HIGH,), ANY_ADC, (IO_LOW,), (IO_HIGH,), ANY_IO)
RM2_WIRELESS = ((ADC_LOW,), (ADC_FLOAT,), (IO_HIGH,), (IO_LOW,), (IO_HIGH,))
SERIAL_SERVO = ((ADC_HIGH,), (ADC_HIGH,), (IO_HIGH,), (IO_LOW,), (IO_LOW,))


def matches(signature, adc1_level, adc2_level, slow1, slow2, slow3):
    """ Whether a slot's reading matches 'signature'. """
    reading = (adc1_level, adc2_level, slow1, slow2, slow3)
    for value, accepted in zip(reading, signature):
        if value not in accepted:
            return False
    return True
