"""Tests for the Logitech Z-5500 Infrared button platform."""

from __future__ import annotations

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.components.logitech_z5500_infrared.const import Z5500Code
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .conftest import MockInfraredEntity
from .utils import check_availability_follows_ir_entity

from tests.common import MockConfigEntry, snapshot_platform


@pytest.fixture
def platforms() -> list[Platform]:
    """Return platforms to set up."""
    return [Platform.BUTTON]


@pytest.mark.usefixtures("init_integration")
async def test_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test all button entities are created with correct attributes."""
    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)

    # Verify all entities belong to the same device
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
    ("entity_id", "expected_code"),
    [
        ("button.logitech_z_5500_power", Z5500Code.POWER),
        ("button.logitech_z_5500_test", Z5500Code.TEST),
        ("button.logitech_z_5500_direct", Z5500Code.DIRECT),
        ("button.logitech_z_5500_optical", Z5500Code.OPTICAL),
        ("button.logitech_z_5500_coaxial", Z5500Code.COAX),
        ("button.logitech_z_5500_effect", Z5500Code.EFFECT),
        ("button.logitech_z_5500_settings", Z5500Code.SETUP),
        ("button.logitech_z_5500_subwoofer_up", Z5500Code.SUBWOOFER_UP),
        ("button.logitech_z_5500_subwoofer_down", Z5500Code.SUBWOOFER_DOWN),
        ("button.logitech_z_5500_center_up", Z5500Code.CENTER_UP),
        ("button.logitech_z_5500_center_down", Z5500Code.CENTER_DOWN),
        ("button.logitech_z_5500_surround_up", Z5500Code.SURROUND_UP),
        ("button.logitech_z_5500_surround_down", Z5500Code.SURROUND_DOWN),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_button_press_sends_correct_code(
    hass: HomeAssistant,
    mock_infrared_entity: MockInfraredEntity,
    entity_id: str,
    expected_code: Z5500Code,
) -> None:
    """Test pressing a button sends the correct IR code."""
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    assert len(mock_infrared_entity.send_command_calls) == 1
    assert mock_infrared_entity.send_command_calls[0] == expected_code


@pytest.mark.usefixtures("init_integration")
async def test_button_availability_follows_ir_entity(
    hass: HomeAssistant,
) -> None:
    """Test button becomes unavailable when IR entity is unavailable."""
    entity_id = "button.logitech_z_5500_power"
    await check_availability_follows_ir_entity(hass, entity_id)
