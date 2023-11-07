# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

import time
import struct
from machine import Pin
from pimoroni_yukon.timing import ticks_add, ticks_diff, ticks_ms
from pimoroni_yukon.errors import TimeoutError
import pimoroni_yukon.logging as logging
from ucollections import namedtuple

Command = namedtuple("Command", ("value", "length"))

# LX Servo Protocol
FRAME_HEADER = 0x55
FRAME_HEADER_LENGTH = 3
FRAME_LENGTH_INDEX = 3
BROADCAST_ID = 0xFE

SERVO_MOVE_TIME_WRITE = Command(1, 7)
SERVO_MOVE_TIME_READ = Command(2, 3)
SERVO_MOVE_TIME_WAIT_WRITE = Command(7, 7)
# SERVO_MOVE_TIME_WAIT_READ = Command(8, 3)  # Does not appear to be implemented on the LX-16A
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


def SerialServoMove(uart, duplexer, id, position, time):
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


def SerialServoStopMove(uart, duplexer, id):
    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_MOVE_STOP.length)
    struct.pack_into("<BBBBB", buffer, 0,  # fmt, buffer, offset
                     FRAME_HEADER,
                     FRAME_HEADER,
                     id,
                     SERVO_MOVE_STOP.length,
                     SERVO_MOVE_STOP.value)
    AppendCheckSum(buffer)
    uart.write(buffer)


def SerialServoSetID(uart, duplexer, old_id, new_id):
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


def SerialServoSetMode(uart, duplexer, id, mode, speed):
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


def SerialServoLoad(uart, duplexer, id):
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


def SerialServoUnload(uart, duplexer, id):
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


def SerialServoActivateLED(uart, duplexer, id):
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


def SerialServoDeactivateLED(uart, duplexer, id):
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


def SerialServoReceiveHandle(uart, duplexer):
    frameStarted = False
    frameCount = 0
    dataCount = 0
    dataLength = 2
    rxBuf = 0
    recvBuf = bytearray(32)

    while uart.any() > 0:
        rxBuf = uart.read(1)[0]
        # print(hex(rxBuf), end=", ")
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
                    # print("Check SUM OK!!", end="\n\n")
                    frameStarted = False
                    return recvBuf[5:5 + dataLength - 3]

    # print()
    return None


def WaitForReceive(uart, duplexer, id, timeout):
    ms = 1000.0 * timeout + 0.5
    end_ms = ticks_add(ticks_ms(), int(ms))

    while uart.any() == 0:
        remaining_ms = ticks_diff(end_ms, ticks_ms())
        if remaining_ms <= 0:
            raise TimeoutError(f"Serial servo #{id} did not reply within the set time")


def SerialServoReadTemperature(uart, duplexer, id, timeout=1.0):
    duplexer.send_on_data()

    ret = 0

    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_TEMP_READ.length)
    struct.pack_into("<BBBBB", buffer, 0,  # fmt, buffer, offset
                     FRAME_HEADER,
                     FRAME_HEADER,
                     id,
                     SERVO_TEMP_READ.length,
                     SERVO_TEMP_READ.value)
    AppendCheckSum(buffer)

    while uart.any():
        uart.read()

    uart.write(buffer)
    time.sleep_us(500)

    try:
        duplexer.receive_on_data()
        WaitForReceive(uart, duplexer, id, timeout)

        returned_buffer = SerialServoReceiveHandle(uart, duplexer)
        if returned_buffer is not None:
            ret = struct.unpack("<B", returned_buffer)[0]
        else:
            ret = -1
    finally:
        duplexer.send_on_data()

    return ret


def SerialServoReadID(uart, duplexer, id, timeout=1.0):
    duplexer.send_on_data()

    ret = 0

    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_ID_READ.length)
    struct.pack_into("<BBBBB", buffer, 0,  # fmt, buffer, offset
                     FRAME_HEADER,
                     FRAME_HEADER,
                     id,
                     SERVO_ID_READ.length,
                     SERVO_ID_READ.value)
    AppendCheckSum(buffer)

    while uart.any():
        uart.read()

    uart.write(buffer)
    time.sleep_us(500)

    try:
        duplexer.receive_on_data()
        WaitForReceive(uart, duplexer, id, timeout)

        returned_buffer = SerialServoReceiveHandle(uart, duplexer)
        if returned_buffer is not None:
            ret = struct.unpack("<B", returned_buffer)[0]
        else:
            ret = -1
    finally:
        duplexer.send_on_data()

    return ret


