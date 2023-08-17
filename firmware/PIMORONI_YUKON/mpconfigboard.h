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

// Enable networking.
//#define MICROPY_PY_NETWORK 1
//#define MICROPY_PY_NETWORK_HOSTNAME_DEFAULT     "Yukon"

// CYW43 driver configuration.
//#define CYW43_USE_SPI (1)
//#define CYW43_LWIP (1)
//#define CYW43_GPIO (1)
//#define CYW43_SPI_PIO (1)

// For debugging mbedtls - also set
// Debug level (0-4) 1=warning, 2=info, 3=debug, 4=verbose
// #define MODUSSL_MBEDTLS_DEBUG_LEVEL 1

#define MICROPY_PY_TCA9555 (1)
#define MICROPY_HW_PIN_EXT_COUNT    (32)

//#define MICROPY_HW_PIN_RESERVED(i) ((i) == CYW43_PIN_WL_HOST_WAKE || (i) == CYW43_PIN_WL_REG_ON)

#define MICROPY_BOARD_EARLY_INIT board_init
void board_init(void);

#define MICROPY_BOARD_EARLY_RESET board_reset
void board_reset(void);