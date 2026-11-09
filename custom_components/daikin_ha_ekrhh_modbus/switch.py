import logging

from .const import (
    ALTHERMA_4_COILS,
    ALTHERMA_4_COILS_ADDITIONAL_ZONE,
)
from .entity import DaikinEKRHHEntity

from homeassistant.const import CONF_NAME
from homeassistant.components.switch import (
    SwitchEntity,
    SwitchDeviceClass,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = entry.runtime_data

    switch_infos = []
    if not hub._is_air2air:
        if hub.altherma_version == "Altherma 4":
            switch_infos.extend(ALTHERMA_4_COILS)
            if hub._additional_zone:
                switch_infos.extend(
                    switch_info
                    for switch_info in ALTHERMA_4_COILS_ADDITIONAL_ZONE
                    if "Additional zone" in switch_info[1]
                )
    async_add_entities(
        DaikinEKRHHSwitch(
            hub_name, hub, switch_info[2], switch_info[0] - 1, switch_info[5]
        )
        for switch_info in switch_infos
    )
    return True


class DaikinEKRHHSwitch(DaikinEKRHHEntity, SwitchEntity):
    """Representation of a writable Daikin EKRHH Modbus coil."""

    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, device_name, hub, key, register, icon):
        """Initialize the switch."""
        super().__init__(device_name, hub, key, icon)
        self._register = register

    @property
    def is_on(self):
        if self._key not in self._hub.data:
            return None
        return bool(self._hub.data[self._key])

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
