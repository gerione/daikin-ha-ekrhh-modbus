"""Climate entities controlling the main zone and the leaving water offsets."""

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
    CONF_ADDITIONAL_ZONE,
    CONF_CLIMATE_CONTROL,
    DEFAULT_ADDITIONAL_ZONE,
    DEFAULT_CLIMATE_CONTROL,
    OFFSET_CLIMATE_ADDITIONAL,
    OFFSET_CLIMATE_MAIN,
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
    name = entry.data[CONF_NAME]
    # Only the climate entity of the configured control type is created, so the
    # room thermostat one is absent when the zone runs on leaving water.
    control = entry.data.get(CONF_CLIMATE_CONTROL, DEFAULT_CLIMATE_CONTROL)
    entities = [
        DaikinEKRHHClimate(name, hub, control),
        DaikinEKRHHOffsetClimate(name, hub, OFFSET_CLIMATE_MAIN),
    ]
    if entry.data.get(CONF_ADDITIONAL_ZONE, DEFAULT_ADDITIONAL_ZONE):
        entities.append(DaikinEKRHHOffsetClimate(name, hub, OFFSET_CLIMATE_ADDITIONAL))
    async_add_entities(entities)
    return True


class _Setpoint:
    """A writable setpoint and the input registers holding its limits."""

    def __init__(self, version, register, limits=None):
        self.key = register_key(version, "holding", register)
        self.address = register - 1
        row = holding_info(self.key)
        self.format = row[3]
        self.step = row[6]["step"]
        self.default_limits = (row[6]["min"], row[6]["max"])
        self.limit_keys = (
            tuple(register_key(version, "input", r) for r in limits) if limits else None
        )


class _ZoneClimate(DaikinEKRHHEntity, ClimateEntity):
    """A pair of heating and cooling setpoints following the unit's mode."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, device_name, hub, key, heat, cool, current=None) -> None:
        """Initialize from the heating and cooling setpoints."""
        super().__init__(device_name, hub, key)
        version = hub.altherma_version
        registers = CLIMATE_REGISTERS[version]
        self._mode_key = register_key(version, "holding", registers["mode"])
        self._mode_address = registers["mode"] - 1
        self._power_key = register_key(version, "holding", registers["power"])
        self._power_address = registers["power"] - 1
        self._current_key = (
            register_key(version, "input", current) if current is not None else None
        )
        self._setpoints = {HVACMode.HEAT: heat, HVACMode.COOL: cool}
        self._attr_target_temperature_step = heat.step

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
    def _temperature_feature(self) -> ClimateEntityFeature:
        if self._operation == HVACMode.HEAT_COOL:
            return ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def current_temperature(self) -> float | None:
        if self._current_key is None:
            return None
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

    async def _async_done(self) -> None:
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

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


class DaikinEKRHHClimate(_ZoneClimate):
    """Main zone, controlled by either room or leaving water temperature."""

    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.HEAT_COOL,
    ]

    def __init__(self, device_name, hub, control) -> None:
        """Initialize the climate entity."""
        version = hub.altherma_version
        setpoints = CLIMATE_REGISTERS[version][control]
        super().__init__(
            device_name,
            hub,
            CLIMATE_ENTITY[1],
            _Setpoint(version, setpoints["heat"], setpoints.get("heat_limits")),
            _Setpoint(version, setpoints["cool"], setpoints.get("cool_limits")),
            setpoints["current"],
        )

    @property
    def supported_features(self) -> ClimateEntityFeature:
        return (
            ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
            | self._temperature_feature
        )

    async def _async_set_power(self, on: bool) -> None:
        await self._async_write(
            self._power_key, self._power_address, "INT16", 1 if on else 0
        )

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


class DaikinEKRHHOffsetClimate(_ZoneClimate):
    """Weather dependent leaving water setpoint offset of a zone.

    Shows the unit's mode but leaves switching it to the main zone entity, so
    adjusting an offset never turns space heating on or off.
    """

    def __init__(self, device_name, hub, entity) -> None:
        """Initialize from an OFFSET_CLIMATE_* row."""
        _, key, heat, cool = entity
        version = hub.altherma_version
        super().__init__(
            device_name,
            hub,
            key,
            _Setpoint(version, heat),
            _Setpoint(version, cool),
        )
        self._attr_icon = "mdi:thermometer-plus"

    @property
    def hvac_modes(self) -> list[HVACMode]:
        return [self.hvac_mode or HVACMode.OFF]

    @property
    def supported_features(self) -> ClimateEntityFeature:
        return self._temperature_feature

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Accept only the current mode; the main zone entity switches modes."""
        if hvac_mode != self.hvac_mode:
            raise HomeAssistantError(
                "Change the mode on the main zone climate entity"
            )
