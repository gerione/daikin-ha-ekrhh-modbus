import logging
from typing import Optional, Any
from .const import (
    ALTHERMA_3_INPUT,
    ALTHERMA_3_INPUT_ADDITIONAL_ZONE,
    ALTHERMA_4_INPUT,
    ALTHERMA_4_INPUT_ADDITIONAL_ZONE,
    DOMAIN,
    ATTR_STATUS_DESCRIPTION,
    ATTR_MANUFACTURER,
    A2A_SENSOR_TYPES,
)

from homeassistant.const import (
    CONF_NAME,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
        if hub.altherma_version == "Altherma 3 (EKRHH)":
            for sensor_info in ALTHERMA_3_INPUT:
                sensor = DaikinEKRHHSensor(
                    hub_name,
                    hub,
                    device_info,
                    sensor_info[1],
                    sensor_info[2],
                    sensor_info[4],
                    sensor_info[5],
                )
                entities.append(sensor)
            if hub._additional_zone:
                for sensor_info in ALTHERMA_3_INPUT_ADDITIONAL_ZONE:
                    sensor = DaikinEKRHHSensor(
                        hub_name,
                        hub,
                        device_info,
                        sensor_info[1],
                        sensor_info[2],
                        sensor_info[4],
                        sensor_info[5],
                    )
                    entities.append(sensor)
        else:
            for sensor_info in ALTHERMA_4_INPUT:
                sensor = DaikinEKRHHSensor(
                    hub_name,
                    hub,
                    device_info,
                    sensor_info[1],
                    sensor_info[2],
                    sensor_info[4],
                    sensor_info[5],
                )
                entities.append(sensor)
            if hub._additional_zone:
                for sensor_info in ALTHERMA_4_INPUT_ADDITIONAL_ZONE:
                    sensor = DaikinEKRHHSensor(
                        hub_name,
                        hub,
                        device_info,
                        sensor_info[1],
                        sensor_info[2],
                        sensor_info[4],
                        sensor_info[5],
                    )
                    entities.append(sensor)
    else:
        for sensor_info in A2A_SENSOR_TYPES.values():
            sensor = DaikinEKRHHSensor(
                hub_name,
                hub,
                device_info,
                sensor_info[1],
                sensor_info[2],
                sensor_info[4],
                sensor_info[5],
            )
            entities.append(sensor)
    async_add_entities(entities)
    return True


class DaikinEKRHHSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Daikin EKRHH Modbus sensor."""

    def __init__(self, platform_name, hub, device_info, name, key, unit, icon):
        """Initialize the sensor."""
        super().__init__(coordinator=hub)
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

    @callback
    def _handle_coordinator_update(self):
        if self._key in self._hub.data:
            self._state = self._hub.data[self._key]
        self.async_write_ha_state()

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
    def should_poll(self) -> bool:
        """Data is delivered by the hub"""
        return False

    @property
    def device_info(self) -> Optional[dict[str, Any]]:
        return self._device_info

    @property
    def available(self) -> bool:
        return self._hub.checkAvailability(self._key)
