"""Light platform for IR Candle integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_INFRARED_ENTITY_ID,
    NEC_CMD_BRIGHTNESS_DOWN,
    NEC_CMD_BRIGHTNESS_UP,
    NEC_CMD_CANDLE_MODE,
    NEC_CMD_LIGHT_MODE,
    NEC_CMD_OFF,
    NEC_CMD_ON,
)
from .entity import IrCandleEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up IR Candle light from config entry."""
    infrared_entity_id = entry.data[CONF_INFRARED_ENTITY_ID]
    async_add_entities([IrCandleLight(entry, infrared_entity_id)])


class IrCandleLight(IrCandleEntity, LightEntity):
    """IR Candle light entity."""

    _attr_name = None
    _attr_assumed_state = True
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = ["candle", "light"]

    def __init__(self, entry: ConfigEntry, infrared_entity_id: str) -> None:
        """Initialize IR Candle light."""
        super().__init__(entry, infrared_entity_id, unique_id_suffix="light")
        self._attr_is_on = False
        self._attr_brightness = 255
        self._attr_effect = "candle"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the candle."""
        await self._send_command(NEC_CMD_ON)
        self._attr_is_on = True

        if ATTR_BRIGHTNESS in kwargs:
            target = kwargs[ATTR_BRIGHTNESS]
            current = self._attr_brightness or 255
            # Determine direction and number of steps
            # The candle has discrete brightness levels; we approximate
            # by sending multiple brightness up/down commands
            steps = abs(target - current) // 32
            if target > current:
                for _ in range(steps):
                    await self._send_command(NEC_CMD_BRIGHTNESS_UP)
            elif target < current:
                for _ in range(steps):
                    await self._send_command(NEC_CMD_BRIGHTNESS_DOWN)
            self._attr_brightness = target

        if "effect" in kwargs:
            effect = kwargs["effect"]
            if effect == "candle":
                await self._send_command(NEC_CMD_CANDLE_MODE)
            elif effect == "light":
                await self._send_command(NEC_CMD_LIGHT_MODE)
            self._attr_effect = effect

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the candle."""
        await self._send_command(NEC_CMD_OFF)
        self._attr_is_on = False
        self.async_write_ha_state()
