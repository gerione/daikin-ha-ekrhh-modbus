import logging

from .const import (
    ALTHERMA_3_HOLDING,
    ALTHERMA_3_HOLDING_ADDITIONAL_ZONE,
    ALTHERMA_4_HOLDING,
    ALTHERMA_4_HOLDING_ADDITIONAL_ZONE,
    DAIKIN_A2A_NUMBER_TYPES,
)
from .entity import DaikinEKRHHEntity, limited_max


from homeassistant.const import CONF_NAME
from homeassistant.components.number import (
    NumberEntity,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    hub_name = entry.data[CONF_NAME]
    hub = entry.runtime_data

    entities = []
    if not hub._is_air2air:
        if hub.altherma_version == "Altherma 3 (EKRHH)":
            number_infos = list(ALTHERMA_3_HOLDING)
            if hub._additional_zone:
                number_infos.extend(ALTHERMA_3_HOLDING_ADDITIONAL_ZONE)
        else:
            number_infos = list(ALTHERMA_4_HOLDING)
            if hub._additional_zone:
                number_infos.extend(ALTHERMA_4_HOLDING_ADDITIONAL_ZONE)
        for number_info in number_infos:
            attrs = number_info[6]
            entities.append(
                DaikinEKRHHNumber(
                    hub_name,
                    hub,
                    number_info[2],
                    number_info[0] - 1,
                    number_info[3],
                    dict(attrs, max=limited_max(entry.data, number_info[2], attrs["max"])),
                    number_info[5],
                )
            )
    else:
        for number_info in DAIKIN_A2A_NUMBER_TYPES:
            attrs = number_info[4]
            entities.append(
                DaikinEKRHHNumber(
                    hub_name,
                    hub,
                    number_info[1],
                    number_info[2],
                    number_info[3],
                    dict(attrs, max=limited_max(entry.data, number_info[1], attrs["max"])),
                    None,  # No icon specified in DAIKIN_A2A_NUMBER_TYPES
                )
            )
    async_add_entities(entities)


class DaikinEKRHHNumber(DaikinEKRHHEntity, NumberEntity):
    """Representation of an DaikinEKRHH Modbus number."""

    def __init__(self, device_name, hub, key, register, fmt, attrs, icon) -> None:
        """Initialize the number."""
        super().__init__(device_name, hub, key, icon)
        self._register = register
        self._fmt = fmt

        self._attr_native_min_value = attrs["min"]
        self._attr_native_max_value = attrs["max"]
        self._attr_native_step = attrs["step"]
        if "unit" in attrs.keys():
            self._attr_native_unit_of_measurement = attrs["unit"]

    @property
    def native_value(self) -> float:
        if self._key in self._hub.data:
            return self._hub.data[self._key]
        return 0.0

    async def async_set_native_value(self, value: float) -> None:
        """Change the selected value."""
        if not await self._hub.async_write_value(self._register, self._fmt, value):
            _LOGGER.error(f"Could not write value {value} to {self._key}")
            return
        await self.coordinator.async_request_refresh()
        self._hub.data[self._key] = value
        self.async_write_ha_state()
