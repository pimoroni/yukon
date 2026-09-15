// Bluetooth Classic discovery and HID host for MicroPython, on BTstack.
//
// The bluetooth module owns the stack, so the BLE object must be active before anything here is
// called. Results and reports are collected from BTstack events as they arrive and read back from
// Python. One HID connection at a time.

#include "py/runtime.h"
#include "py/objstr.h"

#include "btstack.h"
#include "classic/hid_host.h"
#include "classic/btstack_link_key_db_memory.h"

#define INQUIRY_MAX_RESULTS 8
#define INQUIRY_NAME_MAX 32
#define HID_DESCRIPTOR_STORAGE 512
#define HID_REPORT_MAX 64

typedef struct {
    bd_addr_t address;
    uint32_t class_of_device;
    uint8_t page_scan_repetition_mode;
    uint16_t clock_offset;
    int8_t rssi;
    bool rssi_available;
    bool name_available;
    char name[INQUIRY_NAME_MAX + 1];
} inquiry_result_t;

typedef enum {
    INQUIRY_IDLE,
    INQUIRY_SCANNING,
    INQUIRY_NAMING,
} inquiry_state_t;

// Values match the Python constants below.
typedef enum {
    HID_DISCONNECTED = 0,
    HID_CONNECTING = 1,
    HID_CONNECTED = 2,
    HID_FAILED = 3,
} hid_state_t;

static inquiry_result_t results[INQUIRY_MAX_RESULTS];
static uint8_t result_count = 0;
static inquiry_state_t inquiry_state = INQUIRY_IDLE;

static bool stack_hooked = false;
static btstack_packet_callback_registration_t hci_event_callback;

static uint8_t hid_descriptor_storage[HID_DESCRIPTOR_STORAGE];
static uint16_t hid_cid = 0;
static hid_state_t hid_state = HID_DISCONNECTED;
static uint8_t hid_status = 0;
static bool hid_descriptor_available = false;
static uint8_t hid_report[HID_REPORT_MAX];
static uint16_t hid_report_len = 0;
static uint32_t hid_report_count = 0;

// A pad put back into pairing mode forgets its link key while this side still holds one, so the
// first connect after that fails on security. The stale key is dropped and the connect retried once,
// from Python's polling for the same reason as the name lookups.
static bd_addr_t connect_address;
static bool connect_retried = false;
static bool connect_retry_pending = false;
// BTstack caches the key on its connection record too, so the ACL link has to drop before the
// retry, or the cached key answers the next request and fails again.
static hci_con_handle_t connect_handle = HCI_CON_HANDLE_INVALID;
static bool connect_retry_after_disconnect = false;

// Link keys live in BTstack's in-memory store and are lost at power off. Python reads them out
// with link_keys() after a pairing and puts them back with add_link_key() at start, so the file
// format and its location are a Python decision. This counts new keys so Python knows when to save.
static uint32_t link_key_notifications = 0;

// Name lookups are issued from Python's polling, not from inside the event handler, since a command
// requested while BTstack is dispatching an event may find it unable to send and is not retried.
static bool names_pending = false;
static bool names_wanted = false;
static bool inquiry_mode_pending = false;

static void request_next_name(void) {
    names_pending = false;
    for (uint8_t i = 0; i < result_count; ++i) {
        inquiry_result_t *result = &results[i];
        if (!result->name_available) {
            inquiry_state = INQUIRY_NAMING;
            int status = gap_remote_name_request(result->address, result->page_scan_repetition_mode, result->clock_offset | 0x8000);
            if (status != 0) {
                log_info("remote name request refused, status %d", status);
                names_pending = true;
            }
            return;
        }
    }
    inquiry_state = INQUIRY_IDLE;
}

static void store_name(inquiry_result_t *result, const uint8_t *name, size_t length) {
    if (length > INQUIRY_NAME_MAX) {
        length = INQUIRY_NAME_MAX;
    }
    memcpy(result->name, name, length);
    result->name[length] = '\0';
    result->name_available = true;
}

