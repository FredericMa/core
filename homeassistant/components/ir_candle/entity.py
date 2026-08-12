"""Common entity for IR Candle integration."""

import logging

import infrared_protocols

from homeassistant.components.infrared import async_send_command
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import Event, EventStateChangedData, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, NEC_ADDRESS

_LOGGER = logging.getLogger(__name__)


class IrCandleEntity(Entity):
    """IR Candle base entity."""

    _attr_has_entity_name = True

    def __init__(
        self, entry: ConfigEntry, infrared_entity_id: str, unique_id_suffix: str
    ) -> None:
        """Initialize IR Candle entity."""
        self._infrared_entity_id = infrared_entity_id
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="IR Candle",
            manufacturer="Generic",
            model="Battery IR Candle",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to infrared entity state changes."""
        await super().async_added_to_hass()

        @callback
        def _async_ir_state_changed(event: Event[EventStateChangedData]) -> None:
            """Handle infrared entity state changes."""
            new_state = event.data["new_state"]
            ir_available = (
                new_state is not None and new_state.state != STATE_UNAVAILABLE
            )
            if ir_available != self.available:
                _LOGGER.info(
                    "Infrared entity %s used by %s is %s",
                    self._infrared_entity_id,
                    self.entity_id,
                    "available" if ir_available else "unavailable",
                )

                self._attr_available = ir_available
                self.async_write_ha_state()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._infrared_entity_id], _async_ir_state_changed
            )
        )

        # Set initial availability based on current infrared entity state
        ir_state = self.hass.states.get(self._infrared_entity_id)
        self._attr_available = (
            ir_state is not None and ir_state.state != STATE_UNAVAILABLE
        )

    async def _send_command(self, command_code: int) -> None:
        """Send an IR command using the NEC protocol."""
        command = infrared_protocols.NECCommand(
            address=NEC_ADDRESS,
            command=command_code,
            modulation=38000,
        )
        await async_send_command(
            self.hass,
            self._infrared_entity_id,
            command,
            context=self._context,
        )
