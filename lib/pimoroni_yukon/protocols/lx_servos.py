# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

import struct
import time
from pimoroni_yukon.timing import ticks_add, ticks_diff, ticks_ms
from ucollections import namedtuple

Command = namedtuple("Command", ("value", "length"))

# LX-16A Protocol
FRAME_HEADER = 0x55
FRAME_HEADER_LENGTH = 3
FRAME_LENGTH_INDEX = 3

SERVO_MOVE_TIME_WRITE = Command(1, 7)
SERVO_MOVE_TIME_READ = Command(2, 3)
SERVO_MOVE_TIME_WAIT_WRITE = Command(7, 7)
SERVO_MOVE_TIME_WAIT_READ = Command(8, 3)
SERVO_MOVE_START = Command(11, 3)
SERVO_MOVE_STOP = Command(12, 3)
SERVO_ID_WRITE = Command(13, 4)
SERVO_ID_READ = Command(14, 3)
SERVO_ANGLE_OFFSET_ADJUST = Command(17, 4)
SERVO_ANGLE_OFFSET_WRITE = Command(18, 3)
SERVO_ANGLE_OFFSET_READ = Command(19, 3)
SERVO_ANGLE_LIMIT_WRITE = Command(20, 7)
SERVO_ANGLE_LIMIT_READ = Command(21, 3)
SERVO_VIN_LIMIT_WRITE = Command(22, 7)
SERVO_VIN_LIMIT_READ = Command(23, 3)
SERVO_TEMP_MAX_LIMIT_WRITE = Command(24, 4)
SERVO_TEMP_MAX_LIMIT_READ = Command(25, 3)
SERVO_TEMP_READ = Command(26, 3)
SERVO_VIN_READ = Command(27, 3)
SERVO_POS_READ = Command(28, 3)
SERVO_OR_MOTOR_MODE_WRITE = Command(29, 7)
SERVO_OR_MOTOR_MODE_READ = Command(30, 3)
SERVO_LOAD_OR_UNLOAD_WRITE = Command(31, 4)
SERVO_LOAD_OR_UNLOAD_READ = Command(32, 3)
SERVO_LED_CTRL_WRITE = Command(33, 4)
SERVO_LED_CTRL_READ = Command(34, 3)
SERVO_LED_ERROR_WRITE = Command(35, 4)
SERVO_LED_ERROR_READ = Command(36, 3)


def CheckSum(buffer):
    checksum = 0
    length = buffer[FRAME_LENGTH_INDEX]
    last = length + 2
    for i in range(2, last):
        checksum += buffer[i]

    return (~checksum) & 0xFF

def AppendCheckSum(buffer):
    checksum = 0
    length = buffer[FRAME_LENGTH_INDEX]
    last = length + 2
    for i in range(2, last):
        checksum += buffer[i]

    buffer[last] = (~checksum) & 0xFF

def SerialServoMove(uart, id, position, time):
    if position < 0:
        position = 0
    if position > 1000:
        position = 1000

    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_MOVE_TIME_WRITE.length)
    struct.pack_into("<BBBBBHH", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_MOVE_TIME_WRITE.length,
        SERVO_MOVE_TIME_WRITE.value,
        position,
        time)
    AppendCheckSum(buffer)
    uart.write(buffer)

def SerialServoStopMove(uart, id):
    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_MOVE_STOP.length)
    struct.pack_into("<BBBBB", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_MOVE_STOP.length,
        SERVO_MOVE_STOP.value)
    AppendCheckSum(buffer)
    uart.write(buffer)

def SerialServoSetID(uart, old_id, new_id):
    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_ID_WRITE.length)
    struct.pack_into("<BBBBBB", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        old_id,
        SERVO_ID_WRITE.length,
        SERVO_ID_WRITE.value,
        new_id)
    AppendCheckSum(buffer)
    uart.write(buffer)

def SerialServoSetMode(uart, id, mode, speed):
    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_OR_MOTOR_MODE_WRITE.length)
    struct.pack_into("<BBBBBBBH", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_OR_MOTOR_MODE_WRITE.length,
        SERVO_OR_MOTOR_MODE_WRITE.value,
        mode,
        0,
        speed)
    AppendCheckSum(buffer)
    uart.write(buffer)

def SerialServoLoad(uart, id):
    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_LOAD_OR_UNLOAD_WRITE.length)
    struct.pack_into("<BBBBBB", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_LOAD_OR_UNLOAD_WRITE.length,
        SERVO_LOAD_OR_UNLOAD_WRITE.value,
        1)
    AppendCheckSum(buffer)
    uart.write(buffer)

def SerialServoUnload(uart, id):
    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_LOAD_OR_UNLOAD_WRITE.length)
    struct.pack_into("<BBBBBB", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_LOAD_OR_UNLOAD_WRITE.length,
        SERVO_LOAD_OR_UNLOAD_WRITE.value,
        0)
    AppendCheckSum(buffer)
    uart.write(buffer)