def SerialServoReadPosition(uart, duplexer, id, timeout=1.0):
    duplexer.send_on_data()

    ret = 0

    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_POS_READ.length)
    struct.pack_into("<BBBBB", buffer, 0,  # fmt, buffer, offset
                     FRAME_HEADER,
                     FRAME_HEADER,
                     id,
                     SERVO_POS_READ.length,
                     SERVO_POS_READ.value)
    AppendCheckSum(buffer)

    while uart.any():
        uart.read()

    uart.write(buffer)
    time.sleep_us(500)

    try:
        duplexer.receive_on_data()
        WaitForReceive(uart, duplexer, id, timeout)

        returned_buffer = SerialServoReceiveHandle(uart, duplexer)
        if returned_buffer is not None:
            ret = struct.unpack("<H", returned_buffer)[0]
        else:
            ret = -1
    finally:
        duplexer.send_on_data()

    return ret


def SerialServoReadVin(uart, duplexer, id, timeout=1.0):
    duplexer.send_on_data()

    ret = 0

    buffer = bytearray(FRAME_HEADER_LENGTH + SERVO_VIN_READ.length)
    struct.pack_into("<BBBBB", buffer, 0,  # fmt, buffer, offset
                     FRAME_HEADER,
                     FRAME_HEADER,
                     id,
                     SERVO_VIN_READ.length,
                     SERVO_VIN_READ.value)
    AppendCheckSum(buffer)

    while uart.any():
        uart.read()

    uart.write(buffer)
    time.sleep_us(500)

    try:
        duplexer.receive_on_data()
        WaitForReceive(uart, duplexer, id, timeout)

        returned_buffer = SerialServoReceiveHandle(uart, duplexer)
        if returned_buffer is not None:
            ret = struct.unpack("<H", returned_buffer)[0]
        else:
            ret = -2048
    finally:
        duplexer.send_on_data()

    return ret


