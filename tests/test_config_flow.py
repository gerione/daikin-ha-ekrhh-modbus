"""Tests for the config and options flows."""

from unittest.mock import patch

import pytest
from modbus_connection import ModbusConnectionError

from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.daikin_ha_ekrhh_modbus.const import (
    CONF_ADDITIONAL_ZONE,
    CONF_ALTHERMA_VERSION,
    CONF_MAX_POWER,
    CONF_MODBUS_ADDRESS,
    DOMAIN,
)

from .conftest import ALTHERMA_4, DEVICE_NAME, HOST, entry_data, make_entry, setup_entry

USER_INPUT = {
    CONF_NAME: DEVICE_NAME,
    CONF_HOST: HOST,
    CONF_PORT: 502,
    CONF_MODBUS_ADDRESS: 1,
    CONF_ALTHERMA_VERSION: ALTHERMA_4,
    CONF_ADDITIONAL_ZONE: False,
}


@pytest.fixture(autouse=True)
def skip_setup():
    """Keep the flow tests from setting the entry up."""
    with patch(
        "custom_components.daikin_ha_ekrhh_modbus.async_setup_entry",
        return_value=True,
    ):
        yield


async def _start(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    return result


@pytest.mark.parametrize("host", [HOST, "fd00::50", "heatpump.local"])
async def test_user_flow_creates_entry(hass: HomeAssistant, unit, host) -> None:
    """IPv4, IPv6 and host names are accepted once the unit answers."""
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_HOST: host}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == DEVICE_NAME
    assert result["data"][CONF_HOST] == host
    assert result["result"].unique_id == host
    assert result["result"].minor_version == 8


async def test_user_flow_rejects_invalid_host(hass: HomeAssistant, unit) -> None:
    """A host that is neither an IP address nor a host name is refused."""
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_HOST: "not a host"}
    )
    assert result["type"] is FlowResultType.FORM
    assert CONF_HOST in result["errors"]


async def test_user_flow_cannot_connect(hass: HomeAssistant, unit) -> None:
    """An unreachable unit shows an error, and the user can try again."""
    unit.error = ModbusConnectionError("unreachable")
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    unit.error = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_aborts_when_configured(hass: HomeAssistant, unit) -> None:
    """The same host cannot be added twice."""
    make_entry().add_to_hass(hass)
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow_updates_connection(hass: HomeAssistant, unit) -> None:
    """The options flow changes the entry data and keeps the device name."""
    entry = make_entry()
    await setup_entry(hass, entry)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM

    options = {k: v for k, v in entry_data().items() if k != CONF_NAME}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {**options, CONF_HOST: "192.168.1.60", CONF_MAX_POWER: 10}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.data[CONF_HOST] == "192.168.1.60"
    assert entry.data[CONF_MAX_POWER] == 10
    assert entry.data[CONF_NAME] == DEVICE_NAME


async def test_options_flow_cannot_connect(hass: HomeAssistant, unit) -> None:
    """The options flow does not save a connection that fails."""
    entry = make_entry()
    await setup_entry(hass, entry)

    unit.error = ModbusConnectionError("unreachable")
    result = await hass.config_entries.options.async_init(entry.entry_id)
    options = {k: v for k, v in entry_data().items() if k != CONF_NAME}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {**options, CONF_HOST: "192.168.1.60"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert entry.data[CONF_HOST] == HOST
