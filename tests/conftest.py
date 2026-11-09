"""Fixtures for the Daikin EKRHH Modbus tests."""

from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.daikin_ha_ekrhh_modbus.const import (
    CONF_ADDITIONAL_ZONE,
    CONF_ALTHERMA_VERSION,
    CONF_CLIMATE_CONTROL,
    CONF_MAX_POWER,
    CONF_MAX_WATER_TEMP,
    CONF_MODBUS_ADDRESS,
    DOMAIN,
)

ALTHERMA_3 = "Altherma 3 (EKRHH)"
ALTHERMA_4 = "Altherma 4"
AIR2AIR = "Air2Air (EKRHH)"

DEVICE_NAME = "daikin"
HOST = "192.168.1.50"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow Home Assistant to load the integration under test."""
    yield


class FakeModbusUnit:
    """A Modbus unit serving register values from memory and recording writes.

    Values are stored by the 1-based register numbers used in const.py.
    """

    def __init__(self) -> None:
        self.holding: dict[int, int] = {}
        self.input: dict[int, int] = {}
        self.coils: dict[int, bool] = {}
        self.discrete: dict[int, bool] = {}
        self.writes: list[tuple[str, int, int | bool]] = []
        self.error: Exception | None = None

    def set_input(self, register: int, value: int) -> None:
        """Store a signed value the way the device sends it."""
        self.input[register] = value & 0xFFFF

    def set_holding(self, register: int, value: int) -> None:
        """Store a signed value the way the device sends it."""
        self.holding[register] = value & 0xFFFF

    def _read(self, table, address, count, default):
        if self.error:
            raise self.error
        return [table.get(address + 1 + i, default) for i in range(count)]

    async def read_holding_registers(self, address, count):
        return self._read(self.holding, address, count, 0)

    async def read_input_registers(self, address, count):
        return self._read(self.input, address, count, 0)

    async def read_coils(self, address, count):
        return self._read(self.coils, address, count, False)

    async def read_discrete_inputs(self, address, count):
        return self._read(self.discrete, address, count, False)

    async def write_register(self, address, value):
        if self.error:
            raise self.error
        self.writes.append(("register", address, value))
        self.holding[address + 1] = value

    async def write_coil(self, address, value):
        if self.error:
            raise self.error
        self.writes.append(("coil", address, value))
        self.coils[address + 1] = value


@pytest.fixture
def unit() -> FakeModbusUnit:
    """Serve the fake unit to both setup and the config flow."""
    fake = FakeModbusUnit()
    # Sub code 32766 means "no sub code", which a healthy unit reports.
    fake.set_input(23, 32766)

    @asynccontextmanager
    async def temporary_unit(hass, params, unit_id):
        yield fake

    with (
        patch(
            "custom_components.daikin_ha_ekrhh_modbus.async_get_unit",
            return_value=fake,
        ),
        patch(
            "custom_components.daikin_ha_ekrhh_modbus.config_flow.async_get_temporary_unit",
            temporary_unit,
        ),
    ):
        yield fake


def entry_data(
    version: str = ALTHERMA_4,
    additional_zone: bool = False,
    climate_control: str = "room_thermostat",
) -> dict:
    """Return config entry data as the config flow stores it."""
    return {
        CONF_NAME: DEVICE_NAME,
        CONF_HOST: HOST,
        CONF_PORT: 502,
        CONF_MODBUS_ADDRESS: 1,
        CONF_ALTHERMA_VERSION: version,
        CONF_ADDITIONAL_ZONE: additional_zone,
        CONF_CLIMATE_CONTROL: climate_control,
        CONF_SCAN_INTERVAL: 30,
        CONF_MAX_POWER: 15,
        CONF_MAX_WATER_TEMP: 55,
    }


def make_entry(
    version: str = ALTHERMA_4,
    additional_zone: bool = False,
    climate_control: str = "room_thermostat",
    **kwargs,
) -> MockConfigEntry:
    """Create a config entry for the given heat pump type."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=DEVICE_NAME,
        unique_id=HOST,
        data=entry_data(version, additional_zone, climate_control),
        version=kwargs.pop("entry_version", 1),
        minor_version=kwargs.pop("minor_version", 8),
        **kwargs,
    )


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Add the entry to Home Assistant and set it up."""
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def refresh(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Poll the unit once and let entities update."""
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()


def entity_id(hass: HomeAssistant, platform: str, key: str, prefixed=True) -> str:
    """Look up an entity by its register key, e.g. "altherma4_input_44".

    The Air2Air keys carry no domain prefix; pass prefixed=False for those.
    """
    if prefixed:
        key = f"{DOMAIN}_{key}"
    found = er.async_get(hass).async_get_entity_id(
        platform, DOMAIN, f"{DEVICE_NAME}_{key}"
    )
    assert found, f"no {platform} entity for {key}"
    return found