class LXServo:
    SERVO_MODE = 0
    MOTOR_MODE = 1
    DEFAULT_READ_TIMEOUT = 1.0

    OVER_TEMPERATURE = 0b001
    OVER_VOLTAGE = 0b010
    OVER_LOADED = 0b100

    def __init__(self, id, uart, duplexer, debug_pin=None):
        if id < 0 or id > BROADCAST_ID:
            raise ValueError(f"id out of range. Expected 0 to {BROADCAST_ID}")

        self.__id = id
        self.__uart = uart
        self.__duplexer = duplexer

        self.__debug_pin = debug_pin
        if self.__debug_pin is not None:
            self.__debug_pin.init(Pin.OUT)

        if self.__id == BROADCAST_ID:
            self.__switch_to_servo_mode()
        else:
            logging.info(self.__message_header() + "Searching for servo ... ", end="")

            self.__send(SERVO_ID_READ)
            self.__wait_for_send()
            try:
                self.__receive("B", LXServo.DEFAULT_READ_TIMEOUT)
            except TimeoutError:
                raise RuntimeError(self.__message_header() + "Cannot find servo") from None

            logging.info("found")

            self.__read_mode_and_speed(LXServo.DEFAULT_READ_TIMEOUT)

    def __message_header(self):
        return f"[Servo{self.__id}] "

    @property
    def id(self):
        return self.__id

    @staticmethod
    def detect(id, uart, duplexer, timeout=DEFAULT_READ_TIMEOUT):
        try:
            SerialServoReadID(uart, duplexer, id, timeout)
            return True
        except TimeoutError:
            return False

    def move_to(self, angle, duration):
        if self.__mode != LXServo.SERVO_MODE:
            self.__switch_to_servo_mode()

        position = int(((angle / 90) * 360) + 500)
        position = min(max(position, 0), 1000)

        ms = int(1000.0 * duration + 0.5)
        if ms < 0 or ms > 30000:
            raise ValueError("duration out of range. Expected 0.0s to 30.0s")

        self.__send(SERVO_MOVE_TIME_WRITE, "HH", position, ms)

    def read_move(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_MOVE_TIME_READ)
        self.__wait_for_send()

        received = self.__receive("HH", timeout)
        if received is None:
            return (float("NAN"), float("NAN"))

        angle = ((received[0] - 500) / 360) * 90
        duration = received[1] / 1000.0
        return angle, duration

    def queue_move(self, angle, duration):
        position = int(((angle / 90) * 360) + 500)
        position = min(max(position, 0), 1000)

        ms = int(1000.0 * duration + 0.5)
        if ms < 0 or ms > 30000:
            raise ValueError("duration out of range. Expected 0.0s to 30.0s")

        self.__send(SERVO_MOVE_TIME_WAIT_WRITE, "HH", position, ms)

    # Does not appear to be implemented on the LX-16A
    """
    def read_queued(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_MOVE_TIME_WAIT_READ)
        self.__wait_for_send()

        received = self.__receive("HH", timeout)
        if received is None:
            return (float("NAN"), float("NAN"))

        angle = ((received[0] - 500) / 360) * 90
        duration = received[1] / 1000.0
        return angle, duration
    """

    def start_queued(self):
        if self.__mode != LXServo.SERVO_MODE:
            self.__switch_to_servo_mode()

        self.__send(SERVO_MOVE_START)

    def stop(self):
        if self.__id == BROADCAST_ID:
            self.__send(SERVO_MOVE_STOP)
            self.drive_at(0.0)
        else:
            if self.__mode == LXServo.SERVO_MODE:
                self.__send(SERVO_MOVE_STOP)
            else:
                self.drive_at(0.0)

    def change_id(self, new_id, timeout=DEFAULT_READ_TIMEOUT):
        if self.__id == BROADCAST_ID:
            raise ValueError("cannot change the broadcast address")

        if new_id < 0 or new_id >= BROADCAST_ID:
            raise ValueError(f"id out of range. Expected 0 to {BROADCAST_ID - 1}")

        logging.info(self.__message_header() + f"Changing ID to {new_id} ... ", end="")

        self.__send(SERVO_ID_WRITE, "B", new_id)
        self.__id = new_id

        if self.read_id(timeout) != self.__id:
            raise RuntimeError(self.__message_header() + "Cannot find servo")

        logging.info("success")

    def read_id(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_ID_READ)
        self.__wait_for_send()
        return self.__receive("B", timeout)

    def apply_angle_offset(self, new_offset):
        offset = int((new_offset / 90) * 360)
        offset = min(max(offset, -125), 125)

        self.__send(SERVO_ANGLE_OFFSET_ADJUST, "b", offset)

    def save_angle_offset(self):
        self.__send(SERVO_ANGLE_OFFSET_WRITE)

    def read_angle_offset(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_ANGLE_OFFSET_READ)
        self.__wait_for_send()

        received = self.__receive("b", timeout)
        if received is None:
            return float("NAN")

        return (received / 360) * 90

    def set_angle_limits(self, new_lower_limit, new_upper_limit):
        lower_position = int(((new_lower_limit / 90) * 360) + 500)
        lower_position = max(lower_position, 0)
        upper_position = int(((new_upper_limit / 90) * 360) + 500)
        upper_position = min(max(upper_position, 0), 1000)
        lower_position = min(lower_position, upper_position)

        self.__send(SERVO_ANGLE_LIMIT_WRITE, "HH", lower_position, upper_position)

    def read_angle_limits(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_ANGLE_LIMIT_READ)
        self.__wait_for_send()

        received = self.__receive("HH", timeout)
        if received is None:
            return (float("NAN"), float("NAN"))

        lower_limit = ((received[0] - 500) / 360) * 90
        upper_limit = ((received[1] - 500) / 360) * 90
        return lower_limit, upper_limit

    def set_voltage_limits(self, new_lower_limit, new_upper_limit):
        lower_millivolts = int(new_lower_limit * 1000)
        lower_millivolts = max(lower_millivolts, 4500)
        upper_millivolts = int(new_upper_limit * 1000)
        upper_millivolts = min(max(upper_millivolts, 4500), 14000)  # Servos from factor had 14V set
        lower_millivolts = min(lower_millivolts, upper_millivolts)

        self.__send(SERVO_VIN_LIMIT_WRITE, "HH", lower_millivolts, upper_millivolts)

    def read_voltage_limits(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_VIN_LIMIT_READ)
        self.__wait_for_send()

        received = self.__receive("HH", timeout)
        if received is None:
            return (float("NAN"), float("NAN"))

        lower_limit = received[0] / 1000
        upper_limit = received[1] / 1000
        return lower_limit, upper_limit

    def set_max_temperature_limit(self, new_upper_limit):
        new_upper_limit = min(max(new_upper_limit, 50), 100)
        self.__send(SERVO_TEMP_MAX_LIMIT_WRITE, "B", new_upper_limit)

    def read_max_temperature_limit(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_TEMP_MAX_LIMIT_READ)
        self.__wait_for_send()
        return self.__receive("B", timeout)

    def read_temperature(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_TEMP_READ)
        self.__wait_for_send()
        return self.__receive("B", timeout)

    def read_voltage(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_VIN_READ)
        self.__wait_for_send()

        received = self.__receive("H", timeout)
        if received is None:
            return float("NAN")

        return received / 1000

    def read_angle(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_POS_READ)
        self.__wait_for_send()

        received = self.__receive("h", timeout)  # Angle reports full 360 degree range as signed
        if received is None:
            return float("NAN")

        return ((received - 500) / 360) * 90

    def drive_at(self, speed):
        value = int(speed * 1000)
        value = min(max(value, -1000), 1000)
        self.__send(SERVO_OR_MOTOR_MODE_WRITE, "BBh", LXServo.MOTOR_MODE, 0, value)
        self.__mode = LXServo.MOTOR_MODE

    def __switch_to_motor_mode(self):
        self.__send(SERVO_OR_MOTOR_MODE_WRITE, "BBh", LXServo.MOTOR_MODE, 0, 0)
        self.__mode = LXServo.MOTOR_MODE

    def __switch_to_servo_mode(self):
        self.__send(SERVO_OR_MOTOR_MODE_WRITE, "BBh", LXServo.SERVO_MODE, 0, 0)
        self.__mode = LXServo.SERVO_MODE

    def __read_mode_and_speed(self, timeout):
        self.__send(SERVO_OR_MOTOR_MODE_READ)
        self.__wait_for_send()

        received = self.__receive("BBh", timeout)
        if received is None:
            return (float("NAN"), float("NAN"))

        self.__mode = LXServo.MOTOR_MODE if received[0] == 1 else LXServo.SERVO_MODE
        return self.__mode, received[2] / 1000

    def read_mode(self, timeout=DEFAULT_READ_TIMEOUT):
        return self.__read_mode_and_speed(timeout)[0]

    def read_speed(self, timeout=DEFAULT_READ_TIMEOUT):
        return self.__read_mode_and_speed(timeout)[1]

    def enable(self):
        self.__send(SERVO_LOAD_OR_UNLOAD_WRITE, "B", 1)

    def disable(self):
        self.__send(SERVO_LOAD_OR_UNLOAD_WRITE, "B", 0)

    def is_enabled(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_LOAD_OR_UNLOAD_READ)
        self.__wait_for_send()
        return self.__receive("B", timeout) == 1

    def set_led(self, value):
        self.__send(SERVO_LED_CTRL_WRITE, "B", 0 if value else 1)  # LED state is inverted

    def is_led_on(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_LED_CTRL_READ)
        self.__wait_for_send()
        return self.__receive("B", timeout) == 0  # LED state is inverted

    def configure_faults(self, conditions):
        conditions &= LXServo.OVER_TEMPERATURE | LXServo.OVER_VOLTAGE | LXServo.OVER_LOADED
        self.__send(SERVO_LED_ERROR_WRITE, "B", conditions)

    def read_fault_config(self, timeout=DEFAULT_READ_TIMEOUT):
        self.__send(SERVO_LED_ERROR_READ)
        self.__wait_for_send()
        return self.__receive("B", timeout)

    @staticmethod
    def __checksum(buffer):
        checksum = 0
        length = buffer[FRAME_LENGTH_INDEX]
        last = length + 2
        for i in range(2, last):
            checksum += buffer[i]

        return (~checksum) & 0xFF

    def __send(self, command, fmt="", *data):
        if self.__debug_pin is not None:
            self.__debug_pin.on()

        buffer = bytearray(FRAME_HEADER_LENGTH + command.length)
        struct.pack_into("<BBBBB" + fmt + "B", buffer, 0,  # fmt, buffer, offset
                         FRAME_HEADER,
                         FRAME_HEADER,
                         self.__id,
                         command.length,
                         command.value,
                         *data,
                         0)

        if self.__debug_pin is not None:
            self.__debug_pin.off()

        buffer[-1] = LXServo.__checksum(buffer)

        # Switch to sending data
        self.__duplexer.send_on_data()

        # Clear out the receive buffer since we are now in send mode
        while self.__uart.any():
            self.__uart.read()

        # Write out the previously generated buffer
        self.__uart.write(buffer)

    def __wait_for_send(self):
        # Wait for all the data to be sent to the buffer
        while not self.__uart.txdone():
            pass

        # Wait a short time to let the final bits finish transmitting
        time.sleep_us(1000000 // 115200)

    def __handle_receive(self):
        frameStarted = False
        frameCount = 0
        dataCount = 0
        dataLength = 2
        rxBuf = 0
        recvBuf = bytearray(32)

        while self.__uart.any() > 0:
            if self.__debug_pin is not None:
                self.__debug_pin.on()
            rxBuf = self.__uart.read(1)[0]
            if self.__debug_pin is not None:
                self.__debug_pin.off()
            # print(hex(rxBuf), end=", ")

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
                    if LXServo.__checksum(recvBuf) == recvBuf[dataCount - 1]:
                        # print("Check SUM OK!!", end="\n\n")
                        frameStarted = False
                        return recvBuf[5:5 + dataLength - 3]
            time.sleep_us(100)

        return None

    def __wait_for_receive(self, timeout):
        ms = 1000.0 * timeout + 0.5
        end_ms = ticks_add(ticks_ms(), int(ms))

        while self.__uart.any() == 0:
            remaining_ms = ticks_diff(end_ms, ticks_ms())
            if remaining_ms <= 0:
                self.__duplexer.send_on_data()
                raise TimeoutError(f"Serial servo #{self.__id} did not reply within the set time")

    def __receive(self, fmt="", timeout=DEFAULT_READ_TIMEOUT):
        try:
            self.__duplexer.receive_on_data()
            self.__wait_for_receive(timeout)

            returned_buffer = self.__handle_receive()
            if returned_buffer is not None:
                if len(fmt) == 1:
                    ret = struct.unpack("<" + fmt, returned_buffer)[0]
                else:
                    ret = struct.unpack("<" + fmt, returned_buffer)
            else:
                ret = None
        finally:
            self.__duplexer.send_on_data()

        return ret


class LXServoBroadcaster:

    def __init__(self, uart, duplexer, debug_pin=None):
        self.__servo = LXServo(BROADCAST_ID, uart, duplexer, debug_pin)

    def move_all_to(self, angle, duration):
        self.__servo.move_to(angle, duration)

    def queue_move_all(self, angle, duration):
        self.__servo.queue_move(angle, duration)

    def start_all_queued(self):
        self.__servo.start_queued()

    def stop_all(self):
        self.__servo.stop()

    def apply_all_angle_offsets(self, new_offset):
        self.__servo.apply_angle_offset(new_offset)

    def save_all_angle_offsets(self):
        self.__servo.save_angle_offset()

    def set_all_angle_limits(self, new_lower_limit, new_upper_limit):
        self.__servo.set_angle_limits(new_lower_limit, new_upper_limit)

    def set_all_voltage_limits(self, new_lower_limit, new_upper_limit):
        self.__servo.set_voltage_limits(new_lower_limit, new_upper_limit)

    def set_all_max_temperature_limit(self, new_upper_limit):
        self.__servo.set_max_temperature_limit(new_upper_limit)

    def drive_all_at(self, speed):
        self.__servo.drive_at(speed)

    def enable_all(self):
        self.__servo.enable()

    def disable_all(self):
        self.__servo.disable()

    def set_all_leds(self, value):
        self.__servo.set_led(value)

    def configure_all_faults(self, conditions):
        self.__servo.configure_faults(conditions)