static void handle_inquiry_result(uint8_t *packet) {
    bd_addr_t address;
    gap_event_inquiry_result_get_bd_addr(packet, address);

    // One entry per address, the controller repeats them during an inquiry.
    for (uint8_t i = 0; i < result_count; ++i) {
        if (bd_addr_cmp(results[i].address, address) == 0) {
            return;
        }
    }
    if (result_count >= INQUIRY_MAX_RESULTS) {
        return;
    }

    inquiry_result_t *result = &results[result_count++];
    memcpy(result->address, address, sizeof(bd_addr_t));
    result->class_of_device = gap_event_inquiry_result_get_class_of_device(packet);
    result->page_scan_repetition_mode = gap_event_inquiry_result_get_page_scan_repetition_mode(packet);
    result->clock_offset = gap_event_inquiry_result_get_clock_offset(packet);
    result->rssi_available = gap_event_inquiry_result_get_rssi_available(packet);
    result->rssi = (int8_t)gap_event_inquiry_result_get_rssi(packet);
    result->name_available = false;
    result->name[0] = '\0';
    if (gap_event_inquiry_result_get_name_available(packet)) {
        store_name(result, gap_event_inquiry_result_get_name(packet), gap_event_inquiry_result_get_name_len(packet));
    }
}

static void handle_remote_name(uint8_t *packet) {
    bd_addr_t address;
    hci_event_remote_name_request_complete_get_bd_addr(packet, address);
    for (uint8_t i = 0; i < result_count; ++i) {
        inquiry_result_t *result = &results[i];
        if (bd_addr_cmp(result->address, address) == 0) {
            if (hci_event_remote_name_request_complete_get_status(packet) == ERROR_CODE_SUCCESS) {
                const char *name = hci_event_remote_name_request_complete_get_remote_name(packet);
                store_name(result, (const uint8_t *)name, strlen(name));
            } else {
                result->name_available = true;
            }
        }
    }
    names_pending = true;
}

static void handle_hid_event(uint8_t *packet) {
    switch (hci_event_hid_meta_get_subevent_code(packet)) {
        case HID_SUBEVENT_INCOMING_CONNECTION:
            hid_cid = hid_subevent_incoming_connection_get_hid_cid(packet);
            hid_state = HID_CONNECTING;
            hid_host_accept_connection(hid_cid, HID_PROTOCOL_MODE_REPORT);
            break;

        case HID_SUBEVENT_CONNECTION_OPENED:
            hid_status = hid_subevent_connection_opened_get_status(packet);
            if (hid_status == ERROR_CODE_SUCCESS) {
                hid_cid = hid_subevent_connection_opened_get_hid_cid(packet);
                hid_state = HID_CONNECTED;
            } else if (hid_status == L2CAP_CONNECTION_RESPONSE_RESULT_REFUSED_SECURITY && !connect_retried) {
                gap_drop_link_key_for_bd_addr(connect_address);
                connect_retried = true;
                hid_cid = 0;
                if (connect_handle != HCI_CON_HANDLE_INVALID) {
                    connect_retry_after_disconnect = true;
                    gap_disconnect(connect_handle);
                } else {
                    connect_retry_pending = true;
                }
            } else {
                hid_cid = 0;
                hid_state = HID_FAILED;
            }
            break;

        case HID_SUBEVENT_DESCRIPTOR_AVAILABLE:
            hid_descriptor_available = hid_subevent_descriptor_available_get_status(packet) == ERROR_CODE_SUCCESS;
            break;

        case HID_SUBEVENT_REPORT: {
            uint16_t length = hid_subevent_report_get_report_len(packet);
            if (length > HID_REPORT_MAX) {
                length = HID_REPORT_MAX;
            }
            memcpy(hid_report, hid_subevent_report_get_report(packet), length);
            hid_report_len = length;
            hid_report_count++;
            break;
        }

        case HID_SUBEVENT_CONNECTION_CLOSED:
            hid_cid = 0;
            hid_state = HID_DISCONNECTED;
            hid_descriptor_available = false;
            break;

        default:
            break;
    }
}

