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

"""
Classes and functions for controlling LewanSoul/HiWonder
LX servos (tested on LX-16A and LX-224HV) via Yukon's
Serial Bus Servo module.
"""


Command = namedtuple("Command", ("value", "length"))

# LX Servo Protocol
FRAME_HEADER = 0x55
FRAME_HEADER_LENGTH = 3
FRAME_LENGTH_INDEX = 3
BAUD_RATE = 115200

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


def checksum(buffer):
    # [From the LX protocol datasheet]
    # The calculation method is as follows:
    #
    # Checksum = ~(ID + Length + Cmd + Prm1 + ... PrmN)
    #
    # If the numbers in the brackets are calculated and exceeded 255,
    # then take the lowest one byte, "~" means negation.
    checksum = 0
    length = buffer[FRAME_LENGTH_INDEX]
    last = length + 2
    for i in range(2, last):
        checksum += buffer[i]

    return (~checksum) & 0xFF


def send(id, uart, duplexer, command, fmt="", *data):
    # Create a buffer of the correct length
    buffer = bytearray(FRAME_HEADER_LENGTH + command.length)

    # Populate the buffer with the required header values and command data
    struct.pack_into("<BBBBB" + fmt + "B", buffer, 0,  # fmt, buffer, offset
                     FRAME_HEADER,
                     FRAME_HEADER,
                     id,
                     command.length,
                     command.value,
                     *data,
                     0)  # where the checksum will go

    # Calculate the checksum and update the last byte of the buffer
    buffer[-1] = checksum(buffer)

    duplexer.send_on_data()    # Switch to sending data

    # Clear out the receive buffer since we are now in send mode
    while uart.any():
        uart.read()

    uart.write(buffer)          # Write out the buffer


