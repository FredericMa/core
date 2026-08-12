"""Tests for the IR Candle light platform."""

from __future__ import annotations

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    DOMAIN as LIGHT_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .conftest import MockInfraredEntity
from .utils import check_availability_follows_ir_entity

from tests.common import MockConfigEntry, snapshot_platform

LIGHT_ENTITY_ID = "light.ir_candle"


@pytest.fixture
def platforms() -> list[Platform]:
    """Return platforms to set up."""
    return [Platform.LIGHT]


@pytest.mark.usefixtures("init_integration")
async def test_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the light entity is created with correct attributes."""
    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)

    # Verify entity belongs to the correct device
    device_entry = device_registry.async_get_device(
        identifiers={("ir_candle", mock_config_entry.entry_id)}
    )
    assert device_entry
    entity_entries = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )
    for entity_entry in entity_entries:
        assert entity_entry.device_id == device_entry.id


@pytest.mark.usefixtures("init_integration")
async def test_turn_on(
    hass: HomeAssistant,
    mock_infrared_entity: MockInfraredEntity,
) -> None:
    """Test turning on the candle sends the ON command."""
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: LIGHT_ENTITY_ID},
        blocking=True,
    )

    assert len(mock_infrared_entity.send_command_calls) == 1
    # The mock patches NECCommand to return just the command code
    assert mock_infrared_entity.send_command_calls[0] == 0xBA45


@pytest.mark.usefixtures("init_integration")
async def test_turn_off(
    hass: HomeAssistant,
    mock_infrared_entity: MockInfraredEntity,
) -> None:
    """Test turning off the candle sends the OFF command."""
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: LIGHT_ENTITY_ID},
        blocking=True,
    )

    assert len(mock_infrared_entity.send_command_calls) == 1
    assert mock_infrared_entity.send_command_calls[0] == 0xB847


@pytest.mark.usefixtures("init_integration")
async def test_turn_on_with_effect_candle(
    hass: HomeAssistant,
    mock_infrared_entity: MockInfraredEntity,
) -> None:
    """Test turning on with candle effect sends ON + candle mode commands."""
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: LIGHT_ENTITY_ID, ATTR_EFFECT: "candle"},
        blocking=True,
    )

    assert len(mock_infrared_entity.send_command_calls) == 2
    assert mock_infrared_entity.send_command_calls[0] == 0xBA45  # ON
    assert mock_infrared_entity.send_command_calls[1] == 0xF807  # CANDLE_MODE


@pytest.mark.usefixtures("init_integration")
async def test_turn_on_with_effect_light(
    hass: HomeAssistant,
    mock_infrared_entity: MockInfraredEntity,
) -> None:
    """Test turning on with light effect sends ON + light mode commands."""
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: LIGHT_ENTITY_ID, ATTR_EFFECT: "light"},
        blocking=True,
    )

    assert len(mock_infrared_entity.send_command_calls) == 2
    assert mock_infrared_entity.send_command_calls[0] == 0xBA45  # ON
    assert mock_infrared_entity.send_command_calls[1] == 0xF609  # LIGHT_MODE


@pytest.mark.usefixtures("init_integration")
async def test_turn_on_with_brightness(
    hass: HomeAssistant,
    mock_infrared_entity: MockInfraredEntity,
) -> None:
    """Test turning on with brightness sends ON + brightness commands."""
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: LIGHT_ENTITY_ID, ATTR_BRIGHTNESS: 128},
        blocking=True,
    )

    # ON command + brightness down steps (from 255 to 128 = ~3 steps of 32)
    assert mock_infrared_entity.send_command_calls[0] == 0xBA45  # ON
    # Remaining calls should be brightness down commands
    for call in mock_infrared_entity.send_command_calls[1:]:
        assert call == 0xE916  # BRIGHTNESS_DOWN


@pytest.mark.usefixtures("init_integration")
async def test_light_availability_follows_ir_entity(
    hass: HomeAssistant,
) -> None:
    """Test light becomes unavailable when IR entity is unavailable."""
    await check_availability_follows_ir_entity(hass, LIGHT_ENTITY_ID)
