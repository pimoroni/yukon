#include "mpconfigboard.h"
#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "tca9555.h"

void board_init() {
    // Set the first IO expander's initial state
    tca_set_output_port(0, 0x8800);  // Disable the two ADC Muxes
    tca_set_polarity_port(0, 0x0000);
    tca_set_config_port(0, 0x07BF);

    // Set the second IO expander's initial state
    tca_set_output_port(1, 0x0000);
    tca_set_polarity_port(1, 0x0000);
    tca_set_config_port(1, 0xFCE6);
}

void board_reset(void) {
    for (int i = 0; i < 16; ++i) {
        gpio_init(i);
        hw_clear_bits(&padsbank0_hw->io[i], PADS_BANK0_GPIO0_IE_BITS |
            PADS_BANK0_GPIO0_PUE_BITS |
            PADS_BANK0_GPIO0_PDE_BITS);
        hw_set_bits(&padsbank0_hw->io[i], PADS_BANK0_GPIO0_OD_BITS);
    }

    // Skip over SLOT 5

    for (int i = 20; i < 24; ++i) {
        gpio_init(i);
        hw_clear_bits(&padsbank0_hw->io[i], PADS_BANK0_GPIO0_IE_BITS |
            PADS_BANK0_GPIO0_PUE_BITS |
            PADS_BANK0_GPIO0_PDE_BITS);
        hw_set_bits(&padsbank0_hw->io[i], PADS_BANK0_GPIO0_OD_BITS);
    }

    board_init();
}
