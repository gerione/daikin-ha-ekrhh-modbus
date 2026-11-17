import logging
from .const import (
    ALTHERMA_3_INPUT,
    ALTHERMA_3_INPUT_ADDITIONAL_ZONE,
    ALTHERMA_4_INPUT,
    ALTHERMA_4_INPUT_ADDITIONAL_ZONE,
    A2A_SENSOR_TYPES,
    CALC_FLOW,
    CALC_LEAVING_WATER,
    CALC_POWER,
    CALC_RETURN_WATER,
    CALCULATED_SENSORS,
    DOMAIN,
    FAULT_CODE_SENSOR,
    WATER_HEAT_CAPACITY,
)
from .entity import DaikinEKRHHEntity, register_key

from homeassistant.const import (
    CONF_NAME,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = entry.runtime_data

    entities = []
    if not hub._is_air2air:
        if hub.altherma_version == "Altherma 3 (EKRHH)":
            sensor_infos = list(ALTHERMA_3_INPUT)
            if hub._additional_zone:
                sensor_infos.extend(ALTHERMA_3_INPUT_ADDITIONAL_ZONE)
        else:
            sensor_infos = list(ALTHERMA_4_INPUT)
            if hub._additional_zone:
                sensor_infos.extend(ALTHERMA_4_INPUT_ADDITIONAL_ZONE)
        for sensor_info in sensor_infos:
            entities.append(
                DaikinEKRHHSensor(
                    hub_name, hub, sensor_info[2], sensor_info[4], sensor_info[5]
                )
            )
        entities.append(
            DaikinEKRHHSensor(
                hub_name,
                hub,
                FAULT_CODE_SENSOR[1],
                FAULT_CODE_SENSOR[2],
                FAULT_CODE_SENSOR[3],
            )
        )
        entities.extend(
            DaikinEKRHHCalculatedSensor(hub_name, hub, *info)
            for info in CALCULATED_SENSORS
        )
    else:
        for sensor_info in A2A_SENSOR_TYPES.values():
            entities.append(
                DaikinEKRHHSensor(
                    hub_name, hub, sensor_info[1], sensor_info[2], sensor_info[3]
                )
            )
    async_add_entities(entities)
    return True


class DaikinEKRHHSensor(DaikinEKRHHEntity, SensorEntity):
    """Representation of an Daikin EKRHH Modbus sensor."""

    def __init__(self, device_name, hub, key, unit, icon):
        """Initialize the sensor."""
        super().__init__(device_name, hub, key, icon)
        self._attr_native_unit_of_measurement = unit
        # Unitless values are status codes or text, not measurements.
        if unit is not None:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        if unit == UnitOfPower.WATT or unit == UnitOfPower.KILO_WATT:
            self._attr_device_class = SensorDeviceClass.POWER
        elif unit == UnitOfTemperature.CELSIUS:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
        elif unit == UnitOfVolumeFlowRate.LITERS_PER_MINUTE:
            self._attr_device_class = SensorDeviceClass.VOLUME_FLOW_RATE
        elif unit == UnitOfPressure.BAR:
            self._attr_device_class = SensorDeviceClass.PRESSURE

    @property
    def native_value(self):
        """Return the value of the sensor."""
        return self._hub.data.get(self._key)


class DaikinEKRHHCalculatedSensor(DaikinEKRHHSensor):
    """A value calculated from the water temperatures, flow and power use."""

    def __init__(self, device_name, hub, name, key, unit, icon):
        """Initialize the sensor."""
        super().__init__(device_name, hub, key, unit, icon)
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_suggested_display_precision = 2
        if key == f"{DOMAIN}_delta_t":
            # A temperature difference must not be converted like a temperature
            # (e.g. 5 °C is a 9 °F difference, not 41 °F).
            self._attr_device_class = None
        version = hub.altherma_version
        self._leaving, self._return, self._flow, self._power = (
            register_key(version, "input", register)
            for register in (CALC_LEAVING_WATER, CALC_RETURN_WATER, CALC_FLOW, CALC_POWER)
        )
        self._sources = {
            f"{DOMAIN}_delta_t": (self._leaving, self._return),
            f"{DOMAIN}_heat_generated": (self._leaving, self._return, self._flow),
            f"{DOMAIN}_cop": (self._leaving, self._return, self._flow, self._power),
        }[key]

    @property
    def available(self) -> bool:
        """Return whether every value the calculation uses is valid."""
        return super().available and all(
            self._hub.checkAvailability(source) for source in self._sources
        )

    def _delta_t(self) -> float:
        return self._hub.data[self._leaving] - self._hub.data[self._return]

    def _heat(self) -> float:
        """Return the thermal power in kW; negative while cooling or defrosting."""
        return self._hub.data[self._flow] / 60 * WATER_HEAT_CAPACITY * self._delta_t()

    @property
    def native_value(self):
        """Return the calculated value, or None while a source is missing."""
        if any(self._hub.data.get(source) is None for source in self._sources):
            return None
        if self._key == f"{DOMAIN}_delta_t":
            return round(self._delta_t(), 2)
        if self._key == f"{DOMAIN}_heat_generated":
            return round(self._heat(), 3)
        # COP while heating, EER while cooling; undefined while the unit is idle.
        power = self._hub.data[self._power]
        if power <= 0:
            return None
        return round(abs(self._heat()) / power, 2)
