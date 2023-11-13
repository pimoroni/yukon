# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

from pimoroni_yukon.timing import ticks_diff, ticks_ms

class JoyBTCommander():
    STX = 0x02
    ETX = 0x03
    BUFFER_SIZE = 6
    BUTTON_COUNT = 6
    DEFAULT_COMMS_TIMEOUT = 1.0

    def __init__(self, uart, timeout=DEFAULT_COMMS_TIMEOUT):
        self.__uart = uart
        self.__no_comms_timeout = int(timeout * 1000)
        self.__no_comms_timeout_callback = None
        self.__last_received_millis = 0
        self.__timeout_reached = True

        self.__receiving = False
        self.__data_index = 0
        self.__in_buffer = bytearray(self.BUFFER_SIZE)

        self.__button_state = [False, False, False, False, False, False]

        self.__joystick_x = 0.0
        self.__joystick_y = 0.0
        self.__joystick_callback = None

    @property
    def joystick(self):
        return self.__joystick_x, self.__joystick_y

    def begin(self):
        # Clear the buffer
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
                        self.decode_button_state(self.__in_buffer[0])    # 3 Bytes  ex: < STX "C" ETX >
                    elif self.__data_index == 6:
                        self.decode_joystick_state(self.__in_buffer)     # 6 Bytes  ex: < STX "200" "180" ETX >
                    self.__last_received_millis = ticks_ms()
                    self.__timeout_reached = False

                    self.__receiving = False
                else:
                    self.__in_buffer[self.__data_index] = rx_byte
                    self.__data_index += 1

        current_millis = ticks_ms()
        if (ticks_diff(current_millis, self.__last_received_millis) > self.__no_comms_timeout) and not self.__timeout_reached:
            print("here")
            if self.__no_comms_timeout_callback != None:
                self.__no_comms_timeout_callback()

            self.__timeout_reached = True

    def button_state(self, button):
        return self.__button_state[button]

    def set_button_state(self, button, pressed):
        if pressed:
            self.handle_button_press(button)
        else:
            self.handle_button_release(button)

    def set_timeout_callback(self, timeout_callback):
        self.__no_comms_timeout_callback = timeout_callback

    def set_joystick_callback(self, joystick_callback):
        self.__joystick_callback = joystick_callback

    def decode_button_state(self, data):
        # -----------------  BUTTON #1  -----------------------
        if data == ord('A'):
            self.handle_button_press(0)
        elif data == ord('B'):
            self.handle_button_release(0)

        # -----------------  BUTTON #2  -----------------------
        elif data == ord('C'):
            self.handle_button_press(1)
        elif data == ord('D'):
            self.handle_button_release(1)

        # -----------------  BUTTON #3  -----------------------
        elif data == ord('E'):
            self.handle_button_press(2)
        elif data == ord('F'):
            self.handle_button_release(2)

        # -----------------  BUTTON #4  -----------------------
        elif data == ord('G'):
            self.handle_button_press(3)
        elif data == ord('H'):
            self.handle_button_release(3)

        # -----------------  BUTTON #5  -----------------------
        elif data == ord('I'):
            self.handle_button_press(4)
        elif data == ord('J'):
            self.handle_button_release(4)

        # -----------------  BUTTON #6  -----------------------
        elif data == ord('K'):
            self.handle_button_press(5)
        elif data == ord('L'):
            self.handle_button_release(5)
    
    def decode_joystick_state(self, rx_byte):
        joy_x = (rx_byte[0] - 48) * 100 + (rx_byte[1] - 48) * 10 + (rx_byte[2] - 48)       # obtain the Int from the ASCII representation
        joy_y = (rx_byte[3] - 48) * 100 + (rx_byte[4] - 48) * 10 + (rx_byte[5] - 48)
        joy_x = joy_x - 200;                                                  # Offset to avoid
        joy_y = joy_y - 200;                                                  # transmitting negative numbers

        if joy_x < -100 or joy_x > 100 or joy_y < -100 or joy_y > 100:
            return      # commmunication error

        self.__joystick_x = float(joy_x) / 100.0
        self.__joystick_y = float(joy_y) / 100.0

        if self.__joystick_callback != None:
            self.__joystick_callback(self.__joystick_x, self.__joystick_y)

    def handle_button_press(self, button):
        self.__button_state[button] = True

    def handle_button_release(self, button):
        self.__button_state[button] = False

    def button_states_to_string(self):
        state = ""
        for i in range(0, len(self.__button_state)):
            if self.__button_state[i]:
                state += "1"
            else:
                state += "0"
        return state
