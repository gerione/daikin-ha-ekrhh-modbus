import logging

from .const import (
    ALTHERMA_3_INPUT_BINARY,
    ALTHERMA_4_DISCRETE_INPUTS,
    ALTHERMA_4_DISCRETE_INPUTS_ADDITIONAL_ZONE,
    ALTHERMA_4_INPUT_BINARY,
)
from .entity import DaikinEKRHHEntity

from homeassistant.const import (
    CONF_NAME,
)

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = entry.runtime_data

    sensor_infos = []
    if not hub._is_air2air:
        if hub.altherma_version == "Altherma 3 (EKRHH)":
            sensor_infos.extend(ALTHERMA_3_INPUT_BINARY)
        else:
            sensor_infos.extend(ALTHERMA_4_INPUT_BINARY)
            sensor_infos.extend(ALTHERMA_4_DISCRETE_INPUTS)
            if hub._additional_zone:
                sensor_infos.extend(
                    sensor_info
                    for sensor_info in ALTHERMA_4_DISCRETE_INPUTS_ADDITIONAL_ZONE
                    if "Additional zone" in sensor_info[1]
                )
    async_add_entities(
        DaikinEKRHHBinarySensor(hub_name, hub, sensor_info[2], sensor_info[5])
        for sensor_info in sensor_infos
    )
    return True


class DaikinEKRHHBinarySensor(DaikinEKRHHEntity, BinarySensorEntity):
    """Representation of an Daikin EKRHH Modbus sensor."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING

    @property
    def is_on(self):
        """Return whether the value is set."""
        value = self._hub.data.get(self._key)
        if value is None:
            return None
        return value == 1