static void hci_event_handler(uint8_t packet_type, uint16_t channel, uint8_t *packet, uint16_t size) {
    (void)channel;
    (void)size;
    if (packet_type != HCI_EVENT_PACKET) {
        return;
    }

    switch (hci_event_packet_get_type(packet)) {
        case BTSTACK_EVENT_STATE:
            // The bluetooth module rebuilds the stack on deactivate and soft reset, dropping every
            // handler and setting, while these statics survive. Hook again on the next use.
            if (btstack_event_state_get_state(packet) != HCI_STATE_WORKING) {
                stack_hooked = false;
                inquiry_state = INQUIRY_IDLE;
                names_pending = false;
                hid_state = HID_DISCONNECTED;
                hid_cid = 0;
                hid_descriptor_available = false;
            }
            break;

        case GAP_EVENT_INQUIRY_RESULT:
            handle_inquiry_result(packet);
            break;

        case GAP_EVENT_INQUIRY_COMPLETE:
            if (names_wanted) {
                inquiry_state = INQUIRY_NAMING;
                names_pending = true;
            } else {
                inquiry_state = INQUIRY_IDLE;
            }
            break;

        case HCI_EVENT_REMOTE_NAME_REQUEST_COMPLETE:
            handle_remote_name(packet);
            break;

        case HCI_EVENT_LINK_KEY_NOTIFICATION:
            link_key_notifications++;
            break;

        case HCI_EVENT_CONNECTION_COMPLETE: {
            bd_addr_t address;
            hci_event_connection_complete_get_bd_addr(packet, address);
            if (hci_event_connection_complete_get_status(packet) == ERROR_CODE_SUCCESS && bd_addr_cmp(address, connect_address) == 0) {
                connect_handle = hci_event_connection_complete_get_connection_handle(packet);
            }
            break;
        }

        case HCI_EVENT_DISCONNECTION_COMPLETE:
            if (hci_event_disconnection_complete_get_connection_handle(packet) == connect_handle) {
                connect_handle = HCI_CON_HANDLE_INVALID;
                if (connect_retry_after_disconnect) {
                    connect_retry_after_disconnect = false;
                    connect_retry_pending = true;
                }
            }
            break;

        case HCI_EVENT_PIN_CODE_REQUEST: {
            // Legacy pairing, for devices without Secure Simple Pairing.
            bd_addr_t address;
            hci_event_pin_code_request_get_bd_addr(packet, address);
            gap_pin_code_response(address, "0000");
            break;
        }

        case HCI_EVENT_HID_META:
            handle_hid_event(packet);
            break;

        default:
            break;
    }
}

// Hook the running stack on first use. l2cap_init and sm_init are already done by the bluetooth module.
static void require_stack_working(void) {
    if (hci_get_state() != HCI_STATE_WORKING) {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Bluetooth is not active"));
    }
    if (stack_hooked) {
        return;
    }
    stack_hooked = true;

    // Results then carry RSSI and the extended inquiry response, which usually holds the name. Sent
    // first, while the stack is idle, since the settings below each take the single command credit.
    // Refused only if a command is in flight, and then inquiry_start retries.
    inquiry_mode_pending = hci_send_cmd(&hci_write_inquiry_mode, INQUIRY_MODE_RSSI_AND_EIR) != ERROR_CODE_SUCCESS;

    hci_set_link_key_db(btstack_link_key_db_memory_instance());
    gap_ssp_set_io_capability(SSP_IO_CAPABILITY_NO_INPUT_NO_OUTPUT);
    gap_ssp_set_auto_accept(1);
    gap_set_bondable_mode(1);

    hid_host_init(hid_descriptor_storage, sizeof(hid_descriptor_storage));
    hid_host_register_packet_handler(&hci_event_handler);

    // Pads ask for sniff mode and may want to be master.
    gap_set_default_link_policy_settings(LM_LINK_POLICY_ENABLE_SNIFF_MODE | LM_LINK_POLICY_ENABLE_ROLE_SWITCH);
    hci_set_master_slave_policy(HCI_ROLE_MASTER);

    hci_event_callback.callback = &hci_event_handler;
    hci_add_event_handler(&hci_event_callback);
}