def SerialServoActivateLED(uart, id):
    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_LED_CTRL_WRITE.length)
    struct.pack_into("<BBBBBB", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_LED_CTRL_WRITE.length,
        SERVO_LED_CTRL_WRITE.value,
        1)
    AppendCheckSum(buffer)

    uart.write(buffer)

def SerialServoDeactivateLED(uart, id):
    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_LED_CTRL_WRITE.length)
    struct.pack_into("<BBBBBB", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_LED_CTRL_WRITE.length,
        SERVO_LED_CTRL_WRITE.value,
        0)
    AppendCheckSum(buffer)

    uart.write(buffer)

def SerialServoReceiveHandle(uart):
    frameStarted = False
    frameCount = 0
    dataCount = 0
    dataLength = 2
    rxBuf = 0
    recvBuf = bytearray(32)

    while uart.in_waiting > 0:
        rxBuf = uart.read(1)[0]
        time.sleep_us(100)
        if not frameStarted:
            if rxBuf == FRAME_HEADER:
                frameCount += 1
                if frameCount == 2:
                    frameCount = 0
                    frameStarted = True
                    dataCount = 1
            else:
                frameStarted = False
                dataCount = 0
                frameCount = 0

        if frameStarted:
            recvBuf[dataCount] = rxBuf
            if dataCount == 3:
                dataLength = recvBuf[dataCount]
                if dataLength < 3 or dataCount > 7:
                    dataLength = 2
                    frameStarted = False
            dataCount += 1
            if dataCount == dataLength + 3:
                if CheckSum(recvBuf) == recvBuf[dataCount - 1]:
                    #print("Check SUM OK!!", end="\n\n")
                    frameStarted = False
                    return recvBuf[5:5 + dataLength - 3]

    return None

def WaitForReceive(uart, id, timeout):
    ms = 1000.0 * timeout + 0.5
    end_ms = ticks_add(ticks_ms(), int(ms))

    while uart.in_waiting == 0:
        remaining_ms = ticks_diff(end_ms, ticks_ms())
        if remaining_ms <= 0:
            raise TimeoutError(f"Serial servo #{id} did not reply within the set time")

def SerialServoReadTemperature(uart, send_func, rec_func, id, timeout=1.0):
    send_func()

    ret = 0

    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_TEMP_READ.length)
    struct.pack_into("<BBBBB", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_TEMP_READ.length,
        SERVO_TEMP_READ.value)
    AppendCheckSum(buffer)

    uart.reset_input_buffer()

    uart.write(buffer)
        time.sleep_us(100)

    try:
        rec_func()
        WaitForReceive(uart, id, timeout)

        returned_buffer = SerialServoReceiveHandle(uart)
        if returned_buffer is not None:
            ret = struct.unpack("<B", returned_buffer)[0]
        else:
            ret = -1
    finally:
        send_func()

    return ret


def SerialServoReadID(uart, send_func, rec_func, id, timeout=1.0):
    send_func()

    ret = 0

    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_ID_READ.length)
    struct.pack_into("<BBBBB", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_ID_READ.length,
        SERVO_ID_READ.value)
    AppendCheckSum(buffer)

    uart.reset_input_buffer()

    uart.write(buffer)
    time.sleep_us(500)

    try:
        rec_func()
        WaitForReceive(uart, id, timeout)

        returned_buffer = SerialServoReceiveHandle(uart)
        if returned_buffer is not None:
            ret = struct.unpack("<B", returned_buffer)[0]
        else:
            ret = -1
    finally:
        send_func()

    return ret

def SerialServoReadPosition(uart, send_func, rec_func, id, timeout=1.0):
    send_func()

    ret = 0

    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_POS_READ.length)
    struct.pack_into("<BBBBB", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_POS_READ.length,
        SERVO_POS_READ.value)
    AppendCheckSum(buffer)

    uart.reset_input_buffer()

    uart.write(buffer)
    time.sleep_us(500)

    try:
        rec_func()
        WaitForReceive(uart, id, timeout)

        returned_buffer = SerialServoReceiveHandle(uart)
        if returned_buffer is not None:
            ret = struct.unpack("<H", returned_buffer)[0]
        else:
            ret = -1
    finally:
        send_func()

    return ret

def SerialServoReadVin(uart, send_func, rec_func, id, timeout=1.0):
    send_func()

    ret = 0

    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_VIN_READ.length)
    struct.pack_into("<BBBBB", buffer, 0,  # fmt, buffer, offset
        FRAME_HEADER,
        FRAME_HEADER,
        id,
        SERVO_VIN_READ.length,
        SERVO_VIN_READ.value)
    AppendCheckSum(buffer)

    uart.reset_input_buffer()

    uart.write(buffer)
    time.sleep_us(500)

    try:
        rec_func()
        WaitForReceive(uart, id, timeout)

        returned_buffer = SerialServoReceiveHandle(uart)
        if returned_buffer is not None:
            ret = struct.unpack("<H", returned_buffer)[0]
        else:
            ret = -2048
    finally:
        send_func()

    return ret