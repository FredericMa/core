"""Constants for the Logitech Z-5500 IR integration."""

from enum import IntEnum

DOMAIN = "logitech_z5500_infrared"
CONF_INFRARED_ENTITY_ID = "infrared_entity_id"

Z5500_NEC_ADDRESS = 0xF708


class Z5500Code(IntEnum):
    """Logitech Z-5500 IR command codes (NEC protocol, address 0xF708).

    The Z-5500 uses the NEC IR protocol. ESPHome's NEC decoder reports
    16-bit values that combine each byte with its bitwise inverse:

    - address = addr_byte | (~addr_byte << 8) → 0xF708
    - command = cmd_byte  | (~cmd_byte  << 8) → e.g. 0xEF10 for POWER

    The ``infrared_protocols.NECCommand`` library accepts the 16-bit
    address directly (extended NEC mode) and 8-bit command values.
    The enum values below are the 8-bit command bytes.

    Derived from https://github.com/xens/logitech_Z5500/blob/master/ir_codes.md
    and verified against a physical Z-5500 remote using ESPHome's NEC receiver.
    """

    CENTER_DOWN = 0x06
    CENTER_UP = 0x02
    COAX = 0x0C
    DIRECT = 0x0A
    EFFECT = 0x1D
    MUTE = 0x16
    OPTICAL = 0x0B
    POWER = 0x10
    SETUP = 0x1F
    SUBWOOFER_DOWN = 0x01
    SUBWOOFER_UP = 0x03
    SURROUND_DOWN = 0x04
    SURROUND_UP = 0x00
    TEST = 0x05
    VOLUME_DOWN = 0x0E
    VOLUME_UP = 0x1A
