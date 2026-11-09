"""Water heater entity controlling domestic hot water."""

from homeassistant.components.water_heater import (
    STATE_HEAT_PUMP,
    STATE_PERFORMANCE,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import ATTR_TEMPERATURE, CONF_NAME, STATE_OFF, UnitOfTemperature
from homeassistant.exceptions import HomeAssistantError

from .const import WATER_HEATER_ENTITY, WATER_HEATER_REGISTERS
from .entity import DaikinEKRHHEntity, holding_info, limited_max, register_key


async def async_setup_entry(hass, entry, async_add_entities):
    hub = entry.runtime_data
    if hub._is_air2air:
        return True
    async_add_entities(
        [DaikinEKRHHWaterHeater(entry.data[CONF_NAME], hub, entry.data)]
    )
    return True


class DaikinEKRHHWaterHeater(DaikinEKRHHEntity, WaterHeaterEntity):
    """Domestic hot water tank; the booster is the performance mode."""

    _attr_operation_list = [STATE_OFF, STATE_HEAT_PUMP, STATE_PERFORMANCE]
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.ON_OFF
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, device_name, hub, entry_data) -> None:
        """Initialize the water heater."""
        super().__init__(device_name, hub, WATER_HEATER_ENTITY[1])
        version = hub.altherma_version
        registers = WATER_HEATER_REGISTERS[version]
        self._current_key = register_key(version, "input", registers["current"])

        self._target_key = register_key(version, "holding", registers["target"])
        self._target_address = registers["target"] - 1
        # Same limits as the reheat setpoint number entity.
        row = holding_info(self._target_key)
        self._target_format = row[3]
        self._attr_min_temp = row[6]["min"]
        self._attr_max_temp = limited_max(entry_data, self._target_key, row[6]["max"])

        power_kind, power_register = registers["power"]
        self._power_is_coil = power_kind == "coil"
        self._power_key = register_key(version, power_kind, power_register)
        self._power_address = power_register - 1
        self._boost_key = register_key(version, "holding", registers["boost"])
        self._boost_address = registers["boost"] - 1

    def _value(self, key):
        return self._hub.data.get(key)

    @property
    def current_temperature(self) -> float | None:
        return self._value(self._current_key)

    @property
    def target_temperature(self) -> float | None:
        return self._value(self._target_key)

    @property
    def current_operation(self) -> str | None:
        power = self._value(self._power_key)
        if power is None:
            return None
        if not power:
            return STATE_OFF
        if self._value(self._boost_key) == 1:
            return STATE_PERFORMANCE
        return STATE_HEAT_PUMP

    async def _async_set_power(self, on: bool) -> None:
        if self._power_is_coil:
            written = await self._hub.async_write_coil(self._power_address, on)
            value = on
        else:
            value = 1 if on else 0
            written = await self._hub.async_write_value(
                self._power_address, "INT16", value
            )
        if not written:
            raise HomeAssistantError("Could not switch domestic hot water")
        self._hub.data[self._power_key] = value

    async def _async_set_boost(self, on: bool) -> None:
        value = 1 if on else 0
        if not await self._hub.async_write_value(self._boost_address, "INT16", value):
            raise HomeAssistantError("Could not switch the domestic hot water booster")
        self._hub.data[self._boost_key] = value

    async def _async_done(self) -> None:
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Switch off, or heat with or without the booster."""
        if operation_mode == STATE_OFF:
            await self._async_set_power(False)
        else:
            if not self._value(self._power_key):
                await self._async_set_power(True)
            boost = operation_mode == STATE_PERFORMANCE
            if self._value(self._boost_key) != (1 if boost else 0):
                await self._async_set_boost(boost)
        await self._async_done()

    async def async_turn_on(self, **kwargs) -> None:
        await self._async_set_power(True)
        await self._async_done()

    async def async_turn_off(self, **kwargs) -> None:
        await self._async_set_power(False)
        await self._async_done()

    async def async_set_temperature(self, **kwargs) -> None:
        """Set the reheat setpoint."""
        temperature = kwargs[ATTR_TEMPERATURE]
        if not await self._hub.async_write_value(
            self._target_address, self._target_format, temperature
        ):
            raise HomeAssistantError(
                f"Could not write {temperature} to the Daikin unit"
            )
        self._hub.data[self._target_key] = temperature
        await self._async_done()
