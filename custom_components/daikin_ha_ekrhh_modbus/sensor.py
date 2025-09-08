import logging
from typing import Optional, Dict, Any
from .const import (
    ADDITIONAL_ZONE_SENSOR_TYPES,
    SENSOR_TYPES,
    DOMAIN,
    ATTR_STATUS_DESCRIPTION,
    DEVICE_STATUSSES,
    ATTR_MANUFACTURER,
    A2A_SENSOR_TYPES,
)
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_NAME,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.core import callback
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    if not hub._is_air2air:
        for sensor_info in SENSOR_TYPES.values():
            sensor = DaikinEKRHHSensor(
                hub_name,
                hub,
                device_info,
                sensor_info[0],
                sensor_info[1],
                sensor_info[2],
                sensor_info[3],
            )
            entities.append(sensor)
        if hub._additional_zone:
            for sensor_info in ADDITIONAL_ZONE_SENSOR_TYPES.values():
                sensor = DaikinEKRHHSensor(
                    hub_name,
                    hub,
                    device_info,
                    sensor_info[0],
                    sensor_info[1],
                    sensor_info[2],
                    sensor_info[3],
                )
                entities.append(sensor)
    else:
        for sensor_info in A2A_SENSOR_TYPES.values():
            sensor = DaikinEKRHHSensor(
                hub_name,
                hub,
                device_info,
                sensor_info[0],
                sensor_info[1],
                sensor_info[2],
                sensor_info[3],
            )
            entities.append(sensor)
    async_add_entities(entities)
    return True


class DaikinEKRHHSensor(SensorEntity):
    """Representation of an Daikin EKRHH Modbus sensor."""

    def __init__(self, platform_name, hub, device_info, name, key, unit, icon):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._hub = hub
        self._key = key
        self._name = name
        self._unit_of_measurement = unit
        self._icon = icon
        self._device_info = device_info
        self._attr_state_class = SensorStateClass.MEASUREMENT
        if (
            self._unit_of_measurement == UnitOfPower.WATT
            or self._unit_of_measurement == UnitOfPower.KILO_WATT
        ):
            self._attr_device_class = SensorDeviceClass.POWER
        elif self._unit_of_measurement == UnitOfTemperature.CELSIUS:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
        elif self._unit_of_measurement == UnitOfVolumeFlowRate.LITERS_PER_MINUTE:
            self._attr_device_class = SensorDeviceClass.VOLUME_FLOW_RATE

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_daikin_ekrhh_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_daikin_ekrhh_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
        self.async_write_ha_state()

    @callback
    def _update_state(self):
        if self._key in self._hub.data:
            self._state = self._hub.data[self._key]

    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} {self._name}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self._key}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the sensor icon."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._key in self._hub.data:
            return self._hub.data[self._key]
        return None

    @property
    def extra_state_attributes(self):
        if self._key in ["status", "statusvendor"] and self.state in DEVICE_STATUSSES:
            return {ATTR_STATUS_DESCRIPTION: DEVICE_STATUSSES[self.state]}
        return None

    @property
    def should_poll(self) -> bool:
        """Data is delivered by the hub"""
        return False

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._device_info

    @property
    def available(self) -> bool:
        if (
            not "Unit error sub code" in self._hub.data
            or self._hub.data["Unit error sub code"] != 32766
        ) and not self._hub._is_air2air:
            return False
        return True
