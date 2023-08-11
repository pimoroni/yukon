#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "drivers/tca9555/tca9555.h"

void board_init() {
    gpio_init(8);
    gpio_set_dir(8, GPIO_OUT);
    gpio_put(8, true);
    configure_i2c();
    gpio_put(8, false);

    gpio_init(9);
    gpio_set_dir(9, GPIO_OUT);
    gpio_put(9, true);
    sleep_us(100);
    gpio_put(9, false);
    sleep_us(10);
    gpio_put(9, true);
    // Set the first IO expander's initial state
    tca_set_output_port(0, 0x0000);
    tca_set_polarity_port(0, 0x0000);
    tca_set_config_port(0, 0x07BF);

    // Set the second IO expander's initial state
    tca_set_output_port(1, 0x0000);
    tca_set_polarity_port(1, 0x0000);
    tca_set_config_port(1, 0xFCE6);
    sleep_us(100);
    gpio_put(9, false);
}

void board_reset(void) {
    for (int i = 0; i < 24; ++i) {
        gpio_init(i);
        hw_clear_bits(&padsbank0_hw->io[i], PADS_BANK0_GPIO0_IE_BITS |
            PADS_BANK0_GPIO0_PUE_BITS |
            PADS_BANK0_GPIO0_PDE_BITS);
        hw_set_bits(&padsbank0_hw->io[i], PADS_BANK0_GPIO0_OD_BITS);
    }

    // Set the first IO expander's initial state
    tca_set_output_port(0, 0x0000);
    tca_set_polarity_port(0, 0x0000);
    tca_set_config_port(0, 0x07BF);

    // Set the second IO expander's initial state
    tca_set_output_port(1, 0x0000);
    tca_set_polarity_port(1, 0x0000);
    tca_set_config_port(1, 0xFCE6);
}
