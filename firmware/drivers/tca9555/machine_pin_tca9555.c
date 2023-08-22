/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2016-2022 Damien P. George
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <stdio.h>
#include <string.h>

#include "py/runtime.h"
#include "py/mphal.h"

#if defined(MICROPY_PY_TCA9555) && defined(MICROPY_HW_PIN_EXT_COUNT)

#include "modmachine.h"
#include "machine_pin.h"
#include "../../drivers/tca9555/tca9555.h"

void machine_pin_ext_init(void) {
    // Read the state of each IO expander pin, as some are initialised as outputs
    const mp_map_t *named_map = &pin_board_pins_locals_dict.map;
    for (uint i = 0; i < named_map->used; i++) {
        machine_pin_obj_t *pin = (machine_pin_obj_t *)named_map->table[i].value;
         if(pin->is_ext) {
            pin->last_output_value = tca_gpio_get_output(pin->id);
            pin->is_output = tca_gpio_get_config(pin->id);
        }
    }
}

void machine_pin_ext_set(machine_pin_obj_t *self, bool value) {
    tca_gpio_set_output(self->id, value);
    tca_gpio_set_config(self->id, true);  // Set to output (even if we already think it is)
    self->last_output_value = value;
    self->is_output = true;
}

bool machine_pin_ext_get(machine_pin_obj_t *self) {
    bool value;
    if (self->is_output) {
        value = tca_gpio_get_output(self->id);
    } else {
        value = tca_gpio_get_input(self->id);
    }
    return value;
}

void machine_pin_ext_config(machine_pin_obj_t *self, int mode, int value) {
    if (mode == MACHINE_PIN_MODE_IN) {
        if (value != -1) {
            // figure if you pass a value to IN it should still remember it (this is what regular GPIO does)
            tca_gpio_set_output(self->id, value);
            self->last_output_value = value;
        }
        tca_gpio_set_config(self->id, false);  // Set to input (even if we already think it is)
        self->is_output = false;
    } else if (mode == MACHINE_PIN_MODE_OUT) {
        if (value == -1) {
            value = self->last_output_value;
        }
        machine_pin_ext_set(self, value);
    } else {
        mp_raise_ValueError("only Pin.OUT and Pin.IN are supported for this pin");
    }
}

#endif // defined(MICROPY_PY_TCA9555) && defined(MICROPY_HW_PIN_EXT_COUNT)
