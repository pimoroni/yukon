# The entire lib dir gets added to a LittleFS filesystem and appended to the firmware
from machine import Pin
from ucollections import namedtuple

Slot = namedtuple("Slot", ("ID",
                           "FAST1",
                           "FAST2",
                           "FAST3",
                           "FAST4",
                           "SLOW1",
                           "SLOW2",
                           "SLOW3",
                           "ADC1_ADDR",
                           "ADC2_TEMP_ADDR"))

SLOT1 = Slot(1,
             Pin.board.SLOT1_FAST1,
             Pin.board.SLOT1_FAST2,
             Pin.board.SLOT1_FAST3,
             Pin.board.SLOT1_FAST4,
             Pin.board.SLOT1_SLOW1,
             Pin.board.SLOT1_SLOW2,
             Pin.board.SLOT1_SLOW3,
             0,  # 0b0000
             3   # 0b0011
             ) 

SLOT2 = Slot(2,
             Pin.board.SLOT2_FAST1,
             Pin.board.SLOT2_FAST2,
             Pin.board.SLOT2_FAST3,
             Pin.board.SLOT2_FAST4,
             Pin.board.SLOT2_SLOW1,
             Pin.board.SLOT2_SLOW2,
             Pin.board.SLOT2_SLOW3,
             1,  # 0b0001
             6   # 0b0110
             )

SLOT3 = Slot(3,
             Pin.board.SLOT3_FAST1,
             Pin.board.SLOT3_FAST2,
             Pin.board.SLOT3_FAST3,
             Pin.board.SLOT3_FAST4,
             Pin.board.SLOT3_SLOW1,
             Pin.board.SLOT3_SLOW2,
             Pin.board.SLOT3_SLOW3,
             4,  # 0b0100
             2   # 0b0010
             )

SLOT4 = Slot(4,
             Pin.board.SLOT4_FAST1,
             Pin.board.SLOT4_FAST2,
             Pin.board.SLOT4_FAST3,
             Pin.board.SLOT4_FAST4,
             Pin.board.SLOT4_SLOW1,
             Pin.board.SLOT4_SLOW2,
             Pin.board.SLOT4_SLOW3,
             5,  # 0b0101
             7   # 0b0111
             )

SLOT5 = Slot(5,
             Pin.board.SLOT5_FAST1,
             Pin.board.SLOT5_FAST2,
             Pin.board.SLOT5_FAST3,
             Pin.board.SLOT5_FAST4,
             Pin.board.SLOT5_SLOW1,
             Pin.board.SLOT5_SLOW2,
             Pin.board.SLOT5_SLOW3,
             8,  # 0b1000
             11  # 0b1011
             )

SLOT6 = Slot(6,
             Pin.board.SLOT6_FAST1,
             Pin.board.SLOT6_FAST2,
             Pin.board.SLOT6_FAST3,
             Pin.board.SLOT6_FAST4,
             Pin.board.SLOT6_SLOW1,
             Pin.board.SLOT6_SLOW2,
             Pin.board.SLOT6_SLOW3,
             9,  # 0b1001
             10  # 0b1010
             )

CURRENT_SENSE_ADDR = 12  # 0b1100
TEMP_SENSE_ADDR = 13     # 0b1101
VOLTAGE_SENSE_ADDR = 14  # 0b1110
EX_ADC_ADDR = 15         # 0b1111

# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

import time
import math
import tca
from machine import ADC
from pimoroni_yukon.modules import KNOWN_MODULES, ADC_FLOAT, ADC_LOW, ADC_HIGH
import pimoroni_yukon.logging as logging
from pimoroni_yukon.errors import OverVoltageError, UnderVoltageError, OverCurrentError, OverTemperatureError, FaultError, VerificationError
from pimoroni_yukon.timing import ticks_ms, ticks_add, ticks_diff
from ucollections import OrderedDict


