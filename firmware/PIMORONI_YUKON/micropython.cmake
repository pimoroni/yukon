set(PIMORONI_PICO_PATH ../../../../pimoroni-pico)
include(${CMAKE_CURRENT_LIST_DIR}/../pimoroni_pico_import.cmake)

include_directories(${PIMORONI_PICO_PATH}/micropython)
include_directories(${CMAKE_CURRENT_LIST_DIR}/../modules)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/../../")
list(APPEND CMAKE_MODULE_PATH "${PIMORONI_PICO_PATH}/micropython")
list(APPEND CMAKE_MODULE_PATH "${PIMORONI_PICO_PATH}/micropython/modules")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/../modules")

# Enable support for string_view (for PicoGraphics)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Essential
include(pimoroni_i2c/micropython)
include(pimoroni_bus/micropython)

# Pico Graphics Essential
include(hershey_fonts/micropython)
include(bitmap_fonts/micropython)
include(picographics/micropython)

# Pico Graphics Extra
include(jpegdec/micropython)
include(qrcode/micropython/micropython)

# Sensors & Breakouts
include(micropython-common-breakouts)

# LEDs & Matrices
include(plasma/micropython)

# Servos & Motors
include(pwm/micropython)
include(servo/micropython)
include(encoder/micropython)
include(motor/micropython)

# Utility
include(adcfft/micropython)

# Note: cppmem is *required* for C++ code to function on MicroPython
# it redirects `malloc` and `free` calls to MicroPython's heap
include(cppmem/micropython)

# version.py, pimoroni.py and boot.py
include(modules_py/modules_py)

# Must call `enable_ulab()` to enable
include(micropython-common-ulab)
enable_ulab()

include(tca9555/micropython)