"""Common fixtures for the IR Candle tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import patch

from infrared_protocols import Command as InfraredCommand
import pytest

from homeassistant.components.infrared import (
    DATA_COMPONENT as INFRARED_DATA_COMPONENT,
    DOMAIN as INFRARED_DOMAIN,
    InfraredEntity,
)
from homeassistant.components.ir_candle import PLATFORMS
from homeassistant.components.ir_candle.const import CONF_INFRARED_ENTITY_ID, DOMAIN
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry

MOCK_INFRARED_ENTITY_ID = "infrared.test_ir_transmitter"


class MockInfraredEntity(InfraredEntity):
    """Mock infrared entity for testing."""

    _attr_has_entity_name = True
    _attr_name = "Test IR transmitter"

    def __init__(self, unique_id: str) -> None:
        """Initialize mock entity."""
        self._attr_unique_id = unique_id
        self.send_command_calls: list[InfraredCommand] = []

    async def async_send_command(self, command: InfraredCommand) -> None:
        """Mock send command."""
        self.send_command_calls.append(command)


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        entry_id="01JTEST0000000000000000000",
        title="IR Candle via Test IR transmitter",
        data={
            CONF_INFRARED_ENTITY_ID: MOCK_INFRARED_ENTITY_ID,
        },
        unique_id=f"ir_candle_{MOCK_INFRARED_ENTITY_ID}",
    )


@pytest.fixture
def mock_infrared_entity() -> MockInfraredEntity:
    """Return a mock infrared entity."""
    return MockInfraredEntity("test_ir_transmitter")


@pytest.fixture
def platforms() -> list[Platform]:
    """Return platforms to set up."""
    return PLATFORMS


@pytest.fixture
def mock_send_command() -> Generator[None]:
    """Patch _send_command to capture the raw command code.

    This allows tests to assert on the high-level NEC command code integer
    rather than the full NECCommand object.
    """
    with patch(
        "homeassistant.components.ir_candle.entity.infrared_protocols.NECCommand",
        side_effect=lambda address, command, modulation: command,
    ):
        yield


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_infrared_entity: MockInfraredEntity,
    mock_send_command: None,
    platforms: list[Platform],
) -> MockConfigEntry:
    """Set up the IR Candle integration for testing."""
    assert await async_setup_component(hass, INFRARED_DOMAIN, {})
    await hass.async_block_till_done()

    infrared_component = hass.data[INFRARED_DATA_COMPONENT]
    await infrared_component.async_add_entities([mock_infrared_entity])

    mock_config_entry.add_to_hass(hass)

    with patch("homeassistant.components.ir_candle.PLATFORMS", platforms):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    return mock_config_entry