static void address_from_obj(mp_obj_t obj, bd_addr_t address) {
    mp_buffer_info_t buffer;
    mp_get_buffer_raise(obj, &buffer, MP_BUFFER_READ);
    if (buffer.len != sizeof(bd_addr_t)) {
        mp_raise_ValueError(MP_ERROR_TEXT("address must be 6 bytes"));
    }
    memcpy(address, buffer.buf, sizeof(bd_addr_t));
}

// Start an inquiry lasting duration_s seconds. With names true, a remote name request follows for
// anything found without one, which pages the device and can take seconds per entry.
static mp_obj_t btclassic_inquiry_start(size_t n_args, const mp_obj_t *args) {
    require_stack_working();
    if (inquiry_state != INQUIRY_IDLE) {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("inquiry already running"));
    }

    mp_float_t duration_s = n_args > 0 ? mp_obj_get_float(args[0]) : 5.0f;
    names_wanted = n_args > 1 ? mp_obj_is_true(args[1]) : false;
    int duration_units = (int)(duration_s / 1.28f + 0.5f);
    if (duration_units < 1 || duration_units > 0x30) {
        mp_raise_ValueError(MP_ERROR_TEXT("duration must be 1.28 to 61.44 seconds"));
    }

    // The bluetooth module still has commands in flight just after activation, so give the credit
    // up to half a second to come free. The inquiry then queues behind this command.
    for (int waited_ms = 0; inquiry_mode_pending && waited_ms < 500; waited_ms += 5) {
        if (hci_can_send_command_packet_now()) {
            hci_send_cmd(&hci_write_inquiry_mode, INQUIRY_MODE_RSSI_AND_EIR);
            inquiry_mode_pending = false;
        } else {
            mp_event_wait_ms(5);
        }
    }

    result_count = 0;
    inquiry_state = INQUIRY_SCANNING;
    int status = gap_inquiry_start((uint8_t)duration_units);
    if (status != ERROR_CODE_SUCCESS) {
        inquiry_state = INQUIRY_IDLE;
        mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("inquiry failed to start, status %d"), status);
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(btclassic_inquiry_start_obj, 0, 2, btclassic_inquiry_start);

// Whether an inquiry, or the name lookups that follow it, is still in progress.
static mp_obj_t btclassic_inquiry_active(void) {
    if (names_pending) {
        request_next_name();
    }
    return mp_obj_new_bool(inquiry_state != INQUIRY_IDLE);
}
static MP_DEFINE_CONST_FUN_OBJ_0(btclassic_inquiry_active_obj, btclassic_inquiry_active);

// The devices found so far, as (address, class_of_device, rssi, name) tuples.
static mp_obj_t btclassic_inquiry_results(void) {
    mp_obj_t list = mp_obj_new_list(0, NULL);
    for (uint8_t i = 0; i < result_count; ++i) {
        inquiry_result_t *result = &results[i];
        mp_obj_t items[4] = {
            mp_obj_new_bytes(result->address, sizeof(bd_addr_t)),
            mp_obj_new_int_from_uint(result->class_of_device),
            result->rssi_available ? mp_obj_new_int(result->rssi) : mp_const_none,
            result->name[0] != '\0' ? mp_obj_new_str(result->name, strlen(result->name)) : mp_const_none,
        };
        mp_obj_list_append(list, mp_obj_new_tuple(4, items));
    }
    return list;
}
static MP_DEFINE_CONST_FUN_OBJ_0(btclassic_inquiry_results_obj, btclassic_inquiry_results);

