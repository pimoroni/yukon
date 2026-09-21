# SPDX-FileCopyrightText: 2025 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from pimoroni_yukon.modules import signatures

# Each module class, the file it lives in and the reading that identifies it. Order matters
# because the first signature to match wins. Holding all three here lets a slot be identified
# without importing anything, so only the class that matched is loaded into memory.
KNOWN_MODULES = (
    ("AudioAmpModule",        "audio_amp",         signatures.AUDIO_AMP),
    ("BenchPowerModule",      "bench_power",       signatures.BENCH_POWER),
    ("BigMotorModule",        "big_motor",         signatures.BIG_MOTOR),
    ("DualMotorModule",       "dual_motor",        signatures.DUAL_MOTOR),
    ("DualOutputModule",      "dual_output",       signatures.DUAL_OUTPUT),
    ("LEDStripModule",        "led_strip",         signatures.LED_STRIP),
    ("ProtoPotModule",        "proto",             signatures.PROTO_POT),
    ("QuadServoDirectModule", "quad_servo_direct", signatures.QUAD_SERVO_DIRECT),
    ("QuadServoRegModule",    "quad_servo_reg",    signatures.QUAD_SERVO_REG),
    ("RM2WirelessModule",     "rm2_wireless",      signatures.RM2_WIRELESS),
    ("SerialServoModule",     "serial_servo",      signatures.SERIAL_SERVO),
)


# Import the file holding 'name' and bind the class here, so a later read costs nothing
def __load(name):
    for known, source, _ in KNOWN_MODULES:
        if known == name:
            break
    else:
        raise AttributeError(name)
    value = getattr(__import__(__name__ + "." + source, None, None, (name,)), name)
    globals()[name] = value
    return value


def is_known(module_type):
    """ Whether module_type is one of the module classes listed here.

    Checked by name, so registering a module does not import the other ten. The identity test
    then rejects a different class that happens to share a name.
    """
    name = module_type.__name__
    for known, _, _ in KNOWN_MODULES:
        if known == name:
            return module_type is __load(name)
    return False


def match(adc1_level, adc2_level, slow1, slow2, slow3):
    """ The module class a slot's reading identifies, or None. Only the match is imported. """
    for name, _, signature in KNOWN_MODULES:
        if signatures.matches(signature, adc1_level, adc2_level, slow1, slow2, slow3):
            return __load(name)
    return None


def __getattr__(name):
    return __load(name)
