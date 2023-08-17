# cmake file for Pimoroni Yukon
set(MICROPY_BOARD "PIMORONI_YUKON")

# Allow Pico SDK to locate "pimoroni_yukon.h" in this directory.
list(APPEND PICO_BOARD_HEADER_DIRS "${CMAKE_CURRENT_LIST_DIR}")

set(MICROPY_SOURCE_BOARD
    ${CMAKE_CURRENT_LIST_DIR}/board.c
)

# Board specific version of the frozen manifest
set(MICROPY_FROZEN_MANIFEST ${CMAKE_CURRENT_LIST_DIR}/manifest.py)

set(MICROPY_C_HEAP_SIZE 4096)
