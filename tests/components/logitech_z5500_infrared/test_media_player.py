"""Tests for the Logitech Z-5500 Infrared media player platform."""

from __future__ import annotations

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.logitech_z5500_infrared.const import Z5500Code
from homeassistant.components.media_player import (
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    SERVICE_VOLUME_DOWN,
    SERVICE_VOLUME_MUTE,
    SERVICE_VOLUME_UP,
)
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .conftest import MockInfraredEntity
from .utils import check_availability_follows_ir_entity

from tests.common import MockConfigEntry, snapshot_platform

MEDIA_PLAYER_ENTITY_ID = "media_player.logitech_z_5500"


@pytest.fixture
def platforms() -> list[Platform]:
    """Return platforms to set up."""
    return [Platform.MEDIA_PLAYER]


@pytest.mark.usefixtures("init_integration")
async def test_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the media player entity is created with correct attributes."""
    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)

    # Verify entity belongs to the correct device
    device_entry = device_registry.async_get_device(
        identifiers={("logitech_z5500_infrared", mock_config_entry.entry_id)}
    )
    assert device_entry
    entity_entries = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )
    for entity_entry in entity_entries:
        assert entity_entry.device_id == device_entry.id


@pytest.mark.parametrize(
    ("service", "service_data", "expected_code"),
    [
        (SERVICE_TURN_ON, {}, Z5500Code.POWER),
        (SERVICE_TURN_OFF, {}, Z5500Code.POWER),
        (SERVICE_VOLUME_UP, {}, Z5500Code.VOLUME_UP),
        (SERVICE_VOLUME_DOWN, {}, Z5500Code.VOLUME_DOWN),
        (SERVICE_VOLUME_MUTE, {"is_volume_muted": True}, Z5500Code.MUTE),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_media_player_action_sends_correct_code(
    hass: HomeAssistant,
    mock_infrared_entity: MockInfraredEntity,
    service: str,
    service_data: dict[str, bool],
    expected_code: Z5500Code,
) -> None:
    """Test each media player action sends the correct IR code."""
    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        service,
        {ATTR_ENTITY_ID: MEDIA_PLAYER_ENTITY_ID, **service_data},
        blocking=True,
    )

    assert len(mock_infrared_entity.send_command_calls) == 1
    assert mock_infrared_entity.send_command_calls[0] == expected_code


@pytest.mark.usefixtures("init_integration")
async def test_media_player_availability_follows_ir_entity(
    hass: HomeAssistant,
) -> None:
    """Test media player becomes unavailable when IR entity is unavailable."""
    await check_availability_follows_ir_entity(hass, MEDIA_PLAYER_ENTITY_ID)
