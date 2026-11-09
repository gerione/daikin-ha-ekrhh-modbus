"""Base entity for the Daikin EKRHH Modbus integration."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ALTHERMA_3_HOLDING,
    ALTHERMA_3_HOLDING_ADDITIONAL_ZONE,
    ALTHERMA_4_HOLDING,
    ALTHERMA_4_HOLDING_ADDITIONAL_ZONE,
    ATTR_MANUFACTURER,
    CONF_MAX_POWER,
    CONF_MAX_WATER_TEMP,
    DOMAIN,
)
from .coordinator import DaikinEKRHHModbusHub


def translation_key_for(key: str) -> str:
    """Derive the translation key of an entity from its register key."""
    return key.strip().lower().removeprefix(f"{DOMAIN}_")


def model_prefix(altherma_version: str) -> str:
    """Return the register key prefix of a heat pump model."""
    return "altherma3" if altherma_version == "Altherma 3 (EKRHH)" else "altherma4"


def register_key(altherma_version: str, kind: str, register: int) -> str:
    """Return the data key of a register, e.g. ("Altherma 4", "holding", 10)."""
    return f"{DOMAIN}_{model_prefix(altherma_version)}_{kind}_{register}"


def holding_info(key: str) -> list:
    """Return the register table row of a writable holding register."""
    for table in (
        ALTHERMA_3_HOLDING,
        ALTHERMA_3_HOLDING_ADDITIONAL_ZONE,
        ALTHERMA_4_HOLDING,
        ALTHERMA_4_HOLDING_ADDITIONAL_ZONE,
    ):
        for row in table:
            if row[2] == key:
                return row
    raise KeyError(key)


def limited_max(entry_data, key: str, default):
    """Return the upper limit of a register, capped by the user's options."""
    max_overrides = {
        f"{DOMAIN}_altherma3_holding_57": entry_data[CONF_MAX_POWER],
        f"{DOMAIN}_altherma3_holding_58": entry_data[CONF_MAX_POWER],
        f"{DOMAIN}_altherma3_holding_10": entry_data[CONF_MAX_WATER_TEMP],
        f"{DOMAIN}_altherma4_holding_58": entry_data[CONF_MAX_POWER],
        "Power_limit_for_Demand_Control": entry_data[CONF_MAX_POWER],
    }
    return max_overrides.get(key, default)


class DaikinEKRHHEntity(CoordinatorEntity[DaikinEKRHHModbusHub]):
    """An entity backed by one value the hub polls."""

    _attr_has_entity_name = True

    def __init__(self, device_name, hub, key, icon=None) -> None:
        """Initialize the entity."""
        super().__init__(coordinator=hub)
        self._hub = hub
        self._key = key
        self._attr_icon = icon
        self._attr_translation_key = translation_key_for(key)
        # Kept as-is so existing entities keep their registry entries.
        self._attr_unique_id = f"{device_name}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_name)},
            name=device_name,
            manufacturer=ATTR_MANUFACTURER,
        )

    @property
    def available(self) -> bool:
        """Return whether the last poll succeeded and the value is valid."""
        return super().available and self._hub.checkAvailability(self._key)
