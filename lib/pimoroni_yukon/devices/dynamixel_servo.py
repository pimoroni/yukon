import time
import struct
from machine import Pin
from pimoroni_yukon.timing import ticks_add, ticks_diff, ticks_ms
from pimoroni_yukon.errors import TimeoutError
import pimoroni_yukon.logging as logging

"""
Classes and functions for controlling Dynamixel
AX servos (tested on AX-12W) via Yukon's
Serial Bus Servo module.
"""
BAUD_RATE = 1000000

def wait_for_send(uart):
    # As of MicroPython 1.24 txdone now waits for all data to be transmitted:
    # https://github.com/micropython/micropython/commit/97af1001ae07c573bf432b9923dcdf78055a508c

    # Wait for all the data to be sent from the buffer.
    while not uart.txdone():
        pass
    
def calculate_checksum(id, length, instruction, parameters):
    # For the AX-12W (and other Dynamixel AX-series servos using Protocol 1.0),
    # the checksum is calculated by taking the sum of several packet components
    # and applying a bitwise NOT (ones' complement).
    s = (id + length + instruction + sum(parameters)) & 0xFF
    return (~s) & 0xFF  # Bitwise NOT

def receive_packet(uart, expected_id, duplexer, timeout_ms, check_id=True):
    wait_for_send(uart)                 # Ensure that all data has been sent
    duplexer.receive_on_data()          # Switch to receive mode

    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        if uart.any() >= 6:
            # Look for header 0xFF, 0xFF
            header = uart.read(2)
            if header == b'\xff\xff':
                # Read ID, Length, Error
                status_info = uart.read(3)
                if not status_info: return None
                
                res_id, res_len, res_err = status_info
                # Read parameters (if any) and Checksum
                # Total length in packet includes Error + Params + Checksum
                data = uart.read(res_len) 
                
                # Check for ID match and basic integrity
                if check_id == False or res_id == expected_id:
                    duplexer.send_on_data()             # Switch back to send mode
                    return {"id": res_id, "error": res_err, "params": list(data[:-1])}

    duplexer.send_on_data()             # Switch back to send mode
    raise TimeoutError(f"Serial servo #{id} did not reply within the expected time")

def send_packet(uart, id, duplexer, instruction, parameters=None):
    if parameters is None:
        parameters = []
    
    length = len(parameters) + 2  # Instruction + Parameters + Checksum (1 byte not in length)
    chk = calculate_checksum(id, length, instruction, parameters)
    
    # Packet: [0xFF, 0xFF, ID, Length, Instruction, Param1, ..., Checksum]
    packet = bytearray([0xFF, 0xFF, id, length, instruction])
    packet.extend(parameters)
    packet.append(chk)
    
    duplexer.send_on_data()    # Switch to sending data

    # Clear buffer and send
    while uart.any(): uart.read()
    
    uart.write(packet)

def __degrees_to_raw(degree):
    # Round input to the nearest 0.5 (e.g., 150.2 -> 150.0, 150.3 -> 150.5)
    target_degree = round(degree * 2) / 2
    
    position = int(round(((target_degree + 150.0) / 300.0) * 1023))
    # Map to 0-1023 range
    position = min(max(position, 0), 1023)
    return position

def __raw_to_degrees(raw):
    # Convert raw back to float
    calc_degree = ((raw * 300.0) / 1023.0) - 150.0
    
    # Round the result to the nearest 0.5 to restore symmetry
    return round(calc_degree * 2) / 2

def __speed_to_raw(speed):
    # Round input to the nearest 0.005 (e.g., 0.152 -> 0.150, 0.153 -> 0.155)
    target_speed = round(abs(speed) * 2) / 2
    if speed >= 0:
        raw_speed = int(target_speed * 1023)
        # Map to 0-1023 range
        raw_speed = min(max(raw_speed, 0), 1023)
    else:
        raw_speed = int(target_speed * 1023) + 1024
        # Map to 1024-2047 range
        raw_speed = min(max(raw_speed, 1024), 2047)
    
    return raw_speed

