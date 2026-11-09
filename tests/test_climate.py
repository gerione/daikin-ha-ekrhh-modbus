"""Tests for the main zone climate entity."""

import pytest
from modbus_connection import ModbusConnectionError

from homeassistant.components.climate import (
    ATTR_CURRENT_TEMPERATURE,
    ATTR_HVAC_MODE,
    ATTR_MAX_TEMP,
    ATTR_MIN_TEMP,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ATTR_TARGET_TEMP_STEP,
    DOMAIN as CLIMATE_DOMAIN,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_TEMPERATURE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    HVACMode,
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .conftest import AIR2AIR, ALTHERMA_3, ALTHERMA_4, entity_id, make_entry, setup_entry


async def _call(hass: HomeAssistant, service: str, entity: str, **data) -> None:
    await hass.services.async_call(
        CLIMATE_DOMAIN, service, {ATTR_ENTITY_ID: entity, **data}, blocking=True
    )


@pytest.fixture
def altherma4_heating(unit):
    """An Altherma 4 heating to a 21 °C room setpoint."""
    unit.set_holding(3, 1)  # Heating
    unit.set_holding(4, 1)  # On
    unit.set_holding(76, 2100)
    unit.set_holding(77, 2500)
    unit.set_input(50, 2050)
    unit.set_input(84, 1200)
    unit.set_input(85, 2800)
    unit.set_input(86, 1800)
    unit.set_input(87, 3000)
    return unit


async def test_room_thermostat_state(hass: HomeAssistant, altherma4_heating) -> None:
    """The climate entity shows room temperature and room setpoint."""
    await setup_entry(hass, make_entry(ALTHERMA_4))
    state = hass.states.get(entity_id(hass, "climate", "main_zone"))
    assert state.state == HVACMode.HEAT
    assert state.attributes[ATTR_CURRENT_TEMPERATURE] == 20.5
    assert state.attributes[ATTR_TEMPERATURE] == 21.0
    assert state.attributes[ATTR_MIN_TEMP] == 12.0
    assert state.attributes[ATTR_MAX_TEMP] == 28.0
    assert state.attributes[ATTR_TARGET_TEMP_STEP] == 0.1


async def test_set_room_temperature(hass: HomeAssistant, altherma4_heating) -> None:
    """Setting a temperature writes the room setpoint of the current mode."""
    await setup_entry(hass, make_entry(ALTHERMA_4))
    climate = entity_id(hass, "climate", "main_zone")

    await _call(hass, SERVICE_SET_TEMPERATURE, climate, temperature=21.5)
    assert altherma4_heating.writes == [("register", 75, 2150)]
    assert hass.states.get(climate).attributes[ATTR_TEMPERATURE] == 21.5


async def test_switch_modes(hass: HomeAssistant, altherma4_heating) -> None:
    """Modes write the operation mode and on/off registers as needed."""
    unit = altherma4_heating
    await setup_entry(hass, make_entry(ALTHERMA_4))
    climate = entity_id(hass, "climate", "main_zone")

    await _call(hass, SERVICE_SET_HVAC_MODE, climate, hvac_mode=HVACMode.COOL)
    assert unit.writes == [("register", 2, 2)]
    state = hass.states.get(climate)
    assert state.state == HVACMode.COOL
    assert state.attributes[ATTR_TEMPERATURE] == 25.0
    assert state.attributes[ATTR_MIN_TEMP] == 18.0

    unit.writes.clear()
    await _call(hass, SERVICE_SET_HVAC_MODE, climate, hvac_mode=HVACMode.OFF)
    assert unit.writes == [("register", 3, 0)]
    assert hass.states.get(climate).state == HVACMode.OFF

    unit.writes.clear()
    await _call(hass, SERVICE_TURN_ON, climate)
    assert unit.writes == [("register", 3, 1)]
    assert hass.states.get(climate).state == HVACMode.COOL

    unit.writes.clear()
    await _call(hass, SERVICE_TURN_OFF, climate)
    await _call(hass, SERVICE_SET_HVAC_MODE, climate, hvac_mode=HVACMode.HEAT)
    assert unit.writes == [("register", 3, 0), ("register", 2, 1), ("register", 3, 1)]
    assert hass.states.get(climate).state == HVACMode.HEAT


async def test_auto_uses_a_range(hass: HomeAssistant, altherma4_heating) -> None:
    """Daikin Auto shows and sets the heating and cooling setpoints as a range."""
    altherma4_heating.set_holding(3, 0)
    await setup_entry(hass, make_entry(ALTHERMA_4))
    climate = entity_id(hass, "climate", "main_zone")

    state = hass.states.get(climate)
    assert state.state == HVACMode.HEAT_COOL
    assert state.attributes[ATTR_TARGET_TEMP_LOW] == 21.0
    assert state.attributes[ATTR_TARGET_TEMP_HIGH] == 25.0
    assert state.attributes[ATTR_MIN_TEMP] == 12.0
    assert state.attributes[ATTR_MAX_TEMP] == 30.0

    await _call(
        hass,
        SERVICE_SET_TEMPERATURE,
        climate,
        target_temp_low=20,
        target_temp_high=24,
    )
    assert altherma4_heating.writes == [("register", 75, 2000), ("register", 76, 2400)]


async def test_leaving_water_control(hass: HomeAssistant, unit) -> None:
    """With leaving water control the entity uses the water setpoints."""
    unit.set_holding(3, 1)
    unit.set_holding(4, 1)
    unit.set_holding(1, 35)
    unit.set_input(40, 3400)
    unit.set_input(54, 2500)
    unit.set_input(55, 5500)
    await setup_entry(hass, make_entry(ALTHERMA_3, climate_control="leaving_water"))
    climate = entity_id(hass, "climate", "main_zone")

    state = hass.states.get(climate)
    assert state.attributes[ATTR_CURRENT_TEMPERATURE] == 34.0
    assert state.attributes[ATTR_TEMPERATURE] == 35
    assert state.attributes[ATTR_MIN_TEMP] == 25.0
    assert state.attributes[ATTR_MAX_TEMP] == 55.0
    assert state.attributes[ATTR_TARGET_TEMP_STEP] == 1

    await _call(hass, SERVICE_SET_TEMPERATURE, climate, temperature=40)
    assert unit.writes == [("register", 0, 40)]


async def test_altherma3_room_limits_from_table(hass: HomeAssistant, unit) -> None:
    """Without limit registers the register table limits apply."""
    unit.set_holding(3, 1)
    unit.set_holding(4, 1)
    unit.set_holding(6, 21)
    await setup_entry(hass, make_entry(ALTHERMA_3))
    state = hass.states.get(entity_id(hass, "climate", "main_zone"))
    assert state.attributes[ATTR_TEMPERATURE] == 21
    assert state.attributes[ATTR_MIN_TEMP] == 12
    assert state.attributes[ATTR_MAX_TEMP] == 30


async def test_set_temperature_and_mode(hass: HomeAssistant, altherma4_heating) -> None:
    """A mode passed with the temperature is applied first."""
    await setup_entry(hass, make_entry(ALTHERMA_4))
    climate = entity_id(hass, "climate", "main_zone")
    await _call(
        hass,
        SERVICE_SET_TEMPERATURE,
        climate,
        temperature=24,
        hvac_mode=HVACMode.COOL,
    )
    assert altherma4_heating.writes == [("register", 2, 2), ("register", 76, 2400)]


async def test_failed_write_raises(hass: HomeAssistant, altherma4_heating) -> None:
    """A write the unit does not accept is reported to the user."""
    await setup_entry(hass, make_entry(ALTHERMA_4))
    climate = entity_id(hass, "climate", "main_zone")
    altherma4_heating.error = ModbusConnectionError("unreachable")
    with pytest.raises(HomeAssistantError):
        await _call(hass, SERVICE_SET_TEMPERATURE, climate, temperature=22)


async def test_no_climate_for_air2air(hass: HomeAssistant, unit) -> None:
    """Air2Air units have no climate entity."""
    await setup_entry(hass, make_entry(AIR2AIR))
    assert hass.states.async_entity_ids(CLIMATE_DOMAIN) == []
