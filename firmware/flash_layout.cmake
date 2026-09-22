# The flash split, shared so both variants agree and can be moved between without filesystem loss.
# The port reads the filesystem size from here, so mpconfigboard.h does not set it.
if(NOT DEFINED MICROPY_HW_FLASH_STORAGE_BYTES)
    math(EXPR MICROPY_HW_FLASH_STORAGE_BYTES "14160 * 1024")    # 13.8MB for some reason...
endif()

# A read-only partition that ships empty, mounted at /rom and filled with "mpremote romfs deploy".
# Its 512K comes out of the firmware region, leaving 1712K against 1185K for the largest build.
if(NOT DEFINED MICROPY_HW_ROMFS_BYTES)
    math(EXPR MICROPY_HW_ROMFS_BYTES "512 * 1024")
endif()
