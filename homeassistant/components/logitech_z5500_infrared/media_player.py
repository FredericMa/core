"""Media player platform for Logitech Z-5500 IR integration."""

from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_INFRARED_ENTITY_ID, Z5500Code
from .entity import LogitechZ5500IrEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Logitech Z-5500 IR media player from config entry."""
    infrared_entity_id = entry.data[CONF_INFRARED_ENTITY_ID]
    async_add_entities([LogitechZ5500IrMediaPlayer(entry, infrared_entity_id)])


class LogitechZ5500IrMediaPlayer(LogitechZ5500IrEntity, MediaPlayerEntity):
    """Logitech Z-5500 IR media player entity."""

    _attr_name = None
    _attr_assumed_state = True
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
    )

    def __init__(self, entry: ConfigEntry, infrared_entity_id: str) -> None:
        """Initialize Logitech Z-5500 IR media player."""
        super().__init__(entry, infrared_entity_id, unique_id_suffix="media_player")
        self._attr_state = MediaPlayerState.ON

    async def async_turn_on(self) -> None:
        """Turn on the speaker system."""
        await self._send_command(Z5500Code.POWER)

    async def async_turn_off(self) -> None:
        """Turn off the speaker system."""
        await self._send_command(Z5500Code.POWER)

    async def async_volume_up(self) -> None:
        """Send volume up command."""
        await self._send_command(Z5500Code.VOLUME_UP)

    async def async_volume_down(self) -> None:
        """Send volume down command."""
        await self._send_command(Z5500Code.VOLUME_DOWN)

    async def async_mute_volume(self, mute: bool) -> None:
        """Send mute command."""
        await self._send_command(Z5500Code.MUTE)
