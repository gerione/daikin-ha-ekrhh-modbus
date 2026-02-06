import logging
from typing import Optional, Any

from .const import (
    DOMAIN,
    ATTR_MANUFACTURER,
    ALTHERMA_3_HOLDING,
    ALTHERMA_3_HOLDING_ADDITIONAL_ZONE,
    ALTHERMA_4_HOLDING,
    ALTHERMA_4_HOLDING_ADDITIONAL_ZONE,
    DAIKIN_A2A_NUMBER_TYPES,
)


from homeassistant.const import CONF_NAME
from .const import CONF_MAX_POWER, CONF_MAX_WATER_TEMP
from homeassistant.components.number import (
    NumberEntity,
)

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
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
            for number_info in ALTHERMA_3_HOLDING:
                max = number_info[6]["max"]
                if (
                    number_info[2] == f"{DOMAIN}_holding_58"
                    or number_info[2] == f"{DOMAIN}_holding_59"
                ):
                    max = entry.data[CONF_MAX_POWER]

                if number_info[2] == f"{DOMAIN}_holding_10":
                    max = entry.data[CONF_MAX_WATER_TEMP]

                number = DaikinEKRHHNumber(
                    hub_name,
                    hub,
                    device_info,
                    number_info[1],
                    number_info[2],
                    number_info[0] - 1,
                    number_info[3],
                    dict(
                        min=number_info[6]["min"],
                        max=max,
                        unit=number_info[6]["unit"],
                        step=number_info[6]["step"],
                    ),
                    number_info[5],
                )
                entities.append(number)

            if hub._additional_zone:
                for number_info in ALTHERMA_3_HOLDING_ADDITIONAL_ZONE:
                    number = DaikinEKRHHNumber(
                        hub_name,
                        hub,
                        device_info,
                        number_info[1],
                        number_info[2],
                        number_info[0] - 1,
                        number_info[3],
                        dict(
                            min=number_info[6]["min"],
                            max=number_info[6]["max"],
                            unit=number_info[6]["unit"],
                            step=number_info[6]["step"],
                        ),
                        number_info[5],
                    )
                    entities.append(number)
        else:
            for number_info in ALTHERMA_4_HOLDING:
                max = number_info[6]["max"]

                number = DaikinEKRHHNumber(
                    hub_name,
                    hub,
                    device_info,
                    number_info[1],
                    number_info[2],
                    number_info[0] - 1,
                    number_info[3],
                    dict(
                        min=number_info[6]["min"],
                        max=max,
                        unit=number_info[6]["unit"],
                        step=number_info[6]["step"],
                    ),
                    number_info[5],
                )
                entities.append(number)

            if hub._additional_zone:
                for number_info in ALTHERMA_4_HOLDING_ADDITIONAL_ZONE:
                    number = DaikinEKRHHNumber(
                        hub_name,
                        hub,
                        device_info,
                        number_info[1],
                        number_info[2],
                        number_info[0] - 1,
                        number_info[3],
                        dict(
                            min=number_info[6]["min"],
                            max=number_info[6]["max"],
                            unit=number_info[6]["unit"],
                            step=number_info[6]["step"],
                        ),
                        number_info[5],
                    )
                    entities.append(number)
    else:
        for number_info in DAIKIN_A2A_NUMBER_TYPES:
            max = number_info[4]["max"]
            if number_info[1] == "Power_limit_for_Demand_Control":
                max = entry.data[CONF_MAX_POWER]
            number = DaikinEKRHHNumber(
                hub_name,
                hub,
                device_info,
                number_info[1],
                number_info[2],
                number_info[0] - 1,
                number_info[3],
                dict(
                    min=number_info[6]["min"],
                    max=max,
                    unit=number_info[6]["unit"],
                    step=number_info[6]["step"],
                ),
                number_info[5],
            )
            entities.append(number)
    async_add_entities(entities)


class DaikinEKRHHNumber(CoordinatorEntity, NumberEntity):
    """Representation of an DaikinEKRHH Modbus number."""

    def __init__(
        self, platform_name, hub, device_info, name, key, register, fmt, attrs, icon
    ) -> None:
        """Initialize the selector."""
        super().__init__(coordinator=hub)
        self._platform_name = platform_name
        self._hub = hub
        self._device_info = device_info
        self._name = name
        self._key = key
        self._register = register
        self._fmt = fmt

        self._attr_native_min_value = attrs["min"]
        self._attr_native_max_value = attrs["max"]
        self._attr_native_step = attrs["step"]
        if "unit" in attrs.keys():
            self._attr_native_unit_of_measurement = attrs["unit"]
        self._icon = icon

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()

    @property
    def name(self) -> str:
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
    def should_poll(self) -> bool:
        """Data is delivered by the hub"""
        return False

    @property
    def device_info(self) -> Optional[dict[str, Any]]:
        return self._device_info

    @property
    def native_value(self) -> float:
        if self._key in self._hub.data:
            return self._hub.data[self._key]
        return 0.0

    async def async_set_native_value(self, value: float) -> None:
        """Change the selected value."""
        payload = 0
        if self._fmt == "POW16":
            payload = int(value * 100)
        elif self._fmt == "INT16":
            payload = int(value)

        else:
            _LOGGER.error(f"Invalid encoding format {self._fmt} for {self._key}")
            return

        response = await self._hub._client.write_register(self._register, payload)

        if response.isError():
            _LOGGER.error(f"Could not write value {value} to {self._key}")
            return
        await self.coordinator.async_request_refresh()
        self._hub.data[self._key] = value
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        return self._hub.checkAvailability(self._key)
