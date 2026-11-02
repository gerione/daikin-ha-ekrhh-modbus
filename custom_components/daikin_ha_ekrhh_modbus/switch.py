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

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchDeviceClass,
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
                    sensor_info[0] - 1,
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
                            sensor_info[0] - 1,
                            sensor_info[4],
                            sensor_info[5],
                        )
                        entities.append(sensor)
    async_add_entities(entities)
    return True


class DaikinEKRHHSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a writable Daikin EKRHH Modbus coil."""

    def __init__(
        self, platform_name, hub, device_info, name, key, register, unit, icon
    ):
        """Initialize the sensor."""
        super().__init__(coordinator=hub)
        self._platform_name = platform_name
        self._hub = hub
        self._key = key
        self._register = register
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
        return SwitchDeviceClass.SWITCH

    @property
    def is_on(self):
        if self._key not in self._hub.data:
            return None
        return bool(self._hub.data[self._key])

    @property
    def device_info(self) -> Optional[dict[str, Any]]:
        return self._device_info

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self._async_write(False)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self._async_write(True)

    async def _async_write(self, value: bool) -> None:
        """Write the coil and show the new state right away."""
        if not await self._hub.async_write_coil(self._register, value):
            _LOGGER.error(f"Could not turn {'on' if value else 'off'} {self._key}")
            return
        self._hub.data[self._key] = value
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @property
    def available(self) -> bool:
        return self._hub.checkAvailability(self._key)
