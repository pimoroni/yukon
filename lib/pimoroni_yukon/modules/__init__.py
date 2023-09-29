# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .audio_amp import AudioAmpModule
from .bench_power import BenchPowerModule
from .big_motor import BigMotorModule
from .dual_motor import DualMotorModule
from .dual_switched import DualSwitchedModule
from .led_strip import LEDStripModule
from .proto import ProtoPotModule
from .quad_servo_direct import QuadServoDirectModule
from .quad_servo_reg import QuadServoRegModule
from .serial_servo import SerialServoModule


KNOWN_MODULES = (
    AudioAmpModule,
    BenchPowerModule,
    BigMotorModule,
    DualMotorModule,
    DualSwitchedModule,
    LEDStripModule,
    ProtoPotModule,
    QuadServoDirectModule,
    QuadServoRegModule,
    SerialServoModule
    )
