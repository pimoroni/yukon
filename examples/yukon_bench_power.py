#import time
from pimoroni_yukon import Yukon
from pimoroni_yukon.modules import BenchPowerModule, ProtoPotModule

# Select the slot that the module is installed in
SLOT = 1

# Create a Yukon object to begin using the board, and a set a voltage limit just above what the fans are rated for
yukon = Yukon(voltage_limit=15.5, logging_level=1)

try:
    # Create a BenchPowerModule and register it with a slot on Yukon
    bench = BenchPowerModule()
    pot = ProtoPotModule()
    yukon.register_with_slot(bench, SLOT)
    yukon.register_with_slot(pot, SLOT+1)

    # Initialise Yukon's registered modules
    yukon.initialise_modules(allow_unregistered=True, allow_discrepencies=True)

    # Turn on the module power
    yukon.enable_main_output()

    # Enable the switched outputs
    bench.enable()

    while not yukon.is_boot_pressed():
        pot_val = pot.read()
        bench.set_target(pot_val)

        voltage = bench.read_voltage()
        print(f"Percent = {pot_val}, Voltage = {voltage}")

        # Use the Yukon class to sleep, which lets it monitor voltage, current, and temperature
        yukon.monitored_sleep(0.1)

finally:
    # Put the board back into a safe state, regardless of how the program may have ended
    yukon.reset()
