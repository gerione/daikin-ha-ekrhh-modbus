"""Tests for setting up, unloading and migrating config entries."""

import pytest
from modbus_connection import ModbusConnectionError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component

from custom_components.daikin_ha_ekrhh_modbus.const import (
    CONF_ALTHERMA_VERSION,
    CONF_CLIMATE_CONTROL,
    CONF_ISAIR2AIR,
    CONF_MAX_POWER,
    CONF_MAX_WATER_TEMP,
    CONF_MODBUS_ADDRESS,
    DOMAIN,
)

from .conftest import (
    AIR2AIR,
    ALTHERMA_3,
    ALTHERMA_4,
    DEVICE_NAME,
    HOST,
    make_entry,
    setup_entry,
)


async def test_async_setup(hass: HomeAssistant) -> None:
    """Test the component gets setup."""
    assert await async_setup_component(hass, DOMAIN, {}) is True


@pytest.mark.parametrize(
    ("version", "additional_zone", "expected"),
    [
        (
            ALTHERMA_3,
            False,
            {
                "sensor": 18,
                "binary_sensor": 9,
                "number": 9,
                "select": 8,
                "climate": 1,
                "water_heater": 1,
            },
        ),
        (
            ALTHERMA_3,
            True,
            {
                "sensor": 22,
                "binary_sensor": 9,
                "number": 13,
                "select": 10,
                "climate": 1,
                "water_heater": 1,
            },
        ),
        (
            ALTHERMA_4,
            False,
            {
                "sensor": 39,
                "binary_sensor": 36,
                "number": 10,
                "select": 10,
                "switch": 4,
                "climate": 1,
                "water_heater": 1,
            },
        ),
        (
            ALTHERMA_4,
            True,
            {
                "sensor": 45,
                "binary_sensor": 37,
                "number": 16,
                "select": 11,
                "switch": 5,
                "climate": 1,
                "water_heater": 1,
            },
        ),
        (AIR2AIR, False, {"sensor": 2, "number": 1, "select": 1}),
    ],
)
async def test_setup_and_unload(
    hass: HomeAssistant, unit, version, additional_zone, expected
) -> None:
    """Each heat pump type creates its entities and unloads cleanly."""
    entry = make_entry(version, additional_zone)
    await setup_entry(hass, entry)
    assert entry.state is ConfigEntryState.LOADED

    entities = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    counts: dict[str, int] = {}
    for entity in entities:
        counts[entity.domain] = counts.get(entity.domain, 0) + 1
    assert counts == expected

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_retries_when_unreachable(hass: HomeAssistant, unit) -> None:
    """A unit that does not answer makes Home Assistant retry later."""
    unit.error = ModbusConnectionError("unreachable")
    entry = make_entry()
    await setup_entry(hass, entry)
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_migrate_power_limit_unique_id(hass: HomeAssistant, unit) -> None:
    """The Air2Air power limit keeps its entity when its unique ID is fixed."""
    entry = make_entry(AIR2AIR, minor_version=6)
    entry.add_to_hass(hass)
    registry = er.async_get(hass)
    old = registry.async_get_or_create(
        "number",
        DOMAIN,
        f"{DEVICE_NAME}_ Power_limit_for_Demand_Control",
        config_entry=entry,
        suggested_object_id="daikin_power_limit_for_demand_control",
    )

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.minor_version == 8
    migrated = registry.async_get(old.entity_id)
    assert migrated.unique_id == f"{DEVICE_NAME}_Power_limit_for_Demand_Control"
    assert (
        registry.async_get_entity_id(
            "number", DOMAIN, f"{DEVICE_NAME}_ Power_limit_for_Demand_Control"
        )
        is None
    )


async def test_migrate_oldest_entry(hass: HomeAssistant, unit) -> None:
    """An entry from version 1.1 gains every option added since."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=DEVICE_NAME,
        unique_id=HOST,
        version=1,
        minor_version=1,
        data={
            CONF_NAME: DEVICE_NAME,
            CONF_HOST: HOST,
            CONF_PORT: 502,
            CONF_SCAN_INTERVAL: 30,
            "additional_zone": False,
        },
    )
    await setup_entry(hass, entry)

    assert entry.state is ConfigEntryState.LOADED
    assert entry.minor_version == 8
    assert entry.data[CONF_ISAIR2AIR] is False
    assert entry.data[CONF_MAX_POWER] == 20
    assert entry.data[CONF_MAX_WATER_TEMP] == 60
    assert entry.data[CONF_ALTHERMA_VERSION] == ALTHERMA_3
    assert entry.data[CONF_MODBUS_ADDRESS] == 1
    assert entry.data[CONF_CLIMATE_CONTROL] == "room_thermostat"


async def test_migrate_refuses_future_version(hass: HomeAssistant, unit) -> None:
    """An entry written by a newer version of the integration is not touched."""
    entry = make_entry(ALTHERMA_4, entry_version=2)
    await setup_entry(hass, entry)
    assert entry.state is ConfigEntryState.MIGRATION_ERROR
