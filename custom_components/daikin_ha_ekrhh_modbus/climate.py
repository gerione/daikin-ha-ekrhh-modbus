"""Climate entity controlling the main heating zone."""

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, CONF_NAME, UnitOfTemperature
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CLIMATE_ENTITY,
    CLIMATE_REGISTERS,
    CONF_CLIMATE_CONTROL,
    DEFAULT_CLIMATE_CONTROL,
)
from .entity import DaikinEKRHHEntity, holding_info, register_key

# Values of the operation mode register; Daikin "Auto" switches between
# heating and cooling, keeping both setpoints.
MODE_TO_HVAC = {0: HVACMode.HEAT_COOL, 1: HVACMode.HEAT, 2: HVACMode.COOL}
HVAC_TO_MODE = {hvac: mode for mode, hvac in MODE_TO_HVAC.items()}


async def async_setup_entry(hass, entry, async_add_entities):
    hub = entry.runtime_data
    if hub._is_air2air:
        return True
    control = entry.data.get(CONF_CLIMATE_CONTROL, DEFAULT_CLIMATE_CONTROL)
    async_add_entities([DaikinEKRHHClimate(entry.data[CONF_NAME], hub, control)])
    return True


class _Setpoint:
    """A writable setpoint and the input registers holding its limits."""

    def __init__(self, version, register, limits):
        self.key = register_key(version, "holding", register)
        self.address = register - 1
        row = holding_info(self.key)
        self.format = row[3]
        self.step = row[6]["step"]
        self.default_limits = (row[6]["min"], row[6]["max"])
        self.limit_keys = (
            tuple(register_key(version, "input", r) for r in limits) if limits else None
        )


class DaikinEKRHHClimate(DaikinEKRHHEntity, ClimateEntity):
    """Main zone, controlled by either room or leaving water temperature."""

    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.HEAT_COOL,
    ]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, device_name, hub, control) -> None:
        """Initialize the climate entity."""
        super().__init__(device_name, hub, CLIMATE_ENTITY[1])
        version = hub.altherma_version
        registers = CLIMATE_REGISTERS[version]
        setpoints = registers[control]
        self._mode_key = register_key(version, "holding", registers["mode"])
        self._mode_address = registers["mode"] - 1
        self._power_key = register_key(version, "holding", registers["power"])
        self._power_address = registers["power"] - 1
        self._current_key = register_key(version, "input", setpoints["current"])
        self._setpoints = {
            HVACMode.HEAT: _Setpoint(
                version, setpoints["heat"], setpoints.get("heat_limits")
            ),
            HVACMode.COOL: _Setpoint(
                version, setpoints["cool"], setpoints.get("cool_limits")
            ),
        }
        self._attr_target_temperature_step = self._setpoints[HVACMode.HEAT].step

    def _value(self, key):
        return self._hub.data.get(key)

    @property
    def _operation(self) -> HVACMode | None:
        """Return the mode the unit runs in when switched on."""
        return MODE_TO_HVAC.get(self._value(self._mode_key))

    @property
    def hvac_mode(self) -> HVACMode | None:
        power = self._value(self._power_key)
        if power is None:
            return None
        if power == 0:
            return HVACMode.OFF
        return self._operation

    @property
    def supported_features(self) -> ClimateEntityFeature:
        features = ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF
        if self._operation == HVACMode.HEAT_COOL:
            return features | ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        return features | ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def current_temperature(self) -> float | None:
        return self._value(self._current_key)

    @property
    def target_temperature(self) -> float | None:
        if (operation := self._operation) in self._setpoints:
            return self._value(self._setpoints[operation].key)
        return None

    @property
    def target_temperature_low(self) -> float | None:
        if self._operation == HVACMode.HEAT_COOL:
            return self._value(self._setpoints[HVACMode.HEAT].key)
        return None

    @property
    def target_temperature_high(self) -> float | None:
        if self._operation == HVACMode.HEAT_COOL:
            return self._value(self._setpoints[HVACMode.COOL].key)
        return None

    def _limits(self) -> list[tuple[float, float]]:
        """Return the setpoint limits of the setpoints in use."""
        operation = self._operation
        modes = [operation] if operation in self._setpoints else list(self._setpoints)
        limits = []
        for mode in modes:
            setpoint = self._setpoints[mode]
            low, high = setpoint.default_limits
            if setpoint.limit_keys:
                reported_low, reported_high = map(self._value, setpoint.limit_keys)
                if reported_low is not None:
                    low = reported_low
                if reported_high is not None:
                    high = reported_high
            limits.append((low, high))
        return limits

    @property
    def min_temp(self) -> float:
        return min(low for low, _ in self._limits())

    @property
    def max_temp(self) -> float:
        return max(high for _, high in self._limits())

    async def _async_write(self, key, address, fmt, value) -> None:
        if not await self._hub.async_write_value(address, fmt, value):
            raise HomeAssistantError(f"Could not write {value} to the Daikin unit")
        self._hub.data[key] = value

    async def _async_write_setpoint(self, mode: HVACMode, value: float) -> None:
        setpoint = self._setpoints[mode]
        await self._async_write(setpoint.key, setpoint.address, setpoint.format, value)

    async def _async_set_power(self, on: bool) -> None:
        await self._async_write(
            self._power_key, self._power_address, "INT16", 1 if on else 0
        )

    async def _async_done(self) -> None:
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Switch the zone off, or on in the given mode."""
        if hvac_mode == HVACMode.OFF:
            await self._async_set_power(False)
        else:
            mode = HVAC_TO_MODE[hvac_mode]
            if self._value(self._mode_key) != mode:
                await self._async_write(
                    self._mode_key, self._mode_address, "INT16", mode
                )
            if self._value(self._power_key) != 1:
                await self._async_set_power(True)
        await self._async_done()

    async def async_turn_on(self) -> None:
        await self._async_set_power(True)
        await self._async_done()

    async def async_turn_off(self) -> None:
        await self._async_set_power(False)
        await self._async_done()

    async def async_set_temperature(self, **kwargs) -> None:
        """Set the setpoint of the current mode, or both in Auto."""
        if (hvac_mode := kwargs.get(ATTR_HVAC_MODE)) is not None:
            await self.async_set_hvac_mode(hvac_mode)
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            operation = self._operation
            mode = operation if operation in self._setpoints else HVACMode.HEAT
            await self._async_write_setpoint(mode, temperature)
        if (low := kwargs.get(ATTR_TARGET_TEMP_LOW)) is not None:
            await self._async_write_setpoint(HVACMode.HEAT, low)
        if (high := kwargs.get(ATTR_TARGET_TEMP_HIGH)) is not None:
            await self._async_write_setpoint(HVACMode.COOL, high)
        await self._async_done()
