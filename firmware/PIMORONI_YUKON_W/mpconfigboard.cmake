# cmake file for Pimoroni Yukon
set(MICROPY_BOARD "PIMORONI_YUKON_W")

# Allow Pico SDK to locate "pimoroni_yukon.h" in this directory.
list(APPEND PICO_BOARD_HEADER_DIRS "${CMAKE_CURRENT_LIST_DIR}")

set(MICROPY_SOURCE_BOARD
    ${CMAKE_CURRENT_LIST_DIR}/board.c
)

set(MICROPY_TCA9555_DIR
    ${CMAKE_CURRENT_LIST_DIR}/../drivers/tca9555/
)

set(MICROPY_PY_LWIP ON)
set(MICROPY_PY_NETWORK_CYW43 ON)

# Bluetooth
set(MICROPY_PY_BLUETOOTH ON)
set(MICROPY_BLUETOOTH_BTSTACK ON)
set(MICROPY_PY_BLUETOOTH_CYW43 ON)

# Board specific version of the frozen manifest
set(MICROPY_FROZEN_MANIFEST ${CMAKE_CURRENT_LIST_DIR}/manifest.py)

set(MICROPY_C_HEAP_SIZE 4096)