// Open a HID connection to the device at address, pairing on the way if the device asks.
static mp_obj_t btclassic_connect(mp_obj_t address_obj) {
    require_stack_working();
    if (hid_state == HID_CONNECTING || hid_state == HID_CONNECTED) {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("already connected"));
    }

    address_from_obj(address_obj, connect_address);
    connect_retried = false;
    connect_retry_pending = false;
    connect_retry_after_disconnect = false;
    connect_handle = HCI_CON_HANDLE_INVALID;

    hid_state = HID_CONNECTING;
    hid_status = 0;
    hid_descriptor_available = false;
    hid_report_len = 0;
    uint8_t status = hid_host_connect(connect_address, HID_PROTOCOL_MODE_REPORT, &hid_cid);
    if (status != ERROR_CODE_SUCCESS) {
        hid_state = HID_FAILED;
        hid_status = status;
        mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("connect failed to start, status %d"), status);
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(btclassic_connect_obj, btclassic_connect);

static mp_obj_t btclassic_disconnect(void) {
    if (hid_cid != 0) {
        hid_host_disconnect(hid_cid);
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(btclassic_disconnect_obj, btclassic_disconnect);

// The connection state, one of the STATE_ constants, and the last BTstack status code.
static mp_obj_t btclassic_state(void) {
    if (connect_retry_pending) {
        connect_retry_pending = false;
        uint8_t status = hid_host_connect(connect_address, HID_PROTOCOL_MODE_REPORT, &hid_cid);
        if (status != ERROR_CODE_SUCCESS) {
            hid_status = status;
            hid_state = HID_FAILED;
        }
    }
    mp_obj_t items[2] = { mp_obj_new_int(hid_state), mp_obj_new_int(hid_status) };
    return mp_obj_new_tuple(2, items);
}
static MP_DEFINE_CONST_FUN_OBJ_0(btclassic_state_obj, btclassic_state);

// The most recent input report as raw bytes, with a count of reports received, or None before the first.
static mp_obj_t btclassic_report(void) {
    if (hid_report_len == 0) {
        return mp_const_none;
    }
    mp_obj_t items[2] = { mp_obj_new_int_from_uint(hid_report_count), mp_obj_new_bytes(hid_report, hid_report_len) };
    return mp_obj_new_tuple(2, items);
}
static MP_DEFINE_CONST_FUN_OBJ_0(btclassic_report_obj, btclassic_report);

// The device's HID report descriptor, or None until the connection has fetched it.
static mp_obj_t btclassic_descriptor(void) {
    if (!hid_descriptor_available || hid_cid == 0) {
        return mp_const_none;
    }
    return mp_obj_new_bytes(hid_descriptor_storage_get_descriptor_data(hid_cid), hid_descriptor_storage_get_descriptor_len(hid_cid));
}
static MP_DEFINE_CONST_FUN_OBJ_0(btclassic_descriptor_obj, btclassic_descriptor);

// The stored link keys as (address, key, type) tuples, and a count of keys received since power on.
static mp_obj_t btclassic_link_keys(void) {
    require_stack_working();
    mp_obj_t list = mp_obj_new_list(0, NULL);
    btstack_link_key_iterator_t it;
    if (gap_link_key_iterator_init(&it)) {
        bd_addr_t address;
        link_key_t key;
        link_key_type_t type;
        while (gap_link_key_iterator_get_next(&it, address, key, &type)) {
            mp_obj_t items[3] = {
                mp_obj_new_bytes(address, sizeof(bd_addr_t)),
                mp_obj_new_bytes(key, LINK_KEY_LEN),
                mp_obj_new_int(type),
            };
            mp_obj_list_append(list, mp_obj_new_tuple(3, items));
        }
        gap_link_key_iterator_done(&it);
    }
    mp_obj_t result[2] = { mp_obj_new_int_from_uint(link_key_notifications), list };
    return mp_obj_new_tuple(2, result);
}
static MP_DEFINE_CONST_FUN_OBJ_0(btclassic_link_keys_obj, btclassic_link_keys);

// Store a link key for address, as returned by link_keys() on an earlier run.
static mp_obj_t btclassic_add_link_key(mp_obj_t address_obj, mp_obj_t key_obj, mp_obj_t type_obj) {
    require_stack_working();
    bd_addr_t address;
    address_from_obj(address_obj, address);
    mp_buffer_info_t key;
    mp_get_buffer_raise(key_obj, &key, MP_BUFFER_READ);
    if (key.len != LINK_KEY_LEN) {
        mp_raise_ValueError(MP_ERROR_TEXT("key must be 16 bytes"));
    }
    link_key_t link_key;
    memcpy(link_key, key.buf, LINK_KEY_LEN);
    gap_store_link_key_for_bd_addr(address, link_key, (link_key_type_t)mp_obj_get_int(type_obj));
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_3(btclassic_add_link_key_obj, btclassic_add_link_key);

// Forget the link key for address, so the next connect pairs afresh.
static mp_obj_t btclassic_drop_link_key(mp_obj_t address_obj) {
    require_stack_working();
    bd_addr_t address;
    address_from_obj(address_obj, address);
    gap_drop_link_key_for_bd_addr(address);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(btclassic_drop_link_key_obj, btclassic_drop_link_key);

static const mp_rom_map_elem_t btclassic_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR_link_keys), MP_ROM_PTR(&btclassic_link_keys_obj) },
    { MP_ROM_QSTR(MP_QSTR_add_link_key), MP_ROM_PTR(&btclassic_add_link_key_obj) },
    { MP_ROM_QSTR(MP_QSTR_drop_link_key), MP_ROM_PTR(&btclassic_drop_link_key_obj) },
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_btclassic) },
    { MP_ROM_QSTR(MP_QSTR_inquiry_start), MP_ROM_PTR(&btclassic_inquiry_start_obj) },
    { MP_ROM_QSTR(MP_QSTR_inquiry_active), MP_ROM_PTR(&btclassic_inquiry_active_obj) },
    { MP_ROM_QSTR(MP_QSTR_inquiry_results), MP_ROM_PTR(&btclassic_inquiry_results_obj) },
    { MP_ROM_QSTR(MP_QSTR_connect), MP_ROM_PTR(&btclassic_connect_obj) },
    { MP_ROM_QSTR(MP_QSTR_disconnect), MP_ROM_PTR(&btclassic_disconnect_obj) },
    { MP_ROM_QSTR(MP_QSTR_state), MP_ROM_PTR(&btclassic_state_obj) },
    { MP_ROM_QSTR(MP_QSTR_report), MP_ROM_PTR(&btclassic_report_obj) },
    { MP_ROM_QSTR(MP_QSTR_descriptor), MP_ROM_PTR(&btclassic_descriptor_obj) },
    { MP_ROM_QSTR(MP_QSTR_STATE_DISCONNECTED), MP_ROM_INT(HID_DISCONNECTED) },
    { MP_ROM_QSTR(MP_QSTR_STATE_CONNECTING), MP_ROM_INT(HID_CONNECTING) },
    { MP_ROM_QSTR(MP_QSTR_STATE_CONNECTED), MP_ROM_INT(HID_CONNECTED) },
    { MP_ROM_QSTR(MP_QSTR_STATE_FAILED), MP_ROM_INT(HID_FAILED) },
};
static MP_DEFINE_CONST_DICT(btclassic_module_globals, btclassic_module_globals_table);

const mp_obj_module_t btclassic_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&btclassic_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_btclassic, btclassic_user_cmodule);
