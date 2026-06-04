"""Common entity for Logitech Z-5500 IR integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.infrared import async_send_command
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import Event, EventStateChangedData, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, Z5500_NEC_ADDRESS, Z5500Code

if TYPE_CHECKING:
    from infrared_protocols import Command as InfraredCommand

_LOGGER = logging.getLogger(__name__)


def make_z5500_command(code: Z5500Code, repeat_count: int = 0) -> InfraredCommand:
    """Get the NECCommand for a Logitech Z-5500 IR code."""
    from infrared_protocols import NECCommand  # noqa: PLC0415

    return NECCommand(
        address=Z5500_NEC_ADDRESS,
        command=code,
        modulation=38000,
        repeat_count=repeat_count,
    )


class LogitechZ5500IrEntity(Entity):
    """Logitech Z-5500 IR base entity."""

    _attr_has_entity_name = True

    def __init__(
        self, entry: ConfigEntry, infrared_entity_id: str, unique_id_suffix: str
    ) -> None:
        """Initialize Logitech Z-5500 IR entity."""
        self._infrared_entity_id = infrared_entity_id
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Logitech Z-5500",
            manufacturer="Logitech",
            model="Z-5500",
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

    async def _send_command(self, code: Z5500Code) -> None:
        """Send an IR command using the Logitech Z-5500 NEC protocol."""
        await async_send_command(
            self.hass,
            self._infrared_entity_id,
            make_z5500_command(code),
            context=self._context,
        )
