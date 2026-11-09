"""Tests for decoding polled values into sensor states."""

from modbus_connection import ModbusConnectionError

from homeassistant.components.sensor import ATTR_STATE_CLASS, SensorStateClass
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant

from .conftest import AIR2AIR, ALTHERMA_3, ALTHERMA_4, entity_id, make_entry, refresh, setup_entry


def _text(code: str) -> int:
    """Encode a two letter code the way register 22 holds it."""
    return ord(code[0]) << 8 | ord(code[1])


async def test_altherma4_units_and_scaling(hass: HomeAssistant, unit) -> None:
    """Altherma 4 sensors report their unit, device class and scaling."""
    unit.set_input(44, -550)
    unit.set_input(49, 18)
    unit.set_input(51, 123)
    unit.set_input(79, 2)
    unit.set_input(68, 40)
    await setup_entry(hass, make_entry(ALTHERMA_4))

    outside = hass.states.get(entity_id(hass, "sensor", "altherma4_input_44"))
    assert outside.state == "-5.5"
    assert outside.attributes[ATTR_UNIT_OF_MEASUREMENT] == "°C"
    assert outside.attributes[ATTR_DEVICE_CLASS] == "temperature"
    assert outside.attributes[ATTR_STATE_CLASS] == SensorStateClass.MEASUREMENT

    flow = hass.states.get(entity_id(hass, "sensor", "altherma4_input_49"))
    assert flow.state == "18"
    assert flow.attributes[ATTR_UNIT_OF_MEASUREMENT] == "L/min"
    assert flow.attributes[ATTR_DEVICE_CLASS] == "volume_flow_rate"

    power = hass.states.get(entity_id(hass, "sensor", "altherma4_input_51"))
    assert power.state == "1.23"
    assert power.attributes[ATTR_UNIT_OF_MEASUREMENT] == "kW"
    assert power.attributes[ATTR_DEVICE_CLASS] == "power"

    pressure = hass.states.get(entity_id(hass, "sensor", "altherma4_input_79"))
    assert pressure.state == "2"
    assert pressure.attributes[ATTR_UNIT_OF_MEASUREMENT] == "bar"
    assert pressure.attributes[ATTR_DEVICE_CLASS] == "pressure"

    pump = hass.states.get(entity_id(hass, "sensor", "altherma4_input_68"))
    assert pump.state == "40"
    assert pump.attributes[ATTR_UNIT_OF_MEASUREMENT] == "%"


async def test_altherma3_flow_rate_scaling(hass: HomeAssistant, unit) -> None:
    """Altherma 3 reports the flow rate in 1/100 L/min."""
    unit.set_input(49, 1850)
    await setup_entry(hass, make_entry(ALTHERMA_3))
    flow = hass.states.get(entity_id(hass, "sensor", "altherma3_input_49"))
    assert flow.state == "18.5"


async def test_status_values_are_not_measurements(hass: HomeAssistant, unit) -> None:
    """Codes and texts get no state class, so they keep no statistics."""
    unit.set_input(22, _text("7H"))
    await setup_entry(hass, make_entry(ALTHERMA_4))
    for key in ("altherma4_input_21", "altherma4_input_22", "fault_code"):
        state = hass.states.get(entity_id(hass, "sensor", key))
        assert ATTR_STATE_CLASS not in state.attributes, key


async def test_fault_keeps_values_available(hass: HomeAssistant, unit) -> None:
    """A unit fault is decoded and the other sensors keep reporting."""
    unit.set_input(21, 1)
    unit.set_input(22, _text("7H"))
    unit.set_input(23, 19)
    unit.set_input(40, 2150)
    await setup_entry(hass, make_entry(ALTHERMA_4))

    assert hass.states.get(entity_id(hass, "sensor", "fault_code")).state == "7H-19"
    leaving = hass.states.get(entity_id(hass, "sensor", "altherma4_input_40"))
    assert leaving.state == "21.5"


async def test_fault_cleared(hass: HomeAssistant, unit) -> None:
    """The fault sensor shows when the unit has no error."""
    unit.set_input(21, 1)
    unit.set_input(22, _text("7H"))
    unit.set_input(23, 19)
    entry = make_entry(ALTHERMA_4)
    await setup_entry(hass, entry)

    unit.set_input(21, 0)
    unit.set_input(22, 0)
    unit.set_input(23, 32766)
    await refresh(hass, entry)
    assert hass.states.get(entity_id(hass, "sensor", "fault_code")).state == "No error"


async def test_fault_without_sub_code(hass: HomeAssistant, unit) -> None:
    """A warning without a sub code shows the code alone."""
    unit.set_input(21, 2)
    unit.set_input(22, _text("U4"))
    await setup_entry(hass, make_entry(ALTHERMA_3))
    assert hass.states.get(entity_id(hass, "sensor", "fault_code")).state == "U4"


async def test_unsupported_register_unavailable(hass: HomeAssistant, unit) -> None:
    """Registers reporting 32765 or 32767 are unavailable until they recover."""
    unit.set_input(44, 32767)
    unit.set_input(43, 32765)
    entry = make_entry(ALTHERMA_4)
    await setup_entry(hass, entry)
    outside = entity_id(hass, "sensor", "altherma4_input_44")
    dhw = entity_id(hass, "sensor", "altherma4_input_43")
    assert hass.states.get(outside).state == STATE_UNAVAILABLE
    assert hass.states.get(dhw).state == STATE_UNAVAILABLE

    unit.set_input(44, 1000)
    await refresh(hass, entry)
    assert hass.states.get(outside).state == "10.0"
    assert hass.states.get(dhw).state == STATE_UNAVAILABLE


async def test_failed_poll_makes_entities_unavailable(hass: HomeAssistant, unit) -> None:
    """Values are not shown as current while the unit does not answer."""
    unit.set_input(44, 1000)
    entry = make_entry(ALTHERMA_4)
    await setup_entry(hass, entry)
    outside = entity_id(hass, "sensor", "altherma4_input_44")
    assert hass.states.get(outside).state == "10.0"

    unit.error = ModbusConnectionError("unreachable")
    await refresh(hass, entry)
    assert hass.states.get(outside).state == STATE_UNAVAILABLE

    unit.error = None
    await refresh(hass, entry)
    assert hass.states.get(outside).state == "10.0"


async def test_air2air_sensors(hass: HomeAssistant, unit) -> None:
    """Air2Air units report their smart grid mode and power limit."""
    unit.set_holding(1001, 2)
    unit.set_holding(1002, 250)
    await setup_entry(hass, make_entry(AIR2AIR))
    mode = entity_id(hass, "sensor", "A2A_Smart_Grid_operation_mode", prefixed=False)
    limit = entity_id(hass, "sensor", "Power_limit_for_Demand_Control", prefixed=False)
    assert hass.states.get(mode).state == "2"
    assert hass.states.get(limit).state == "2.5"
