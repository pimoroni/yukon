#include "mpconfigboard.h"
#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "tca9555.h"

void board_init() {
    // Isolate every slot pad, before anything has a chance to claim one. At its
    // reset value a pad has its pull-down enabled, which faintly lights an LED
    // wired with its cathode to the pin.
    for (int i = 0; i < 24; ++i) {
        gpio_init(i);
        hw_clear_bits(&pads_bank0_hw->io[i], PADS_BANK0_GPIO0_IE_BITS |
            PADS_BANK0_GPIO0_PUE_BITS |
            PADS_BANK0_GPIO0_PDE_BITS);
        hw_set_bits(&pads_bank0_hw->io[i], PADS_BANK0_GPIO0_OD_BITS);
    }

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
    board_init();
}
