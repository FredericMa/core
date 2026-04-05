"""Constants for the IR Candle integration."""

from typing import Final

DOMAIN: Final = "ir_candle"
CONF_INFRARED_ENTITY_ID: Final = "infrared_entity_id"

# NEC protocol address for the IR candles
NEC_ADDRESS: Final = 0xFF00

# NEC command codes harvested from the candle remote
NEC_CMD_ON: Final = 0xBA45
NEC_CMD_OFF: Final = 0xB847
NEC_CMD_TIMER_4H: Final = 0xBB44
NEC_CMD_TIMER_8H: Final = 0xBC43
NEC_CMD_CANDLE_MODE: Final = 0xF807
NEC_CMD_LIGHT_MODE: Final = 0xF609
NEC_CMD_BRIGHTNESS_DOWN: Final = 0xE916
NEC_CMD_BRIGHTNESS_UP: Final = 0xF20D
