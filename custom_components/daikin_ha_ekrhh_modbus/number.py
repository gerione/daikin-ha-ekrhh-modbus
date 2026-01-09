import logging
from typing import Optional, Any

from .const import (
    DOMAIN,
    ATTR_MANUFACTURER,
    DAIKIN_ADDITIONAL_ZONE_NUMBER_TYPES,
    DAIKIN_NUMBER_TYPES,
    DAIKIN_4_ADDITIONAL_ZONE_NUMBER_TYPES,
    DAIKIN_4_NUMBER_TYPES,
    DAIKIN_A2A_NUMBER_TYPES,
)


from homeassistant.const import CONF_NAME
from .const import CONF_MAX_POWER, CONF_MAX_WATER_TEMP
from homeassistant.components.number import (
    NumberEntity,
)

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
        if hub.altherma_version == 3:
            for number_info in DAIKIN_NUMBER_TYPES:
                max = number_info[4]["max"]
                if (
                    number_info[1] == "General_power_limit"
                    or number_info[1] == "Power_limit_during_Recommended_on_buffering"
                ):
                    max = entry.data[CONF_MAX_POWER]

                if number_info[1] == "DHW_reheat_setpoint":
                    max = entry.data[CONF_MAX_WATER_TEMP]

                number = DaikinEKRHHNumber(
                    hub_name,
                    hub,
                    device_info,
                    number_info[0],
                    number_info[1],
                    number_info[2],
                    number_info[3],
                    dict(
                        min=number_info[4]["min"],
                        max=max,
                        unit=number_info[4]["unit"],
                        step=number_info[4]["step"],
                    ),
                )
                entities.append(number)

            if hub._additional_zone:
                for number_info in DAIKIN_ADDITIONAL_ZONE_NUMBER_TYPES:
                    number = DaikinEKRHHNumber(
                        hub_name,
                        hub,
                        device_info,
                        number_info[0],
                        number_info[1],
                        number_info[2],
                        number_info[3],
                        dict(
                            min=number_info[4]["min"],
                            max=number_info[4]["max"],
                            unit=number_info[4]["unit"],
                            step=number_info[4]["step"],
                        ),
                    )
                    entities.append(number)
        else:
            for number_info in DAIKIN_4_NUMBER_TYPES:
                max = number_info[4]["max"]
                if (
                    number_info[1] == "General_power_limit"
                    or number_info[1] == "Power_limit_during_Recommended_on_buffering"
                ):
                    max = entry.data[CONF_MAX_POWER]

                if number_info[1] == "DHW_reheat_setpoint":
                    max = entry.data[CONF_MAX_WATER_TEMP]

                number = DaikinEKRHHNumber(
                    hub_name,
                    hub,
                    device_info,
                    number_info[0],
                    number_info[1],
                    number_info[2],
                    number_info[3],
                    dict(
                        min=number_info[4]["min"],
                        max=max,
                        unit=number_info[4]["unit"],
                        step=number_info[4]["step"],
                    ),
                )
                entities.append(number)

            if hub._additional_zone:
                for number_info in DAIKIN_4_ADDITIONAL_ZONE_NUMBER_TYPES:
                    number = DaikinEKRHHNumber(
                        hub_name,
                        hub,
                        device_info,
                        number_info[0],
                        number_info[1],
                        number_info[2],
                        number_info[3],
                        dict(
                            min=number_info[4]["min"],
                            max=number_info[4]["max"],
                            unit=number_info[4]["unit"],
                            step=number_info[4]["step"],
                        ),
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
                number_info[0],
                number_info[1],
                number_info[2],
                number_info[3],
                dict(
                    min=number_info[4]["min"],
                    max=max,
                    unit=number_info[4]["unit"],
                    step=number_info[4]["step"],
                ),
            )
            entities.append(number)
    async_add_entities(entities)


class DaikinEKRHHNumber(NumberEntity):
    """Representation of an DaikinEKRHH Modbus number."""

    def __init__(
        self, platform_name, hub, device_info, name, key, register, fmt, attrs
    ) -> None:
        """Initialize the selector."""
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

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self._hub.async_add_daikin_ekrhh_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_daikin_ekrhh_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self) -> None:
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self._platform_name} {self._name}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self._key}"

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
        if self._fmt == "u32":
            payload = self._hub._client.convert_to_registers(
                int(value),
                data_type=self._hub._client.DATATYPE.UINT32,
                word_order="big",
            )
        elif self._fmt == "u16":
            payload = self._hub._client.convert_to_registers(
                int(value),
                data_type=self._hub._client.DATATYPE.UINT16,
                word_order="big",
            )
        elif self._fmt == "f":
            payload = self._hub._client.convert_to_registers(
                value,
                data_type=self._hub._client.DATATYPE.FLOAT32,
                word_order="big",
            )
        elif self._fmt == "pow":
            payload = self._hub._client.convert_to_registers(
                int(value * 100),
                data_type=self._hub._client.DATATYPE.UINT16,
                word_order="big",
            )
        elif self._fmt == "i16":
            payload = self._hub._client.convert_to_registers(
                int(value),
                data_type=self._hub._client.DATATYPE.INT16,
                word_order="big",
            )

        else:
            _LOGGER.error(f"Invalid encoding format {self._fmt} for {self._key}")
            return

        response = self._hub.write_registers(
            unit=1, address=self._register, payload=payload
        )

        if response.isError():
            _LOGGER.error(f"Could not write value {value} to {self._key}")
            return

        self._hub.data[self._key] = value
        self.async_write_ha_state()

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
