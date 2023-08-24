// This is a hack! Need to replace with upstream board definition.
#define MICROPY_HW_BOARD_NAME          "Pimoroni Yukon"
#define MICROPY_HW_FLASH_STORAGE_BYTES (15 * 1024 * 1024)

#define MICROPY_HW_USB_VID (0x2E8A)
#define MICROPY_HW_USB_PID (0x105B)

#define MICROPY_HW_SPI0_SCK (0)
#define MICROPY_HW_SPI0_MOSI (0)
#define MICROPY_HW_SPI0_MISO (0)

#define MICROPY_HW_I2C0_SDA (24)
#define MICROPY_HW_I2C0_SCL (25)

#define MICROPY_BOARD_EARLY_INIT board_init
void board_init(void);

#define MICROPY_BOARD_EARLY_RESET board_reset
void board_reset(void);