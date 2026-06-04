"""Button platform for Logitech Z-5500 IR integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_INFRARED_ENTITY_ID, Z5500Code
from .entity import LogitechZ5500IrEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class Z5500ButtonEntityDescription(ButtonEntityDescription):
    """Describes Logitech Z-5500 IR button entity."""

    command_code: Z5500Code


BUTTON_DESCRIPTIONS: tuple[Z5500ButtonEntityDescription, ...] = (
    Z5500ButtonEntityDescription(
        key="power", translation_key="power", command_code=Z5500Code.POWER
    ),
    Z5500ButtonEntityDescription(
        key="test", translation_key="test", command_code=Z5500Code.TEST
    ),
    Z5500ButtonEntityDescription(
        key="direct", translation_key="direct", command_code=Z5500Code.DIRECT
    ),
    Z5500ButtonEntityDescription(
        key="optical", translation_key="optical", command_code=Z5500Code.OPTICAL
    ),
    Z5500ButtonEntityDescription(
        key="coax", translation_key="coax", command_code=Z5500Code.COAX
    ),
    Z5500ButtonEntityDescription(
        key="effect", translation_key="effect", command_code=Z5500Code.EFFECT
    ),
    Z5500ButtonEntityDescription(
        key="setup", translation_key="setup", command_code=Z5500Code.SETUP
    ),
    Z5500ButtonEntityDescription(
        key="subwoofer_up",
        translation_key="subwoofer_up",
        command_code=Z5500Code.SUBWOOFER_UP,
    ),
    Z5500ButtonEntityDescription(
        key="subwoofer_down",
        translation_key="subwoofer_down",
        command_code=Z5500Code.SUBWOOFER_DOWN,
    ),
    Z5500ButtonEntityDescription(
        key="center_up",
        translation_key="center_up",
        command_code=Z5500Code.CENTER_UP,
    ),
    Z5500ButtonEntityDescription(
        key="center_down",
        translation_key="center_down",
        command_code=Z5500Code.CENTER_DOWN,
    ),
    Z5500ButtonEntityDescription(
        key="surround_up",
        translation_key="surround_up",
        command_code=Z5500Code.SURROUND_UP,
    ),
    Z5500ButtonEntityDescription(
        key="surround_down",
        translation_key="surround_down",
        command_code=Z5500Code.SURROUND_DOWN,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Logitech Z-5500 IR buttons from config entry."""
    infrared_entity_id = entry.data[CONF_INFRARED_ENTITY_ID]
    async_add_entities(
        Z5500IrButton(entry, infrared_entity_id, description)
        for description in BUTTON_DESCRIPTIONS
    )


class Z5500IrButton(LogitechZ5500IrEntity, ButtonEntity):
    """Logitech Z-5500 IR button entity."""

    entity_description: Z5500ButtonEntityDescription

    def __init__(
        self,
        entry: ConfigEntry,
        infrared_entity_id: str,
        description: Z5500ButtonEntityDescription,
    ) -> None:
        """Initialize Logitech Z-5500 IR button."""
        super().__init__(entry, infrared_entity_id, unique_id_suffix=description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Send the IR command."""
        await self._send_command(self.entity_description.command_code)
