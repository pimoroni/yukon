# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from .led_strip import LEDStripModule
from .quad_servo_direct import QuadServoDirectModule
from .quad_servo_reg import QuadServoRegModule
from .big_motor import BigMotorModule
from .dual_motor import DualMotorModule
from .dual_switched import DualSwitchedModule
from .bench_power import BenchPowerModule
from .audio_amp import AudioAmpModule
from .proto import ProtoPotModule

KNOWN_MODULES = (
    LEDStripModule,
    QuadServoDirectModule,
    QuadServoRegModule,
    BigMotorModule,
    DualMotorModule,
    DualSwitchedModule,
    BenchPowerModule,
    AudioAmpModule,
    ProtoPotModule)
