import logging

from typing import Optional, Any
from .const import (
    DOMAIN,
    ALTHERMA_4_COILS,
    ALTHERMA_4_COILS_ADDITIONAL_ZONE,
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
        if hub.altherma_version == "Altherma 4":
            for sensor_info in ALTHERMA_4_COILS:
                sensor = DaikinEKRHHSwitch(
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
                for sensor_info in ALTHERMA_4_COILS_ADDITIONAL_ZONE:
                    if "Additional zone" in sensor_info[1]:
                        sensor = DaikinEKRHHSwitch(
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


class DaikinEKRHHSwitch(CoordinatorEntity, BinarySensorEntity):
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
    def device_info(self) -> Optional[dict[str, Any]]:
        return self._device_info

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        response = await self._hub._client.write_coil(self._key, False)
        if response.isError():
            _LOGGER.error(f"Could not turn off {self._key}")

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        response = await self._hub._client.write_coil(self._key, True)
        if response.isError():
            _LOGGER.error(f"Could not turn on {self._key}")

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
        current_state = self.is_on
        response = await self._hub._client.write_coil(self._key, not current_state)
        if response.isError():
            _LOGGER.error(f"Could not toggle {self._key}")

    @property
    def available(self) -> bool:
        return self._hub.checkAvailability(self._key)
