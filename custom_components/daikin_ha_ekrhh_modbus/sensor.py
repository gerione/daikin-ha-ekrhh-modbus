import logging
from .const import (
    ALTHERMA_3_INPUT,
    ALTHERMA_3_INPUT_ADDITIONAL_ZONE,
    ALTHERMA_4_INPUT,
    ALTHERMA_4_INPUT_ADDITIONAL_ZONE,
    A2A_SENSOR_TYPES,
    FAULT_CODE_SENSOR,
)
from .entity import DaikinEKRHHEntity

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
