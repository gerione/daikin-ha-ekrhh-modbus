import logging

from .const import (
    ALTHERMA_3_HOLDING_SELECT,
    ALTHERMA_3_HOLDING_SELECT_ADDITIONAL_ZONE,
    ALTHERMA_4_HOLDING_SELECT,
    ALTHERMA_4_HOLDING_SELECT_ADDITIONAL_ZONE,
    DAIKIN_A2A_SELECT_TYPES,
)
from .entity import DaikinEKRHHEntity

from homeassistant.const import CONF_NAME
from homeassistant.components.select import (
    SelectEntity,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    hub_name = entry.data[CONF_NAME]
    hub = entry.runtime_data

    entities = []
    if not hub._is_air2air:
        if hub.altherma_version == "Altherma 3 (EKRHH)":
            select_infos = list(ALTHERMA_3_HOLDING_SELECT)
            if hub._additional_zone:
                select_infos.extend(ALTHERMA_3_HOLDING_SELECT_ADDITIONAL_ZONE)
        else:
            select_infos = list(ALTHERMA_4_HOLDING_SELECT)
            if hub._additional_zone:
                select_infos.extend(ALTHERMA_4_HOLDING_SELECT_ADDITIONAL_ZONE)
        for select_info in select_infos:
            entities.append(
                DaikinHAEKRHHModbusSelect(
                    hub_name,
                    hub,
                    select_info[2],
                    select_info[0] - 1,
                    select_info[6],
                    select_info[5],
                )
            )
    else:
        for select_info in DAIKIN_A2A_SELECT_TYPES:
            entities.append(
                DaikinHAEKRHHModbusSelect(
                    hub_name,
                    hub,
                    select_info[1],
                    select_info[2],
                    select_info[3],
                    None,  # No icon specified in DAIKIN_A2A_SELECT_TYPES
                )
            )
    async_add_entities(entities)

    return True


def get_key(my_dict, search):
    for k, v in my_dict.items():
        if v == search:
            return k
    return None


class DaikinHAEKRHHModbusSelect(DaikinEKRHHEntity, SelectEntity):
    """Representation of an daikin_ekrhh Modbus select."""

    def __init__(self, device_name, hub, key, register, options, icon) -> None:
        """Initialize the selector."""
        super().__init__(device_name, hub, key, icon)
        self._register = register
        self._option_dict = options

        self._attr_options = list(options.values())

    @property
    def current_option(self) -> str | None:
        index = self._hub.data.get(self._key)
        if index is not None and 0 <= index < len(self.options):
            return self.options[index]
        return None  # or return some default value

    def get_options(self):
        return list(self._option_dict.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        new_mode = get_key(self._option_dict, option)
        if await self._hub.async_write_register(self._register, new_mode):
            self._hub.data[self._key] = new_mode

        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()
