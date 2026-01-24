import logging

from typing import Optional, Any
from .const import (
    ALTHERMA_3_BINARY_SENSOR_TYPES,
    ALTHERMA_4_BINARY_SENSOR_TYPES,
    DOMAIN,
    ATTR_MANUFACTURER,
)

from homeassistant.const import (
    CONF_NAME,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

from homeassistant.core import callback

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
        if hub.altherma_version == 3:
            for sensor_info in ALTHERMA_3_BINARY_SENSOR_TYPES:
                sensor = DaikinEKRHHBinarySensor(
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
            for sensor_info in ALTHERMA_4_BINARY_SENSOR_TYPES:
                sensor = DaikinEKRHHBinarySensor(
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


class DaikinEKRHHBinarySensor(CoordinatorEntity, BinarySensorEntity):
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

    @callback
    def _handle_coordinator_update(self):
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
    def icon(self):
        """Return the sensor icon."""
        return self._icon

    @property
    def device_class(self):
        return BinarySensorDeviceClass.RUNNING

    @property
    def is_on(self):
        return self._hub.data[self._key] == 1

    @property
    def should_poll(self) -> bool:
        """Data is delivered by the hub"""
        return False

    @property
    def device_info(self) -> Optional[dict[str, Any]]:
        return self._device_info

    @property
    def available(self) -> bool:
        if self._key in ("Unit error", "Unit error sub code", "Unit error code"):
            return True
        if self._hub._is_air2air:
            return True
        if "Unit error" not in self._hub.data or (
            self._hub.data["Unit error"] != 0 and self._hub.data["Unit error"] != 2
        ):
            return False
        if (
            "Unit error sub code" not in self._hub.data
            or self._hub.data["Unit error sub code"] != 32766
        ):
            return False
        return True
