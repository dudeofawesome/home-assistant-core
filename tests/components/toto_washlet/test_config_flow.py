"""Tests for the TOTO Washlet config flow."""

from __future__ import annotations

import pytest

from homeassistant import config_entries
from homeassistant.components.infrared import (
    DATA_COMPONENT as INFRARED_DATA_COMPONENT,
    DOMAIN as INFRARED_DOMAIN,
)
from homeassistant.components.toto_washlet.const import CONF_INFRARED_ENTITY_ID, DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.setup import async_setup_component

from .conftest import MOCK_INFRARED_ENTITY_ID, MockInfraredEntity


async def test_form_no_emitters(hass: HomeAssistant) -> None:
    """Test config flow aborts when no infrared emitters are available."""
    assert await async_setup_component(hass, INFRARED_DOMAIN, {})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_emitters"


@pytest.mark.usefixtures("mock_setup_entry")
async def test_form(hass: HomeAssistant) -> None:
    """Test config flow creates an entry."""
    assert await async_setup_component(hass, INFRARED_DOMAIN, {})
    infrared_component = hass.data[INFRARED_DATA_COMPONENT]
    await infrared_component.async_add_entities([MockInfraredEntity("test_ir_transmitter")])

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_INFRARED_ENTITY_ID: MOCK_INFRARED_ENTITY_ID},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "TOTO Washlet via Test IR transmitter"
    assert result["data"] == {CONF_INFRARED_ENTITY_ID: MOCK_INFRARED_ENTITY_ID}
