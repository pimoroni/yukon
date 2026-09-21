# SPDX-FileCopyrightText: 2025 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

# A signature is how a module is recognised, held as data so that a slot can be identified before
# any module class is imported. Each lists the values its five fields accept, in the column order
# of the tables below, and a reading matches when all five are accepted. A table's ALL is a field
# the module does not care about, written here as ANY_ADC or ANY_IO.
#
# A module class names its signature in SIGNATURE, and YukonModule does the matching.

ADC_LOW = 0
ADC_HIGH = 1
ADC_FLOAT = 2
IO_LOW = False
IO_HIGH = True

ANY_ADC = (ADC_LOW, ADC_HIGH, ADC_FLOAT)
ANY_IO = (IO_LOW, IO_HIGH)

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | FLOAT | ALL   | 0     | 1     | 1     | Audio Amp            |                             |
AUDIO_AMP = ((ADC_FLOAT,), ANY_ADC, (IO_LOW,), (IO_HIGH,), (IO_HIGH,))

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | LOW   | ALL   | 1     | 0     | 0     | Bench Power          | Output Discharged           |
# | FLOAT | ALL   | 1     | 0     | 0     | Bench Power          | Output Discharging          |
BENCH_POWER = ((ADC_LOW, ADC_FLOAT), ANY_ADC, (IO_HIGH,), (IO_LOW,), (IO_LOW,))

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | LOW   | ALL   | 0     | 0     | 1     | Big Motor            | Not in fault                |
# | LOW   | ALL   | 0     | 1     | 1     | Big Motor            | In fault                    |
BIG_MOTOR = ((ADC_LOW,), ANY_ADC, (IO_LOW,), ANY_IO, (IO_HIGH,))

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | HIGH  | ALL   | 0     | 0     | 1     | Dual Motor           |                             |
DUAL_MOTOR = ((ADC_HIGH,), ANY_ADC, (IO_LOW,), (IO_LOW,), (IO_HIGH,))

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | FLOAT | ALL   | 1     | 0     | 1     | Dual Switched Output |                             |
DUAL_OUTPUT = ((ADC_FLOAT,), ANY_ADC, (IO_HIGH,), (IO_LOW,), (IO_HIGH,))

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | LOW   | ALL   | 1     | 1     | 1     | LED Strip            |                             |
LED_STRIP = ((ADC_LOW,), ANY_ADC, (IO_HIGH,), (IO_HIGH,), (IO_HIGH,))

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | LOW   | HIGH  | 1     | 1     | 0     | Proto Potentiometer  | Pot in low position         |
# | FLOAT | HIGH  | 1     | 1     | 0     | Proto Potentiometer  | Pot in middle position      |
# | HIGH  | HIGH  | 1     | 1     | 0     | Proto Potentiometer  | Pot in high position        |
PROTO_POT = (ANY_ADC, (ADC_HIGH,), (IO_HIGH,), (IO_HIGH,), (IO_LOW,))

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | FLOAT | LOW   | 1     | 1     | 0     | Proto Potentiometer  | Pot in low position         |
# | FLOAT | FLOAT | 1     | 1     | 0     | Proto Potentiometer  | Pot in middle position      |
# | FLOAT | HIGH  | 1     | 1     | 0     | Proto Potentiometer  | Pot in high position        |
PROTO_POT_2 = ((ADC_FLOAT,), ANY_ADC, (IO_HIGH,), (IO_HIGH,), (IO_LOW,))

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
QUAD_SERVO_DIRECT = (ANY_ADC, ANY_ADC, (IO_LOW,), (IO_LOW,), (IO_LOW,))

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | HIGH  | ALL   | 0     | 1     | 0     | Quad Servo Regulated | Power Not Good              |
# | HIGH  | ALL   | 0     | 1     | 1     | Quad Servo Regulated | Power Good                  |
QUAD_SERVO_REG = ((ADC_HIGH,), ANY_ADC, (IO_LOW,), (IO_HIGH,), ANY_IO)

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | LOW   | FLOAT | 1     | 0     | 1     | RM2 Wireless         |                             |
RM2_WIRELESS = ((ADC_LOW,), (ADC_FLOAT,), (IO_HIGH,), (IO_LOW,), (IO_HIGH,))

# | ADC1  | ADC2  | SLOW1 | SLOW2 | SLOW3 | Module               | Condition (if any)          |
# |-------|-------|-------|-------|-------|----------------------|-----------------------------|
# | HIGH  | HIGH  | 1     | 0     | 0     | Serial Servo         |                             |
SERIAL_SERVO = ((ADC_HIGH,), (ADC_HIGH,), (IO_HIGH,), (IO_LOW,), (IO_LOW,))


def matches(signature, adc1_level, adc2_level, slow1, slow2, slow3):
    """ Whether a slot's reading matches 'signature'. """
    reading = (adc1_level, adc2_level, slow1, slow2, slow3)
    for value, accepted in zip(reading, signature):
        if value not in accepted:
            return False
    return True