class Yukon:
    """Yukon class."""

    VOLTAGE_MAX = 17.0
    VOLTAGE_MIN_MEASURE = 0.030
    VOLTAGE_MAX_MEASURE = 2.294

    CURRENT_MAX = 10.0
    CURRENT_MIN_MEASURE = 0.0147
    CURRENT_MAX_MEASURE = 0.9307

    SWITCH_A = 0
    SWITCH_B = 1
    SWITCH_A_NAME = 'A'
    SWITCH_B_NAME = 'B'
    SWITCH_USER = 2
    NUM_SLOTS = 6

    DEFAULT_VOLTAGE_LIMIT = 17.2
    VOLTAGE_LOWER_LIMIT = 4.8
    VOLTAGE_ZERO_LEVEL = 0.05
    DEFAULT_CURRENT_LIMIT = 20
    DEFAULT_TEMPERATURE_LIMIT = 90
    ABSOLUTE_MAX_VOLTAGE_LIMIT = 18

    DETECTION_SAMPLES = 64
    DETECTION_ADC_LOW = 0.1
    DETECTION_ADC_HIGH = 3.2

    def __init__(self, voltage_limit=DEFAULT_VOLTAGE_LIMIT, current_limit=DEFAULT_CURRENT_LIMIT, temperature_limit=DEFAULT_TEMPERATURE_LIMIT, logging_level=logging.LOG_INFO):
        self.__voltage_limit = min(voltage_limit, self.ABSOLUTE_MAX_VOLTAGE_LIMIT)
        self.__current_limit = current_limit
        self.__temperature_limit = temperature_limit
        logging.level = logging_level

        self.__slot_assignments = OrderedDict({
            SLOT1: None,
            SLOT2: None,
            SLOT3: None,
            SLOT4: None,
            SLOT5: None,
            SLOT6: None
        })

        # Main output enable
        self.__main_en = Pin.board.MAIN_EN
        self.__main_en.init(Pin.OUT, value=False)

        # User/Boot switch
        self.__sw_boot = Pin.board.USER_SW
        self.__sw_boot.init(Pin.IN)

        # ADC mux enable pins
        self.__adc_mux_ens = (Pin.board.ADC_MUX_EN_1,
                              Pin.board.ADC_MUX_EN_2)
        self.__adc_mux_ens[0].init(Pin.OUT, value=False)
        self.__adc_mux_ens[1].init(Pin.OUT, value=False)

        # ADC mux address pins
        self.__adc_mux_addrs = (Pin.board.ADC_ADDR_1,
                                Pin.board.ADC_ADDR_2,
                                Pin.board.ADC_ADDR_3)
        self.__adc_mux_addrs[0].init(Pin.OUT, value=False)
        self.__adc_mux_addrs[1].init(Pin.OUT, value=False)
        self.__adc_mux_addrs[2].init(Pin.OUT, value=False)

        self.__adc_io_chip = tca.get_chip(Pin.board.ADC_ADDR_1)
        self.__adc_io_ens_addrs = (1 << tca.get_number(Pin.board.ADC_MUX_EN_1),
                                   1 << tca.get_number(Pin.board.ADC_MUX_EN_2))
        self.__adc_io_adc_addrs = (1 << tca.get_number(Pin.board.ADC_ADDR_1),
                                   1 << tca.get_number(Pin.board.ADC_ADDR_2),
                                   1 << tca.get_number(Pin.board.ADC_ADDR_3))
        self.__adc_io_mask = self.__adc_io_ens_addrs[0] | self.__adc_io_ens_addrs[1] | \
                             self.__adc_io_adc_addrs[0] | self.__adc_io_adc_addrs[1] | self.__adc_io_adc_addrs[2]

        # User switches
        self.__switches = (Pin.board.SW_A,
                           Pin.board.SW_B)
        self.__switches[0].init(Pin.IN)
        self.__switches[1].init(Pin.IN)

        # User LEDs
        self.__leds = (Pin.board.LED_A,
                       Pin.board.LED_B)
        self.__leds[0].init(Pin.OUT, value=False)
        self.__leds[1].init(Pin.OUT, value=False)

        # Shared analog input
        self.__shared_adc = ADC(Pin.board.SHARED_ADC)

        self.__clear_readings()

        self.__monitor_action_callback = None

    def change_logging(self, logging_level):
        logging.level = logging_level

    def __check_slot(self, slot):
        if type(slot) is int:
            if slot < 1 or slot > self.NUM_SLOTS:
                raise ValueError("slot index out of range. Expected 1 to 6, or a slot object")

            slot = list(self.__slot_assignments.keys())[slot - 1]

        elif slot not in self.__slot_assignments:
            raise ValueError("slot is not a valid slot object or index")

        return slot

    def find_slots_with_module(self, module_type):
        if self.is_main_output():
            raise RuntimeError("Cannot find slots with modules whilst the main output is active")

        logging.info(f"> Finding slots with '{module_type.NAME}' module")

        slots = []
        for slot in self.__slot_assignments.keys():
            logging.info(f"[Slot{slot.ID}]", end=" ")
            detected = self.__detect_module(slot)

            if detected is module_type:
                logging.info(f"Found '{detected.NAME}' module")
                slots.append(slot.ID)
            else:
                logging.info(f"No '{module_type.NAME}` module")

        return slots

    def register_with_slot(self, module, slot):
        if self.is_main_output():
            raise RuntimeError("Cannot register modules with slots whilst the main output is active")

        slot = self.__check_slot(slot)

        if self.__slot_assignments[slot] is None:
            self.__slot_assignments[slot] = module
        else:
            raise ValueError("The selected slot is already populated")

    def deregister_slot(self, slot):
        if self.is_main_output():
            raise RuntimeError("Cannot deregister module slots whilst the main output is active")

        slot = self.__check_slot(slot)

        module = self.__slot_assignments[slot]
        if module is not None:
            module.deregister()
            self.__slot_assignments[slot] = None

    def __match_module(self, adc_level, slow1, slow2, slow3):
        for m in KNOWN_MODULES:
            if m.is_module(adc_level, slow1, slow2, slow3):
                return m
        return None

    def __detect_module(self, slot):
        slow1 = slot.SLOW1
        slow1.init(Pin.IN)

        slow2 = slot.SLOW2
        slow2.init(Pin.IN)

        slow3 = slot.SLOW3
        slow3.init(Pin.IN)

        self.__select_address(slot.ADC1_ADDR)
        adc_val = 0
        for i in range(self.DETECTION_SAMPLES):
            adc_val += self.__shared_adc_voltage()
        adc_val /= self.DETECTION_SAMPLES

        logging.debug(f"ADC1 = {adc_val}, SLOW1 = {int(slow1.value)}, SLOW2 = {int(slow2.value)}, SLOW3 = {int(slow3.value)}", end=", ")

        adc_level = ADC_FLOAT
        if adc_val <= self.DETECTION_ADC_LOW:
            adc_level = ADC_LOW
        elif adc_val >= self.DETECTION_ADC_HIGH:
            adc_level = ADC_HIGH

        detected = self.__match_module(adc_level, slow1.value, slow2.value, slow3.value)

        self.__deselect_address()
        slow3.deinit()
        slow2.deinit()
        slow1.deinit()

        return detected

    def detect_module(self, slot):
        if self.is_main_output():
            raise RuntimeError("Cannot detect modules whilst the main output is active")

        slot = self.__check_slot(slot)

        return self.__detect_module(slot)

    def __expand_slot_list(self, slot_list):
        if type(slot_list) is bool:
            if slot_list:
                return list(self.__slot_assignments.keys())
            else:
                return []

        if type(slot_list) in (list, tuple):
            exp_list = []
            for slot in slot_list:
                exp_list.append(self.__check_slot(slot))
            return exp_list

        return [self.__check_slot(slot_list)]

    def __verify_modules(self, allow_unregistered, allow_undetected, allow_discrepencies, allow_no_modules):
        # Take the allowed parameters and expand them into slot lists that are easier to compare against
        allow_unregistered = self.__expand_slot_list(allow_unregistered)
        allow_undetected = self.__expand_slot_list(allow_undetected)
        allow_discrepencies = self.__expand_slot_list(allow_discrepencies)

        raise_unregistered = False
        raise_undetected = False
        raise_discrepency = False
        unregistered_slots = 0

        for slot, module in self.__slot_assignments.items():
            logging.info(f"[Slot{slot.ID}]", end=" ")
            detected = self.__detect_module(slot)

            if detected is None:
                if module is not None:
                    logging.info(f"No module detected! Expected a '{module.NAME}' module.")
                    if slot not in allow_undetected:
                        raise_undetected = True
                else:
                    logging.info("Module slot is empty.")
                    unregistered_slots += 1
            else:
                if module is not None:
                    if type(module) is detected:
                        logging.info(f"'{module.NAME}' module detected and registered.")
                    else:
                        logging.info(f"Module discrepency! Expected a '{module.NAME}' module, but detected a '{detected.NAME}' module.")
                        if slot not in allow_discrepencies:
                            raise_discrepency = True
                else:
                    logging.info(f"'{detected.NAME}' module detected but not registered.")
                    if slot not in allow_unregistered:
                        raise_unregistered = True
                    unregistered_slots += 1

        if not allow_no_modules and unregistered_slots == self.NUM_SLOTS:
            raise VerificationError("No modules have been registered with Yukon. At least one module needs to be registered to enable the output")

        if raise_discrepency:
            raise VerificationError("Detected a different combination of modules than what was registered with Yukon. Please check the modules attached to your board and the program you are running.")

        if raise_undetected:
            raise VerificationError("Some or all modules registered with Yukon have not been detected. Please check that the modules are correctly attached to your board or disable this warning.")

        if raise_unregistered:
            raise VerificationError("Detected modules that have not been registered with Yukon, which could behave unexpectedly when connected to power. Please remove these modules or disable this warning.")

        logging.info()  # New line

    def initialise_modules(self, allow_unregistered=False, allow_undetected=False, allow_discrepencies=False, allow_no_modules=False):
        if self.is_main_output():
            raise RuntimeError("Cannot verify modules whilst the main output is active")

        logging.info("> Verifying modules")

        self.__verify_modules(allow_unregistered, allow_undetected, allow_discrepencies, allow_no_modules)

        logging.info("> Initialising modules")

        for slot, module in self.__slot_assignments.items():
            if module is not None:
                logging.info(f"[Slot{slot.ID} '{module.NAME}'] Initialising ... ", end="")
                module.initialise(slot, self.read_slot_adc1, self.read_slot_adc2)
                logging.info("done")

        logging.info()  # New line

    def is_pressed(self, switch):
        if switch is self.SWITCH_A_NAME:
            switch = self.SWITCH_A
        elif switch is self.SWITCH_B_NAME:
            switch = self.SWITCH_B
        elif switch < 0 or switch > 1:
            raise ValueError("switch out of range. Expected 'A' or 'B', or SWITCH_A (0) or SWITCH_B (1)")

        return not self.__switches[switch].value()

    def is_boot_pressed(self):
        return not self.__sw_boot.value()

    def set_led(self, switch, value):
        if switch is self.SWITCH_A_NAME:
            switch = self.SWITCH_A
        elif switch is self.SWITCH_B_NAME:
            switch = self.SWITCH_B
        elif switch < 0 or switch > 1:
            raise ValueError("switch out of range. Expected 'A' or 'B', or SWITCH_A (0) or SWITCH_B (1)")

        self.__leds[switch].value(value)

    def enable_main_output(self):
        if self.is_main_output() is False:
            start = time.ticks_us()

            self.__select_address(board.VOLTAGE_SENSE_ADDR)

            old_voltage = max(((self.__shared_adc_voltage() - self.VOLTAGE_MIN_MEASURE) * self.VOLTAGE_MAX) / (self.VOLTAGE_MAX_MEASURE - self.VOLTAGE_MIN_MEASURE), 0.0)
            first_stable_time = 0
            new_voltage = 0
            dur = 100 * 1000
            dur_b = 5 * 1000

            logging.info("> Enabling output ...")
            self.__enable_main_output()
            while True:
                new_voltage = ((self.__shared_adc_voltage() - self.VOLTAGE_MIN_MEASURE) * self.VOLTAGE_MAX) / (self.VOLTAGE_MAX_MEASURE - self.VOLTAGE_MIN_MEASURE)
                if new_voltage > self.ABSOLUTE_MAX_VOLTAGE_LIMIT:
                    self.disable_main_output()
                    raise OverVoltageError("[Yukon] Input voltage exceeded a safe level! Turning off output")

                new_time = time.ticks_us()
                if abs(new_voltage - old_voltage) < 0.05:
                    if first_stable_time == 0:
                        first_stable_time = new_time
                    elif new_time - first_stable_time > dur_b:
                        break
                else:
                    first_stable_time = 0

                if new_time - start > dur:
                    self.disable_main_output()
                    raise FaultError("[Yukon] Output voltage did not stablise in an acceptable time. Turning off output")

                old_voltage = new_voltage

            if new_voltage < self.VOLTAGE_ZERO_LEVEL:
                self.disable_main_output()
                raise UnderVoltageError("[Yukon] No input voltage detected! Make sure power is being provided to the XT-30 (yellow) connector")

            if new_voltage < self.VOLTAGE_LOWER_LIMIT:
                self.disable_main_output()
                raise UnderVoltageError("[Yukon] Input voltage below minimum operating level. Turning off output")

            self.clear_readings()

            logging.info("> Output enabled")

    def __enable_main_output(self):
        self.__main_en.value(True)

    def disable_main_output(self):
        self.__main_en.value(False)
        logging.info("> Output disabled")

    def is_main_output(self):
        return self.__main_en.value()

    def __deselect_address(self):
        self.__adc_mux_ens[0].value(False)
        self.__adc_mux_ens[1].value(False)

    def __select_address(self, address):
        if address < 0:
            raise ValueError("address is less than zero")
        elif address > 0b1111:
            raise ValueError("address is greater than number of available addresses")
        else:
            state = 0x0000

            if address & 0b0001 > 0:
                state |= self.__adc_io_adc_addrs[0]

            if address & 0b0010 > 0:
                state |= self.__adc_io_adc_addrs[1]

            if address & 0b0100 > 0:
                state |= self.__adc_io_adc_addrs[2]

            if address & 0b1000 > 0:
                state |= self.__adc_io_ens_addrs[0]
            else:
                state |= self.__adc_io_ens_addrs[1]

            tca.change_output_mask(self.__adc_io_chip, self.__adc_io_mask, state)

    def __shared_adc_voltage(self):
        return (self.__shared_adc.read_u16() * 3.3) / 65536 # TODO check if 65536 or 65535

    def read_voltage(self):
        self.__select_address(VOLTAGE_SENSE_ADDR)
        # return (self.__shared_adc_voltage() * (100 + 16)) / 16  # Old equation, kept for reference
        return max(((self.__shared_adc_voltage() - self.VOLTAGE_MIN_MEASURE) * self.VOLTAGE_MAX) / (self.VOLTAGE_MAX_MEASURE - self.VOLTAGE_MIN_MEASURE), 0.0)

    def read_current(self):
        self.__select_address(CURRENT_SENSE_ADDR)
        # return (self.__shared_adc_voltage() - 0.015) / ((1 + (5100 / 27.4)) * 0.0005)  # Old equation, kept for reference
        return max(((self.__shared_adc_voltage() - self.CURRENT_MIN_MEASURE) * self.CURRENT_MAX) / (self.CURRENT_MAX_MEASURE - self.CURRENT_MIN_MEASURE), 0.0)

    def read_temperature(self):
        self.__select_address(TEMP_SENSE_ADDR)
        sense = self.__shared_adc_voltage()
        r_thermistor = sense / ((3.3 - sense) / 5100)
        ROOM_TEMP = 273.15 + 25
        RESISTOR_AT_ROOM_TEMP = 10000.0
        BETA = 3435
        t_kelvin = (BETA * ROOM_TEMP) / (BETA + (ROOM_TEMP * math.log(r_thermistor / RESISTOR_AT_ROOM_TEMP)))
        t_celsius = t_kelvin - 273.15

        # https://www.allaboutcircuits.com/projects/measuring-temperature-with-an-ntc-thermistor/
        return t_celsius

    def read_expansion(self):
        self.__select_address(EX_ADC_ADDR)
        return self.__shared_adc_voltage()

    def read_slot_adc1(self, slot):
        self.__select_address(slot.ADC1_ADDR)
        return self.__shared_adc_voltage()

    def read_slot_adc2(self, slot):
        self.__select_address(slot.ADC2_TEMP_ADDR)
        return self.__shared_adc_voltage()

    def assign_monitor_action(self, callback_function):
        if not None and not callable(callback_function):
            raise TypeError("callback is not callable or None")

        self.__monitor_action_callback = callback_function

    def monitor(self):
        voltage = self.read_voltage()
        if voltage > self.__voltage_limit:
            self.disable_main_output()
            raise OverVoltageError(f"[Yukon] Voltage of {voltage}V exceeded the user set level of {self.__voltage_limit}V! Turning off output")

        if voltage < self.VOLTAGE_LOWER_LIMIT:
            self.disable_main_output()
            raise UnderVoltageError(f"[Yukon] Voltage of {voltage}V below minimum operating level. Turning off output")

        current = self.read_current()
        if current > self.__current_limit:
            self.disable_main_output()
            raise OverCurrentError(f"[Yukon] Current of {current}A exceeded the user set level of {self.__current_limit}A! Turning off output")

        temperature = self.read_temperature()
        if temperature > self.__temperature_limit:
            self.disable_main_output()
            raise OverTemperatureError(f"[Yukon] Temperature of {temperature}°C exceeded the user set level of {self.__temperature_limit}°C! Turning off output")

        # Run some user action based on the latest readings
        if self.__monitor_action_callback is not None:
            self.__monitor_action_callback(voltage, current, temperature)

        for module in self.__slot_assignments.values():
            if module is not None:
                try:
                    module.monitor()
                except Exception:
                    self.disable_main_output()
                    raise  # Now the output is off, let the exception continue into user code

        self.__max_voltage = max(voltage, self.__max_voltage)
        self.__min_voltage = min(voltage, self.__min_voltage)
        self.__avg_voltage += voltage

        self.__max_current = max(current, self.__max_current)
        self.__min_current = min(current, self.__min_current)
        self.__avg_current += current

        self.__max_temperature = max(temperature, self.__max_temperature)
        self.__min_temperature = min(temperature, self.__min_temperature)
        self.__avg_temperature += temperature

        self.__count_avg += 1

    def monitored_sleep(self, seconds, allowed=None, excluded=None):
        # Convert and handle the sleep as milliseconds
        self.monitored_sleep_ms(1000.0 * seconds + 0.5, allowed=allowed, excluded=excluded)

    def monitored_sleep_ms(self, ms, allowed=None, excluded=None):
        if ms < 0:
            raise ValueError("sleep length must be non-negative")

        # Calculate the time this sleep should end at, and monitor until then
        self.monitor_until_ms(ticks_add(ticks_ms(), int(ms)), allowed=allowed, excluded=excluded)

    def monitor_until_ms(self, end_ms, allowed=None, excluded=None):
        if end_ms < 0:
            raise ValueError("end_ms out or range. Must be a value obtained from time.ticks_ms()")

        # Clear any readings from previous monitoring attempts
        self.clear_readings()

        # Ensure that at least one monitor check is performed
        self.monitor()
        remaining_ms = ticks_diff(end_ms, ticks_ms())

        # Perform any subsequent monitors until the end time is reached
        while remaining_ms > 0:
            self.monitor()
            remaining_ms = ticks_diff(end_ms, ticks_ms())

        # Process any readings that need it (e.g. averages)
        self.process_readings()

        if logging.level >= logging.LOG_INFO:
            self.__print_readings(allowed, excluded)

    def monitor_once(self, allowed=None, excluded=None):
        # Clear any readings from previous monitoring attempts
        self.clear_readings()

        # Perform a single monitoring check
        self.monitor()

        # Process any readings that need it (e.g. averages)
        self.process_readings()

        if logging.level >= logging.LOG_INFO:
            self.__print_readings(allowed, excluded)

    def __print_readings(self, allowed=None, excluded=None):
        self.__print_dict("[Yukon]", self.get_readings(), allowed, excluded)

        for slot, module in self.__slot_assignments.items():
            if module is not None:
                self.__print_dict(f"[Slot{slot.ID}]", module.get_readings(), allowed, excluded)
        print()

    def get_readings(self):
        return OrderedDict({
            "V_max": self.__max_voltage,
            "V_min": self.__min_voltage,
            "V_avg": self.__avg_voltage,
            "C_max": self.__max_current,
            "C_min": self.__min_current,
            "C_avg": self.__avg_current,
            "T_max": self.__max_temperature,
            "T_min": self.__min_temperature,
            "T_avg": self.__avg_temperature
        })

    def process_readings(self):
        if self.__count_avg > 0:
            self.__avg_voltage /= self.__count_avg
            self.__avg_current /= self.__count_avg
            self.__avg_temperature /= self.__count_avg

        for module in self.__slot_assignments.values():
            if module is not None:
                module.process_readings()

    def __clear_readings(self):
        self.__max_voltage = float('-inf')
        self.__min_voltage = float('inf')
        self.__avg_voltage = 0

        self.__max_current = float('-inf')
        self.__min_current = float('inf')
        self.__avg_current = 0

        self.__max_temperature = float('-inf')
        self.__min_temperature = float('inf')
        self.__avg_temperature = 0

        self.__count_avg = 0

    def clear_readings(self):
        self.__clear_readings()
        for module in self.__slot_assignments.values():
            if module is not None:
                module.clear_readings()

    def __print_dict(self, section_name, readings, allowed=None, excluded=None):
        if len(readings) > 0:
            print(section_name, end=" ")
            for name, value in readings.items():
                if ((allowed is None) or (allowed is not None and name in allowed)) and ((excluded is None) or (excluded is not None and name not in excluded)):
                    if type(value) is bool:
                        print(f"{name} = {int(value)},", end=" ")  # Output 0 or 1 rather than True of False, so bools can appear on plotter charts
                    else:
                        print(f"{name} = {value},", end=" ")

    def reset(self):
        # Only disable the output if enabled (avoids duplicate messages)
        if self.is_main_output() is True:
            self.disable_main_output()

        self.__adc_mux_ens[0].value(False)
        self.__adc_mux_ens[1].value(False)

        self.__adc_mux_addrs[0].value(False)
        self.__adc_mux_addrs[1].value(False)
        self.__adc_mux_addrs[2].value(False)

        self.__leds[0].value(False)
        self.__leds[1].value(False)

        # Configure each module so they go back to their default states
        for module in self.__slot_assignments.values():
            if module is not None and module.is_initialised():
                module.configure()
