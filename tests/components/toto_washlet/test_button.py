"""Tests for the TOTO Washlet button platform."""

from __future__ import annotations

import pytest

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.components.toto_washlet.commands import TotoWashletCode
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .conftest import MockInfraredEntity

from tests.common import MockConfigEntry


@pytest.fixture
def platforms() -> list[Platform]:
    """Return platforms to set up."""
    return [Platform.BUTTON]


@pytest.mark.usefixtures("init_integration")
async def test_entities(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test all button entities are created with correct attributes."""
    entity_entries = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )
    assert len(entity_entries) == len(TotoWashletCode)

    device_entry = device_registry.async_get_device(
        identifiers={("toto_washlet", mock_config_entry.entry_id)}
    )
    assert device_entry
    for entity_entry in entity_entries:
        assert entity_entry.device_id == device_entry.id


@pytest.mark.parametrize(
    ("entity_id", "expected_code"),
    [
        ("button.toto_washlet_stop", TotoWashletCode.STOP),
        ("button.toto_washlet_rear_wash", TotoWashletCode.REAR),
        ("button.toto_washlet_user_1", TotoWashletCode.USER_1),
        ("button.toto_washlet_full_flush", TotoWashletCode.FULL_FLUSH),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_button_press_sends_correct_code(
    hass: HomeAssistant,
    mock_infrared_entity: MockInfraredEntity,
    entity_id: str,
    expected_code: TotoWashletCode,
) -> None:
    """Test pressing a button sends the correct IR code."""
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    assert len(mock_infrared_entity.send_command_calls) == 1
    command = mock_infrared_entity.send_command_calls[0]
    assert command.get_raw_timings() == expected_code.to_command().get_raw_timings()


@pytest.mark.usefixtures("init_integration")
async def test_button_availability_follows_ir_entity(hass: HomeAssistant) -> None:
    """Test button becomes unavailable when IR entity is unavailable."""
    entity_id = "button.toto_washlet_stop"
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state != "unavailable"

    hass.states.async_set("infrared.test_ir_transmitter", "unavailable")
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == "unavailable"
