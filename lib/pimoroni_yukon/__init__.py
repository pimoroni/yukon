# SPDX-FileCopyrightText: 2023 Christopher Parrott for Pimoroni Ltd
#
# SPDX-License-Identifier: MIT

import sys
import time
import tca
from machine import ADC, Pin, I2C
from pimoroni_yukon.modules import KNOWN_MODULES
from pimoroni_yukon.modules.common import ADC_FLOAT, ADC_LOW, ADC_HIGH, YukonModule
import pimoroni_yukon.logging as logging
from pimoroni_yukon.errors import OverVoltageError, UnderVoltageError, OverCurrentError, OverTemperatureError, FaultError, VerificationError
from pimoroni_yukon.timing import ticks_ms, ticks_add, ticks_diff
from pimoroni_yukon.conversion import u16_to_voltage_in, u16_to_voltage_out, u16_to_current, analog_to_temp
from ucollections import OrderedDict, namedtuple


YUKON_VERSION = "1.0.0"

Slot = namedtuple("Slot", ("ID",
                           "FAST1",
                           "FAST2",
                           "FAST3",
                           "FAST4",
                           "SLOW1",
                           "SLOW2",
                           "SLOW3",
                           "ADC1_ADDR",
                           "ADC2_THERM_ADDR"))

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

GP26 = Pin.board.GP26
GP27 = Pin.board.GP27

LCD_CS = Pin.board.LCD_CS
LCD_DC = Pin.board.LCD_DC
LCD_BL = Pin.board.LCD_BL


