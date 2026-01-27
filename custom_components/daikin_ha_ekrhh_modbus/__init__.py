import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from .coordinator import DaikinEKRHHModbusHub

from .const import (
    DOMAIN,
    CONF_MAX_POWER,
    CONF_MAX_WATER_TEMP,
    CONF_ADDITIONAL_ZONE,
    CONF_ISAIR2AIR,
    CONF_ALTHERMA_VERSION,
)

_LOGGER = logging.getLogger(__name__)


PLATFORMS = ["binary_sensor", "number", "select", "sensor", "switch"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Daikin EKRHH Modbus component."""
    # @TODO: Add setup code.
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a daikin_ekrhh mobus."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    port = entry.data[CONF_PORT]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]
    additional_zone = entry.data[CONF_ADDITIONAL_ZONE]
    altherma_version = entry.data[CONF_ALTHERMA_VERSION]
    is_air2air = altherma_version == "Air2Air (EKRHH)"

    hub = DaikinEKRHHModbusHub(
        hass,
        name,
        host,
        port,
        scan_interval,
        additional_zone,
        is_air2air,
        altherma_version,
    )
    await hub.async_config_entry_first_refresh()
    hass.data[DOMAIN][name] = {"hub": hub}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    """Unload daikin_ekrhh mobus entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if not unload_ok:
        return False

    hass.data[DOMAIN].pop(entry.data["name"])
    return True


# Example migration function
async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug(
        "Migrating configuration from version %s.%s",
        config_entry.version,
        config_entry.minor_version,
    )

    if config_entry.version > 1:
        # This means the user has downgraded from a future version
        return False

    if config_entry.version == 1:
        new_data = {**config_entry.data}
        if config_entry.minor_version < 2:
            new_data[CONF_ISAIR2AIR] = False

        if config_entry.minor_version < 3:
            new_data[CONF_MAX_POWER] = 20
            new_data[CONF_MAX_WATER_TEMP] = 60

        if config_entry.minor_version < 5:
            if config_entry.data[CONF_ISAIR2AIR]:
                new_data[CONF_ALTHERMA_VERSION] = "Air2Air (EKRHH)"
            elif config_entry.data.get(CONF_ALTHERMA_VERSION) == "4":
                new_data[CONF_ALTHERMA_VERSION] = "Altherma 4"
            else:
                new_data[CONF_ALTHERMA_VERSION] = "Altherma 3 (EKRHH)"

        hass.config_entries.async_update_entry(
            config_entry, data=new_data, minor_version=3, version=1
        )

    _LOGGER.debug(
        "Migration to configuration version %s.%s successful",
        config_entry.version,
        config_entry.minor_version,
    )

    return True
