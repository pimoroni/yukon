# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from pimoroni_yukon.timing import ticks_diff, ticks_ms


"""
JoyBTCommander is a class for communicating with an Android-based
bluetooth serial controller app of the same name. This app provides
a virtual joystick and up to 6 buttons on a smart phone's touch screen.

This Micropython implementation is a port of an Arduino implmentation
originally created by Christopher "ZodiusInfuser" Parrott, found at:
https://github.com/ZodiusInfuser/JoyBTCommander
"""


class JoyBTCommander():
    STX = 0x02
    ETX = 0x03
    BUFFER_SIZE = 6
    BUTTON_COUNT = 6
    DEFAULT_COMMS_TIMEOUT = 1.0

    def __init__(self, uart, no_comms_timeout=DEFAULT_COMMS_TIMEOUT):
        self.__uart = uart
        self.__no_comms_timeout_ms = int(no_comms_timeout * 1000)
        self.__no_comms_timeout_callback = None
        self.__last_received_ms = 0
        self.__timeout_reached = True       # Set as true initially so the timeout callback does not get called immediately

        self.__receiving = False
        self.__data_index = 0
        self.__in_buffer = bytearray(self.BUFFER_SIZE)

        self.__button_state = [False] * self.BUTTON_COUNT
        self.__momentary_button = [False] * self.BUTTON_COUNT
        self.__button_pressed_callback = [None] * self.BUTTON_COUNT
        self.__button_released_callback = [None] * self.BUTTON_COUNT

        self.__joystick_x = 0.0
        self.__joystick_y = 0.0
        self.__joystick_callback = None

        # Clear the receive buffer
        while self.__uart.any() > 0:
            self.__uart.read()

    def is_connected(self):
        return not self.__timeout_reached

    def check_receive(self):
        while self.__uart.any() > 0:
            rx_byte = self.__uart.read(1)[0]
            if not self.__receiving:
                if rx_byte == self.STX:
                    self.__receiving = True
                    self.__data_index = 0
            else:
                if rx_byte > 127 or self.__data_index > self.BUFFER_SIZE:
                    self.__receiving = False
                elif rx_byte == self.ETX:
                    if self.__data_index == 1:
                        self.__decode_button_state(self.__in_buffer[0])    # 3 Bytes  ex: < STX "C" ETX >
                    elif self.__data_index == 6:
                        self.__decode_joystick_state(self.__in_buffer)     # 6 Bytes  ex: < STX "200" "180" ETX >
                    self.__last_received_ms = ticks_ms()
                    self.__timeout_reached = False

                    self.__receiving = False
                else:
                    self.__in_buffer[self.__data_index] = rx_byte
                    self.__data_index += 1

        current_millis = ticks_ms()
        if (ticks_diff(current_millis, self.__last_received_ms) > self.__no_comms_timeout_ms) and not self.__timeout_reached:
            if self.__no_comms_timeout_callback is not None:
                self.__no_comms_timeout_callback()

            self.__timeout_reached = True

    def send_fields(self, data_field1="XXX", data_field2="XXX", data_field3="XXX"):
        # Data frame transmitted back from Micropython to Android device:
        # < 0X02   Buttons state   0X01   DataField#1   0x04   DataField#2   0x05   DataField#3    0x03 >
        # < 0X02      "01011"      0X01     "120.00"    0x04     "-4500"     0x05  "Motor enabled" 0x03 >    // example

        self.__uart.write(self.STX)                         # Start transmission
        self.__uart.write(self.__button_states_to_string())   # Button state feedback
        self.__uart.write(0x1)
        self.__uart.write(str(data_field1))                 # Data Field #1
        self.__uart.write(0x4)
        self.__uart.write(str(data_field2))                 # Data Field #2
        self.__uart.write(0x5)
        self.__uart.write(str(data_field3))                 # Data Field #3
        self.__uart.write(self.ETX)                         # End transmission

    def is_button_pressed(self, button):
        if button < 0 or button >= self.BUTTON_COUNT:
            raise ValueError(f"button out of range. Expected 0 to {self.BUTTON_COUNT - 1}")

        return self.__button_state[button]

    def set_button_pressed(self, button, pressed):
        if button < 0 or button >= self.BUTTON_COUNT:
            raise ValueError(f"button out of range. Expected 0 to {self.BUTTON_COUNT - 1}")

        if pressed:
            self.__handle_button_press(button)
        else:
            self.__handle_button_release(button)

    def is_momentary_button(self, button):
        if button < 0 or button >= self.BUTTON_COUNT:
            raise ValueError(f"button out of range. Expected 0 to {self.BUTTON_COUNT - 1}")

        return self.__momentary_button[button]

    def set_button_as_momentary(self, button, momentary):
        if button < 0 or button >= self.BUTTON_COUNT:
            raise ValueError(f"button out of range. Expected 0 to {self.BUTTON_COUNT - 1}")

        self.__momentary_button[button] = momentary

    @property
    def joystick_x(self):
        return self.__joystick_x

    @property
    def joystick_y(self):
        return self.__joystick_y

    def set_button_pressed_callback(self, button, button_callback):
        if button < 0 or button >= self.BUTTON_COUNT:
            raise ValueError(f"button out of range. Expected 0 to {self.BUTTON_COUNT - 1}")

        self.__button_pressed_callback[button] = button_callback

    def set_button_released_callback(self, button, button_callback):
        if button < 0 or button >= self.BUTTON_COUNT:
            raise ValueError(f"button out of range. Expected 0 to {self.BUTTON_COUNT - 1}")

        self.__button_released_callback[button] = button_callback

    def set_timeout_callback(self, timeout_callback):
        self.__no_comms_timeout_callback = timeout_callback

    def set_joystick_callback(self, joystick_callback):
        self.__joystick_callback = joystick_callback

    def __decode_button_state(self, data):
        # -----------------  BUTTON #1  -----------------------
        if data == ord('A'):
            self.__handle_button_press(0)
        elif data == ord('B'):
            self.__handle_button_release(0)

        # -----------------  BUTTON #2  -----------------------
        elif data == ord('C'):
            self.__handle_button_press(1)
        elif data == ord('D'):
            self.__handle_button_release(1)

        # -----------------  BUTTON #3  -----------------------
        elif data == ord('E'):
            self.__handle_button_press(2)
        elif data == ord('F'):
            self.__handle_button_release(2)

        # -----------------  BUTTON #4  -----------------------
        elif data == ord('G'):
            self.__handle_button_press(3)
        elif data == ord('H'):
            self.__handle_button_release(3)

        # -----------------  BUTTON #5  -----------------------
        elif data == ord('I'):
            self.__handle_button_press(4)
        elif data == ord('J'):
            self.__handle_button_release(4)

        # -----------------  BUTTON #6  -----------------------
        elif data == ord('K'):
            self.__handle_button_press(5)
        elif data == ord('L'):
            self.__handle_button_release(5)

    def __decode_joystick_state(self, rx_byte):
        # Obtain the int from the ASCII representation
        joy_x = (rx_byte[0] - 48) * 100 + (rx_byte[1] - 48) * 10 + (rx_byte[2] - 48)
        joy_y = (rx_byte[3] - 48) * 100 + (rx_byte[4] - 48) * 10 + (rx_byte[5] - 48)

        # Offset to avoid transmitting negative numbers
        joy_x = joy_x - 200
        joy_y = joy_y - 200

        if joy_x < -100 or joy_x > 100 or joy_y < -100 or joy_y > 100:
            return      # Invalid data, so just ignore it

        self.__joystick_x = float(joy_x) / 100.0
        self.__joystick_y = float(joy_y) / 100.0

        if self.__joystick_callback is not None:
            self.__joystick_callback(self.__joystick_x, self.__joystick_y)

    def __handle_button_press(self, button):
        if not self.__momentary_button[button]:     # Only set the button state to pressed if the button is not momentary
            self.__button_state = True

        if self.__button_pressed_callback[button] is not None:
            self.__button_pressed_callback[button]()

    def __handle_button_release(self, button):
        self.__button_state = False

        if self.__button_released_callback[button] is not None:
            self.__button_released_callback[button]()

    def __button_states_to_string(self):
        state = ""
        for i in range(0, len(self.__button_state)):
            if self.__button_state[i] is True:
                state += "1"
            else:
                state += "0"
        return state