class Yukon:
    """Yukon class."""
    SWITCH_A = 0
    SWITCH_B = 1
    SWITCH_A_NAME = 'A'
    SWITCH_B_NAME = 'B'
    SWITCH_USER = 2
    NUM_SLOTS = 6

    DEFAULT_VOLTAGE_LIMIT = 17.2
    VOLTAGE_LOWER_LIMIT = 4.8
    VOLTAGE_ZERO_LEVEL = 0.2
    VOLTAGE_SHORT_LEVEL = 0.5
    DEFAULT_CURRENT_LIMIT = 20
    DEFAULT_TEMPERATURE_LIMIT = 80
    ABSOLUTE_MAX_VOLTAGE_LIMIT = 18
    UNDERVOLTAGE_COUNT_LIMIT = 3

    DETECTION_SAMPLES = 64
    DETECTION_ADC_LOW = 0.2
    DETECTION_ADC_HIGH = 3.2

    CURRENT_SENSE_ADDR = 12      # 0b1100
    TEMP_SENSE_ADDR = 13         # 0b1101
    VOLTAGE_OUT_SENSE_ADDR = 14  # 0b1110
    VOLTAGE_IN_SENSE_ADDR = 15   # 0b1111

    OUTPUT_STABLISE_TIMEOUT_US = 200 * 1000     # The time to wait for the output voltage to stablise after being enabled
    OUTPUT_STABLISE_TIME_US = 10 * 1000
    OUTPUT_STABLISE_V_DIFF = 0.1

    OUTPUT_DISSIPATE_TIMEOUT_S = 5              # The time to wait for the voltage to dissipate below the level needed for module detection
    OUTPUT_DISSIPATE_TIMEOUT_US = OUTPUT_DISSIPATE_TIMEOUT_S * 1000 * 1000
    OUTPUT_DISSIPATE_TIME_US = 10 * 1000
    OUTPUT_DISSIPATE_LEVEL = 2.0                # The voltage below which we can reliably obtain the address of attached modules

    def __init__(self, voltage_limit=DEFAULT_VOLTAGE_LIMIT, current_limit=DEFAULT_CURRENT_LIMIT, temperature_limit=DEFAULT_TEMPERATURE_LIMIT, logging_level=logging.LOG_INFO):
        self.__voltage_limit = min(voltage_limit, self.ABSOLUTE_MAX_VOLTAGE_LIMIT)
        self.__current_limit = current_limit
        self.__temperature_limit = temperature_limit
        logging.level = logging_level

        logging.info(f"> Running Yukon {YUKON_VERSION}, {sys.version.split('; ')[1]}")

        self.__slot_assignments = OrderedDict({
            SLOT1: None,
            SLOT2: None,
            SLOT3: None,
            SLOT4: None,
            SLOT5: None,
            SLOT6: None
        })

        # Set up the i2c for Qw/st and Breakout Garden
        self.i2c = I2C(0, sda=Pin.board.SDA, scl=Pin.board.SCL, freq=400000)

        # Main output enable
        self.__main_en = Pin.board.MAIN_EN
        self.__main_en.init(Pin.OUT, value=False)

        # User/Boot switch
        self.__sw_boot = Pin.board.USER_SW
        self.__sw_boot.init(Pin.IN)

        # ADC mux enable pins
        self.__adc_mux_ens = (Pin.board.ADC_MUX_EN_1,
                              Pin.board.ADC_MUX_EN_2)
        self.__adc_mux_ens[0].init(Pin.OUT, value=True)  # Active low
        self.__adc_mux_ens[1].init(Pin.OUT, value=True)  # Active low

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

        self.__clear_counts_and_readings()

        self.__monitor_action_callback = None

    def reset(self):
        logging.debug("[Yukon] Resetting")

        # Only disable the output if enabled (avoids duplicate messages)
        if self.is_main_output_enabled() is True:
            self.disable_main_output()

        self.__deselect_address()

        self.__leds[0].value(False)
        self.__leds[1].value(False)

        # Configure each module so they go back to their default states
        for module in self.__slot_assignments.values():
            if module is not None and module.is_initialised():
                module.reset()

    def change_logging(self, logging_level):
        logging.level = logging_level

    def __check_slot(self, slot):
        if isinstance(slot, int):
            if slot < 1 or slot > self.NUM_SLOTS:
                raise ValueError("slot index out of range. Expected 1 to 6, or a slot object")

            slot = list(self.__slot_assignments.keys())[slot - 1]

        elif slot not in self.__slot_assignments:
            raise ValueError("slot is not a valid slot object or index")

        return slot

    def __check_output_dissipated(self, message):
        logging.info("> Checking output voltage ...")
        voltage = self.read_output_voltage()
        logging.debug(f"Output Voltage = {voltage} V")
        if voltage >= self.OUTPUT_DISSIPATE_LEVEL:
            logging.warn("> Waiting for output voltage to dissipate ...")

            start = time.ticks_us()
            first_below_time = 0
            while True:
                new_voltage = self.read_output_voltage()
                logging.debug(f"Output Voltage = {new_voltage} V")
                new_time = time.ticks_us()
                if new_voltage < self.OUTPUT_DISSIPATE_LEVEL:
                    if first_below_time == 0:
                        first_below_time = new_time
                    elif ticks_diff(new_time, first_below_time) > self.OUTPUT_DISSIPATE_TIME_US:
                        break
                else:
                    first_below_time = 0

                if ticks_diff(new_time, start) > self.OUTPUT_DISSIPATE_TIMEOUT_US:
                    raise FaultError(f"[Yukon] Output voltage did not dissipate in an acceptable time. Aborting {message}")

    def find_slots_with(self, module_type):
        if self.is_main_output_enabled():
            raise RuntimeError("Cannot find slots with modules whilst the main output is active")

        self.__check_output_dissipated("module finding")

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

        logging.info()  # New line

        return slots

    def register_with_slot(self, module, slot):
        if self.is_main_output_enabled():
            raise RuntimeError("Cannot register modules with slots whilst the main output is active")

        slot = self.__check_slot(slot)

        module_type = type(module)
        if module_type is YukonModule:
            raise ValueError("Cannot register YukonModule")

        if module_type not in KNOWN_MODULES:
            raise ValueError(f"{module_type} is not a known module. If this is custom module, be sure to include it in the KNOWN_MODULES list.")

        if self.__slot_assignments[slot] is None:
            self.__slot_assignments[slot] = module
        else:
            raise ValueError("The selected slot is already populated")

    def deregister_slot(self, slot):
        if self.is_main_output_enabled():
            raise RuntimeError("Cannot deregister module slots whilst the main output is active")

        slot = self.__check_slot(slot)

        module = self.__slot_assignments[slot]
        if module is not None:
            module.deregister()
            self.__slot_assignments[slot] = None

    def __match_module(self, adc1_level, adc2_level, slow1, slow2, slow3):
        for m in KNOWN_MODULES:
            if m.is_module(adc1_level, adc2_level, slow1, slow2, slow3):
                return m
        if YukonModule.is_module(adc1_level, adc2_level, slow1, slow2, slow3):
            return YukonModule
        return None

    def __detect_module(self, slot):
        slow1 = slot.SLOW1
        slow1.init(Pin.IN)

        slow2 = slot.SLOW2
        slow2.init(Pin.IN)

        slow3 = slot.SLOW3
        slow3.init(Pin.IN)

        adc1_val = self.read_slot_adc1(slot, self.DETECTION_SAMPLES)
        adc2_val = self.read_slot_adc2(slot, self.DETECTION_SAMPLES)

        logging.debug(f"ADC1 = {adc1_val}, ADC2 = {adc2_val}, SLOW1 = {slow1.value()}, SLOW2 = {slow2.value()}, SLOW3 = {slow3.value()}", end=", ")

        # Convert the ADC voltage to a LOW, FLOAT, or HIGH level
        adc1_level = ADC_LOW if adc1_val <= self.DETECTION_ADC_LOW else ADC_HIGH if adc1_val >= self.DETECTION_ADC_HIGH else ADC_FLOAT
        adc2_level = ADC_LOW if adc2_val <= self.DETECTION_ADC_LOW else ADC_HIGH if adc2_val >= self.DETECTION_ADC_HIGH else ADC_FLOAT

        detected = self.__match_module(adc1_level, adc2_level, slow1.value() == 1, slow2.value() == 1, slow3.value() == 1)

        self.__deselect_address()

        return detected

    def detect_in_slot(self, slot):
        if self.is_main_output_enabled():
            raise RuntimeError("Cannot detect module whilst the main output is active")

        self.__check_output_dissipated("module detection")

        slot = self.__check_slot(slot)

        return self.__detect_module(slot)

    def __expand_slot_list(self, slot_list):
        if isinstance(slot_list, bool):
            if slot_list:
                return list(self.__slot_assignments.keys())
            else:
                return []

        if isinstance(slot_list, (list, tuple)):
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
            raise VerificationError("No modules have been registered with Yukon. At least one module needs to be registered to enable the output, or disable this warning with `allow_no_modules=True`.")

        if raise_discrepency:
            raise VerificationError("Detected a different combination of modules than what was registered with Yukon. Please check the modules attached to your board and the program you are running, or disable this warning with `allow_discrepencies=True`.")

        if raise_undetected:
            raise VerificationError("Some or all modules registered with Yukon have not been detected. Please check that the modules are correctly attached to your board, or disable this warning with `allow_undetected=True`.")

        if raise_unregistered:
            raise VerificationError("Detected modules that have not been registered with Yukon, which could behave unexpectedly when connected to power. Please register these modules with Yukon using `.register_with_slot()`, disconnect them from your board, or disable this warning with `allow_unregistered=True`.")

        logging.info()  # New line

    def verify_and_initialise(self, allow_unregistered=False, allow_undetected=False, allow_discrepencies=False, allow_no_modules=False):
        if self.is_main_output_enabled():
            raise RuntimeError("Cannot verify modules whilst the main output is active")

        self.__check_output_dissipated("module initialisation")

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

        return self.__switches[switch].value() != 1

    def is_boot_pressed(self):
        return self.__sw_boot.value() != 1

    def is_led_on(self, switch):
        if switch is self.SWITCH_A_NAME:
            switch = self.SWITCH_A
        elif switch is self.SWITCH_B_NAME:
            switch = self.SWITCH_B
        elif switch < 0 or switch > 1:
            raise ValueError("switch out of range. Expected 'A' or 'B', or SWITCH_A (0) or SWITCH_B (1)")

        return self.__leds[switch].value() == 1

    def set_led(self, switch, value):
        if switch is self.SWITCH_A_NAME:
            switch = self.SWITCH_A
        elif switch is self.SWITCH_B_NAME:
            switch = self.SWITCH_B
        elif switch < 0 or switch > 1:
            raise ValueError("switch out of range. Expected 'A' or 'B', or SWITCH_A (0) or SWITCH_B (1)")

        self.__leds[switch].value(value)

    def enable_main_output(self):
        if self.is_main_output_enabled() is False:
            logging.info("> Checking input voltage ...")
            voltage_in = self.read_input_voltage()
            if voltage_in > self.ABSOLUTE_MAX_VOLTAGE_LIMIT:
                raise OverVoltageError(f"[Yukon] Input voltage of {voltage_in}V exceeds the maximum of {self.ABSOLUTE_MAX_VOLTAGE_LIMIT}V! Aborting enable output")

            if voltage_in > self.__voltage_limit:
                raise OverVoltageError(f"[Yukon] Input voltage of {voltage_in}V exceeds the user set limit of {self.__voltage_limit}V! Aborting enable output")

            if voltage_in < self.VOLTAGE_ZERO_LEVEL:
                raise UnderVoltageError("[Yukon] No input voltage detected! Make sure power is being provided to the XT-30 (yellow) connector")

            if voltage_in < self.VOLTAGE_LOWER_LIMIT:
                raise UnderVoltageError(f"[Yukon] Input voltage of {voltage_in}V below minimum operating level of {self.VOLTAGE_LOWER_LIMIT}V! Aborting enable output")

            start = time.ticks_us()

            old_voltage = self.read_output_voltage()
            first_stable_time = 0
            new_voltage = 0

            logging.info("> Enabling output ...")
            self.__enable_main_output()
            while True:
                new_voltage = self.read_output_voltage()
                if new_voltage > self.__voltage_limit:  # User limit cannot be beyond the absolute max, so this check is fine
                    self.disable_main_output()
                    if new_voltage > self.ABSOLUTE_MAX_VOLTAGE_LIMIT:
                        raise OverVoltageError(f"[Yukon] Output voltage of {new_voltage}V exceeded the maximum of {self.ABSOLUTE_MAX_VOLTAGE_LIMIT}V! Turning off output")
                    else:
                        raise OverVoltageError(f"[Yukon] Output voltage of {new_voltage}V exceeded the user set limit of {self.__voltage_limit}V! Turning off output")

                new_time = time.ticks_us()
                if abs(new_voltage - old_voltage) < self.OUTPUT_STABLISE_V_DIFF:
                    if first_stable_time == 0:
                        first_stable_time = new_time
                    elif ticks_diff(new_time, first_stable_time) > self.OUTPUT_STABLISE_TIME_US:
                        break
                else:
                    first_stable_time = 0

                if ticks_diff(new_time, start) > self.OUTPUT_STABLISE_TIMEOUT_US:
                    self.disable_main_output()
                    raise FaultError("[Yukon] Output voltage did not stablise in an acceptable time. Turning off output")

                old_voltage = new_voltage

            # Short Circuit
            if new_voltage < self.VOLTAGE_SHORT_LEVEL:
                self.disable_main_output()
                raise FaultError(f"[Yukon] Possible short circuit! Output voltage was {new_voltage}V whilst the input voltage was {voltage_in}V. Turning off output")

            # Under Voltage
            if new_voltage < self.VOLTAGE_LOWER_LIMIT:
                self.disable_main_output()
                raise UnderVoltageError(f"[Yukon] Output voltage of {new_voltage}V below minimum operating level. Turning off output")

            self.clear_readings()

            logging.info("> Output enabled")

    def __enable_main_output(self):
        self.__main_en.value(True)

    def disable_main_output(self):
        self.__main_en.value(False)
        logging.info("> Output disabled")

    def is_main_output_enabled(self):
        return self.__main_en.value() == 1

    def __deselect_address(self):
        # Deselect the muxes and reset the address to zero
        state = self.__adc_io_ens_addrs[0] | self.__adc_io_ens_addrs[1]
        tca.change_output_mask(self.__adc_io_chip, self.__adc_io_mask, state)

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

    def __shared_adc_u16(self, samples=1):
        val = 0
        for _ in range(samples):
            val += self.__shared_adc.read_u16()
        return val / samples

    def __shared_adc_voltage(self, samples=1):
        return (self.__shared_adc_u16(samples) * 3.3) / 65535  # This has been checked to be correct

    def read_input_voltage(self, samples=1):
        self.__select_address(self.VOLTAGE_IN_SENSE_ADDR)
        return u16_to_voltage_in(self.__shared_adc_u16(samples))

    def read_output_voltage(self, samples=1):
        self.__select_address(self.VOLTAGE_OUT_SENSE_ADDR)
        return u16_to_voltage_out(self.__shared_adc_u16(samples))

    def read_current(self, samples=1):
        self.__select_address(self.CURRENT_SENSE_ADDR)
        return u16_to_current(self.__shared_adc_u16(samples))

    def read_temperature(self, samples=1):
        self.__select_address(self.TEMP_SENSE_ADDR)
        return analog_to_temp(self.__shared_adc_voltage(samples))

    def read_slot_adc1(self, slot, samples=1):
        self.__select_address(slot.ADC1_ADDR)
        return self.__shared_adc_voltage(samples)

    def read_slot_adc2(self, slot, samples=1):
        self.__select_address(slot.ADC2_THERM_ADDR)
        return self.__shared_adc_voltage(samples)

    def assign_monitor_action(self, callback_function):
        if not None and not callable(callback_function):
            raise TypeError("callback is not callable or None")

        self.__monitor_action_callback = callback_function

    def monitor(self, under_voltage_counter=UNDERVOLTAGE_COUNT_LIMIT):
        voltage_in = self.read_input_voltage()

        # Over Voltage
        if voltage_in > self.__voltage_limit:  # User limit cannot be beyond the absolute max, so this check is fine
            self.disable_main_output()
            if voltage_in > self.ABSOLUTE_MAX_VOLTAGE_LIMIT:
                raise OverVoltageError(f"[Yukon] Input voltage of {voltage_in}V exceeded the maximum of {self.ABSOLUTE_MAX_VOLTAGE_LIMIT}V! Turning off output")
            else:
                raise OverVoltageError(f"[Yukon] Input voltage of {voltage_in}V exceeded the user set limit of {self.__voltage_limit}V! Turning off output")

        # Under Voltage
        if voltage_in < self.VOLTAGE_LOWER_LIMIT:
            self.__undervoltage_count += 1
            if self.__undervoltage_count > under_voltage_counter or voltage_in < self.VOLTAGE_SHORT_LEVEL:
                self.disable_main_output()
                raise UnderVoltageError(f"[Yukon] Input voltage of {voltage_in}V below minimum operating level of {self.VOLTAGE_LOWER_LIMIT}V. Turning off output")
        else:
            self.__undervoltage_count = 0

        voltage_out = self.read_output_voltage()

        # Only check the output voltage if the main output is enabled
        if self.is_main_output_enabled():
            # Short Circuit
            if voltage_out < self.VOLTAGE_SHORT_LEVEL and voltage_in >= self.VOLTAGE_LOWER_LIMIT:
                self.disable_main_output()
                raise FaultError(f"[Yukon] Possible short circuit! Output voltage was {voltage_out}V whilst the input voltage was {voltage_in}V. Turning off output")

        # Over Current
        current = self.read_current()
        if current > self.__current_limit:
            self.disable_main_output()
            raise OverCurrentError(f"[Yukon] Current of {current}A exceeded the user set limit of {self.__current_limit}A! Turning off output")

        # Over Temperature
        temperature = self.read_temperature()
        if temperature > self.__temperature_limit:
            self.disable_main_output()
            raise OverTemperatureError(f"[Yukon] Temperature of {temperature}°C exceeded the user set limit of {self.__temperature_limit}°C! Turning off output")

        # Run some user action based on the latest readings
        if self.__monitor_action_callback is not None:
            self.__monitor_action_callback(voltage_in, voltage_out, current, temperature)

        for module in self.__slot_assignments.values():
            if module is not None:
                try:
                    module.monitor()
                except Exception:
                    self.disable_main_output()
                    raise  # Now the output is off, let the exception continue into user code

        self.__max_voltage_in = max(voltage_in, self.__max_voltage_in)
        self.__min_voltage_in = min(voltage_in, self.__min_voltage_in)
        self.__avg_voltage_in += voltage_in

        self.__max_voltage_out = max(voltage_out, self.__max_voltage_out)
        self.__min_voltage_out = min(voltage_out, self.__min_voltage_out)
        self.__avg_voltage_out += voltage_out

        self.__max_current = max(current, self.__max_current)
        self.__min_current = min(current, self.__min_current)
        self.__avg_current += current

        self.__max_temperature = max(temperature, self.__max_temperature)
        self.__min_temperature = min(temperature, self.__min_temperature)
        self.__avg_temperature += temperature

        self.__count_avg += 1

    def monitored_sleep(self, seconds, allowed=None, excluded=None, include_modules=True):
        # Convert and handle the sleep as milliseconds
        self.monitored_sleep_ms(1000.0 * seconds + 0.5, allowed, excluded, include_modules)

    def monitored_sleep_ms(self, ms, allowed=None, excluded=None, include_modules=True):
        if ms < 0:
            raise ValueError("sleep length must be non-negative")

        # Calculate the time this sleep should end at, and monitor until then
        self.monitor_until_ms(ticks_add(ticks_ms(), int(ms)), allowed, excluded, include_modules)

    def monitor_until_ms(self, end_ms, allowed=None, excluded=None, include_modules=True):
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

        if logging.level >= logging.LOG_DEBUG:
            self.print_readings(allowed, excluded, include_modules)

    def monitor_once(self, allowed=None, excluded=None, include_modules=True):
        # Clear any readings from previous monitoring attempts
        self.clear_readings()

        # Perform a single monitoring check
        self.monitor(under_voltage_counter=0)

        # Process any readings that need it (e.g. averages)
        self.process_readings()

        if logging.level >= logging.LOG_DEBUG:
            self.print_readings(allowed, excluded, include_modules)

    def get_readings(self):
        return OrderedDict({
            "Vi_max": self.__max_voltage_in,
            "Vi_min": self.__min_voltage_in,
            "Vi_avg": self.__avg_voltage_in,
            "Vo_max": self.__max_voltage_out,
            "Vo_min": self.__min_voltage_out,
            "Vo_avg": self.__avg_voltage_out,
            "C_max": self.__max_current,
            "C_min": self.__min_current,
            "C_avg": self.__avg_current,
            "T_max": self.__max_temperature,
            "T_min": self.__min_temperature,
            "T_avg": self.__avg_temperature
        })

    def get_formatted_readings(self, allowed=None, excluded=None, include_modules=True):
        text = logging.format_dict("[Yukon]", self.get_readings(), allowed, excluded)

        if include_modules:
            for module in self.__slot_assignments.values():
                if module is not None:
                    text += module.get_formatted_readings(allowed, excluded)
        return text

    def print_readings(self, allowed=None, excluded=None, include_modules=True):
        print(self.get_formatted_readings(allowed, excluded, include_modules))

    def process_readings(self):
        if self.__count_avg > 0:
            self.__avg_voltage_in /= self.__count_avg
            self.__avg_voltage_out /= self.__count_avg
            self.__avg_current /= self.__count_avg
            self.__avg_temperature /= self.__count_avg
            self.__count_avg = 0    # Clear the count to prevent process readings acting more than once

        for module in self.__slot_assignments.values():
            if module is not None:
                module.process_readings()

    def __clear_counts_and_readings(self):
        self.__undervoltage_count = 0

        self.__max_voltage_in = float('-inf')
        self.__min_voltage_in = float('inf')
        self.__avg_voltage_in = 0

        self.__max_voltage_out = float('-inf')
        self.__min_voltage_out = float('inf')
        self.__avg_voltage_out = 0

        self.__max_current = float('-inf')
        self.__min_current = float('inf')
        self.__avg_current = 0

        self.__max_temperature = float('-inf')
        self.__min_temperature = float('inf')
        self.__avg_temperature = 0

        self.__count_avg = 0

    def clear_readings(self):
        self.__clear_counts_and_readings()
        for module in self.__slot_assignments.values():
            if module is not None:
                module.clear_readings()
