import logging
from typing import Optional, Dict, Any

from .const import (
    DOMAIN,
    ATTR_MANUFACTURER,
    DAIKIN_SELECT_TYPES,
    DAIKIN_ADDITIONAL_ZONE_SELECT_TYPES,
    DAIKIN_A2A_SELECT_TYPES,
)

from homeassistant.const import CONF_NAME
from homeassistant.components.select import (
    SelectEntity,
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
        for select_info in DAIKIN_SELECT_TYPES:
            select = DaikinHAEKRHHModbusSelect(
                hub_name,
                hub,
                device_info,
                select_info[0],
                select_info[1],
                select_info[2],
                select_info[3],
            )
            entities.append(select)

        if hub._additional_zone:
            for select_info in DAIKIN_ADDITIONAL_ZONE_SELECT_TYPES:
                select = DaikinHAEKRHHModbusSelect(
                    hub_name,
                    hub,
                    device_info,
                    select_info[0],
                    select_info[1],
                    select_info[2],
                    select_info[3],
                )
                entities.append(select)
    else:
        for select_info in DAIKIN_A2A_SELECT_TYPES:
            select = DaikinHAEKRHHModbusSelect(
                hub_name,
                hub,
                device_info,
                select_info[0],
                select_info[1],
                select_info[2],
                select_info[3],
            )
            entities.append(select)
    async_add_entities(entities)

    return True


def get_key(my_dict, search):
    for k, v in my_dict.items():
        if v == search:
            return k
    return None


class DaikinHAEKRHHModbusSelect(CoordinatorEntity, SelectEntity):
    """Representation of an daikin_ekrhh Modbus select."""

    def __init__(
        self, platform_name, hub, device_info, name, key, register, options
    ) -> None:
        """Initialize the selector."""
        super().__init__(coordinator=hub)
        self._platform_name = platform_name
        self._hub = hub
        self._device_info = device_info
        self._name = name
        self._key = key
        self._register = register
        self._option_dict = options

        self._attr_options = list(options.values())

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
    def should_poll(self) -> bool:
        """Data is delivered by the hub"""
        return False

    @property
    def current_option(self) -> str:
        index = self._hub.data.get(self._key)
        if index is not None and 0 <= index < len(self.options):
            return self.options[index]
        return None  # or return some default value

    def get_options(self):
        return list(self._option_dict.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        new_mode = get_key(self._option_dict, option)
        response = await self._hub._client.write_register(self._register, new_mode)

        if not response.isError():
            self._hub.data[self._key] = new_mode

        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
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