def __raw_to_speed(raw):
    # Convert raw back to float
    if (raw < 1024):
        calc_speed = raw / 1023.0
        calc_speed = round(calc_speed * 2) / 2
        return calc_speed
    else:
        calc_speed = (raw-1024) / 1023.0 
        calc_speed = round(calc_speed * 2) / 2
        return -calc_speed
    
class AXServo:
    SERVO_MODE = 0
    MOTOR_MODE = 1
    # Default switch from Read->Write for the servos is 500 micro-seconds, so add some
    # headroom for send and receive and mode switches from SERVO<->MOTOR. 
    DEFAULT_READ_TIMEOUT = 50.0

    # Instructions for AX Servos
    INST_PING = 0x01
    INST_READ = 0x02
    INST_WRITE = 0x03
    INST_REG_WRITE = 0x04
    INST_ACTION = 0x05
    
    # Registers for AX Servos
    REG_ID = 0x03
    TORQUE_ENABLE = 0x18
    LED = 0x19
    CW_ANGLE_LIMIT = 0x06
    CCW_ANGLE_LIMIT = 0x08
    TEMP_LIMIT = 0x0B
    DOWN_LIMIT_VOLTAGE = 0x0C
    UP_LIMIT_VOLTAGE = 0x0D
    ADDR_ALARM_LED = 0x11
    ADDR_ALARM_SHUTDOWN = 0x12
    GOAL_POS = 0x1E
    GOAL_SPEED = 0x20
    TORQUE_LIMIT = 0x22
    PUNCH = 0x30
    BROADCAST_ID = 0xFE
    ADDR_PRESENT_POS = 0x24
    ADDR_PRESENT_VOLT = 0x2A
    ADDR_PRESENT_TEMP = 0x2B
    

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
            logging.info(f"> Searching for Serial Servo #{self.__id} ... ", end="")

            self.verify_id()

            logging.info("found")

            response = self.angle_limits()
            self.__mode = AXServo.MOTOR_MODE if response[0] == -150.0 and response[1] == -150.0 else AXServo.SERVO_MODE

    @property
    def id(self):
        return self.__id

    @staticmethod
    def detect(id, uart, duplexer, timeout=DEFAULT_READ_TIMEOUT):
        """
        determine whether a servo with a given id is connected
        
        :id: the servo ID to try and detect
        :uart: the uart connection for the serial servo module
        :duplexer: the switch between send and receive on the uart
        :return: True if a servo with the given id is detected, False otherwise. 
        """
        if id == AXServo.BROADCAST_ID:
            raise ValueError("cannot detect using the broadcast ID")
        
        send_packet(uart, id, duplexer, AXServo.INST_PING)
    
        try:
            received = receive_packet(uart, None, duplexer, timeout, check_id=False)
            if received['id'] != id:
                raise RuntimeError(f"Serial Servo #{id} incorrectly reported its ID as {received}")
            return True
        except TimeoutError:
            return False

    def verify_id(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot verify the ID when broadcasting")

        # Send Ping: there are no parameters.
        self.__send(self.INST_PING)
        try:
            # Wait for a Status Packet response
            # A successful response confirms the servo is online.
            received = self.__receive(check_id=False)['id']
            if received != self.__id:
                raise RuntimeError(self.__message_header() + f"Incorrectly reported its ID as {received}")
        except TimeoutError:
            raise RuntimeError(self.__message_header() + "Cannot find servo") from None
        
    def change_id(self, new_id):
        """
        change the id of a servo to new_id
        
        :new_id: the id to set
        """
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot change ID when broadcasting")

        if new_id < 0 or new_id >= self.BROADCAST_ID:
            raise ValueError(f"id out of range. Expected 0 to {self.BROADCAST_ID - 1}")

        logging.info(self.__message_header() + f"Changing ID to {new_id} ... ", end="")

        params = [self.REG_ID, new_id]
        self.__send(INST_WRITE, params)
        
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

        self.__id = new_id

        self.verify_id()

        logging.info("success")

    # Power Control
    def enable(self):
        self.__send(self.INST_WRITE, [self.TORQUE_ENABLE, 1])
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

    def disable(self):
        self.__send(self.INST_WRITE, [self.TORQUE_ENABLE, 0])
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

    def is_enabled(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the enabled state when broadcasting")

        self.__send(self.INST_READ, [self.TORQUE_ENABLE, 1])
        response = self.__receive()
        return response['params'][0]


    # Movement Control
    def mode(self):
        """
        reports whether the servo is in SERVO mode or MOTOR mode.
        
        :return: whether the servo is in AXServo.SERVO_MODE or AXServo.MOTOR_MODE
        """
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the mode when broadcasting")

        response = self.angle_limits()
        return AXServo.MOTOR_MODE if response[0] == -150.0 and response[1] == -150.0 else AXServo.SERVO_MODE

    def __move_to(self, angle, deg_per_sec, queued):
        # The register accepts integers from 1 to 1023.
        # Each unit change results in a speed difference
        # of about 0.666 deg/s

        raw_speed = int(deg_per_sec / 0.666)
        raw_speed = max(0, min(1023, raw_speed)) # Clamp 1-1023 (0 is max speed)
        
        angle = max(min(angle, 150.0), -150.0)
        raw_goal = __degrees_to_raw(angle)
    
        params = [
            self.GOAL_POS, 
            raw_goal & 0xFF, (raw_goal >> 8) & 0xFF,
            raw_speed & 0xFF, (raw_speed >> 8) & 0xFF
        ]
        speed_params = [self.GOAL_SPEED, raw_speed & 0xFF, (raw_speed >> 8) & 0xFF]
        if queued:
            self.__send(self.INST_REG_WRITE, params)
        else:            
            self.__send(self.INST_WRITE, params)
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())
        if queued:    
            logging.debug(self.__message_header() + f"Queued move to {((raw_goal / 1023.0) * 300) - 150}° at {raw_speed * 0.666} °/s")
        else:
            logging.debug(self.__message_header() + f"Moving to {((raw_goal / 1023.0) * 300) - 150}° at {raw_speed * 0.666} °/s")

    def move_to(self, angle, deg_per_sec):
        """
        moves the servo to a particular angle at a given speed, will switch to AXServo.SERVO_MODE
        if currently in AXServo.MOTOR_MODE.
        
        :angle: the angle to move to in degress, between -300 and 300 unless other angle limits have been set
        :deg_per_sec: the speed to move at in degrees per second. Specific 0 to move at hardware limits.
            
        """
        if self.__id == self.BROADCAST_ID or self.__mode != AXServo.SERVO_MODE:
            self.__switch_to_servo_mode()

        self.__move_to(angle, deg_per_sec, False)

    def queue_move(self, angle, deg_per_sec):
        """
        queues a move for the servo to a particular angle at a given speed.
        
        :angle: the angle to move to in degress, between -300 and 300 unless other angle limits have been set
        :deg_per_sec: the speed to move at in degrees per second. Specific 0 to move at hardware limits. 
        """
        self.__move_to(angle, deg_per_sec, True)

    def start_queued(self):
        """
        starts a previous queued servo move.
        """
        if self.__id == self.BROADCAST_ID or self.__mode != AXServo.SERVO_MODE:
            self.__switch_to_servo_mode()

        self.__send(self.INST_ACTION, [])
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

    def drive_at(self, speed):
        """
        make the servo drive forwards or backwards in MOTOR mode.
        
        :speed: forward or backwards speed between -1.0 (CCW) to 1.0 (CW)
        """        
        if self.__id == self.BROADCAST_ID or self.__mode == AXServo.SERVO_MODE:
            self.__switch_to_motor_mode()

        raw_speed = __speed_to_raw(speed)

        params = [self.GOAL_SPEED, raw_speed & 0xFF, (raw_speed >> 8) & 0xFF]
        self.__send(self.INST_WRITE, params)
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

        if raw_speed == 0:
            logging.info(self.__message_header() + "Stop driving")
        else:
            logging.info(self.__message_header() + f"Driving at {(raw_speed / 1023)}")

    def last_move(self):
        """
        report the last position and speed that the servo was asked to move to
        
        :return: the angle and degrees and speed in deg/sec that the servo was asked to move to
        """
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the last move when broadcasting")

        self.__send(self.INST_READ, [self.GOAL_POS, 4])
        response = self.__receive()
        p = response['params']
        raw_pos = p[0] + (p[1] << 8)
        raw_speed = p[2] + (p[3] << 8)

        angle = round(((raw_pos / 1023.0) * 300) - 150, 1)
        deg_per_sec = raw_speed * 0.666
        
        return angle, deg_per_sec

    def last_speed(self):
        """
        report the last speed that the servo was asked to move at
        
        :return: the last speed that the servo was asked to move
        at as a percentage between -1.0 and 1.0
        """
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the last speed when broadcasting")

        self.__send(self.INST_READ, [self.GOAL_SPEED, 2])
        response = self.__receive()
        p = response['params']
        raw_speed = p[0] + (p[1] << 8)
        
        return __raw_to_speed(raw_speed)

    def stop(self):
        if self.__id == self.BROADCAST_ID:
            # There is no neat way to do this via broadcast with the Dynamixel protocol
            raise ValueError("cannot stop all when broadcasting")
        else:
            if self.__mode == AXServo.SERVO_MODE:
                # Make the target position be the current position
                self.move_to(self.read_angle(), 0)
                logging.info(self.__message_header() + "Stop moving")
            else:
                # Stop the wheels from moving
                self.drive_at(0.0)

    # LED Control
    def is_led_on(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the LED state when broadcasting")

        self.__send(self.INST_READ, [self.LED, 1])
        response = self.__receive()
        return response['params'][0]

    def set_led(self, value):
        self.__send(self.INST_WRITE, [self.LED, value])
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

    # Sensing
    def read_angle(self):
        """
        read the current angle of the servo
        
        :return: The current servo angle between -150 and 150 degrees
        """
        pos = self.__read_angle_raw()
        degrees = __raw_to_degrees(pos)
        return degrees
    
    def __read_angle_raw(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the temperature when broadcasting")

        self.__send(self.INST_READ, [self.ADDR_PRESENT_POS, 2])
        response = self.__receive()
        p = response['params']
        pos = p[0] + (p[1] << 8)
        return pos
    
    def read_voltage(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the voltage when broadcasting")

        self.__send(self.INST_READ, [self.ADDR_PRESENT_VOLT, 1])
        response = self.__receive()
        return response['params'][0] / 10.0

    def torque_limit(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the torque when broadcasting")

        self.__send(self.INST_READ, [self.TORQUE_LIMIT, 2])
        response = self.__receive()
        p = response['params']
        # Combine bytes (Little-Endian)
        torque_limit = p[0] + (p[1] << 8)
        return torque_limit

    def punch(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the punch when broadcasting")

        self.__send(self.INST_READ, [self.PUNCH, 2])
        response = self.__receive()
        p = response['params']
        # Combine bytes (Little-Endian)
        punch = p[0] + (p[1] << 8)
        return punch
    
    def read_temperature(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the temperature when broadcasting")

        self.__send(self.INST_READ, [self.ADDR_PRESENT_TEMP, 1])
        response = self.__receive()
        return response['params'][0]

    # Limit Settings
    def angle_limits(self):
        """
        returns the angle limits in degrees between -150.0 and 150.0. If in motor mode
        then both upper (clockwise) and lower (counter clockwise) limits will be -150.0.
        
        :return: the lower (counter clockwise) and upper (clockwise) limits as degrees
        between -150.0 and 150.0. If the servo is in AXServo.MOTOR_MODE then the angle_limits
        will be (-150.0, -150.0)
        """
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the angle limits when broadcasting")

        self.__send(self.INST_READ, [self.CW_ANGLE_LIMIT, 4])
        response = self.__receive()
        
        p = response['params']
        # Combine bytes (Little-Endian)
        ccw_raw = p[0] + (p[1] << 8)
        cw_raw = p[2] + (p[3] << 8)
        
        # Convert to degrees
        cw_deg = __raw_to_degrees(cw_raw)
        ccw_deg = __raw_to_degrees(ccw_raw)
  
        return ccw_deg, cw_deg

    def voltage_limits(self):
        """
        the upper and lower voltage limits that the servo is configured to work within
        
        :return: the lower and upper voltage limits (in Volts)
        """
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the voltage limits when broadcasting")

        self.__send(self.INST_READ, [self.DOWN_LIMIT_VOLTAGE, 2])
        response = self.__receive()

        low_v = response['params'][0] / 10.0
        high_v = response['params'][1] / 10.0
        return low_v, high_v

    def temperature_limit(self):
        """
        the upper temperature limit that the servo is configured to function within
        
        :return: the upper temperature limit in degress centigrade.
        """
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the temperature limit when broadcasting")

        self.__send(self.INST_READ, [self.TEMP_LIMIT, 1])
        response = self.__receive()
        return response['params'][0]

    def set_angle_limits(self, lower_degrees, upper_degrees):
        """
        set the range of movement for the servo in degrees (between -150 and 150).
        If lower_degrees and upper_degrees are the same then switches the servo to
        AXServo.MOTOR_MODE otherwise servo will be in AXServo.SERVO_MODE. 
        
        :lower_degrees: the lower/counter clockwise limit of motion of the servo. Between -150 and 150 degrees.
        :upper_degrees: the upper/clockwise limit of motion of the servo. Between -150 and 150 degrees
        """
        cw = 0
        ccw = 0
        if lower_degrees != upper_degrees:
            ccw = __degrees_to_raw(lower_degrees)
            cw = __degrees_to_raw(upper_degrees)

        # Parameters: [Address, CW_L, CW_H, CCW_L, CCW_H]
        params = [
            self.CW_ANGLE_LIMIT, 
            ccw & 0xFF, (ccw >> 8) & 0xFF, 
            cw & 0xFF, (cw >> 8) & 0xFF
        ]
        self.__send(self.INST_WRITE, params)
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())
        self.__mode = self.MOTOR_MODE if cw == 0 and ccw == 0 else self.SERVO_MODE

    def set_torque_limit(self, torque_limit):
        """
        set the torque limit of the servo.
        
        :torque_limit: the new torque limit in the range 0..1023.
        """
        # Clamp to hardware limits
        clamped_torque_limit = max(0, min(1023, torque_limit))
    
        # Parameters: [Address, CW_L, CW_H, CCW_L, CCW_H]
        params = [
            self.TORQUE_LIMIT, 
            clamped_torque_limit & 0xFF, (clamped_torque_limit >> 8) & 0xFF
        ]
        self.__send(self.INST_WRITE, params)
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

    def set_punch(self, punch):    
        """
        set the punch of the servo.
        
        :punch: the new punch in the range 0..1023.
        """
        # Clamp to hardware limits
        clamped_punch = max(0, min(1023, punch))
    
        # Parameters: [Address, PUNCH_L, PUNCH_H]
        params = [
            self.PUNCH, 
            clamped_punch & 0xFF, (clamped_punch >> 8) & 0xFF
        ]
        self.__send(self.INST_WRITE, params)
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

    def set_voltage_limits(self, low_v, high_v):
        """
        set the low and high voltage limits. These limits define the
        safe operating range for the input voltage; if the actual voltage
        falls outside this range, the servo triggers an error to protect
        its internal components. 
        
        :low_v: the low voltage level in the range 5-16V
        :high_v: the high voltage level in the range 5-16V        
        """
        # Convert Volts to raw 1-byte integers (e.g., 11.5V -> 115)
        # Range is roughly 50 to 160 (5.0V to 16.0V)
        low_raw = int(max(5.0, min(16.0, low_v)) * 10)
        high_raw = int(max(5.0, min(16.0, high_v)) * 10)
        
        # Parameters: [Starting Address, Low_Val, High_Val]
        params = [self.DOWN_LIMIT_VOLTAGE, low_raw, high_raw]
        
        self.__send(self.INST_WRITE, params)
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

    def set_temperature_limit(self, limit):
        """
        set the max safe operating temperature for the servo. This limits
        defines the safe max temperature; if the actual temperature of the servo
        is above this then the servo triggers an error to protect its internal
        components. 
        
        :limit: the temperature limit between 50..100C. 
        """
        limit = min(max(limit, 50), 100)
        self.__send(self.INST_WRITE, [self.TEMP_LIMIT, limit])
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

    # Fault Settings
    def fault_config(self):
        if self.__id == self.BROADCAST_ID:
            raise ValueError("cannot read the fault configuration when broadcasting")

        self.__send(self.INST_READ, [self.ADDR_ALARM_LED, 2])
        response = self.__receive()

        return response['params'][0], response['params'][1]

    def configure_faults(self, led_bits=None, shutdown_bits=None):
        """
        Updates LED or Shutdown behavior. Pass None to keep current.
        """
        current_led, current_shutdown = self.fault_config()
        
        new_led = led_bits if led_bits is not None else current_led
        new_shutdown = shutdown_bits if shutdown_bits is not None else current_shutdown

        params = [self.ADDR_ALARM_LED, new_led, new_shutdown]

        self.__send(self.INST_WRITE, params)
        if self.__id != self.BROADCAST_ID:
            self.__check_response(self.__receive())

    def __check_response(self, response):
        if response['error'] != 0:
            raise ValueError(f"error setting properties: {response}")
        
    def __switch_to_servo_mode(self):
        self.set_angle_limits(-150.0, 150.0)

        if self.__id != self.BROADCAST_ID:
            self.__mode = AXServo.SERVO_MODE

    def __switch_to_motor_mode(self):
        self.set_angle_limits(-150.0, -150.0)

        if self.__id != self.BROADCAST_ID:
            self.__mode = AXServo.MOTOR_MODE

    def __send(self, command, *data):
        send_packet(self.__uart, self.__id, self.__duplexer, command, *data)

    def __receive(self, check_id=True):
        return receive_packet(self.__uart, self.__id, self.__duplexer, self.__timeout, check_id)

    def __message_header(self):
        return f"[Servo{self.__id}] "
    

class AXServoBroadcaster:

    def __init__(self, uart, duplexer, timeout=AXServo.DEFAULT_READ_TIMEOUT, debug_pin=None):
        self.__servo = AXServo(AXServo.BROADCAST_ID, uart, duplexer, timeout, debug_pin)

    # Power Control
    def enable_all(self):
        self.__servo.enable()

    def disable_all(self):
        self.__servo.disable()

    # Movement Control
    def move_all_to(self, angle, deg_per_sec):
        self.__servo.move_to(angle, deg_per_sec)

    def queue_move_all(self, angle, deg_per_sec):
        self.__servo.queue_move(angle, deg_per_sec)

    def start_all_queued(self):
        self.__servo.start_queued()

    def drive_all_at(self, speed):
        self.__servo.drive_at(speed)

    # LED Control
    def set_all_leds(self, value):
        self.__servo.set_led(value)

    # Limit Settings
    def set_all_angle_limits(self, lower, upper):
        self.__servo.set_angle_limits(lower, upper)

    def set_all_voltage_limits(self, lower, upper):
        self.__servo.set_voltage_limits(lower, upper)

    def set_all_temperature_limits(self, upper):
        self.__servo.set_temperature_limit(upper)

    def set_all_punch(self, punch):
        self.__servo.set_punch(punch)

    def set_all_torque_limit(self, torque):
        self.__servo.set_torque_limit(torque)

    # Fault Settings
    def configure_all_faults(self, led_bits, shutdown_bits):
        self.__servo.configure_faults(led_bits, shutdown_bits)




