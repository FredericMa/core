"""Button platform for IR Candle integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_INFRARED_ENTITY_ID,
    NEC_CMD_CANDLE_MODE,
    NEC_CMD_LIGHT_MODE,
    NEC_CMD_TIMER_4H,
    NEC_CMD_TIMER_8H,
)
from .entity import IrCandleEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class IrCandleButtonEntityDescription(ButtonEntityDescription):
    """Describes IR Candle button entity."""

    command_code: int


BUTTON_DESCRIPTIONS: tuple[IrCandleButtonEntityDescription, ...] = (
    IrCandleButtonEntityDescription(
        key="timer_4h",
        translation_key="timer_4h",
        command_code=NEC_CMD_TIMER_4H,
    ),
    IrCandleButtonEntityDescription(
        key="timer_8h",
        translation_key="timer_8h",
        command_code=NEC_CMD_TIMER_8H,
    ),
    IrCandleButtonEntityDescription(
        key="candle_mode",
        translation_key="candle_mode",
        command_code=NEC_CMD_CANDLE_MODE,
    ),
    IrCandleButtonEntityDescription(
        key="light_mode",
        translation_key="light_mode",
        command_code=NEC_CMD_LIGHT_MODE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up IR Candle buttons from config entry."""
    infrared_entity_id = entry.data[CONF_INFRARED_ENTITY_ID]
    async_add_entities(
        IrCandleButton(entry, infrared_entity_id, description)
        for description in BUTTON_DESCRIPTIONS
    )


class IrCandleButton(IrCandleEntity, ButtonEntity):
    """IR Candle button entity."""

    entity_description: IrCandleButtonEntityDescription

    def __init__(
        self,
        entry: ConfigEntry,
        infrared_entity_id: str,
        description: IrCandleButtonEntityDescription,
    ) -> None:
        """Initialize IR Candle button."""
        super().__init__(entry, infrared_entity_id, unique_id_suffix=description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Press the button."""
        await self._send_command(self.entity_description.command_code)
