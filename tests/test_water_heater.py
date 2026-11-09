"""Tests for the domestic hot water entity."""

import pytest

from homeassistant.components.water_heater import (
    ATTR_CURRENT_TEMPERATURE,
    ATTR_MAX_TEMP,
    ATTR_MIN_TEMP,
    ATTR_OPERATION_MODE,
    DOMAIN as WATER_HEATER_DOMAIN,
    SERVICE_SET_OPERATION_MODE,
    SERVICE_SET_TEMPERATURE,
    STATE_HEAT_PUMP,
    STATE_PERFORMANCE,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
)
from homeassistant.core import HomeAssistant

from .conftest import AIR2AIR, ALTHERMA_3, ALTHERMA_4, entity_id, make_entry, setup_entry


async def _call(hass: HomeAssistant, service: str, entity: str, **data) -> None:
    await hass.services.async_call(
        WATER_HEATER_DOMAIN, service, {ATTR_ENTITY_ID: entity, **data}, blocking=True
    )


@pytest.fixture
def altherma4_dhw(unit):
    """An Altherma 4 with hot water on and the booster off."""
    unit.coils[1] = True
    unit.set_holding(10, 50)
    unit.set_holding(13, 0)
    unit.set_input(43, 4800)
    return unit


async def test_state(hass: HomeAssistant, altherma4_dhw) -> None:
    """The water heater shows tank temperature, setpoint and mode."""
    await setup_entry(hass, make_entry(ALTHERMA_4))
    state = hass.states.get(entity_id(hass, "water_heater", "domestic_hot_water"))
    assert state.state == STATE_HEAT_PUMP
    assert state.attributes[ATTR_CURRENT_TEMPERATURE] == 48.0
    assert state.attributes[ATTR_TEMPERATURE] == 50
    assert state.attributes[ATTR_MIN_TEMP] == 30
    assert state.attributes[ATTR_MAX_TEMP] == 85


async def test_operation_modes(hass: HomeAssistant, altherma4_dhw) -> None:
    """Performance switches the booster; off switches the DHW coil."""
    unit = altherma4_dhw
    await setup_entry(hass, make_entry(ALTHERMA_4))
    heater = entity_id(hass, "water_heater", "domestic_hot_water")

    await _call(hass, SERVICE_SET_OPERATION_MODE, heater, operation_mode=STATE_PERFORMANCE)
    assert unit.writes == [("register", 12, 1)]
    assert hass.states.get(heater).state == STATE_PERFORMANCE

    unit.writes.clear()
    await _call(hass, SERVICE_SET_OPERATION_MODE, heater, operation_mode=STATE_OFF)
    assert unit.writes == [("coil", 0, False)]
    assert hass.states.get(heater).state == STATE_OFF

    unit.writes.clear()
    await _call(hass, SERVICE_SET_OPERATION_MODE, heater, operation_mode=STATE_HEAT_PUMP)
    assert unit.writes == [("coil", 0, True), ("register", 12, 0)]
    assert hass.states.get(heater).state == STATE_HEAT_PUMP


async def test_turn_on_off(hass: HomeAssistant, altherma4_dhw) -> None:
    """Turning off and on switches the DHW coil."""
    await setup_entry(hass, make_entry(ALTHERMA_4))
    heater = entity_id(hass, "water_heater", "domestic_hot_water")
    await _call(hass, SERVICE_TURN_OFF, heater)
    await _call(hass, SERVICE_TURN_ON, heater)
    assert altherma4_dhw.writes == [("coil", 0, False), ("coil", 0, True)]


async def test_set_temperature(hass: HomeAssistant, altherma4_dhw) -> None:
    """Setting a temperature writes the reheat setpoint."""
    await setup_entry(hass, make_entry(ALTHERMA_4))
    heater = entity_id(hass, "water_heater", "domestic_hot_water")
    await _call(hass, SERVICE_SET_TEMPERATURE, heater, temperature=52)
    assert altherma4_dhw.writes == [("register", 9, 52)]
    assert hass.states.get(heater).attributes[ATTR_TEMPERATURE] == 52


async def test_altherma3(hass: HomeAssistant, unit) -> None:
    """Altherma 3 switches hot water by register and caps the setpoint."""
    unit.set_holding(12, 0)
    unit.set_holding(10, 48)
    await setup_entry(hass, make_entry(ALTHERMA_3))
    heater = entity_id(hass, "water_heater", "domestic_hot_water")

    state = hass.states.get(heater)
    assert state.state == STATE_OFF
    assert state.attributes[ATTR_MAX_TEMP] == 55

    await _call(hass, SERVICE_TURN_ON, heater)
    assert unit.writes == [("register", 11, 1)]
    assert hass.states.get(heater).state == STATE_HEAT_PUMP


async def test_no_water_heater_for_air2air(hass: HomeAssistant, unit) -> None:
    """Air2Air units have no water heater entity."""
    await setup_entry(hass, make_entry(AIR2AIR))
    assert hass.states.async_entity_ids(WATER_HEATER_DOMAIN) == []
