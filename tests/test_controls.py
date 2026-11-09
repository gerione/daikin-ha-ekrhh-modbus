"""Tests for writing to the unit through numbers, selects and switches."""

import pytest

from homeassistant.components.number import (
    ATTR_MAX,
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.components.select import (
    ATTR_OPTION,
    DOMAIN as SELECT_DOMAIN,
    SERVICE_SELECT_OPTION,
)
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant

from .conftest import AIR2AIR, ALTHERMA_3, ALTHERMA_4, entity_id, make_entry, setup_entry


async def _set_number(hass: HomeAssistant, entity: str, value: float) -> None:
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: entity, ATTR_VALUE: value},
        blocking=True,
    )


@pytest.mark.parametrize(
    ("key", "value", "register", "payload"),
    [
        # TEMP16 setpoints are sent in 1/100 °C.
        ("altherma4_holding_76", 21.3, 75, 2130),
        ("altherma4_holding_16", 48.5, 15, 4850),
        # POW16 limits are sent in 1/100 kW, rounded rather than truncated.
        ("altherma4_holding_58", 2.3, 57, 230),
        # Negative INT16 offsets are sent as two's complement.
        ("altherma4_holding_54", -3, 53, 65533),
        ("altherma4_holding_1", 35, 0, 35),
    ],
)
async def test_number_writes(
    hass: HomeAssistant, unit, key, value, register, payload
) -> None:
    """Numbers encode their value for the register they write."""
    await setup_entry(hass, make_entry(ALTHERMA_4))
    await _set_number(hass, entity_id(hass, "number", key), value)
    assert unit.writes == [("register", register, payload)]


async def test_number_max_follows_options(hass: HomeAssistant, unit) -> None:
    """Configured maximum power and water temperature cap the numbers."""
    await setup_entry(hass, make_entry(ALTHERMA_3))
    dhw = hass.states.get(entity_id(hass, "number", "altherma3_holding_10"))
    power = hass.states.get(entity_id(hass, "number", "altherma3_holding_58"))
    room = hass.states.get(entity_id(hass, "number", "altherma3_holding_6"))
    assert dhw.attributes[ATTR_MAX] == 55
    assert power.attributes[ATTR_MAX] == 15
    assert room.attributes[ATTR_MAX] == 30


async def test_air2air_power_limit(hass: HomeAssistant, unit) -> None:
    """The Air2Air power limit shows the polled value and is capped."""
    unit.set_holding(1002, 250)
    await setup_entry(hass, make_entry(AIR2AIR))
    limit = entity_id(hass, "number", "Power_limit_for_Demand_Control", prefixed=False)
    state = hass.states.get(limit)
    assert state.state == "2.5"
    assert state.attributes[ATTR_MAX] == 15

    await _set_number(hass, limit, 4.2)
    assert unit.writes == [("register", 1001, 420)]


async def test_select_writes_option_index(hass: HomeAssistant, unit) -> None:
    """Selects show the polled option and write the option's index."""
    unit.set_holding(3, 1)
    await setup_entry(hass, make_entry(ALTHERMA_4))
    mode = entity_id(hass, "select", "altherma4_holding_3")
    assert hass.states.get(mode).state == "Heating"

    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: mode, ATTR_OPTION: "Cooling"},
        blocking=True,
    )
    assert unit.writes == [("register", 2, 2)]
    assert hass.states.get(mode).state == "Cooling"


async def test_switch_writes_coil(hass: HomeAssistant, unit) -> None:
    """Switches show and write their coil."""
    unit.coils[1] = False
    await setup_entry(hass, make_entry(ALTHERMA_4))
    dhw = entity_id(hass, "switch", "altherma4_coil_1")
    assert hass.states.get(dhw).state == STATE_OFF

    await hass.services.async_call(
        SWITCH_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: dhw}, blocking=True
    )
    assert unit.writes == [("coil", 0, True)]
    assert hass.states.get(dhw).state == STATE_ON

    await hass.services.async_call(
        SWITCH_DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: dhw}, blocking=True
    )
    assert unit.writes[-1] == ("coil", 0, False)
    assert hass.states.get(dhw).state == STATE_OFF


async def test_binary_sensor_state(hass: HomeAssistant, unit) -> None:
    """Binary sensors follow their register."""
    unit.set_input(31, 1)
    unit.discrete[11] = True
    await setup_entry(hass, make_entry(ALTHERMA_4))
    assert hass.states.get(entity_id(hass, "binary_sensor", "altherma4_input_31")).state == STATE_ON
    assert (
        hass.states.get(entity_id(hass, "binary_sensor", "altherma4_discrete_input_11")).state
        == STATE_ON
    )
    assert hass.states.get(entity_id(hass, "binary_sensor", "altherma4_input_30")).state == STATE_OFF