def wait_for_send(uart):
    # Wait for all the data to be sent from the buffer
    while not uart.txdone():
        pass

    # Wait a short time to let the final bits finish transmitting
    time.sleep_us(1500000 // BAUD_RATE)


def handle_receive(uart):
    # Variables for handling received bytes
    frame_started = False
    header_count = 0
    data_count = 0
    data_length = 2
    rx_byte = 0
    rx_buffer = bytearray(32)

    while uart.any() > 0:
        rx_byte = uart.read(1)[0]   # Read the next byte
        # print(hex(rx_byte), end=", ")

        # Are we outside of the frame?
        if not frame_started:
            # Only look for header bytes
            if rx_byte == FRAME_HEADER:
                header_count += 1

                # Have to header bytes been received?
                if header_count == 2:
                    header_count = 0
                    frame_started = True
                    data_count = 1
            else:
                frame_started = False
                data_count = 0
                header_count = 0

        # Are we inside the frame?
        if frame_started:
            rx_buffer[data_count] = rx_byte  # Add the byte to the buffer

            # Extract the frame length from the data, exiting if it contradicts
            if data_count == 3:
                data_length = rx_buffer[data_count]
                if data_length < 3 or data_count > 7:
                    data_length = 2
                    frame_started = False

            data_count += 1

            # Have we reached the expected end of the received data?
            if data_count == data_length + 3:
                # Does the checksum we calculate match what was received?
                if checksum(rx_buffer) == rx_buffer[data_count - 1]:
                    # print("Checksum OK!!", end="\n\n")
                    frame_started = False
                    return rx_buffer[5:5 + data_length - 3]

        time.sleep_us(100)  # Sleep enough time for another byte to have been received

    return None


def receive(id, uart, duplexer, timeout, fmt=""):
    wait_for_send(uart)                 # Ensure that all data has been sent
    duplexer.receive_on_data()          # Switch to receive mode

    # Calculate how long to wait for data
    ms = int(1000.0 * timeout + 0.5)
    end_ms = ticks_add(ticks_ms(), ms)

    # Wait for data to start coming in
    while uart.any() == 0:
        remaining_ms = ticks_diff(end_ms, ticks_ms())

        # Has the timeout been reached?
        if remaining_ms <= 0:
            duplexer.send_on_data()     # Switch back to send mode before throwing the error
            raise TimeoutError(f"Serial servo #{id} did not reply within the expected time")

    # Handle the received data
    data_buffer = handle_receive(uart)

    # Was valid data received?
    data = None
    if data_buffer is not None:
        data = struct.unpack("<" + fmt, data_buffer)

        # If there is only one piece of data expected, extract it
        if len(fmt) == 1:
            data = data[0]

    duplexer.send_on_data()             # Switch back to send mode
    return data


class LXServo:
    SERVO_MODE = 0
    MOTOR_MODE = 1
    DEFAULT_READ_TIMEOUT = 1.0

    OVER_TEMPERATURE = 0b001
    OVER_VOLTAGE = 0b010
    OVER_LOADED = 0b100

    BROADCAST_ID = 0xFE

    def __init__(self, id, uart, duplexer, timeout=DEFAULT_READ_TIMEOUT, debug_pin=None):
        if id < 0 or id > self.BROADCAST_ID:
            raise ValueError(f"id out of range. Expected 0 to {self.BROADCAST_ID}")

        if timeout <= 0:
            raise ValueError("timeout out or range. Expected greater than 0")

        self.__id = id
        self.__uart = uart
        self.__duplexer = duplexer
        self.__timeout = timeout

        self.__debug_pin = debug_pin
        if self.__debug_pin is not None:
            self.__debug_pin.init(Pin.OUT)

        if self.__id != self.BROADCAST_ID:
            logging.info(self.__message_header() + "Searching for servo ... ", end="")

            self.verify_id()

            logging.info("found")

            self.__mode = self.__read_mode_and_speed()[0]

    @property
    def id(self):
        return self.__id

    @staticmethod
    def detect(id, uart, duplexer, timeout=DEFAULT_READ_TIMEOUT):
        if id == LXServo.BROADCAST_ID:
            raise ValueError("cannot detect using the broadcast ID")

        send(id, uart, duplexer, SERVO_ID_READ)
        try:
            received = receive(id, uart, duplexer, timeout, "B")
            if received != id:
                raise RuntimeError(f"Serial servo #{id} incorrectly reported its ID as {received}")
            return True
        except TimeoutError:
            return False

    def verify_id(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot verify the ID when broadcasting")

        self.__send(SERVO_ID_READ)
        try:
            received = self.__receive("B")
            if received != self.__id:
                raise RuntimeError(self.__message_header() + f"Incorrectly reported its ID as {received}")
        except TimeoutError:
            raise RuntimeError(self.__message_header() + "Cannot find servo") from None

    def change_id(self, new_id):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot change ID when broadcasting")

        if new_id < 0 or new_id >= self.BROADCAST_ID:
            raise ValueError(f"id out of range. Expected 0 to {self.BROADCAST_ID - 1}")

        logging.info(self.__message_header() + f"Changing ID to {new_id} ... ", end="")

        self.__send(SERVO_ID_WRITE, "B", new_id)
        self.__id = new_id

        self.verify_id()

        logging.info("success")

    # Power Control
    def enable(self):
        self.__send(SERVO_LOAD_OR_UNLOAD_WRITE, "B", 1)

    def disable(self):
        self.__send(SERVO_LOAD_OR_UNLOAD_WRITE, "B", 0)

    def is_enabled(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the enabled state when broadcasting")

        self.__send(SERVO_LOAD_OR_UNLOAD_READ)
        return self.__receive("B") == 1

    # Movement Control
    def mode(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the mode when broadcasting")

        return self.__read_mode_and_speed()[0]

    def move_to(self, angle, duration):
        if self.__id == self.BROADCAST_ID or self.__mode != LXServo.SERVO_MODE:
            self.__switch_to_servo_mode()

        position = int(((angle / 90) * 360) + 500)
        position = min(max(position, 0), 1000)

        ms = int(1000.0 * duration + 0.5)
        if ms < 0 or ms > 30000:
            raise ValueError("duration out of range. Expected 0.0s to 30.0s")

        self.__send(SERVO_MOVE_TIME_WRITE, "HH", position, ms)

    def queue_move(self, angle, duration):
        position = int(((angle / 90) * 360) + 500)
        position = min(max(position, 0), 1000)

        ms = int(1000.0 * duration + 0.5)
        if ms < 0 or ms > 30000:
            raise ValueError("duration out of range. Expected 0.0s to 30.0s")

        self.__send(SERVO_MOVE_TIME_WAIT_WRITE, "HH", position, ms)

    def start_queued(self):
        if self.__id == self.BROADCAST_ID or self.__mode != LXServo.SERVO_MODE:
            self.__switch_to_servo_mode()

        self.__send(SERVO_MOVE_START)

    def drive_at(self, speed):
        value = int(speed * 1000)
        value = min(max(value, -1000), 1000)
        self.__send(SERVO_OR_MOTOR_MODE_WRITE, "BBh", LXServo.MOTOR_MODE, 0, value)

        if self.__id != self.BROADCAST_ID:
            self.__mode = LXServo.MOTOR_MODE

    def last_move(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the last move when broadcasting")

        self.__send(SERVO_MOVE_TIME_READ)
        received = self.__receive("HH")
        if received is None:
            return (float("NAN"), float("NAN"))

        angle = ((received[0] - 500) / 360) * 90
        duration = received[1] / 1000.0
        return angle, duration

    def last_speed(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the last speed when broadcasting")

        return self.__read_mode_and_speed()[1]

    def stop(self):
        if self.__id == self.BROADCAST_ID:
            self.__send(SERVO_MOVE_STOP)
            self.drive_at(0.0)
        else:
            if self.__mode == LXServo.SERVO_MODE:
                self.__send(SERVO_MOVE_STOP)
            else:
                self.drive_at(0.0)

    # LED Control
    def is_led_on(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the LED state when broadcasting")

        self.__send(SERVO_LED_CTRL_READ)
        return self.__receive("B") == 0  # LED state is inverted

    def set_led(self, value):
        self.__send(SERVO_LED_CTRL_WRITE, "B", 0 if value else 1)  # LED state is inverted

    # Sensing
    def read_angle(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the angle when broadcasting")

        self.__send(SERVO_POS_READ)
        received = self.__receive("h")  # Angle reports full 360 degree range as signed
        if received is None:
            return float("NAN")

        return ((received - 500) / 360) * 90

    def read_voltage(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the voltage when broadcasting")

        self.__send(SERVO_VIN_READ)
        received = self.__receive("H")
        if received is None:
            return float("NAN")

        return received / 1000

    def read_temperature(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the temperature when broadcasting")

        self.__send(SERVO_TEMP_READ)
        return self.__receive("B")

    # Angle Settings
    def angle_offset(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the angle offset when broadcasting")

        self.__send(SERVO_ANGLE_OFFSET_READ)
        received = self.__receive("b")
        if received is None:
            return float("NAN")

        return (received / 360) * 90

    def try_angle_offset(self, offset):
        int_offset = int((offset / 90) * 360)
        int_offset = min(max(int_offset, -125), 125)

        self.__send(SERVO_ANGLE_OFFSET_ADJUST, "b", int_offset)

    def save_angle_offset(self):
        self.__send(SERVO_ANGLE_OFFSET_WRITE)

    # Limit Settings
    def angle_limits(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the angle limits when broadcasting")

        self.__send(SERVO_ANGLE_LIMIT_READ)
        received = self.__receive("HH")
        if received is None:
            return (float("NAN"), float("NAN"))

        lower_limit = ((received[0] - 500) / 360) * 90
        upper_limit = ((received[1] - 500) / 360) * 90
        return lower_limit, upper_limit

    def voltage_limits(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the voltage limits when broadcasting")

        self.__send(SERVO_VIN_LIMIT_READ)
        received = self.__receive("HH")
        if received is None:
            return (float("NAN"), float("NAN"))

        lower_limit = received[0] / 1000
        upper_limit = received[1] / 1000
        return lower_limit, upper_limit

    def temperature_limit(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the temperature limit when broadcasting")

        self.__send(SERVO_TEMP_MAX_LIMIT_READ)
        return self.__receive("B")

    def set_angle_limits(self, lower, upper):
        lower_pos = int(((lower / 90) * 360) + 500)
        lower_pos = max(lower_pos, 0)
        upper_pos = int(((upper / 90) * 360) + 500)
        upper_pos = min(max(upper_pos, 0), 1000)
        lower_pos = min(lower_pos, upper_pos)

        self.__send(SERVO_ANGLE_LIMIT_WRITE, "HH", lower_pos, upper_pos)

    def set_voltage_limits(self, lower, upper):
        lower_mv = int(lower * 1000)
        lower_mv = max(lower_mv, 4500)
        upper_mv = int(upper * 1000)
        upper_mv = min(max(upper_mv, 4500), 14000)  # Servos from factor had 14V set
        lower_mv = min(lower_mv, upper_mv)

        self.__send(SERVO_VIN_LIMIT_WRITE, "HH", lower_mv, upper_mv)

    def set_temperature_limit(self, limit):
        limit = min(max(limit, 50), 100)
        self.__send(SERVO_TEMP_MAX_LIMIT_WRITE, "B", limit)

    # Fault Settings
    def fault_config(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the fault configuration when broadcasting")

        self.__send(SERVO_LED_ERROR_READ)
        return self.__receive("B")

    def configure_faults(self, conditions):
        conditions &= LXServo.OVER_TEMPERATURE | LXServo.OVER_VOLTAGE | LXServo.OVER_LOADED
        self.__send(SERVO_LED_ERROR_WRITE, "B", conditions)

    def __switch_to_servo_mode(self):
        self.__send(SERVO_OR_MOTOR_MODE_WRITE, "BBh", LXServo.SERVO_MODE, 0, 0)

        if self.__id != self.BROADCAST_ID:
            self.__mode = LXServo.SERVO_MODE

    def __read_mode_and_speed(self):
        self.__send(SERVO_OR_MOTOR_MODE_READ)
        received = self.__receive("BBh")
        if received is None:
            return (float("NAN"), float("NAN"))

        mode = LXServo.MOTOR_MODE if received[0] == 1 else LXServo.SERVO_MODE
        return mode, received[2] / 1000

    def __send(self, command, fmt="", *data):
        send(self.__id, self.__uart, self.__duplexer, command, fmt, *data)

    def __receive(self, fmt=""):
        return receive(self.__id, self.__uart, self.__duplexer, self.__timeout, fmt)

    def __message_header(self):
        return f"[Servo{self.__id}] "


class LXServoBroadcaster:

    def __init__(self, uart, duplexer, timeout=LXServo.DEFAULT_READ_TIMEOUT, debug_pin=None):
        self.__servo = LXServo(LXServo.BROADCAST_ID, uart, duplexer, timeout, debug_pin)

    # Power Control
    def enable_all(self):
        self.__servo.enable()

    def disable_all(self):
        self.__servo.disable()

    # Movement Control
    def move_all_to(self, angle, duration):
        self.__servo.move_to(angle, duration)

    def queue_move_all(self, angle, duration):
        self.__servo.queue_move(angle, duration)

    def start_all_queued(self):
        self.__servo.start_queued()

    def drive_all_at(self, speed):
        self.__servo.drive_at(speed)

    def stop_all(self):
        self.__servo.stop()

    # LED Control
    def set_all_leds(self, value):
        self.__servo.set_led(value)

    # Angle Settings
    def try_all_angle_offsets(self, offset):
        self.__servo.try_angle_offset(offset)

    def save_all_angle_offsets(self):
        self.__servo.save_angle_offset()

    # Limit Settings
    def set_all_angle_limits(self, lower, upper):
        self.__servo.set_angle_limits(lower, upper)

    def set_all_voltage_limits(self, lower, upper):
        self.__servo.set_voltage_limits(lower, upper)

    def set_all_temperature_limits(self, upper):
        self.__servo.set_temperature_limit(upper)

    # Fault Settings
    def configure_all_faults(self, conditions):
        self.__servo.configure_faults(conditions)
